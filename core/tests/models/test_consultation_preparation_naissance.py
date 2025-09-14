"""
Tests pour le modèle ConsultationPreparationNaissance
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date, timedelta

from core.models import ConsultationPreparationNaissance, Patient, SageFemme, Caisse, ConditionPaiement


class ConsultationPreparationNaissanceModelTest(TestCase):
    """Tests pour le modèle ConsultationPreparationNaissance"""
    
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
        
        # Créer une sage-femme
        self.sage_femme = SageFemme.objects.create(
            nom="Dupont",
            prenom="Marie",
            titre="Sage-femme",
            telephone="0123456789",
            email="marie@test.com",
            numero_cafat="123456789",
            ridet="123456789",
            rib="12345678901234567890",
            banque="BCI",
            situation="titulaire"
        )
        
        # Créer une patiente femme avec DDG
        self.patiente = Patient.objects.create(
            nom="Martin",
            prenom="Julie",
            date_naissance=date(1990, 5, 15),
            telephone="0123456789",
            type_patient="femme",
            caisse=self.caisse,
            date_debut_grossesse=date(2024, 1, 1)
        )
        
        # Créer une patiente femme sans DDG
        self.patiente_sans_ddg = Patient.objects.create(
            nom="Dubois",
            prenom="Sophie",
            date_naissance=date(1992, 3, 20),
            telephone="0123456790",
            type_patient="femme",
            caisse=self.caisse
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
    
    def test_creation_consultation_preparation_naissance_valide(self):
        """Test création d'une consultation valide"""
        consultation = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today(),
            theme_aborde="Respiration et relaxation",
            a_prevoir="Revoir les exercices",
            created_by=self.sage_femme
        )
        
        self.assertEqual(consultation.patient, self.patiente)
        self.assertEqual(consultation.date_consultation, date.today())
        self.assertEqual(consultation.theme_aborde, "Respiration et relaxation")
        self.assertEqual(consultation.a_prevoir, "Revoir les exercices")
        self.assertEqual(consultation.created_by, self.sage_femme)
        self.assertIsNotNone(consultation.created_at)
        self.assertIsNotNone(consultation.updated_at)
    
    def test_consultation_preparation_naissance_avec_calcul_sa(self):
        """Test calcul automatique des SA"""
        date_consultation = self.patiente.date_debut_grossesse + timedelta(days=154)  # 22 semaines
        
        consultation = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date_consultation,
            theme_aborde="Allaitement maternel"
        )
        
        self.assertEqual(consultation.semaines_amenorrhee, "22 SA")
    
    def test_consultation_preparation_naissance_avec_calcul_sa_et_jours(self):
        """Test calcul SA avec jours restants"""
        date_consultation = self.patiente.date_debut_grossesse + timedelta(days=157)  # 22 SA + 3j
        
        consultation = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date_consultation,
            theme_aborde="Positions d'accouchement"
        )
        
        self.assertEqual(consultation.semaines_amenorrhee, "22 SA + 3j")
    
    def test_consultation_preparation_naissance_sans_ddg(self):
        """Test avec patiente sans DDG"""
        consultation = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente_sans_ddg,
            date_consultation=date.today(),
            theme_aborde="Préparation générale"
        )
        
        self.assertIsNone(consultation.semaines_amenorrhee)
    
    def test_validation_date_future(self):
        """Test validation : date dans le futur"""
        date_future = date.today() + timedelta(days=1)
        
        consultation = ConsultationPreparationNaissance(
            patient=self.patiente,
            date_consultation=date_future,
            theme_aborde="Test futur"
        )
        
        with self.assertRaises(ValidationError) as context:
            consultation.full_clean()
        
        self.assertIn('date_consultation', context.exception.error_dict)
        self.assertIn('futur', str(context.exception.error_dict['date_consultation'][0]))
    
    def test_validation_patient_bebe(self):
        """Test validation : patient bébé non autorisé"""
        consultation = ConsultationPreparationNaissance(
            patient=self.bebe,
            date_consultation=date.today(),
            theme_aborde="Test bébé"
        )
        
        with self.assertRaises(ValidationError) as context:
            consultation.full_clean()
        
        self.assertIn('patient', context.exception.error_dict)
        self.assertIn('femmes', str(context.exception.error_dict['patient'][0]))
    
    def test_str_representation(self):
        """Test représentation string"""
        consultation = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date(2024, 6, 15),
            theme_aborde="Test représentation"
        )
        
        expected = f"Préparation naissance - {self.patiente.nom_complet} du 15/06/2024"
        self.assertEqual(str(consultation), expected)
    
    def test_meta_options(self):
        """Test options Meta du modèle"""
        meta = ConsultationPreparationNaissance._meta
        
        self.assertEqual(meta.verbose_name, "6.1.5 Consultation Préparation à la Naissance")
        self.assertEqual(meta.verbose_name_plural, "6.1.5 Consultations Préparation à la Naissance")
        self.assertEqual(meta.ordering, ['-date_consultation', '-created_at'])
    
    def test_consultation_resume_property(self):
        """Test propriété consultation_resume"""
        consultation = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today(),
            theme_aborde="Respiration et relaxation",
            a_prevoir="Revoir les exercices"
        )
        
        expected = "Thème: Respiration et relaxation | À prévoir: Revoir les exercices"
        self.assertEqual(consultation.consultation_resume, expected)
    
    def test_consultation_resume_property_theme_seulement(self):
        """Test propriété consultation_resume avec thème seulement"""
        consultation = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today(),
            theme_aborde="Allaitement maternel"
        )
        
        expected = "Thème: Allaitement maternel"
        self.assertEqual(consultation.consultation_resume, expected)
    
    def test_consultation_resume_property_a_prevoir_seulement(self):
        """Test propriété consultation_resume avec à prévoir seulement"""
        consultation = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today(),
            a_prevoir="Prévoir visite maternité"
        )
        
        expected = "À prévoir: Prévoir visite maternité"
        self.assertEqual(consultation.consultation_resume, expected)
    
    def test_consultation_resume_property_vide(self):
        """Test propriété consultation_resume sans contenu"""
        consultation = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today()
        )
        
        expected = "Consultation de préparation à la naissance"
        self.assertEqual(consultation.consultation_resume, expected)
    
    def test_sa_affichage_property(self):
        """Test propriété sa_affichage"""
        consultation = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=self.patiente.date_debut_grossesse + timedelta(days=140),
            theme_aborde="Test SA"
        )
        
        self.assertEqual(consultation.sa_affichage, "20 SA")
    
    def test_sa_affichage_property_sans_sa(self):
        """Test propriété sa_affichage sans SA"""
        consultation = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente_sans_ddg,
            date_consultation=date.today(),
            theme_aborde="Test sans SA"
        )
        
        self.assertEqual(consultation.sa_affichage, "SA non calculées")
    
    def test_calculer_semaines_amenorrhee_ddg_posterieure(self):
        """Test calcul SA avec DDG postérieure à la consultation"""
        date_consultation = self.patiente.date_debut_grossesse - timedelta(days=10)
        
        consultation = ConsultationPreparationNaissance(
            patient=self.patiente,
            date_consultation=date_consultation
        )
        
        sa = consultation.calculer_semaines_amenorrhee()
        self.assertEqual(sa, "DDG postérieure")
    
    def test_calculer_semaines_amenorrhee_sans_patient(self):
        """Test calcul SA sans patient"""
        # Créer une consultation avec un patient mais tester la méthode avec patient=None
        consultation = ConsultationPreparationNaissance(
            patient=self.patiente_sans_ddg,
            date_consultation=date.today(),
            theme_aborde="Test"
        )
        
        # Tester directement la méthode avec patient=None
        consultation.patient = None
        sa = consultation.calculer_semaines_amenorrhee()
        self.assertIsNone(sa)
    
    def test_calculer_semaines_amenorrhee_sans_ddg(self):
        """Test calcul SA sans DDG"""
        consultation = ConsultationPreparationNaissance(
            patient=self.patiente_sans_ddg,
            date_consultation=date.today()
        )
        
        sa = consultation.calculer_semaines_amenorrhee()
        self.assertIsNone(sa)
    
    def test_ordering_consultations(self):
        """Test ordre des consultations"""
        # Créer plusieurs consultations à dates différentes
        consultation1 = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date(2024, 1, 10),
            theme_aborde="Première consultation"
        )
        
        consultation2 = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date(2024, 1, 20),
            theme_aborde="Deuxième consultation"
        )
        
        consultation3 = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date(2024, 1, 15),
            theme_aborde="Troisième consultation"
        )
        
        consultations = list(ConsultationPreparationNaissance.objects.all())
        
        # Vérifier l'ordre : plus récente en premier
        self.assertEqual(consultations[0], consultation2)  # 20/01
        self.assertEqual(consultations[1], consultation3)  # 15/01
        self.assertEqual(consultations[2], consultation1)  # 10/01
    
    def test_related_name_patient(self):
        """Test related_name avec patient"""
        consultation = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today(),
            theme_aborde="Test related name"
        )
        
        consultations = self.patiente.consultations_preparation_naissance.all()
        self.assertIn(consultation, consultations)
    
    def test_related_name_sage_femme(self):
        """Test related_name avec sage-femme"""
        consultation = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today(),
            theme_aborde="Test créateur",
            created_by=self.sage_femme
        )
        
        consultations = self.sage_femme.consultations_preparation_naissance_creees.all()
        self.assertIn(consultation, consultations)
    
    def test_set_null_sage_femme(self):
        """Test SET_NULL lors de suppression sage-femme"""
        consultation = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today(),
            theme_aborde="Test SET_NULL",
            created_by=self.sage_femme
        )
        
        self.sage_femme.delete()
        consultation.refresh_from_db()
        
        self.assertIsNone(consultation.created_by)
    
    def test_cascade_delete_patient(self):
        """Test CASCADE lors de suppression patient"""
        consultation = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today(),
            theme_aborde="Test CASCADE"
        )
        
        consultation_id = consultation.id
        self.patiente.delete()
        
        with self.assertRaises(ConsultationPreparationNaissance.DoesNotExist):
            ConsultationPreparationNaissance.objects.get(id=consultation_id)
    
    def test_date_consultation_default(self):
        """Test valeur par défaut date_consultation"""
        # Tester que le champ a une valeur par défaut
        field = ConsultationPreparationNaissance._meta.get_field('date_consultation')
        self.assertIsNotNone(field.default)
        
        # Créer l'instance sans spécifier la date_consultation
        consultation = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            theme_aborde="Test default date"
        )
        
        # La valeur devrait être la date d'aujourd'hui
        self.assertEqual(consultation.date_consultation, date.today())
    
    def test_index_database(self):
        """Test présence des index de base de données"""
        meta = ConsultationPreparationNaissance._meta
        index_fields = []
        
        for index in meta.indexes:
            index_fields.extend(index.fields)
        
        # Vérifier que les champs attendus sont indexés
        self.assertIn('patient', index_fields)
        self.assertIn('date_consultation', index_fields)
        self.assertIn('created_by', index_fields)