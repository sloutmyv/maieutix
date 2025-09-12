"""
Tests d'intégration pour EntretienPrenatalPrecoce
"""

from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, timedelta

from core.models import EntretienPrenatalPrecoce, Patient, SageFemme, Caisse
from authentication.models import SageFemmeUser


class EntretienPrenatalPrecoceIntegrationTest(TestCase):
    """Tests d'intégration pour le workflow complet EPP"""
    
    def setUp(self):
        """Configuration des données de test"""
        # Client
        self.client = Client()
        
        # Caisse
        self.caisse = Caisse.objects.create(nom="CAFAT")
        
        # Utilisateur et sage-femme
        self.user = SageFemmeUser.objects.create_superuser(
            email='sage.femme@test.com',
            password='testpass123'
        )
        self.sage_femme = SageFemme.objects.create(
            user=self.user,
            nom='Martin',
            prenom='Dr Sophie',
            titre='Sage-Femme',
            telephone='123456789',
            email='sage.femme@test.com',
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
        
        # Connexion
        self.client.login(email='sage.femme@test.com', password='testpass123')
    
    def test_complete_epp_creation_workflow(self):
        """Test workflow complet de création d'un EPP"""
        # 1. Accéder à la page de détail patient
        patient_detail_url = reverse('patients:patient_detail', args=[self.patient_femme.id])
        response = self.client.get(patient_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Entretien prénatal précoce')
        
        # 2. Charger l'historique des EPP (initialement vide)
        history_url = reverse('patients:patient_entretiens_prenataux_precoces', args=[self.patient_femme.id])
        response = self.client.get(history_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aucun entretien')
        self.assertContains(response, 'Ajouter le premier entretien')
        
        # 3. Charger le formulaire rapide
        quick_form_url = reverse('patients:entretien_prenatal_precoce_quick_form', args=[self.patient_femme.id])
        response = self.client.get(quick_form_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nouvel Entretien Prénatal Précoce')
        self.assertContains(response, 'SA calculée automatiquement')
        self.assertContains(response, f"DDG: {self.patient_femme.date_debut_grossesse.strftime('%d/%m/%Y')}")
        
        # 4. Soumettre le formulaire avec données valides
        date_entretien = self.patient_femme.date_debut_grossesse + timedelta(days=140)  # 20 SA
        form_data = {
            'date_entretien': date_entretien.strftime('%Y-%m-%d'),
            'conjoint_present': True,
            'lieu_accouchement_prevu': 'Maternité CHT',
            'atcd_marquants_sante': 'Aucun ATCD particulier',
            'environnement_social_familial': 'Environnement familial stable',
            'projet_naissance_parentalite': 'Accouchement naturel souhaité, préparation parentale en cours',
            'ressenti': 'Très positive et confiante',
            'propositions_liens': 'Cours de préparation à la naissance, suivi nutritionnel'
        }
        
        save_url = reverse('patients:save_quick_entretien_prenatal_precoce', args=[self.patient_femme.id])
        response = self.client.post(save_url, data=form_data)
        self.assertEqual(response.status_code, 200)
        
        # 5. Vérifier que l'entretien a été créé correctement
        entretien = EntretienPrenatalPrecoce.objects.filter(patient=self.patient_femme).first()
        self.assertIsNotNone(entretien)
        self.assertEqual(entretien.date_entretien, date_entretien)
        self.assertTrue(entretien.conjoint_present)
        self.assertEqual(entretien.lieu_accouchement_prevu, 'Maternité CHT')
        self.assertEqual(entretien.sage_femme, self.sage_femme)
        self.assertEqual(entretien.semaines_amenorrhee, '20 SA')
        self.assertTrue(entretien.est_dans_periode_optimale)
        
        # 6. Vérifier l'historique mis à jour
        response = self.client.get(history_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Aucun entretien')
        self.assertContains(response, date_entretien.strftime('%d/%m/%Y'))
        self.assertContains(response, '20 SA')
        self.assertContains(response, 'Conjoint présent')
        self.assertContains(response, 'Maternité CHT')
        
        # 7. Tester l'affichage des détails en modal
        detail_url = reverse('patients:entretien_prenatal_precoce_detail', args=[entretien.id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Entretien du {date_entretien.strftime('%d/%m/%Y')}")
        self.assertContains(response, self.patient_femme.nom_complet)
        self.assertContains(response, '20 SA')
        self.assertContains(response, 'Oui')  # Conjoint présent
        self.assertContains(response, 'Maternité CHT')
        self.assertContains(response, 'closeModal()')
        
        # 8. Tester la suppression
        delete_url = reverse('patients:delete_entretien_prenatal_precoce', args=[entretien.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que l'entretien a été supprimé
        self.assertFalse(EntretienPrenatalPrecoce.objects.filter(id=entretien.id).exists())
    
    def test_epp_workflow_with_multiple_entries(self):
        """Test workflow avec plusieurs entretiens"""
        # Créer plusieurs entretiens
        dates_entretiens = [
            self.patient_femme.date_debut_grossesse + timedelta(days=112),  # 16 SA
            self.patient_femme.date_debut_grossesse + timedelta(days=140),  # 20 SA
            self.patient_femme.date_debut_grossesse + timedelta(days=196),  # 28 SA
        ]
        
        entretiens = []
        for i, date_entretien in enumerate(dates_entretiens):
            entretien = EntretienPrenatalPrecoce.objects.create(
                patient=self.patient_femme,
                sage_femme=self.sage_femme,
                date_entretien=date_entretien,
                conjoint_present=i % 2 == 0,
                lieu_accouchement_prevu=f'Lieu {i+1}',
                atcd_marquants_sante=f'ATCD {i+1}'
            )
            entretiens.append(entretien)
        
        # Vérifier l'affichage de l'historique
        history_url = reverse('patients:patient_entretiens_prenataux_precoces', args=[self.patient_femme.id])
        response = self.client.get(history_url)
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que tous les entretiens sont affichés
        for entretien in entretiens:
            self.assertContains(response, entretien.date_entretien.strftime('%d/%m/%Y'))
            self.assertContains(response, entretien.lieu_accouchement_prevu)
        
        # Vérifier l'ordre chronologique décroissant
        content = response.content.decode()
        pos_28sa = content.find('28 SA')
        pos_20sa = content.find('20 SA')
        pos_16sa = content.find('16 SA')
        
        self.assertTrue(pos_28sa < pos_20sa < pos_16sa)
    
    def test_epp_validation_workflow(self):
        """Test workflow de validation des erreurs"""
        # Tenter de créer un entretien avec date dans le futur
        form_data = {
            'date_entretien': (date.today() + timedelta(days=10)).strftime('%Y-%m-%d'),
            'conjoint_present': False
        }
        
        save_url = reverse('patients:save_quick_entretien_prenatal_precoce', args=[self.patient_femme.id])
        response = self.client.post(save_url, data=form_data)
        
        # Vérifier que l'erreur est affichée
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ne peut pas être dans le futur')
        
        # Vérifier qu'aucun entretien n'a été créé
        self.assertEqual(EntretienPrenatalPrecoce.objects.filter(patient=self.patient_femme).count(), 0)
    
    def test_epp_sa_calculation_workflow(self):
        """Test workflow de calcul automatique des SA"""
        # Créer entretien à différentes dates
        test_cases = [
            (70, '10 SA'),      # 10 semaines exactement
            (73, '10 SA + 3j'), # 10 semaines + 3 jours
            (140, '20 SA'),     # 20 semaines exactement
            (147, '21 SA'),     # 21 semaines exactement
        ]
        
        for jours_apres_ddg, sa_attendue in test_cases:
            date_entretien = self.patient_femme.date_debut_grossesse + timedelta(days=jours_apres_ddg)
            
            form_data = {
                'date_entretien': date_entretien.strftime('%Y-%m-%d'),
                'conjoint_present': False,
                'atcd_marquants_sante': f'Test {sa_attendue}'
            }
            
            save_url = reverse('patients:save_quick_entretien_prenatal_precoce', args=[self.patient_femme.id])
            response = self.client.post(save_url, data=form_data)
            self.assertEqual(response.status_code, 200)
            
            # Vérifier le calcul SA
            entretien = EntretienPrenatalPrecoce.objects.filter(
                atcd_marquants_sante=f'Test {sa_attendue}'
            ).first()
            self.assertIsNotNone(entretien)
            self.assertEqual(entretien.semaines_amenorrhee, sa_attendue)
    
    def test_epp_periode_optimale_workflow(self):
        """Test workflow d'évaluation de la période optimale"""
        test_cases = [
            (105, False, 'limite'),    # 15 SA - Trop tôt
            (112, True, 'optimal'),    # 16 SA - Limite basse optimale
            (140, True, 'optimal'),    # 20 SA - Milieu optimal
            (196, True, 'optimal'),    # 28 SA - Limite haute optimale
            (210, False, 'limite'),    # 30 SA - Trop tard
        ]
        
        for jours_apres_ddg, est_optimal, indicateur in test_cases:
            date_entretien = self.patient_femme.date_debut_grossesse + timedelta(days=jours_apres_ddg)
            
            entretien = EntretienPrenatalPrecoce.objects.create(
                patient=self.patient_femme,
                sage_femme=self.sage_femme,
                date_entretien=date_entretien,
                conjoint_present=False
            )
            
            self.assertEqual(entretien.est_dans_periode_optimale, est_optimal)
            self.assertEqual(entretien.indicateur_periode, indicateur)
    
    def test_epp_patient_filtering_workflow(self):
        """Test workflow de filtrage des patients"""
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
        
        # Tenter d'accéder aux vues EPP pour patient sans DDG
        urls_to_test = [
            ('patients:patient_entretiens_prenataux_precoces', patient_sans_ddg.id),
            ('patients:entretien_prenatal_precoce_quick_form', patient_sans_ddg.id),
            ('patients:save_quick_entretien_prenatal_precoce', patient_sans_ddg.id),
        ]
        
        for url_name, patient_id in urls_to_test:
            url = reverse(url_name, args=[patient_id])
            response = self.client.get(url) if 'save' not in url_name else self.client.post(url, {})
            self.assertEqual(response.status_code, 404, f"URL {url_name} devrait retourner 404")
        
        # Même test pour patient bébé
        for url_name, _ in urls_to_test:
            url = reverse(url_name, args=[patient_bebe.id])
            response = self.client.get(url) if 'save' not in url_name else self.client.post(url, {})
            self.assertEqual(response.status_code, 404, f"URL {url_name} devrait retourner 404")
    
    def test_epp_permission_workflow(self):
        """Test workflow des permissions d'accès"""
        # Déconnexion
        self.client.logout()
        
        # Tenter d'accéder aux vues sans authentification
        protected_urls = [
            reverse('patients:patient_entretiens_prenataux_precoces', args=[self.patient_femme.id]),
            reverse('patients:entretien_prenatal_precoce_quick_form', args=[self.patient_femme.id]),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Redirection vers login
            self.assertIn('connexion', response.url)
    
    def test_epp_htmx_workflow(self):
        """Test workflow HTMX avec headers appropriés"""
        # Test avec headers HTMX
        history_url = reverse('patients:patient_entretiens_prenataux_precoces', args=[self.patient_femme.id])
        response = self.client.get(history_url, HTTP_HX_REQUEST='true')
        
        self.assertEqual(response.status_code, 200)
        # Les templates HTMX ne devraient pas contenir de balises HTML complètes
        self.assertNotContains(response, '<html>')
        self.assertNotContains(response, '<!DOCTYPE')
        
        # Test formulaire HTMX
        form_url = reverse('patients:entretien_prenatal_precoce_quick_form', args=[self.patient_femme.id])
        response = self.client.get(form_url, HTTP_HX_REQUEST='true')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'hx-post')  # Attributs HTMX présents
        self.assertContains(response, 'hx-target')
    
    def test_complete_crud_workflow(self):
        """Test workflow CRUD complet"""
        # CREATE
        entretien = EntretienPrenatalPrecoce.objects.create(
            patient=self.patient_femme,
            sage_femme=self.sage_femme,
            date_entretien=date.today(),
            conjoint_present=True,
            lieu_accouchement_prevu='Test CRUD'
        )
        
        # READ
        history_url = reverse('patients:patient_entretiens_prenataux_precoces', args=[self.patient_femme.id])
        response = self.client.get(history_url)
        self.assertContains(response, 'Test CRUD')
        
        detail_url = reverse('patients:entretien_prenatal_precoce_detail', args=[entretien.id])
        response = self.client.get(detail_url)
        self.assertContains(response, 'Test CRUD')
        
        # UPDATE (via formulaire modal)
        modal_url = reverse('patients:entretien_prenatal_precoce_modal', args=[self.patient_femme.id])
        response = self.client.get(modal_url)
        self.assertEqual(response.status_code, 200)
        
        # DELETE
        delete_url = reverse('patients:delete_entretien_prenatal_precoce', args=[entretien.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 200)
        
        # Vérifier suppression
        self.assertFalse(EntretienPrenatalPrecoce.objects.filter(id=entretien.id).exists())
    
    def test_performance_optimization_workflow(self):
        """Test workflow d'optimisation des performances"""
        # Créer plusieurs entretiens
        for i in range(10):
            EntretienPrenatalPrecoce.objects.create(
                patient=self.patient_femme,
                sage_femme=self.sage_femme,
                date_entretien=date.today() - timedelta(days=i),
                conjoint_present=i % 2 == 0
            )
        
        # Test que les requêtes sont optimisées avec select_related
        history_url = reverse('patients:patient_entretiens_prenataux_precoces', args=[self.patient_femme.id])
        
        with self.assertNumQueries(2):  # 1 patient + 1 entretiens avec select_related
            response = self.client.get(history_url)
            self.assertEqual(response.status_code, 200)