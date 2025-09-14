"""
Tests pour les formulaires de ConsultationPreparationNaissance
"""

from django.test import TestCase
from django.forms import ValidationError
from datetime import date, timedelta

from core.forms.consultation_preparation_naissance import (
    ConsultationPreparationNaissanceForm,
    ConsultationPreparationNaissanceModalForm,
    ConsultationPreparationNaissanceQuickForm,
    ConsultationPreparationNaissanceSearchForm
)
from core.models import Patient, SageFemme, Caisse, ConditionPaiement


class ConsultationPreparationNaissanceFormTest(TestCase):
    """Tests pour ConsultationPreparationNaissanceForm"""
    
    def setUp(self):
        """Configuration pour chaque test"""
        # Créer une caisse et condition de paiement
        self.condition = ConditionPaiement.objects.create(
            designation="Test Condition",
            pourcentage=70
        )
        self.caisse = Caisse.objects.create(
            nom="CAFAT"
        )
        self.caisse.conditions_paiement_eligibles.add(self.condition)
        
        # Créer une patiente femme
        self.patiente = Patient.objects.create(
            nom="Martin",
            prenom="Julie",
            date_naissance=date(1990, 5, 15),
            telephone="0123456789",
            type_patient="femme",
            caisse=self.caisse,
            date_debut_grossesse=date(2024, 1, 1)
        )
        
        # Créer un patient bébé
        self.bebe = Patient.objects.create(
            nom="Martin",
            prenom="Lucas",
            date_naissance=date(2024, 6, 1),
            type_patient="bebe",
            caisse=self.caisse,
            mere=self.patiente
        )
        
        # Patiente inactive
        self.patiente_inactive = Patient.objects.create(
            nom="Dubois",
            prenom="Sophie",
            date_naissance=date(1992, 3, 20),
            telephone="0123456790",
            type_patient="femme",
            caisse=self.caisse,
            is_active=False
        )
    
    def test_form_fields_present(self):
        """Test présence des champs requis"""
        form = ConsultationPreparationNaissanceForm()
        
        expected_fields = ['patient', 'date_consultation', 'theme_aborde', 'a_prevoir']
        self.assertEqual(list(form.fields.keys()), expected_fields)
    
    def test_form_labels(self):
        """Test des labels des champs"""
        form = ConsultationPreparationNaissanceForm()
        
        self.assertEqual(form.fields['patient'].label, 'Patiente')
        self.assertEqual(form.fields['date_consultation'].label, 'Date de consultation')
        self.assertEqual(form.fields['theme_aborde'].label, 'Thème(s) abordé(s)')
        self.assertEqual(form.fields['a_prevoir'].label, 'À prévoir')
    
    def test_form_help_texts(self):
        """Test des textes d'aide"""
        form = ConsultationPreparationNaissanceForm()
        
        self.assertIn('aujourd\'hui', form.fields['date_consultation'].help_text)
        self.assertIn('consultation', form.fields['theme_aborde'].help_text)
        self.assertIn('accouchement', form.fields['a_prevoir'].help_text)
    
    def test_form_widgets_classes(self):
        """Test des classes CSS des widgets"""
        form = ConsultationPreparationNaissanceForm()
        
        # Vérifier les classes focus:ring-green-500
        for field_name in ['patient', 'date_consultation', 'theme_aborde', 'a_prevoir']:
            widget_class = form.fields[field_name].widget.attrs.get('class', '')
            self.assertIn('focus:ring-green-500', widget_class)
    
    def test_patient_queryset_filtrage(self):
        """Test filtrage du queryset des patients"""
        form = ConsultationPreparationNaissanceForm()
        
        # Seules les femmes actives doivent être disponibles
        patients = form.fields['patient'].queryset
        self.assertIn(self.patiente, patients)
        self.assertNotIn(self.bebe, patients)
        self.assertNotIn(self.patiente_inactive, patients)
    
    def test_date_consultation_default(self):
        """Test valeur par défaut de la date"""
        form = ConsultationPreparationNaissanceForm()
        
        self.assertEqual(form.fields['date_consultation'].initial, date.today())
    
    def test_date_consultation_max_attribute(self):
        """Test attribut max de la date"""
        form = ConsultationPreparationNaissanceForm()
        
        max_date = form.fields['date_consultation'].widget.attrs.get('max')
        self.assertEqual(max_date, date.today().isoformat())
    
    def test_valid_form_data(self):
        """Test formulaire valide"""
        form_data = {
            'patient': self.patiente.id,
            'date_consultation': date.today(),
            'theme_aborde': 'Respiration et relaxation',
            'a_prevoir': 'Revoir les exercices'
        }
        
        form = ConsultationPreparationNaissanceForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_valid_form_minimal_data(self):
        """Test formulaire valide avec données minimales"""
        form_data = {
            'patient': self.patiente.id,
            'date_consultation': date.today()
        }
        
        form = ConsultationPreparationNaissanceForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_date_future_invalid(self):
        """Test date future invalide"""
        form_data = {
            'patient': self.patiente.id,
            'date_consultation': date.today() + timedelta(days=1),
            'theme_aborde': 'Test futur'
        }
        
        form = ConsultationPreparationNaissanceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_consultation', form.errors)
        self.assertIn('futur', form.errors['date_consultation'][0])
    
    def test_missing_required_fields(self):
        """Test champs requis manquants"""
        form = ConsultationPreparationNaissanceForm(data={})
        
        self.assertFalse(form.is_valid())
        self.assertIn('patient', form.errors)
        self.assertIn('date_consultation', form.errors)
    
    def test_save_method(self):
        """Test méthode save"""
        form_data = {
            'patient': self.patiente.id,
            'date_consultation': date.today(),
            'theme_aborde': 'Test save'
        }
        
        form = ConsultationPreparationNaissanceForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        consultation = form.save()
        self.assertEqual(consultation.patient, self.patiente)
        self.assertEqual(consultation.theme_aborde, 'Test save')


class ConsultationPreparationNaissanceModalFormTest(TestCase):
    """Tests pour ConsultationPreparationNaissanceModalForm"""
    
    def setUp(self):
        """Configuration pour chaque test"""
        # Créer une caisse et condition de paiement
        self.condition = ConditionPaiement.objects.create(
            designation="Test Condition",
            pourcentage=70
        )
        self.caisse = Caisse.objects.create(
            nom="CAFAT"
        )
        self.caisse.conditions_paiement_eligibles.add(self.condition)
        
        # Créer une patiente femme
        self.patiente = Patient.objects.create(
            nom="Martin",
            prenom="Julie",
            date_naissance=date(1990, 5, 15),
            telephone="0123456789",
            type_patient="femme",
            caisse=self.caisse,
        )
    
    def test_patient_hidden_avec_patient_id(self):
        """Test masquage du champ patient avec patient_id"""
        form = ConsultationPreparationNaissanceModalForm(patient_id=self.patiente.id)
        
        # Le champ patient devrait être masqué
        self.assertEqual(form.fields['patient'].widget.__class__.__name__, 'HiddenInput')
        self.assertEqual(form.fields['patient'].initial, self.patiente)
    
    def test_patient_visible_sans_patient_id(self):
        """Test champ patient visible sans patient_id"""
        form = ConsultationPreparationNaissanceModalForm()
        
        # Le champ patient devrait être visible
        self.assertNotEqual(form.fields['patient'].widget.__class__.__name__, 'HiddenInput')
    
    def test_patient_id_inexistant(self):
        """Test avec patient_id inexistant"""
        form = ConsultationPreparationNaissanceModalForm(patient_id=99999)
        
        # Ne devrait pas lever d'exception
        self.assertEqual(form.fields['patient'].widget.__class__.__name__, 'HiddenInput')
        self.assertIsNone(form.fields['patient'].initial)
    
    def test_css_classes_modal(self):
        """Test classes CSS adaptées pour modal"""
        form = ConsultationPreparationNaissanceModalForm(patient_id=self.patiente.id)
        
        # Vérifier que les classes CSS sont appropriées pour un modal
        for field_name, field in form.fields.items():
            if field_name != 'patient' and hasattr(field.widget, 'attrs'):
                widget_class = field.widget.attrs.get('class', '')
                self.assertIn('focus:ring-green-500', widget_class)


class ConsultationPreparationNaissanceQuickFormTest(TestCase):
    """Tests pour ConsultationPreparationNaissanceQuickForm"""
    
    def setUp(self):
        """Configuration pour chaque test"""
        # Créer une caisse et condition de paiement
        self.condition = ConditionPaiement.objects.create(
            designation="Test Condition",
            pourcentage=70
        )
        self.caisse = Caisse.objects.create(
            nom="CAFAT"
        )
        self.caisse.conditions_paiement_eligibles.add(self.condition)
        
        # Créer une patiente femme
        self.patiente = Patient.objects.create(
            nom="Martin",
            prenom="Julie",
            date_naissance=date(1990, 5, 15),
            telephone="0123456789",
            type_patient="femme",
            caisse=self.caisse,
        )
        
        # Créer un patient bébé
        self.bebe = Patient.objects.create(
            nom="Martin",
            prenom="Lucas",
            date_naissance=date(2024, 6, 1),
            type_patient="bebe",
            caisse=self.caisse,
            mere=self.patiente
        )
    
    def test_form_fields_quick(self):
        """Test champs du formulaire rapide"""
        form = ConsultationPreparationNaissanceQuickForm()
        
        expected_fields = ['date_consultation', 'theme_aborde', 'a_prevoir']
        self.assertEqual(list(form.fields.keys()), expected_fields)
    
    def test_form_labels_quick(self):
        """Test labels simplifiés"""
        form = ConsultationPreparationNaissanceQuickForm()
        
        self.assertEqual(form.fields['date_consultation'].label, 'Date')
        self.assertEqual(form.fields['theme_aborde'].label, 'Thème(s) abordé(s)')
        self.assertEqual(form.fields['a_prevoir'].label, 'À prévoir')
    
    def test_form_widgets_purple_classes(self):
        """Test classes CSS violettes pour quick form"""
        form = ConsultationPreparationNaissanceQuickForm()
        
        # Vérifier les classes focus:ring-purple-400
        for field_name in ['date_consultation', 'theme_aborde', 'a_prevoir']:
            widget_class = form.fields[field_name].widget.attrs.get('class', '')
            self.assertIn('focus:ring-purple-400', widget_class)
    
    def test_date_default_today(self):
        """Test date par défaut aujourd'hui"""
        form = ConsultationPreparationNaissanceQuickForm()
        
        self.assertEqual(form.fields['date_consultation'].initial, date.today())
    
    def test_patient_assignment(self):
        """Test assignation du patient"""
        form = ConsultationPreparationNaissanceQuickForm(patient=self.patiente)
        
        self.assertEqual(form.patient, self.patiente)
    
    def test_valid_quick_form(self):
        """Test formulaire rapide valide"""
        form_data = {
            'date_consultation': date.today(),
            'theme_aborde': 'Respiration',
            'a_prevoir': 'Exercices'
        }
        
        form = ConsultationPreparationNaissanceQuickForm(data=form_data, patient=self.patiente)
        self.assertTrue(form.is_valid())
    
    def test_validation_patient_bebe(self):
        """Test validation avec patient bébé"""
        form_data = {
            'date_consultation': date.today(),
            'theme_aborde': 'Test bébé'
        }
        
        form = ConsultationPreparationNaissanceQuickForm(data=form_data, patient=self.bebe)
        self.assertFalse(form.is_valid())
        self.assertIn('femmes', str(form.errors['__all__']))
    
    def test_date_future_invalid_quick(self):
        """Test date future invalide dans quick form"""
        form_data = {
            'date_consultation': date.today() + timedelta(days=1),
            'theme_aborde': 'Test futur'
        }
        
        form = ConsultationPreparationNaissanceQuickForm(data=form_data, patient=self.patiente)
        self.assertFalse(form.is_valid())
        self.assertIn('date_consultation', form.errors)
    
    def test_save_with_patient_assignment(self):
        """Test sauvegarde avec assignation du patient"""
        form_data = {
            'date_consultation': date.today(),
            'theme_aborde': 'Test save quick'
        }
        
        form = ConsultationPreparationNaissanceQuickForm(data=form_data, patient=self.patiente)
        self.assertTrue(form.is_valid())
        
        consultation = form.save()
        self.assertEqual(consultation.patient, self.patiente)
        self.assertEqual(consultation.theme_aborde, 'Test save quick')
    
    def test_save_commit_false(self):
        """Test sauvegarde avec commit=False"""
        form_data = {
            'date_consultation': date.today(),
            'theme_aborde': 'Test commit false'
        }
        
        form = ConsultationPreparationNaissanceQuickForm(data=form_data, patient=self.patiente)
        self.assertTrue(form.is_valid())
        
        consultation = form.save(commit=False)
        self.assertEqual(consultation.patient, self.patiente)
        self.assertIsNone(consultation.pk)  # Pas encore sauvegardé en base
    
    def test_duplicate_save_method_removed(self):
        """Test que la méthode save dupliquée est gérée correctement"""
        # Le formulaire a deux méthodes save dans le code original
        # Vérifier que cela fonctionne quand même
        form_data = {
            'date_consultation': date.today(),
            'theme_aborde': 'Test duplicate save'
        }
        
        form = ConsultationPreparationNaissanceQuickForm(data=form_data, patient=self.patiente)
        self.assertTrue(form.is_valid())
        
        consultation = form.save()
        self.assertEqual(consultation.patient, self.patiente)


class ConsultationPreparationNaissanceSearchFormTest(TestCase):
    """Tests pour ConsultationPreparationNaissanceSearchForm"""
    
    def test_form_fields_search(self):
        """Test champs du formulaire de recherche"""
        form = ConsultationPreparationNaissanceSearchForm()
        
        expected_fields = ['recherche', 'date_debut', 'date_fin']
        self.assertEqual(list(form.fields.keys()), expected_fields)
    
    def test_form_labels_search(self):
        """Test labels du formulaire de recherche"""
        form = ConsultationPreparationNaissanceSearchForm()
        
        self.assertEqual(form.fields['recherche'].label, 'Recherche')
        self.assertEqual(form.fields['date_debut'].label, 'Date de début')
        self.assertEqual(form.fields['date_fin'].label, 'Date de fin')
    
    def test_all_fields_optional(self):
        """Test que tous les champs sont optionnels"""
        form = ConsultationPreparationNaissanceSearchForm()
        
        for field in form.fields.values():
            self.assertFalse(field.required)
    
    def test_search_widgets_classes(self):
        """Test classes CSS des widgets de recherche"""
        form = ConsultationPreparationNaissanceSearchForm()
        
        # Vérifier les classes focus:ring-green-500
        for field_name in ['recherche', 'date_debut', 'date_fin']:
            widget_class = form.fields[field_name].widget.attrs.get('class', '')
            self.assertIn('focus:ring-green-500', widget_class)
    
    def test_recherche_placeholder(self):
        """Test placeholder du champ recherche"""
        form = ConsultationPreparationNaissanceSearchForm()
        
        placeholder = form.fields['recherche'].widget.attrs.get('placeholder', '')
        self.assertIn('nom', placeholder.lower())
        self.assertIn('thème', placeholder.lower())
    
    def test_date_widgets_type(self):
        """Test type des widgets de date"""
        form = ConsultationPreparationNaissanceSearchForm()
        
        # Vérifier que les widgets ont des attributs de date
        date_debut_widget = form.fields['date_debut'].widget
        date_fin_widget = form.fields['date_fin'].widget
        
        # Vérifier que ce sont des widgets DateInput
        from django.forms.widgets import DateInput
        self.assertIsInstance(date_debut_widget, DateInput)
        self.assertIsInstance(date_fin_widget, DateInput)
    
    def test_valid_search_form_empty(self):
        """Test formulaire de recherche vide valide"""
        form = ConsultationPreparationNaissanceSearchForm(data={})
        self.assertTrue(form.is_valid())
    
    def test_valid_search_form_with_data(self):
        """Test formulaire de recherche avec données"""
        form_data = {
            'recherche': 'respiration',
            'date_debut': date(2024, 1, 1),
            'date_fin': date(2024, 12, 31)
        }
        
        form = ConsultationPreparationNaissanceSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_valid_search_form_partial_data(self):
        """Test formulaire de recherche avec données partielles"""
        form_data = {
            'recherche': 'allaitement'
        }
        
        form = ConsultationPreparationNaissanceSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test avec seulement les dates
        form_data = {
            'date_debut': date(2024, 6, 1),
            'date_fin': date(2024, 6, 30)
        }
        
        form = ConsultationPreparationNaissanceSearchForm(data=form_data)
        self.assertTrue(form.is_valid())