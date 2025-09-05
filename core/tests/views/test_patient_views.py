"""
Tests pour les vues Patient
Tests complets des fonctionnalités CRUD et API
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from datetime import date, timedelta
import json

from core.models import Patient, Caisse
from authentication.models import SageFemmeUser


User = get_user_model()


class PatientViewsTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.client = Client()
        
        # Créer un superutilisateur de test
        self.user = SageFemmeUser.objects.create_superuser(
            email='admin@maieutix.nc',
            password='testpass123'
        )
        
        # Créer une caisse
        self.caisse = Caisse.objects.create(
            nom="CAFAT"
        )
        
        # Créer des patients de test
        self.femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse,
            est_assure_titulaire=True
        )
        
        self.bebe = Patient.objects.create(
            type_patient='bebe',
            nom='Dupont',
            prenom='Lucas',
            date_naissance=date.today() - timedelta(days=30),
            mere=self.femme,
            caisse=self.caisse,
            est_assure_titulaire=False,
            nom_assure='Dupont',
            prenom_assure='Marie',
            date_naissance_assure=date(1990, 5, 15),
            rue_assure='123 Rue Test',
            code_postal_assure='98800',
            commune_assure='Noumea'
        )
        
        # Se connecter
        self.client.login(email='admin@maieutix.nc', password='testpass123')
    
    def test_patients_view_get(self):
        """Test de la vue liste des patients"""
        url = reverse('patients:patients_view')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Vérifier que les patients sont présents (dans l'ordre prenom nom)
        self.assertContains(response, 'Marie Dupont')
        self.assertContains(response, 'Lucas Dupont')
        self.assertIn('patients', response.context)
        self.assertEqual(response.context['section'], 'patients')
    
    def test_patients_view_search(self):
        """Test de la recherche dans la liste des patients"""
        url = reverse('patients:patients_view')
        response = self.client.get(url, {'search': 'Marie'})
        
        self.assertEqual(response.status_code, 200)
        # Marie Dupont est trouvée directement
        self.assertContains(response, 'Marie Dupont')
        # Lucas Dupont est aussi trouvé car sa mère s'appelle Marie
        self.assertContains(response, 'Lucas Dupont')
    
    def test_patients_view_htmx_request(self):
        """Test de la vue patients avec requête HTMX"""
        url = reverse('patients:patients_view')
        response = self.client.get(url, HTTP_HX_REQUEST='true')
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/patients/partials/patient_table.html')
    
    def test_patient_create_get(self):
        """Test GET du formulaire de création"""
        url = reverse('patients:patient_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nouveau patient')
        self.assertContains(response, 'Créer')
        self.assertIn('form', response.context)
    
    def test_patient_create_post_valid(self):
        """Test POST création patient valide"""
        url = reverse('patients:patient_create')
        data = {
            'type_patient': 'femme',
            'nom': 'Martin',
            'prenom': 'Sophie',
            'date_naissance': '1985-03-10',
            'telephone': '0123456789',
            'caisse': self.caisse.id,
            'est_assure_titulaire': True
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Patient.objects.filter(nom='Martin', prenom='Sophie').exists())
        
        # Vérifier la réponse JSON
        content = json.loads(response.content)
        self.assertTrue(content['success'])
        self.assertIn('redirect', content)
    
    def test_patient_create_post_invalid(self):
        """Test POST création patient invalide"""
        url = reverse('patients:patient_create')
        data = {
            'type_patient': 'femme',
            'nom': '',  # Nom requis
            'prenom': 'Sophie',
            'date_naissance': '1985-03-10'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Patient.objects.filter(prenom='Sophie').exists())
        self.assertContains(response, 'Nouveau patient')
    
    def test_patient_create_bebe_with_validation_error(self):
        """Test création bébé avec erreur de validation métier"""
        url = reverse('patients:patient_create')
        data = {
            'type_patient': 'bebe',
            'nom': 'Test',
            'prenom': 'Bebe',
            'date_naissance': date.today() - timedelta(days=10),
            'est_assure_titulaire': True,  # Invalide pour un bébé
            'mere': self.femme.id
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Patient.objects.filter(nom='Test', prenom='Bebe').exists())
    
    def test_patient_edit_get(self):
        """Test GET du formulaire de modification"""
        url = reverse('patients:patient_edit', kwargs={'patient_id': self.femme.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'Modifier {self.femme.nom_complet}')
        self.assertContains(response, 'Sauvegarder')
        self.assertIn('patient', response.context)
        self.assertEqual(response.context['patient'], self.femme)
    
    def test_patient_edit_post_valid(self):
        """Test POST modification patient valide"""
        url = reverse('patients:patient_edit', kwargs={'patient_id': self.femme.id})
        data = {
            'type_patient': 'femme',
            'nom': 'Dupont-Martin',  # Modification du nom
            'prenom': 'Marie',
            'date_naissance': '1990-05-15',
            'telephone': '0123456789',
            'caisse': self.caisse.id,
            'est_assure_titulaire': True
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.femme.refresh_from_db()
        self.assertEqual(self.femme.nom, 'Dupont-Martin')
        
        # Vérifier la réponse JSON
        content = json.loads(response.content)
        self.assertTrue(content['success'])
    
    def test_patient_edit_post_invalid(self):
        """Test POST modification patient invalide"""
        url = reverse('patients:patient_edit', kwargs={'patient_id': self.femme.id})
        data = {
            'type_patient': 'femme',
            'nom': '',  # Nom requis
            'prenom': 'Marie',
            'date_naissance': '1990-05-15'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.femme.refresh_from_db()
        self.assertEqual(self.femme.nom, 'Dupont')  # Pas de changement
    
    def test_patient_edit_nonexistent(self):
        """Test modification patient inexistant"""
        url = reverse('patients:patient_edit', kwargs={'patient_id': 9999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_patient_detail_view(self):
        """Test de la vue détail patient"""
        url = reverse('patients:patient_detail', kwargs={'patient_id': self.femme.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.femme.nom_complet)
        self.assertContains(response, 'Ajouter une feuille de soin')
        self.assertIn('patient', response.context)
        self.assertEqual(response.context['patient'], self.femme)
        
        # Vérifier les bébés pour une femme
        self.assertIn('bebes', response.context)
        bebes = response.context['bebes']
        self.assertIn(self.bebe, bebes)
    
    def test_patient_detail_bebe(self):
        """Test de la vue détail pour un bébé"""
        url = reverse('patients:patient_detail', kwargs={'patient_id': self.bebe.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.bebe.nom_complet)
        # Pour un bébé, pas de liste de bébés
        self.assertIsNone(response.context['bebes'])
    
    def test_patient_detail_modal(self):
        """Test de la vue détail en modal"""
        url = reverse('patients:patient_detail_modal', kwargs={'patient_id': self.femme.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/patients/patient_detail.html')
        self.assertIn('patient', response.context)
    
    def test_patient_toggle_active(self):
        """Test activation/désactivation patient"""
        url = reverse('patients:patient_toggle_active', kwargs={'patient_id': self.femme.id})
        
        # Vérifier état initial
        self.assertTrue(self.femme.is_active)
        
        # Désactiver
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        
        content = json.loads(response.content)
        self.assertTrue(content['success'])
        self.assertFalse(content['is_active'])
        
        self.femme.refresh_from_db()
        self.assertFalse(self.femme.is_active)
        
        # Réactiver
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        
        content = json.loads(response.content)
        self.assertTrue(content['success'])
        self.assertTrue(content['is_active'])
        
        self.femme.refresh_from_db()
        self.assertTrue(self.femme.is_active)
    
    def test_patient_toggle_active_nonexistent(self):
        """Test toggle patient inexistant"""
        url = reverse('patients:patient_toggle_active', kwargs={'patient_id': 9999})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_search_meres_view(self):
        """Test de l'API de recherche des mères"""
        url = reverse('patients:search_meres')
        response = self.client.get(url, {'q': 'Dup'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        
        mere_data = data[0]
        self.assertEqual(mere_data['id'], self.femme.id)
        self.assertEqual(mere_data['nom_complet'], self.femme.nom_complet)
        self.assertIn('date_naissance_formatted', mere_data)
    
    def test_search_meres_empty_query(self):
        """Test recherche mères avec query vide"""
        url = reverse('patients:search_meres')
        response = self.client.get(url, {'q': ''})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Doit retourner jusqu'à 50 résultats sans filtre
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)  # Au moins notre femme de test
    
    def test_search_meres_no_results(self):
        """Test recherche mères sans résultats"""
        url = reverse('patients:search_meres')
        response = self.client.get(url, {'q': 'Inexistant'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)
    
    def test_patient_details_for_baby_api(self):
        """Test de l'API de détails patient pour bébé"""
        url = reverse('patients:patient_details_for_baby', kwargs={'patient_id': self.femme.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertEqual(data['telephone'], self.femme.telephone)
        self.assertEqual(data['caisse_id'], self.caisse.id)
    
    def test_patient_details_for_baby_invalid_type(self):
        """Test API détails pour patient non-femme"""
        url = reverse('patients:patient_details_for_baby', kwargs={'patient_id': self.bebe.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_patient_details_for_baby_nonexistent(self):
        """Test API détails patient inexistant"""
        url = reverse('patients:patient_details_for_baby', kwargs={'patient_id': 9999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_views_require_login(self):
        """Test que toutes les vues nécessitent une authentification"""
        self.client.logout()
        
        urls = [
            reverse('patients:patients_view'),
            reverse('patients:patient_create'),
            reverse('patients:patient_edit', kwargs={'patient_id': self.femme.id}),
            reverse('patients:patient_detail', kwargs={'patient_id': self.femme.id}),
            reverse('patients:search_meres'),
            reverse('patients:patient_details_for_baby', kwargs={'patient_id': self.femme.id}),
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Redirection vers login
    
    def test_post_views_require_login(self):
        """Test que les vues POST nécessitent une authentification"""
        self.client.logout()
        
        urls = [
            reverse('patients:patient_create'),
            reverse('patients:patient_edit', kwargs={'patient_id': self.femme.id}),
            reverse('patients:patient_toggle_active', kwargs={'patient_id': self.femme.id}),
        ]
        
        for url in urls:
            response = self.client.post(url, {})
            self.assertEqual(response.status_code, 302)  # Redirection vers login
    
    def test_patient_view_with_inactive_patients(self):
        """Test que les patients inactifs sont inclus dans la liste"""
        # Désactiver un patient
        self.femme.is_active = False
        self.femme.save()
        
        url = reverse('patients:patients_view')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Doit toujours contenir le patient inactif
        self.assertContains(response, self.femme.nom_complet)
    
    def test_search_meres_only_active_femmes(self):
        """Test que la recherche mères ne retourne que les femmes actives"""
        # Désactiver la femme
        self.femme.is_active = False
        self.femme.save()
        
        url = reverse('patients:search_meres')
        response = self.client.get(url, {'q': 'Dupont'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)  # Pas de résultats car femme inactive
    
    def test_patient_form_initial_max_dates(self):
        """Test que le formulaire a des dates max correctes"""
        url = reverse('patients:patient_create')
        response = self.client.get(url)
        
        form = response.context['form']
        today_str = date.today().strftime('%Y-%m-%d')
        
        # Vérifier que les champs de date ont la limite à aujourd'hui
        self.assertEqual(form.fields['date_naissance'].widget.attrs['max'], today_str)
        self.assertEqual(form.fields['date_debut_grossesse'].widget.attrs['max'], today_str)
        self.assertEqual(form.fields['date_naissance_assure'].widget.attrs['max'], today_str)