"""
Tests d'intégration pour ConsultationPreparationNaissance
"""

import json
from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import (
    Patient, ConsultationPreparationNaissance, SageFemme,
    Caisse, ConditionPaiement, PeriodeActivite
)
from authentication.models import SageFemmeUser

User = get_user_model()


class ConsultationPreparationNaissanceIntegrationTest(TestCase):
    """Tests d'intégration complets pour ConsultationPreparationNaissance"""
    
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
            date_debut=date.today() - timedelta(days=30)
        )
        
        # Créer utilisateur connecté
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
        
        # Se connecter
        self.client.login(email="marie@test.com", password="testpass123")
    
    def test_workflow_creation_consultation_complete(self):
        """Test workflow complet de création d'une consultation"""
        # 1. Afficher le formulaire quick
        response = self.client.get(f'/patients/{self.patiente.id}/consultation-preparation-naissance/quick-form/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # 2. Sauvegarder la consultation
        data = {
            'date_consultation': date.today().isoformat(),
            'theme_aborde': 'Préparation complète à l\'accouchement',
            'a_prevoir': 'Revoir les positions et exercices de respiration'
        }
        
        response = self.client.post(
            f'/patients/{self.patiente.id}/consultation-preparation-naissance/save-quick/',
            data
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Préparation complète')
        
        # 3. Vérifier que la consultation a été créée en base
        consultation = ConsultationPreparationNaissance.objects.filter(
            patient=self.patiente,
            theme_aborde='Préparation complète à l\'accouchement'
        ).first()
        
        self.assertIsNotNone(consultation)
        self.assertEqual(consultation.created_by, self.sage_femme)
        self.assertIsNotNone(consultation.semaines_amenorrhee)  # SA calculées automatiquement
        
        # 4. Afficher l'historique mis à jour
        response = self.client.get(f'/patients/{self.patiente.id}/consultations-preparation-naissance/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Préparation complète')
        self.assertContains(response, consultation.semaines_amenorrhee)
    
    def test_workflow_modal_consultation(self):
        """Test workflow avec modal de consultation"""
        # 1. Afficher le modal
        response = self.client.get(f'/patients/{self.patiente.id}/consultation-preparation-naissance/modal/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # 2. Soumettre le formulaire modal
        data = {
            'patient': self.patiente.id,
            'date_consultation': date.today().isoformat(),
            'theme_aborde': 'Allaitement et soins du nouveau-né',
            'a_prevoir': 'Prévoir matériel allaitement'
        }
        
        response = self.client.post(
            f'/patients/{self.patiente.id}/consultation-preparation-naissance/modal/',
            data
        )
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la réponse JSON
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('consultation_id', response_data)
        
        # 3. Vérifier la consultation en base
        consultation = ConsultationPreparationNaissance.objects.get(
            id=response_data['consultation_id']
        )
        self.assertEqual(consultation.theme_aborde, 'Allaitement et soins du nouveau-né')
    
    def test_workflow_detail_consultation(self):
        """Test workflow d'affichage des détails"""
        # 1. Créer une consultation
        consultation = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today(),
            theme_aborde='Positions d\'accouchement',
            a_prevoir='Pratiquer les positions apprises',
            created_by=self.sage_femme
        )
        
        # 2. Afficher les détails dans un modal
        response = self.client.get(f'/consultation-preparation-naissance/{consultation.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Positions d&#x27;accouchement')
        self.assertContains(response, 'Pratiquer les positions apprises')
        self.assertContains(response, consultation.semaines_amenorrhee)
    
    def test_workflow_suppression_consultation(self):
        """Test workflow de suppression"""
        # 1. Créer des consultations
        consultation1 = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today() - timedelta(days=7),
            theme_aborde='Première consultation',
            created_by=self.sage_femme
        )
        
        consultation2 = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today() - timedelta(days=3),
            theme_aborde='Deuxième consultation',
            created_by=self.sage_femme
        )
        
        # 2. Supprimer une consultation
        response = self.client.post(f'/consultation-preparation-naissance/{consultation1.id}/delete/')
        self.assertEqual(response.status_code, 200)
        
        # 3. Vérifier que l'historique est mis à jour
        self.assertContains(response, 'Deuxième consultation')
        self.assertNotContains(response, 'Première consultation')
        
        # 4. Vérifier en base de données
        with self.assertRaises(ConsultationPreparationNaissance.DoesNotExist):
            ConsultationPreparationNaissance.objects.get(id=consultation1.id)
        
        # La consultation 2 doit toujours exister
        self.assertTrue(
            ConsultationPreparationNaissance.objects.filter(id=consultation2.id).exists()
        )
    
    def test_workflow_recherche_consultations(self):
        """Test workflow de recherche dans la liste"""
        # 1. Créer plusieurs consultations
        ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today() - timedelta(days=10),
            theme_aborde='Respiration et relaxation',
            a_prevoir='Exercices quotidiens',
            created_by=self.sage_femme
        )
        
        ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today() - timedelta(days=5),
            theme_aborde='Allaitement maternel',
            a_prevoir='Prévoir tire-lait',
            created_by=self.sage_femme
        )
        
        # 2. Recherche par thème
        response = self.client.get('/consultations-preparation-naissance/', {
            'recherche': 'allaitement'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Allaitement maternel')
        self.assertNotContains(response, 'Respiration et relaxation')
        
        # 3. Recherche par nom de patiente
        response = self.client.get('/consultations-preparation-naissance/', {
            'recherche': 'Martin'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Allaitement maternel')
        self.assertContains(response, 'Respiration et relaxation')
        
        # 4. Filtre par date
        response = self.client.get('/consultations-preparation-naissance/', {
            'date_debut': (date.today() - timedelta(days=7)).isoformat()
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Allaitement maternel')
        self.assertNotContains(response, 'Respiration et relaxation')
    
    def test_workflow_calcul_automatique_sa(self):
        """Test workflow avec calcul automatique des SA"""
        # 1. Créer consultation à une date spécifique
        date_consultation = self.patiente.date_debut_grossesse + timedelta(days=154)  # 22 semaines
        
        data = {
            'date_consultation': date_consultation.isoformat(),
            'theme_aborde': 'Consultation 22 SA',
            'a_prevoir': 'Préparation accouchement'
        }
        
        response = self.client.post(
            f'/patients/{self.patiente.id}/consultation-preparation-naissance/save-quick/',
            data
        )
        self.assertEqual(response.status_code, 200)
        
        # 2. Vérifier que les SA sont affichées
        self.assertContains(response, '22 SA')
        
        # 3. Vérifier en base de données
        consultation = ConsultationPreparationNaissance.objects.filter(
            patient=self.patiente,
            theme_aborde='Consultation 22 SA'
        ).first()
        
        self.assertEqual(consultation.semaines_amenorrhee, '22 SA')
    
    def test_workflow_patiente_sans_ddg(self):
        """Test workflow avec patiente sans DDG"""
        # 1. Créer patiente sans DDG
        patiente_sans_ddg = Patient.objects.create(
            nom="Dubois",
            prenom="Sophie",
            date_naissance=date(1992, 3, 20),
            telephone="0123456790",
            type_patient="femme",
            caisse=self.caisse
            # Pas de date_debut_grossesse
        )
        
        # 2. Créer consultation
        data = {
            'date_consultation': date.today().isoformat(),
            'theme_aborde': 'Consultation sans DDG',
            'a_prevoir': 'Définir DDG'
        }
        
        response = self.client.post(
            f'/patients/{patiente_sans_ddg.id}/consultation-preparation-naissance/save-quick/',
            data
        )
        self.assertEqual(response.status_code, 200)
        
        # 3. Vérifier que les SA ne sont pas calculées
        consultation = ConsultationPreparationNaissance.objects.filter(
            patient=patiente_sans_ddg,
            theme_aborde='Consultation sans DDG'
        ).first()
        
        self.assertIsNone(consultation.semaines_amenorrhee)
    
    def test_workflow_gestion_erreurs(self):
        """Test workflow avec gestion d'erreurs"""
        # 1. Tentative avec date future
        data = {
            'date_consultation': (date.today() + timedelta(days=1)).isoformat(),
            'theme_aborde': 'Test erreur date',
            'a_prevoir': 'Ne devrait pas fonctionner'
        }
        
        response = self.client.post(
            f'/patients/{self.patiente.id}/consultation-preparation-naissance/save-quick/',
            data
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'futur')  # Message d'erreur
        
        # 2. Vérifier qu'aucune consultation n'a été créée
        consultation = ConsultationPreparationNaissance.objects.filter(
            patient=self.patiente,
            theme_aborde='Test erreur date'
        ).first()
        self.assertIsNone(consultation)
    
    def test_workflow_patient_bebe_restrictions(self):
        """Test workflow avec restrictions pour patients bébés"""
        # 1. Créer un patient bébé
        bebe = Patient.objects.create(
            nom="Martin",
            prenom="Lucas",
            date_naissance=date(2024, 6, 1),
            type_patient="bebe",
            caisse=self.caisse,
            mere=self.patiente
        )
        
        # 2. Tentative d'accès au formulaire
        response = self.client.get(f'/patients/{bebe.id}/consultation-preparation-naissance/quick-form/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'réservées aux femmes')
        self.assertIn('error', response.context)
        
        # 3. Tentative de sauvegarde
        data = {
            'date_consultation': date.today().isoformat(),
            'theme_aborde': 'Test bébé',
        }
        
        response = self.client.post(
            f'/patients/{bebe.id}/consultation-preparation-naissance/save-quick/',
            data
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'réservées aux femmes')
    
    def test_workflow_integration_api_ajax(self):
        """Test workflow d'intégration avec API AJAX"""
        # 1. Sauvegarder via API AJAX
        data = {
            'patient_id': self.patiente.id,
            'date_consultation': date.today().isoformat(),
            'theme_aborde': 'Consultation via API',
            'a_prevoir': 'Tests API'
        }
        
        response = self.client.post('/consultation-preparation-naissance/save/', data)
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('consultation', response_data)
        
        # 2. Vérifier les données retournées
        consultation_data = response_data['consultation']
        self.assertEqual(consultation_data['theme_aborde'], 'Consultation via API')
        self.assertIn('id', consultation_data)
        self.assertIn('semaines_amenorrhee', consultation_data)
        self.assertIn('consultation_resume', consultation_data)
        
        # 3. Vérifier en base de données
        consultation = ConsultationPreparationNaissance.objects.get(
            id=consultation_data['id']
        )
        self.assertEqual(consultation.theme_aborde, 'Consultation via API')
        self.assertEqual(consultation.created_by, self.sage_femme)
    
    def test_workflow_pagination_liste(self):
        """Test workflow avec pagination dans la liste"""
        # 1. Créer un grand nombre de consultations
        for i in range(30):
            ConsultationPreparationNaissance.objects.create(
                patient=self.patiente,
                date_consultation=date.today() - timedelta(days=i),
                theme_aborde=f'Consultation {i}',
                created_by=self.sage_femme
            )
        
        # 2. Accéder à la première page
        response = self.client.get('/consultations-preparation-naissance/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Consultation 0')  # Plus récente
        self.assertNotContains(response, 'Consultation 29')  # Plus ancienne
        
        # 3. Accéder à la page suivante
        response = self.client.get('/consultations-preparation-naissance/?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Consultation 0')  # Plus récente
        self.assertContains(response, 'Consultation 29')  # Plus ancienne
    
    def test_workflow_session_utilisateur(self):
        """Test workflow avec session utilisateur"""
        # 1. Créer consultation en étant connecté
        data = {
            'date_consultation': date.today().isoformat(),
            'theme_aborde': 'Test session utilisateur',
        }
        
        response = self.client.post(
            f'/patients/{self.patiente.id}/consultation-preparation-naissance/save-quick/',
            data
        )
        self.assertEqual(response.status_code, 200)
        
        # 2. Vérifier que la sage-femme est bien associée
        consultation = ConsultationPreparationNaissance.objects.filter(
            theme_aborde='Test session utilisateur'
        ).first()
        self.assertEqual(consultation.created_by, self.sage_femme)
        
        # 3. Déconnexion et tentative d'accès
        self.client.logout()
        
        response = self.client.get(f'/patients/{self.patiente.id}/consultations-preparation-naissance/')
        self.assertRedirects(
            response, 
            f'/auth/connexion/?next=/patients/{self.patiente.id}/consultations-preparation-naissance/'
        )
    
    def test_workflow_mise_a_jour_historique(self):
        """Test workflow de mise à jour automatique de l'historique"""
        # 1. Créer consultation initiale
        consultation = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today() - timedelta(days=7),
            theme_aborde='Consultation initiale',
            created_by=self.sage_femme
        )
        
        # 2. Afficher l'historique
        response = self.client.get(f'/patients/{self.patiente.id}/consultations-preparation-naissance/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Consultation initiale')
        
        # 3. Ajouter nouvelle consultation
        data = {
            'date_consultation': date.today().isoformat(),
            'theme_aborde': 'Nouvelle consultation',
        }
        
        response = self.client.post(
            f'/patients/{self.patiente.id}/consultation-preparation-naissance/save-quick/',
            data
        )
        self.assertEqual(response.status_code, 200)
        
        # 4. Vérifier que l'historique est mis à jour automatiquement
        self.assertContains(response, 'Nouvelle consultation')
        self.assertContains(response, 'Consultation initiale')
        
        # Les consultations doivent être ordonnées par date décroissante
        content = response.content.decode()
        pos_nouvelle = content.find('Nouvelle consultation')
        pos_initiale = content.find('Consultation initiale')
        self.assertLess(pos_nouvelle, pos_initiale)  # Plus récente en premier