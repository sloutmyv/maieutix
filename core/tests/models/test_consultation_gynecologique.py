"""
Tests pour le modèle ConsultationGynecologique
Tests complets des fonctionnalités métier et validations
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date, timedelta
from core.models import ConsultationGynecologique, Patient, Caisse, SageFemme, Antecedents
from authentication.models import SageFemmeUser


class ConsultationGynecologiqueModelTest(TestCase):
    
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
            telephone='0123456789',
            caisse=self.caisse
        )
        
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
            numero_cafat='12345',
            ridet='RIDET123',
            rib='RIB123456789',
            banque='BCI',
            situation='titulaire'
        )
        
        # Créer des antécédents avec taille pour tester l'IMC
        self.antecedents = Antecedents.objects.create(
            patient=self.patient_femme,
            taille=1.65  # 1m65 pour calculer l'IMC
        )
        
    def test_consultation_creation_valid(self):
        """Test création d'une consultation valide"""
        consultation = ConsultationGynecologique.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today(),
            tension_systolique=120,
            tension_diastolique=80,
            poids=65.5,
            motif="Consultation de routine",
            examen="RAS",
            prescription="Aucune",
            created_by=self.sage_femme
        )
        
        self.assertEqual(consultation.patient, self.patient_femme)
        self.assertEqual(consultation.tension_systolique, 120)
        self.assertEqual(consultation.tension_diastolique, 80)
        self.assertEqual(consultation.poids, 65.5)
        self.assertEqual(consultation.motif, "Consultation de routine")
        self.assertIsNotNone(consultation.created_at)
        self.assertIsNotNone(consultation.updated_at)

    def test_consultation_creation_minimal(self):
        """Test création d'une consultation avec données minimales"""
        consultation = ConsultationGynecologique.objects.create(
            patient=self.patient_femme,
            motif="Consultation simple"
        )
        
        self.assertEqual(consultation.patient, self.patient_femme)
        self.assertEqual(consultation.motif, "Consultation simple")
        self.assertEqual(consultation.date_consultation, date.today())
        self.assertIsNone(consultation.tension_systolique)
        self.assertIsNone(consultation.poids)

    def test_tension_complete_property(self):
        """Test de la propriété tension_complete"""
        consultation = ConsultationGynecologique(
            patient=self.patient_femme,
            tension_systolique=140,
            tension_diastolique=90,
            motif="Test tension"
        )
        
        self.assertEqual(consultation.tension_complete, "140/90 mmHg")

    def test_tension_complete_property_incomplete(self):
        """Test tension_complete avec données incomplètes"""
        consultation = ConsultationGynecologique(
            patient=self.patient_femme,
            tension_systolique=140,
            motif="Test tension incomplète"
        )
        
        self.assertIsNone(consultation.tension_complete)

    def test_tension_interpretation_normal(self):
        """Test interprétation tension normale"""
        consultation = ConsultationGynecologique(
            patient=self.patient_femme,
            tension_systolique=110,
            tension_diastolique=70,
            motif="Test tension normale"
        )
        
        self.assertEqual(consultation.tension_interpretation, "Tension normale")

    def test_tension_interpretation_hypertension(self):
        """Test interprétation hypertension"""
        consultation = ConsultationGynecologique(
            patient=self.patient_femme,
            tension_systolique=150,
            tension_diastolique=95,
            motif="Test hypertension"
        )
        
        self.assertEqual(consultation.tension_interpretation, "Hypertension stade 2")

    def test_tension_interpretation_crise(self):
        """Test interprétation crise hypertensive"""
        consultation = ConsultationGynecologique(
            patient=self.patient_femme,
            tension_systolique=200,
            tension_diastolique=130,
            motif="Test crise"
        )
        
        self.assertEqual(consultation.tension_interpretation, "Crise hypertensive")

    def test_imc_calculation(self):
        """Test calcul de l'IMC avec antécédents"""
        consultation = ConsultationGynecologique(
            patient=self.patient_femme,
            poids=65.5,
            motif="Test IMC"
        )
        
        # IMC = 65.5 / (1.65^2) = 24.1
        expected_imc = round(65.5 / (1.65 ** 2), 1)
        self.assertEqual(consultation.imc, expected_imc)

    def test_imc_sans_poids(self):
        """Test IMC sans poids"""
        consultation = ConsultationGynecologique(
            patient=self.patient_femme,
            motif="Test sans poids"
        )
        
        self.assertIsNone(consultation.imc)

    def test_resume_consultation_property(self):
        """Test de la propriété resume_consultation"""
        consultation = ConsultationGynecologique(
            patient=self.patient_femme,
            motif="Consultation pour douleurs abdominales importantes",
            tension_systolique=130,
            tension_diastolique=85,
            poids=68.0
        )
        
        resume = consultation.resume_consultation
        self.assertIn("Consultation pour douleurs abdominales", resume)
        self.assertIn("TA: 130/85 mmHg", resume)
        self.assertIn("Poids: 68.0kg", resume)

    def test_resume_consultation_motif_long(self):
        """Test résumé avec motif long (troncature)"""
        motif_long = "Consultation pour des douleurs très importantes qui durent depuis plusieurs semaines"
        consultation = ConsultationGynecologique(
            patient=self.patient_femme,
            motif=motif_long
        )
        
        resume = consultation.resume_consultation
        self.assertTrue(resume.startswith("Motif: Consultation pour des douleurs très importan"))
        self.assertIn("...", resume)

    def test_validation_date_future(self):
        """Test validation date future"""
        consultation = ConsultationGynecologique(
            patient=self.patient_femme,
            date_consultation=date.today() + timedelta(days=1),
            motif="Test date future"
        )
        
        with self.assertRaises(ValidationError) as context:
            consultation.full_clean()
        
        self.assertIn('date_consultation', context.exception.message_dict)

    def test_validation_tension_coherence(self):
        """Test validation cohérence des tensions"""
        consultation = ConsultationGynecologique(
            patient=self.patient_femme,
            tension_systolique=80,
            tension_diastolique=120,  # Diastolique > Systolique
            motif="Test tension incohérente"
        )
        
        with self.assertRaises(ValidationError) as context:
            consultation.full_clean()
        
        self.assertIn('tension_systolique', context.exception.message_dict)

    def test_validation_tension_incomplete_sys(self):
        """Test validation tension incomplète (systolique seulement)"""
        consultation = ConsultationGynecologique(
            patient=self.patient_femme,
            tension_systolique=120,
            motif="Test tension incomplète"
        )
        
        with self.assertRaises(ValidationError) as context:
            consultation.full_clean()
        
        self.assertIn('__all__', context.exception.message_dict)

    def test_validation_tension_incomplete_dia(self):
        """Test validation tension incomplète (diastolique seulement)"""
        consultation = ConsultationGynecologique(
            patient=self.patient_femme,
            tension_diastolique=80,
            motif="Test tension incomplète"
        )
        
        with self.assertRaises(ValidationError) as context:
            consultation.full_clean()
        
        self.assertIn('__all__', context.exception.message_dict)

    def test_validation_tension_valeurs_limites(self):
        """Test validation des valeurs limites de tension"""
        # Tension systolique trop faible
        consultation1 = ConsultationGynecologique(
            patient=self.patient_femme,
            tension_systolique=70,  # < 80
            tension_diastolique=50,
            motif="Test limite basse"
        )
        
        with self.assertRaises(ValidationError):
            consultation1.full_clean()
        
        # Tension diastolique trop élevée
        consultation2 = ConsultationGynecologique(
            patient=self.patient_femme,
            tension_systolique=140,
            tension_diastolique=160,  # > 150
            motif="Test limite haute"
        )
        
        with self.assertRaises(ValidationError):
            consultation2.full_clean()

    def test_validation_poids_limites(self):
        """Test validation des limites de poids"""
        # Poids trop faible
        consultation1 = ConsultationGynecologique(
            patient=self.patient_femme,
            poids=25.0,  # < 30
            motif="Test poids faible"
        )
        
        with self.assertRaises(ValidationError):
            consultation1.full_clean()
        
        # Poids trop élevé
        consultation2 = ConsultationGynecologique(
            patient=self.patient_femme,
            poids=250.0,  # > 200
            motif="Test poids élevé"
        )
        
        with self.assertRaises(ValidationError):
            consultation2.full_clean()

    def test_str_representation(self):
        """Test représentation string du modèle"""
        consultation = ConsultationGynecologique.objects.create(
            patient=self.patient_femme,
            date_consultation=date(2024, 1, 15),
            motif="Test str"
        )
        
        expected = f"Consultation du 15/01/2024 - {self.patient_femme.nom_complet}"
        self.assertEqual(str(consultation), expected)

    def test_ordering(self):
        """Test de l'ordering du modèle"""
        # Créer plusieurs consultations avec des dates différentes
        consultation1 = ConsultationGynecologique.objects.create(
            patient=self.patient_femme,
            date_consultation=date(2024, 1, 10),
            motif="Première consultation"
        )
        
        consultation2 = ConsultationGynecologique.objects.create(
            patient=self.patient_femme,
            date_consultation=date(2024, 1, 15),
            motif="Seconde consultation"
        )
        
        consultation3 = ConsultationGynecologique.objects.create(
            patient=self.patient_femme,
            date_consultation=date(2024, 1, 5),
            motif="Troisième consultation"
        )
        
        consultations = list(ConsultationGynecologique.objects.all())
        
        # Vérifier que les consultations sont triées par date décroissante
        self.assertEqual(consultations[0], consultation2)  # 15/01
        self.assertEqual(consultations[1], consultation1)  # 10/01
        self.assertEqual(consultations[2], consultation3)  # 05/01

    def test_related_name(self):
        """Test du related_name pour accéder aux consultations depuis le patient"""
        consultation = ConsultationGynecologique.objects.create(
            patient=self.patient_femme,
            motif="Test related name"
        )
        
        consultations = self.patient_femme.consultations_gynecologiques.all()
        self.assertEqual(consultations.count(), 1)
        self.assertEqual(consultations.first(), consultation)

    def test_save_with_validation(self):
        """Test que save() appelle full_clean()"""
        consultation = ConsultationGynecologique(
            patient=self.patient_femme,
            date_consultation=date.today() + timedelta(days=1),
            motif="Test save validation"
        )
        
        with self.assertRaises(ValidationError):
            consultation.save()

    def test_meta_verbose_names(self):
        """Test des noms verbose du meta"""
        meta = ConsultationGynecologique._meta
        self.assertEqual(meta.verbose_name, "6.1.2 Consultation Gynécologique")
        self.assertEqual(meta.verbose_name_plural, "6.1.2 Consultations Gynécologiques")

    def test_cascade_delete_patient(self):
        """Test suppression en cascade quand le patient est supprimé"""
        consultation = ConsultationGynecologique.objects.create(
            patient=self.patient_femme,
            motif="Test cascade delete"
        )
        
        consultation_id = consultation.id
        self.patient_femme.delete()
        
        # La consultation doit être supprimée aussi
        with self.assertRaises(ConsultationGynecologique.DoesNotExist):
            ConsultationGynecologique.objects.get(id=consultation_id)

    def test_set_null_sage_femme_delete(self):
        """Test SET_NULL quand la sage-femme est supprimée"""
        consultation = ConsultationGynecologique.objects.create(
            patient=self.patient_femme,
            motif="Test sage femme delete",
            created_by=self.sage_femme
        )
        
        self.sage_femme.delete()
        consultation.refresh_from_db()
        
        # created_by doit être None
        self.assertIsNone(consultation.created_by)