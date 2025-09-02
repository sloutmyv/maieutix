"""
Tests pour l'administration des modèles Caisse et ConditionPaiement.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.admin.sites import AdminSite
from authentication.models import SageFemmeUser
from decimal import Decimal

from core.models.caisse import Caisse
from core.models.condition_paiement import ConditionPaiement
from core.admin.caisse import CaisseAdmin
from core.admin.condition_paiement import ConditionPaiementAdmin


class CaisseAdminTest(TestCase):
    """Tests de l'interface d'administration pour Caisse"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = Client()
        
        # Créer un superutilisateur
        self.admin_user = SageFemmeUser.objects.create_superuser(
            email='admin@test.nc',
            password='admin123'
        )
        
        # Créer des conditions de paiement pour les tests
        self.condition1 = ConditionPaiement.objects.create(
            designation='CAFAT Standard',
            pourcentage=Decimal('80.00')
        )
        self.condition2 = ConditionPaiement.objects.create(
            designation='Mutuelle complémentaire',
            pourcentage=Decimal('20.00')
        )
        self.condition3 = ConditionPaiement.objects.create(
            designation='Accident du travail',
            pourcentage=Decimal('100.00')
        )
        
        # Créer des caisses de test
        self.caisse1 = Caisse.objects.create(nom='CAFAT NC')
        self.caisse1.conditions_paiement_eligibles.add(self.condition1, self.condition3)
        
        self.caisse2 = Caisse.objects.create(nom='Mutuelle Médialis')
        self.caisse2.conditions_paiement_eligibles.add(self.condition2)
        
        self.caisse3 = Caisse.objects.create(nom='Caisse sans conditions')
        
        # Instance de l'admin pour les tests
        self.site = AdminSite()
        self.admin = CaisseAdmin(Caisse, self.site)

    def test_admin_list_display(self):
        """Test des champs affichés dans la liste"""
        expected_fields = [
            'nom',
            'get_conditions_count',
            'created_at'
        ]
        self.assertEqual(list(self.admin.list_display), expected_fields)

    def test_admin_list_filter(self):
        """Test des filtres disponibles"""
        expected_filters = [
            'created_at'
        ]
        self.assertEqual(list(self.admin.list_filter), expected_filters)

    def test_admin_search_fields(self):
        """Test des champs de recherche"""
        expected_search_fields = [
            'nom'
        ]
        self.assertEqual(list(self.admin.search_fields), expected_search_fields)

    def test_admin_filter_horizontal(self):
        """Test du widget horizontal pour les relations ManyToMany"""
        expected_filter_horizontal = ['conditions_paiement_eligibles']
        self.assertEqual(list(self.admin.filter_horizontal), expected_filter_horizontal)

    def test_admin_readonly_fields(self):
        """Test des champs en lecture seule"""
        expected_readonly_fields = ['created_at', 'updated_at']
        self.assertEqual(list(self.admin.readonly_fields), expected_readonly_fields)

    def test_admin_ordering(self):
        """Test de l'ordre par défaut"""
        # L'admin par défaut n'a pas d'ordering défini
        self.assertIsNone(self.admin.ordering)

    def test_admin_verbose_name(self):
        """Test du nom verbose du modèle dans l'admin"""
        self.assertEqual(Caisse._meta.verbose_name, '5. Caisse')
        self.assertEqual(Caisse._meta.verbose_name_plural, '5. Caisses')

    def test_get_conditions_count_method(self):
        """Test de la méthode get_conditions_count"""
        # Test avec caisse ayant des conditions
        result = self.admin.get_conditions_count(self.caisse1)
        self.assertEqual(result, 2)
        
        # Test avec caisse sans conditions
        result = self.admin.get_conditions_count(self.caisse3)
        self.assertEqual(result, 0)
        
        # Vérifier le nom court de la colonne
        self.assertEqual(self.admin.get_conditions_count.short_description, 'Nb conditions')

    def test_admin_access_superuser(self):
        """Test d'accès à l'admin avec superutilisateur"""
        self.client.login(username='admin@test.nc', password='admin123')
        url = reverse('admin:core_caisse_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CAFAT NC')
        self.assertContains(response, 'Mutuelle Médialis')
        self.assertContains(response, 'Caisse sans conditions')

    def test_admin_add_caisse(self):
        """Test d'ajout d'une caisse via l'admin"""
        self.client.login(username='admin@test.nc', password='admin123')
        url = reverse('admin:core_caisse_add')
        
        # Test GET du formulaire d'ajout
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ajouter 5. Caisse')
        
        # Test POST pour créer une caisse
        data = {
            'nom': 'Nouvelle Caisse Test',
            'conditions_paiement_eligibles': [self.condition1.pk, self.condition2.pk]
        }
        response = self.client.post(url, data)
        
        # Devrait rediriger vers la liste après création
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la caisse a été créée
        self.assertTrue(Caisse.objects.filter(nom='Nouvelle Caisse Test').exists())
        nouvelle_caisse = Caisse.objects.get(nom='Nouvelle Caisse Test')
        self.assertEqual(nouvelle_caisse.conditions_paiement_eligibles.count(), 2)

    def test_admin_change_caisse(self):
        """Test de modification d'une caisse via l'admin"""
        self.client.login(username='admin@test.nc', password='admin123')
        url = reverse('admin:core_caisse_change', args=[self.caisse1.pk])
        
        # Test GET du formulaire de modification
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.caisse1.nom)
        
        # Test POST pour modifier la caisse
        data = {
            'nom': 'CAFAT NC Modifiée',
            'conditions_paiement_eligibles': [self.condition2.pk, self.condition3.pk]
        }
        response = self.client.post(url, data)
        
        # Devrait rediriger vers la liste après modification
        self.assertEqual(response.status_code, 302)
        
        # Vérifier les modifications
        self.caisse1.refresh_from_db()
        self.assertEqual(self.caisse1.nom, 'CAFAT NC Modifiée')
        self.assertEqual(self.caisse1.conditions_paiement_eligibles.count(), 2)
        self.assertNotIn(self.condition1, self.caisse1.conditions_paiement_eligibles.all())

    def test_admin_delete_caisse(self):
        """Test de suppression d'une caisse via l'admin"""
        self.client.login(username='admin@test.nc', password='admin123')
        url = reverse('admin:core_caisse_delete', args=[self.caisse1.pk])
        
        # Test GET de la page de confirmation
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'5. Caisse: <a href="/admin/core/caisse/{self.caisse1.pk}/change/">{self.caisse1.nom}</a>')
        
        # Test POST pour confirmer la suppression
        response = self.client.post(url, {'post': 'yes'})
        
        # Devrait rediriger vers la liste après suppression
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la caisse a été supprimée
        self.assertFalse(Caisse.objects.filter(pk=self.caisse1.pk).exists())


class ConditionPaiementAdminTest(TestCase):
    """Tests de l'interface d'administration pour ConditionPaiement"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = Client()
        
        # Créer un superutilisateur
        self.admin_user = SageFemmeUser.objects.create_superuser(
            email='admin@test.nc',
            password='admin123'
        )
        
        # Créer des conditions de test
        self.condition1 = ConditionPaiement.objects.create(
            designation='CAFAT Standard',
            pourcentage=Decimal('80.00')
        )
        self.condition2 = ConditionPaiement.objects.create(
            designation='Mutuelle complémentaire',
            pourcentage=Decimal('20.00')
        )
        self.condition3 = ConditionPaiement.objects.create(
            designation='Accident du travail',
            pourcentage=Decimal('100.00')
        )
        
        # Créer une caisse utilisant une condition pour tester les relations
        self.caisse = Caisse.objects.create(nom='Test Caisse')
        self.caisse.conditions_paiement_eligibles.add(self.condition1)
        
        # Instance de l'admin pour les tests
        self.site = AdminSite()
        self.admin = ConditionPaiementAdmin(ConditionPaiement, self.site)

    def test_admin_list_display(self):
        """Test des champs affichés dans la liste"""
        expected_fields = [
            'designation',
            'pourcentage',
            'created_at'
        ]
        self.assertEqual(list(self.admin.list_display), expected_fields)

    def test_admin_list_filter(self):
        """Test des filtres disponibles"""
        expected_filters = [
            'created_at'
        ]
        self.assertEqual(list(self.admin.list_filter), expected_filters)

    def test_admin_search_fields(self):
        """Test des champs de recherche"""
        expected_search_fields = [
            'designation'
        ]
        self.assertEqual(list(self.admin.search_fields), expected_search_fields)

    def test_admin_readonly_fields(self):
        """Test des champs en lecture seule"""
        expected_readonly_fields = ['created_at', 'updated_at']
        self.assertEqual(list(self.admin.readonly_fields), expected_readonly_fields)

    def test_admin_ordering(self):
        """Test de l'ordre par défaut"""
        # L'admin par défaut n'a pas d'ordering défini
        self.assertIsNone(self.admin.ordering)

    def test_admin_verbose_name(self):
        """Test du nom verbose du modèle dans l'admin"""
        self.assertEqual(ConditionPaiement._meta.verbose_name, '5.1 Condition de paiement')
        self.assertEqual(ConditionPaiement._meta.verbose_name_plural, '5.1 Conditions de paiement')

    def test_admin_basic_functionality(self):
        """Test de la fonctionnalité de base de l'admin"""
        # Test que l'admin fonctionne avec les champs de base
        self.assertTrue(hasattr(self.admin, 'list_display'))
        self.assertTrue(hasattr(self.admin, 'search_fields'))
        self.assertTrue(hasattr(self.admin, 'readonly_fields'))

    def test_admin_access_superuser(self):
        """Test d'accès à l'admin avec superutilisateur"""
        self.client.login(username='admin@test.nc', password='admin123')
        url = reverse('admin:core_conditionpaiement_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CAFAT Standard')
        self.assertContains(response, 'Mutuelle complémentaire')
        self.assertContains(response, 'Accident du travail')

    def test_admin_add_condition(self):
        """Test d'ajout d'une condition via l'admin"""
        self.client.login(username='admin@test.nc', password='admin123')
        url = reverse('admin:core_conditionpaiement_add')
        
        # Test GET du formulaire d'ajout
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ajouter 5.1 Condition de paiement')
        
        # Test POST pour créer une condition
        data = {
            'designation': 'Nouvelle Condition Test',
            'pourcentage': '75.50'
        }
        response = self.client.post(url, data)
        
        # Devrait rediriger vers la liste après création
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la condition a été créée
        self.assertTrue(ConditionPaiement.objects.filter(designation='Nouvelle Condition Test').exists())
        nouvelle_condition = ConditionPaiement.objects.get(designation='Nouvelle Condition Test')
        self.assertEqual(nouvelle_condition.pourcentage, Decimal('75.50'))

    def test_admin_change_condition(self):
        """Test de modification d'une condition via l'admin"""
        self.client.login(username='admin@test.nc', password='admin123')
        url = reverse('admin:core_conditionpaiement_change', args=[self.condition1.pk])
        
        # Test GET du formulaire de modification
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.condition1.designation)
        
        # Test POST pour modifier la condition
        data = {
            'designation': 'CAFAT Standard Modifié',
            'pourcentage': '85.00'
        }
        response = self.client.post(url, data)
        
        # Devrait rediriger vers la liste après modification
        self.assertEqual(response.status_code, 302)
        
        # Vérifier les modifications
        self.condition1.refresh_from_db()
        self.assertEqual(self.condition1.designation, 'CAFAT Standard Modifié')
        self.assertEqual(self.condition1.pourcentage, Decimal('85.00'))

    def test_admin_delete_condition(self):
        """Test de suppression d'une condition via l'admin"""
        self.client.login(username='admin@test.nc', password='admin123')
        url = reverse('admin:core_conditionpaiement_delete', args=[self.condition2.pk])
        
        # Test GET de la page de confirmation
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'5.1 Condition de paiement: <a href="/admin/core/conditionpaiement/{self.condition2.pk}/change/">{self.condition2}</a>')
        
        # Test POST pour confirmer la suppression
        response = self.client.post(url, {'post': 'yes'})
        
        # Devrait rediriger vers la liste après suppression
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la condition a été supprimée
        self.assertFalse(ConditionPaiement.objects.filter(pk=self.condition2.pk).exists())

    def test_admin_delete_condition_used_by_caisse(self):
        """Test de suppression d'une condition utilisée par une caisse"""
        self.client.login(username='admin@test.nc', password='admin123')
        url = reverse('admin:core_conditionpaiement_delete', args=[self.condition1.pk])
        
        # Test POST pour confirmer la suppression
        response = self.client.post(url, {'post': 'yes'})
        
        # La suppression devrait réussir
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la condition a été supprimée
        self.assertFalse(ConditionPaiement.objects.filter(pk=self.condition1.pk).exists())
        
        # Vérifier que la caisse existe toujours mais n'a plus cette condition
        self.caisse.refresh_from_db()
        self.assertEqual(self.caisse.conditions_paiement_eligibles.count(), 0)


class AdminIntegrationTest(TestCase):
    """Tests d'intégration entre les admins Caisse et ConditionPaiement"""
    
    def setUp(self):
        """Configuration pour les tests d'intégration"""
        self.client = Client()
        
        # Créer un superutilisateur
        self.admin_user = SageFemmeUser.objects.create_superuser(
            email='admin@test.nc',
            password='admin123'
        )
        
        # Créer des données de test
        self.condition = ConditionPaiement.objects.create(
            designation='Integration Test',
            pourcentage=Decimal('50.00')
        )
        self.caisse = Caisse.objects.create(nom='Integration Caisse')
        self.caisse.conditions_paiement_eligibles.add(self.condition)

    def test_admin_workflow_creation(self):
        """Test du workflow de création condition -> caisse"""
        self.client.login(username='admin@test.nc', password='admin123')
        
        # 1. Créer une nouvelle condition
        url = reverse('admin:core_conditionpaiement_add')
        data = {
            'designation': 'Workflow Condition',
            'pourcentage': '60.00'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        # Récupérer la condition créée
        nouvelle_condition = ConditionPaiement.objects.get(designation='Workflow Condition')
        
        # 2. Créer une caisse utilisant cette condition
        url = reverse('admin:core_caisse_add')
        data = {
            'nom': 'Workflow Caisse',
            'conditions_paiement_eligibles': [nouvelle_condition.pk]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        # Vérifier les relations
        nouvelle_caisse = Caisse.objects.get(nom='Workflow Caisse')
        self.assertEqual(nouvelle_caisse.conditions_paiement_eligibles.count(), 1)
        self.assertEqual(nouvelle_caisse.conditions_paiement_eligibles.first(), nouvelle_condition)

    def test_admin_filter_integration(self):
        """Test des filtres entre les modèles"""
        self.client.login(username='admin@test.nc', password='admin123')
        
        # Test du filtre par condition dans la liste des caisses
        url = reverse('admin:core_caisse_changelist')
        response = self.client.get(url, {'conditions_paiement_eligibles__exact': self.condition.pk})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration Caisse')

    def test_admin_search_integration(self):
        """Test de la recherche par nom de caisse"""
        self.client.login(username='admin@test.nc', password='admin123')
        
        # Recherche dans les caisses par nom de caisse
        url = reverse('admin:core_caisse_changelist')
        response = self.client.get(url, {'q': 'Integration'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration Caisse')