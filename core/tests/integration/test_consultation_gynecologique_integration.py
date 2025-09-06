"""
Tests d'intégration pour les consultations gynécologiques
Tests complets des workflows et interactions entre composants
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from datetime import date, timedelta
import json

from core.models import ConsultationGynecologique, Patient, Caisse, SageFemme, Antecedents
from authentication.models import SageFemmeUser


User = get_user_model()


class ConsultationGynecologiqueIntegrationTest(TestCase):
    
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
        
        # Créer des patients
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
        
        # Créer des antécédents avec taille pour tester l'IMC
        self.antecedents = Antecedents.objects.create(
            patient=self.patient_femme,
            taille=1.65
        )
        
        # Se connecter
        self.client.login(email='admin@maieutix.nc', password='testpass123')

    def test_complete_consultation_workflow(self):
        """Test complet du workflow de consultation gynécologique"""
        # 1. Accéder à la page patiente
        patient_url = reverse('patients:patient_detail', args=[self.patient_femme.id])
        response = self.client.get(patient_url)
        self.assertEqual(response.status_code, 200)
        
        # 2. Vérifier qu'il n'y a pas encore de consultations
        consultations_url = reverse('patients:patient_consultations', args=[self.patient_femme.id])
        response = self.client.get(consultations_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['consultations']), 0)
        
        # 3. Ouvrir le modal de consultation
        modal_url = reverse('patients:consultation_modal', args=[self.patient_femme.id])
        response = self.client.get(modal_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        
        # 4. Créer une consultation via le modal
        consultation_data = {
            'patient': self.patient_femme.id,
            'date_consultation': date.today(),
            'tension_systolique': 120,
            'tension_diastolique': 80,
            'poids': 65.5,
            'motif': 'Consultation de routine',
            'examen': 'Examen normal, RAS',
            'prescription': 'Vitamines prénatales',
            'notes': 'Patiente en bonne santé'
        }
        
        response = self.client.post(modal_url, consultation_data)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        consultation_id = response_data['consultation_id']
        
        # 5. Vérifier que la consultation a été créée
        consultation = ConsultationGynecologique.objects.get(id=consultation_id)
        self.assertEqual(consultation.patient, self.patient_femme)
        self.assertEqual(consultation.motif, 'Consultation de routine')
        self.assertEqual(consultation.tension_systolique, 120)
        self.assertEqual(consultation.created_by, self.sage_femme)
        
        # 6. Vérifier l'affichage de la consultation dans l'historique
        response = self.client.get(consultations_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['consultations']), 1)
        self.assertContains(response, 'Consultation de routine')
        self.assertContains(response, '120/80 mmHg')
        
        # 7. Consulter les détails de la consultation
        detail_url = reverse('patients:consultation_detail', args=[consultation_id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['consultation'], consultation)

    def test_consultation_quick_form_workflow(self):
        """Test du workflow avec le formulaire rapide"""
        # 1. Accéder au formulaire rapide
        quick_form_url = reverse('patients:consultation_quick_form', args=[self.patient_femme.id])
        response = self.client.get(quick_form_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        
        # 2. Soumettre une consultation rapide
        quick_data = {
            'date_consultation': date.today(),
            'motif': 'Consultation rapide',
            'poids': 67.0,
            'examen': 'Examen de routine'
        }
        
        save_quick_url = reverse('patients:save_quick_consultation', args=[self.patient_femme.id])
        response = self.client.post(save_quick_url, quick_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('HX-Trigger', response.headers)
        
        # 3. Vérifier que la consultation est créée
        consultation = ConsultationGynecologique.objects.filter(
            patient=self.patient_femme,
            motif='Consultation rapide'
        ).first()
        self.assertIsNotNone(consultation)
        self.assertEqual(consultation.poids, 67.0)

    def test_consultation_api_workflow(self):
        """Test du workflow via l'API de sauvegarde"""
        # 1. Sauvegarder via l'API
        api_url = reverse('patients:save_consultation')
        api_data = {
            'patient_id': self.patient_femme.id,
            'date_consultation': date.today().isoformat(),
            'tension_systolique': '140',
            'tension_diastolique': '90',
            'poids': '70.0',
            'motif': 'Consultation via API',
            'examen': 'Hypertension légère détectée',
            'prescription': 'Surveillance tension',
            'notes': 'Contrôle dans 2 semaines'
        }
        
        response = self.client.post(api_url, api_data)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # 2. Vérifier les données calculées
        consultation_data = response_data['consultation']
        self.assertEqual(consultation_data['tension_complete'], '140/90 mmHg')
        self.assertEqual(consultation_data['tension_interpretation'], 'Hypertension stade 2')  # 140/90 = stade 2
        self.assertIsNotNone(consultation_data['imc'])  # IMC calculé avec antécédents

    def test_consultation_with_imc_calculation(self):
        """Test du calcul d'IMC intégré"""
        consultation_data = {
            'patient_id': self.patient_femme.id,
            'poids': '65.5',
            'motif': 'Test IMC'
        }
        
        api_url = reverse('patients:save_consultation')
        response = self.client.post(api_url, consultation_data)
        response_data = json.loads(response.content)
        
        # Vérifier que l'IMC est calculé (65.5 / 1.65²)
        expected_imc = round(65.5 / (1.65 ** 2), 1)
        self.assertEqual(response_data['consultation']['imc'], expected_imc)

    def test_consultation_deletion_workflow(self):
        """Test du workflow de suppression"""
        # 1. Créer une consultation
        consultation = ConsultationGynecologique.objects.create(
            patient=self.patient_femme,
            motif='Consultation à supprimer',
            created_by=self.sage_femme
        )
        
        # 2. Vérifier qu'elle existe dans l'historique
        consultations_url = reverse('patients:patient_consultations', args=[self.patient_femme.id])
        response = self.client.get(consultations_url)
        self.assertContains(response, 'Consultation à supprimer')
        
        # 3. Supprimer la consultation
        delete_url = reverse('patients:delete_consultation', args=[consultation.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 200)
        
        # 4. Vérifier qu'elle n'apparaît plus dans l'historique
        response = self.client.get(consultations_url)
        self.assertNotContains(response, 'Consultation à supprimer')

    def test_consultation_validation_integration(self):
        """Test de l'intégration des validations"""
        # Test avec une date future (invalide)
        future_data = {
            'patient_id': self.patient_femme.id,
            'date_consultation': (date.today() + timedelta(days=1)).isoformat(),
            'motif': 'Test validation date'
        }
        
        api_url = reverse('patients:save_consultation')
        response = self.client.post(api_url, future_data)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('validation', response_data['error'].lower())

    def test_patient_type_restriction_integration(self):
        """Test de la restriction par type de patient"""
        # Essayer de créer une consultation pour un bébé
        baby_consultation_url = reverse('patients:consultation_modal', args=[self.patient_bebe.id])
        response = self.client.get(baby_consultation_url)
        self.assertEqual(response.status_code, 404)
        
        # Vérifier le message d'erreur via les consultations
        consultations_url = reverse('patients:patient_consultations', args=[self.patient_bebe.id])
        response = self.client.get(consultations_url)
        self.assertIn('error', response.context)
        self.assertIn('réservées aux femmes', response.context['error'])

    def test_multiple_consultations_ordering(self):
        """Test de l'ordre des consultations multiples"""
        # Créer plusieurs consultations avec des dates différentes
        dates = [
            date(2024, 1, 15),
            date(2024, 1, 10),
            date(2024, 1, 20),
            date(2024, 1, 5)
        ]
        
        consultations = []
        for i, consultation_date in enumerate(dates):
            consultation = ConsultationGynecologique.objects.create(
                patient=self.patient_femme,
                date_consultation=consultation_date,
                motif=f'Consultation {i+1}',
                created_by=self.sage_femme
            )
            consultations.append(consultation)
        
        # Vérifier l'ordre dans l'affichage
        consultations_url = reverse('patients:patient_consultations', args=[self.patient_femme.id])
        response = self.client.get(consultations_url)
        
        # Les consultations doivent être triées par date décroissante
        consultations_ordered = response.context['consultations']
        self.assertEqual(consultations_ordered[0].date_consultation, date(2024, 1, 20))
        self.assertEqual(consultations_ordered[1].date_consultation, date(2024, 1, 15))
        self.assertEqual(consultations_ordered[2].date_consultation, date(2024, 1, 10))
        self.assertEqual(consultations_ordered[3].date_consultation, date(2024, 1, 5))

    def test_consultation_with_all_fields(self):
        """Test d'intégration avec tous les champs remplis"""
        complete_data = {
            'patient': self.patient_femme.id,
            'date_consultation': date.today(),
            'tension_systolique': 125,
            'tension_diastolique': 85,
            'poids': 68.5,
            'motif': 'Consultation complète avec tous les champs',
            'examen': 'Examen gynécologique complet:\n- Inspection: RAS\n- Palpation: normale',
            'prescription': 'Prescription détaillée:\n- Vitamine D: 1000UI/jour\n- Contrôle dans 3 mois',
            'notes': 'Notes importantes:\n- Patiente anxieuse\n- Expliquer les résultats\n- RDV de suivi nécessaire'
        }
        
        modal_url = reverse('patients:consultation_modal', args=[self.patient_femme.id])
        response = self.client.post(modal_url, complete_data)
        response_data = json.loads(response.content)
        
        consultation = ConsultationGynecologique.objects.get(id=response_data['consultation_id'])
        
        # Vérifier tous les champs
        self.assertEqual(consultation.tension_systolique, 125)
        self.assertEqual(consultation.tension_diastolique, 85)
        self.assertEqual(consultation.poids, 68.5)
        self.assertIn('Consultation complète', consultation.motif)
        self.assertIn('Examen gynécologique', consultation.examen)
        self.assertIn('Vitamine D', consultation.prescription)
        self.assertIn('anxieuse', consultation.notes)
        
        # Vérifier les propriétés calculées
        self.assertEqual(consultation.tension_complete, '125/85 mmHg')
        self.assertIn('stade 1', consultation.tension_interpretation.lower())  # 125/85 = stade 1
        self.assertIsNotNone(consultation.imc)

    def test_error_handling_integration(self):
        """Test de la gestion d'erreurs intégrée"""
        # Test avec patient inexistant
        api_url = reverse('patients:save_consultation')
        invalid_data = {
            'patient_id': 99999,
            'motif': 'Patient inexistant'
        }
        
        response = self.client.post(api_url, invalid_data)
        self.assertEqual(response.status_code, 200)  # L'erreur est gérée par le catch
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        
        # Test avec données corrompues
        corrupted_data = {
            'patient_id': self.patient_femme.id,
            'tension_systolique': 'pas_un_nombre',
            'poids': 'invalide',
            'motif': 'Test données corrompues'
        }
        
        response = self.client.post(api_url, corrupted_data)
        response_data = json.loads(response.content)
        # Doit réussir mais ignorer les valeurs invalides
        self.assertTrue(response_data['success'])

    def test_sage_femme_tracking_integration(self):
        """Test du suivi de la sage-femme créatrice"""
        # Créer une consultation
        consultation_data = {
            'patient_id': self.patient_femme.id,
            'motif': 'Test tracking sage-femme'
        }
        
        api_url = reverse('patients:save_consultation')
        response = self.client.post(api_url, consultation_data)
        response_data = json.loads(response.content)
        
        consultation = ConsultationGynecologique.objects.get(
            id=response_data['consultation']['id']
        )
        
        # Vérifier que la sage-femme est associée
        self.assertEqual(consultation.created_by, self.sage_femme)
        
        # Vérifier dans l'affichage
        consultations_url = reverse('patients:patient_consultations', args=[self.patient_femme.id])
        response = self.client.get(consultations_url)
        consultation_from_context = response.context['consultations'][0]
        self.assertEqual(consultation_from_context.created_by, self.sage_femme)

    def test_consultation_search_and_filter_integration(self):
        """Test d'intégration avec recherche et filtres (si disponibles)"""
        # Créer plusieurs consultations avec motifs différents
        motifs = [
            'Consultation routine',
            'Douleurs abdominales',
            'Suivi grossesse',
            'Contrôle post-partum'
        ]
        
        for motif in motifs:
            ConsultationGynecologique.objects.create(
                patient=self.patient_femme,
                motif=motif,
                created_by=self.sage_femme
            )
        
        # Vérifier que toutes apparaissent dans l'historique
        consultations_url = reverse('patients:patient_consultations', args=[self.patient_femme.id])
        response = self.client.get(consultations_url)
        
        for motif in motifs:
            self.assertContains(response, motif)

    def test_consultation_resume_property_integration(self):
        """Test de l'intégration de la propriété résumé"""
        # Créer une consultation avec des données pour le résumé
        consultation = ConsultationGynecologique.objects.create(
            patient=self.patient_femme,
            motif='Consultation pour douleurs abdominales importantes nécessitant une attention particulière',
            tension_systolique=135,
            tension_diastolique=88,
            poids=66.5,
            created_by=self.sage_femme
        )
        
        resume = consultation.resume_consultation
        
        # Vérifier les éléments du résumé
        self.assertIn('douleurs abdominales', resume)
        self.assertIn('135/88 mmHg', resume)
        self.assertIn('66.5kg', resume)
        
        # Vérifier la troncature si nécessaire
        if len(consultation.motif) > 50:
            self.assertIn('...', resume)