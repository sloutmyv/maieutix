"""
Tests pour l'administration des prestations
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.urls import reverse
from decimal import Decimal
from datetime import date, timedelta

from core.models.prestation import Prestation
from core.models.cadre_exercice import CadreExercice
from core.models.acte import Acte, TarifPeriode
from core.admin.prestation import PrestationAdmin

User = get_user_model()


class PrestationAdminTests(TestCase):
    """Tests pour la classe PrestationAdmin"""
    
    def setUp(self):
        """Configuration des données de test"""
        # Créer un superutilisateur
        self.superuser = User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass'
        )
        
        self.site = AdminSite()
        self.admin = PrestationAdmin(Prestation, self.site)
        self.client = Client()
        
        self.today = date.today()
        
        # Créer un cadre d'exercice
        self.cadre_exercice = CadreExercice.objects.create(
            label='Suivi prénatal',
            description='Cadre d\'exercice pour le suivi de grossesse'
        )
        
        # Créer un acte
        self.acte = Acte.objects.create(
            code='CSF',
            libelle='Consultation Sage-Femme'
        )
        
        # Créer un tarif
        self.tarif = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=Decimal('5000'),
            date_debut=self.today - timedelta(days=30)
        )
        
        # Créer une prestation de test
        self.prestation = Prestation.objects.create(
            cadre_exercice=self.cadre_exercice,
            designation='Consultation prénatale standard',
            limite='Maximum 7 consultations par grossesse',
            acte=self.acte,
            cotation=Decimal('1.5'),
            entente_prealable='Non nécessaire',
            assurance_maladie='Prise en charge à 70%',
            assurance_maternite_normale='Prise en charge à 100%',
            assurance_maternite_pathologie='Prise en charge majorée',
            observation='Consultation de routine',
            suffixe='TEST',
            origine='MT',
            actif=True,
            prescription=False
        )
    
    def test_list_display_configuration(self):
        """Test de la configuration list_display"""
        expected_fields = [
            'cadre_exercice',
            'designation_short',
            'suffixe',
            'origine',
            'cotation',
            'acte_code',
            'actif',
            'prescription',
            'tarif_display_admin',
            'created_at'
        ]
        
        self.assertEqual(self.admin.list_display, expected_fields)
    
    def test_list_filter_configuration(self):
        """Test de la configuration list_filter"""
        expected_filters = [
            'cadre_exercice',
            'origine',
            'actif',
            'prescription',
            'cotation',
            'created_at',
            'updated_at'
        ]
        
        self.assertEqual(self.admin.list_filter, expected_filters)
    
    def test_search_fields_configuration(self):
        """Test de la configuration search_fields"""
        expected_fields = [
            'designation',
            'suffixe',
            'limite',
            'entente_prealable',
            'observation',
            'cadre_exercice__label'
        ]
        
        self.assertEqual(self.admin.search_fields, expected_fields)
    
    def test_ordering_configuration(self):
        """Test de la configuration ordering"""
        expected_ordering = ['cadre_exercice__label', 'designation']
        
        self.assertEqual(self.admin.ordering, expected_ordering)
    
    def test_fieldsets_configuration(self):
        """Test de la configuration des fieldsets"""
        expected_fieldsets = (
            ('Informations principales', {
                'fields': ('cadre_exercice', 'designation', 'limite', 'cotation')
            }),
            ('Acte associé', {
                'fields': ('acte', 'suffixe', 'origine', 'prescription')
            }),
            ('Configuration', {
                'fields': ('actif',)
            }),
            ('Entente et assurances', {
                'fields': (
                    'entente_prealable',
                    'assurance_maladie',
                    'assurance_maternite_normale',
                    'assurance_maternite_pathologie'
                )
            }),
            ('Observations', {
                'fields': ('observation',),
                'classes': ('collapse',)
            }),
        )
        
        self.assertEqual(self.admin.fieldsets, expected_fieldsets)
    
    def test_designation_short_method(self):
        """Test de la méthode designation_short"""
        # Test avec désignation normale
        result = self.admin.designation_short(self.prestation)
        expected = 'Consultation prénatale standard'
        self.assertEqual(result, expected)
        
        # Test avec désignation longue
        long_prestation = Prestation.objects.create(
            cadre_exercice=self.cadre_exercice,
            designation='A' * 80,  # 80 caractères
            acte=self.acte,
            cotation=Decimal('1.0'),
            entente_prealable='Test'
        )
        
        result = self.admin.designation_short(long_prestation)
        expected = 'A' * 60 + '...'  # Tronqué à 60 caractères + ...
        self.assertEqual(result, expected)
        self.assertEqual(len(result), 63)  # 60 + 3 pour '...'
    
    def test_acte_code_method(self):
        """Test de la méthode acte_code"""
        result = self.admin.acte_code(self.prestation)
        expected = 'CSF'
        self.assertEqual(result, expected)
        
        # Test avec prestation sans acte (ne devrait pas arriver en pratique)
        prestation_no_acte = Prestation(
            cadre_exercice=self.cadre_exercice,
            designation='Test',
            cotation=Decimal('1.0'),
            entente_prealable='Test'
        )
        prestation_no_acte.acte = None
        
        result = self.admin.acte_code(prestation_no_acte)
        expected = 'Aucun'
        self.assertEqual(result, expected)
    
    def test_tarif_display_admin_method(self):
        """Test de la méthode tarif_display_admin"""
        result = self.admin.tarif_display_admin(self.prestation)
        expected = '7500 XPF'  # 1.5 × 5000
        self.assertEqual(result, expected)
        
        # Test avec prestation sans tarif calculable
        prestation_no_tarif = Prestation.objects.create(
            cadre_exercice=self.cadre_exercice,
            designation='Test sans tarif',
            acte=self.acte,
            cotation=Decimal('1.0'),
            entente_prealable='Test'
        )
        
        # Supprimer les tarifs
        TarifPeriode.objects.all().delete()
        
        result = self.admin.tarif_display_admin(prestation_no_tarif)
        expected = 'Non calculable'
        self.assertEqual(result, expected)
    
    def test_get_readonly_fields_new_object(self):
        """Test de get_readonly_fields pour un nouvel objet"""
        request = type('MockRequest', (), {})()  # Mock request
        readonly_fields = self.admin.get_readonly_fields(request, obj=None)
        
        self.assertEqual(readonly_fields, [])
    
    def test_get_readonly_fields_existing_object(self):
        """Test de get_readonly_fields pour un objet existant"""
        request = type('MockRequest', (), {})()  # Mock request
        readonly_fields = self.admin.get_readonly_fields(request, obj=self.prestation)
        
        expected = ['created_at', 'updated_at']
        self.assertEqual(readonly_fields, expected)
    
    def test_get_queryset_optimization(self):
        """Test de l'optimisation du queryset"""
        request = type('MockRequest', (), {})()  # Mock request
        queryset = self.admin.get_queryset(request)
        
        # Vérifier que select_related est appliqué
        self.assertIn('cadre_exercice', queryset.query.select_related)
        self.assertIn('acte', queryset.query.select_related)


class PrestationAdminIntegrationTests(TestCase):
    """Tests d'intégration pour l'admin des prestations"""
    
    def setUp(self):
        """Configuration des données de test"""
        # Créer un superutilisateur
        self.superuser = User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass'
        )
        
        self.client = Client()
        self.today = date.today()
        
        # Créer des données de test
        self.cadre_exercice = CadreExercice.objects.create(
            label='Test Cadre',
            description='Description test'
        )
        
        self.acte = Acte.objects.create(
            code='TEST',
            libelle='Acte de test'
        )
        
        TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=Decimal('1000'),
            date_debut=self.today - timedelta(days=30)
        )
        
        self.prestation = Prestation.objects.create(
            cadre_exercice=self.cadre_exercice,
            designation='Prestation de test',
            acte=self.acte,
            cotation=Decimal('2.0'),
            entente_prealable='Test entente',
            suffixe='INT',
            origine='AT',
            actif=True,
            prescription=True
        )
    
    def test_admin_list_view(self):
        """Test de la vue liste de l'admin"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_prestation_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la prestation apparaît
        self.assertContains(response, 'Prestation de test')
        self.assertContains(response, 'Test Cadre')
        self.assertContains(response, 'TEST')
        self.assertContains(response, '2000 XPF')  # 2.0 × 1000
    
    def test_admin_add_view(self):
        """Test de la vue d'ajout de l'admin"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_prestation_add')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les fieldsets
        self.assertContains(response, 'Informations principales')
        self.assertContains(response, 'Acte associé')
        self.assertContains(response, 'Configuration')
        self.assertContains(response, 'Entente et assurances')
        self.assertContains(response, 'Observations')
        
        # Vérifier les champs
        self.assertContains(response, 'name="cadre_exercice"')
        self.assertContains(response, 'name="designation"')
        self.assertContains(response, 'name="acte"')
        self.assertContains(response, 'name="cotation"')
        self.assertContains(response, 'name="suffixe"')
        self.assertContains(response, 'name="origine"')
        self.assertContains(response, 'name="actif"')
        self.assertContains(response, 'name="prescription"')
    
    def test_admin_change_view(self):
        """Test de la vue de modification de l'admin"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_prestation_change', args=[self.prestation.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que les données sont pré-remplies
        self.assertContains(response, 'Prestation de test')
        self.assertContains(response, 'Test entente')
        
        # Vérifier que la page fonctionne correctement
        self.assertContains(response, 'Enregistrer')
    
    def test_admin_search_functionality(self):
        """Test de la fonctionnalité de recherche"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_prestation_changelist')
        
        # Test recherche par designation
        response = self.client.get(url, {'q': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Prestation de test')
        
        # Test recherche par cadre d'exercice
        response = self.client.get(url, {'q': 'Test Cadre'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Prestation de test')
        
        # Test recherche sans résultat
        response = self.client.get(url, {'q': 'inexistant'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Prestation de test')
    
    def test_admin_filter_functionality(self):
        """Test des filtres de l'admin"""
        # Créer des données supplémentaires pour tester les filtres
        autre_cadre = CadreExercice.objects.create(
            label='Autre Cadre',
            description='Autre description'
        )
        
        Prestation.objects.create(
            cadre_exercice=autre_cadre,
            designation='Autre prestation',
            acte=self.acte,
            cotation=Decimal('3.0'),
            entente_prealable='Autre entente',
            actif=True
        )
        
        self.client.login(email='admin@test.com', password='adminpass')
        url = reverse('admin:core_prestation_changelist')
        
        # Test filtre par cadre d'exercice
        response = self.client.get(url, {'cadre_exercice__id__exact': self.cadre_exercice.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Prestation de test')
        self.assertNotContains(response, 'Autre prestation')
        
        # Test filtre par cotation
        response = self.client.get(url, {'cotation': '2.0'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Prestation de test')
        self.assertNotContains(response, 'Autre prestation')
    
    def test_admin_create_prestation(self):
        """Test de création d'une prestation via l'admin"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_prestation_add')
        data = {
            'cadre_exercice': self.cadre_exercice.pk,
            'designation': 'Nouvelle prestation admin',
            'limite': 'Limite test',
            'acte': self.acte.pk,
            'cotation': '1.5',
            'entente_prealable': 'Entente admin',
            'assurance_maladie': 'AM test',
            'assurance_maternite_normale': 'AMN test',
            'assurance_maternite_pathologie': 'AMP test',
            'observation': 'Observation admin',
            'suffixe': 'ADMIN',
            'origine': 'LM',
            'actif': True,
            'prescription': True
        }
        
        response = self.client.post(url, data)
        
        # Devrait rediriger après création réussie
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la prestation a été créée
        self.assertTrue(
            Prestation.objects.filter(designation='Nouvelle prestation admin').exists()
        )
        
        # Vérifier les données
        prestation = Prestation.objects.get(designation='Nouvelle prestation admin')
        self.assertEqual(prestation.cadre_exercice, self.cadre_exercice)
        self.assertEqual(prestation.acte, self.acte)
        self.assertEqual(prestation.cotation, Decimal('1.5'))
        self.assertEqual(prestation.limite, 'Limite test')
        self.assertEqual(prestation.suffixe, 'ADMIN')
        self.assertEqual(prestation.origine, 'LM')
        self.assertEqual(prestation.actif, True)
        self.assertEqual(prestation.prescription, True)
    
    def test_admin_update_prestation(self):
        """Test de modification d'une prestation via l'admin"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_prestation_change', args=[self.prestation.pk])
        data = {
            'cadre_exercice': self.cadre_exercice.pk,
            'designation': 'Prestation modifiée admin',
            'limite': 'Limite modifiée',
            'acte': self.acte.pk,
            'cotation': '2.5',
            'entente_prealable': 'Entente modifiée',
            'observation': 'Observation modifiée',
            'suffixe': 'MODIF',
            'origine': 'GP',
            'actif': True,
            'prescription': False
        }
        
        response = self.client.post(url, data)
        
        # Devrait rediriger après modification réussie
        self.assertEqual(response.status_code, 302)
        
        # Vérifier les modifications
        self.prestation.refresh_from_db()
        self.assertEqual(self.prestation.designation, 'Prestation modifiée admin')
        self.assertEqual(self.prestation.cotation, Decimal('2.5'))
        self.assertEqual(self.prestation.limite, 'Limite modifiée')
        self.assertEqual(self.prestation.observation, 'Observation modifiée')
        self.assertEqual(self.prestation.suffixe, 'MODIF')
        self.assertEqual(self.prestation.origine, 'GP')
        self.assertEqual(self.prestation.actif, True)
        self.assertEqual(self.prestation.prescription, False)
    
    def test_admin_delete_prestation(self):
        """Test de suppression d'une prestation via l'admin"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        # Page de confirmation de suppression
        url = reverse('admin:core_prestation_delete', args=[self.prestation.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Confirmation de suppression
        response = self.client.post(url, {'post': 'yes'})
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la prestation a été supprimée
        self.assertFalse(
            Prestation.objects.filter(pk=self.prestation.pk).exists()
        )


class PrestationAdminPermissionsTests(TestCase):
    """Tests des permissions pour l'admin des prestations"""
    
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
        
        url = reverse('admin:core_prestation_changelist')
        response = self.client.get(url)
        
        # Devrait rediriger vers la page de login ou être interdit
        self.assertIn(response.status_code, [302, 403])
    
    def test_admin_access_superuser(self):
        """Test d'accès à l'admin avec superutilisateur"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = reverse('admin:core_prestation_changelist')
        response = self.client.get(url)
        
        # Devrait fonctionner
        self.assertEqual(response.status_code, 200)
    
    def test_admin_access_anonymous(self):
        """Test d'accès à l'admin sans authentification"""
        url = reverse('admin:core_prestation_changelist')
        response = self.client.get(url)
        
        # Devrait rediriger vers la page de login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)