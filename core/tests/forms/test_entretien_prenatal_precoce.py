"""
Tests pour les formulaires EntretienPrenatalPrecoce
"""

from django.test import TestCase
from django.forms.widgets import HiddenInput
from datetime import date, timedelta

from core.forms.entretien_prenatal_precoce import (
    EntretienPrenatalPrecoceForm,
    EntretienPrenatalPrecoceModalForm,
    EntretienPrenatalPrecoceQuickForm,
    EntretienPrenatalPrecoceSearchForm
)
from core.models import Patient, SageFemme, Caisse, EntretienPrenatalPrecoce
from authentication.models import SageFemmeUser


class EntretienPrenatalPrecoceFormTest(TestCase):
    """Tests pour EntretienPrenatalPrecoceForm"""
    
    def setUp(self):
        """Configuration des données de test"""
        # Caisse
        self.caisse = Caisse.objects.create(nom="CAFAT")
        
        # Utilisateur et sage-femme
        self.user = SageFemmeUser.objects.create_user(
            email='sage.femme@test.com',
            password='testpass123'
        )
        self.sage_femme = SageFemme.objects.create(
            user=self.user,
            nom='Martin',
            prenom='Dr Sophie',
            titre='Sage-Femme',
            telephone='123456789',
            email='sage.femme@test.com',
            numero_cafat='123456',
            ridet='987654',
            rib='FR7630001007941234567890185',
            banque='BNC',
            situation='titulaire'
        )
        
        # Patiente femme avec DDG
        self.patient_femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            caisse=self.caisse,
            date_debut_grossesse=date(2024, 1, 15)
        )
        
        # Patiente femme sans DDG
        self.patient_femme_sans_ddg = Patient.objects.create(
            type_patient='femme',
            nom='Martin',
            prenom='Sophie',
            date_naissance=date(1988, 3, 10),
            caisse=self.caisse
        )
        
        # Patient bébé
        self.patient_bebe = Patient.objects.create(
            type_patient='bebe',
            nom='Petit',
            prenom='Lucas',
            date_naissance=date(2024, 1, 1),
            caisse=self.caisse
        )
        
        self.valid_form_data = {
            'patient': self.patient_femme.id,
            'date_entretien': date.today(),
            'conjoint_present': True,
            'lieu_accouchement_prevu': 'Maternité CHT',
            'atcd_marquants_sante': 'Aucun ATCD particulier',
            'environnement_social_familial': 'Environnement stable',
            'projet_naissance_parentalite': 'Accouchement naturel souhaité',
            'ressenti': 'Très positive sur la grossesse',
            'propositions_liens': 'Cours de préparation à la naissance'
        }
    
    def test_form_initialization(self):
        """Test initialisation du formulaire"""
        form = EntretienPrenatalPrecoceForm()
        
        # Vérifier que seules les femmes avec DDG sont disponibles
        queryset = form.fields['patient'].queryset
        patient_ids = list(queryset.values_list('id', flat=True))
        
        self.assertIn(self.patient_femme.id, patient_ids)
        self.assertNotIn(self.patient_femme_sans_ddg.id, patient_ids)
        self.assertNotIn(self.patient_bebe.id, patient_ids)
    
    def test_form_valid_data(self):
        """Test formulaire avec données valides"""
        form = EntretienPrenatalPrecoceForm(data=self.valid_form_data)
        
        self.assertTrue(form.is_valid(), f"Erreurs: {form.errors}")
        
        # Test sauvegarde
        entretien = form.save()
        self.assertEqual(entretien.patient, self.patient_femme)
        self.assertTrue(entretien.conjoint_present)
        self.assertEqual(entretien.lieu_accouchement_prevu, 'Maternité CHT')
    
    def test_form_missing_required_fields(self):
        """Test champs obligatoires manquants"""
        # Test sans patient
        form_data = self.valid_form_data.copy()
        del form_data['patient']
        form = EntretienPrenatalPrecoceForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('patient', form.errors)
        
        # Test sans date_entretien
        form_data = self.valid_form_data.copy()
        del form_data['date_entretien']
        form = EntretienPrenatalPrecoceForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('date_entretien', form.errors)
    
    def test_clean_date_entretien_future(self):
        """Test validation date dans le futur"""
        form_data = self.valid_form_data.copy()
        form_data['date_entretien'] = date.today() + timedelta(days=10)
        
        form = EntretienPrenatalPrecoceForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('date_entretien', form.errors)
        self.assertIn("ne peut pas être dans le futur", form.errors['date_entretien'][0])
    
    def test_clean_validation_ddg_missing(self):
        """Test validation globale : patiente sans DDG"""
        form_data = self.valid_form_data.copy()
        form_data['patient'] = self.patient_femme_sans_ddg.id
        
        form = EntretienPrenatalPrecoceForm(data=form_data)
        
        # La patiente ne devrait même pas être dans les choix
        self.assertFalse(form.is_valid())
    
    def test_clean_validation_date_avant_ddg(self):
        """Test validation : date avant DDG"""
        form_data = self.valid_form_data.copy()
        form_data['date_entretien'] = self.patient_femme.date_debut_grossesse - timedelta(days=1)
        
        form = EntretienPrenatalPrecoceForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn("postérieure au début de grossesse", form.errors['__all__'][0])
    
    def test_widget_attributes(self):
        """Test attributs des widgets"""
        form = EntretienPrenatalPrecoceForm()
        
        # Test widget date avec max aujourd'hui
        date_widget = form.fields['date_entretien'].widget
        self.assertIn('max', date_widget.attrs)
        self.assertIn('class', date_widget.attrs)
        
        # Test widgets textarea avec rows
        textarea_fields = ['atcd_marquants_sante', 'environnement_social_familial', 
                          'projet_naissance_parentalite', 'ressenti', 'propositions_liens']
        
        for field_name in textarea_fields:
            widget = form.fields[field_name].widget
            self.assertIn('rows', widget.attrs)
            self.assertIn('class', widget.attrs)
            self.assertIn('placeholder', widget.attrs)
    
    def test_labels_francais(self):
        """Test labels en français"""
        form = EntretienPrenatalPrecoceForm()
        
        expected_labels = {
            'patient': 'Patiente',
            'date_entretien': "Date de l'entretien",
            'conjoint_present': 'Conjoint/partenaire présent',
            'lieu_accouchement_prevu': "Lieu d'accouchement prévu",
            'atcd_marquants_sante': 'ATCD marquants et santé globale',
            'environnement_social_familial': 'Environnement social et familial',
            'projet_naissance_parentalite': 'Projet de naissance et de parentalité',
            'ressenti': 'Ressenti',
            'propositions_liens': 'Propositions/liens'
        }
        
        for field_name, expected_label in expected_labels.items():
            self.assertEqual(form.fields[field_name].label, expected_label)


class EntretienPrenatalPrecoceModalFormTest(TestCase):
    """Tests pour EntretienPrenatalPrecoceModalForm"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.caisse = Caisse.objects.create(nom="CAFAT")
        self.patient_femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            caisse=self.caisse,
            date_debut_grossesse=date(2024, 1, 15)
        )
    
    def test_form_with_patient_id(self):
        """Test formulaire modal avec patient_id"""
        form = EntretienPrenatalPrecoceModalForm(patient_id=self.patient_femme.id)
        
        # Le champ patient devrait être caché et pré-rempli
        self.assertIsInstance(form.fields['patient'].widget, HiddenInput)
        self.assertEqual(form.fields['patient'].initial, self.patient_femme)
    
    def test_form_without_patient_id(self):
        """Test formulaire modal sans patient_id"""
        form = EntretienPrenatalPrecoceModalForm()
        
        # Le champ patient ne devrait pas être caché
        self.assertNotIsInstance(form.fields['patient'].widget, HiddenInput)
    
    def test_css_classes_adjustment(self):
        """Test ajustement des classes CSS pour modal"""
        form = EntretienPrenatalPrecoceModalForm()
        
        # Vérifier que les classes CSS sont ajustées
        for field_name, field in form.fields.items():
            if hasattr(field.widget, 'attrs') and 'class' in field.widget.attrs:
                css_class = field.widget.attrs['class']
                # Les classes sm:text-sm devraient être remplacées par text-sm
                self.assertNotIn('sm:text-sm', css_class)


class EntretienPrenatalPrecoceQuickFormTest(TestCase):
    """Tests pour EntretienPrenatalPrecoceQuickForm"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.caisse = Caisse.objects.create(nom="CAFAT")
        self.patient_femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            caisse=self.caisse,
            date_debut_grossesse=date(2024, 1, 15)
        )
        
        self.valid_form_data = {
            'date_entretien': date.today(),
            'conjoint_present': True,
            'lieu_accouchement_prevu': 'Maternité CHT',
            'atcd_marquants_sante': 'Aucun ATCD',
            'environnement_social_familial': 'Stable',
            'projet_naissance_parentalite': 'Naturel',
            'ressenti': 'Positive',
            'propositions_liens': 'Cours préparation'
        }
    
    def test_form_initialization_with_patient(self):
        """Test initialisation avec patiente"""
        form = EntretienPrenatalPrecoceQuickForm(patient=self.patient_femme)
        
        self.assertEqual(form.patient, self.patient_femme)
    
    def test_form_valid_data(self):
        """Test formulaire avec données valides"""
        form = EntretienPrenatalPrecoceQuickForm(
            data=self.valid_form_data,
            patient=self.patient_femme
        )
        
        self.assertTrue(form.is_valid(), f"Erreurs: {form.errors}")
    
    def test_form_save_with_patient(self):
        """Test sauvegarde avec assignation patiente"""
        form = EntretienPrenatalPrecoceQuickForm(
            data=self.valid_form_data,
            patient=self.patient_femme
        )
        
        self.assertTrue(form.is_valid())
        entretien = form.save()
        
        self.assertEqual(entretien.patient, self.patient_femme)
        self.assertTrue(entretien.conjoint_present)
        self.assertEqual(entretien.lieu_accouchement_prevu, 'Maternité CHT')
    
    def test_form_save_commit_false(self):
        """Test sauvegarde avec commit=False"""
        form = EntretienPrenatalPrecoceQuickForm(
            data=self.valid_form_data,
            patient=self.patient_femme
        )
        
        self.assertTrue(form.is_valid())
        entretien = form.save(commit=False)
        
        # L'objet ne devrait pas être sauvé en base
        self.assertIsNone(entretien.id)
        self.assertEqual(entretien.patient, self.patient_femme)
    
    def test_clean_date_entretien_with_patient(self):
        """Test validation date avec patiente"""
        form_data = self.valid_form_data.copy()
        form_data['date_entretien'] = self.patient_femme.date_debut_grossesse - timedelta(days=1)
        
        form = EntretienPrenatalPrecoceQuickForm(
            data=form_data,
            patient=self.patient_femme
        )
        
        self.assertFalse(form.is_valid())
        self.assertIn('date_entretien', form.errors)
        self.assertIn("postérieure au début de grossesse", form.errors['date_entretien'][0])
    
    def test_clean_date_entretien_future(self):
        """Test validation date future"""
        form_data = self.valid_form_data.copy()
        form_data['date_entretien'] = date.today() + timedelta(days=5)
        
        form = EntretienPrenatalPrecoceQuickForm(
            data=form_data,
            patient=self.patient_femme
        )
        
        self.assertFalse(form.is_valid())
        self.assertIn('date_entretien', form.errors)
        self.assertIn("ne peut pas être dans le futur", form.errors['date_entretien'][0])
    
    def test_labels_simplifies(self):
        """Test labels simplifiés pour formulaire rapide"""
        form = EntretienPrenatalPrecoceQuickForm(patient=self.patient_femme)
        
        expected_labels = {
            'date_entretien': 'Date',
            'conjoint_present': 'Conjoint présent',
            'lieu_accouchement_prevu': 'Lieu accouchement',
            'atcd_marquants_sante': 'ATCD marquants et santé globale',
            'environnement_social_familial': 'Environnement social et familial',
            'projet_naissance_parentalite': 'Projet de naissance et de parentalité',
            'ressenti': 'Ressenti',
            'propositions_liens': 'Propositions/liens'
        }
        
        for field_name, expected_label in expected_labels.items():
            self.assertEqual(form.fields[field_name].label, expected_label)
    
    def test_widget_purple_theme(self):
        """Test thème violet des widgets"""
        form = EntretienPrenatalPrecoceQuickForm(patient=self.patient_femme)
        
        # Tous les champs devraient avoir des classes purple
        for field_name, field in form.fields.items():
            if hasattr(field.widget, 'attrs') and 'class' in field.widget.attrs:
                css_class = field.widget.attrs['class']
                self.assertIn('purple', css_class)


class EntretienPrenatalPrecoceSearchFormTest(TestCase):
    """Tests pour EntretienPrenatalPrecoceSearchForm"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.user = SageFemmeUser.objects.create_user(
            email='sage.femme@test.com',
            password='testpass123'
        )
        self.sage_femme = SageFemme.objects.create(
            user=self.user,
            nom='Martin',
            prenom='Dr Sophie',
            titre='Sage-Femme',
            telephone='123456789',
            email='sage.femme@test.com',
            numero_cafat='123456',
            ridet='987654',
            rib='FR7630001007941234567890185',
            banque='BNC',
            situation='titulaire',
        )
    
    def test_form_initialization(self):
        """Test initialisation du formulaire de recherche"""
        form = EntretienPrenatalPrecoceSearchForm()
        
        # Tous les champs devraient être optionnels
        for field in form.fields.values():
            self.assertFalse(field.required)
    
    def test_sage_femme_queryset(self):
        """Test queryset des sages-femmes actives"""
        form = EntretienPrenatalPrecoceSearchForm()
        
        queryset = form.fields['sage_femme'].queryset
        sage_femme_ids = list(queryset.values_list('id', flat=True))
        
        self.assertIn(self.sage_femme.id, sage_femme_ids)
    
    def test_form_valid_empty(self):
        """Test formulaire vide valide"""
        form = EntretienPrenatalPrecoceSearchForm(data={})
        
        self.assertTrue(form.is_valid())
    
    def test_form_valid_with_data(self):
        """Test formulaire avec données de recherche"""
        form_data = {
            'recherche': 'Dupont',
            'date_debut': date(2024, 1, 1),
            'date_fin': date(2024, 12, 31),
            'conjoint_present': 'oui',
            'sage_femme': self.sage_femme.id
        }
        
        form = EntretienPrenatalPrecoceSearchForm(data=form_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['recherche'], 'Dupont')
        self.assertEqual(form.cleaned_data['conjoint_present'], 'oui')
    
    def test_conjoint_present_choices(self):
        """Test choix pour présence conjoint"""
        form = EntretienPrenatalPrecoceSearchForm()
        
        choices = form.fields['conjoint_present'].choices
        choice_values = [choice[0] for choice in choices]
        
        self.assertIn('', choice_values)  # Tous
        self.assertIn('oui', choice_values)  # Présent
        self.assertIn('non', choice_values)  # Absent