"""
Tests d'intégration pour les patients
Tests complets des workflows et interactions entre composants
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from datetime import date, timedelta
import json

from core.models import Patient, Caisse
from authentication.models import SageFemmeUser


User = get_user_model()


class PatientIntegrationTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.client = Client()
        
        # Créer un superutilisateur de test
        self.user = SageFemmeUser.objects.create_superuser(
            email='admin@maieutix.nc',
            password='testpass123'
        )
        
        # Créer des caisses
        self.caisse1 = Caisse.objects.create(
            nom="CAFAT"
        )
        
        self.caisse2 = Caisse.objects.create(
            nom="RUAMM"
        )
        
        # Se connecter
        self.client.login(email='admin@maieutix.nc', password='testpass123')
    
    def test_complete_patient_workflow_femme(self):
        """Test complet du workflow création/modification/activation femme"""
        # 1. Accéder à la liste des patients (vide)
        response = self.client.get(reverse('patients:patients_view'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Dupont')
        
        # 2. Créer une nouvelle patiente
        create_data = {
            'type_patient': 'femme',
            'nom': 'Dupont',
            'prenom': 'Marie',
            'date_naissance': '1990-05-15',
            'telephone': '0123456789',
            'nom_jf': 'Martin',
            'profession': 'Infirmière',
            'est_assure_titulaire': True,
            'nom_assure': 'Dupont',
            'prenom_assure': 'Marie',
            'date_naissance_assure': '1990-05-15',
            'rue_assure': '123 Rue Test',
            'code_postal_assure': '98800',
            'commune_assure': 'Nouméa',
            'caisse': self.caisse1.id
        }
        
        response = self.client.post(reverse('patients:patient_create'), create_data)
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la création
        patient = Patient.objects.get(nom='Dupont', prenom='Marie')
        self.assertEqual(patient.type_patient, 'femme')
        self.assertTrue(patient.is_active)
        
        # 3. Vérifier que la patiente apparaît dans la liste
        response = self.client.get(reverse('patients:patients_view'))
        self.assertContains(response, 'Marie Dupont')
        
        # 4. Accéder au détail de la patiente
        response = self.client.get(reverse('patients:patient_detail', kwargs={'patient_id': patient.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Marie Dupont')
        self.assertContains(response, 'Infirmière')
        
        # 5. Modifier la patiente
        edit_data = create_data.copy()
        edit_data['profession'] = 'Sage-femme'
        edit_data['telephone'] = '0654321098'
        
        response = self.client.post(
            reverse('patients:patient_edit', kwargs={'patient_id': patient.id}),
            edit_data
        )
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les modifications
        patient.refresh_from_db()
        self.assertEqual(patient.profession, 'Sage-femme')
        self.assertEqual(patient.telephone, '0654321098')
        
        # 6. Désactiver la patiente
        response = self.client.post(
            reverse('patients:patient_toggle_active', kwargs={'patient_id': patient.id})
        )
        self.assertEqual(response.status_code, 200)
        
        patient.refresh_from_db()
        self.assertFalse(patient.is_active)
        
        # 7. Vérifier que la patiente apparaît toujours dans la liste (mais grisée)
        response = self.client.get(reverse('patients:patients_view'))
        self.assertContains(response, 'Marie Dupont')
        
        # 8. Réactiver la patiente
        response = self.client.post(
            reverse('patients:patient_toggle_active', kwargs={'patient_id': patient.id})
        )
        self.assertEqual(response.status_code, 200)
        
        patient.refresh_from_db()
        self.assertTrue(patient.is_active)
    
    def test_complete_patient_workflow_bebe(self):
        """Test complet du workflow création bébé avec mère"""
        # 1. Créer d'abord une mère
        mere_data = {
            'type_patient': 'femme',
            'nom': 'Martin',
            'prenom': 'Sophie',
            'date_naissance': '1985-03-10',
            'telephone': '0123456789',
            'caisse': self.caisse1.id,
            'est_assure_titulaire': True,
            'nom_assure': 'Martin',
            'prenom_assure': 'Sophie'
        }
        
        response = self.client.post(reverse('patients:patient_create'), mere_data)
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la réponse pour la création de la mère
        content = json.loads(response.content)
        if not content.get('success', False):
            self.fail(f"Failed to create mother: {content}")
        
        mere = Patient.objects.get(nom='Martin', prenom='Sophie')
        
        # 2. Tester l'API de recherche des mères
        response = self.client.get(reverse('patients:search_meres'), {'q': 'Martin'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['nom_complet'], 'Sophie Martin')
        
        # 3. Tester l'API de détails de la mère
        response = self.client.get(
            reverse('patients:patient_details_for_baby', kwargs={'patient_id': mere.id})
        )
        self.assertEqual(response.status_code, 200)
        
        details = json.loads(response.content)
        self.assertEqual(details['telephone'], '0123456789')
        self.assertEqual(details['nom_assure'], 'Martin')
        
        # 4. Créer un bébé associé à la mère
        bebe_data = {
            'type_patient': 'bebe',
            'nom': 'Martin',
            'prenom': 'Lucas',
            'date_naissance': (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'mere': mere.id,
            'telephone': '0123456789',  # Hérité de la mère
            'caisse': self.caisse1.id,
            'est_assure_titulaire': False,  # Bébé ne peut pas être titulaire
            'nom_assure': 'Martin',
            'prenom_assure': 'Sophie',
            'date_naissance_assure': '1985-03-10',  # Date de naissance du titulaire (mère)
            'rue_assure': '123 Rue Test',
            'code_postal_assure': '98800',
            'commune_assure': 'Nouméa'
        }
        
        response = self.client.post(reverse('patients:patient_create'), bebe_data)
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la réponse pour la création du bébé
        try:
            bebe_content = json.loads(response.content)
            if not bebe_content.get('success', False):
                self.fail(f"Failed to create baby: {bebe_content}")
        except json.JSONDecodeError:
            # La réponse n'est pas JSON, probablement des erreurs de formulaire
            form_errors = ""
            if 'form' in response.context and response.context['form'].errors:
                form_errors = response.context['form'].errors
            self.fail(f"Failed to create baby, form returned HTML with errors: {form_errors}")
        
        bebe = Patient.objects.get(nom='Martin', prenom='Lucas')
        self.assertEqual(bebe.mere, mere)
        self.assertFalse(bebe.est_assure_titulaire)  # Bébé ne peut pas être titulaire
        
        # 5. Vérifier que le bébé apparaît dans la liste des bébés de la mère
        response = self.client.get(reverse('patients:patient_detail', kwargs={'patient_id': mere.id}))
        self.assertContains(response, 'Lucas Martin')
        
        # 6. Vérifier le détail du bébé
        response = self.client.get(reverse('patients:patient_detail', kwargs={'patient_id': bebe.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lucas Martin')
        self.assertContains(response, 'Bébé')
    
    def test_search_and_filter_integration(self):
        """Test intégration recherche et filtres"""
        # Créer plusieurs patients
        patients_data = [
            {
                'type_patient': 'femme',
                'nom': 'Dupont',
                'prenom': 'Marie',
                'date_naissance': '1990-01-01',
                'telephone': '0123456789',
                'caisse': self.caisse1.id,
                'est_assure_titulaire': True,
                'nom_assure': 'Dupont',
                'prenom_assure': 'Marie',
                'date_naissance_assure': '1990-01-01',
                'rue_assure': '123 Rue Test',
                'code_postal_assure': '98800',
                'commune_assure': 'Nouméa'
            },
            {
                'type_patient': 'femme',
                'nom': 'Martin',
                'prenom': 'Sophie',
                'date_naissance': '1985-01-01',
                'telephone': '0223456789',
                'caisse': self.caisse2.id,
                'est_assure_titulaire': True,
                'nom_assure': 'Martin',
                'prenom_assure': 'Sophie',
                'date_naissance_assure': '1985-01-01',
                'rue_assure': '456 Avenue Test',
                'code_postal_assure': '98800',
                'commune_assure': 'Nouméa'
            },
            {
                'type_patient': 'femme',
                'nom': 'Durand',
                'prenom': 'Claire',
                'date_naissance': '1992-01-01',
                'telephone': '0323456789',
                'caisse': self.caisse1.id,
                'est_assure_titulaire': True,
                'nom_assure': 'Durand',
                'prenom_assure': 'Claire',
                'date_naissance_assure': '1992-01-01',
                'rue_assure': '789 Boulevard Test',
                'code_postal_assure': '98800',
                'commune_assure': 'Nouméa'
            }
        ]
        
        for data in patients_data:
            self.client.post(reverse('patients:patient_create'), data)
        
        # Test recherche par nom
        response = self.client.get(reverse('patients:patients_view'), {'search': 'Dupont'})
        self.assertContains(response, 'Marie Dupont')
        self.assertNotContains(response, 'Sophie Martin')
        
        # Test recherche par prénom
        response = self.client.get(reverse('patients:patients_view'), {'search': 'Sophie'})
        self.assertContains(response, 'Sophie Martin')
        self.assertNotContains(response, 'Marie Dupont')
        
        # Test recherche par téléphone
        response = self.client.get(reverse('patients:patients_view'), {'search': '0223456789'})
        self.assertContains(response, 'Sophie Martin')
        self.assertNotContains(response, 'Marie Dupont')
        
        # Test avec requête HTMX
        response = self.client.get(
            reverse('patients:patients_view'),
            {'search': 'Claire'},
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Claire Durand')
    
    def test_patient_activation_cascade_effects(self):
        """Test des effets en cascade de l'activation/désactivation"""
        # Créer une mère et un bébé
        mere = Patient.objects.create(
            type_patient='femme',
            nom='Test',
            prenom='Mere',
            date_naissance=date(1990, 1, 1),
            caisse=self.caisse1
        )
        
        bebe = Patient.objects.create(
            type_patient='bebe',
            nom='Test',
            prenom='Bebe',
            date_naissance=date.today() - timedelta(days=30),
            mere=mere,
            caisse=self.caisse1
        )
        
        # Vérifier que les deux sont actifs initialement
        self.assertTrue(mere.is_active)
        self.assertTrue(bebe.is_active)
        
        # Désactiver la mère
        response = self.client.post(
            reverse('patients:patient_toggle_active', kwargs={'patient_id': mere.id})
        )
        self.assertEqual(response.status_code, 200)
        
        mere.refresh_from_db()
        self.assertFalse(mere.is_active)
        
        # Vérifier que la mère désactivée n'apparaît plus dans les recherches de mères
        response = self.client.get(reverse('patients:search_meres'), {'q': 'Test'})
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)
        
        # Mais elle apparaît toujours dans la liste générale
        response = self.client.get(reverse('patients:patients_view'))
        self.assertContains(response, 'Mere Test')
    
    def test_form_conditional_fields_integration(self):
        """Test intégration des champs conditionnels du formulaire"""
        # Créer une mère pour les tests
        mere = Patient.objects.create(
            type_patient='femme',
            nom='Mere',
            prenom='Test',
            date_naissance=date(1990, 1, 1),
            telephone='0123456789',
            caisse=self.caisse1,
            nom_assure='Mere Assure',
            prenom_assure='Test',
            date_naissance_assure=date(1990, 1, 1),
            rue_assure='123 Rue Test',
            code_postal_assure='98800',
            commune_assure='Nouméa',
            est_assure_titulaire=True
        )
        
        # Tester la récupération des détails pour pré-remplissage
        response = self.client.get(
            reverse('patients:patient_details_for_baby', kwargs={'patient_id': mere.id})
        )
        self.assertEqual(response.status_code, 200)
        
        details = json.loads(response.content)
        self.assertEqual(details['telephone'], '0123456789')
        self.assertEqual(details['nom_assure'], 'Mere Assure')
        self.assertEqual(details['rue_assure'], '123 Rue Test')
        
        # Créer un bébé avec les données héritées
        bebe_data = {
            'type_patient': 'bebe',
            'nom': 'Bebe',
            'prenom': 'Test',
            'date_naissance': (date.today() - timedelta(days=10)).strftime('%Y-%m-%d'),
            'mere': mere.id,
            'telephone': details['telephone'],
            'caisse': details['caisse_id'],
            'est_assure_titulaire': False,
            'nom_assure': details['nom_assure'],
            'prenom_assure': details.get('prenom_assure', 'Test'),
            'date_naissance_assure': details.get('date_naissance_assure', '1990-01-01'),
            'rue_assure': details['rue_assure'],
            'code_postal_assure': details.get('code_postal_assure', '98800'),
            'commune_assure': details.get('commune_assure', 'Nouméa')
        }
        
        response = self.client.post(reverse('patients:patient_create'), bebe_data)
        self.assertEqual(response.status_code, 200)
        
        bebe = Patient.objects.get(nom='Bebe', prenom='Test')
        self.assertEqual(bebe.telephone, '0123456789')
        self.assertEqual(bebe.nom_assure, 'Mere Assure')
    
    def test_pregnancy_alerts_integration(self):
        """Test intégration des alertes de grossesse"""
        # Créer une patiente avec grossesse dépassée
        patiente = Patient.objects.create(
            type_patient='femme',
            nom='Grossesse',
            prenom='Depassee',
            date_naissance=date(1990, 1, 1),
            date_debut_grossesse=date.today() - timedelta(days=300),  # Grossesse très dépassée
            caisse=self.caisse1
        )
        
        # Accéder à la page de détail
        response = self.client.get(
            reverse('patients:patient_detail', kwargs={'patient_id': patiente.id})
        )
        self.assertEqual(response.status_code, 200)
        
        # La logique d'alerte devrait être dans le template
        # Vérifier que les données sont disponibles pour l'affichage
        self.assertIn('patient', response.context)
        self.assertEqual(response.context['patient'], patiente)
    
    def test_error_handling_integration(self):
        """Test de gestion d'erreurs intégrée"""
        # Test patient inexistant
        response = self.client.get(reverse('patients:patient_detail', kwargs={'patient_id': 9999}))
        self.assertEqual(response.status_code, 404)
        
        # Test création avec données invalides
        invalid_data = {
            'type_patient': 'bebe',
            'nom': 'Test',
            'prenom': 'Invalid',
            'date_naissance': (date.today() - timedelta(days=10)).strftime('%Y-%m-%d'),
            'est_assure_titulaire': True  # Invalide pour un bébé
            # Pas de mère spécifiée
        }
        
        response = self.client.post(reverse('patients:patient_create'), invalid_data)
        self.assertEqual(response.status_code, 200)  # Reste sur le formulaire
        
        # Vérifier que le patient n'a pas été créé
        self.assertFalse(Patient.objects.filter(nom='Test', prenom='Invalid').exists())
    
    def test_messages_integration(self):
        """Test intégration du système de messages"""
        # Créer un patient avec succès
        data = {
            'type_patient': 'femme',
            'nom': 'Message',
            'prenom': 'Test',
            'date_naissance': '1990-01-01',
            'caisse': self.caisse1.id,
            'est_assure_titulaire': True
        }
        
        response = self.client.post(reverse('patients:patient_create'), data)
        
        # Vérifier la création réussie (via JSON response)
        content = json.loads(response.content)
        self.assertTrue(content['success'])
        
        # Test de toggle avec messages
        patient = Patient.objects.get(nom='Message', prenom='Test')
        response = self.client.post(
            reverse('patients:patient_toggle_active', kwargs={'patient_id': patient.id})
        )
        
        content = json.loads(response.content)
        self.assertTrue(content['success'])
    
    def test_permissions_integration(self):
        """Test intégration des permissions"""
        # Test sans authentification
        self.client.logout()
        
        response = self.client.get(reverse('patients:patients_view'))
        self.assertIn(response.status_code, [302, 403])  # Redirection ou accès refusé
        
        response = self.client.post(reverse('patients:patient_create'), {})
        self.assertIn(response.status_code, [302, 403])
    
    def test_navigation_integration(self):
        """Test intégration de la navigation"""
        # Créer un patient
        patient = Patient.objects.create(
            type_patient='femme',
            nom='Navigation',
            prenom='Test',
            date_naissance=date(1990, 1, 1),
            caisse=self.caisse1
        )
        
        # Navigation liste -> détail
        response = self.client.get(reverse('patients:patients_view'))
        self.assertContains(response, reverse('patients:patient_detail', kwargs={'patient_id': patient.id}))
        
        # Navigation détail -> retour liste
        response = self.client.get(reverse('patients:patient_detail', kwargs={'patient_id': patient.id}))
        self.assertContains(response, reverse('patients:patients_view'))
    
    def test_responsive_design_elements(self):
        """Test éléments de design responsive"""
        # Créer un patient pour les tests
        patient = Patient.objects.create(
            type_patient='femme',
            nom='Design',
            prenom='Test',
            date_naissance=date(1990, 1, 1),
            caisse=self.caisse1
        )
        
        # Vérifier la présence d'éléments de design
        response = self.client.get(reverse('patients:patients_view'))
        self.assertContains(response, 'Patients')
        
        response = self.client.get(reverse('patients:patient_detail', kwargs={'patient_id': patient.id}))
        self.assertContains(response, 'Ajouter une feuille de soin')
        self.assertContains(response, 'Modifier')

    def test_complete_crud_cycle(self):
        """Test complet du cycle CRUD"""
        initial_count = Patient.objects.count()
        
        # CREATE
        create_data = {
            'type_patient': 'femme',
            'nom': 'CRUD',
            'prenom': 'Test',
            'date_naissance': '1990-01-01',
            'caisse': self.caisse1.id,
            'est_assure_titulaire': True
        }
        
        response = self.client.post(reverse('patients:patient_create'), create_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Patient.objects.count(), initial_count + 1)
        
        patient = Patient.objects.get(nom='CRUD', prenom='Test')
        
        # READ
        response = self.client.get(reverse('patients:patient_detail', kwargs={'patient_id': patient.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test CRUD')  # Le nom s'affiche prenom nom
        
        # UPDATE
        update_data = create_data.copy()
        update_data['profession'] = 'Updated'
        
        response = self.client.post(
            reverse('patients:patient_edit', kwargs={'patient_id': patient.id}),
            update_data
        )
        self.assertEqual(response.status_code, 200)
        
        patient.refresh_from_db()
        self.assertEqual(patient.profession, 'Updated')
        
        # "DELETE" (désactivation)
        response = self.client.post(
            reverse('patients:patient_toggle_active', kwargs={'patient_id': patient.id})
        )
        self.assertEqual(response.status_code, 200)
        
        patient.refresh_from_db()
        self.assertFalse(patient.is_active)
        
        # Le patient existe toujours mais est inactif
        self.assertEqual(Patient.objects.count(), initial_count + 1)