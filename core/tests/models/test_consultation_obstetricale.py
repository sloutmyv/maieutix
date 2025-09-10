"""
Tests pour le modèle ConsultationObstetricale
Tests complets des fonctionnalités métier et validations
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date, timedelta
from core.models import ConsultationObstetricale, Patient, Caisse, SageFemme
from authentication.models import SageFemmeUser


class ConsultationObstetricaleModelTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.caisse = Caisse.objects.create(
            nom="CAFAT"
        )
        
        # Patient femme enceinte
        self.patient_femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse,
            date_debut_grossesse=date.today() - timedelta(days=140)  # 20 SA environ
        )
        
        # Patient femme sans grossesse
        self.patient_femme_sans_grossesse = Patient.objects.create(
            type_patient='femme',
            nom='Martin',
            prenom='Sophie',
            date_naissance=date(1985, 3, 20),
            telephone='0123456788',
            caisse=self.caisse
        )
        
        # Patient bébé (ne devrait pas avoir de consultation obstétricale)
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
    
    def test_consultation_obstetricale_creation_valid(self):
        """Test de création d'une consultation obstétricale valide"""
        consultation = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today(),
            motif="Contrôle de routine",
            tension_systolique=120,
            tension_diastolique=80,
            poids=68.5,
            created_by=self.sage_femme
        )
        
        self.assertEqual(consultation.patient, self.patient_femme)
        self.assertEqual(consultation.motif, "Contrôle de routine")
        self.assertEqual(consultation.tension_systolique, 120)
        self.assertEqual(consultation.tension_diastolique, 80)
        self.assertEqual(consultation.poids, 68.5)
        self.assertIsNotNone(consultation.created_at)
        self.assertIsNotNone(consultation.updated_at)
    
    def test_consultation_obstetricale_str_representation(self):
        """Test de la représentation string du modèle"""
        consultation = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date(2024, 1, 15),
            motif="Test consultation"
        )
        
        expected_str = f"Consultation du 15/01/2024 - {self.patient_femme.nom_complet}"
        self.assertEqual(str(consultation), expected_str)
    
    def test_calcul_sa_automatique_lors_sauvegarde(self):
        """Test du calcul automatique de la SA lors de la sauvegarde"""
        consultation = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today(),
            motif="Contrôle SA"
        )
        
        # Vérifier que la SA a été calculée automatiquement
        self.assertIsNotNone(consultation.semaines_amenorrhee)
        self.assertIn("SA", consultation.semaines_amenorrhee)
    
    def test_calcul_sa_avec_ddg(self):
        """Test du calcul de SA avec une DDG définie"""
        # Définir une DDG précise
        ddg = date.today() - timedelta(days=168)  # 24 semaines exactement
        patient_test = Patient.objects.create(
            type_patient='femme',
            nom='Test',
            prenom='SA',
            date_naissance=date(1995, 1, 1),
            telephone='0123456787',
            caisse=self.caisse,
            date_debut_grossesse=ddg
        )
        
        consultation = ConsultationObstetricale.objects.create(
            patient=patient_test,
            date_consultation=date.today(),
            motif="Test SA"
        )
        
        self.assertEqual(consultation.semaines_amenorrhee, "24 SA")
    
    def test_calcul_sa_avec_jours_supplementaires(self):
        """Test du calcul de SA avec des jours supplémentaires"""
        # DDG avec 24 SA + 3 jours
        ddg = date.today() - timedelta(days=171)  # 24 SA + 3j
        patient_test = Patient.objects.create(
            type_patient='femme',
            nom='Test',
            prenom='SA Plus',
            date_naissance=date(1995, 1, 1),
            telephone='0123456786',
            caisse=self.caisse,
            date_debut_grossesse=ddg
        )
        
        consultation = ConsultationObstetricale.objects.create(
            patient=patient_test,
            date_consultation=date.today(),
            motif="Test SA avec jours"
        )
        
        self.assertEqual(consultation.semaines_amenorrhee, "24 SA + 3j")
    
    def test_calcul_sa_sans_ddg(self):
        """Test du calcul de SA sans DDG définie"""
        consultation = ConsultationObstetricale.objects.create(
            patient=self.patient_femme_sans_grossesse,
            date_consultation=date.today(),
            motif="Consultation sans DDG"
        )
        
        # SA devrait être vide si pas de DDG
        self.assertEqual(consultation.semaines_amenorrhee, "")
    
    def test_calcul_sa_grossesse_future(self):
        """Test du calcul de SA pour une grossesse future"""
        ddg_future = date.today() + timedelta(days=10)
        patient_test = Patient.objects.create(
            type_patient='femme',
            nom='Test',
            prenom='Future',
            date_naissance=date(1995, 1, 1),
            telephone='0123456785',
            caisse=self.caisse,
            date_debut_grossesse=ddg_future
        )
        
        consultation = ConsultationObstetricale.objects.create(
            patient=patient_test,
            date_consultation=date.today(),
            motif="Grossesse future"
        )
        
        self.assertEqual(consultation.semaines_amenorrhee, "Grossesse pas encore commencée")
    
    def test_validation_tension_arterielle_coherente(self):
        """Test de validation de la cohérence de la tension artérielle"""
        with self.assertRaises(ValidationError):
            consultation = ConsultationObstetricale(
                patient=self.patient_femme,
                date_consultation=date.today(),
                motif="Test tension invalide",
                tension_systolique=80,  # Plus faible que la diastolique
                tension_diastolique=120
            )
            consultation.full_clean()
    
    def test_validation_tension_incomplete(self):
        """Test de validation tension incomplète"""
        with self.assertRaises(ValidationError):
            consultation = ConsultationObstetricale(
                patient=self.patient_femme,
                date_consultation=date.today(),
                motif="Test tension incomplète",
                tension_systolique=120
                # tension_diastolique manquante
            )
            consultation.full_clean()
    
    def test_validation_date_future(self):
        """Test de validation date de consultation future"""
        with self.assertRaises(ValidationError):
            consultation = ConsultationObstetricale(
                patient=self.patient_femme,
                date_consultation=date.today() + timedelta(days=1),
                motif="Consultation future"
            )
            consultation.full_clean()
    
    def test_validation_motif_obligatoire(self):
        """Test de validation du motif obligatoire"""
        with self.assertRaises(ValidationError):
            consultation = ConsultationObstetricale(
                patient=self.patient_femme,
                date_consultation=date.today()
                # motif manquant
            )
            consultation.full_clean()
    
    def test_validation_poids_limites(self):
        """Test de validation des limites de poids"""
        with self.assertRaises(ValidationError):
            consultation = ConsultationObstetricale(
                patient=self.patient_femme,
                date_consultation=date.today(),
                motif="Test poids invalide",
                poids=250  # Au-dessus de la limite
            )
            consultation.full_clean()
    
    def test_validation_tension_limites(self):
        """Test de validation des limites de tension"""
        with self.assertRaises(ValidationError):
            consultation = ConsultationObstetricale(
                patient=self.patient_femme,
                date_consultation=date.today(),
                motif="Test tension hors limites",
                tension_systolique=300,  # Au-dessus de la limite
                tension_diastolique=80
            )
            consultation.full_clean()
    
    def test_tension_complete_property(self):
        """Test de la propriété tension_complete"""
        consultation = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today(),
            motif="Test tension complète",
            tension_systolique=130,
            tension_diastolique=85
        )
        
        self.assertEqual(consultation.tension_complete, "130/85 mmHg")
        
        # Test sans tension
        consultation_sans_tension = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today() - timedelta(days=1),
            motif="Sans tension"
        )
        self.assertIsNone(consultation_sans_tension.tension_complete)
    
    def test_tension_interpretation_property(self):
        """Test de la propriété tension_interpretation"""
        # Tension normale
        consultation_normale = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today(),
            motif="Tension normale",
            tension_systolique=110,
            tension_diastolique=70
        )
        self.assertEqual(consultation_normale.tension_interpretation, "Tension normale")
        
        # Hypertension
        consultation_hypertension = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today() - timedelta(days=1),
            motif="Hypertension",
            tension_systolique=150,
            tension_diastolique=95
        )
        self.assertEqual(consultation_hypertension.tension_interpretation, "Hypertension stade 2")
    
    def test_imc_property(self):
        """Test de la propriété IMC"""
        # Créer des antécédents avec taille pour le calcul IMC
        from core.models import Antecedents
        antecedents = Antecedents.objects.create(
            patient=self.patient_femme,
            taille=1.65
        )
        
        consultation = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today(),
            motif="Test IMC",
            poids=60.0
        )
        
        # IMC = 60 / (1.65^2) = 22.0
        self.assertEqual(consultation.imc, 22.0)
    
    def test_resume_consultation_property(self):
        """Test de la propriété resume_consultation"""
        consultation = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today(),
            motif="Contrôle de routine 20 SA avec examen complet",
            tension_systolique=120,
            tension_diastolique=80,
            poids=65.5
        )
        
        resume = consultation.resume_consultation
        self.assertIn("Contrôle de routine 20 SA avec examen complet", resume)
        self.assertIn("TA: 120/80 mmHg", resume)
        self.assertIn("Poids: 65.5kg", resume)
    
    def test_meta_options(self):
        """Test des options Meta du modèle"""
        self.assertEqual(ConsultationObstetricale._meta.verbose_name, "6.1.3.2 Consultation Obstétricale")
        self.assertEqual(ConsultationObstetricale._meta.verbose_name_plural, "6.1.3.2 Consultations Obstétricales")
        self.assertEqual(ConsultationObstetricale._meta.ordering, ['-date_consultation', '-created_at'])
    
    def test_champs_optionnels(self):
        """Test que les champs optionnels peuvent être vides"""
        consultation = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today(),
            motif="Consultation minimale"
            # Tous les autres champs optionnels omis
        )
        
        self.assertIsNone(consultation.tension_systolique)
        self.assertIsNone(consultation.tension_diastolique)
        self.assertIsNone(consultation.poids)
        self.assertEqual(consultation.examen, "")
        self.assertEqual(consultation.prescription, "")
        self.assertEqual(consultation.notes, "")
    
    def test_relation_patient_required(self):
        """Test que la relation patient est obligatoire"""
        with self.assertRaises(ValidationError):
            consultation = ConsultationObstetricale(
                date_consultation=date.today(),
                motif="Sans patient"
            )
            consultation.full_clean()
    
    def test_created_by_optional(self):
        """Test que created_by est optionnel"""
        consultation = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today(),
            motif="Sans sage-femme"
        )
        
        self.assertIsNone(consultation.created_by)
    
    def test_mise_a_jour_sa_lors_modification(self):
        """Test que la SA est recalculée lors de la modification"""
        consultation = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today(),
            motif="Test modification"
        )
        
        sa_initiale = consultation.semaines_amenorrhee
        
        # Modifier la date de consultation
        consultation.date_consultation = date.today() - timedelta(days=7)
        consultation.save()
        
        # La SA devrait être différente
        self.assertNotEqual(consultation.semaines_amenorrhee, sa_initiale)