"""
Tests pour le modèle ConditionPaiement
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal

from core.models.condition_paiement import ConditionPaiement


class ConditionPaiementModelTests(TestCase):
    """Tests pour le modèle ConditionPaiement"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.condition = ConditionPaiement.objects.create(
            designation='Remboursement CAFAT',
            pourcentage=Decimal('80.00')
        )
    
    def test_str_method(self):
        """Test de la représentation string"""
        expected = 'Remboursement CAFAT (80.00%)'
        self.assertEqual(str(self.condition), expected)
    
    def test_str_method_with_long_designation(self):
        """Test str avec désignation longue (pas de troncature dans __str__)"""
        long_designation = 'Remboursement intégral par la caisse d\'assurance maladie universelle'
        condition = ConditionPaiement.objects.create(
            designation=long_designation,
            pourcentage=Decimal('100.00')
        )
        # Le __str__ retourne la désignation complète + pourcentage
        expected = f'{long_designation} (100.00%)'
        self.assertEqual(str(condition), expected)
    
    def test_full_clean_negative_percentage(self):
        """Test que les pourcentages négatifs sont rejetés par les validateurs"""
        condition = ConditionPaiement(
            designation='Test',
            pourcentage=Decimal('-10.00')
        )
        with self.assertRaises(ValidationError):
            condition.full_clean()
    
    def test_full_clean_zero_percentage(self):
        """Test que le pourcentage zéro est accepté"""
        condition = ConditionPaiement(
            designation='Aucun remboursement',
            pourcentage=Decimal('0.00')
        )
        # Ne devrait pas lever d'erreur
        condition.full_clean()
    
    def test_full_clean_percentage_over_100(self):
        """Test que les pourcentages supérieurs à 100% sont rejetés par les validateurs"""
        condition = ConditionPaiement(
            designation='Test',
            pourcentage=Decimal('150.00')
        )
        with self.assertRaises(ValidationError):
            condition.full_clean()
    
    def test_full_clean_valid_percentage(self):
        """Test que les pourcentages valides passent la validation"""
        condition = ConditionPaiement(
            designation='Remboursement partiel',
            pourcentage=Decimal('75.50')
        )
        # Ne devrait pas lever d'erreur
        condition.full_clean()
    
    def test_designation_required(self):
        """Test que la désignation est obligatoire"""
        with self.assertRaises(ValidationError):
            condition = ConditionPaiement(pourcentage=Decimal('50.00'))
            condition.full_clean()
    
    def test_pourcentage_required(self):
        """Test que le pourcentage est obligatoire"""
        with self.assertRaises(ValidationError):
            condition = ConditionPaiement(designation='Test')
            condition.full_clean()
    
    def test_designation_max_length(self):
        """Test de la longueur maximale de la désignation"""
        long_designation = 'x' * 201  # Plus de 200 caractères
        with self.assertRaises(ValidationError):
            condition = ConditionPaiement(
                designation=long_designation,
                pourcentage=Decimal('50.00')
            )
            condition.full_clean()
    
    def test_pourcentage_decimal_places(self):
        """Test de la précision décimale du pourcentage"""
        condition = ConditionPaiement.objects.create(
            designation='Test précision',
            pourcentage=Decimal('33.33')
        )
        self.assertEqual(condition.pourcentage, Decimal('33.33'))
    
    def test_ordering_by_designation(self):
        """Test tri par désignation"""
        condition1 = ConditionPaiement.objects.create(
            designation='Zebra',
            pourcentage=Decimal('50.00')
        )
        condition2 = ConditionPaiement.objects.create(
            designation='Alpha',
            pourcentage=Decimal('60.00')
        )
        
        conditions = list(ConditionPaiement.objects.all())
        # Vérifie que les conditions sont triées par désignation
        designations = [c.designation for c in conditions]
        self.assertEqual(designations, sorted(designations))
    
    def test_meta_verbose_names(self):
        """Test des noms verbose du modèle"""
        self.assertEqual(ConditionPaiement._meta.verbose_name, '5.1 Condition de paiement')
        self.assertEqual(ConditionPaiement._meta.verbose_name_plural, '5.1 Conditions de paiement')
    
    def test_designation_can_be_duplicated(self):
        """Test que les désignations peuvent être dupliquées (pas de contrainte unique)"""
        # Créer une deuxième condition avec la même désignation
        condition2 = ConditionPaiement.objects.create(
            designation='Remboursement CAFAT',  # Même désignation
            pourcentage=Decimal('90.00')
        )
        self.assertNotEqual(self.condition.pk, condition2.pk)
        self.assertEqual(self.condition.designation, condition2.designation)
    
    def test_database_fields(self):
        """Test des contraintes de champs de base de données"""
        # Test que les champs sont correctement sauvegardés
        condition = ConditionPaiement.objects.create(
            designation='Test DB',
            pourcentage=Decimal('42.75')
        )
        
        # Rechargement depuis la DB
        condition.refresh_from_db()
        self.assertEqual(condition.designation, 'Test DB')
        self.assertEqual(condition.pourcentage, Decimal('42.75'))
    
    def test_created_at_field(self):
        """Test que le champ created_at est automatiquement rempli"""
        condition = ConditionPaiement.objects.create(
            designation='Test timestamp',
            pourcentage=Decimal('25.00')
        )
        self.assertIsNotNone(condition.created_at)
    
    def test_updated_at_field(self):
        """Test que le champ updated_at est automatiquement mis à jour"""
        condition = ConditionPaiement.objects.create(
            designation='Test update',
            pourcentage=Decimal('25.00')
        )
        original_updated = condition.updated_at
        
        # Modification
        condition.pourcentage = Decimal('30.00')
        condition.save()
        
        condition.refresh_from_db()
        self.assertGreater(condition.updated_at, original_updated)


class ConditionPaiementQueryTests(TestCase):
    """Tests des requêtes sur le modèle ConditionPaiement"""
    
    def setUp(self):
        """Configuration des données de test"""
        ConditionPaiement.objects.create(
            designation='CAFAT Standard',
            pourcentage=Decimal('80.00')
        )
        ConditionPaiement.objects.create(
            designation='CAFAT Accident du travail',
            pourcentage=Decimal('100.00')
        )
        ConditionPaiement.objects.create(
            designation='Mutuelle complémentaire',
            pourcentage=Decimal('20.00')
        )
    
    def test_filter_by_percentage_range(self):
        """Test filtrage par plage de pourcentage"""
        conditions_high = ConditionPaiement.objects.filter(pourcentage__gte=80)
        self.assertEqual(conditions_high.count(), 2)
        
        conditions_low = ConditionPaiement.objects.filter(pourcentage__lt=50)
        self.assertEqual(conditions_low.count(), 1)
    
    def test_search_by_designation(self):
        """Test recherche par désignation"""
        cafat_conditions = ConditionPaiement.objects.filter(
            designation__icontains='CAFAT'
        )
        self.assertEqual(cafat_conditions.count(), 2)
    
    def test_order_by_percentage_desc(self):
        """Test tri par pourcentage décroissant"""
        conditions = list(ConditionPaiement.objects.order_by('-pourcentage'))
        pourcentages = [c.pourcentage for c in conditions]
        self.assertEqual(pourcentages, sorted(pourcentages, reverse=True))
    
    def test_count_total_conditions(self):
        """Test comptage total des conditions"""
        self.assertEqual(ConditionPaiement.objects.count(), 3)
    
    def test_exists_method(self):
        """Test de la méthode exists()"""
        self.assertTrue(
            ConditionPaiement.objects.filter(pourcentage=100).exists()
        )
        self.assertFalse(
            ConditionPaiement.objects.filter(pourcentage=150).exists()
        )