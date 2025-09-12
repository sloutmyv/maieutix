"""
Tests pour les vues EntretienPrenatalPrecoce
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, timedelta
import json

from core.models import EntretienPrenatalPrecoce, Patient, SageFemme, Caisse
from authentication.models import SageFemmeUser


class EntretienPrenatalPrecoceViewsTest(TestCase):
    """Tests pour les vues des entretiens prénataux précoces"""
    
    def setUp(self):
        """Configuration des données de test"""
        # Client et utilisateur
        self.client = Client()
        
        # Caisse
        self.caisse = Caisse.objects.create(nom="CAFAT")
        
        # Utilisateur et sage-femme
        self.user = SageFemmeUser.objects.create_user(
            email='admin@maieutix.nc',
            password='testpass123'
        )
        self.sage_femme = SageFemme.objects.create(
            user=self.user,
            nom='Martin',
            prenom='Dr Sophie',
            titre='Sage-Femme',
            telephone='123456789',
            email='admin@maieutix.nc',
            numero_cafat='123456',
            ridet='987654',
            rib='FR7630001007941234567890185',
            banque='BNC',
            situation='titulaire'
        )
        
        # Patiente femme avec DDG
        self.patient_femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            caisse=self.caisse,
            date_debut_grossesse=date(2024, 1, 15)
        )
        
        # Entretien de test
        self.entretien = EntretienPrenatalPrecoce.objects.create(
            patient=self.patient_femme,
            sage_femme=self.sage_femme,
            date_entretien=date.today(),
            conjoint_present=True,
            lieu_accouchement_prevu='Maternité CHT',
            atcd_marquants_sante='Aucun ATCD particulier',
            environnement_social_familial='Environnement stable',
            projet_naissance_parentalite='Accouchement naturel souhaité',
            ressenti='Très positive',
            propositions_liens='Cours préparation naissance'
        )
        
        # Connexion
        self.client.login(email='admin@maieutix.nc', password='testpass123')
    
    def test_patient_entretiens_prenataux_precoces_view_get(self):
        """Test vue historique EPP en GET"""
        url = reverse('patients:patient_entretiens_prenataux_precoces', args=[self.patient_femme.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.entretien.date_entretien.strftime('%d/%m/%Y'))
        self.assertContains(response, 'Maternité CHT')
        self.assertContains(response, 'Conjoint présent')
    
    def test_patient_entretiens_prenataux_precoces_view_patient_not_found(self):
        """Test vue historique avec patient inexistant"""
        url = reverse('patients:patient_entretiens_prenataux_precoces', args=[9999])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_entretien_prenatal_precoce_quick_form_view_get(self):
        """Test vue formulaire rapide en GET"""
        url = reverse('patients:entretien_prenatal_precoce_quick_form', args=[self.patient_femme.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nouvel Entretien Prénatal Précoce')
        self.assertContains(response, 'id_date_entretien')
        self.assertContains(response, 'id_conjoint_present')
        self.assertContains(response, 'DDG:')
    
    def test_save_quick_entretien_prenatal_precoce_view_post_valid(self):
        """Test sauvegarde rapide avec données valides"""
        url = reverse('patients:save_quick_entretien_prenatal_precoce', args=[self.patient_femme.id])
        
        form_data = {
            'date_entretien': date.today().strftime('%Y-%m-%d'),
            'conjoint_present': True,
            'lieu_accouchement_prevu': 'Clinique Test',
            'atcd_marquants_sante': 'Aucun ATCD',
            'environnement_social_familial': 'Stable',
            'projet_naissance_parentalite': 'Naturel',
            'ressenti': 'Positive',
            'propositions_liens': 'Cours'
        }
        
        response = self.client.post(url, data=form_data)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier qu'un nouvel entretien a été créé
        nouveaux_entretiens = EntretienPrenatalPrecoce.objects.filter(
            patient=self.patient_femme,
            lieu_accouchement_prevu='Clinique Test'
        )
        self.assertEqual(nouveaux_entretiens.count(), 1)
        
        # Vérifier que la sage-femme connectée est assignée
        nouvel_entretien = nouveaux_entretiens.first()
        self.assertEqual(nouvel_entretien.sage_femme, self.sage_femme)
        self.assertIsNotNone(nouvel_entretien.semaines_amenorrhee)  # SA calculées automatiquement
    
    def test_save_quick_entretien_prenatal_precoce_view_post_invalid(self):
        """Test sauvegarde rapide avec données invalides"""
        url = reverse('patients:save_quick_entretien_prenatal_precoce', args=[self.patient_femme.id])
        
        # Données invalides : date dans le futur
        form_data = {
            'date_entretien': (date.today() + timedelta(days=10)).strftime('%Y-%m-%d'),
            'conjoint_present': False
        }
        
        response = self.client.post(url, data=form_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ne peut pas être dans le futur')
    
    def test_save_quick_entretien_prenatal_precoce_view_patient_not_found(self):
        """Test sauvegarde avec patient inexistant"""
        url = reverse('patients:save_quick_entretien_prenatal_precoce', args=[9999])
        
        form_data = {
            'date_entretien': date.today().strftime('%Y-%m-%d'),
            'conjoint_present': False
        }
        
        response = self.client.post(url, data=form_data)
        
        self.assertEqual(response.status_code, 404)
    
    def test_entretien_prenatal_precoce_detail_view(self):
        """Test vue détail d'un entretien"""
        url = reverse('patients:entretien_prenatal_precoce_detail', args=[self.entretien.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Entretien du {self.entretien.date_entretien.strftime('%d/%m/%Y')}")
        self.assertContains(response, self.patient_femme.nom_complet)
        self.assertContains(response, 'Maternité CHT')
        self.assertContains(response, 'Aucun ATCD particulier')
        self.assertContains(response, 'closeModal()')  # Script de fermeture modal
    
    def test_entretien_prenatal_precoce_detail_view_not_found(self):
        """Test vue détail avec entretien inexistant"""
        url = reverse('patients:entretien_prenatal_precoce_detail', args=[9999])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_delete_entretien_prenatal_precoce_view(self):
        """Test suppression d'un entretien"""
        url = reverse('patients:delete_entretien_prenatal_precoce', args=[self.entretien.id])
        
        # Vérifier que l'entretien existe
        self.assertTrue(EntretienPrenatalPrecoce.objects.filter(id=self.entretien.id).exists())
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que l'entretien a été supprimé
        self.assertFalse(EntretienPrenatalPrecoce.objects.filter(id=self.entretien.id).exists())
    
    def test_delete_entretien_prenatal_precoce_view_not_found(self):
        """Test suppression avec entretien inexistant"""
        url = reverse('patients:delete_entretien_prenatal_precoce', args=[9999])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_entretien_prenatal_precoce_modal_view(self):
        """Test vue modal d'un entretien"""
        url = reverse('patients:entretien_prenatal_precoce_modal', args=[self.patient_femme.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nouvel Entretien Prénatal Précoce')
        # Le champ patient devrait être caché dans le modal
        self.assertNotContains(response, 'name="patient"')
    
    def test_save_entretien_prenatal_precoce_view_post_valid(self):
        """Test sauvegarde complète avec données valides"""
        url = reverse('patients:save_entretien_prenatal_precoce')
        
        form_data = {
            'patient': self.patient_femme.id,
            'date_entretien': date.today().strftime('%Y-%m-%d'),
            'conjoint_present': True,
            'lieu_accouchement_prevu': 'Maternité Complète',
            'atcd_marquants_sante': 'ATCD détaillés',
            'environnement_social_familial': 'Environnement complet',
            'projet_naissance_parentalite': 'Projet détaillé',
            'ressenti': 'Ressenti complet',
            'propositions_liens': 'Propositions détaillées'
        }
        
        response = self.client.post(url, data=form_data)
        
        # Devrait rediriger après sauvegarde réussie
        self.assertEqual(response.status_code, 302)
        
        # Vérifier qu'un nouvel entretien a été créé
        nouveaux_entretiens = EntretienPrenatalPrecoce.objects.filter(
            patient=self.patient_femme,
            lieu_accouchement_prevu='Maternité Complète'
        )
        self.assertEqual(nouveaux_entretiens.count(), 1)
    
    def test_unauthorized_access(self):
        """Test accès non autorisé"""
        self.client.logout()
        
        url = reverse('patients:patient_entretiens_prenataux_precoces', args=[self.patient_femme.id])
        response = self.client.get(url)
        
        # Devrait rediriger vers la page de connexion
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_patient_filtering_femme_with_ddg_only(self):
        """Test filtrage : seules les femmes avec DDG"""
        # Créer patiente sans DDG
        patient_sans_ddg = Patient.objects.create(
            type_patient='femme',
            nom='Sans',
            prenom='DDG',
            date_naissance=date(1995, 1, 1),
            caisse=self.caisse
        )
        
        # Créer patient bébé
        patient_bebe = Patient.objects.create(
            type_patient='bebe',
            nom='Bébé',
            prenom='Test',
            date_naissance=date(2024, 1, 1),
            caisse=self.caisse
        )
        
        # Tenter d'accéder aux vues avec patient sans DDG
        url_sans_ddg = reverse('patients:patient_entretiens_prenataux_precoces', args=[patient_sans_ddg.id])
        response_sans_ddg = self.client.get(url_sans_ddg)
        self.assertEqual(response_sans_ddg.status_code, 404)
        
        # Tenter d'accéder aux vues avec patient bébé
        url_bebe = reverse('patients:patient_entretiens_prenataux_precoces', args=[patient_bebe.id])
        response_bebe = self.client.get(url_bebe)
        self.assertEqual(response_bebe.status_code, 404)
    
    def test_automatic_sage_femme_assignment(self):
        """Test assignation automatique de la sage-femme connectée"""
        url = reverse('patients:save_quick_entretien_prenatal_precoce', args=[self.patient_femme.id])
        
        form_data = {
            'date_entretien': date.today().strftime('%Y-%m-%d'),
            'conjoint_present': False,
            'atcd_marquants_sante': 'Test assignation'
        }
        
        response = self.client.post(url, data=form_data)
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la sage-femme connectée est bien assignée
        entretien_cree = EntretienPrenatalPrecoce.objects.filter(
            atcd_marquants_sante='Test assignation'
        ).first()
        
        self.assertIsNotNone(entretien_cree)
        self.assertEqual(entretien_cree.sage_femme, self.sage_femme)
        self.assertEqual(entretien_cree.created_by, self.sage_femme)
    
    def test_calcul_sa_automatique_in_view(self):
        """Test calcul automatique SA dans la vue"""
        url = reverse('patients:save_quick_entretien_prenatal_precoce', args=[self.patient_femme.id])
        
        # Date à 20 semaines après DDG
        date_entretien = self.patient_femme.date_debut_grossesse + timedelta(days=140)
        
        form_data = {
            'date_entretien': date_entretien.strftime('%Y-%m-%d'),
            'conjoint_present': False
        }
        
        response = self.client.post(url, data=form_data)
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que les SA sont calculées
        entretien_cree = EntretienPrenatalPrecoce.objects.filter(
            date_entretien=date_entretien
        ).first()
        
        self.assertIsNotNone(entretien_cree)
        self.assertEqual(entretien_cree.semaines_amenorrhee, '20 SA')
    
    def test_htmx_responses(self):
        """Test réponses HTMX appropriées"""
        # Test historique (template partiel)
        url = reverse('patients:patient_entretiens_prenataux_precoces', args=[self.patient_femme.id])
        response = self.client.get(url, HTTP_HX_REQUEST='true')
        
        self.assertEqual(response.status_code, 200)
        # Ne devrait pas contenir le layout complet
        self.assertNotContains(response, '<html>')
        self.assertNotContains(response, '<head>')
        
        # Test formulaire rapide (template partiel)
        url_form = reverse('patients:entretien_prenatal_precoce_quick_form', args=[self.patient_femme.id])
        response_form = self.client.get(url_form, HTTP_HX_REQUEST='true')
        
        self.assertEqual(response_form.status_code, 200)
        self.assertNotContains(response_form, '<html>')
        self.assertContains(response_form, 'Nouvel Entretien Prénatal Précoce')
    
    def test_view_performance_queries(self):
        """Test performance des requêtes dans les vues"""
        # Créer plusieurs entretiens
        for i in range(3):
            EntretienPrenatalPrecoce.objects.create(
                patient=self.patient_femme,
                sage_femme=self.sage_femme,
                date_entretien=date.today() - timedelta(days=i),
                conjoint_present=i % 2 == 0
            )
        
        url = reverse('patients:patient_entretiens_prenataux_precoces', args=[self.patient_femme.id])
        
        # La vue devrait utiliser select_related pour optimiser les requêtes
        with self.assertNumQueries(2):  # 1 pour patient + 1 pour entretiens avec select_related
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
    
    def test_error_handling(self):
        """Test gestion des erreurs"""
        # Test avec données POST invalides
        url = reverse('patients:save_quick_entretien_prenatal_precoce', args=[self.patient_femme.id])
        
        # Date invalide
        form_data = {
            'date_entretien': 'invalid-date',
            'conjoint_present': False
        }
        
        response = self.client.post(url, data=form_data)
        self.assertEqual(response.status_code, 200)
        # Devrait contenir le formulaire avec erreurs
        self.assertContains(response, 'error')
    
    def test_context_data_in_views(self):
        """Test données de contexte dans les vues"""
        # Test vue historique
        url = reverse('patients:patient_entretiens_prenataux_precoces', args=[self.patient_femme.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Vérifier que les entretiens sont triés par date décroissante
        entretiens = response.context['entretiens'] if 'entretiens' in response.context else []
        if len(entretiens) > 1:
            dates = [e.date_entretien for e in entretiens]
            self.assertEqual(dates, sorted(dates, reverse=True))