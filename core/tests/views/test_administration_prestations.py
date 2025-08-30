"""
Tests pour les vues d'administration des prestations
"""
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from decimal import Decimal

from core.models.prestation import Prestation
from core.models.cadre_exercice import CadreExercice
from core.models.acte import Acte, TarifPeriode
from core.models.sagefemme import SageFemme
from core.models.periode_activite import PeriodeActivite

User = get_user_model()


class PrestationViewsBaseTest(TestCase):
    """Classe de base pour les tests des vues prestations"""
    
    def setUp(self):
        """Configuration commune des tests"""
        self.client = Client()
        
        # Créer un utilisateur sage-femme titulaire
        self.user = User.objects.create_user(
            email='titulaire@test.com',
            password='testpass123'
        )
        
        self.sagefemme = SageFemme.objects.create(
            user=self.user,
            nom='Test',
            prenom='Sage-femme',
            titre='Sage-femme',
            telephone='123456789',
            email='titulaire@test.com',
            rue='123 rue Test',
            code_postal='98800',
            ville='Nouméa',
            numero_cafat='123456',
            ridet='123456789',
            rib='123456789012',
            banque='Test Bank',
            situation='titulaire',
            is_active=True
        )
        
        self.today = timezone.now().date()
        
        # Créer une période d'activité active pour la sage-femme
        PeriodeActivite.objects.create(
            sage_femme=self.sagefemme,
            date_debut=self.today - timedelta(days=30),
            commentaire="Période de test"
        )
        
        # Mettre à jour le statut de l'utilisateur
        self.user.update_active_status()
        # Éviter la redirection vers changement de mot de passe
        self.user.must_change_password = False
        self.user.save()
        
        # Créer des cadres d'exercice
        self.cadre1 = CadreExercice.objects.create(
            label='Suivi de grossesse',
            description='Cadre d\'exercice pour le suivi de grossesse'
        )
        
        self.cadre2 = CadreExercice.objects.create(
            label='Post-partum',
            description='Cadre d\'exercice pour le suivi post-partum'
        )
        
        # Créer des actes
        self.acte1 = Acte.objects.create(
            code='CSF',
            libelle='Consultation Sage-Femme'
        )
        
        self.acte2 = Acte.objects.create(
            code='VPN',
            libelle='Visite post-natale'
        )
        
        # Créer des tarifs
        TarifPeriode.objects.create(
            acte=self.acte1,
            cout_xpf=5000,
            date_debut=self.today - timedelta(days=30)
        )
        
        TarifPeriode.objects.create(
            acte=self.acte2,
            cout_xpf=4500,
            date_debut=self.today - timedelta(days=30)
        )
        
        # Créer des prestations de test
        self.prestation1 = Prestation.objects.create(
            cadre_exercice=self.cadre1,
            designation='Consultation prénatale standard',
            acte=self.acte1,
            cotation=Decimal('1.5'),
            entente_prealable='Nécessaire'
        )
        
        self.prestation2 = Prestation.objects.create(
            cadre_exercice=self.cadre2,
            designation='Visite de contrôle post-natal',
            acte=self.acte2,
            cotation=Decimal('1.0'),
            entente_prealable='Non nécessaire'
        )
    
    def login_as_titulaire(self):
        """Se connecter en tant que titulaire"""
        self.client.login(email='titulaire@test.com', password='testpass123')


class AdministrationPrestationsViewTests(PrestationViewsBaseTest):
    """Tests pour la vue principale d'administration des prestations"""
    
    def test_administration_prestations_view_success_titulaire(self):
        """Test accès autorisé pour titulaire"""
        self.login_as_titulaire()
        
        url = reverse('administration:administration_prestations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Administration - Prestations')
        self.assertContains(response, 'Consultation prénatale standard')
        self.assertContains(response, 'Visite de contrôle post-natal')
    
    def test_administration_prestations_view_redirect_anonymous(self):
        """Test redirection pour utilisateur anonyme"""
        url = reverse('administration:administration_prestations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
    
    def test_administration_prestations_view_forbidden_non_titulaire(self):
        """Test accès refusé pour non-titulaire"""
        # Créer un collaborateur
        user_collab = User.objects.create_user(
            email='collab@test.com',
            password='testpass123'
        )
        
        SageFemme.objects.create(
            user=user_collab,
            nom='Collaborateur',
            prenom='Test',
            titre='Sage-femme',
            telephone='123456789',
            email='collab@test.com',
            rue='123 rue Test',
            code_postal='98800',
            ville='Nouméa',
            numero_cafat='123457',
            ridet='123456790',
            rib='123456789013',
            banque='Test Bank',
            situation='collaborateur',
            is_active=True
        )
        
        self.client.login(email='collab@test.com', password='testpass123')
        
        url = reverse('administration:administration_prestations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)  # Redirect to home
    
    def test_administration_prestations_context(self):
        """Test du contexte de la vue"""
        self.login_as_titulaire()
        
        url = reverse('administration:administration_prestations')
        response = self.client.get(url)
        
        self.assertIn('page_title', response.context)
        self.assertIn('prestations', response.context)
        self.assertIn('cadres_exercice', response.context)
        self.assertIn('actes', response.context)
        self.assertEqual(response.context['section'], 'administration')


class PrestationListViewTests(PrestationViewsBaseTest):
    """Tests pour la vue liste HTMX des prestations"""
    
    def test_prestation_list_view_success(self):
        """Test liste des prestations"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Consultation prénatale standard')
        self.assertContains(response, 'Visite de contrôle post-natal')
    
    def test_prestation_list_view_with_search(self):
        """Test recherche dans la liste des prestations"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_list')
        response = self.client.get(url, {'search': 'prénatale'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Consultation prénatale standard')
        self.assertNotContains(response, 'Visite de contrôle post-natal')
    
    def test_prestation_list_view_search_by_cadre(self):
        """Test recherche par cadre d'exercice"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_list')
        response = self.client.get(url, {'search': 'Post-partum'})
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Consultation prénatale standard')
        self.assertContains(response, 'Visite de contrôle post-natal')
    
    def test_prestation_list_view_filter_by_cadre_exercice(self):
        """Test filtrage par cadre d'exercice"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_list')
        response = self.client.get(url, {'cadre_exercice': self.cadre1.pk})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Consultation prénatale standard')
        self.assertNotContains(response, 'Visite de contrôle post-natal')
    
    def test_prestation_list_view_filter_by_acte(self):
        """Test filtrage par acte"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_list')
        response = self.client.get(url, {'acte': self.acte2.pk})
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Consultation prénatale standard')
        self.assertContains(response, 'Visite de contrôle post-natal')
    
    def test_prestation_list_view_forbidden(self):
        """Test accès refusé pour non-titulaire"""
        url = reverse('administration:prestation_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 403)


class PrestationCreateViewTests(PrestationViewsBaseTest):
    """Tests pour la vue de création de prestation"""
    
    def test_prestation_create_view_get(self):
        """Test affichage du formulaire de création"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ajouter une prestation')
        self.assertContains(response, 'Cadre d\'exercice')
        self.assertContains(response, 'Désignation')
    
    def test_prestation_create_view_post_success(self):
        """Test création de prestation avec succès"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_create')
        data = {
            'cadre_exercice': self.cadre1.pk,
            'designation': 'Nouvelle consultation',
            'acte': self.acte1.pk,
            'cotation': '2.0',
            'entente_prealable': 'Obligatoire'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'showNotification')
        self.assertContains(response, 'créée avec succès')
        
        # Vérifier que la prestation a été créée
        self.assertTrue(Prestation.objects.filter(designation='Nouvelle consultation').exists())
    
    def test_prestation_create_view_post_with_all_fields(self):
        """Test création avec tous les champs renseignés"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_create')
        data = {
            'cadre_exercice': self.cadre2.pk,
            'designation': 'Consultation complète',
            'limite': 'Maximum 5 par grossesse',
            'acte': self.acte2.pk,
            'cotation': '2.5',
            'entente_prealable': 'Obligatoire avec justificatifs',
            'assurance_maladie': '100%',
            'assurance_maternite_normale': 'Standard',
            'assurance_maternite_pathologie': 'Majoré',
            'observation': 'Consultation spécialisée'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'créée avec succès')
        
        # Vérifier tous les champs
        prestation = Prestation.objects.get(designation='Consultation complète')
        self.assertEqual(prestation.limite, 'Maximum 5 par grossesse')
        self.assertEqual(prestation.cotation, Decimal('2.5'))
        self.assertEqual(prestation.assurance_maladie, '100%')
    
    def test_prestation_create_view_post_invalid_data(self):
        """Test création avec données invalides"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_create')
        data = {
            'cadre_exercice': '',  # Champ obligatoire vide
            'designation': 'Test',
            'acte': self.acte1.pk,
            'cotation': '1.0',
            'entente_prealable': 'Test'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ce champ est obligatoire')
    
    def test_prestation_create_view_post_negative_cotation(self):
        """Test création avec cotation négative"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_create')
        data = {
            'cadre_exercice': self.cadre1.pk,
            'designation': 'Test',
            'acte': self.acte1.pk,
            'cotation': '-1.0',  # Cotation négative
            'entente_prealable': 'Test'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'La cotation doit être un nombre positif')
    
    def test_prestation_create_view_forbidden(self):
        """Test accès refusé"""
        url = reverse('administration:prestation_create')
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, 403)


class PrestationDetailViewTests(PrestationViewsBaseTest):
    """Tests pour la vue détail de prestation"""
    
    def test_prestation_detail_view_success(self):
        """Test affichage détail de prestation"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_detail', kwargs={'pk': self.prestation1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Consultation prénatale standard')
        self.assertContains(response, self.cadre1.label)
        self.assertContains(response, self.acte1.code)
        self.assertContains(response, '1.5')  # Cotation
    
    def test_prestation_detail_view_with_tarif(self):
        """Test détail avec tarif calculé"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_detail', kwargs={'pk': self.prestation1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Tarif = 1.5 * 5000 = 7500 XPF
        self.assertContains(response, '7500 XPF')
    
    def test_prestation_detail_view_not_found(self):
        """Test prestation inexistante"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)


class PrestationUpdateViewTests(PrestationViewsBaseTest):
    """Tests pour la vue de modification de prestation"""
    
    def test_prestation_update_view_get(self):
        """Test affichage du formulaire de modification"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_update', kwargs={'pk': self.prestation1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Modifier la prestation')
        self.assertContains(response, 'Consultation prénatale standard')
    
    def test_prestation_update_view_post_success(self):
        """Test modification avec succès"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_update', kwargs={'pk': self.prestation1.pk})
        data = {
            'cadre_exercice': self.cadre1.pk,
            'designation': 'Consultation prénatale modifiée',
            'acte': self.acte1.pk,
            'cotation': '2.0',
            'entente_prealable': 'Modifiée'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'modifiée avec succès')
        
        # Vérifier la modification
        self.prestation1.refresh_from_db()
        self.assertEqual(self.prestation1.designation, 'Consultation prénatale modifiée')
        self.assertEqual(self.prestation1.cotation, Decimal('2.0'))
    
    def test_prestation_update_view_post_change_acte(self):
        """Test modification de l'acte associé"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_update', kwargs={'pk': self.prestation1.pk})
        data = {
            'cadre_exercice': self.prestation1.cadre_exercice.pk,
            'designation': self.prestation1.designation,
            'acte': self.acte2.pk,  # Changer l'acte
            'cotation': self.prestation1.cotation,
            'entente_prealable': self.prestation1.entente_prealable
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier le changement d'acte
        self.prestation1.refresh_from_db()
        self.assertEqual(self.prestation1.acte, self.acte2)
        # Le tarif devrait changer aussi (1.5 * 4500 = 6750)
        self.assertEqual(self.prestation1.tarif, 1.5 * 4500)
    
    def test_prestation_update_view_post_invalid_data(self):
        """Test modification avec données invalides"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_update', kwargs={'pk': self.prestation1.pk})
        data = {
            'cadre_exercice': '',  # Champ obligatoire vide
            'designation': 'Test',
            'acte': self.acte1.pk,
            'cotation': '1.0',
            'entente_prealable': 'Test'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ce champ est obligatoire')


class PrestationDeleteViewTests(PrestationViewsBaseTest):
    """Tests pour la vue de suppression de prestation"""
    
    def test_prestation_delete_view_success(self):
        """Test suppression avec succès"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_delete', kwargs={'pk': self.prestation1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'supprimée avec succès')
        
        # Vérifier la suppression
        self.assertFalse(Prestation.objects.filter(pk=self.prestation1.pk).exists())
    
    def test_prestation_delete_view_method_not_allowed(self):
        """Test méthode non autorisée"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_delete', kwargs={'pk': self.prestation1.pk})
        response = self.client.get(url)  # GET au lieu de DELETE
        
        self.assertEqual(response.status_code, 405)
    
    def test_prestation_delete_view_not_found(self):
        """Test suppression prestation inexistante"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_delete', kwargs={'pk': 9999})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 404)


class PrestationFormsTests(PrestationViewsBaseTest):
    """Tests pour les formulaires des prestations"""
    
    def test_prestation_form_clean_cotation_positive(self):
        """Test validation cotation positive"""
        from core.views.administration import PrestationForm
        
        form = PrestationForm(data={
            'cadre_exercice': self.cadre1.pk,
            'designation': 'Test',
            'acte': self.acte1.pk,
            'cotation': '2.5',
            'entente_prealable': 'Test'
        })
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['cotation'], Decimal('2.5'))
    
    def test_prestation_form_clean_cotation_negative(self):
        """Test validation cotation négative"""
        from core.views.administration import PrestationForm
        
        form = PrestationForm(data={
            'cadre_exercice': self.cadre1.pk,
            'designation': 'Test',
            'acte': self.acte1.pk,
            'cotation': '-1.0',
            'entente_prealable': 'Test'
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('cotation', form.errors)
        self.assertIn('positif', form.errors['cotation'][0])
    
    def test_prestation_form_clean_cotation_zero(self):
        """Test validation cotation zéro"""
        from core.views.administration import PrestationForm
        
        form = PrestationForm(data={
            'cadre_exercice': self.cadre1.pk,
            'designation': 'Test',
            'acte': self.acte1.pk,
            'cotation': '0',
            'entente_prealable': 'Test'
        })
        
        # Le formulaire peut être valide mais le modèle doit valider
        if form.is_valid():
            prestation = form.save(commit=False)
            with self.assertRaises(ValidationError):
                prestation.clean()
        else:
            self.assertIn('cotation', form.errors)
    
    def test_prestation_form_optional_fields(self):
        """Test que les champs optionnels peuvent être vides"""
        from core.views.administration import PrestationForm
        
        form = PrestationForm(data={
            'cadre_exercice': self.cadre1.pk,
            'designation': 'Test minimal',
            'acte': self.acte1.pk,
            'cotation': '1.0',
            'entente_prealable': 'Nécessaire'
            # Tous les autres champs optionnels omis
        })
        
        self.assertTrue(form.is_valid())


class PrestationIntegrationTests(PrestationViewsBaseTest):
    """Tests d'intégration pour les vues prestations"""
    
    def test_full_prestation_lifecycle(self):
        """Test complet du cycle de vie d'une prestation"""
        self.login_as_titulaire()
        
        # 1. Créer une prestation
        create_url = reverse('administration:prestation_create')
        create_data = {
            'cadre_exercice': self.cadre1.pk,
            'designation': 'Prestation test lifecycle',
            'limite': 'Test limite',
            'acte': self.acte1.pk,
            'cotation': '3.0',
            'entente_prealable': 'Test entente',
            'observation': 'Test observation'
        }
        create_response = self.client.post(create_url, create_data)
        self.assertEqual(create_response.status_code, 200)
        
        # Récupérer la prestation créée
        prestation = Prestation.objects.get(designation='Prestation test lifecycle')
        
        # 2. Voir les détails
        detail_url = reverse('administration:prestation_detail', kwargs={'pk': prestation.pk})
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, 'Prestation test lifecycle')
        
        # 3. Modifier la prestation
        update_url = reverse('administration:prestation_update', kwargs={'pk': prestation.pk})
        update_data = create_data.copy()
        update_data['designation'] = 'Prestation test modifiée'
        update_data['cotation'] = '3.5'
        update_response = self.client.post(update_url, update_data)
        self.assertEqual(update_response.status_code, 200)
        
        # Vérifier la modification
        prestation.refresh_from_db()
        self.assertEqual(prestation.designation, 'Prestation test modifiée')
        self.assertEqual(prestation.cotation, Decimal('3.5'))
        
        # 4. Supprimer la prestation
        delete_url = reverse('administration:prestation_delete', kwargs={'pk': prestation.pk})
        delete_response = self.client.delete(delete_url)
        self.assertEqual(delete_response.status_code, 200)
        
        # Vérifier la suppression
        self.assertFalse(Prestation.objects.filter(pk=prestation.pk).exists())
    
    def test_prestation_with_multiple_cadres_and_actes(self):
        """Test prestations avec plusieurs cadres et actes"""
        self.login_as_titulaire()
        
        # Créer des prestations avec différentes combinaisons
        prestations_data = [
            (self.cadre1, self.acte1, 'Prestation 1-1'),
            (self.cadre1, self.acte2, 'Prestation 1-2'),
            (self.cadre2, self.acte1, 'Prestation 2-1'),
            (self.cadre2, self.acte2, 'Prestation 2-2'),
        ]
        
        for cadre, acte, designation in prestations_data:
            Prestation.objects.create(
                cadre_exercice=cadre,
                designation=designation,
                acte=acte,
                cotation=Decimal('1.0'),
                entente_prealable='Test'
            )
        
        # Tester le filtrage par cadre
        list_url = reverse('administration:prestation_list')
        
        # Filtrage par cadre 1
        response = self.client.get(list_url, {'cadre_exercice': self.cadre1.pk})
        self.login_as_titulaire()
        response = self.client.get(list_url, {'cadre_exercice': self.cadre1.pk})
        self.assertContains(response, 'Prestation 1-1')
        self.assertContains(response, 'Prestation 1-2')
        self.assertNotContains(response, 'Prestation 2-1')
        
        # Filtrage par acte 1
        response = self.client.get(list_url, {'acte': self.acte1.pk})
        self.assertContains(response, 'Prestation 1-1')
        self.assertContains(response, 'Prestation 2-1')
        self.assertNotContains(response, 'Prestation 1-2')
    
    def test_prestation_tarif_calculation_accuracy(self):
        """Test précision du calcul des tarifs"""
        self.login_as_titulaire()
        
        # Créer une prestation avec cotation décimale précise
        prestation = Prestation.objects.create(
            cadre_exercice=self.cadre1,
            designation='Test précision',
            acte=self.acte1,
            cotation=Decimal('1.23'),  # Valeur décimale précise
            entente_prealable='Test'
        )
        
        # Vérifier le calcul: 1.23 * 5000 = 6150.0
        expected_tarif = float(Decimal('1.23')) * 5000
        self.assertEqual(prestation.tarif, expected_tarif)
        
        # Vérifier l'affichage
        detail_url = reverse('administration:prestation_detail', kwargs={'pk': prestation.pk})
        self.login_as_titulaire()
        response = self.client.get(detail_url)
        self.assertContains(response, '6150 XPF')


class PrestationPermissionTests(PrestationViewsBaseTest):
    """Tests des permissions pour les vues prestations"""
    
    def test_superuser_access(self):
        """Test accès superutilisateur"""
        superuser = User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass'
        )
        
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('administration:administration_prestations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
    
    def test_all_prestation_views_require_titulaire(self):
        """Test que toutes les vues prestations nécessitent les droits titulaire"""
        urls_to_test = [
            ('administration:prestation_list', 'GET', {}),
            ('administration:prestation_create', 'GET', {}),
            ('administration:prestation_detail', 'GET', {'pk': self.prestation1.pk}),
            ('administration:prestation_update', 'GET', {'pk': self.prestation1.pk}),
        ]
        
        for url_name, method, kwargs in urls_to_test:
            with self.subTest(url=url_name):
                url = reverse(url_name, kwargs=kwargs)
                
                # Test sans authentification
                if method == 'GET':
                    response = self.client.get(url)
                elif method == 'POST':
                    response = self.client.post(url, {})
                
                # Devrait rediriger vers login ou être interdit
                self.assertIn(response.status_code, [302, 403])
    
    def test_prestation_delete_requires_delete_method(self):
        """Test que la suppression nécessite la méthode DELETE"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_delete', kwargs={'pk': self.prestation1.pk})
        
        # Tester avec GET (devrait échouer)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        
        # Tester avec POST (devrait échouer)
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 405)
        
        # Tester avec DELETE (devrait fonctionner)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)