"""
Tests pour le modèle Patient
Tests complets des fonctionnalités métier et validations
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date, timedelta
from core.models import Patient, Caisse


class PatientModelTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.caisse = Caisse.objects.create(
            nom="CAFAT"
        )
        
    def test_patient_creation_femme(self):
        """Test création d'une patiente femme"""
        patient = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse
        )
        
        self.assertEqual(patient.type_patient, 'femme')
        self.assertEqual(patient.nom, 'Dupont')
        self.assertEqual(patient.prenom, 'Marie')
        self.assertTrue(patient.is_active)
        self.assertIsNotNone(patient.created_at)
        self.assertIsNotNone(patient.updated_at)
    
    def test_patient_creation_bebe(self):
        """Test création d'un patient bébé avec mère"""
        mere = Patient.objects.create(
            type_patient='femme',
            nom='Martin',
            prenom='Sophie',
            date_naissance=date(1985, 3, 10),
            caisse=self.caisse
        )
        
        bebe = Patient.objects.create(
            type_patient='bebe',
            nom='Martin',
            prenom='Lucas',
            date_naissance=date.today() - timedelta(days=30),
            mere=mere,
            caisse=self.caisse
        )
        
        self.assertEqual(bebe.type_patient, 'bebe')
        self.assertEqual(bebe.mere, mere)
        self.assertEqual(bebe.nom, 'Martin')
        # Par défaut le modèle met True, mais la validation clean() empêchera la sauvegarde si on tente de valider
        # Ici on teste juste la création basique sans validation complète
    
    def test_nom_complet_property(self):
        """Test de la propriété nom_complet"""
        patient = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            caisse=self.caisse
        )
        
        self.assertEqual(patient.nom_complet, 'Marie Dupont')
    
    def test_age_calculation(self):
        """Test du calcul de l'âge"""
        # Patient né il y a exactement 30 ans
        naissance = date.today() - timedelta(days=30*365)  # Approximation
        patient = Patient.objects.create(
            type_patient='femme',
            nom='Test',
            prenom='Age',
            date_naissance=naissance,
            caisse=self.caisse
        )
        
        age = patient.age
        self.assertIsInstance(age, int)
        self.assertGreaterEqual(age, 29)
        self.assertLessEqual(age, 31)  # Approximation pour éviter les problèmes de dates
    
    def test_age_detail_property(self):
        """Test de la propriété age_detail"""
        # Bébé de quelques jours
        bebe = Patient.objects.create(
            type_patient='bebe',
            nom='Test',
            prenom='Bebe',
            date_naissance=date.today() - timedelta(days=10),
            caisse=self.caisse
        )
        
        age_detail = bebe.age_detail
        self.assertIn('jour', age_detail)
        
        # Adulte
        adulte = Patient.objects.create(
            type_patient='femme',
            nom='Test',
            prenom='Adulte',
            date_naissance=date.today() - timedelta(days=365*25),
            caisse=self.caisse
        )
        
        age_detail = adulte.age_detail
        self.assertIn('an', age_detail)
    
    def test_get_bebes_method(self):
        """Test de la méthode get_bebes"""
        mere = Patient.objects.create(
            type_patient='femme',
            nom='Mere',
            prenom='Test',
            date_naissance=date(1990, 1, 1),
            caisse=self.caisse
        )
        
        # Créer plusieurs bébés
        bebe1 = Patient.objects.create(
            type_patient='bebe',
            nom='Bebe1',
            prenom='Test',
            date_naissance=date.today() - timedelta(days=30),
            mere=mere,
            caisse=self.caisse
        )
        
        bebe2 = Patient.objects.create(
            type_patient='bebe',
            nom='Bebe2',
            prenom='Test',
            date_naissance=date.today() - timedelta(days=60),
            mere=mere,
            caisse=self.caisse
        )
        
        bebes = mere.get_bebes()
        self.assertEqual(bebes.count(), 2)
        self.assertIn(bebe1, bebes)
        self.assertIn(bebe2, bebes)
    
    def test_date_naissance_future_validation(self):
        """Test validation date de naissance future"""
        patient = Patient(
            type_patient='femme',
            nom='Test',
            prenom='Future',
            date_naissance=date.today() + timedelta(days=1),  # Date future
            caisse=self.caisse
        )
        
        with self.assertRaises(ValidationError):
            patient.full_clean()
    
    def test_date_debut_grossesse_future_validation(self):
        """Test validation date début grossesse future"""
        patient = Patient(
            type_patient='femme',
            nom='Test',
            prenom='Grossesse',
            date_naissance=date(1990, 1, 1),
            date_debut_grossesse=date.today() + timedelta(days=1),  # Date future
            caisse=self.caisse
        )
        
        with self.assertRaises(ValidationError):
            patient.full_clean()
    
    def test_bebe_cannot_be_titulaire(self):
        """Test qu'un bébé ne peut pas être assuré titulaire"""
        mere = Patient.objects.create(
            type_patient='femme',
            nom='Mere',
            prenom='Test',
            date_naissance=date(1990, 1, 1),
            caisse=self.caisse
        )
        
        bebe = Patient(
            type_patient='bebe',
            nom='Bebe',
            prenom='Test',
            date_naissance=date.today() - timedelta(days=30),
            mere=mere,
            est_assure_titulaire=True,  # Invalide pour un bébé
            caisse=self.caisse
        )
        
        with self.assertRaises(ValidationError):
            bebe.full_clean()
    
    def test_bebe_must_have_mere(self):
        """Test qu'un bébé doit avoir une mère"""
        bebe = Patient(
            type_patient='bebe',
            nom='Bebe',
            prenom='Test',
            date_naissance=date.today() - timedelta(days=30),
            mere=None,  # Pas de mère définie
            caisse=self.caisse
        )
        
        with self.assertRaises(ValidationError):
            bebe.full_clean()
    
    def test_femme_cannot_have_mere(self):
        """Test qu'une femme ne peut pas avoir de mère définie"""
        mere = Patient.objects.create(
            type_patient='femme',
            nom='Mere',
            prenom='Test',
            date_naissance=date(1990, 1, 1),
            caisse=self.caisse
        )
        
        femme = Patient(
            type_patient='femme',
            nom='Femme',
            prenom='Test',
            date_naissance=date(1995, 1, 1),
            mere=mere,  # Invalide pour une femme
            caisse=self.caisse
        )
        
        with self.assertRaises(ValidationError):
            femme.full_clean()
    
    def test_patient_str_method(self):
        """Test de la méthode __str__"""
        patient = Patient.objects.create(
            type_patient='femme',
            nom='Test',
            prenom='Str',
            date_naissance=date(1990, 1, 1),
            caisse=self.caisse
        )
        
        self.assertEqual(str(patient), 'Str Test')
    
    def test_patient_ordering(self):
        """Test de l'ordering par défaut"""
        # Créer plusieurs patients
        patient1 = Patient.objects.create(
            type_patient='femme',
            nom='Zebra',
            prenom='A',
            date_naissance=date(1990, 1, 1),
            caisse=self.caisse
        )
        
        patient2 = Patient.objects.create(
            type_patient='femme',
            nom='Alpha',
            prenom='Z',
            date_naissance=date(1990, 1, 1),
            caisse=self.caisse
        )
        
        patients = list(Patient.objects.all())
        self.assertEqual(patients[0], patient2)  # Alpha avant Zebra
        self.assertEqual(patients[1], patient1)
    
    def test_patient_meta_options(self):
        """Test des options Meta du modèle"""
        meta = Patient._meta
        self.assertEqual(meta.verbose_name, '6. Patient')
        self.assertEqual(meta.verbose_name_plural, '6. Patients')
        self.assertEqual(meta.ordering, ['nom', 'prenom'])
    
    def test_patient_fields_max_length(self):
        """Test des longueurs maximales des champs"""
        # Test nom trop long
        long_nom = 'x' * 101  # Plus que la limite de 100
        patient = Patient(
            type_patient='femme',
            nom=long_nom,
            prenom='Test',
            date_naissance=date(1990, 1, 1),
            caisse=self.caisse
        )
        
        with self.assertRaises(ValidationError):
            patient.full_clean()
    
    def test_patient_active_inactive_toggle(self):
        """Test du toggle actif/inactif"""
        patient = Patient.objects.create(
            type_patient='femme',
            nom='Test',
            prenom='Toggle',
            date_naissance=date(1990, 1, 1),
            caisse=self.caisse
        )
        
        # Par défaut actif
        self.assertTrue(patient.is_active)
        
        # Désactiver
        patient.is_active = False
        patient.save()
        patient.refresh_from_db()
        self.assertFalse(patient.is_active)
        
        # Réactiver
        patient.is_active = True
        patient.save()
        patient.refresh_from_db()
        self.assertTrue(patient.is_active)
    
    def test_patient_caisse_relationship(self):
        """Test de la relation avec Caisse"""
        patient = Patient.objects.create(
            type_patient='femme',
            nom='Test',
            prenom='Caisse',
            date_naissance=date(1990, 1, 1),
            caisse=self.caisse
        )
        
        self.assertEqual(patient.caisse, self.caisse)
        self.assertIn(patient, self.caisse.patient_set.all())
    
    def test_patient_without_caisse(self):
        """Test patient sans caisse (optionnel)"""
        patient = Patient.objects.create(
            type_patient='femme',
            nom='Test',
            prenom='SansCaisse',
            date_naissance=date(1990, 1, 1)
            # Pas de caisse définie
        )
        
        self.assertIsNone(patient.caisse)
        self.assertEqual(patient.nom, 'Test')
    
    def test_date_naissance_assure_validation(self):
        """Test validation date naissance assuré future"""
        patient = Patient(
            type_patient='femme',
            nom='Test',
            prenom='AssureFuture',
            date_naissance=date(1990, 1, 1),
            date_naissance_assure=date.today() + timedelta(days=1),  # Future
            caisse=self.caisse
        )
        
        with self.assertRaises(ValidationError):
            patient.full_clean()