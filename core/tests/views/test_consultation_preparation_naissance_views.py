"""
Tests pour les vues de ConsultationPreparationNaissance
"""

import json
from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import JsonResponse

from core.models import (
    Patient, ConsultationPreparationNaissance, SageFemme, 
    Caisse, ConditionPaiement, PeriodeActivite
)
from authentication.models import SageFemmeUser

User = get_user_model()


class ConsultationPreparationNaissanceViewsTest(TestCase):
    """Tests pour les vues de ConsultationPreparationNaissance"""
    
    def setUp(self):
        """Configuration pour chaque test"""
        self.client = Client()
        
        # Créer une caisse et condition de paiement
        self.condition = ConditionPaiement.objects.create(
            designation="Test Condition",
            pourcentage=70
        )
        self.caisse = Caisse.objects.create(
            nom="CAFAT"
        )
        self.caisse.conditions_paiement_eligibles.add(self.condition)
        
        # Créer une sage-femme et son utilisateur
        self.sage_femme = SageFemme.objects.create(
            nom="Dupont",
            prenom="Marie",
            titre="Sage-femme",
            telephone="0123456789",
            email="marie@test.com",
            numero_cafat="123456789",
            ridet="123456789",
            rib="12345678901234567890",
            banque="BCI",
            situation="titulaire"
        )
        
        # Créer période d'activité active
        self.periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=date.today() - timedelta(days=30),
            # pas de date_fin = période active
        )
        
        # Créer utilisateur
        self.user = SageFemmeUser.objects.create_superuser(
            email="marie@test.com",
            password="testpass123"
        )
        # Connecter la sage-femme au user (relation OneToOne)
        self.sage_femme.user = self.user
        self.sage_femme.save()
        
        # Créer une patiente femme
        self.patiente = Patient.objects.create(
            nom="Martin",
            prenom="Julie",
            date_naissance=date(1990, 5, 15),
            telephone="0123456789",
            type_patient="femme",
            caisse=self.caisse,
            date_debut_grossesse=date(2024, 1, 1)
        )
        
        # Créer un patient bébé
        self.bebe = Patient.objects.create(
            nom="Martin",
            prenom="Lucas",
            date_naissance=date(2024, 6, 1),
            type_patient="bebe",
            caisse=self.caisse,
            mere=self.patiente
        )
        
        # Créer des consultations de test
        self.consultation1 = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today() - timedelta(days=7),
            theme_aborde="Respiration et relaxation",
            a_prevoir="Revoir les exercices",
            created_by=self.sage_femme
        )
        
        self.consultation2 = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today() - timedelta(days=3),
            theme_aborde="Allaitement maternel",
            created_by=self.sage_femme
        )
        
        # Se connecter
        self.client.login(email="marie@test.com", password="testpass123")
    
    def test_patient_consultations_preparation_naissance_get(self):
        """Test récupération des consultations d'une patiente"""
        response = self.client.get(f'/patients/{self.patiente.id}/consultations-preparation-naissance/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Respiration et relaxation')
        self.assertContains(response, 'Allaitement maternel')
        self.assertIn('consultations', response.context)
        self.assertEqual(len(response.context['consultations']), 2)
    
    def test_patient_consultations_preparation_naissance_patient_bebe(self):
        """Test récupération consultations pour patient bébé"""
        response = self.client.get(f'/patients/{self.bebe.id}/consultations-preparation-naissance/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'réservées aux femmes')
        self.assertEqual(len(response.context['consultations']), 0)
        self.assertIn('error', response.context)
    
    def test_patient_consultations_preparation_naissance_patient_inexistant(self):
        """Test récupération consultations pour patient inexistant"""
        response = self.client.get('/patients/99999/consultations-preparation-naissance/')
        
        self.assertEqual(response.status_code, 404)
    
    def test_consultation_preparation_naissance_modal_get(self):
        """Test affichage du modal de consultation"""
        response = self.client.get(f'/patients/{self.patiente.id}/consultation-preparation-naissance/modal/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('patient', response.context)
        self.assertEqual(response.context['patient'], self.patiente)
    
    def test_consultation_preparation_naissance_modal_get_patient_bebe(self):
        """Test modal pour patient bébé"""
        response = self.client.get(f'/patients/{self.bebe.id}/consultation-preparation-naissance/modal/')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('femmes', data['error'])
    
    def test_consultation_preparation_naissance_modal_post_valid(self):
        """Test création consultation via modal avec données valides"""
        data = {
            'patient': self.patiente.id,
            'date_consultation': date.today().isoformat(),
            'theme_aborde': 'Positions d\'accouchement',
            'a_prevoir': 'Prévoir visite maternité'
        }
        
        response = self.client.post(
            f'/patients/{self.patiente.id}/consultation-preparation-naissance/modal/',
            data
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('consultation_id', response_data)
        
        # Vérifier que la consultation a été créée
        consultation = ConsultationPreparationNaissance.objects.get(id=response_data['consultation_id'])
        self.assertEqual(consultation.theme_aborde, 'Positions d\'accouchement')
        self.assertEqual(consultation.created_by, self.sage_femme)
    
    def test_consultation_preparation_naissance_modal_post_invalid(self):
        """Test création consultation via modal avec données invalides"""
        data = {
            'patient': self.patiente.id,
            'date_consultation': (date.today() + timedelta(days=1)).isoformat(),  # Date future
            'theme_aborde': 'Test invalide'
        }
        
        response = self.client.post(
            f'/patients/{self.patiente.id}/consultation-preparation-naissance/modal/',
            data
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('errors', response_data)
    
    def test_save_consultation_preparation_naissance_valid(self):
        """Test sauvegarde consultation via API avec données valides"""
        data = {
            'patient_id': self.patiente.id,
            'date_consultation': date.today().isoformat(),
            'theme_aborde': 'Préparation physique',
            'a_prevoir': 'Continuer les exercices'
        }
        
        response = self.client.post('/consultation-preparation-naissance/save/', data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('consultation', response_data)
        
        # Vérifier les données de la consultation retournée
        consultation_data = response_data['consultation']
        self.assertEqual(consultation_data['theme_aborde'], 'Préparation physique')
    
    def test_save_consultation_preparation_naissance_missing_patient_id(self):
        """Test sauvegarde consultation sans patient_id"""
        data = {
            'date_consultation': date.today().isoformat(),
            'theme_aborde': 'Test sans patient'
        }
        
        response = self.client.post('/consultation-preparation-naissance/save/', data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Patient ID manquant', response_data['error'])
    
    def test_save_consultation_preparation_naissance_patient_bebe(self):
        """Test sauvegarde consultation pour patient bébé"""
        data = {
            'patient_id': self.bebe.id,
            'date_consultation': date.today().isoformat(),
            'theme_aborde': 'Test bébé'
        }
        
        response = self.client.post('/consultation-preparation-naissance/save/', data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('femmes', response_data['error'])
    
    def test_save_consultation_preparation_naissance_invalid_date(self):
        """Test sauvegarde consultation avec date invalide"""
        data = {
            'patient_id': self.patiente.id,
            'date_consultation': 'invalid-date',
            'theme_aborde': 'Test date invalide'
        }
        
        response = self.client.post('/consultation-preparation-naissance/save/', data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        # Devrait quand même réussir car la date par défaut sera utilisée
        self.assertTrue(response_data['success'])
    
    def test_delete_consultation_preparation_naissance(self):
        """Test suppression consultation"""
        response = self.client.post(f'/consultation-preparation-naissance/{self.consultation1.id}/delete/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Allaitement maternel')  # Consultation 2 toujours présente
        self.assertNotContains(response, 'Respiration et relaxation')  # Consultation 1 supprimée
        
        # Vérifier en base de données
        with self.assertRaises(ConsultationPreparationNaissance.DoesNotExist):
            ConsultationPreparationNaissance.objects.get(id=self.consultation1.id)
    
    def test_delete_consultation_preparation_naissance_inexistante(self):
        """Test suppression consultation inexistante"""
        response = self.client.post('/consultation-preparation-naissance/99999/delete/')
        
        self.assertEqual(response.status_code, 404)
    
    def test_consultation_preparation_naissance_detail(self):
        """Test affichage détail consultation"""
        response = self.client.get(f'/consultation-preparation-naissance/{self.consultation1.id}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('consultation', response.context)
        self.assertEqual(response.context['consultation'], self.consultation1)
        self.assertContains(response, 'Respiration et relaxation')
    
    def test_consultation_preparation_naissance_detail_inexistante(self):
        """Test détail consultation inexistante"""
        response = self.client.get('/consultation-preparation-naissance/99999/')
        
        self.assertEqual(response.status_code, 404)
    
    def test_consultation_preparation_naissance_quick_form_get(self):
        """Test formulaire rapide inline"""
        response = self.client.get(f'/patients/{self.patiente.id}/consultation-preparation-naissance/quick-form/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('patient', response.context)
        self.assertEqual(response.context['patient'], self.patiente)
    
    def test_consultation_preparation_naissance_quick_form_patient_bebe(self):
        """Test formulaire rapide pour patient bébé"""
        response = self.client.get(f'/patients/{self.bebe.id}/consultation-preparation-naissance/quick-form/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.assertIn('femmes', response.context['error'])
        self.assertIsNone(response.context['form'])
    
    def test_save_quick_consultation_preparation_naissance_valid(self):
        """Test sauvegarde consultation rapide avec données valides"""
        data = {
            'date_consultation': date.today().isoformat(),
            'theme_aborde': 'Relaxation',
            'a_prevoir': 'Exercices quotidiens'
        }
        
        response = self.client.post(
            f'/patients/{self.patiente.id}/consultation-preparation-naissance/save-quick/',
            data
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Relaxation')
        self.assertIn('HX-Trigger', response)
        
        # Vérifier en base de données
        consultation = ConsultationPreparationNaissance.objects.filter(
            patient=self.patiente,
            theme_aborde='Relaxation'
        ).first()
        self.assertIsNotNone(consultation)
        self.assertEqual(consultation.created_by, self.sage_femme)
    
    def test_save_quick_consultation_preparation_naissance_invalid(self):
        """Test sauvegarde consultation rapide avec données invalides"""
        data = {
            'date_consultation': (date.today() + timedelta(days=1)).isoformat(),  # Date future
            'theme_aborde': 'Test invalide'
        }
        
        response = self.client.post(
            f'/patients/{self.patiente.id}/consultation-preparation-naissance/save-quick/',
            data
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)
    
    def test_save_quick_consultation_preparation_naissance_patient_bebe(self):
        """Test sauvegarde consultation rapide pour patient bébé"""
        data = {
            'date_consultation': date.today().isoformat(),
            'theme_aborde': 'Test bébé'
        }
        
        response = self.client.post(
            f'/patients/{self.bebe.id}/consultation-preparation-naissance/save-quick/',
            data
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.assertIn('femmes', response.context['error'])
    
    def test_liste_consultations_preparation_naissance(self):
        """Test liste des consultations avec recherche"""
        response = self.client.get('/consultations-preparation-naissance/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('consultations', response.context)
        self.assertContains(response, 'Respiration et relaxation')
        self.assertContains(response, 'Allaitement maternel')
    
    def test_liste_consultations_preparation_naissance_recherche(self):
        """Test liste avec recherche par nom"""
        response = self.client.get('/consultations-preparation-naissance/', {
            'recherche': 'Martin'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Martin')
        self.assertContains(response, 'Respiration et relaxation')
    
    def test_liste_consultations_preparation_naissance_recherche_theme(self):
        """Test liste avec recherche par thème"""
        response = self.client.get('/consultations-preparation-naissance/', {
            'recherche': 'allaitement'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Allaitement maternel')
        self.assertNotContains(response, 'Respiration et relaxation')
    
    def test_liste_consultations_preparation_naissance_date_debut(self):
        """Test liste avec filtre date début"""
        response = self.client.get('/consultations-preparation-naissance/', {
            'date_debut': (date.today() - timedelta(days=5)).isoformat()
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Allaitement maternel')  # Plus récent
        self.assertNotContains(response, 'Respiration et relaxation')  # Plus ancien
    
    def test_liste_consultations_preparation_naissance_date_fin(self):
        """Test liste avec filtre date fin"""
        response = self.client.get('/consultations-preparation-naissance/', {
            'date_fin': (date.today() - timedelta(days=5)).isoformat()
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Allaitement maternel')  # Plus récent
        self.assertContains(response, 'Respiration et relaxation')  # Plus ancien
    
    def test_liste_consultations_preparation_naissance_pagination(self):
        """Test pagination de la liste"""
        # Créer plus de consultations pour tester la pagination
        for i in range(30):
            ConsultationPreparationNaissance.objects.create(
                patient=self.patiente,
                date_consultation=date.today() - timedelta(days=i),
                theme_aborde=f'Thème {i}',
                created_by=self.sage_femme
            )
        
        response = self.client.get('/consultations-preparation-naissance/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('consultations', response.context)
        # Vérifier que la pagination fonctionne (25 par page)
        self.assertEqual(len(response.context['consultations']), 25)
    
    def test_unauthorized_access(self):
        """Test accès non autorisé"""
        self.client.logout()
        
        response = self.client.get(f'/patients/{self.patiente.id}/consultations-preparation-naissance/')
        self.assertRedirects(response, f'/auth/connexion/?next=/patients/{self.patiente.id}/consultations-preparation-naissance/')
    
    def test_http_methods_not_allowed(self):
        """Test méthodes HTTP non autorisées"""
        # Test PUT sur une vue GET only
        response = self.client.put(f'/patients/{self.patiente.id}/consultations-preparation-naissance/')
        self.assertEqual(response.status_code, 405)
        
        # Test GET sur une vue POST only
        response = self.client.get('/consultation-preparation-naissance/save/')
        self.assertEqual(response.status_code, 405)
    
    def test_user_without_sagefemme(self):
        """Test utilisateur sans sage-femme associée"""
        # Créer un utilisateur sans sage-femme (superuser pour accès aux vues)
        user_no_sf = SageFemmeUser.objects.create_superuser(
            email="nosf@test.com",
            password="testpass123"
        )
        
        self.client.logout()
        self.client.login(email="nosf@test.com", password="testpass123")
        
        data = {
            'patient_id': self.patiente.id,
            'date_consultation': date.today().isoformat(),
            'theme_aborde': 'Test sans sage-femme'
        }
        
        response = self.client.post('/consultation-preparation-naissance/save/', data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Vérifier que la consultation a été créée sans created_by
        consultation = ConsultationPreparationNaissance.objects.get(
            id=response_data['consultation']['id']
        )
        self.assertIsNone(consultation.created_by)