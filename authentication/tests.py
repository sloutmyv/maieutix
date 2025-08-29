"""
Tests complets pour l'application authentication
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import date, timedelta

from authentication.models import SageFemmeUser
from core.models.sagefemme import SageFemme
from core.models.periode_activite import PeriodeActivite


class SageFemmeUserModelTest(TestCase):
    """Tests pour le modèle SageFemmeUser"""
    
    def setUp(self):
        """Configuration initiale des tests"""
        self.user_data = {
            'email': 'test@maieutix.nc',
            'password': 'testpass123'
        }
    
    def test_create_user(self):
        """Test création d'un utilisateur basique"""
        user = SageFemmeUser.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.must_change_password)
    
    def test_create_superuser(self):
        """Test création d'un superutilisateur"""
        user = SageFemmeUser.objects.create_superuser(**self.user_data)
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertFalse(user.must_change_password)
    
    def test_email_required(self):
        """Test que l'email est obligatoire"""
        with self.assertRaises(ValueError):
            SageFemmeUser.objects.create_user(email='', password='testpass123')
    
    def test_str_representation(self):
        """Test de la représentation string"""
        user = SageFemmeUser.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data['email'])
    
    def test_set_default_password(self):
        """Test définition du mot de passe par défaut"""
        user = SageFemmeUser.objects.create_user(**self.user_data)
        user.set_default_password()
        
        self.assertTrue(user.check_password('azerty'))
        self.assertTrue(user.must_change_password)
        self.assertIsNone(user.last_password_change)
    
    def test_prenom_property_with_sagefemme(self):
        """Test propriété prénom avec sage-femme associée"""
        user = SageFemmeUser.objects.create_user(**self.user_data)
        sagefemme = SageFemme.objects.create(
            nom='Dupont',
            prenom='Marie',
            titre='Sage-femme',
            telephone='123456789',
            email=self.user_data['email'],
            numero_cafat='12345',
            ridet='67890',
            rib='FR123456',
            banque='BNC',
            situation='titulaire',
            user=user
        )
        
        self.assertEqual(user.prenom, 'Marie')
    
    def test_prenom_property_without_sagefemme(self):
        """Test propriété prénom sans sage-femme associée"""
        user = SageFemmeUser.objects.create_user(**self.user_data)
        expected_prenom = self.user_data['email'].split('@')[0].capitalize()
        self.assertEqual(user.prenom, expected_prenom)
    
    def test_is_titulaire_property(self):
        """Test propriété is_titulaire"""
        user = SageFemmeUser.objects.create_user(**self.user_data)
        
        # Sans sage-femme
        self.assertFalse(user.is_titulaire)
        
        # Avec sage-femme titulaire
        SageFemme.objects.create(
            nom='Dupont',
            prenom='Marie',
            titre='Sage-femme',
            telephone='123456789',
            email=self.user_data['email'],
            numero_cafat='12345',
            ridet='67890',
            rib='FR123456',
            banque='BNC',
            situation='titulaire',
            user=user
        )
        self.assertTrue(user.is_titulaire)
    
    def test_can_access_administration_property(self):
        """Test propriété can_access_administration"""
        # Utilisateur normal
        user = SageFemmeUser.objects.create_user(**self.user_data)
        self.assertFalse(user.can_access_administration)
        
        # Superuser
        superuser = SageFemmeUser.objects.create_superuser(
            email='admin@maieutix.nc',
            password='adminpass123'
        )
        self.assertTrue(superuser.can_access_administration)
        
        # Sage-femme titulaire
        SageFemme.objects.create(
            nom='Dupont',
            prenom='Marie',
            titre='Sage-femme',
            telephone='123456789',
            email=self.user_data['email'],
            numero_cafat='12345',
            ridet='67890',
            rib='FR123456',
            banque='BNC',
            situation='titulaire',
            user=user
        )
        self.assertTrue(user.can_access_administration)
    
    def test_update_active_status_with_active_period(self):
        """Test mise à jour du statut actif avec période active"""
        user = SageFemmeUser.objects.create_user(**self.user_data)
        sagefemme = SageFemme.objects.create(
            nom='Dupont',
            prenom='Marie',
            titre='Sage-femme',
            telephone='123456789',
            email=self.user_data['email'],
            numero_cafat='12345',
            ridet='67890',
            rib='FR123456',
            banque='BNC',
            situation='collaborateur',
            user=user
        )
        
        # Créer une période active
        PeriodeActivite.objects.create(
            sage_femme=sagefemme,
            date_debut=date.today() - timedelta(days=30),
            commentaire="Période test"
        )
        
        user.update_active_status()
        self.assertTrue(user.is_active)
    
    def test_update_active_status_with_inactive_period(self):
        """Test mise à jour du statut actif avec période inactive"""
        user = SageFemmeUser.objects.create_user(**self.user_data)
        sagefemme = SageFemme.objects.create(
            nom='Dupont',
            prenom='Marie',
            titre='Sage-femme',
            telephone='123456789',
            email=self.user_data['email'],
            numero_cafat='12345',
            ridet='67890',
            rib='FR123456',
            banque='BNC',
            situation='collaborateur',
            user=user
        )
        
        # Créer une période terminée
        PeriodeActivite.objects.create(
            sage_femme=sagefemme,
            date_debut=date.today() - timedelta(days=60),
            date_fin=date.today() - timedelta(days=30),
            commentaire="Période terminée"
        )
        
        user.update_active_status()
        self.assertFalse(user.is_active)
    
    def test_superuser_always_active(self):
        """Test que les superusers restent toujours actifs"""
        superuser = SageFemmeUser.objects.create_superuser(
            email='admin@maieutix.nc',
            password='adminpass123'
        )
        
        superuser.update_active_status()
        self.assertTrue(superuser.is_active)


class AuthenticationViewsTest(TestCase):
    """Tests pour les vues d'authentification"""
    
    def setUp(self):
        """Configuration initiale des tests"""
        self.client = Client()
        self.login_url = reverse('auth:login')
        self.logout_url = reverse('auth:logout')
        self.change_password_url = reverse('auth:change_password')
        self.change_password_required_url = reverse('auth:change_password_required')
        
        # Utilisateur avec période active
        self.active_user = SageFemmeUser.objects.create_user(
            email='active@maieutix.nc',
            password='azerty'
        )
        self.active_sagefemme = SageFemme.objects.create(
            nom='Active',
            prenom='Marie',
            titre='Sage-femme',
            telephone='123456789',
            email='active@maieutix.nc',
            numero_cafat='12345',
            ridet='67890',
            rib='FR123456',
            banque='BNC',
            situation='titulaire',
            user=self.active_user
        )
        PeriodeActivite.objects.create(
            sage_femme=self.active_sagefemme,
            date_debut=date.today() - timedelta(days=30),
            commentaire="Période active"
        )
        self.active_user.update_active_status()
        self.active_user.save()
        
        # Utilisateur avec période inactive
        self.inactive_user = SageFemmeUser.objects.create_user(
            email='inactive@maieutix.nc',
            password='azerty'
        )
        self.inactive_sagefemme = SageFemme.objects.create(
            nom='Inactive',
            prenom='Julie',
            titre='Sage-femme',
            telephone='123456789',
            email='inactive@maieutix.nc',
            numero_cafat='54321',
            ridet='09876',
            rib='FR654321',
            banque='BNC',
            situation='collaborateur',
            user=self.inactive_user
        )
        PeriodeActivite.objects.create(
            sage_femme=self.inactive_sagefemme,
            date_debut=date.today() - timedelta(days=60),
            date_fin=date.today() - timedelta(days=30),
            commentaire="Période terminée"
        )
        self.inactive_user.update_active_status()
        self.inactive_user.save()
    
    def test_login_view_get(self):
        """Test affichage de la page de connexion"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Connexion Sages-Femmes')
        self.assertContains(response, 'form')
    
    def test_login_view_authenticated_redirect(self):
        """Test redirection si déjà connecté"""
        self.client.force_login(self.active_user)
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 302)
    
    def test_successful_login_active_user(self):
        """Test connexion réussie avec utilisateur actif"""
        response = self.client.post(self.login_url, {
            'email': 'active@maieutix.nc',
            'password': 'azerty'
        })
        
        # Doit rediriger vers changement de mot de passe (premier login)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.change_password_required_url)
    
    def test_failed_login_inactive_user(self):
        """Test échec de connexion avec utilisateur inactif"""
        # S'assurer que l'utilisateur existe et est inactif
        self.assertFalse(self.inactive_user.is_active)
        
        response = self.client.post(self.login_url, {
            'email': 'inactive@maieutix.nc',
            'password': 'azerty'
        })
        
        # La connexion échoue (pas de redirection)
        self.assertEqual(response.status_code, 200)
        
        # L'utilisateur n'est pas connecté
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_failed_login_wrong_credentials(self):
        """Test échec de connexion avec mauvais identifiants"""
        response = self.client.post(self.login_url, {
            'email': 'active@maieutix.nc',
            'password': 'wrongpass'
        })
        
        # La connexion échoue (pas de redirection)
        self.assertEqual(response.status_code, 200)
        
        # L'utilisateur n'est pas connecté
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_logout_view(self):
        """Test déconnexion"""
        self.client.force_login(self.active_user)
        response = self.client.get(self.logout_url)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
    
    def test_change_password_view_get(self):
        """Test affichage de la page de changement de mot de passe"""
        # S'assurer que l'utilisateur n'a pas besoin de changer obligatoirement son mot de passe
        self.active_user.must_change_password = False
        self.active_user.save()
        
        self.client.force_login(self.active_user)
        response = self.client.get(self.change_password_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Changer le mot de passe')
    
    def test_change_password_view_post_success(self):
        """Test changement de mot de passe réussi"""
        # S'assurer que l'utilisateur n'a pas besoin de changer obligatoirement son mot de passe
        self.active_user.must_change_password = False
        self.active_user.save()
        
        self.client.force_login(self.active_user)
        response = self.client.post(self.change_password_url, {
            'current_password': 'azerty',
            'new_password1': 'newpass123456',
            'new_password2': 'newpass123456'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que le mot de passe a changé
        self.active_user.refresh_from_db()
        self.assertTrue(self.active_user.check_password('newpass123456'))
        self.assertFalse(self.active_user.must_change_password)
    
    def test_change_password_required_view(self):
        """Test page de changement obligatoire"""
        self.client.force_login(self.active_user)
        response = self.client.get(self.change_password_required_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Changement de mot de passe obligatoire')
    
    def test_change_password_required_redirect_if_not_needed(self):
        """Test redirection si changement pas nécessaire"""
        self.active_user.must_change_password = False
        self.active_user.save()
        
        self.client.force_login(self.active_user)
        response = self.client.get(self.change_password_required_url)
        
        self.assertEqual(response.status_code, 302)


class AuthenticationIntegrationTest(TestCase):
    """Tests d'intégration pour l'authentification"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        
        # Créer un superuser
        self.superuser = SageFemmeUser.objects.create_superuser(
            email='admin@maieutix.com',
            password='admin123'
        )
        
        # Créer une sage-femme titulaire active
        self.titulaire_user = SageFemmeUser.objects.create_user(
            email='titulaire@maieutix.nc',
            password='azerty'
        )
        self.titulaire_sagefemme = SageFemme.objects.create(
            nom='Martin',
            prenom='Sophie',
            titre='Sage-femme',
            telephone='123456789',
            email='titulaire@maieutix.nc',
            numero_cafat='11111',
            ridet='22222',
            rib='FR111111',
            banque='BNC',
            situation='titulaire',
            user=self.titulaire_user
        )
        PeriodeActivite.objects.create(
            sage_femme=self.titulaire_sagefemme,
            date_debut=date.today() - timedelta(days=100),
            commentaire="Période titulaire"
        )
        self.titulaire_user.update_active_status()
        self.titulaire_user.save()
        
        # Créer une sage-femme collaboratrice inactive
        self.collaborateur_user = SageFemmeUser.objects.create_user(
            email='collaborateur@maieutix.nc',
            password='azerty'
        )
        self.collaborateur_sagefemme = SageFemme.objects.create(
            nom='Dubois',
            prenom='Marie',
            titre='Sage-femme',
            telephone='987654321',
            email='collaborateur@maieutix.nc',
            numero_cafat='33333',
            ridet='44444',
            rib='FR333333',
            banque='BNC',
            situation='collaborateur',
            user=self.collaborateur_user
        )
        PeriodeActivite.objects.create(
            sage_femme=self.collaborateur_sagefemme,
            date_debut=date.today() - timedelta(days=60),
            date_fin=date.today() - timedelta(days=10),
            commentaire="Période terminée"
        )
        self.collaborateur_user.update_active_status()
        self.collaborateur_user.save()
    
    def test_superuser_access_all(self):
        """Test que le superuser accède à tout"""
        self.client.force_login(self.superuser)
        
        # Accès à l'administration
        admin_url = reverse('administration:administration_sages_femmes')
        response = self.client.get(admin_url)
        self.assertEqual(response.status_code, 200)
        
        # Accès à Django admin
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
    
    def test_titulaire_access_administration_only(self):
        """Test qu'une titulaire accède seulement à l'administration"""
        self.titulaire_user.must_change_password = False
        self.titulaire_user.save()
        self.client.force_login(self.titulaire_user)
        
        # Accès à l'administration
        admin_url = reverse('administration:administration_sages_femmes')
        response = self.client.get(admin_url)
        self.assertEqual(response.status_code, 200)
        
        # Pas d'accès à Django admin
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirection login admin
    
    def test_collaborateur_inactive_no_access(self):
        """Test qu'une collaboratrice inactive n'accède à rien"""
        # Ne peut pas se connecter
        auth_result = authenticate(
            username='collaborateur@maieutix.nc',
            password='azerty'
        )
        self.assertIsNone(auth_result)
    
    def test_period_change_updates_access(self):
        """Test que les changements de périodes mettent à jour l'accès"""
        from django.utils import timezone
        
        # Initialement inactive
        self.assertFalse(self.collaborateur_user.is_active)
        
        # Ajouter une période active
        PeriodeActivite.objects.create(
            sage_femme=self.collaborateur_sagefemme,
            date_debut=timezone.now().date(),
            commentaire="Nouvelle période active"
        )
        
        # L'utilisateur devrait maintenant être actif
        self.collaborateur_user.refresh_from_db()
        self.assertTrue(self.collaborateur_user.is_active)
        
        # Peut maintenant s'authentifier
        auth_result = authenticate(
            username='collaborateur@maieutix.nc',
            password='azerty'
        )
        self.assertIsNotNone(auth_result)
    
    def test_full_login_flow(self):
        """Test complet du flux de connexion"""
        # 1. Première connexion avec mot de passe par défaut
        response = self.client.post(reverse('auth:login'), {
            'email': 'titulaire@maieutix.nc',
            'password': 'azerty'
        })
        
        # Redirection vers changement obligatoire
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('auth:change_password_required'))
        
        # 2. Changement du mot de passe
        response = self.client.post(reverse('auth:change_password_required'), {
            'current_password': 'azerty',
            'new_password1': 'newpass123456',
            'new_password2': 'newpass123456'
        })
        
        # Redirection vers home
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        
        # 3. Vérification que l'utilisateur est connecté et peut accéder à l'admin
        admin_url = reverse('administration:administration_sages_femmes')
        response = self.client.get(admin_url)
        self.assertEqual(response.status_code, 200)
        
        # 4. Déconnexion
        response = self.client.get(reverse('auth:logout'))
        self.assertEqual(response.status_code, 302)
        
        # 5. Reconnexion avec nouveau mot de passe
        response = self.client.post(reverse('auth:login'), {
            'email': 'titulaire@maieutix.nc',
            'password': 'newpass123456'
        })
        
        # Redirection directe vers home (pas de changement obligatoire)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))