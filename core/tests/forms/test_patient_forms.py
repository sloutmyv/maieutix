"""
Tests pour les formulaires Patient
Tests complets des validations et fonctionnalités
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date, timedelta

from core.models import Patient, Caisse
from core.views.patients import PatientForm


class PatientFormTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.caisse = Caisse.objects.create(
            nom="CAFAT"
        )
        
        self.femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='123456',
            caisse=self.caisse
        )
    
    def test_form_initialization(self):
        """Test d'initialisation du formulaire"""
        form = PatientForm()
        
        # Vérifier que les champs ont les bonnes contraintes de date
        today_str = date.today().strftime('%Y-%m-%d')
        self.assertEqual(form.fields['date_naissance'].widget.attrs['max'], today_str)
        self.assertEqual(form.fields['date_debut_grossesse'].widget.attrs['max'], today_str)
        self.assertEqual(form.fields['date_naissance_assure'].widget.attrs['max'], today_str)
        
        # Vérifier les querysets
        self.assertEqual(
            list(form.fields['mere'].queryset),
            list(Patient.objects.filter(type_patient='femme', is_active=True))
        )
        self.assertEqual(
            list(form.fields['caisse'].queryset),
            list(Caisse.objects.all())
        )
    
    def test_form_valid_femme_data(self):
        """Test formulaire valide pour une femme"""
        data = {
            'type_patient': 'femme',
            'nom': 'Martin',
            'prenom': 'Sophie',
            'date_naissance': '1985-03-10',
            'telephone': '0123456789',
            'caisse': self.caisse.id,
            'est_assure_titulaire': True
        }
        
        form = PatientForm(data)
        self.assertTrue(form.is_valid())
        
        patient = form.save()
        self.assertEqual(patient.nom, 'Martin')
        self.assertEqual(patient.prenom, 'Sophie')
        self.assertEqual(patient.type_patient, 'femme')
    
    def test_form_valid_bebe_data(self):
        """Test formulaire valide pour un bébé"""
        data = {
            'type_patient': 'bebe',
            'nom': 'Dupont',
            'prenom': 'Lucas',
            'date_naissance': (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'mere': self.femme.id,
            'caisse': self.caisse.id,
            'est_assure_titulaire': False,
            'nom_assure': 'Dupont',
            'prenom_assure': 'Marie',
            'date_naissance_assure': '1990-05-15',
            'rue_assure': '123 Rue Test',
            'code_postal_assure': '98800',
            'commune_assure': 'Noumea'
        }
        
        form = PatientForm(data)
        self.assertTrue(form.is_valid())
        
        patient = form.save()
        self.assertEqual(patient.type_patient, 'bebe')
        self.assertEqual(patient.mere, self.femme)
    
    def test_form_missing_required_fields(self):
        """Test formulaire avec champs requis manquants"""
        data = {
            'type_patient': 'femme',
            # Nom manquant
            'prenom': 'Sophie',
            'date_naissance': '1985-03-10'
        }
        
        form = PatientForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('nom', form.errors)
    
    def test_form_invalid_date_format(self):
        """Test formulaire avec format de date invalide"""
        data = {
            'type_patient': 'femme',
            'nom': 'Test',
            'prenom': 'Date',
            'date_naissance': '15/05/1990'  # Format incorrect
        }
        
        form = PatientForm(data)
        self.assertFalse(form.is_valid())
        # Les erreurs peuvent être dans date_naissance ou __all__
        self.assertTrue(form.errors)  # Il doit y avoir des erreurs
    
    def test_form_future_date_validation(self):
        """Test validation date future côté formulaire"""
        future_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        data = {
            'type_patient': 'femme',
            'nom': 'Test',
            'prenom': 'Future',
            'date_naissance': future_date,
            'caisse': self.caisse.id
        }
        
        form = PatientForm(data)
        
        # Le formulaire peut être valide côté Django mais échouera à la validation modèle
        if form.is_valid():
            with self.assertRaises(ValidationError):
                form.save()
        else:
            # Si le formulaire invalide directement, vérifier qu'il y a une erreur
            self.assertTrue(form.errors)  # Il doit y avoir des erreurs
    
    def test_form_bebe_without_mere(self):
        """Test formulaire bébé sans mère"""
        data = {
            'type_patient': 'bebe',
            'nom': 'Test',
            'prenom': 'Bebe',
            'date_naissance': (date.today() - timedelta(days=10)).strftime('%Y-%m-%d'),
            # Pas de mère spécifiée
            'caisse': self.caisse.id
        }
        
        form = PatientForm(data)
        
        if form.is_valid():
            with self.assertRaises(ValidationError):
                form.save()
        else:
            # Le formulaire pourrait déjà détecter l'erreur
            pass
    
    def test_form_bebe_as_titulaire(self):
        """Test formulaire bébé comme assuré titulaire (invalide)"""
        data = {
            'type_patient': 'bebe',
            'nom': 'Test',
            'prenom': 'Bebe',
            'date_naissance': (date.today() - timedelta(days=10)).strftime('%Y-%m-%d'),
            'mere': self.femme.id,
            'est_assure_titulaire': True,  # Invalide
            'caisse': self.caisse.id
        }
        
        form = PatientForm(data)
        
        if form.is_valid():
            with self.assertRaises(ValidationError):
                form.save()
        else:
            # Le formulaire pourrait déjà détecter l'erreur
            pass
    
    def test_form_update_existing_patient(self):
        """Test modification d'un patient existant"""
        data = {
            'type_patient': 'femme',
            'nom': 'Dupont-Martin',  # Modification
            'prenom': 'Marie',
            'date_naissance': '1990-05-15',
            'telephone': '0123456789',  # Modification
            'caisse': self.caisse.id,
            'est_assure_titulaire': True
        }
        
        form = PatientForm(data, instance=self.femme)
        self.assertTrue(form.is_valid())
        
        patient = form.save()
        self.assertEqual(patient.nom, 'Dupont-Martin')
        self.assertEqual(patient.telephone, '0123456789')
        self.assertEqual(patient.id, self.femme.id)  # Même instance
    
    def test_form_widget_attributes(self):
        """Test des attributs des widgets de formulaire"""
        form = PatientForm()
        
        # Vérifier les classes CSS
        expected_css_class = 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'
        
        for field_name in ['nom', 'prenom', 'telephone']:
            widget_attrs = form.fields[field_name].widget.attrs
            self.assertEqual(widget_attrs['class'], expected_css_class)
        
        # Vérifier les champs de date
        date_fields = ['date_naissance', 'date_debut_grossesse', 'date_naissance_assure']
        for field_name in date_fields:
            widget_attrs = form.fields[field_name].widget.attrs
            # Vérifier que le type est date ou que le widget est DateInput
            self.assertTrue(
                widget_attrs.get('type') == 'date' or 
                form.fields[field_name].widget.__class__.__name__ == 'DateInput'
            )
            self.assertEqual(widget_attrs['class'], expected_css_class)
    
    def test_form_choice_fields(self):
        """Test des champs de choix"""
        form = PatientForm()
        
        # Vérifier le champ type_patient
        type_choices = form.fields['type_patient'].choices
        self.assertIn(('femme', 'Femme'), type_choices)
        self.assertIn(('bebe', 'Bébé'), type_choices)
        
        # Vérifier les empty_label
        self.assertEqual(form.fields['mere'].empty_label, "Sélectionner une mère")
        self.assertEqual(form.fields['caisse'].empty_label, "Sélectionner une caisse")
    
    def test_form_with_inactive_mere(self):
        """Test que les mères inactives ne sont pas dans les choix"""
        # Désactiver la femme
        self.femme.is_active = False
        self.femme.save()
        
        form = PatientForm()
        
        # Vérifier que la femme inactive n'est pas dans les choix
        mere_ids = [choice[0] for choice in form.fields['mere'].choices if choice[0] != '']
        self.assertNotIn(self.femme.id, mere_ids)
    
    def test_form_empty_optional_fields(self):
        """Test formulaire avec champs optionnels vides"""
        data = {
            'type_patient': 'femme',
            'nom': 'Test',
            'prenom': 'Optional',
            'date_naissance': '1990-01-01',
            'est_assure_titulaire': True
            # Tous les autres champs optionnels omis
        }
        
        form = PatientForm(data)
        self.assertTrue(form.is_valid())
        
        patient = form.save()
        self.assertEqual(patient.nom, 'Test')
        self.assertIsNone(patient.caisse)
        self.assertIsNone(patient.telephone)
    
    def test_form_max_length_validation(self):
        """Test validation longueur maximale des champs"""
        data = {
            'type_patient': 'femme',
            'nom': 'x' * 101,  # Trop long (limite 100)
            'prenom': 'Test',
            'date_naissance': '1990-01-01',
            'caisse': self.caisse.id
        }
        
        form = PatientForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('nom', form.errors)
    
    def test_form_telephone_field(self):
        """Test du champ téléphone"""
        data = {
            'type_patient': 'femme',
            'nom': 'Test',
            'prenom': 'Phone',
            'date_naissance': '1990-01-01',
            'telephone': '0123456789',
            'caisse': self.caisse.id,
            'est_assure_titulaire': True
        }
        
        form = PatientForm(data)
        self.assertTrue(form.is_valid())
        
        patient = form.save()
        self.assertEqual(patient.telephone, '0123456789')
    
    def test_form_assurance_fields(self):
        """Test des champs d'assurance"""
        data = {
            'type_patient': 'femme',
            'nom': 'Test',
            'prenom': 'Assurance',
            'date_naissance': '1990-01-01',
            'est_assure_titulaire': True,
            'nom_assure': 'AssureNom',
            'prenom_assure': 'AssurePrenom',
            'date_naissance_assure': '1985-01-01',
            'rue_assure': '123 Rue Test',
            'code_postal_assure': '98800',
            'commune_assure': 'Nouméa',
            'caisse': self.caisse.id
        }
        
        form = PatientForm(data)
        self.assertTrue(form.is_valid())
        
        patient = form.save()
        self.assertTrue(patient.est_assure_titulaire)
        self.assertEqual(patient.nom_assure, 'AssureNom')
        self.assertEqual(patient.commune_assure, 'Nouméa')
    
    def test_form_grossesse_fields(self):
        """Test des champs de grossesse"""
        data = {
            'type_patient': 'femme',
            'nom': 'Test',
            'prenom': 'Grossesse',
            'date_naissance': '1990-01-01',
            'date_debut_grossesse': '2024-01-01',
            'caisse': self.caisse.id,
            'est_assure_titulaire': True
        }
        
        form = PatientForm(data)
        self.assertTrue(form.is_valid())
        
        patient = form.save()
        self.assertEqual(patient.date_debut_grossesse.year, 2024)
    
    def test_form_save_commit_false(self):
        """Test sauvegarde avec commit=False"""
        data = {
            'type_patient': 'femme',
            'nom': 'Test',
            'prenom': 'Commit',
            'date_naissance': '1990-01-01',
            'caisse': self.caisse.id,
            'est_assure_titulaire': True
        }
        
        form = PatientForm(data)
        self.assertTrue(form.is_valid())
        
        patient = form.save(commit=False)
        self.assertEqual(patient.nom, 'Test')
        self.assertIsNone(patient.pk)  # Pas encore sauvegardé
        
        patient.save()
        self.assertIsNotNone(patient.pk)  # Maintenant sauvegardé
    
    def test_form_with_all_fields(self):
        """Test formulaire avec tous les champs remplis"""
        data = {
            'type_patient': 'femme',
            'nom': 'Complete',
            'prenom': 'Test',
            'date_naissance': '1990-01-01',
            'nom_jf': 'MaidenName',
            'profession': 'Ingénieur',
            'telephone': '0123456789',
            'numero_ep': 'EP123',
            'date_debut_grossesse': '2024-01-01',
            'est_assure_titulaire': True,
            'nom_assure': 'AssureNom',
            'prenom_assure': 'AssurePrenom',
            'date_naissance_assure': '1985-01-01',
            'rue_assure': '123 Rue Complete',
            'code_postal_assure': '98800',
            'commune_assure': 'Nouméa',
            'caisse': self.caisse.id
        }
        
        form = PatientForm(data)
        self.assertTrue(form.is_valid())
        
        patient = form.save()
        self.assertEqual(patient.nom, 'Complete')
        self.assertEqual(patient.nom_jf, 'MaidenName')
        self.assertEqual(patient.profession, 'Ingénieur')
        self.assertEqual(patient.numero_ep, 'EP123')
        self.assertTrue(patient.est_assure_titulaire)