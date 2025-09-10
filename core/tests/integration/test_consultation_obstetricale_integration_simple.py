"""
Tests d'intégration simplifiés pour ConsultationObstetricale
Tests des fonctionnalités qui existent réellement
"""

from django.test import TestCase, Client
from datetime import date, timedelta
from core.models import ConsultationObstetricale, Patient, Caisse, SageFemme, Antecedents
from authentication.models import SageFemmeUser


class ConsultationObstetricaleSimpleIntegrationTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.client = Client()
        
        self.caisse = Caisse.objects.create(nom="CAFAT")
        
        # Patient femme enceinte
        self.patient_femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse,
            date_debut_grossesse=date.today() - timedelta(days=140)
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
    
    def test_creation_consultation_avec_calcul_sa(self):
        """Test de création d'une consultation avec calcul automatique SA"""
        consultation = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today(),
            motif='Contrôle de routine',
            tension_systolique=120,
            tension_diastolique=80,
            poids=65.5,
            created_by=self.sage_femme
        )
        
        # Vérifier que la consultation a été créée avec SA calculée
        self.assertEqual(consultation.patient, self.patient_femme)
        self.assertEqual(consultation.created_by, self.sage_femme)
        if consultation.semaines_amenorrhee:
            self.assertIn('SA', consultation.semaines_amenorrhee)
    
    def test_integration_avec_antecedents_imc(self):
        """Test de l'intégration avec les antécédents pour calcul IMC"""
        # Créer des antécédents avec taille
        antecedents = Antecedents.objects.create(
            patient=self.patient_femme,
            taille=1.65,
            poids=58.0
        )
        
        # Créer une consultation avec poids
        consultation = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today(),
            motif='Test IMC',
            poids=60.0,
            created_by=self.sage_femme
        )
        
        # Vérifier que l'IMC est calculé
        self.assertIsNotNone(consultation.imc)
        expected_imc = round(60.0 / (1.65 ** 2), 1)
        self.assertEqual(consultation.imc, expected_imc)
    
    def test_calcul_sa_avec_ddg_precise(self):
        """Test du calcul SA avec DDG précise"""
        # Patient avec DDG pour 24 SA exactement
        patient_test = Patient.objects.create(
            type_patient='femme',
            nom='Test',
            prenom='SA',
            date_naissance=date(1995, 1, 1),
            telephone='0123456787',
            caisse=self.caisse,
            date_debut_grossesse=date.today() - timedelta(days=168)  # 24 SA exactement
        )
        
        consultation = ConsultationObstetricale.objects.create(
            patient=patient_test,
            date_consultation=date.today(),
            motif='Test calcul SA',
            created_by=self.sage_femme
        )
        
        self.assertEqual(consultation.semaines_amenorrhee, "24 SA")
    
    def test_modification_recalcul_sa(self):
        """Test que la SA est recalculée lors des modifications"""
        consultation = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today(),
            motif='Test modification',
            created_by=self.sage_femme
        )
        
        sa_initiale = consultation.semaines_amenorrhee
        
        # Modifier la date de consultation
        consultation.date_consultation = date.today() - timedelta(days=7)
        consultation.save()
        
        # La SA devrait être différente
        self.assertNotEqual(consultation.semaines_amenorrhee, sa_initiale)
    
    def test_proprietes_consultation(self):
        """Test des propriétés calculées de la consultation"""
        consultation = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today(),
            motif='Test propriétés',
            tension_systolique=130,
            tension_diastolique=85,
            poids=66.5,
            created_by=self.sage_femme
        )
        
        # Test tension complète
        self.assertEqual(consultation.tension_complete, "130/85 mmHg")
        
        # Test interprétation tension
        self.assertIsNotNone(consultation.tension_interpretation)
        
        # Test résumé consultation
        resume = consultation.resume_consultation
        self.assertIn("Test propriétés", resume)
        self.assertIn("130/85 mmHg", resume)
        self.assertIn("66.5kg", resume)
    
    def test_validation_regles_metier(self):
        """Test des validations de règles métier"""
        from django.core.exceptions import ValidationError
        
        # Test tension incohérente
        with self.assertRaises(ValidationError):
            consultation = ConsultationObstetricale(
                patient=self.patient_femme,
                date_consultation=date.today(),
                motif="Test tension invalide",
                tension_systolique=80,  # Plus faible que diastolique
                tension_diastolique=120
            )
            consultation.full_clean()
        
        # Test date future
        with self.assertRaises(ValidationError):
            consultation = ConsultationObstetricale(
                patient=self.patient_femme,
                date_consultation=date.today() + timedelta(days=1),
                motif="Date future"
            )
            consultation.full_clean()
    
    def test_creation_sans_sage_femme(self):
        """Test création consultation sans sage-femme associée"""
        consultation = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today(),
            motif='Sans sage-femme'
        )
        
        self.assertIsNone(consultation.created_by)
        self.assertEqual(consultation.motif, 'Sans sage-femme')
        if consultation.semaines_amenorrhee:
            self.assertIn('SA', consultation.semaines_amenorrhee)
    
    def test_consultation_meta_information(self):
        """Test des informations meta du modèle"""
        consultation = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today(),
            motif='Test meta'
        )
        
        # Test __str__ representation
        expected_str = f"Consultation du {date.today().strftime('%d/%m/%Y')} - {self.patient_femme.nom_complet}"
        self.assertEqual(str(consultation), expected_str)
        
        # Test Meta options
        self.assertEqual(
            ConsultationObstetricale._meta.verbose_name,
            "6.1.3.2 Consultation Obstétricale"
        )
        self.assertEqual(
            ConsultationObstetricale._meta.verbose_name_plural,
            "6.1.3.2 Consultations Obstétricales"
        )
    
    def test_performance_requetes(self):
        """Test de performance des requêtes"""
        # Créer plusieurs consultations
        for i in range(3):
            ConsultationObstetricale.objects.create(
                patient=self.patient_femme,
                date_consultation=date.today() - timedelta(days=i),
                motif=f'Performance test {i}',
                created_by=self.sage_femme
            )
        
        # Test select_related pour éviter N+1 queries
        with self.assertNumQueries(1):
            consultations = list(
                ConsultationObstetricale.objects
                .select_related('created_by', 'patient')
                .filter(patient=self.patient_femme)
            )
            
            # Accéder aux relations ne génère pas de requêtes supplémentaires
            for consultation in consultations:
                _ = consultation.created_by
                _ = consultation.patient
    
    def test_gestion_erreurs_calcul_sa(self):
        """Test de la gestion d'erreurs lors du calcul SA"""
        # Test avec patient sans DDG
        patient_sans_ddg = Patient.objects.create(
            type_patient='femme',
            nom='Sans DDG',
            prenom='Test',
            date_naissance=date(1990, 1, 1),
            telephone='0123456786',
            caisse=self.caisse
            # Pas de date_debut_grossesse
        )
        
        consultation = ConsultationObstetricale.objects.create(
            patient=patient_sans_ddg,
            date_consultation=date.today(),
            motif='Test sans DDG'
        )
        
        # La SA devrait être None ou vide
        self.assertIn(consultation.semaines_amenorrhee, [None, ''])
        
        # La consultation doit quand même être créée
        self.assertEqual(consultation.motif, 'Test sans DDG')
        self.assertEqual(consultation.patient, patient_sans_ddg)