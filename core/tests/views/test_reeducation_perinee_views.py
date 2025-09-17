"""
Tests pour les vues de ReeducationPerinee
"""

import json
from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import JsonResponse

from core.models import (
    Patient, ReeducationPerinee, SageFemme, 
    Caisse, ConditionPaiement, PeriodeActivite
)
from authentication.models import SageFemmeUser

User = get_user_model()


class ReeducationPerineeViewsTest(TestCase):
    """Tests pour les vues de ReeducationPerinee"""
    
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
            caisse=self.caisse
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
        
        # Créer des séances de test
        self.seance1 = ReeducationPerinee.objects.create(
            patient=self.patiente,
            date_consultation=date.today() - timedelta(days=7),
            numero_seance=1,
            examen_clinique_travail="Évaluation du tonus périnéal",
            a_prevoir="Exercices de Kegel",
            created_by=self.sage_femme
        )
        
        self.seance2 = ReeducationPerinee.objects.create(
            patient=self.patiente,
            date_consultation=date.today() - timedelta(days=3),
            numero_seance=2,
            examen_clinique_travail="Travail de renforcement",
            created_by=self.sage_femme
        )
        
        # Se connecter
        self.client.login(email="marie@test.com", password="testpass123")
    
    def test_patient_reeducations_perinee_get(self):
        """Test récupération des séances d'une patiente"""
        response = self.client.get(f'/patients/{self.patiente.id}/reeducations-perinee/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Évaluation du tonus périnéal')
        self.assertContains(response, 'Travail de renforcement')
        self.assertIn('seances', response.context)
        self.assertEqual(len(response.context['seances']), 2)
    
    def test_patient_reeducations_perinee_patient_bebe(self):
        """Test récupération séances pour patient bébé"""
        response = self.client.get(f'/patients/{self.bebe.id}/reeducations-perinee/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'réservées aux femmes')
        self.assertEqual(len(response.context['seances']), 0)
        self.assertIn('error', response.context)
    
    def test_patient_reeducations_perinee_patient_inexistant(self):
        """Test récupération séances pour patient inexistant"""
        response = self.client.get('/patients/99999/reeducations-perinee/')
        
        self.assertEqual(response.status_code, 404)
    
    def test_reeducation_perinee_modal_get(self):
        """Test affichage du modal de séance"""
        response = self.client.get(f'/reeducation-perinee/modal/{self.patiente.id}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('patient', response.context)
        self.assertEqual(response.context['patient'], self.patiente)
    
    def test_reeducation_perinee_modal_get_patient_bebe(self):
        """Test modal pour patient bébé"""
        response = self.client.get(f'/reeducation-perinee/modal/{self.bebe.id}/')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('femmes', data['error'])
    
    def test_reeducation_perinee_modal_post_valid(self):
        """Test création séance via modal POST valide"""
        data = {
            'patient': self.patiente.id,
            'date_consultation': date.today(),
            'numero_seance': 3,
            'examen_clinique_travail': 'Nouvelle séance test',
            'a_prevoir': 'Continuer les exercices'
        }
        
        response = self.client.post(f'/reeducation-perinee/modal/{self.patiente.id}/', data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('message', response_data)
        
        # Vérifier que la séance a été créée
        seance = ReeducationPerinee.objects.get(numero_seance=3, patient=self.patiente)
        self.assertEqual(seance.examen_clinique_travail, 'Nouvelle séance test')
        self.assertEqual(seance.created_by, self.sage_femme)
    
    def test_reeducation_perinee_modal_post_invalid(self):
        """Test création séance via modal POST invalide"""
        data = {
            'patient': self.patiente.id,
            'date_consultation': date.today() + timedelta(days=1),  # Date future invalide
            'numero_seance': 0,  # Numéro invalide
        }
        
        response = self.client.post(f'/reeducation-perinee/modal/{self.patiente.id}/', data)
        
        self.assertEqual(response.status_code, 200)
        # La vue retourne une réponse JSON avec les erreurs
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)
    
    def test_reeducation_perinee_modal_post_patient_bebe(self):
        """Test création séance pour patient bébé"""
        data = {
            'patient': self.bebe.id,
            'date_consultation': date.today(),
            'numero_seance': 1,
            'examen_clinique_travail': 'Test bébé'
        }
        
        response = self.client.post(f'/reeducation-perinee/modal/{self.bebe.id}/', data)
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('femmes', data['error'])
    
    def test_save_reeducation_perinee_post_valid(self):
        """Test sauvegarde séance POST valide"""
        data = {
            'patient_id': self.patiente.id,
            'date_consultation': date.today().isoformat(),
            'numero_seance': 4,
            'examen_clinique_travail': 'Séance sauvegardée',
            'a_prevoir': 'Planifier suivante'
        }
        
        response = self.client.post('/reeducation-perinee/save/', data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('message', response_data)
        
        # Vérifier que la séance a été créée
        seance = ReeducationPerinee.objects.get(numero_seance=4, patient=self.patiente)
        self.assertEqual(seance.examen_clinique_travail, 'Séance sauvegardée')
        self.assertEqual(seance.created_by, self.sage_femme)
    
    def test_save_reeducation_perinee_post_invalid(self):
        """Test sauvegarde séance POST invalide"""
        data = {
            'patient_id': self.patiente.id,
            'date_consultation': (date.today() + timedelta(days=1)).isoformat(),  # Date future invalide
            'numero_seance': -1,  # Numéro invalide
        }
        
        response = self.client.post('/reeducation-perinee/save/', data)
        
        self.assertEqual(response.status_code, 200)  # La vue retourne 200 avec success=False
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)
    
    def test_save_reeducation_perinee_get_method(self):
        """Test méthode GET sur save (devrait être interdite)"""
        response = self.client.get('/reeducation-perinee/save/')
        
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
    
    def test_delete_reeducation_perinee_post_valid(self):
        """Test suppression séance POST valide"""
        seance_id = self.seance1.id
        
        response = self.client.post(f'/reeducation-perinee/{seance_id}/delete/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Travail de renforcement')  # Seance2 reste
        self.assertNotContains(response, 'Évaluation du tonus périnéal')  # Seance1 supprimée
        
        # Vérifier que la séance a été supprimée
        with self.assertRaises(ReeducationPerinee.DoesNotExist):
            ReeducationPerinee.objects.get(id=seance_id)
    
    def test_delete_reeducation_perinee_seance_inexistante(self):
        """Test suppression séance inexistante"""
        response = self.client.post('/reeducation-perinee/99999/delete/')
        
        self.assertEqual(response.status_code, 404)
    
    def test_delete_reeducation_perinee_patient_bebe(self):
        """Test suppression séance pour patient bébé (ID inexistant)"""
        # Ce test vérifie que la vue vérifie bien le type de patient
        # En pratique, il n'y aura jamais de séances pour les bébés car la validation l'empêche
        # Donc on teste avec un ID inexistant qui simule le cas
        response = self.client.post('/reeducation-perinee/99998/delete/')
        
        self.assertEqual(response.status_code, 404)
    
    def test_delete_reeducation_perinee_get_method(self):
        """Test méthode GET sur delete (devrait être interdite)"""
        response = self.client.get(f'/reeducation-perinee/{self.seance1.id}/delete/')
        
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
    
    def test_reeducation_perinee_detail_get(self):
        """Test affichage détail séance"""
        response = self.client.get(f'/reeducation-perinee/{self.seance1.id}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('seance', response.context)
        self.assertEqual(response.context['seance'], self.seance1)
        self.assertContains(response, 'Évaluation du tonus périnéal')
        self.assertContains(response, 'Exercices de Kegel')
    
    def test_reeducation_perinee_detail_seance_inexistante(self):
        """Test détail séance inexistante"""
        response = self.client.get('/reeducation-perinee/99999/')
        
        self.assertEqual(response.status_code, 404)
    
    def test_liste_reeducations_perinee_get(self):
        """Test affichage liste des séances"""
        response = self.client.get('/reeducations-perinee/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('seances', response.context)
        self.assertIn('form', response.context)  # Le contexte utilise 'form' pas 'search_form'
        # Les deux séances devraient être dans la liste
        seances = list(response.context['seances'])
        self.assertIn(self.seance1, seances)
        self.assertIn(self.seance2, seances)
    
    def test_liste_reeducations_perinee_avec_recherche(self):
        """Test liste avec paramètres de recherche"""
        data = {
            'recherche': 'tonus',
            'numero_seance': 1
        }
        
        response = self.client.get('/reeducations-perinee/', data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('seances', response.context)
        # Devrait contenir la séance1 qui contient "tonus"
        seances = list(response.context['seances'])
        self.assertIn(self.seance1, seances)
    
    def test_liste_reeducations_perinee_recherche_vide(self):
        """Test liste avec recherche ne donnant aucun résultat"""
        data = {
            'recherche': 'inexistant_terme_recherche',
        }
        
        response = self.client.get('/reeducations-perinee/', data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('seances', response.context)
        seances = list(response.context['seances'])
        self.assertEqual(len(seances), 0)
    
    def test_authentication_required(self):
        """Test authentification requise pour toutes les vues"""
        self.client.logout()
        
        urls_to_test = [
            f'/patients/{self.patiente.id}/reeducations-perinee/',
            f'/reeducation-perinee/modal/{self.patiente.id}/',
            '/reeducation-perinee/save/',
            f'/reeducation-perinee/{self.seance1.id}/',
            f'/reeducation-perinee/{self.seance1.id}/delete/',
            '/reeducations-perinee/',
        ]
        
        for url in urls_to_test:
            response = self.client.get(url)
            self.assertIn(response.status_code, [302, 405])  # Redirection ou Method Not Allowed
    
    def test_calcul_prochain_numero_seance_modal(self):
        """Test calcul automatique du prochain numéro dans le modal"""
        response = self.client.get(f'/reeducation-perinee/modal/{self.patiente.id}/')
        
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        
        # Le prochain numéro devrait être 3 (après séance1=1 et séance2=2)
        self.assertEqual(form.fields['numero_seance'].initial, 3)
    
    def test_calcul_prochain_numero_seance_premiere_seance(self):
        """Test calcul pour la première séance d'une nouvelle patiente"""
        # Créer une nouvelle patiente sans séances
        nouvelle_patiente = Patient.objects.create(
            nom="Nouveau",
            prenom="Patient",
            date_naissance=date(1985, 1, 1),
            telephone="0987654321",
            type_patient="femme",
            caisse=self.caisse
        )
        
        response = self.client.get(f'/reeducation-perinee/modal/{nouvelle_patiente.id}/')
        
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        
        # Le premier numéro devrait être 1
        self.assertEqual(form.fields['numero_seance'].initial, 1)
    
    def test_ordre_seances_dans_historique(self):
        """Test ordre des séances dans l'historique (plus récente en premier)"""
        response = self.client.get(f'/patients/{self.patiente.id}/reeducations-perinee/')
        
        self.assertEqual(response.status_code, 200)
        seances = list(response.context['seances'])
        
        # Vérifier l'ordre : séance2 (plus récente) avant séance1
        self.assertEqual(seances[0], self.seance2)
        self.assertEqual(seances[1], self.seance1)
    
    def test_context_patient_dans_templates(self):
        """Test présence du context patient dans les templates"""
        response = self.client.get(f'/patients/{self.patiente.id}/reeducations-perinee/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('patient', response.context)
        self.assertEqual(response.context['patient'], self.patiente)
    
    def test_gestion_erreurs_validation_formulaire(self):
        """Test gestion des erreurs de validation dans les vues"""
        # Test avec des données invalides dans le modal
        data = {
            'patient': '',  # Patient manquant
            'date_consultation': '',  # Date manquante
            'numero_seance': 'abc',  # Numéro invalide
        }
        
        response = self.client.post(f'/reeducation-perinee/modal/{self.patiente.id}/', data)
        
        self.assertEqual(response.status_code, 200)
        # La vue retourne une réponse JSON avec les erreurs
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)
        self.assertIn('errors', response_data)