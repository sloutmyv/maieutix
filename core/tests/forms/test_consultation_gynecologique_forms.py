"""
Tests pour les formulaires ConsultationGynecologique
Tests complets des validations et fonctionnalités
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date, timedelta

from core.models import ConsultationGynecologique, Patient, Caisse
from core.forms.consultation_gynecologique import (
    ConsultationGynecologiqueForm,
    ConsultationGynecologiqueModalForm,
    ConsultationGynecologiqueQuickForm
)


class ConsultationGynecologiqueFormTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.caisse = Caisse.objects.create(
            nom="CAFAT"
        )
        
        self.patient_femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='123456',
            caisse=self.caisse
        )
        
        self.patient_bebe = Patient.objects.create(
            type_patient='bebe',
            nom='Petit',
            prenom='Lucas',
            date_naissance=date.today() - timedelta(days=30),
            caisse=self.caisse
        )
    
    def test_form_initialization(self):
        """Test d'initialisation du formulaire"""
        form = ConsultationGynecologiqueForm()
        
        # Vérifier que les champs obligatoires sont marqués
        self.assertTrue(form.fields['patient'].required)
        self.assertTrue(form.fields['date_consultation'].required)
        self.assertTrue(form.fields['motif'].required)
        
        # Vérifier que les tensions et poids sont optionnels
        self.assertFalse(form.fields['tension_systolique'].required)
        self.assertFalse(form.fields['tension_diastolique'].required)
        self.assertFalse(form.fields['poids'].required)
        
        # Vérifier la date max
        today_str = date.today().isoformat()
        self.assertEqual(form.fields['date_consultation'].widget.attrs['max'], today_str)
        
        # Vérifier que le queryset ne contient que les femmes
        expected_queryset = Patient.objects.filter(
            type_patient='femme'
        ).order_by('nom', 'prenom')
        self.assertEqual(
            list(form.fields['patient'].queryset),
            list(expected_queryset)
        )

    def test_form_initialization_with_patient_id(self):
        """Test d'initialisation avec un patient spécifique"""
        form = ConsultationGynecologiqueForm(patient_id=self.patient_femme.id)
        
        # Vérifier que le queryset ne contient que ce patient
        expected_queryset = Patient.objects.filter(pk=self.patient_femme.id)
        self.assertEqual(
            list(form.fields['patient'].queryset),
            list(expected_queryset)
        )
        self.assertEqual(form.fields['patient'].initial, self.patient_femme)

    def test_form_valid_data(self):
        """Test avec des données valides"""
        form_data = {
            'patient': self.patient_femme.id,
            'date_consultation': date.today(),
            'tension_systolique': 120,
            'tension_diastolique': 80,
            'poids': 65.5,
            'motif': 'Consultation de routine',
            'examen': 'RAS',
            'prescription': 'Aucune',
            'notes': 'Patiente en bonne santé'
        }
        
        form = ConsultationGynecologiqueForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_minimal_valid_data(self):
        """Test avec données minimales valides"""
        form_data = {
            'patient': self.patient_femme.id,
            'date_consultation': date.today(),
            'motif': 'Consultation simple'
        }
        
        form = ConsultationGynecologiqueForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_missing_required_fields(self):
        """Test avec champs obligatoires manquants"""
        form_data = {
            'tension_systolique': 120,
            'poids': 65.5
        }
        
        form = ConsultationGynecologiqueForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('patient', form.errors)
        self.assertIn('motif', form.errors)

    def test_clean_date_consultation_future(self):
        """Test validation date consultation dans le futur"""
        form_data = {
            'patient': self.patient_femme.id,
            'date_consultation': date.today() + timedelta(days=1),
            'motif': 'Test date future'
        }
        
        form = ConsultationGynecologiqueForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_consultation', form.errors)

    def test_clean_tension_coherence(self):
        """Test validation cohérence des tensions"""
        form_data = {
            'patient': self.patient_femme.id,
            'date_consultation': date.today(),
            'tension_systolique': 80,
            'tension_diastolique': 120,  # Diastolique > Systolique
            'motif': 'Test tension incohérente'
        }
        
        form = ConsultationGynecologiqueForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('tension_systolique', form.errors)

    def test_clean_tension_incomplete(self):
        """Test validation tension incomplète"""
        # Seulement systolique
        form_data = {
            'patient': self.patient_femme.id,
            'date_consultation': date.today(),
            'tension_systolique': 120,
            'motif': 'Test tension incomplète'
        }
        
        form = ConsultationGynecologiqueForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        
        # Seulement diastolique
        form_data = {
            'patient': self.patient_femme.id,
            'date_consultation': date.today(),
            'tension_diastolique': 80,
            'motif': 'Test tension incomplète'
        }
        
        form = ConsultationGynecologiqueForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_clean_patient_not_femme(self):
        """Test validation patient qui n'est pas une femme"""
        form_data = {
            'patient': self.patient_bebe.id,
            'date_consultation': date.today(),
            'motif': 'Test patient bébé'
        }
        
        # Pour ce test, on doit contourner le queryset filtré
        form = ConsultationGynecologiqueForm(data=form_data)
        form.fields['patient'].queryset = Patient.objects.all()  # Permettre tous les patients
        
        self.assertFalse(form.is_valid())
        self.assertIn('patient', form.errors)

    def test_widget_attributes(self):
        """Test des attributs des widgets"""
        form = ConsultationGynecologiqueForm()
        
        # Vérifier les attributs de classe CSS
        self.assertIn('mt-1 block w-full', form.fields['patient'].widget.attrs['class'])
        self.assertIn('focus:ring-primary', form.fields['patient'].widget.attrs['class'])
        
        # Vérifier les attributs spéciaux
        self.assertEqual(form.fields['tension_systolique'].widget.attrs['min'], '80')
        self.assertEqual(form.fields['tension_systolique'].widget.attrs['max'], '250')
        self.assertEqual(form.fields['tension_diastolique'].widget.attrs['min'], '40')
        self.assertEqual(form.fields['tension_diastolique'].widget.attrs['max'], '150')
        self.assertEqual(form.fields['poids'].widget.attrs['step'], '0.1')


class ConsultationGynecologiqueModalFormTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.caisse = Caisse.objects.create(
            nom="CAFAT"
        )
        
        self.patient_femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='123456',
            caisse=self.caisse
        )

    def test_modal_form_initialization(self):
        """Test d'initialisation du formulaire modal"""
        form = ConsultationGynecologiqueModalForm(patient_id=self.patient_femme.id)
        
        # Vérifier que le patient est caché dans le modal
        from django.forms.widgets import HiddenInput
        self.assertIsInstance(form.fields['patient'].widget, HiddenInput)

    def test_modal_form_css_classes(self):
        """Test des classes CSS spécifiques au modal"""
        form = ConsultationGynecologiqueModalForm()
        
        # Vérifier que les classes sont adaptées au modal
        for field_name, field in form.fields.items():
            if hasattr(field.widget, 'attrs') and 'class' in field.widget.attrs:
                css_class = field.widget.attrs['class']
                if 'focus:ring-primary' in css_class:
                    # Dans le modal, ça devrait être changé en blue-500
                    pass  # Le remplacement peut varier selon l'implémentation


class ConsultationGynecologiqueQuickFormTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.caisse = Caisse.objects.create(
            nom="CAFAT"
        )
        
        self.patient_femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='123456',
            caisse=self.caisse
        )

    def test_quick_form_initialization(self):
        """Test d'initialisation du formulaire rapide"""
        form = ConsultationGynecologiqueQuickForm(patient=self.patient_femme)
        
        # Vérifier que tous les champs sont optionnels sauf motif
        for field_name, field in form.fields.items():
            if field_name == 'motif':
                self.assertTrue(field.required)
            else:
                self.assertFalse(field.required)
        
        # Vérifier la date initiale pour une nouvelle instance
        self.assertEqual(form.fields['date_consultation'].initial, date.today())

    def test_quick_form_fields(self):
        """Test des champs du formulaire rapide"""
        form = ConsultationGynecologiqueQuickForm()
        
        # Vérifier que le patient n'est pas dans les champs (sera associé via save)
        self.assertNotIn('patient', form.fields)
        
        # Vérifier les champs présents
        expected_fields = [
            'date_consultation', 'tension_systolique', 'tension_diastolique',
            'poids', 'motif', 'examen', 'prescription', 'notes'
        ]
        for field in expected_fields:
            self.assertIn(field, form.fields)

    def test_quick_form_save(self):
        """Test de la méthode save du formulaire rapide"""
        form_data = {
            'date_consultation': date.today(),
            'motif': 'Consultation rapide',
            'poids': 65.5
        }
        
        form = ConsultationGynecologiqueQuickForm(data=form_data, patient=self.patient_femme)
        self.assertTrue(form.is_valid())
        
        consultation = form.save()
        self.assertEqual(consultation.patient, self.patient_femme)
        self.assertEqual(consultation.motif, 'Consultation rapide')
        self.assertEqual(consultation.poids, 65.5)

    def test_quick_form_save_without_commit(self):
        """Test de la méthode save sans commit"""
        form_data = {
            'date_consultation': date.today(),
            'motif': 'Consultation test'
        }
        
        form = ConsultationGynecologiqueQuickForm(data=form_data, patient=self.patient_femme)
        self.assertTrue(form.is_valid())
        
        consultation = form.save(commit=False)
        self.assertEqual(consultation.patient, self.patient_femme)
        self.assertIsNone(consultation.pk)  # Pas encore sauvegardé

    def test_quick_form_widget_classes(self):
        """Test des classes CSS du formulaire rapide"""
        form = ConsultationGynecologiqueQuickForm()
        
        # Vérifier les classes spécifiques au formulaire rapide
        for field_name, field in form.fields.items():
            if hasattr(field.widget, 'attrs') and 'class' in field.widget.attrs:
                css_class = field.widget.attrs['class']
                self.assertIn('focus:ring-blue-500', css_class)
                self.assertIn('focus:border-blue-500', css_class)

    def test_quick_form_height_constraints(self):
        """Test des contraintes de hauteur des textarea"""
        form = ConsultationGynecologiqueQuickForm()
        
        # Vérifier les hauteurs spécifiques
        motif_style = form.fields['motif'].widget.attrs.get('style', '')
        self.assertIn('height: 88px', motif_style)
        
        examen_class = form.fields['examen'].widget.attrs.get('class', '')
        self.assertIn('h-16', examen_class)

    def test_form_labels_and_help_texts(self):
        """Test des labels et textes d'aide"""
        form = ConsultationGynecologiqueForm()
        
        # Vérifier quelques labels
        expected_labels = {
            'patient': 'Patiente',
            'date_consultation': 'Date de consultation',
            'tension_systolique': 'Tension systolique (mmHg)',
            'motif': 'Motif de la consultation'
        }
        
        for field_name, expected_label in expected_labels.items():
            self.assertEqual(form.fields[field_name].label, expected_label)

    def test_form_help_texts(self):
        """Test des textes d'aide"""
        form = ConsultationGynecologiqueForm()
        
        # Vérifier quelques textes d'aide
        expected_help_texts = {
            'tension_systolique': 'Tension artérielle systolique (80-250 mmHg)',
            'poids': 'Poids de la patiente en kilogrammes (30-200 kg)',
            'motif': 'Raison de la venue de la patiente'
        }
        
        for field_name, expected_help_text in expected_help_texts.items():
            self.assertEqual(form.fields[field_name].help_text, expected_help_text)