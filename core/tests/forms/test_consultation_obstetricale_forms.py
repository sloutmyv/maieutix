"""
Tests pour les formulaires ConsultationObstetricale
Tests complets des formulaires et validations
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from core.forms.consultation_obstetricale import (
    ConsultationObstetricaleForm, 
    ConsultationObstetricaleModalForm,
    ConsultationObstetricaleQuickForm
)
from core.models import Patient, Caisse, SageFemme
from authentication.models import SageFemmeUser


class ConsultationObstetricaleFormTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.caisse = Caisse.objects.create(nom="CAFAT")
        
        # Patient femme
        self.patient_femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse,
            date_debut_grossesse=date.today() - timedelta(days=140)
        )
        
        # Patient bébé
        self.patient_bebe = Patient.objects.create(
            type_patient='bebe',
            nom='Petit',
            prenom='Lucas',
            date_naissance=date.today() - timedelta(days=30),
            caisse=self.caisse
        )
        
        # Créer une sage-femme
        self.user = SageFemmeUser.objects.create_user(
            email='sage_femme_test@test.com',
            password='testpass123'
        )
        self.sage_femme = SageFemme.objects.create(
            user=self.user,
            nom='Martin',
            prenom='Dr Sophie',
            titre='Sage-Femme',
            telephone='0987654321',
            email='sophie.martin@test.com',
            numero_cafat='123456',
            ridet='987654',
            rib='FR7630001007941234567890185',
            banque='BNC',
            situation='titulaire'
        )
    
    def test_form_valid_data(self):
        """Test formulaire avec données valides"""
        form_data = {
            'patient': self.patient_femme.pk,
            'date_consultation': date.today(),
            'motif': 'Contrôle de routine',
            'tension_systolique': 120,
            'tension_diastolique': 80,
            'poids': 65.5,
            'examen': 'Examen normal',
            'prescription': 'Repos',
            'notes': 'RAS'
        }
        
        form = ConsultationObstetricaleForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_required_fields(self):
        """Test des champs obligatoires"""
        form = ConsultationObstetricaleForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('patient', form.errors)
        self.assertIn('date_consultation', form.errors)
        self.assertIn('motif', form.errors)
    
    def test_form_date_future_invalid(self):
        """Test validation date future invalide"""
        form_data = {
            'patient': self.patient_femme.pk,
            'date_consultation': date.today() + timedelta(days=1),
            'motif': 'Consultation future'
        }
        
        form = ConsultationObstetricaleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_consultation', form.errors)
        self.assertIn('futur', str(form.errors['date_consultation'][0]))
    
    def test_form_tension_coherence(self):
        """Test validation cohérence tension artérielle"""
        form_data = {
            'patient': self.patient_femme.pk,
            'date_consultation': date.today(),
            'motif': 'Test tension',
            'tension_systolique': 80,  # Plus faible que diastolique
            'tension_diastolique': 120
        }
        
        form = ConsultationObstetricaleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('tension_systolique', form.errors)
    
    def test_form_tension_incomplete(self):
        """Test validation tension incomplète"""
        form_data = {
            'patient': self.patient_femme.pk,
            'date_consultation': date.today(),
            'motif': 'Test tension incomplète',
            'tension_systolique': 120
            # tension_diastolique manquante
        }
        
        form = ConsultationObstetricaleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('complète', str(form.errors['__all__'][0]))
    
    def test_form_patient_type_validation(self):
        """Test validation type de patient (femme uniquement)"""
        form_data = {
            'patient': self.patient_bebe.pk,
            'date_consultation': date.today(),
            'motif': 'Test bébé'
        }
        
        form = ConsultationObstetricaleForm(data=form_data)
        self.assertFalse(form.is_valid())
        # Le patient bébé n'est pas dans le queryset filtré, donc erreur de choix invalide
        self.assertIn('patient', form.errors)
    
    def test_form_queryset_filtered_by_gender(self):
        """Test que le queryset est filtré pour les femmes"""
        form = ConsultationObstetricaleForm()
        patient_pks = list(form.fields['patient'].queryset.values_list('pk', flat=True))
        self.assertIn(self.patient_femme.pk, patient_pks)
        self.assertNotIn(self.patient_bebe.pk, patient_pks)
    
    def test_form_with_patient_id(self):
        """Test formulaire avec patient_id spécifique"""
        form = ConsultationObstetricaleForm(patient_id=self.patient_femme.pk)
        
        # Le queryset devrait être limité à cette patiente
        self.assertEqual(form.fields['patient'].queryset.count(), 1)
        self.assertEqual(form.fields['patient'].initial, self.patient_femme)
    
    def test_form_poids_limits(self):
        """Test validation limites de poids via les widgets"""
        form = ConsultationObstetricaleForm()
        
        poids_widget = form.fields['poids'].widget
        self.assertEqual(poids_widget.attrs['min'], '30')
        self.assertEqual(poids_widget.attrs['max'], '200')
        self.assertEqual(poids_widget.attrs['step'], '0.1')
    
    def test_form_tension_limits(self):
        """Test validation limites de tension via les widgets"""
        form = ConsultationObstetricaleForm()
        
        sys_widget = form.fields['tension_systolique'].widget
        dia_widget = form.fields['tension_diastolique'].widget
        
        self.assertEqual(sys_widget.attrs['min'], '80')
        self.assertEqual(sys_widget.attrs['max'], '250')
        self.assertEqual(dia_widget.attrs['min'], '40')
        self.assertEqual(dia_widget.attrs['max'], '150')
    
    def test_form_date_max_today(self):
        """Test que la date max est fixée à aujourd'hui"""
        form = ConsultationObstetricaleForm()
        date_widget = form.fields['date_consultation'].widget
        self.assertEqual(date_widget.attrs['max'], date.today().isoformat())
    
    def test_form_css_classes(self):
        """Test présence des classes CSS Tailwind"""
        form = ConsultationObstetricaleForm()
        
        for field_name in form.fields:
            widget = form.fields[field_name].widget
            if hasattr(widget, 'attrs') and 'class' in widget.attrs:
                css_class = widget.attrs['class']
                self.assertIn('border-gray-300', css_class)
                self.assertIn('focus:ring-primary', css_class)
    
    def test_form_labels(self):
        """Test des labels personnalisés"""
        form = ConsultationObstetricaleForm()
        
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
        form = ConsultationObstetricaleForm()
        
        self.assertIn('80-250', form.fields['tension_systolique'].help_text)
        self.assertIn('40-150', form.fields['tension_diastolique'].help_text)
        self.assertIn('30-200', form.fields['poids'].help_text)


class ConsultationObstetricaleModalFormTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.caisse = Caisse.objects.create(nom="CAFAT")
        
        self.patient_femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse
        )
    
    def test_modal_form_css_classes(self):
        """Test des classes CSS spécifiques au modal"""
        form = ConsultationObstetricaleModalForm(patient_id=self.patient_femme.pk)
        
        for field_name in form.fields:
            if field_name != 'patient':  # Patient peut être caché
                widget = form.fields[field_name].widget
                if hasattr(widget, 'attrs') and 'class' in widget.attrs:
                    css_class = widget.attrs['class']
                    self.assertIn('focus:ring-blue-500', css_class)
    
    def test_modal_form_patient_hidden(self):
        """Test que le champ patient est caché avec patient_id"""
        form = ConsultationObstetricaleModalForm(patient_id=self.patient_femme.pk)
        
        from django import forms
        self.assertIsInstance(form.fields['patient'].widget, forms.HiddenInput)


class ConsultationObstetricaleQuickFormTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.caisse = Caisse.objects.create(nom="CAFAT")
        
        self.patient_femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse
        )
    
    def test_quick_form_excludes_patient_field(self):
        """Test que le formulaire quick n'inclut pas le champ patient"""
        form = ConsultationObstetricaleQuickForm()
        self.assertNotIn('patient', form.fields)
    
    def test_quick_form_date_default(self):
        """Test que la date par défaut est aujourd'hui"""
        form = ConsultationObstetricaleQuickForm()
        self.assertEqual(form.fields['date_consultation'].initial, date.today())
    
    def test_quick_form_only_motif_required(self):
        """Test que seul le motif est obligatoire"""
        form = ConsultationObstetricaleQuickForm()
        
        required_fields = [name for name, field in form.fields.items() if field.required]
        self.assertEqual(required_fields, ['motif'])
    
    def test_quick_form_compact_css_classes(self):
        """Test des classes CSS compactes pour le formulaire quick"""
        form = ConsultationObstetricaleQuickForm()
        
        # Vérifier les classes spécifiques aux formulaires compacts
        for field_name in form.fields:
            widget = form.fields[field_name].widget
            if hasattr(widget, 'attrs') and 'class' in widget.attrs:
                css_class = widget.attrs['class']
                self.assertIn('focus:ring-blue-500', css_class)
    
    def test_quick_form_save_with_patient(self):
        """Test de la sauvegarde avec patient fourni"""
        form_data = {
            'date_consultation': date.today(),
            'motif': 'Consultation quick test',
            'tension_systolique': 125,
            'tension_diastolique': 85
        }
        
        form = ConsultationObstetricaleQuickForm(
            data=form_data, 
            patient=self.patient_femme
        )
        
        self.assertTrue(form.is_valid())
        
        consultation = form.save()
        self.assertEqual(consultation.patient, self.patient_femme)
        self.assertEqual(consultation.motif, 'Consultation quick test')
    
    def test_quick_form_save_commit_false(self):
        """Test de la sauvegarde avec commit=False"""
        form_data = {
            'date_consultation': date.today(),
            'motif': 'Test commit false'
        }
        
        form = ConsultationObstetricaleQuickForm(
            data=form_data,
            patient=self.patient_femme
        )
        
        self.assertTrue(form.is_valid())
        
        consultation = form.save(commit=False)
        self.assertEqual(consultation.patient, self.patient_femme)
        self.assertIsNone(consultation.pk)  # Pas encore sauvé en DB
    
    def test_quick_form_compact_textarea_heights(self):
        """Test des hauteurs spécifiques des textarea compacts"""
        form = ConsultationObstetricaleQuickForm()
        
        # Vérifier les styles spécifiques aux textarea
        motif_widget = form.fields['motif'].widget
        self.assertIn('height: 88px', motif_widget.attrs['style'])
        
        examen_widget = form.fields['examen'].widget
        self.assertIn('h-16', examen_widget.attrs['class'])
    
    def test_quick_form_input_heights(self):
        """Test des hauteurs des inputs compacts"""
        form = ConsultationObstetricaleQuickForm()
        
        input_fields = ['date_consultation', 'tension_systolique', 'tension_diastolique', 'poids']
        
        for field_name in input_fields:
            widget = form.fields[field_name].widget
            self.assertIn('h-8', widget.attrs['class'])
    
    def test_all_forms_inheritance(self):
        """Test de l'héritage des formulaires"""
        # ModalForm hérite de Form de base
        self.assertTrue(issubclass(ConsultationObstetricaleModalForm, ConsultationObstetricaleForm))
        
        # QuickForm hérite directement de ModelForm
        from django import forms
        self.assertTrue(issubclass(ConsultationObstetricaleQuickForm, forms.ModelForm))
    
    def test_form_placeholders(self):
        """Test des placeholders informatifs"""
        form = ConsultationObstetricaleForm()
        
        expected_placeholders = {
            'tension_systolique': 'Ex: 120',
            'tension_diastolique': 'Ex: 80',
            'poids': 'Ex: 65.5',
            'motif': 'Motif de la consultation...'
        }
        
        for field_name, expected_placeholder in expected_placeholders.items():
            widget = form.fields[field_name].widget
            self.assertEqual(widget.attrs['placeholder'], expected_placeholder)
    
    def test_form_minimal_valid_data(self):
        """Test avec données minimales valides"""
        form_data = {
            'patient': self.patient_femme.pk,
            'date_consultation': date.today(),
            'motif': 'Contrôle minimal'
        }
        
        form = ConsultationObstetricaleForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        consultation = form.save()
        self.assertEqual(consultation.patient, self.patient_femme)
        self.assertEqual(consultation.motif, 'Contrôle minimal')
        self.assertIsNone(consultation.tension_systolique)
        self.assertIsNone(consultation.poids)