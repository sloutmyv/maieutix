"""
Tests pour les conditions de visibilité et permissions selon les profils utilisateurs
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta

from authentication.models import SageFemmeUser
from core.models.sagefemme import SageFemme
from core.models.periode_activite import PeriodeActivite


class NavbarVisibilityTest(TestCase):
    """Tests pour la visibilité des éléments de la navbar selon les profils"""
    
    def setUp(self):
        """Configuration initiale des tests"""
        self.client = Client()
        
        # Créer un superuser
        self.superuser = SageFemmeUser.objects.create_superuser(
            email='admin@maieutix.com',
            password='admin123'
        )
        
        # Créer une sage-femme titulaire active
        self.titulaire_user = SageFemmeUser.objects.create_user(
            email='titulaire@maieutix.nc',
            password='testpass123'
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
        self.titulaire_user.must_change_password = False
        self.titulaire_user.save()
        
        # Créer une sage-femme collaboratrice active
        self.collaborateur_user = SageFemmeUser.objects.create_user(
            email='collaborateur@maieutix.nc',
            password='testpass123'
        )
        self.collaborateur_sagefemme = SageFemme.objects.create(
            nom='Durand',
            prenom='Claire',
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
            date_debut=date.today() - timedelta(days=30),
            commentaire="Période collaborateur"
        )
        self.collaborateur_user.update_active_status()
        self.collaborateur_user.must_change_password = False
        self.collaborateur_user.save()
        
        # Créer une sage-femme remplaçante active
        self.remplacant_user = SageFemmeUser.objects.create_user(
            email='remplacant@maieutix.nc',
            password='testpass123'
        )
        self.remplacant_sagefemme = SageFemme.objects.create(
            nom='Leroy',
            prenom='Marie',
            titre='Sage-femme',
            telephone='555666777',
            email='remplacant@maieutix.nc',
            numero_cafat='55555',
            ridet='66666',
            rib='FR555555',
            banque='BNC',
            situation='remplacant',
            remplacement_de=self.titulaire_sagefemme,
            user=self.remplacant_user
        )
        PeriodeActivite.objects.create(
            sage_femme=self.remplacant_sagefemme,
            date_debut=date.today() - timedelta(days=15),
            commentaire="Période remplacement"
        )
        self.remplacant_user.update_active_status()
        self.remplacant_user.must_change_password = False
        self.remplacant_user.save()
    
    def test_superuser_navbar_visibility(self):
        """Test visibilité navbar pour superuser"""
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('home'))
        
        # Doit voir le menu Administration
        self.assertContains(response, 'Administration')
        self.assertContains(response, 'Sages Femmes')
        self.assertContains(response, 'Admin Django')
        
        # Doit voir son prénom (Admin par défaut car pas de sage-femme associée)
        self.assertContains(response, 'Admin')  # Prénom par défaut depuis email
        
        # Doit voir le menu utilisateur
        self.assertContains(response, 'Changer le mot de passe')
        self.assertContains(response, 'Se déconnecter')
    
    def test_titulaire_navbar_visibility(self):
        """Test visibilité navbar pour sage-femme titulaire"""
        self.client.force_login(self.titulaire_user)
        response = self.client.get(reverse('home'))
        
        # Doit voir le menu Administration
        self.assertContains(response, 'Administration')
        self.assertContains(response, 'Sages Femmes')
        
        # Ne doit PAS voir Admin Django
        self.assertNotContains(response, 'Admin Django')
        
        # Doit voir son prénom
        self.assertContains(response, 'Sophie')
        
        # Doit voir les menus de navigation principaux
        self.assertContains(response, 'Feuille de Soins')
        self.assertContains(response, 'Patients')
        self.assertContains(response, 'Outils')
        self.assertContains(response, 'Statistiques')
    
    def test_collaborateur_navbar_visibility(self):
        """Test visibilité navbar pour sage-femme collaboratrice"""
        self.client.force_login(self.collaborateur_user)
        response = self.client.get(reverse('home'))
        
        # DOIT voir les liens du menu Administration (lecture seule)
        self.assertContains(response, 'Sages Femmes</a>')
        # Ne doit PAS voir Admin Django (réservé aux superusers)
        self.assertNotContains(response, 'Admin Django</a>')
        
        # Doit voir son prénom
        self.assertContains(response, 'Claire')
        
        # Doit voir les menus de navigation principaux
        self.assertContains(response, 'Feuille de Soins')
        self.assertContains(response, 'Patients')
        self.assertContains(response, 'Outils')
        self.assertContains(response, 'Statistiques')
    
    def test_remplacant_navbar_visibility(self):
        """Test visibilité navbar pour sage-femme remplaçante"""
        self.client.force_login(self.remplacant_user)
        response = self.client.get(reverse('home'))
        
        # DOIT voir les liens du menu Administration (lecture seule)
        self.assertContains(response, 'Sages Femmes</a>')
        # Ne doit PAS voir Admin Django (réservé aux superusers)
        self.assertNotContains(response, 'Admin Django</a>')
        
        # Doit voir son prénom
        self.assertContains(response, 'Marie')
        
        # Doit voir les menus de navigation principaux
        self.assertContains(response, 'Feuille de Soins')
        self.assertContains(response, 'Patients')
        self.assertContains(response, 'Outils')
        self.assertContains(response, 'Statistiques')


class AdministrationAccessTest(TestCase):
    """Tests pour l'accès aux fonctions d'administration selon les profils"""
    
    def setUp(self):
        """Configuration initiale des tests"""
        self.client = Client()
        
        # Créer un superuser
        self.superuser = SageFemmeUser.objects.create_superuser(
            email='admin@maieutix.com',
            password='admin123'
        )
        
        # Créer une sage-femme titulaire active
        self.titulaire_user = SageFemmeUser.objects.create_user(
            email='titulaire@maieutix.nc',
            password='testpass123'
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
        self.titulaire_user.must_change_password = False
        self.titulaire_user.save()
        
        # Créer une sage-femme collaboratrice active
        self.collaborateur_user = SageFemmeUser.objects.create_user(
            email='collaborateur@maieutix.nc',
            password='testpass123'
        )
        self.collaborateur_sagefemme = SageFemme.objects.create(
            nom='Durand',
            prenom='Claire',
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
            date_debut=date.today() - timedelta(days=30),
            commentaire="Période collaborateur"
        )
        self.collaborateur_user.update_active_status()
        self.collaborateur_user.must_change_password = False
        self.collaborateur_user.save()
        
        self.admin_url = reverse('administration:administration_sages_femmes')
    
    def test_superuser_administration_access(self):
        """Test accès administration pour superuser"""
        self.client.force_login(self.superuser)
        
        # Accès à la page principale d'administration
        response = self.client.get(self.admin_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Administration - Sages Femmes')
        
        # Accès à Django admin
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
    
    def test_titulaire_administration_access(self):
        """Test accès administration pour sage-femme titulaire"""
        self.client.force_login(self.titulaire_user)
        
        # Accès à la page principale d'administration
        response = self.client.get(self.admin_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Administration - Sages Femmes')
        
        # Pas d'accès à Django admin
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirection vers login admin
    
    def test_collaborateur_administration_read_only(self):
        """Test accès en lecture seule à l'administration pour sage-femme collaboratrice"""
        self.client.force_login(self.collaborateur_user)
        
        # DOIT avoir accès à la page d'administration (lecture seule)
        response = self.client.get(self.admin_url)
        self.assertEqual(response.status_code, 200)  # Accès autorisé
        
        # Pas d'accès à Django admin
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirection vers login admin
    
    def test_anonymous_user_denied(self):
        """Test refus d'accès pour utilisateur non connecté"""
        # Pas d'accès à l'administration
        response = self.client.get(self.admin_url)
        self.assertEqual(response.status_code, 302)  # Redirection vers login
        
        # Pas d'accès à Django admin
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirection vers login admin


class PeriodBasedAccessTest(TestCase):
    """Tests pour l'accès basé sur les périodes d'activité"""
    
    def setUp(self):
        """Configuration initiale des tests"""
        self.client = Client()
        
        # Créer une sage-femme avec période terminée
        self.inactive_user = SageFemmeUser.objects.create_user(
            email='inactive@maieutix.nc',
            password='testpass123'
        )
        self.inactive_sagefemme = SageFemme.objects.create(
            nom='Inactive',
            prenom='Julie',
            titre='Sage-femme',
            telephone='123456789',
            email='inactive@maieutix.nc',
            numero_cafat='77777',
            ridet='88888',
            rib='FR777777',
            banque='BNC',
            situation='collaborateur',
            user=self.inactive_user
        )
        PeriodeActivite.objects.create(
            sage_femme=self.inactive_sagefemme,
            date_debut=date.today() - timedelta(days=60),
            date_fin=date.today() - timedelta(days=10),
            commentaire="Période terminée"
        )
        self.inactive_user.update_active_status()
        self.inactive_user.save()
        
        # Créer une sage-femme avec période future
        self.future_user = SageFemmeUser.objects.create_user(
            email='future@maieutix.nc',
            password='testpass123'
        )
        self.future_sagefemme = SageFemme.objects.create(
            nom='Future',
            prenom='Anne',
            titre='Sage-femme',
            telephone='123456789',
            email='future@maieutix.nc',
            numero_cafat='99999',
            ridet='00000',
            rib='FR999999',
            banque='BNC',
            situation='collaborateur',
            user=self.future_user
        )
        PeriodeActivite.objects.create(
            sage_femme=self.future_sagefemme,
            date_debut=date.today() + timedelta(days=10),
            commentaire="Période future"
        )
        self.future_user.update_active_status()
        self.future_user.save()
    
    def test_inactive_user_cannot_login(self):
        """Test qu'un utilisateur avec période terminée ne peut pas se connecter"""
        # Vérifier que l'utilisateur est inactif
        self.assertFalse(self.inactive_user.is_active)
        
        response = self.client.post(reverse('auth:login'), {
            'email': 'inactive@maieutix.nc',
            'password': 'testpass123'
        })
        
        # Connexion échouée (pas de redirection)
        self.assertEqual(response.status_code, 200)
        
        # L'utilisateur n'est pas connecté
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_future_user_cannot_login(self):
        """Test qu'un utilisateur avec période future ne peut pas se connecter"""
        # Vérifier que l'utilisateur est inactif
        self.assertFalse(self.future_user.is_active)
        
        response = self.client.post(reverse('auth:login'), {
            'email': 'future@maieutix.nc',
            'password': 'testpass123'
        })
        
        # Connexion échouée (pas de redirection)
        self.assertEqual(response.status_code, 200)
        
        # L'utilisateur n'est pas connecté
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_period_activation_enables_login(self):
        """Test qu'ajouter une période active permet la connexion"""
        # Ajouter une période active à l'utilisateur inactif
        PeriodeActivite.objects.create(
            sage_femme=self.inactive_sagefemme,
            date_debut=timezone.now().date(),
            commentaire="Nouvelle période active"
        )
        
        # L'utilisateur devrait maintenant être actif
        self.inactive_user.refresh_from_db()
        self.assertTrue(self.inactive_user.is_active)
        
        # Connexion devrait maintenant réussir
        response = self.client.post(reverse('auth:login'), {
            'email': 'inactive@maieutix.nc',
            'password': 'testpass123'
        })
        
        # Redirection (connexion réussie)
        self.assertEqual(response.status_code, 302)


class ProfileSpecificFunctionalityTest(TestCase):
    """Tests pour les fonctionnalités spécifiques selon les profils"""
    
    def setUp(self):
        """Configuration initiale des tests"""
        self.client = Client()
        
        # Créer différents profils d'utilisateurs
        self.superuser = SageFemmeUser.objects.create_superuser(
            email='admin@maieutix.com',
            password='admin123'
        )
        
        self.titulaire_user = SageFemmeUser.objects.create_user(
            email='titulaire@maieutix.nc',
            password='testpass123'
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
        self.titulaire_user.must_change_password = False
        self.titulaire_user.save()
        
        self.collaborateur_user = SageFemmeUser.objects.create_user(
            email='collaborateur@maieutix.nc',
            password='testpass123'
        )
        self.collaborateur_sagefemme = SageFemme.objects.create(
            nom='Durand',
            prenom='Claire',
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
            date_debut=date.today() - timedelta(days=30),
            commentaire="Période collaborateur"
        )
        self.collaborateur_user.update_active_status()
        self.collaborateur_user.must_change_password = False
        self.collaborateur_user.save()
    
    def test_titulaire_can_manage_sages_femmes(self):
        """Test qu'une titulaire peut gérer les sages-femmes"""
        self.client.force_login(self.titulaire_user)
        
        # Peut accéder à la liste des sages-femmes
        response = self.client.get(reverse('administration:administration_sages_femmes'))
        self.assertEqual(response.status_code, 200)
        
        # La page contient le titre d'administration
        self.assertContains(response, 'Administration - Sages Femmes')
    
    def test_collaborateur_can_view_sages_femmes_read_only(self):
        """Test qu'une collaboratrice peut voir les sages-femmes en lecture seule"""
        self.client.force_login(self.collaborateur_user)
        
        # PEUT accéder à la gestion des sages-femmes (lecture seule)
        response = self.client.get(reverse('administration:administration_sages_femmes'))
        self.assertEqual(response.status_code, 200)  # Accès autorisé
    
    def test_prenom_display_in_navbar(self):
        """Test affichage du prénom dans la navbar selon les profils"""
        # Test avec titulaire
        self.client.force_login(self.titulaire_user)
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Sophie')  # Prénom de la sage-femme
        
        # Test avec collaboratrice
        self.client.force_login(self.collaborateur_user)
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Claire')  # Prénom de la sage-femme
        
        # Test avec superuser (pas de sage-femme associée)
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Admin')  # Prénom dérivé de l'email
    
    def test_user_properties_consistency(self):
        """Test cohérence des propriétés utilisateur"""
        # Vérifier les propriétés pour différents types d'utilisateurs
        
        # Superuser
        self.assertTrue(self.superuser.is_superuser)
        self.assertTrue(self.superuser.can_access_administration)
        self.assertFalse(self.superuser.is_titulaire)
        
        # Titulaire
        self.assertFalse(self.titulaire_user.is_superuser)
        self.assertTrue(self.titulaire_user.can_access_administration)
        self.assertTrue(self.titulaire_user.is_titulaire)
        
        # Collaborateur
        self.assertFalse(self.collaborateur_user.is_superuser)
        self.assertTrue(self.collaborateur_user.can_access_administration)  # Maintenant accessible en lecture
        self.assertFalse(self.collaborateur_user.can_edit_administration)  # Mais pas en écriture
        self.assertFalse(self.collaborateur_user.is_titulaire)