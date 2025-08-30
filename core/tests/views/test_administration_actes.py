"""
Tests pour les vues d'administration des actes médicaux
"""
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from core.models.acte import Acte, TarifPeriode
from core.models.sagefemme import SageFemme
from core.models.periode_activite import PeriodeActivite

User = get_user_model()


class ActeViewsBaseTest(TestCase):
    """Classe de base pour les tests des vues actes"""
    
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
        
        # Créer des actes de test
        self.acte1 = Acte.objects.create(
            code='CSF',
            libelle='Consultation Sage-Femme'
        )
        
        self.acte2 = Acte.objects.create(
            code='VGC',
            libelle='Visite gynécologique complète'
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
        
        # Créer des tarifs de test
        self.tarif1 = TarifPeriode.objects.create(
            acte=self.acte1,
            cout_xpf=5000,
            date_debut=self.today - timedelta(days=30)
        )
    
    def login_as_titulaire(self):
        """Se connecter en tant que titulaire"""
        self.client.login(email='titulaire@test.com', password='testpass123')


class AdministrationActesViewTests(ActeViewsBaseTest):
    """Tests pour la vue principale d'administration des actes"""
    
    def test_administration_actes_view_success_titulaire(self):
        """Test accès autorisé pour titulaire"""
        self.login_as_titulaire()
        
        url = reverse('administration:administration_actes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Administration - Actes')
        self.assertContains(response, self.acte1.code)
        self.assertContains(response, self.acte2.code)
    
    def test_administration_actes_view_redirect_anonymous(self):
        """Test redirection pour utilisateur anonyme"""
        url = reverse('administration:administration_actes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
    
    def test_administration_actes_view_forbidden_non_titulaire(self):
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
        
        url = reverse('administration:administration_actes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)  # Redirect to home
    
    def test_administration_actes_context(self):
        """Test du contexte de la vue"""
        self.login_as_titulaire()
        
        url = reverse('administration:administration_actes')
        response = self.client.get(url)
        
        self.assertIn('page_title', response.context)
        self.assertIn('actes', response.context)
        self.assertEqual(response.context['section'], 'administration')


class ActeListViewTests(ActeViewsBaseTest):
    """Tests pour la vue liste HTMX des actes"""
    
    def test_acte_list_view_success(self):
        """Test liste des actes"""
        self.login_as_titulaire()
        
        url = reverse('administration:acte_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.acte1.code)
        self.assertContains(response, self.acte2.code)
    
    def test_acte_list_view_with_search(self):
        """Test recherche dans la liste des actes"""
        self.login_as_titulaire()
        
        url = reverse('administration:acte_list')
        response = self.client.get(url, {'search': 'CSF'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.acte1.code)
        self.assertNotContains(response, self.acte2.code)
    
    def test_acte_list_view_search_by_libelle(self):
        """Test recherche par libellé"""
        self.login_as_titulaire()
        
        url = reverse('administration:acte_list')
        response = self.client.get(url, {'search': 'gynécologique'})
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.acte1.code)
        self.assertContains(response, self.acte2.code)
    
    def test_acte_list_view_forbidden(self):
        """Test accès refusé pour non-titulaire"""
        url = reverse('administration:acte_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 403)


class ActeCreateViewTests(ActeViewsBaseTest):
    """Tests pour la vue de création d'acte"""
    
    def test_acte_create_view_get(self):
        """Test affichage du formulaire de création"""
        self.login_as_titulaire()
        
        url = reverse('administration:acte_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ajouter un acte')
        self.assertContains(response, 'Code de l\'acte')
    
    def test_acte_create_view_post_success(self):
        """Test création d'acte avec succès"""
        self.login_as_titulaire()
        
        url = reverse('administration:acte_create')
        data = {
            'code': 'ACO',
            'libelle': 'Accompagnement obstétrical'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'showNotification')
        self.assertContains(response, 'ACO créé avec succès')
        
        # Vérifier que l'acte a été créé
        self.assertTrue(Acte.objects.filter(code='ACO').exists())
    
    def test_acte_create_view_post_invalid_data(self):
        """Test création avec données invalides"""
        self.login_as_titulaire()
        
        url = reverse('administration:acte_create')
        data = {
            'code': '',  # Code vide
            'libelle': 'Test'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ce champ est obligatoire')
    
    def test_acte_create_view_post_duplicate_code(self):
        """Test création avec code déjà existant"""
        self.login_as_titulaire()
        
        url = reverse('administration:acte_create')
        data = {
            'code': 'CSF',  # Code déjà existant
            'libelle': 'Autre consultation'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Un acte avec ce code existe déjà')
    
    def test_acte_create_view_forbidden(self):
        """Test accès refusé"""
        url = reverse('administration:acte_create')
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, 403)


class ActeDetailViewTests(ActeViewsBaseTest):
    """Tests pour la vue détail d'acte"""
    
    def test_acte_detail_view_success(self):
        """Test affichage détail d'acte"""
        self.login_as_titulaire()
        
        url = reverse('administration:acte_detail', kwargs={'pk': self.acte1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Détails de l\'acte')
        self.assertContains(response, self.acte1.code)
        self.assertContains(response, self.acte1.libelle)
        self.assertContains(response, '5000 XPF')  # Tarif actuel
    
    def test_acte_detail_view_with_tarifs(self):
        """Test détail avec plusieurs tarifs"""
        self.login_as_titulaire()
        
        # Ajouter un second tarif
        TarifPeriode.objects.create(
            acte=self.acte1,
            cout_xpf=6000,
            date_debut=self.today,
            date_fin=self.today + timedelta(days=30)
        )
        
        url = reverse('administration:acte_detail', kwargs={'pk': self.acte1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '5000 XPF')
        self.assertContains(response, '6000 XPF')
    
    def test_acte_detail_view_not_found(self):
        """Test acte inexistant"""
        self.login_as_titulaire()
        
        url = reverse('administration:acte_detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)


class ActeUpdateViewTests(ActeViewsBaseTest):
    """Tests pour la vue de modification d'acte"""
    
    def test_acte_update_view_get(self):
        """Test affichage du formulaire de modification"""
        self.login_as_titulaire()
        
        url = reverse('administration:acte_update', kwargs={'pk': self.acte1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Modifier l\'acte')
        self.assertContains(response, self.acte1.code)
        self.assertContains(response, self.acte1.libelle)
    
    def test_acte_update_view_post_success(self):
        """Test modification avec succès"""
        self.login_as_titulaire()
        
        url = reverse('administration:acte_update', kwargs={'pk': self.acte1.pk})
        data = {
            'code': 'CSF',
            'libelle': 'Consultation Sage-Femme Modifiée'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'modifié avec succès')
        
        # Vérifier la modification
        self.acte1.refresh_from_db()
        self.assertEqual(self.acte1.libelle, 'Consultation Sage-Femme Modifiée')
    
    def test_acte_update_view_post_invalid_data(self):
        """Test modification avec données invalides"""
        self.login_as_titulaire()
        
        url = reverse('administration:acte_update', kwargs={'pk': self.acte1.pk})
        data = {
            'code': '',  # Code vide
            'libelle': 'Test'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ce champ est obligatoire')


class ActeDeleteViewTests(ActeViewsBaseTest):
    """Tests pour la vue de suppression d'acte"""
    
    def test_acte_delete_view_success(self):
        """Test suppression avec succès"""
        self.login_as_titulaire()
        
        url = reverse('administration:acte_delete', kwargs={'pk': self.acte1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'supprimé avec succès')
        
        # Vérifier la suppression
        self.assertFalse(Acte.objects.filter(pk=self.acte1.pk).exists())
    
    def test_acte_delete_view_method_not_allowed(self):
        """Test méthode non autorisée"""
        self.login_as_titulaire()
        
        url = reverse('administration:acte_delete', kwargs={'pk': self.acte1.pk})
        response = self.client.get(url)  # GET au lieu de DELETE
        
        self.assertEqual(response.status_code, 405)
    
    def test_acte_delete_view_not_found(self):
        """Test suppression acte inexistant"""
        self.login_as_titulaire()
        
        url = reverse('administration:acte_delete', kwargs={'pk': 9999})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 404)


class TarifPeriodeAPIViewTests(ActeViewsBaseTest):
    """Tests pour les vues API des périodes tarifaires"""
    
    def test_ajouter_tarif_periode_success(self):
        """Test ajout de période tarifaire"""
        self.login_as_titulaire()
        
        url = reverse('administration:ajouter_tarif', kwargs={'pk': self.acte2.pk})
        data = {
            'cout_xpf': 8000,
            'date_debut': str(self.today),
            'date_fin': str(self.today + timedelta(days=30))
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertTrue(json_response['success'])
        
        # Vérifier création
        self.assertTrue(
            TarifPeriode.objects.filter(acte=self.acte2, cout_xpf=8000).exists()
        )
    
    def test_ajouter_tarif_periode_invalid_data(self):
        """Test ajout avec données invalides"""
        self.login_as_titulaire()
        
        url = reverse('administration:ajouter_tarif', kwargs={'pk': self.acte2.pk})
        data = {
            'cout_xpf': 'invalid',  # Valeur invalide
            'date_debut': str(self.today)
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertFalse(json_response['success'])
    
    def test_modifier_tarif_periode_success(self):
        """Test modification de période tarifaire"""
        self.login_as_titulaire()
        
        url = reverse('administration:modifier_tarif', kwargs={'pk': self.tarif1.pk})
        data = {
            'cout_xpf': 5500,
            'date_debut': str(self.today - timedelta(days=30)),
            'date_fin': str(self.today + timedelta(days=30))
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertTrue(json_response['success'])
        
        # Vérifier modification
        self.tarif1.refresh_from_db()
        self.assertEqual(self.tarif1.cout_xpf, Decimal('5500'))
    
    def test_supprimer_tarif_periode_success(self):
        """Test suppression de période tarifaire"""
        self.login_as_titulaire()
        
        url = reverse('administration:supprimer_tarif', kwargs={'pk': self.tarif1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertTrue(json_response['success'])
        
        # Vérifier suppression
        self.assertFalse(TarifPeriode.objects.filter(pk=self.tarif1.pk).exists())
    
    def test_tarif_periode_api_forbidden(self):
        """Test accès refusé aux API tarifs"""
        # Tester avec les bonnes méthodes HTTP
        
        # POST pour ajouter tarif
        url = reverse('administration:ajouter_tarif', kwargs={'pk': self.acte1.pk})
        response = self.client.post(url, {}, content_type='application/json')
        # Sans authentification, redirection vers login (302) ou 403
        self.assertIn(response.status_code, [302, 403])
        
        # POST pour modifier tarif
        url = reverse('administration:modifier_tarif', kwargs={'pk': self.tarif1.pk})
        response = self.client.post(url, {}, content_type='application/json')
        self.assertIn(response.status_code, [302, 403])
        
        # DELETE pour supprimer tarif
        url = reverse('administration:supprimer_tarif', kwargs={'pk': self.tarif1.pk})
        response = self.client.delete(url, content_type='application/json')
        self.assertIn(response.status_code, [302, 403])


class ActeFormsTests(ActeViewsBaseTest):
    """Tests pour les formulaires des actes"""
    
    def test_acte_form_clean_code_uppercase(self):
        """Test normalisation du code en majuscules"""
        from core.views.administration import ActeForm
        
        form = ActeForm(data={
            'code': 'test',  # Utiliser un code unique
            'libelle': 'Test'
        })
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['code'], 'TEST')
    
    def test_acte_form_clean_code_unique(self):
        """Test validation unicité du code"""
        from core.views.administration import ActeForm
        
        form = ActeForm(data={
            'code': 'CSF',  # Code déjà existant
            'libelle': 'Test'
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('code', form.errors)
    
    def test_tarif_periode_form_valid_data(self):
        """Test formulaire TarifPeriode avec données valides"""
        from core.views.administration import TarifPeriodeForm
        
        form = TarifPeriodeForm(data={
            'acte': self.acte2.pk,  # Utiliser un autre acte pour éviter les chevauchements
            'cout_xpf': 6000,
            'date_debut': self.today,
            'date_fin': self.today + timedelta(days=30)
        })
        
        self.assertTrue(form.is_valid())


class ActePermissionTests(ActeViewsBaseTest):
    """Tests des permissions pour les vues actes"""
    
    def test_superuser_access(self):
        """Test accès superutilisateur"""
        superuser = User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass'
        )
        
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('administration:administration_actes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
    
    def test_check_titulaire_permission_function(self):
        """Test de la fonction check_titulaire_permission"""
        from core.views.administration import check_titulaire_permission
        from django.test import RequestFactory
        
        factory = RequestFactory()
        
        # Test avec utilisateur anonyme
        from django.contrib.auth.models import AnonymousUser
        request = factory.get('/')
        request.user = AnonymousUser()
        self.assertFalse(check_titulaire_permission(request))
        
        # Test avec sage-femme titulaire
        request.user = self.user
        self.assertTrue(check_titulaire_permission(request))
        
        # Test avec superutilisateur
        superuser = User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass'
        )
        request.user = superuser
        self.assertTrue(check_titulaire_permission(request))