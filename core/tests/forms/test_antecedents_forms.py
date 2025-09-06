"""
Tests pour les formulaires et validations des antécédents
Tests des validations côté serveur et logique de formulaires
"""

from datetime import date
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from core.models import Patient, Caisse, Antecedents, FrottisCV


class AntecedentsModelFormTest(TestCase):
    """Tests pour les formulaires basés sur le modèle Antecedents"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.caisse = Caisse.objects.create(nom="CAFAT")
        self.patiente = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse
        )
    
    def test_antecedents_model_form_valid_data(self):
        """Test formulaire avec données valides"""
        # Création d'un formulaire basé sur le modèle
        class AntecedentsForm(ModelForm):
            class Meta:
                model = Antecedents
                fields = ['patient', 'taille', 'poids', 'medecin_traitant', 'gynecologue']
        
        form_data = {
            'patient': self.patiente.pk,
            'taille': 1.65,
            'poids': 60.0,
            'medecin_traitant': 'Dr. Martin',
            'gynecologue': 'Dr. Bernard'
        }
        
        form = AntecedentsForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        # Test sauvegarde
        antecedents = form.save()
        self.assertEqual(antecedents.patient, self.patiente)
        self.assertEqual(antecedents.taille, 1.65)
        self.assertEqual(antecedents.poids, 60.0)
    
    def test_antecedents_model_form_invalid_taille(self):
        """Test formulaire avec taille invalide"""
        class AntecedentsForm(ModelForm):
            class Meta:
                model = Antecedents
                fields = ['patient', 'taille', 'poids']
        
        # Taille trop petite
        form_data = {
            'patient': self.patiente.pk,
            'taille': 0.3,  # Invalide
            'poids': 60.0
        }
        
        form = AntecedentsForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('taille', form.errors)
    
    def test_antecedents_model_form_invalid_poids(self):
        """Test formulaire avec poids invalide"""
        class AntecedentsForm(ModelForm):
            class Meta:
                model = Antecedents
                fields = ['patient', 'taille', 'poids']
        
        # Poids trop élevé
        form_data = {
            'patient': self.patiente.pk,
            'taille': 1.65,
            'poids': 250.0  # Invalide
        }
        
        form = AntecedentsForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('poids', form.errors)
    
    def test_antecedents_model_form_missing_patient(self):
        """Test formulaire sans patient (champ obligatoire)"""
        class AntecedentsForm(ModelForm):
            class Meta:
                model = Antecedents
                fields = ['patient', 'taille', 'poids']
        
        form_data = {
            'taille': 1.65,
            'poids': 60.0
            # patient manquant
        }
        
        form = AntecedentsForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('patient', form.errors)
    
    def test_antecedents_model_form_complete_medical_data(self):
        """Test formulaire avec données médicales complètes"""
        class AntecedentsCompletForm(ModelForm):
            class Meta:
                model = Antecedents
                fields = [
                    'patient', 'taille', 'poids', 'medecin_traitant', 'gynecologue',
                    'allergie', 'asthme', 'diabete', 'hta', 'epilepsie',
                    'atcd_obstetricaux', 'contraception'
                ]
        
        form_data = {
            'patient': self.patiente.pk,
            'taille': 1.70,
            'poids': 65.0,
            'medecin_traitant': 'Dr. Rousseau',
            'gynecologue': 'Dr. Lemaire',
            'allergie': 'Pénicilline, pollen',
            'asthme': True,
            'diabete': False,
            'hta': True,
            'epilepsie': False,
            'atcd_obstetricaux': 'G2P1, césarienne en 2020',
            'contraception': 'Pilule oestroprogestative'
        }
        
        form = AntecedentsCompletForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        antecedents = form.save()
        self.assertEqual(antecedents.allergie, 'Pénicilline, pollen')
        self.assertTrue(antecedents.asthme)
        self.assertFalse(antecedents.diabete)
        self.assertTrue(antecedents.hta)
        self.assertEqual(antecedents.contraception, 'Pilule oestroprogestative')
    
    def test_antecedents_model_form_update_existing(self):
        """Test mise à jour d'antécédents existants via formulaire"""
        # Créer des antécédents existants
        antecedents = Antecedents.objects.create(
            patient=self.patiente,
            taille=1.65,
            poids=60.0,
            medecin_traitant='Dr. Ancien'
        )
        
        class AntecedentsForm(ModelForm):
            class Meta:
                model = Antecedents
                fields = ['taille', 'poids', 'medecin_traitant', 'gynecologue']
        
        # Données de mise à jour
        form_data = {
            'taille': 1.68,
            'poids': 62.5,
            'medecin_traitant': 'Dr. Nouveau',
            'gynecologue': 'Dr. Spécialiste'
        }
        
        form = AntecedentsForm(data=form_data, instance=antecedents)
        self.assertTrue(form.is_valid())
        
        updated_antecedents = form.save()
        self.assertEqual(updated_antecedents.taille, 1.68)
        self.assertEqual(updated_antecedents.medecin_traitant, 'Dr. Nouveau')
        self.assertEqual(updated_antecedents.gynecologue, 'Dr. Spécialiste')


class FrottisCVModelFormTest(TestCase):
    """Tests pour les formulaires basés sur le modèle FrottisCV"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.caisse = Caisse.objects.create(nom="CAFAT")
        self.patiente = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse
        )
        self.antecedents = Antecedents.objects.create(
            patient=self.patiente,
            taille=1.65,
            poids=60.0
        )
    
    def test_frottis_model_form_valid_data(self):
        """Test formulaire frottis avec données valides"""
        class FrottisForm(ModelForm):
            class Meta:
                model = FrottisCV
                fields = ['antecedents', 'date_frottis', 'resultat']
        
        form_data = {
            'antecedents': self.antecedents.pk,
            'date_frottis': date(2024, 6, 15),
            'resultat': 'Normal - Absence de cellules anormales'
        }
        
        form = FrottisForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        frottis = form.save()
        self.assertEqual(frottis.antecedents, self.antecedents)
        self.assertEqual(frottis.date_frottis, date(2024, 6, 15))
        self.assertEqual(frottis.resultat, 'Normal - Absence de cellules anormales')
    
    def test_frottis_model_form_missing_required_fields(self):
        """Test formulaire frottis avec champs obligatoires manquants"""
        class FrottisForm(ModelForm):
            class Meta:
                model = FrottisCV
                fields = ['antecedents', 'date_frottis', 'resultat']
        
        # Données incomplètes
        form_data = {
            'antecedents': self.antecedents.pk,
            # date_frottis manquante
            'resultat': 'Normal'
        }
        
        form = FrottisForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_frottis', form.errors)
    
    def test_frottis_model_form_resultat_too_long(self):
        """Test formulaire frottis avec résultat trop long"""
        class FrottisForm(ModelForm):
            class Meta:
                model = FrottisCV
                fields = ['antecedents', 'date_frottis', 'resultat']
        
        long_resultat = 'A' * 501  # Dépasse la limite de 500 caractères
        
        form_data = {
            'antecedents': self.antecedents.pk,
            'date_frottis': date(2024, 6, 15),
            'resultat': long_resultat
        }
        
        form = FrottisForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('resultat', form.errors)
    
    def test_frottis_model_form_detailed_result(self):
        """Test formulaire frottis avec résultat médical détaillé"""
        class FrottisForm(ModelForm):
            class Meta:
                model = FrottisCV
                fields = ['antecedents', 'date_frottis', 'resultat']
        
        resultat_detaille = """
        Frottis cervico-vaginal en milieu liquide
        Qualité du prélèvement : Satisfaisante
        Flore : Lactobacilles prédominants
        Épithélium malpighien : Cellules de surface et intermédiaires normales
        Conclusion : Frottis normal, absence de lésion intra-épithéliale
        """
        
        form_data = {
            'antecedents': self.antecedents.pk,
            'date_frottis': date(2024, 3, 10),
            'resultat': resultat_detaille.strip()
        }
        
        form = FrottisForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        frottis = form.save()
        self.assertIn('Lactobacilles', frottis.resultat)
        self.assertIn('Frottis normal', frottis.resultat)
    
    def test_frottis_model_form_future_date_validation(self):
        """Test validation date future pour frottis"""
        from datetime import timedelta
        
        class FrottisForm(ModelForm):
            class Meta:
                model = FrottisCV
                fields = ['antecedents', 'date_frottis', 'resultat']
            
            def clean_date_frottis(self):
                date_frottis = self.cleaned_data['date_frottis']
                if date_frottis > date.today():
                    raise ValidationError("La date du frottis ne peut pas être dans le futur")
                return date_frottis
        
        future_date = date.today() + timedelta(days=1)
        
        form_data = {
            'antecedents': self.antecedents.pk,
            'date_frottis': future_date,
            'resultat': 'Test futur'
        }
        
        form = FrottisForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_frottis', form.errors)


class AntecedentsFormValidationTest(TestCase):
    """Tests spécifiques des validations métier pour les antécédents"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.caisse = Caisse.objects.create(nom="CAFAT")
        self.patiente = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse
        )
    
    def test_antecedents_one_per_patient_validation(self):
        """Test validation : un seul antécédent par patiente"""
        # Créer premier antécédent
        Antecedents.objects.create(
            patient=self.patiente,
            taille=1.65,
            poids=60.0
        )
        
        class AntecedentsForm(ModelForm):
            class Meta:
                model = Antecedents
                fields = ['patient', 'taille', 'poids']
            
            def clean_patient(self):
                patient = self.cleaned_data['patient']
                if Antecedents.objects.filter(patient=patient).exists():
                    raise ValidationError("Cette patiente a déjà des antécédents enregistrés")
                return patient
        
        # Tentative de créer un second antécédent
        form_data = {
            'patient': self.patiente.pk,
            'taille': 1.70,
            'poids': 65.0
        }
        
        form = AntecedentsForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('patient', form.errors)
    
    def test_antecedents_imc_coherence_validation(self):
        """Test validation cohérence IMC avec données biométriques"""
        class AntecedentsForm(ModelForm):
            class Meta:
                model = Antecedents
                fields = ['patient', 'taille', 'poids']
            
            def clean(self):
                cleaned_data = super().clean()
                taille = cleaned_data.get('taille')
                poids = cleaned_data.get('poids')
                
                if taille and poids:
                    imc = poids / (taille ** 2)
                    if imc < 10 or imc > 60:
                        raise ValidationError("Les données biométriques semblent incohérentes (IMC extrême)")
                
                return cleaned_data
        
        # Données incohérentes (IMC extrême)
        form_data = {
            'patient': self.patiente.pk,
            'taille': 2.0,  # 2m
            'poids': 30.0   # 30kg -> IMC = 7.5 (extrême)
        }
        
        form = AntecedentsForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_antecedents_medical_consistency_validation(self):
        """Test validation cohérence des données médicales"""
        class AntecedentsForm(ModelForm):
            class Meta:
                model = Antecedents
                fields = ['patient', 'asthme', 'allergie']
            
            def clean(self):
                cleaned_data = super().clean()
                asthme = cleaned_data.get('asthme')
                allergie = cleaned_data.get('allergie', '').strip()
                
                if asthme and not allergie:
                    self.add_error('allergie', "Précisez les allergies en cas d'asthme")
                
                return cleaned_data
        
        # Asthme coché mais pas d'allergie spécifiée
        form_data = {
            'patient': self.patiente.pk,
            'asthme': True,
            'allergie': ''  # Vide
        }
        
        form = AntecedentsForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('allergie', form.errors)
    
    def test_frottis_chronological_order_validation(self):
        """Test validation ordre chronologique des frottis"""
        # Créer un frottis existant
        antecedents = Antecedents.objects.create(
            patient=self.patiente,
            taille=1.65,
            poids=60.0
        )
        
        frottis_existant = FrottisCV.objects.create(
            antecedents=antecedents,
            date_frottis=date(2024, 6, 15),
            resultat='Premier frottis'
        )
        
        class FrottisForm(ModelForm):
            class Meta:
                model = FrottisCV
                fields = ['antecedents', 'date_frottis', 'resultat']
            
            def clean_date_frottis(self):
                date_frottis = self.cleaned_data['date_frottis']
                antecedents = self.cleaned_data.get('antecedents')
                
                if antecedents:
                    dernier_frottis = antecedents.frottis.first()  # Le plus récent
                    if dernier_frottis and date_frottis > dernier_frottis.date_frottis:
                        if (date_frottis - dernier_frottis.date_frottis).days < 180:
                            raise ValidationError("Un frottis trop récent existe déjà (minimum 6 mois)")
                
                return date_frottis
        
        # Tentative d'ajouter un frottis trop récent (1 mois après)
        form_data = {
            'antecedents': antecedents.pk,
            'date_frottis': date(2024, 7, 15),  # 1 mois après le 15/06
            'resultat': 'Frottis trop récent'
        }
        
        form = FrottisForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_frottis', form.errors)
        
        # Test avec un frottis assez espacé (valide)
        form_data_valid = {
            'antecedents': antecedents.pk,
            'date_frottis': date(2025, 1, 15),  # 7 mois après
            'resultat': 'Frottis valide'
        }
        
        form_valid = FrottisForm(data=form_data_valid)
        self.assertTrue(form_valid.is_valid())