"""
Tests pour l'administration des cadres d'exercice
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.urls import reverse
from datetime import timedelta

from core.models.cadre_exercice import CadreExercice
from core.admin.cadre_exercice import CadreExerciceAdmin

User = get_user_model()


class CadreExerciceAdminTests(TestCase):
    """Tests pour la classe CadreExerciceAdmin"""
    
    def setUp(self):
        """Configuration des données de test"""
        # Créer un superutilisateur
        self.superuser = User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass'
        )
        
        self.site = AdminSite()
        self.admin = CadreExerciceAdmin(CadreExercice, self.site)
        self.client = Client()
        
        # Créer un cadre d'exercice de test
        self.cadre_exercice = CadreExercice.objects.create(
            label='Suivi prénatal',
            description='Cadre d\'exercice pour le suivi de grossesse normale et pathologique'
        )
    
    def test_list_display_configuration(self):
        """Test de la configuration list_display"""
        expected_fields = [
            'label',
            'description',
            'created_at',
            'updated_at'
        ]
        
        self.assertEqual(self.admin.list_display, expected_fields)
    
    def test_list_filter_configuration(self):
        """Test de la configuration list_filter"""
        expected_filters = [
            'created_at',
            'updated_at'
        ]
        
        self.assertEqual(self.admin.list_filter, expected_filters)
    
    def test_search_fields_configuration(self):
        """Test de la configuration search_fields"""
        expected_fields = [
            'label',
            'description'
        ]
        
        self.assertEqual(self.admin.search_fields, expected_fields)
    
    def test_ordering_configuration(self):
        """Test de la configuration ordering"""
        expected_ordering = ['label']
        
        self.assertEqual(self.admin.ordering, expected_ordering)
    
    def test_fields_configuration(self):
        """Test de la configuration des fields"""
        expected_fields = ['label', 'description']
        
        self.assertEqual(self.admin.fields, expected_fields)
    
    def test_get_readonly_fields_new_object(self):
        """Test de get_readonly_fields pour un nouvel objet"""
        request = type('MockRequest', (), {})()  # Mock request
        readonly_fields = self.admin.get_readonly_fields(request, obj=None)
        
        self.assertEqual(readonly_fields, [])
    
    def test_get_readonly_fields_existing_object(self):
        """Test de get_readonly_fields pour un objet existant"""
        request = type('MockRequest', (), {})()  # Mock request
        readonly_fields = self.admin.get_readonly_fields(request, obj=self.cadre_exercice)
        
        expected = ['created_at', 'updated_at']
        self.assertEqual(readonly_fields, expected)


class CadreExerciceAdminIntegrationTests(TestCase):
    """Tests d'intégration pour l'admin des cadres d'exercice"""
    
    def setUp(self):
        """Configuration des données de test"""
        # Créer un superutilisateur
        self.superuser = User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass'
        )
        
        self.client = Client()
        
        # Créer des cadres d'exercice de test
        self.cadre1 = CadreExercice.objects.create(
            label='Suivi prénatal',
            description='Suivi de grossesse normale'
        )
        
        self.cadre2 = CadreExercice.objects.create(
            label='Accouchement',
            description='Accompagnement à l\'accouchement physiologique'
        )
        
        self.cadre3 = CadreExercice.objects.create(
            label='Post-partum',
            description='Suivi après accouchement et rééducation périnéale'
        )
    
    def test_admin_list_view(self):
        """Test de la vue liste de l'admin"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_cadreexercice_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que tous les cadres apparaissent
        self.assertContains(response, 'Suivi prénatal')
        self.assertContains(response, 'Accouchement')
        self.assertContains(response, 'Post-partum')
        
        # Vérifier l'ordre alphabétique
        content = response.content.decode()
        pos_accouchement = content.find('Accouchement')
        pos_postnatal = content.find('Post-partum')
        pos_prenatal = content.find('Suivi prénatal')
        
        self.assertLess(pos_accouchement, pos_postnatal)
        self.assertLess(pos_postnatal, pos_prenatal)
    
    def test_admin_add_view(self):
        """Test de la vue d'ajout de l'admin"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_cadreexercice_add')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les champs du formulaire
        self.assertContains(response, 'name="label"')
        self.assertContains(response, 'name="description"')
        
        # Vérifier que les timestamps ne sont pas dans le formulaire pour un nouvel objet
        self.assertNotContains(response, 'created_at')
        self.assertNotContains(response, 'updated_at')
    
    def test_admin_change_view(self):
        """Test de la vue de modification de l'admin"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_cadreexercice_change', args=[self.cadre1.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que les données sont pré-remplies
        self.assertContains(response, 'Suivi prénatal')
        self.assertContains(response, 'Suivi de grossesse normale')
        
        # Vérifier que le formulaire fonctionne correctement
        self.assertContains(response, 'Enregistrer')
    
    def test_admin_search_functionality(self):
        """Test de la fonctionnalité de recherche"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_cadreexercice_changelist')
        
        # Test recherche par label
        response = self.client.get(url, {'q': 'prénatal'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Suivi prénatal')
        self.assertNotContains(response, 'Accouchement')
        self.assertNotContains(response, 'Post-partum')
        
        # Test recherche par description
        response = self.client.get(url, {'q': 'physiologique'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Accouchement')
        self.assertNotContains(response, 'Suivi prénatal')
        self.assertNotContains(response, 'Post-partum')
        
        # Test recherche sans résultat
        response = self.client.get(url, {'q': 'inexistant'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Suivi prénatal')
        self.assertNotContains(response, 'Accouchement')
        self.assertNotContains(response, 'Post-partum')
    
    def test_admin_filter_functionality(self):
        """Test des filtres de l'admin"""
        self.client.login(email='admin@test.com', password='adminpass')
        url = reverse('admin:core_cadreexercice_changelist')
        
        # Test filtre par date de création (aujourd'hui)
        from datetime import date
        today = date.today()
        
        # Les cadres ont été créés aujourd'hui, donc devraient apparaître
        response = self.client.get(url, {
            'created_at__year': today.year,
            'created_at__month': today.month,
            'created_at__day': today.day
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Suivi prénatal')
        
        # Test filtre avec une date où aucun cadre n'a été créé
        yesterday = today - timedelta(days=1)
        response = self.client.get(url, {
            'created_at__year': yesterday.year,
            'created_at__month': yesterday.month,
            'created_at__day': yesterday.day
        })
        self.assertEqual(response.status_code, 200)
        # Ne devrait pas contenir nos cadres créés aujourd'hui
        self.assertNotContains(response, 'Suivi prénatal')
    
    def test_admin_create_cadre_exercice(self):
        """Test de création d'un cadre d'exercice via l'admin"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_cadreexercice_add')
        data = {
            'label': 'Nouveau cadre admin',
            'description': 'Description créée via admin'
        }
        
        response = self.client.post(url, data)
        
        # Devrait rediriger après création réussie
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que le cadre a été créé
        self.assertTrue(
            CadreExercice.objects.filter(label='Nouveau cadre admin').exists()
        )
        
        # Vérifier les données
        cadre = CadreExercice.objects.get(label='Nouveau cadre admin')
        self.assertEqual(cadre.description, 'Description créée via admin')
    
    def test_admin_update_cadre_exercice(self):
        """Test de modification d'un cadre d'exercice via l'admin"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_cadreexercice_change', args=[self.cadre1.pk])
        data = {
            'label': 'Suivi prénatal modifié',
            'description': 'Description modifiée via admin'
        }
        
        response = self.client.post(url, data)
        
        # Devrait rediriger après modification réussie
        self.assertEqual(response.status_code, 302)
        
        # Vérifier les modifications
        self.cadre1.refresh_from_db()
        self.assertEqual(self.cadre1.label, 'Suivi prénatal modifié')
        self.assertEqual(self.cadre1.description, 'Description modifiée via admin')
    
    def test_admin_delete_cadre_exercice(self):
        """Test de suppression d'un cadre d'exercice via l'admin"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        # Page de confirmation de suppression
        url = reverse('admin:core_cadreexercice_delete', args=[self.cadre1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Confirmation de suppression
        response = self.client.post(url, {'post': 'yes'})
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que le cadre a été supprimé
        self.assertFalse(
            CadreExercice.objects.filter(pk=self.cadre1.pk).exists()
        )
    
    def test_admin_bulk_actions(self):
        """Test des actions en lot"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_cadreexercice_changelist')
        data = {
            'action': 'delete_selected',
            '_selected_action': [self.cadre1.pk, self.cadre2.pk],
            'post': 'yes',  # Confirmation
        }
        
        response = self.client.post(url, data)
        
        # Devrait rediriger après suppression
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que les cadres ont été supprimés
        self.assertFalse(CadreExercice.objects.filter(pk=self.cadre1.pk).exists())
        self.assertFalse(CadreExercice.objects.filter(pk=self.cadre2.pk).exists())
        
        # Le troisième cadre devrait toujours exister
        self.assertTrue(CadreExercice.objects.filter(pk=self.cadre3.pk).exists())


class CadreExerciceAdminValidationTests(TestCase):
    """Tests de validation dans l'admin des cadres d'exercice"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.superuser = User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass'
        )
        
        self.client = Client()
    
    def test_admin_create_empty_label(self):
        """Test de création avec label vide"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_cadreexercice_add')
        data = {
            'label': '',  # Label vide
            'description': 'Description test'
        }
        
        response = self.client.post(url, data)
        
        # Ne devrait pas rediriger (erreur de validation)
        self.assertEqual(response.status_code, 200)
        
        # Devrait contenir un message d'erreur
        self.assertContains(response, 'Ce champ est obligatoire')
        
        # Ne devrait pas créer le cadre
        self.assertFalse(CadreExercice.objects.filter(description='Description test').exists())
    
    def test_admin_create_empty_description(self):
        """Test de création avec description vide"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_cadreexercice_add')
        data = {
            'label': 'Label test',
            'description': ''  # Description vide
        }
        
        response = self.client.post(url, data)
        
        # Ne devrait pas rediriger (erreur de validation)
        self.assertEqual(response.status_code, 200)
        
        # Devrait contenir un message d'erreur
        self.assertContains(response, 'Ce champ est obligatoire')
        
        # Ne devrait pas créer le cadre
        self.assertFalse(CadreExercice.objects.filter(label='Label test').exists())
    
    def test_admin_create_long_label(self):
        """Test de création avec label très long"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_cadreexercice_add')
        data = {
            'label': 'A' * 201,  # Dépasse la limite de 200 caractères
            'description': 'Description test'
        }
        
        response = self.client.post(url, data)
        
        # Ne devrait pas rediriger (erreur de validation)
        self.assertEqual(response.status_code, 200)
        
        # Devrait contenir un message d'erreur sur la longueur
        content = response.content.decode()
        self.assertTrue('200 caractères' in content or 'maximum' in content.lower() or 'plus' in content.lower())
        
        # Ne devrait pas créer le cadre
        self.assertFalse(CadreExercice.objects.filter(description='Description test').exists())
    
    def test_admin_create_valid_long_description(self):
        """Test de création avec description très longue (devrait fonctionner)"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_cadreexercice_add')
        long_description = 'Description très longue ' * 100  # Texte très long
        data = {
            'label': 'Cadre description longue',
            'description': long_description
        }
        
        response = self.client.post(url, data)
        
        # Devrait rediriger (création réussie)
        self.assertEqual(response.status_code, 302)
        
        # Devrait créer le cadre
        self.assertTrue(CadreExercice.objects.filter(label='Cadre description longue').exists())
        
        # Vérifier que la description a été sauvée (longueur similaire)
        cadre = CadreExercice.objects.get(label='Cadre description longue')
        self.assertGreater(len(cadre.description), 1000)  # Assez long


class CadreExerciceAdminPermissionsTests(TestCase):
    """Tests des permissions pour l'admin des cadres d'exercice"""
    
    def setUp(self):
        """Configuration des données de test"""
        # Créer un utilisateur normal (non-superuser)
        self.normal_user = User.objects.create_user(
            email='user@test.com',
            password='userpass'
        )
        
        # Créer un superutilisateur
        self.superuser = User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass'
        )
        
        self.client = Client()
    
    def test_admin_access_normal_user(self):
        """Test d'accès à l'admin avec utilisateur normal"""
        self.client.login(email='user@test.com', password='userpass')
        
        url = reverse('admin:core_cadreexercice_changelist')
        response = self.client.get(url)
        
        # Devrait rediriger vers la page de login ou être interdit
        self.assertIn(response.status_code, [302, 403])
    
    def test_admin_access_superuser(self):
        """Test d'accès à l'admin avec superutilisateur"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_cadreexercice_changelist')
        response = self.client.get(url)
        
        # Devrait fonctionner
        self.assertEqual(response.status_code, 200)
    
    def test_admin_access_anonymous(self):
        """Test d'accès à l'admin sans authentification"""
        url = reverse('admin:core_cadreexercice_changelist')
        response = self.client.get(url)
        
        # Devrait rediriger vers la page de login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)


class CadreExerciceAdminDisplayTests(TestCase):
    """Tests de l'affichage dans l'admin des cadres d'exercice"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.superuser = User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass'
        )
        
        self.client = Client()
        
        # Créer des cadres avec différentes caractéristiques
        self.cadre_normal = CadreExercice.objects.create(
            label='Cadre normal',
            description='Description de longueur normale'
        )
        
        self.cadre_long_label = CadreExercice.objects.create(
            label='Cadre avec un label particulièrement long qui dépasse la normale',
            description='Description courte'
        )
        
        self.cadre_long_description = CadreExercice.objects.create(
            label='Cadre description longue',
            description='Description extrêmement longue qui contient beaucoup de détails ' * 20
        )
        
        self.cadre_caracteres_speciaux = CadreExercice.objects.create(
            label='Cadre éàçèê & spéciaux',
            description='Description avec "guillemets", \'apostrophes\' et <balises>'
        )
    
    def test_admin_list_display_truncation(self):
        """Test de l'affichage et de la troncature dans la liste"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_cadreexercice_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode()
        
        # Tous les cadres devraient apparaître
        self.assertContains(response, 'Cadre normal')
        self.assertContains(response, 'Cadre avec un label')
        self.assertContains(response, 'Cadre description longue')
        self.assertContains(response, 'Cadre éàçèê')
        
        # Vérifier la gestion des caractères spéciaux
        self.assertIn('&amp;', content)  # & échappé
        self.assertNotIn('<balises>', content)  # Balises échappées
    
    def test_admin_change_form_display(self):
        """Test de l'affichage du formulaire de modification"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_cadreexercice_change', args=[self.cadre_long_description.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # La description complète devrait être visible dans le textarea
        self.assertContains(response, 'Description extrêmement longue')
        self.assertContains(response, 'beaucoup de détails')
    
    def test_admin_verbose_names(self):
        """Test de l'affichage des verbose names"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_cadreexercice_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les noms verbose du modèle
        self.assertContains(response, "4.1 Cadres d&#x27;exercice")  # Titre de la page (HTML escaped)
        
        url = reverse('admin:core_cadreexercice_add')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les labels des champs
        self.assertContains(response, 'Label')
        self.assertContains(response, 'Description')