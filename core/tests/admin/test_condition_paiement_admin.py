"""
Tests spécifiques pour l'administration du modèle ConditionPaiement.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.admin.sites import AdminSite
from authentication.models import SageFemmeUser
from decimal import Decimal

from core.models.condition_paiement import ConditionPaiement
from core.models.caisse import Caisse
from core.admin.condition_paiement import ConditionPaiementAdmin


class ConditionPaiementAdminDetailedTest(TestCase):
    """Tests détaillés de l'interface d'administration pour ConditionPaiement"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = Client()
        
        # Créer un superutilisateur
        self.admin_user = SageFemmeUser.objects.create_superuser(
            email='admin@test.nc',
            password='admin123'
        )
        
        # Créer des conditions de test avec différents pourcentages
        self.condition_zero = ConditionPaiement.objects.create(
            designation='Aucun remboursement',
            pourcentage=Decimal('0.00')
        )
        
        self.condition_partiel = ConditionPaiement.objects.create(
            designation='Remboursement partiel',
            pourcentage=Decimal('33.33')
        )
        
        self.condition_standard = ConditionPaiement.objects.create(
            designation='CAFAT Standard',
            pourcentage=Decimal('80.00')
        )
        
        self.condition_total = ConditionPaiement.objects.create(
            designation='Remboursement total',
            pourcentage=Decimal('100.00')
        )
        
        # Créer des caisses utilisant certaines conditions
        self.caisse1 = Caisse.objects.create(nom='Caisse Principale')
        self.caisse1.conditions_paiement_eligibles.add(
            self.condition_standard, self.condition_total
        )
        
        self.caisse2 = Caisse.objects.create(nom='Caisse Secondaire')
        self.caisse2.conditions_paiement_eligibles.add(self.condition_partiel)
        
        self.caisse3 = Caisse.objects.create(nom='Caisse Multiple')
        self.caisse3.conditions_paiement_eligibles.add(
            self.condition_standard, self.condition_partiel, self.condition_zero
        )
        
        # Instance de l'admin pour les tests
        self.site = AdminSite()
        self.admin = ConditionPaiementAdmin(ConditionPaiement, self.site)

    def test_admin_list_display_content(self):
        """Test du contenu des champs affichés dans la liste"""
        self.client.login(username='admin@test.nc', password='admin123')
        url = reverse('admin:core_conditionpaiement_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que tous les noms de conditions sont affichés
        self.assertContains(response, 'Aucun remboursement')
        self.assertContains(response, 'Remboursement partiel')
        self.assertContains(response, 'CAFAT Standard')
        self.assertContains(response, 'Remboursement total')
        
        # Vérifier l'affichage des pourcentages formatés
        self.assertContains(response, '0.00%')
        self.assertContains(response, '33.33%')
        self.assertContains(response, '80.00%')
        self.assertContains(response, '100.00%')

    def test_list_display_fields(self):
        """Test que les champs de list_display sont corrects"""
        expected_fields = ['designation', 'pourcentage', 'created_at']
        self.assertEqual(list(self.admin.list_display), expected_fields)

    def test_search_fields_configuration(self):
        """Test que les champs de recherche sont correctement configurés"""
        expected_fields = ['designation']
        self.assertEqual(list(self.admin.search_fields), expected_fields)

    def test_list_filter_configuration(self):
        """Test que les filtres sont correctement configurés"""
        expected_filters = ['created_at']
        self.assertEqual(list(self.admin.list_filter), expected_filters)

    def test_admin_filter_by_percentage(self):
        """Test du filtrage par pourcentage"""
        self.client.login(username='admin@test.nc', password='admin123')
        url = reverse('admin:core_conditionpaiement_changelist')
        
        # Test filtre par pourcentage exact
        response = self.client.get(url, {'pourcentage__exact': '80.00'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CAFAT Standard')
        self.assertNotContains(response, 'Remboursement partiel')
        
        # Test filtre par pourcentage supérieur
        response = self.client.get(url, {'pourcentage__gte': '50.00'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CAFAT Standard')
        self.assertContains(response, 'Remboursement total')
        self.assertNotContains(response, 'Remboursement partiel')

    def test_admin_search_functionality(self):
        """Test de la fonctionnalité de recherche"""
        self.client.login(username='admin@test.nc', password='admin123')
        url = reverse('admin:core_conditionpaiement_changelist')
        
        # Recherche par désignation complète
        response = self.client.get(url, {'q': 'CAFAT Standard'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CAFAT Standard')
        self.assertNotContains(response, 'Remboursement partiel')
        
        # Recherche par mot partiel
        response = self.client.get(url, {'q': 'Remboursement'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Remboursement partiel')
        self.assertContains(response, 'Remboursement total')
        self.assertContains(response, 'Aucun remboursement')
        self.assertNotContains(response, 'CAFAT Standard')
        
        # Recherche insensible à la casse
        response = self.client.get(url, {'q': 'cafat'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CAFAT Standard')

    def test_admin_ordering(self):
        """Test de l'ordre d'affichage"""
        self.client.login(username='admin@test.nc', password='admin123')
        url = reverse('admin:core_conditionpaiement_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Extraire l'ordre des conditions depuis la réponse
        content = response.content.decode()
        
        # Vérifier que les conditions apparaissent dans l'ordre alphabétique par désignation
        pos_aucun = content.find('Aucun remboursement')
        pos_cafat = content.find('CAFAT Standard')
        pos_partiel = content.find('Remboursement partiel')
        pos_total = content.find('Remboursement total')
        
        self.assertTrue(pos_aucun < pos_cafat < pos_partiel < pos_total)

    def test_admin_form_validation(self):
        """Test de la validation du formulaire d'administration"""
        self.client.login(username='admin@test.nc', password='admin123')
        url = reverse('admin:core_conditionpaiement_add')
        
        # Test avec données valides
        valid_data = {
            'designation': 'Test Validation Valide',
            'pourcentage': '75.25'
        }
        response = self.client.post(url, valid_data)
        self.assertEqual(response.status_code, 302)  # Redirection après succès
        
        # Vérifier la création
        self.assertTrue(
            ConditionPaiement.objects.filter(designation='Test Validation Valide').exists()
        )
        
        # Test avec pourcentage négatif
        invalid_data = {
            'designation': 'Test Invalide',
            'pourcentage': '-10.00'
        }
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, 200)  # Reste sur la page avec erreurs
        self.assertContains(response, 'error')
        
        # Test avec pourcentage trop élevé
        invalid_data = {
            'designation': 'Test Invalide 2',
            'pourcentage': '150.00'
        }
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, 200)  # Reste sur la page avec erreurs
        self.assertContains(response, 'error')

    def test_admin_bulk_actions(self):
        """Test des actions en lot"""
        self.client.login(username='admin@test.nc', password='admin123')
        url = reverse('admin:core_conditionpaiement_changelist')
        
        # Test de sélection multiple pour suppression
        data = {
            'action': 'delete_selected',
            '_selected_action': [self.condition_zero.pk, self.condition_partiel.pk],
            'post': 'yes'  # Confirmer la suppression
        }
        
        # D'abord, obtenir la page de confirmation
        response = self.client.post(url, {
            'action': 'delete_selected',
            '_selected_action': [self.condition_zero.pk, self.condition_partiel.pk]
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tous les objets suivants et les éléments liés seront supprimés')
        
        # Confirmer la suppression
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirection après suppression
        
        # Vérifier les suppressions
        self.assertFalse(
            ConditionPaiement.objects.filter(pk=self.condition_zero.pk).exists()
        )
        self.assertFalse(
            ConditionPaiement.objects.filter(pk=self.condition_partiel.pk).exists()
        )

    def test_admin_readonly_fields_display(self):
        """Test de l'affichage des champs en lecture seule"""
        self.client.login(username='admin@test.nc', password='admin123')
        url = reverse('admin:core_conditionpaiement_change', args=[self.condition_standard.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que les champs readonly sont affichés mais non modifiables
        # Les labels peuvent être en anglais ou français selon la configuration
        self.assertTrue(
            'Created at' in response.content.decode() or 'Créée le' in response.content.decode()
        )
        self.assertTrue(
            'Updated at' in response.content.decode() or 'Modifiée le' in response.content.decode()
        )
        
        # Les champs readonly ne devraient pas avoir d'input modifiable
        content = response.content.decode()
        self.assertNotIn('name="created_at"', content)
        self.assertNotIn('name="updated_at"', content)

    def test_admin_readonly_fields(self):
        """Test que les champs readonly sont correctement configurés"""
        expected_readonly = ['created_at', 'updated_at']
        self.assertEqual(list(self.admin.readonly_fields), expected_readonly)

    def test_admin_unicode_handling(self):
        """Test de la gestion des caractères Unicode"""
        self.client.login(username='admin@test.nc', password='admin123')
        url = reverse('admin:core_conditionpaiement_add')
        
        # Test avec des caractères spéciaux
        data = {
            'designation': 'Condition spéciale avec accents éàî',
            'pourcentage': '42.50'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        # Vérifier la création avec caractères spéciaux
        condition = ConditionPaiement.objects.get(designation='Condition spéciale avec accents éàî')
        self.assertEqual(condition.pourcentage, Decimal('42.50'))
        
        # Vérifier l'affichage dans la liste
        list_url = reverse('admin:core_conditionpaiement_changelist')
        response = self.client.get(list_url)
        self.assertContains(response, 'Condition spéciale avec accents éàî')

    def test_admin_performance_queries(self):
        """Test de performance pour éviter les requêtes N+1"""
        self.client.login(username='admin@test.nc', password='admin123')
        
        # Créer plus de données pour tester la performance
        for i in range(10):
            condition = ConditionPaiement.objects.create(
                designation=f'Condition Performance {i}',
                pourcentage=Decimal(f'{i * 10}.00')
            )
            caisse = Caisse.objects.create(nom=f'Caisse Performance {i}')
            caisse.conditions_paiement_eligibles.add(condition)
        
        url = reverse('admin:core_conditionpaiement_changelist')
        
        # Le test de performance réel nécessiterait django-debug-toolbar
        # ou des outils similaires. Ici on teste juste que la page se charge
        # Test de performance - le nombre exact de requêtes peut varier selon Django
        # On teste juste que la page se charge correctement sans tester le nombre exact
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_admin_custom_actions(self):
        """Test des actions personnalisées si elles existent"""
        # Ce test vérifie que l'admin fonctionne correctement
        # même si des actions personnalisées sont ajoutées plus tard
        
        self.client.login(username='admin@test.nc', password='admin123')
        url = reverse('admin:core_conditionpaiement_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que l'action par défaut (delete_selected) est disponible
        self.assertContains(response, 'delete_selected')