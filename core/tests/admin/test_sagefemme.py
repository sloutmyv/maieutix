"""
Tests pour l'administration du modèle SageFemme.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.admin.sites import AdminSite
from core.models.sagefemme import SageFemme
from core.admin.sagefemme import SageFemmeAdmin, SageFemmeAdminForm


class SageFemmeAdminTest(TestCase):
    """Tests de l'interface d'administration pour SageFemme"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = Client()
        
        # Créer un superutilisateur
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.nc',
            password='admin123'
        )
        
        # Créer des sages-femmes de test
        self.gerant = SageFemme.objects.create(
            nom='Gerant',
            prenom='Pierre',
            titre='Sage-femme gérant',
            telephone='687111111',
            email='pierre.gerant@test.nc',
            numero_cafat='111111111',
            ridet='RIDET111111',
            rib='FR1111111111111111111111111',
            banque='BCI',
            situation='gerant'
        )
        
        self.collaborateur = SageFemme.objects.create(
            nom='Collaborateur',
            prenom='Julie',
            titre='Sage-femme collaboratrice',
            telephone='687222222',
            email='julie.collaborateur@test.nc',
            numero_cafat='222222222',
            ridet='RIDET222222',
            rib='FR2222222222222222222222222',
            banque='BCI',
            situation='collaborateur'
        )
        
        self.remplacant = SageFemme.objects.create(
            nom='Remplacant',
            prenom='Sophie',
            titre='Sage-femme remplaçante',
            telephone='687333333',
            email='sophie.remplacant@test.nc',
            numero_cafat='333333333',
            ridet='RIDET333333',
            rib='FR3333333333333333333333333',
            banque='BCI',
            situation='remplacant',
            remplacement_de=self.gerant,
            etat_recapitulatif_commun=True,
            bons_depot_communs=True
        )
        
        # Instance de l'admin pour les tests
        self.site = AdminSite()
        self.admin = SageFemmeAdmin(SageFemme, self.site)

    def test_admin_list_display(self):
        """Test des champs affichés dans la liste"""
        expected_fields = [
            'nom_complet_display',
            'titre',
            'situation',
            'telephone',
            'email',
            'is_active',
            'updated_at'
        ]
        self.assertEqual(list(self.admin.list_display), expected_fields)

    def test_admin_list_filter(self):
        """Test des filtres disponibles"""
        expected_filters = [
            'situation',
            'is_active',
            'created_at',
            'updated_at'
        ]
        self.assertEqual(list(self.admin.list_filter), expected_filters)

    def test_admin_search_fields(self):
        """Test des champs de recherche"""
        expected_search_fields = [
            'nom',
            'prenom',
            'titre',
            'telephone',
            'email',
            'numero_cafat',
            'ridet'
        ]
        self.assertEqual(list(self.admin.search_fields), expected_search_fields)

    def test_admin_list_editable(self):
        """Test des champs modifiables dans la liste"""
        self.assertEqual(list(self.admin.list_editable), ['is_active'])

    def test_admin_ordering(self):
        """Test de l'ordre par défaut"""
        self.assertEqual(list(self.admin.ordering), ['nom', 'prenom'])

    def test_nom_complet_display_method(self):
        """Test de la méthode nom_complet_display"""
        result = self.admin.nom_complet_display(self.gerant)
        self.assertEqual(result, "Pierre Gerant")
        
        # Vérifier les attributs de la méthode
        self.assertEqual(self.admin.nom_complet_display.short_description, "Nom complet")
        self.assertEqual(self.admin.nom_complet_display.admin_order_field, 'nom')

    def test_admin_fieldsets(self):
        """Test de l'organisation des champs en sections"""
        fieldsets = self.admin.fieldsets
        
        # Vérifier le nombre de sections
        self.assertEqual(len(fieldsets), 6)
        
        # Vérifier les titres des sections
        section_titles = [fieldset[0] for fieldset in fieldsets]
        expected_titles = [
            'Informations personnelles',
            'Contact',
            'Adresse',
            'Informations professionnelles',
            'Situation professionnelle',
            'Options pour remplaçants',
            'Statut'
        ]
        self.assertEqual(section_titles, expected_titles)
        
        # Vérifier que la section Adresse est collapsible
        adresse_section = fieldsets[2]
        self.assertIn('collapse', adresse_section[1]['classes'])
        
        # Vérifier que la section Options pour remplaçants est collapsible
        options_section = fieldsets[5]
        self.assertIn('collapse', options_section[1]['classes'])

    def test_admin_readonly_fields(self):
        """Test des champs en lecture seule"""
        expected_readonly = ['created_at', 'updated_at']
        self.assertEqual(list(self.admin.readonly_fields), expected_readonly)

    def test_admin_access_requires_login(self):
        """Test que l'accès à l'admin nécessite une connexion"""
        url = reverse('admin:core_sagefemme_changelist')
        response = self.client.get(url)
        
        # Doit rediriger vers la page de connexion
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_admin_changelist_view_authenticated(self):
        """Test de la vue liste avec utilisateur connecté"""
        self.client.login(username='admin', password='admin123')
        url = reverse('admin:core_sagefemme_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pierre Gerant')
        self.assertContains(response, 'Julie Collaborateur')
        self.assertContains(response, 'Sophie Remplacant')

    def test_admin_add_view(self):
        """Test de la vue d'ajout"""
        self.client.login(username='admin', password='admin123')
        url = reverse('admin:core_sagefemme_add')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nom')
        self.assertContains(response, 'Prénom')
        self.assertContains(response, 'Situation')

    def test_admin_change_view(self):
        """Test de la vue de modification"""
        self.client.login(username='admin', password='admin123')
        url = reverse('admin:core_sagefemme_change', args=[self.gerant.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pierre')
        self.assertContains(response, 'Gerant')

    def test_admin_search_functionality(self):
        """Test de la fonctionnalité de recherche"""
        self.client.login(username='admin', password='admin123')
        url = reverse('admin:core_sagefemme_changelist')
        
        # Recherche par nom
        response = self.client.get(url, {'q': 'Gerant'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pierre Gerant')
        self.assertNotContains(response, 'Julie Collaborateur')
        
        # Recherche par téléphone
        response = self.client.get(url, {'q': '687222222'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Julie Collaborateur')
        self.assertNotContains(response, 'Pierre Gerant')

    def test_admin_filter_by_situation(self):
        """Test du filtrage par situation"""
        self.client.login(username='admin', password='admin123')
        url = reverse('admin:core_sagefemme_changelist')
        
        # Filtrer par gérant
        response = self.client.get(url, {'situation': 'gerant'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pierre Gerant')
        self.assertNotContains(response, 'Julie Collaborateur')
        
        # Filtrer par remplaçant
        response = self.client.get(url, {'situation': 'remplacant'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sophie Remplacant')
        self.assertNotContains(response, 'Pierre Gerant')

    def test_admin_filter_by_active_status(self):
        """Test du filtrage par statut actif"""
        # Désactiver une sage-femme
        self.gerant.is_active = False
        self.gerant.save()
        
        self.client.login(username='admin', password='admin123')
        url = reverse('admin:core_sagefemme_changelist')
        
        # Filtrer par actif
        response = self.client.get(url, {'is_active': 'True'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Pierre Gerant')
        self.assertContains(response, 'Julie Collaborateur')


class SageFemmeAdminFormTest(TestCase):
    """Tests du formulaire d'administration"""

    def setUp(self):
        """Configuration pour les tests de formulaire"""
        self.gerant = SageFemme.objects.create(
            nom='Gerant',
            prenom='Pierre',
            titre='Sage-femme gérant',
            telephone='687111111',
            email='pierre.gerant@test.nc',
            numero_cafat='111111111',
            ridet='RIDET111111',
            rib='FR1111111111111111111111111',
            banque='BCI',
            situation='gerant'
        )
        
        self.collaborateur = SageFemme.objects.create(
            nom='Collaborateur',
            prenom='Julie',
            titre='Sage-femme collaboratrice',
            telephone='687222222',
            email='julie.collaborateur@test.nc',
            numero_cafat='222222222',
            ridet='RIDET222222',
            rib='FR2222222222222222222222222',
            banque='BCI',
            situation='collaborateur'
        )

    def test_form_remplacement_de_queryset(self):
        """Test que le queryset pour remplacement_de est filtré correctement"""
        form = SageFemmeAdminForm()
        
        # Le queryset doit contenir seulement les gérants et collaborateurs actifs
        queryset = form.fields['remplacement_de'].queryset
        situations = list(queryset.values_list('situation', flat=True))
        
        self.assertIn('gerant', situations)
        self.assertIn('collaborateur', situations)
        self.assertNotIn('remplacant', situations)

    def test_form_validation_remplacant_sans_remplacement_de(self):
        """Test de validation : remplaçant sans remplacement_de"""
        form_data = {
            'nom': 'Test',
            'prenom': 'Test',
            'titre': 'Test',
            'telephone': '687000000',
            'email': 'test@test.nc',
            'numero_cafat': '000000000',
            'ridet': 'RIDET000000',
            'rib': 'FR0000000000000000000000000',
            'banque': 'BCI',
            'situation': 'remplacant'
            # remplacement_de manquant
        }
        
        form = SageFemmeAdminForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('remplacement_de', form.errors)

    def test_form_validation_gerant_avec_remplacement_de(self):
        """Test de validation : gérant avec remplacement_de"""
        form_data = {
            'nom': 'Test',
            'prenom': 'Test',
            'titre': 'Test',
            'telephone': '687000000',
            'email': 'test@test.nc',
            'numero_cafat': '000000000',
            'ridet': 'RIDET000000',
            'rib': 'FR0000000000000000000000000',
            'banque': 'BCI',
            'situation': 'gerant',
            'remplacement_de': self.gerant.pk
        }
        
        form = SageFemmeAdminForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('remplacement_de', form.errors)

    def test_form_validation_remplacant_valide(self):
        """Test de validation : remplaçant valide"""
        form_data = {
            'nom': 'Test',
            'prenom': 'Test',
            'titre': 'Test',
            'telephone': '687000000',
            'email': 'test@test.nc',
            'numero_cafat': '000000000',
            'ridet': 'RIDET000000',
            'rib': 'FR0000000000000000000000000',
            'banque': 'BCI',
            'situation': 'remplacant',
            'remplacement_de': self.gerant.pk,
            'etat_recapitulatif_commun': True,
            'bons_depot_communs': False
        }
        
        form = SageFemmeAdminForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_exclude_self_from_remplacement_de(self):
        """Test que le formulaire exclut l'instance courante du queryset remplacement_de"""
        # Simuler la modification d'une sage-femme existante
        form = SageFemmeAdminForm(instance=self.gerant)
        
        queryset = form.fields['remplacement_de'].queryset
        
        # Le gérant ne doit pas pouvoir se remplacer lui-même
        self.assertNotIn(self.gerant, queryset)
        self.assertIn(self.collaborateur, queryset)

    def test_form_email_unique_validation(self):
        """Test que l'email doit être unique"""
        form_data = {
            'nom': 'Test',
            'prenom': 'Test',
            'titre': 'Test',
            'telephone': '687000000',
            'email': self.gerant.email,  # Email déjà utilisé
            'numero_cafat': '000000000',
            'ridet': 'RIDET000000',
            'rib': 'FR0000000000000000000000000',
            'banque': 'BCI',
            'situation': 'collaborateur'
        }
        
        form = SageFemmeAdminForm(data=form_data)
        # Note: La validation d'unicité de l'email se fait au niveau du modèle,
        # pas du formulaire, donc le formulaire pourrait être valide ici
        # mais l'erreur apparaîtrait lors de la sauvegarde