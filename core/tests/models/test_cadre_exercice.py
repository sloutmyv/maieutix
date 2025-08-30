"""
Tests pour le modèle CadreExercice
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from core.models.cadre_exercice import CadreExercice


class CadreExerciceModelTests(TestCase):
    """Tests pour le modèle CadreExercice"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.cadre_exercice = CadreExercice.objects.create(
            label='Suivi de grossesse',
            description='Cadre d\'exercice pour le suivi de grossesse normale'
        )
    
    def test_str_method(self):
        """Test de la représentation string"""
        expected = 'Suivi de grossesse'
        self.assertEqual(str(self.cadre_exercice), expected)
    
    def test_str_method_with_different_labels(self):
        """Test str avec différents labels"""
        cadres = [
            CadreExercice.objects.create(
                label='Accouchement',
                description='Description accouchement'
            ),
            CadreExercice.objects.create(
                label='Post-partum',
                description='Description post-partum'
            ),
            CadreExercice.objects.create(
                label='Gynécologie',
                description='Description gynécologie'
            )
        ]
        
        expected_strs = ['Accouchement', 'Post-partum', 'Gynécologie']
        actual_strs = [str(cadre) for cadre in cadres]
        
        self.assertEqual(actual_strs, expected_strs)
    
    def test_required_fields(self):
        """Test des champs obligatoires"""
        from django.core.exceptions import ValidationError
        
        # Test sans label - valider au niveau modèle
        cadre_no_label = CadreExercice(
            description='Description sans label'
        )
        with self.assertRaises(ValidationError):
            cadre_no_label.full_clean()
        
        # Test sans description - valider au niveau modèle
        cadre_no_description = CadreExercice(
            label='Label sans description'
        )
        with self.assertRaises(ValidationError):
            cadre_no_description.full_clean()
    
    def test_label_max_length(self):
        """Test de la longueur maximale du label (200 caractères)"""
        long_label = 'A' * 200  # Exactement 200 caractères
        cadre = CadreExercice.objects.create(
            label=long_label,
            description='Description valide'
        )
        self.assertEqual(cadre.label, long_label)
        
        # Test dépassement de la limite
        too_long_label = 'A' * 201  # 201 caractères
        with self.assertRaises(Exception):
            CadreExercice.objects.create(
                label=too_long_label,
                description='Description valide'
            )
    
    def test_description_text_field(self):
        """Test que description peut contenir de longs textes"""
        long_description = 'Description très longue ' * 100  # Texte très long
        cadre = CadreExercice.objects.create(
            label='Test description longue',
            description=long_description
        )
        self.assertEqual(cadre.description, long_description)
    
    def test_ordering_by_label(self):
        """Test du tri par label"""
        # Créer des cadres dans un ordre différent de l'ordre alphabétique
        cadre_z = CadreExercice.objects.create(
            label='Zythologie',
            description='Description Z'
        )
        cadre_a = CadreExercice.objects.create(
            label='Anatomie',
            description='Description A'
        )
        cadre_m = CadreExercice.objects.create(
            label='Maternité',
            description='Description M'
        )
        
        # Récupérer tous les cadres dans l'ordre par défaut
        cadres = list(CadreExercice.objects.all())
        
        # Vérifier l'ordre alphabétique
        labels = [cadre.label for cadre in cadres]
        expected_labels = ['Anatomie', 'Maternité', 'Suivi de grossesse', 'Zythologie']
        self.assertEqual(labels, expected_labels)
    
    def test_meta_verbose_names(self):
        """Test des noms verbose du modèle"""
        self.assertEqual(CadreExercice._meta.verbose_name, "4.1 Cadre d'exercice")
        self.assertEqual(CadreExercice._meta.verbose_name_plural, "4.1 Cadres d'exercice")
    
    def test_timestamps(self):
        """Test des timestamps created_at et updated_at"""
        # Vérifier que created_at est défini
        self.assertIsNotNone(self.cadre_exercice.created_at)
        self.assertIsNotNone(self.cadre_exercice.updated_at)
        
        # Vérifier que created_at et updated_at sont identiques à la création
        self.assertEqual(
            self.cadre_exercice.created_at.replace(microsecond=0),
            self.cadre_exercice.updated_at.replace(microsecond=0)
        )
        
        # Modifier le cadre et vérifier que updated_at change
        original_updated_at = self.cadre_exercice.updated_at
        
        # Attendre un peu pour s'assurer que le timestamp change
        import time
        time.sleep(0.01)
        
        self.cadre_exercice.description = 'Description modifiée'
        self.cadre_exercice.save()
        
        self.assertGreater(self.cadre_exercice.updated_at, original_updated_at)
    
    def test_unique_constraints(self):
        """Test qu'il n'y a pas de contrainte d'unicité sur label"""
        # Créer deux cadres avec le même label (devrait être autorisé)
        cadre1 = CadreExercice.objects.create(
            label='Consultation',
            description='Description 1'
        )
        cadre2 = CadreExercice.objects.create(
            label='Consultation',
            description='Description 2'
        )
        
        # Vérifier que les deux sont bien créés
        self.assertEqual(CadreExercice.objects.filter(label='Consultation').count(), 2)
        self.assertNotEqual(cadre1.id, cadre2.id)
    
    def test_deletion(self):
        """Test de la suppression d'un cadre d'exercice"""
        cadre_id = self.cadre_exercice.id
        self.cadre_exercice.delete()
        
        with self.assertRaises(CadreExercice.DoesNotExist):
            CadreExercice.objects.get(id=cadre_id)
    
    def test_update_fields(self):
        """Test de la modification des champs"""
        original_label = self.cadre_exercice.label
        original_description = self.cadre_exercice.description
        
        # Modifier les champs
        self.cadre_exercice.label = 'Nouveau label'
        self.cadre_exercice.description = 'Nouvelle description'
        self.cadre_exercice.save()
        
        # Recharger depuis la base
        self.cadre_exercice.refresh_from_db()
        
        # Vérifier les modifications
        self.assertEqual(self.cadre_exercice.label, 'Nouveau label')
        self.assertEqual(self.cadre_exercice.description, 'Nouvelle description')
        self.assertNotEqual(self.cadre_exercice.label, original_label)
        self.assertNotEqual(self.cadre_exercice.description, original_description)
    
    def test_field_help_texts(self):
        """Test des textes d'aide des champs"""
        label_field = CadreExercice._meta.get_field('label')
        description_field = CadreExercice._meta.get_field('description')
        
        self.assertEqual(label_field.help_text, "Nom du cadre d'exercice")
        self.assertEqual(description_field.help_text, "Description détaillée du cadre d'exercice")
    
    def test_field_verbose_names(self):
        """Test des noms verbose des champs"""
        label_field = CadreExercice._meta.get_field('label')
        description_field = CadreExercice._meta.get_field('description')
        created_at_field = CadreExercice._meta.get_field('created_at')
        updated_at_field = CadreExercice._meta.get_field('updated_at')
        
        self.assertEqual(label_field.verbose_name, 'Label')
        self.assertEqual(description_field.verbose_name, 'Description')
        self.assertEqual(created_at_field.verbose_name, 'Créé le')
        self.assertEqual(updated_at_field.verbose_name, 'Modifié le')


class CadreExerciceIntegrationTests(TestCase):
    """Tests d'intégration pour le modèle CadreExercice"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.cadre1 = CadreExercice.objects.create(
            label='Prénatal',
            description='Suivi prénatal complet'
        )
        self.cadre2 = CadreExercice.objects.create(
            label='Postnatal',
            description='Suivi postnatal et rééducation'
        )
    
    def test_multiple_cadres_creation(self):
        """Test de création de multiples cadres d'exercice"""
        cadres_data = [
            {'label': 'Urgences', 'description': 'Prise en charge des urgences obstétricales'},
            {'label': 'Préparation', 'description': 'Préparation à la naissance et à la parentalité'},
            {'label': 'Rééducation', 'description': 'Rééducation périnéale et abdominale'},
        ]
        
        for data in cadres_data:
            CadreExercice.objects.create(**data)
        
        # Vérifier que tous les cadres ont été créés
        total_count = CadreExercice.objects.count()
        self.assertEqual(total_count, 5)  # 2 du setUp + 3 créés
        
        # Vérifier l'ordre alphabétique
        all_labels = list(CadreExercice.objects.values_list('label', flat=True))
        expected_order = ['Postnatal', 'Prénatal', 'Préparation', 'Rééducation', 'Urgences']
        self.assertEqual(all_labels, expected_order)
    
    def test_cascade_relationships(self):
        """Test que la suppression d'un cadre n'affecte pas les autres"""
        initial_count = CadreExercice.objects.count()
        
        # Supprimer un cadre
        self.cadre1.delete()
        
        # Vérifier que seul ce cadre a été supprimé
        self.assertEqual(CadreExercice.objects.count(), initial_count - 1)
        
        # Vérifier que l'autre cadre existe toujours
        self.assertTrue(CadreExercice.objects.filter(id=self.cadre2.id).exists())
    
    def test_bulk_operations(self):
        """Test des opérations en lot"""
        # Création en lot
        cadres_data = [
            CadreExercice(label=f'Cadre {i}', description=f'Description {i}') 
            for i in range(5)
        ]
        CadreExercice.objects.bulk_create(cadres_data)
        
        # Vérifier que tous ont été créés
        self.assertEqual(CadreExercice.objects.count(), 7)  # 2 du setUp + 5 créés
        
        # Mise à jour en lot
        CadreExercice.objects.filter(label__startswith='Cadre').update(
            description='Description mise à jour en lot'
        )
        
        # Vérifier la mise à jour
        updated_count = CadreExercice.objects.filter(
            description='Description mise à jour en lot'
        ).count()
        self.assertEqual(updated_count, 5)
    
    def test_search_and_filtering(self):
        """Test de recherche et filtrage"""
        # Créer des cadres avec des caractéristiques spécifiques
        CadreExercice.objects.create(
            label='Gynécologie préventive',
            description='Consultation de prévention en gynécologie'
        )
        CadreExercice.objects.create(
            label='Gynécologie thérapeutique',
            description='Traitement des pathologies gynécologiques'
        )
        
        # Test filtrage par label contenant un terme
        gyno_cadres = CadreExercice.objects.filter(label__icontains='gynécologie')
        self.assertEqual(gyno_cadres.count(), 2)
        
        # Test filtrage par description contenant un terme
        prevention_cadres = CadreExercice.objects.filter(description__icontains='prévention')
        self.assertEqual(prevention_cadres.count(), 1)
        
        # Test recherche complexe
        from django.db.models import Q
        complexe_search = CadreExercice.objects.filter(
            Q(label__icontains='postnatal') | Q(description__icontains='rééducation')
        )
        self.assertEqual(complexe_search.count(), 1)  # Doit trouver le cadre "Postnatal"
    
    def test_model_field_constraints(self):
        """Test des contraintes de champs du modèle"""
        # Test avec des espaces en début et fin (devrait être accepté)
        cadre_spaces = CadreExercice.objects.create(
            label='  Label avec espaces  ',
            description='  Description avec espaces  '
        )
        self.assertEqual(cadre_spaces.label, '  Label avec espaces  ')
        
        # Test avec caractères spéciaux
        cadre_special = CadreExercice.objects.create(
            label='Label avec éàçèê & caractères spéciaux !@#',
            description='Description avec émojis 🤱 et caractères spéciaux'
        )
        self.assertIn('éàçèê', cadre_special.label)
        self.assertIn('🤱', cadre_special.description)
    
    def test_performance_with_large_dataset(self):
        """Test de performance avec un jeu de données plus important"""
        import time
        
        # Créer un lot de cadres d'exercice
        start_time = time.time()
        
        cadres_batch = []
        for i in range(100):
            cadres_batch.append(
                CadreExercice(
                    label=f'Cadre Performance {i:03d}',
                    description=f'Description détaillée pour le cadre numéro {i}'
                )
            )
        
        CadreExercice.objects.bulk_create(cadres_batch)
        creation_time = time.time() - start_time
        
        # Vérifier que la création s'est bien passée
        self.assertEqual(CadreExercice.objects.count(), 102)  # 2 du setUp + 100 créés
        
        # Test de requête sur le grand dataset
        start_time = time.time()
        filtered_cadres = CadreExercice.objects.filter(
            label__icontains='Performance'
        ).order_by('label')
        query_time = time.time() - start_time
        
        self.assertEqual(filtered_cadres.count(), 100)
        
        # Les temps ne devraient pas être excessifs (limite généreuse pour les tests)
        self.assertLess(creation_time, 5.0)  # Création en moins de 5 secondes
        self.assertLess(query_time, 1.0)     # Requête en moins de 1 seconde