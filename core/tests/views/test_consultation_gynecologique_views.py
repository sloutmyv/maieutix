"""
Tests pour les vues ConsultationGynecologique
Tests complets des fonctionnalités CRUD et API
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from datetime import date, timedelta
import json

from core.models import ConsultationGynecologique, Patient, Caisse, SageFemme
from authentication.models import SageFemmeUser


User = get_user_model()


class ConsultationGynecologiqueViewsTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.client = Client()
        
        # Créer un superutilisateur de test
        self.user = SageFemmeUser.objects.create_superuser(
            email='admin@maieutix.nc',
            password='testpass123'
        )
        
        # Créer une sage-femme associée
        self.sage_femme = SageFemme.objects.create(
            user=self.user,
            nom='Martin',
            prenom='Dr Sophie',
            titre='Sage-Femme',
            telephone='0987654321',
            email='sophie.martin@test.com',
            numero_cafat='12345',
            ridet='RIDET123',
            rib='RIB123456789',
            banque='BCI',
            situation='titulaire'
        )
        
        # Créer une caisse
        self.caisse = Caisse.objects.create(
            nom="CAFAT"
        )
        
        # Créer des patients de test
        self.patient_femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse
        )
        
        self.patient_bebe = Patient.objects.create(
            type_patient='bebe',
            nom='Petit',
            prenom='Lucas',
            date_naissance=date.today() - timedelta(days=30),
            caisse=self.caisse
        )
        
        # Créer une consultation test
        self.consultation = ConsultationGynecologique.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today(),
            tension_systolique=120,
            tension_diastolique=80,
            poids=65.5,
            motif="Consultation de routine",
            examen="RAS",
            created_by=self.sage_femme
        )
        
        # Connexion de l'utilisateur
        self.client.login(email='admin@maieutix.nc', password='testpass123')

    def test_patient_consultations_view_get(self):
        """Test de la vue patient_consultations en GET"""
        url = reverse('patients:patient_consultations', args=[self.patient_femme.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.consultation.motif)
        self.assertIn('consultations', response.context)
        self.assertIn('patient', response.context)
        self.assertEqual(response.context['patient'], self.patient_femme)

    def test_patient_consultations_view_not_femme(self):
        """Test patient_consultations avec un patient non-femme"""
        url = reverse('patients:patient_consultations', args=[self.patient_bebe.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['consultations']), 0)
        self.assertIn('error', response.context)
        self.assertIn('réservées aux femmes', response.context['error'])

    def test_consultation_modal_view_get(self):
        """Test de la vue consultation_modal en GET"""
        url = reverse('patients:consultation_modal', args=[self.patient_femme.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('patient', response.context)
        self.assertEqual(response.context['patient'], self.patient_femme)

    def test_consultation_modal_view_not_femme(self):
        """Test consultation_modal avec patient non-femme"""
        url = reverse('patients:consultation_modal', args=[self.patient_bebe.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertIn('error', data)

    def test_consultation_modal_view_post_valid(self):
        """Test consultation_modal POST avec données valides"""
        url = reverse('patients:consultation_modal', args=[self.patient_femme.id])
        data = {
            'patient': self.patient_femme.id,
            'date_consultation': date.today(),
            'tension_systolique': 130,
            'tension_diastolique': 85,
            'poids': 67.0,
            'motif': 'Nouvelle consultation',
            'examen': 'Examen normal',
            'prescription': 'Repos'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('consultation_id', response_data)

    def test_consultation_modal_view_post_invalid(self):
        """Test consultation_modal POST avec données invalides"""
        url = reverse('patients:consultation_modal', args=[self.patient_femme.id])
        data = {
            'patient': self.patient_femme.id,
            'date_consultation': date.today() + timedelta(days=1),  # Date future
            'motif': 'Test invalide'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)

    def test_save_consultation_view_valid(self):
        """Test de la vue save_consultation avec données valides"""
        url = reverse('patients:save_consultation')
        data = {
            'patient_id': self.patient_femme.id,
            'date_consultation': date.today().isoformat(),
            'tension_systolique': '140',
            'tension_diastolique': '90',
            'poids': '70.5',
            'motif': 'Consultation via API',
            'examen': 'Examen complet',
            'prescription': 'Médicaments prescrits',
            'notes': 'Notes importantes'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('consultation', response_data)

    def test_save_consultation_view_missing_patient_id(self):
        """Test save_consultation sans patient_id"""
        url = reverse('patients:save_consultation')
        data = {
            'motif': 'Test sans patient'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)

    def test_save_consultation_view_not_femme(self):
        """Test save_consultation avec patient non-femme"""
        url = reverse('patients:save_consultation')
        data = {
            'patient_id': self.patient_bebe.id,
            'motif': 'Test patient bébé'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)

    def test_save_consultation_view_invalid_data(self):
        """Test save_consultation avec données invalides"""
        url = reverse('patients:save_consultation')
        data = {
            'patient_id': self.patient_femme.id,
            'date_consultation': (date.today() + timedelta(days=1)).isoformat(),  # Future
            'motif': 'Test date future'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)

    def test_delete_consultation_view(self):
        """Test de la vue delete_consultation"""
        url = reverse('patients:delete_consultation', args=[self.consultation.id])
        
        # Vérifier que la consultation existe
        self.assertTrue(ConsultationGynecologique.objects.filter(id=self.consultation.id).exists())
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la consultation a été supprimée
        self.assertFalse(ConsultationGynecologique.objects.filter(id=self.consultation.id).exists())

    def test_consultation_detail_view(self):
        """Test de la vue consultation_detail"""
        url = reverse('patients:consultation_detail', args=[self.consultation.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('consultation', response.context)
        self.assertEqual(response.context['consultation'], self.consultation)

    def test_consultation_quick_form_view(self):
        """Test de la vue consultation_quick_form"""
        url = reverse('patients:consultation_quick_form', args=[self.patient_femme.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('patient', response.context)
        self.assertEqual(response.context['patient'], self.patient_femme)

    def test_consultation_quick_form_view_not_femme(self):
        """Test consultation_quick_form avec patient non-femme"""
        url = reverse('patients:consultation_quick_form', args=[self.patient_bebe.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['form'])
        self.assertIn('error', response.context)

    def test_save_quick_consultation_view_valid(self):
        """Test de la vue save_quick_consultation avec données valides"""
        url = reverse('patients:save_quick_consultation', args=[self.patient_femme.id])
        data = {
            'date_consultation': date.today(),
            'motif': 'Consultation rapide',
            'poids': '68.0',
            'examen': 'Examen rapide'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('HX-Trigger', response.headers)

    def test_save_quick_consultation_view_invalid(self):
        """Test save_quick_consultation avec données invalides"""
        url = reverse('patients:save_quick_consultation', args=[self.patient_femme.id])
        data = {
            # Pas de motif (requis)
            'date_consultation': date.today(),
            'poids': '68.0'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)

    def test_save_quick_consultation_view_not_femme(self):
        """Test save_quick_consultation avec patient non-femme"""
        url = reverse('patients:save_quick_consultation', args=[self.patient_bebe.id])
        data = {
            'motif': 'Test bébé'
        }
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)  # Method not allowed for GET
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)

    def test_unauthorized_access(self):
        """Test accès non autorisé aux vues"""
        self.client.logout()
        
        views_to_test = [
            ('patients:patient_consultations', [self.patient_femme.id]),
            ('patients:consultation_modal', [self.patient_femme.id]),
            ('patients:save_consultation', []),
            ('patients:consultation_detail', [self.consultation.id]),
            ('patients:consultation_quick_form', [self.patient_femme.id]),
            ('patients:save_quick_consultation', [self.patient_femme.id]),
        ]
        
        for view_name, args in views_to_test:
            url = reverse(view_name, args=args)
            response = self.client.get(url)
            
            # Doit rediriger vers la page de connexion
            self.assertIn(response.status_code, [302, 405])  # 405 pour POST only

    def test_sage_femme_association(self):
        """Test que les consultations sont associées à la sage-femme connectée"""
        url = reverse('patients:save_consultation')
        data = {
            'patient_id': self.patient_femme.id,
            'motif': 'Test association sage-femme'
        }
        
        response = self.client.post(url, data)
        response_data = json.loads(response.content)
        
        consultation_id = response_data['consultation']['id']
        consultation = ConsultationGynecologique.objects.get(id=consultation_id)
        
        self.assertEqual(consultation.created_by, self.sage_femme)

    def test_error_handling_in_views(self):
        """Test de la gestion d'erreurs dans les vues"""
        # Simuler une erreur en supprimant le patient pendant une requête
        url = reverse('patients:save_consultation')
        data = {
            'patient_id': 99999,  # Patient inexistant
            'motif': 'Test erreur'
        }
        
        response = self.client.post(url, data)
        
        # L'erreur est gérée par le catch général et retourne 200 avec une erreur JSON
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])

    def test_data_types_conversion(self):
        """Test de la conversion des types de données"""
        url = reverse('patients:save_consultation')
        data = {
            'patient_id': self.patient_femme.id,
            'tension_systolique': '130',  # String valide convertible en int
            'tension_diastolique': '85',
            'poids': '67.5',  # String valide convertible en float
            'motif': 'Test conversion types'
        }
        
        response = self.client.post(url, data)
        
        # Doit gérer correctement les conversions valides
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

    def test_ajax_response_format(self):
        """Test du format des réponses AJAX"""
        url = reverse('patients:save_consultation')
        data = {
            'patient_id': self.patient_femme.id,
            'tension_systolique': '120',
            'tension_diastolique': '80',
            'poids': '65.5',
            'motif': 'Test format réponse'
        }
        
        response = self.client.post(url, data)
        response_data = json.loads(response.content)
        
        # Vérifier la structure de la réponse
        self.assertIn('success', response_data)
        self.assertIn('message', response_data)
        self.assertIn('consultation', response_data)
        
        consultation_data = response_data['consultation']
        self.assertIn('id', consultation_data)
        self.assertIn('date_consultation', consultation_data)
        self.assertIn('motif', consultation_data)
        self.assertIn('tension_complete', consultation_data)
        self.assertIn('tension_interpretation', consultation_data)