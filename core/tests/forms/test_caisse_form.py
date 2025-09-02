"""
Tests pour les formulaires des caisses et conditions de paiement.
"""
from django.test import TestCase
from decimal import Decimal

from core.views.administration import CaisseForm, ConditionPaiementForm
from core.models.caisse import Caisse
from core.models.condition_paiement import ConditionPaiement


class CaisseFormTests(TestCase):
    """Tests pour le formulaire CaisseForm"""
    
    def setUp(self):
        """Configuration de base pour tous les tests"""
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
        
        self.valid_data = {
            'nom': 'CAFAT Nouvelle-Calédonie',
            'conditions_paiement_eligibles': [self.condition1.pk, self.condition2.pk]
        }
    
    def test_form_valide_avec_donnees_completes(self):
        """Test du formulaire avec toutes les données valides"""
        form = CaisseForm(data=self.valid_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)
    
    def test_form_nom_obligatoire(self):
        """Test que le nom est obligatoire"""
        data = self.valid_data.copy()
        del data['nom']
        
        form = CaisseForm(data=data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('nom', form.errors)
    
    def test_form_conditions_optionnelles(self):
        """Test que les conditions de paiement sont optionnelles"""
        data = {'nom': 'Caisse sans conditions'}
        
        form = CaisseForm(data=data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)
    
    def test_form_conditions_vides(self):
        """Test avec une liste vide de conditions"""
        data = {
            'nom': 'Caisse vide',
            'conditions_paiement_eligibles': []
        }
        
        form = CaisseForm(data=data)
        
        self.assertTrue(form.is_valid())
    
    def test_form_une_seule_condition(self):
        """Test avec une seule condition sélectionnée"""
        data = {
            'nom': 'Caisse unique',
            'conditions_paiement_eligibles': [self.condition1.pk]
        }
        
        form = CaisseForm(data=data)
        
        self.assertTrue(form.is_valid())
        
        # Vérifier la sauvegarde
        caisse = form.save()
        self.assertEqual(caisse.conditions_paiement_eligibles.count(), 1)
        self.assertEqual(caisse.conditions_paiement_eligibles.first(), self.condition1)
    
    def test_form_toutes_conditions_selectionnees(self):
        """Test avec toutes les conditions sélectionnées"""
        data = {
            'nom': 'Caisse complète',
            'conditions_paiement_eligibles': [
                self.condition1.pk, self.condition2.pk, self.condition3.pk
            ]
        }
        
        form = CaisseForm(data=data)
        
        self.assertTrue(form.is_valid())
        
        # Vérifier la sauvegarde
        caisse = form.save()
        self.assertEqual(caisse.conditions_paiement_eligibles.count(), 3)
    
    def test_form_condition_inexistante(self):
        """Test avec un ID de condition inexistant"""
        data = {
            'nom': 'Caisse test',
            'conditions_paiement_eligibles': [99999]  # ID inexistant
        }
        
        form = CaisseForm(data=data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('conditions_paiement_eligibles', form.errors)
    
    def test_form_fields_included(self):
        """Test que tous les champs nécessaires sont inclus"""
        form = CaisseForm()
        
        expected_fields = ['nom', 'conditions_paiement_eligibles']
        
        for field in expected_fields:
            self.assertIn(field, form.fields, f"Le champ '{field}' devrait être dans le formulaire")
    
    def test_form_css_classes(self):
        """Test que les champs ont les bonnes classes CSS"""
        form = CaisseForm()
        
        # Vérifier la classe CSS du champ nom
        expected_css_class = 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'
        self.assertIn(expected_css_class, form.fields['nom'].widget.attrs.get('class', ''))
        
        # Vérifier le widget CheckboxSelectMultiple
        from django import forms
        self.assertIsInstance(form.fields['conditions_paiement_eligibles'].widget, forms.CheckboxSelectMultiple)
    
    def test_form_widget_attributes(self):
        """Test des attributs du widget conditions_paiement_eligibles"""
        form = CaisseForm()
        
        widget = form.fields['conditions_paiement_eligibles'].widget
        expected_css_class = 'text-primary focus:ring-primary'
        
        # Vérifier que le widget a les bonnes classes CSS
        self.assertEqual(widget.attrs.get('class'), expected_css_class)
    
    def test_form_sauvegarde_nouvelle_instance(self):
        """Test de création d'une nouvelle instance"""
        form = CaisseForm(data=self.valid_data)
        
        self.assertTrue(form.is_valid())
        
        # Sauvegarder
        caisse = form.save()
        
        self.assertIsNotNone(caisse.pk)
        self.assertEqual(caisse.nom, 'CAFAT Nouvelle-Calédonie')
        self.assertEqual(caisse.conditions_paiement_eligibles.count(), 2)
        
        # Vérifier les conditions associées
        conditions = list(caisse.conditions_paiement_eligibles.all())
        self.assertIn(self.condition1, conditions)
        self.assertIn(self.condition2, conditions)
    
    def test_form_modification_instance_existante(self):
        """Test de modification d'une instance existante"""
        # Créer d'abord une caisse
        caisse = Caisse.objects.create(nom='Caisse originale')
        caisse.conditions_paiement_eligibles.add(self.condition1)
        
        # Modifier ses données
        new_data = {
            'nom': 'Caisse modifiée',
            'conditions_paiement_eligibles': [self.condition2.pk, self.condition3.pk]
        }
        
        form = CaisseForm(data=new_data, instance=caisse)
        
        self.assertTrue(form.is_valid())
        
        # Sauvegarder
        updated_caisse = form.save()
        
        self.assertEqual(updated_caisse.pk, caisse.pk)
        self.assertEqual(updated_caisse.nom, 'Caisse modifiée')
        self.assertEqual(updated_caisse.conditions_paiement_eligibles.count(), 2)
        
        # Vérifier que les bonnes conditions sont associées
        conditions = list(updated_caisse.conditions_paiement_eligibles.all())
        self.assertIn(self.condition2, conditions)
        self.assertIn(self.condition3, conditions)
        self.assertNotIn(self.condition1, conditions)
    
    def test_form_nom_trop_long(self):
        """Test avec un nom dépassant la limite"""
        data = {
            'nom': 'x' * 201,  # Dépasse la limite de 200 caractères
            'conditions_paiement_eligibles': []
        }
        
        form = CaisseForm(data=data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('nom', form.errors)
    
    def test_form_queryset_conditions(self):
        """Test du queryset des conditions de paiement"""
        form = CaisseForm()
        
        # Le queryset devrait contenir toutes les conditions existantes
        queryset = form.fields['conditions_paiement_eligibles'].queryset
        
        self.assertIn(self.condition1, queryset)
        self.assertIn(self.condition2, queryset)
        self.assertIn(self.condition3, queryset)
        self.assertEqual(queryset.count(), 3)


class ConditionPaiementFormTests(TestCase):
    """Tests pour le formulaire ConditionPaiementForm"""
    
    def setUp(self):
        """Configuration de base pour tous les tests"""
        self.valid_data = {
            'designation': 'Test Condition',
            'pourcentage': Decimal('75.50')
        }
    
    def test_form_valide_avec_donnees_completes(self):
        """Test du formulaire avec toutes les données valides"""
        form = ConditionPaiementForm(data=self.valid_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)
    
    def test_form_champs_obligatoires(self):
        """Test que les champs obligatoires sont requis"""
        champs_obligatoires = ['designation', 'pourcentage']
        
        for champ in champs_obligatoires:
            data = self.valid_data.copy()
            del data[champ]
            
            form = ConditionPaiementForm(data=data)
            
            self.assertFalse(form.is_valid(), f"Le formulaire devrait être invalide sans le champ '{champ}'")
            self.assertIn(champ, form.errors, f"Le champ '{champ}' devrait avoir une erreur")
    
    def test_form_pourcentage_zero(self):
        """Test avec un pourcentage de 0"""
        data = self.valid_data.copy()
        data['pourcentage'] = Decimal('0.00')
        
        form = ConditionPaiementForm(data=data)
        
        self.assertTrue(form.is_valid())
    
    def test_form_pourcentage_cent(self):
        """Test avec un pourcentage de 100%"""
        data = self.valid_data.copy()
        data['pourcentage'] = Decimal('100.00')
        
        form = ConditionPaiementForm(data=data)
        
        self.assertTrue(form.is_valid())
    
    def test_form_pourcentage_decimal(self):
        """Test avec des décimales dans le pourcentage"""
        data = self.valid_data.copy()
        data['pourcentage'] = Decimal('33.33')
        
        form = ConditionPaiementForm(data=data)
        
        self.assertTrue(form.is_valid())
        
        # Vérifier la sauvegarde
        condition = form.save()
        self.assertEqual(condition.pourcentage, Decimal('33.33'))
    
    def test_form_fields_included(self):
        """Test que tous les champs nécessaires sont inclus"""
        form = ConditionPaiementForm()
        
        expected_fields = ['designation', 'pourcentage']
        
        for field in expected_fields:
            self.assertIn(field, form.fields, f"Le champ '{field}' devrait être dans le formulaire")
    
    def test_form_css_classes(self):
        """Test que les champs ont les bonnes classes CSS"""
        form = ConditionPaiementForm()
        
        expected_css_class = 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'
        
        self.assertIn(expected_css_class, form.fields['designation'].widget.attrs.get('class', ''))
        self.assertIn(expected_css_class, form.fields['pourcentage'].widget.attrs.get('class', ''))
    
    def test_form_widget_types(self):
        """Test des types de widgets"""
        form = ConditionPaiementForm()
        
        from django import forms
        
        self.assertIsInstance(form.fields['designation'].widget, forms.TextInput)
        self.assertIsInstance(form.fields['pourcentage'].widget, forms.NumberInput)
    
    def test_form_sauvegarde_nouvelle_instance(self):
        """Test de création d'une nouvelle instance"""
        form = ConditionPaiementForm(data=self.valid_data)
        
        self.assertTrue(form.is_valid())
        
        # Sauvegarder
        condition = form.save()
        
        self.assertIsNotNone(condition.pk)
        self.assertEqual(condition.designation, 'Test Condition')
        self.assertEqual(condition.pourcentage, Decimal('75.50'))
    
    def test_form_modification_instance_existante(self):
        """Test de modification d'une instance existante"""
        # Créer d'abord une condition
        condition = ConditionPaiement.objects.create(
            designation='Condition originale',
            pourcentage=Decimal('50.00')
        )
        
        # Modifier ses données
        new_data = {
            'designation': 'Condition modifiée',
            'pourcentage': Decimal('90.00')
        }
        
        form = ConditionPaiementForm(data=new_data, instance=condition)
        
        self.assertTrue(form.is_valid())
        
        # Sauvegarder
        updated_condition = form.save()
        
        self.assertEqual(updated_condition.pk, condition.pk)
        self.assertEqual(updated_condition.designation, 'Condition modifiée')
        self.assertEqual(updated_condition.pourcentage, Decimal('90.00'))
    
    def test_form_designation_trop_longue(self):
        """Test avec une désignation dépassant la limite"""
        data = {
            'designation': 'x' * 201,  # Dépasse la limite de 200 caractères
            'pourcentage': Decimal('50.00')
        }
        
        form = ConditionPaiementForm(data=data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('designation', form.errors)
    
    def test_form_pourcentage_widget_attributes(self):
        """Test des attributs spécifiques du widget pourcentage"""
        form = ConditionPaiementForm()
        
        widget = form.fields['pourcentage'].widget
        
        # Vérifier les attributs min, max, step
        self.assertEqual(widget.attrs.get('min'), '0')
        self.assertEqual(widget.attrs.get('max'), '100')
        self.assertEqual(widget.attrs.get('step'), '0.01')


class FormIntegrationTests(TestCase):
    """Tests d'intégration entre les formulaires"""
    
    def setUp(self):
        """Configuration pour les tests d'intégration"""
        self.condition = ConditionPaiement.objects.create(
            designation='Integration Test',
            pourcentage=Decimal('80.00')
        )
    
    def test_creation_caisse_avec_nouvelle_condition(self):
        """Test de création d'une caisse avec une condition nouvellement créée"""
        # Créer d'abord une nouvelle condition via le formulaire
        condition_data = {
            'designation': 'Nouvelle condition pour caisse',
            'pourcentage': Decimal('60.00')
        }
        
        condition_form = ConditionPaiementForm(data=condition_data)
        self.assertTrue(condition_form.is_valid())
        
        nouvelle_condition = condition_form.save()
        
        # Créer maintenant une caisse avec cette condition
        caisse_data = {
            'nom': 'Caisse avec nouvelle condition',
            'conditions_paiement_eligibles': [nouvelle_condition.pk, self.condition.pk]
        }
        
        caisse_form = CaisseForm(data=caisse_data)
        self.assertTrue(caisse_form.is_valid())
        
        caisse = caisse_form.save()
        
        # Vérifier que les relations sont correctes
        self.assertEqual(caisse.conditions_paiement_eligibles.count(), 2)
        self.assertIn(nouvelle_condition, caisse.conditions_paiement_eligibles.all())
        self.assertIn(self.condition, caisse.conditions_paiement_eligibles.all())
    
    def test_modification_condition_utilisee_par_caisse(self):
        """Test de modification d'une condition utilisée par une caisse"""
        # Créer une caisse avec la condition
        caisse = Caisse.objects.create(nom='Caisse test')
        caisse.conditions_paiement_eligibles.add(self.condition)
        
        # Modifier la condition
        new_data = {
            'designation': 'Condition modifiée',
            'pourcentage': Decimal('85.00')
        }
        
        form = ConditionPaiementForm(data=new_data, instance=self.condition)
        self.assertTrue(form.is_valid())
        
        updated_condition = form.save()
        
        # Vérifier que la caisse utilise toujours la condition modifiée
        caisse.refresh_from_db()
        condition_from_caisse = caisse.conditions_paiement_eligibles.first()
        
        self.assertEqual(condition_from_caisse.pk, updated_condition.pk)
        self.assertEqual(condition_from_caisse.designation, 'Condition modifiée')
        self.assertEqual(condition_from_caisse.pourcentage, Decimal('85.00'))