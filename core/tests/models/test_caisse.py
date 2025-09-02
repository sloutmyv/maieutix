"""
Tests pour le modèle Caisse
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal

from core.models.caisse import Caisse
from core.models.condition_paiement import ConditionPaiement


class CaisseModelTests(TestCase):
    """Tests pour le modèle Caisse"""
    
    def setUp(self):
        """Configuration des données de test"""
        # Créer des conditions de paiement pour les tests
        self.condition1 = ConditionPaiement.objects.create(
            designation='Remboursement CAFAT',
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
        
        self.caisse = Caisse.objects.create(
            nom='CAFAT Nouvelle-Calédonie'
        )
    
    def test_str_method(self):
        """Test de la représentation string"""
        expected = 'CAFAT Nouvelle-Calédonie'
        self.assertEqual(str(self.caisse), expected)
    
    def test_str_method_with_long_name(self):
        """Test str avec nom long (pas de troncature dans __str__)"""
        long_nom = 'Caisse d\'assurance maladie universelle avec un nom extrêmement long qui dépasse largement la limite recommandée'
        caisse = Caisse.objects.create(nom=long_nom)
        # Le __str__ retourne le nom complet, pas de troncature
        self.assertEqual(str(caisse), long_nom)
    
    def test_nom_required(self):
        """Test que le nom est obligatoire"""
        with self.assertRaises(ValidationError):
            caisse = Caisse()
            caisse.full_clean()
    
    def test_nom_max_length(self):
        """Test de la longueur maximale du nom"""
        long_nom = 'x' * 201  # Plus de 200 caractères
        with self.assertRaises(ValidationError):
            caisse = Caisse(nom=long_nom)
            caisse.full_clean()
    
    def test_nom_can_be_duplicated(self):
        """Test que les noms peuvent être dupliqués (pas de contrainte unique)"""
        # Créer une deuxième caisse avec le même nom
        caisse2 = Caisse.objects.create(nom='CAFAT Nouvelle-Calédonie')
        self.assertNotEqual(self.caisse.pk, caisse2.pk)
        self.assertEqual(self.caisse.nom, caisse2.nom)
    
    def test_many_to_many_relationship(self):
        """Test de la relation ManyToMany avec ConditionPaiement"""
        # Ajouter des conditions à la caisse
        self.caisse.conditions_paiement_eligibles.add(self.condition1, self.condition2)
        
        # Vérifier la relation
        conditions = list(self.caisse.conditions_paiement_eligibles.all())
        self.assertEqual(len(conditions), 2)
        self.assertIn(self.condition1, conditions)
        self.assertIn(self.condition2, conditions)
    
    def test_reverse_relationship(self):
        """Test de la relation inverse depuis ConditionPaiement"""
        self.caisse.conditions_paiement_eligibles.add(self.condition1)
        
        # Vérifier la relation inverse
        caisses = list(self.condition1.caisses_eligibles.all())
        self.assertEqual(len(caisses), 1)
        self.assertEqual(caisses[0], self.caisse)
    
    def test_empty_conditions_allowed(self):
        """Test qu'une caisse peut n'avoir aucune condition"""
        caisse_vide = Caisse.objects.create(nom='Caisse sans conditions')
        self.assertEqual(caisse_vide.conditions_paiement_eligibles.count(), 0)
    
    def test_multiple_conditions_management(self):
        """Test de la gestion de plusieurs conditions"""
        # Ajouter toutes les conditions
        self.caisse.conditions_paiement_eligibles.set([
            self.condition1, self.condition2, self.condition3
        ])
        
        self.assertEqual(self.caisse.conditions_paiement_eligibles.count(), 3)
        
        # Retirer une condition
        self.caisse.conditions_paiement_eligibles.remove(self.condition2)
        self.assertEqual(self.caisse.conditions_paiement_eligibles.count(), 2)
        
        # Vérifier les conditions restantes
        conditions_restantes = list(self.caisse.conditions_paiement_eligibles.all())
        self.assertIn(self.condition1, conditions_restantes)
        self.assertIn(self.condition3, conditions_restantes)
        self.assertNotIn(self.condition2, conditions_restantes)
    
    def test_ordering_by_nom(self):
        """Test tri par nom"""
        caisse1 = Caisse.objects.create(nom='Zebra Caisse')
        caisse2 = Caisse.objects.create(nom='Alpha Caisse')
        
        caisses = list(Caisse.objects.all())
        # Vérifie que les caisses sont triées par nom
        noms = [c.nom for c in caisses]
        self.assertEqual(noms, sorted(noms))
    
    def test_meta_verbose_names(self):
        """Test des noms verbose du modèle"""
        self.assertEqual(Caisse._meta.verbose_name, '5. Caisse')
        self.assertEqual(Caisse._meta.verbose_name_plural, '5. Caisses')
    
    def test_created_at_field(self):
        """Test que le champ created_at est automatiquement rempli"""
        caisse = Caisse.objects.create(nom='Test timestamp')
        self.assertIsNotNone(caisse.created_at)
    
    def test_updated_at_field(self):
        """Test que le champ updated_at est automatiquement mis à jour"""
        caisse = Caisse.objects.create(nom='Test update')
        original_updated = caisse.updated_at
        
        # Modification
        caisse.nom = 'Test update modifié'
        caisse.save()
        
        caisse.refresh_from_db()
        self.assertGreater(caisse.updated_at, original_updated)
    
    def test_database_fields(self):
        """Test des contraintes de champs de base de données"""
        # Test que les champs sont correctement sauvegardés
        caisse = Caisse.objects.create(nom='Test DB')
        caisse.conditions_paiement_eligibles.add(self.condition1)
        
        # Rechargement depuis la DB
        caisse.refresh_from_db()
        self.assertEqual(caisse.nom, 'Test DB')
        self.assertEqual(caisse.conditions_paiement_eligibles.count(), 1)


class CaisseQueryTests(TestCase):
    """Tests des requêtes sur le modèle Caisse"""
    
    def setUp(self):
        """Configuration des données de test"""
        # Conditions de paiement
        self.condition_cafat = ConditionPaiement.objects.create(
            designation='CAFAT',
            pourcentage=Decimal('80.00')
        )
        self.condition_mutuelle = ConditionPaiement.objects.create(
            designation='Mutuelle',
            pourcentage=Decimal('20.00')
        )
        self.condition_at = ConditionPaiement.objects.create(
            designation='Accident du travail',
            pourcentage=Decimal('100.00')
        )
        
        # Caisses
        self.caisse1 = Caisse.objects.create(nom='CAFAT NC')
        self.caisse1.conditions_paiement_eligibles.add(
            self.condition_cafat, self.condition_at
        )
        
        self.caisse2 = Caisse.objects.create(nom='Mutuelle Médialis')
        self.caisse2.conditions_paiement_eligibles.add(self.condition_mutuelle)
        
        self.caisse3 = Caisse.objects.create(nom='Caisse sans conditions')
    
    def test_filter_by_conditions(self):
        """Test filtrage par conditions de paiement"""
        caisses_avec_cafat = Caisse.objects.filter(
            conditions_paiement_eligibles=self.condition_cafat
        )
        self.assertEqual(caisses_avec_cafat.count(), 1)
        self.assertEqual(caisses_avec_cafat.first(), self.caisse1)
    
    def test_filter_by_multiple_conditions(self):
        """Test filtrage par plusieurs conditions"""
        caisses_avec_at = Caisse.objects.filter(
            conditions_paiement_eligibles=self.condition_at
        )
        self.assertEqual(caisses_avec_at.count(), 1)
        self.assertEqual(caisses_avec_at.first(), self.caisse1)
    
    def test_filter_caisses_without_conditions(self):
        """Test filtrage des caisses sans conditions"""
        caisses_sans_conditions = Caisse.objects.filter(
            conditions_paiement_eligibles__isnull=True
        )
        self.assertEqual(caisses_sans_conditions.count(), 1)
        self.assertEqual(caisses_sans_conditions.first(), self.caisse3)
    
    def test_search_by_nom(self):
        """Test recherche par nom"""
        caisses_cafat = Caisse.objects.filter(nom__icontains='CAFAT')
        self.assertEqual(caisses_cafat.count(), 1)
        self.assertEqual(caisses_cafat.first(), self.caisse1)
    
    def test_prefetch_conditions(self):
        """Test préchargement des conditions liées"""
        caisses = Caisse.objects.prefetch_related(
            'conditions_paiement_eligibles'
        ).all()
        
        # Vérification que le préchargement fonctionne
        for caisse in caisses:
            conditions = list(caisse.conditions_paiement_eligibles.all())
            # Cette opération ne devrait pas générer de nouvelle requête
            # grâce au prefetch_related
            if caisse == self.caisse1:
                self.assertEqual(len(conditions), 2)
            elif caisse == self.caisse2:
                self.assertEqual(len(conditions), 1)
            else:  # caisse3
                self.assertEqual(len(conditions), 0)
    
    def test_count_caisses_by_conditions(self):
        """Test comptage des caisses par conditions"""
        # Nombre de caisses avec des conditions
        caisses_avec_conditions = Caisse.objects.exclude(
            conditions_paiement_eligibles__isnull=True
        ).distinct()
        self.assertEqual(caisses_avec_conditions.count(), 2)
        
        # Nombre total de caisses
        self.assertEqual(Caisse.objects.count(), 3)
    
    def test_order_by_conditions_count(self):
        """Test tri par nombre de conditions"""
        from django.db.models import Count
        
        caisses = Caisse.objects.annotate(
            nb_conditions=Count('conditions_paiement_eligibles')
        ).order_by('-nb_conditions')
        
        caisses_list = list(caisses)
        # La caisse1 a 2 conditions, caisse2 a 1, caisse3 a 0
        self.assertEqual(caisses_list[0], self.caisse1)
        self.assertEqual(caisses_list[1], self.caisse2)
        self.assertEqual(caisses_list[2], self.caisse3)


class CaisseConditionPaiementIntegrationTests(TestCase):
    """Tests d'intégration entre Caisse et ConditionPaiement"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.condition = ConditionPaiement.objects.create(
            designation='Test Integration',
            pourcentage=Decimal('50.00')
        )
        self.caisse = Caisse.objects.create(nom='Test Integration')
    
    def test_cascade_delete_condition(self):
        """Test suppression d'une condition utilisée par des caisses"""
        self.caisse.conditions_paiement_eligibles.add(self.condition)
        
        # Supprimer la condition
        condition_id = self.condition.id
        self.condition.delete()
        
        # Vérifier que la relation a été supprimée mais pas la caisse
        self.caisse.refresh_from_db()
        self.assertEqual(self.caisse.conditions_paiement_eligibles.count(), 0)
        self.assertTrue(Caisse.objects.filter(id=self.caisse.id).exists())
    
    def test_cascade_delete_caisse(self):
        """Test suppression d'une caisse avec des conditions"""
        self.caisse.conditions_paiement_eligibles.add(self.condition)
        
        # Supprimer la caisse
        caisse_id = self.caisse.id
        self.caisse.delete()
        
        # Vérifier que la condition existe toujours
        self.assertTrue(
            ConditionPaiement.objects.filter(id=self.condition.id).exists()
        )
        self.assertFalse(Caisse.objects.filter(id=caisse_id).exists())
    
    def test_multiple_caisses_same_condition(self):
        """Test qu'une condition peut être utilisée par plusieurs caisses"""
        caisse2 = Caisse.objects.create(nom='Caisse 2')
        
        # Associer la même condition aux deux caisses
        self.caisse.conditions_paiement_eligibles.add(self.condition)
        caisse2.conditions_paiement_eligibles.add(self.condition)
        
        # Vérifier les relations
        self.assertEqual(
            self.condition.caisses_eligibles.count(), 2
        )
        caisses = list(self.condition.caisses_eligibles.all())
        self.assertIn(self.caisse, caisses)
        self.assertIn(caisse2, caisses)
    
    def test_bulk_operations(self):
        """Test des opérations en lot"""
        # Créer plusieurs conditions
        conditions = []
        for i in range(5):
            condition = ConditionPaiement.objects.create(
                designation=f'Condition {i}',
                pourcentage=Decimal(f'{i * 10}.00')
            )
            conditions.append(condition)
        
        # Associer toutes les conditions à la caisse en une seule opération
        self.caisse.conditions_paiement_eligibles.set(conditions)
        
        self.assertEqual(self.caisse.conditions_paiement_eligibles.count(), 5)
        
        # Retirer plusieurs conditions
        self.caisse.conditions_paiement_eligibles.remove(
            conditions[0], conditions[1]
        )
        
        self.assertEqual(self.caisse.conditions_paiement_eligibles.count(), 3)