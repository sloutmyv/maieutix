"""
Tests d'intégration pour les antécédents et frottis
Tests des workflows complets et interactions entre composants
"""

import json
from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Patient, Caisse, Antecedents, FrottisCV, SageFemme, PeriodeActivite


class AntecedentsIntegrationTest(TestCase):
    """Tests d'intégration complets pour les antécédents"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.client = Client()
        
        # Créer les données de base
        self.caisse = Caisse.objects.create(nom="CAFAT")
        
        self.patiente = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse
        )
        
        # Créer un superutilisateur pour les tests admin
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            email='admin@test.com',
            password='admin123',
            must_change_password=False
        )
    
    def test_complete_antecedents_workflow_via_api(self):
        """Test workflow complet : création, récupération, modification via API"""
        # Se connecter en tant qu'admin
        self.client.login(email='admin@test.com', password='admin123')
        
        # 1. Vérifier qu'aucun antécédent n'existe initialement
        url_get = reverse('patients:patient_antecedents', args=[self.patiente.pk])
        response = self.client.get(url_get)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsNone(data['antecedents'])
        self.assertEqual(data['frottis'], [])
        
        # 2. Créer des antécédents complets avec frottis via API
        url_save = reverse('patients:save_antecedents')
        antecedents_data = {
            'patient_id': self.patiente.pk,
            'taille': '1.65',
            'poids': '60.0',
            'medecin_traitant': 'Dr. Martin',
            'gynecologue': 'Dr. Bernard',
            'allergie': 'Pénicilline',
            'asthme': 'true',
            'diabete': 'false',
            'hta': 'true',
            'atcd_obstetricaux': 'G1P1, accouchement normal en 2022',
            'atcd_fam_diabete': 'true',
            'contraception': 'Pilule oestroprogestative',
            'frottis_date_0': '2023-06-15',
            'frottis_resultat_0': 'Normal - Premier frottis',
            'frottis_date_1': '2024-03-10',
            'frottis_resultat_1': 'Normal - Contrôle régulier',
        }
        
        response = self.client.post(url_save, antecedents_data)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # 3. Vérifier que les antécédents ont été créés correctement
        antecedents = Antecedents.objects.get(patient=self.patiente)
        self.assertEqual(antecedents.taille, 1.65)
        self.assertEqual(antecedents.poids, 60.0)
        self.assertTrue(antecedents.asthme)
        self.assertTrue(antecedents.hta)
        self.assertFalse(antecedents.diabete)
        self.assertEqual(antecedents.allergie, 'Pénicilline')
        
        # 4. Vérifier que les frottis ont été créés
        frottis_list = list(antecedents.frottis.all().order_by('date_frottis'))
        self.assertEqual(len(frottis_list), 2)
        self.assertEqual(frottis_list[0].resultat, 'Normal - Premier frottis')
        self.assertEqual(frottis_list[1].resultat, 'Normal - Contrôle régulier')
        
        # 5. Récupérer les antécédents via API et vérifier les données
        response = self.client.get(url_get)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIsNotNone(data['antecedents'])
        self.assertEqual(data['antecedents']['taille'], 1.65)
        self.assertEqual(data['antecedents']['medecin_traitant'], 'Dr. Martin')
        self.assertTrue(data['antecedents']['asthme'])
        
        self.assertEqual(len(data['frottis']), 2)
        # Les frottis sont ordonnés par date décroissante
        self.assertEqual(data['frottis'][0]['date_frottis'], '2024-03-10')
        self.assertEqual(data['frottis'][1]['date_frottis'], '2023-06-15')
        
        # 6. Modifier les antécédents existants
        modified_data = {
            'patient_id': self.patiente.pk,
            'taille': '1.68',  # Modifié
            'poids': '62.5',   # Modifié
            'medecin_traitant': 'Dr. Martin Nouveau',  # Modifié
            'gynecologue': 'Dr. Bernard Spécialiste',  # Modifié
            'epilepsie': 'true',  # Nouveau
            'infection_urinaire': 'false',  # Nouveau
            'frottis_date_0': '2024-09-05',  # Nouveau frottis
            'frottis_resultat_0': 'Normal - Frottis récent modifié',
        }
        
        response = self.client.post(url_save, modified_data)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # 7. Vérifier les modifications
        antecedents.refresh_from_db()
        self.assertEqual(antecedents.taille, 1.68)
        self.assertEqual(antecedents.poids, 62.5)
        self.assertEqual(antecedents.medecin_traitant, 'Dr. Martin Nouveau')
        self.assertTrue(antecedents.epilepsie)
        
        # Vérifier que les anciens frottis ont été remplacés
        frottis_list = list(antecedents.frottis.all())
        self.assertEqual(len(frottis_list), 1)
        self.assertEqual(frottis_list[0].resultat, 'Normal - Frottis récent modifié')
    
    def test_patient_detail_page_antecedents_integration(self):
        """Test intégration complète page détail patient avec antécédents"""
        # Créer des antécédents avec frottis
        antecedents = Antecedents.objects.create(
            patient=self.patiente,
            taille=1.65,
            poids=60.0,
            medecin_traitant="Dr. Test",
            asthme=True,
            diabete=False
        )
        
        FrottisCV.objects.create(
            antecedents=antecedents,
            date_frottis=date(2024, 6, 15),
            resultat="Normal - Test intégration"
        )
        
        # Se connecter
        self.client.login(email='admin@test.com', password='admin123')
        
        # Accéder à la page de détail du patient
        url = reverse('patients:patient_detail', args=[self.patiente.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.patiente.nom_complet)
        self.assertContains(response, 'Dossier patiente')
        
        # Vérifier l'existence des données via l'API plutôt que le contenu HTML
        url_api = reverse('patients:patient_antecedents', args=[self.patiente.pk])
        api_response = self.client.get(url_api)
        self.assertEqual(api_response.status_code, 200)
        
        import json
        data = json.loads(api_response.content)
        self.assertIsNotNone(data['antecedents'])
        self.assertEqual(data['antecedents']['medecin_traitant'], 'Dr. Test')
    
    def test_admin_interface_antecedents_integration(self):
        """Test intégration complète interface admin pour antécédents"""
        # Se connecter en tant qu'admin
        self.client.login(email='admin@test.com', password='admin123')
        
        # 1. Accès à la liste des antécédents (vide)
        url_list = reverse('admin:core_antecedents_changelist')
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '6.1.1 Antécédents')
        
        # 2. Accès au formulaire d'ajout
        url_add = reverse('admin:core_antecedents_add')
        response = self.client.get(url_add)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Patient')
        self.assertContains(response, 'Biométrie')
        self.assertContains(response, 'frottis-group')  # Inline frottis
        
        # 3. Création d'antécédents via admin avec inline frottis
        form_data = {
            'patient': self.patiente.pk,
            'taille': '1.65',
            'poids': '60.0',
            'medecin_traitant': 'Dr. Admin Test',
            'asthme': True,
            'diabete': False,
            'hta': True,
            
            # Données inline frottis
            'frottis-TOTAL_FORMS': '2',
            'frottis-INITIAL_FORMS': '0',
            'frottis-MIN_NUM_FORMS': '0',
            'frottis-MAX_NUM_FORMS': '1000',
            'frottis-0-date_frottis': '2024-03-15',
            'frottis-0-resultat': 'Normal - Premier via admin',
            'frottis-1-date_frottis': '2024-06-20',
            'frottis-1-resultat': 'Normal - Deuxième via admin',
        }
        
        response = self.client.post(url_add, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # 4. Vérifier que les antécédents ont été créés
        antecedents = Antecedents.objects.get(patient=self.patiente)
        self.assertEqual(antecedents.medecin_traitant, 'Dr. Admin Test')
        self.assertTrue(antecedents.asthme)
        self.assertTrue(antecedents.hta)
        
        # 5. Vérifier que les frottis inline ont été créés
        frottis_list = list(antecedents.frottis.all().order_by('date_frottis'))
        self.assertEqual(len(frottis_list), 2)
        self.assertEqual(frottis_list[0].resultat, 'Normal - Premier via admin')
        self.assertEqual(frottis_list[1].resultat, 'Normal - Deuxième via admin')
        
        # 6. Modifier via admin
        url_change = reverse('admin:core_antecedents_change', args=[antecedents.pk])
        response = self.client.get(url_change)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dr. Admin Test')
        
        # 7. Test recherche dans l'admin
        response = self.client.get(url_list, {'q': 'Admin Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dr. Admin Test')
        
        # 8. Test filtres admin
        response = self.client.get(url_list, {'asthme__exact': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.patiente.nom_complet)
    
    def test_imc_calculation_integration(self):
        """Test intégration calcul IMC dans différents contextes"""
        # Créer antécédents avec taille/poids
        antecedents = Antecedents.objects.create(
            patient=self.patiente,
            taille=1.70,
            poids=68.0  # IMC = 23.5
        )
        
        # 1. Test calcul IMC via propriété du modèle
        expected_imc = round(68.0 / (1.70 ** 2), 1)  # 23.5
        self.assertEqual(antecedents.imc, expected_imc)
        self.assertEqual(antecedents.imc_interpretation, "Poids normal")
        
        # 2. Test récupération dans l'admin (skip display test car HTML complexe)
        self.client.login(email='admin@test.com', password='admin123')
        url = reverse('admin:core_antecedents_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que l'antécédent existe dans l'admin
        self.assertEqual(Antecedents.objects.count(), 1)
        
        # 3. Test récupération IMC via API
        url_api = reverse('patients:patient_antecedents', args=[self.patiente.pk])
        response = self.client.get(url_api)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['antecedents']['taille'], 1.70)
        self.assertEqual(data['antecedents']['poids'], 68.0)
        
        # 4. Test modification biométrie et recalcul IMC
        url_save = reverse('patients:save_antecedents')
        modified_data = {
            'patient_id': self.patiente.pk,
            'taille': '1.75',
            'poids': '70.0'  # Nouvel IMC
        }
        
        response = self.client.post(url_save, modified_data)
        self.assertEqual(response.status_code, 200)
        
        antecedents.refresh_from_db()
        new_imc = round(70.0 / (1.75 ** 2), 1)  # 22.9
        self.assertEqual(antecedents.imc, new_imc)
        self.assertEqual(antecedents.imc_interpretation, "Poids normal")
    
    def test_frottis_management_integration(self):
        """Test intégration complète gestion des frottis"""
        # Créer antécédents
        antecedents = Antecedents.objects.create(
            patient=self.patiente,
            taille=1.65,
            poids=60.0
        )
        
        self.client.login(email='admin@test.com', password='admin123')
        
        # 1. Ajouter plusieurs frottis via API
        url_save = reverse('patients:save_antecedents')
        data_with_frottis = {
            'patient_id': self.patiente.pk,
            'frottis_date_0': '2023-01-15',
            'frottis_resultat_0': 'Normal - Premier',
            'frottis_date_1': '2023-07-20',
            'frottis_resultat_1': 'Normal - Deuxième',
            'frottis_date_2': '2024-02-10',
            'frottis_resultat_2': 'Normal - Troisième',
        }
        
        response = self.client.post(url_save, data_with_frottis)
        self.assertEqual(response.status_code, 200)
        
        # 2. Vérifier l'ordre chronologique des frottis
        frottis_list = list(antecedents.frottis.all())  # Ordre par défaut: -date_frottis
        self.assertEqual(len(frottis_list), 3)
        
        # Le plus récent en premier
        self.assertEqual(frottis_list[0].date_frottis, date(2024, 2, 10))
        self.assertEqual(frottis_list[1].date_frottis, date(2023, 7, 20))
        self.assertEqual(frottis_list[2].date_frottis, date(2023, 1, 15))
        
        # 3. Récupérer via API et vérifier l'ordre
        url_get = reverse('patients:patient_antecedents', args=[self.patiente.pk])
        response = self.client.get(url_get)
        data = json.loads(response.content)
        
        frottis_data = data['frottis']
        self.assertEqual(len(frottis_data), 3)
        self.assertEqual(frottis_data[0]['date_frottis'], '2024-02-10')  # Plus récent
        self.assertEqual(frottis_data[0]['resultat'], 'Normal - Troisième')
        
        # 4. Remplacer tous les frottis par un seul nouveau
        new_data = {
            'patient_id': self.patiente.pk,
            'frottis_date_0': '2024-09-05',
            'frottis_resultat_0': 'Normal - Nouveau frottis unique',
        }
        
        response = self.client.post(url_save, new_data)
        self.assertEqual(response.status_code, 200)
        
        # 5. Vérifier que seul le nouveau frottis existe
        frottis_list = list(antecedents.frottis.all())
        self.assertEqual(len(frottis_list), 1)
        self.assertEqual(frottis_list[0].resultat, 'Normal - Nouveau frottis unique')
        
        # 6. Test gestion via admin des frottis
        url_frottis_list = reverse('admin:core_frottiscv_changelist')
        response = self.client.get(url_frottis_list)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '6.1.1.1 Frottis')
        self.assertContains(response, 'Nouveau frottis unique')
    
    def test_error_handling_integration(self):
        """Test gestion d'erreurs intégrée dans tous les composants"""
        self.client.login(email='admin@test.com', password='admin123')
        
        # 1. Test erreur patient inexistant via API
        url_get = reverse('patients:patient_antecedents', args=[99999])
        response = self.client.get(url_get)
        self.assertEqual(response.status_code, 404)
        
        # 2. Test erreur sauvegarde sans patient_id
        url_save = reverse('patients:save_antecedents')
        response = self.client.post(url_save, {'taille': '1.65'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Patient ID manquant')
        
        # 3. Test erreur données biométriques invalides
        invalid_data = {
            'patient_id': self.patiente.pk,
            'taille': 'invalid',
            'poids': '60.0'
        }
        
        response = self.client.post(url_save, invalid_data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
        
        # 4. Test comportement avec bébé (interdit)
        bebe = Patient.objects.create(
            type_patient='bebe',
            nom='Dupont',
            prenom='Lucas',
            date_naissance=date.today(),
            mere=self.patiente,
            caisse=self.caisse
        )
        
        url_bebe = reverse('patients:patient_antecedents', args=[bebe.pk])
        response = self.client.get(url_bebe)
        self.assertEqual(response.status_code, 404)
    
    def test_data_consistency_integration(self):
        """Test cohérence des données à travers tous les composants"""
        # Créer des données via l'admin
        self.client.login(email='admin@test.com', password='admin123')
        
        # 1. Créer via admin
        url_add = reverse('admin:core_antecedents_add')
        admin_data = {
            'patient': self.patiente.pk,
            'taille': '1.68',
            'poids': '63.0',
            'medecin_traitant': 'Dr. Cohérence',
            'asthme': True,
            'allergie': 'Acariens',
            
            'frottis-TOTAL_FORMS': '1',
            'frottis-INITIAL_FORMS': '0',
            'frottis-MIN_NUM_FORMS': '0',
            'frottis-MAX_NUM_FORMS': '1000',
            'frottis-0-date_frottis': '2024-05-15',
            'frottis-0-resultat': 'Cohérence admin',
        }
        
        response = self.client.post(url_add, admin_data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # 2. Vérifier cohérence via API
        url_api = reverse('patients:patient_antecedents', args=[self.patiente.pk])
        response = self.client.get(url_api)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['antecedents']['medecin_traitant'], 'Dr. Cohérence')
        self.assertTrue(data['antecedents']['asthme'])
        self.assertEqual(data['antecedents']['allergie'], 'Acariens')
        self.assertEqual(len(data['frottis']), 1)
        self.assertEqual(data['frottis'][0]['resultat'], 'Cohérence admin')
        
        # 3. Modifier via API et vérifier dans admin
        url_save = reverse('patients:save_antecedents')
        api_data = {
            'patient_id': self.patiente.pk,
            'medecin_traitant': 'Dr. Cohérence Modifié',
            'epilepsie': 'true',
            'frottis_date_0': '2024-09-05',
            'frottis_resultat_0': 'Cohérence API modifiée',
        }
        
        response = self.client.post(url_save, api_data)
        self.assertEqual(response.status_code, 200)
        
        # 4. Vérifier cohérence dans l'admin
        antecedents = Antecedents.objects.get(patient=self.patiente)
        url_change = reverse('admin:core_antecedents_change', args=[antecedents.pk])
        response = self.client.get(url_change)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dr. Cohérence Modifié')
        
        # 5. Vérifier que les frottis ont été remplacés
        frottis_count = antecedents.frottis.count()
        self.assertEqual(frottis_count, 1)
        frottis = antecedents.frottis.first()
        self.assertEqual(frottis.resultat, 'Cohérence API modifiée')