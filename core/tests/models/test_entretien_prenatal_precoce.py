"""
Tests pour le modèle EntretienPrenatalPrecoce
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date, timedelta

from core.models import EntretienPrenatalPrecoce, Patient, SageFemme, Caisse
from authentication.models import SageFemmeUser


class EntretienPrenatalPrecoceModelTest(TestCase):
    """Tests pour le modèle EntretienPrenatalPrecoce"""
    
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
            date_debut_grossesse=date(2024, 1, 15)  # DDG il y a ~9 mois
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
        
        # Date d'entretien (à 20 SA = ~140 jours après DDG)
        self.date_entretien = self.patient_femme.date_debut_grossesse + timedelta(days=140)
    
    def test_creation_entretien_valide(self):
        """Test création d'un entretien avec données valides"""
        entretien = EntretienPrenatalPrecoce.objects.create(
            patient=self.patient_femme,
            sage_femme=self.sage_femme,
            date_entretien=self.date_entretien,
            conjoint_present=True,
            lieu_accouchement_prevu='Maternité CHT',
            atcd_marquants_sante='Aucun ATCD particulier',
            environnement_social_familial='Environnement stable',
            projet_naissance_parentalite='Accouchement naturel',
            ressenti='Très positive',
            propositions_liens='Cours préparation naissance'
        )
        
        self.assertEqual(entretien.patient, self.patient_femme)
        self.assertEqual(entretien.sage_femme, self.sage_femme)
        self.assertEqual(entretien.date_entretien, self.date_entretien)
        self.assertTrue(entretien.conjoint_present)
        self.assertEqual(entretien.lieu_accouchement_prevu, 'Maternité CHT')
        self.assertIsNotNone(entretien.created_at)
        self.assertIsNotNone(entretien.updated_at)
    
    def test_creation_entretien_minimal(self):
        """Test création avec données minimales obligatoires"""
        entretien = EntretienPrenatalPrecoce.objects.create(
            patient=self.patient_femme,
            date_entretien=self.date_entretien,
            conjoint_present=False
        )
        
        self.assertEqual(entretien.patient, self.patient_femme)
        self.assertEqual(entretien.date_entretien, self.date_entretien)
        self.assertFalse(entretien.conjoint_present)
        self.assertEqual(entretien.lieu_accouchement_prevu, '')
        self.assertEqual(entretien.atcd_marquants_sante, '')
    
    def test_calcul_sa_automatique(self):
        """Test calcul automatique des SA"""
        entretien = EntretienPrenatalPrecoce.objects.create(
            patient=self.patient_femme,
            date_entretien=self.date_entretien,
            conjoint_present=False
        )
        
        # Vérifier que les SA sont calculées automatiquement
        self.assertIsNotNone(entretien.semaines_amenorrhee)
        
        # Calcul manuel attendu (140 jours = 20 semaines)
        self.assertEqual(entretien.semaines_amenorrhee, '20 SA')
    
    def test_calculer_sa_methode(self):
        """Test de la méthode calculer_sa"""
        entretien = EntretienPrenatalPrecoce(
            patient=self.patient_femme,
            date_entretien=self.patient_femme.date_debut_grossesse + timedelta(days=147),  # 21 SA + 0j
            conjoint_present=False
        )
        
        sa_calculee = entretien.calculer_sa()
        self.assertEqual(sa_calculee, '21 SA')
        
        # Test avec jours supplémentaires
        entretien.date_entretien = self.patient_femme.date_debut_grossesse + timedelta(days=150)  # 21 SA + 3j
        sa_calculee = entretien.calculer_sa()
        self.assertEqual(sa_calculee, '21 SA + 3j')
    
    def test_calculer_sa_sans_ddg(self):
        """Test calcul SA sans DDG définie"""
        entretien = EntretienPrenatalPrecoce(
            patient=self.patient_femme_sans_ddg,
            date_entretien=date.today(),
            conjoint_present=False
        )
        
        sa_calculee = entretien.calculer_sa()
        self.assertEqual(sa_calculee, '')
    
    def test_calculer_sa_date_anterieure(self):
        """Test calcul SA avec date antérieure à DDG"""
        entretien = EntretienPrenatalPrecoce(
            patient=self.patient_femme,
            date_entretien=self.patient_femme.date_debut_grossesse - timedelta(days=10),
            conjoint_present=False
        )
        
        sa_calculee = entretien.calculer_sa()
        self.assertEqual(sa_calculee, 'Grossesse pas encore commencée')
    
    def test_validation_patient_femme_obligatoire(self):
        """Test validation : seules les femmes sont autorisées"""
        with self.assertRaises(ValidationError) as context:
            entretien = EntretienPrenatalPrecoce(
                patient=self.patient_bebe,
                date_entretien=date.today(),
                conjoint_present=False
            )
            entretien.full_clean()
        
        self.assertIn('__all__', context.exception.message_dict)
        self.assertIn("réservé aux femmes", str(context.exception.message_dict['__all__']))
    
    def test_validation_ddg_obligatoire(self):
        """Test validation : DDG obligatoire"""
        with self.assertRaises(ValidationError) as context:
            entretien = EntretienPrenatalPrecoce(
                patient=self.patient_femme_sans_ddg,
                date_entretien=date.today(),
                conjoint_present=False
            )
            entretien.full_clean()
        
        self.assertIn('__all__', context.exception.message_dict)
        self.assertIn("date de début de grossesse", str(context.exception.message_dict['__all__']))
    
    def test_validation_date_future(self):
        """Test validation : date d'entretien ne peut pas être dans le futur"""
        with self.assertRaises(ValidationError) as context:
            entretien = EntretienPrenatalPrecoce(
                patient=self.patient_femme,
                date_entretien=date.today() + timedelta(days=10),
                conjoint_present=False
            )
            entretien.full_clean()
        
        self.assertIn('__all__', context.exception.message_dict)
        self.assertIn("ne peut pas être dans le futur", str(context.exception.message_dict['__all__']))
    
    def test_validation_date_avant_ddg(self):
        """Test validation : date d'entretien après DDG"""
        with self.assertRaises(ValidationError) as context:
            entretien = EntretienPrenatalPrecoce(
                patient=self.patient_femme,
                date_entretien=self.patient_femme.date_debut_grossesse - timedelta(days=1),
                conjoint_present=False
            )
            entretien.full_clean()
        
        self.assertIn('__all__', context.exception.message_dict)
        self.assertIn("postérieure au début de grossesse", str(context.exception.message_dict['__all__']))
    
    def test_str_representation(self):
        """Test représentation string"""
        entretien = EntretienPrenatalPrecoce.objects.create(
            patient=self.patient_femme,
            date_entretien=self.date_entretien,
            conjoint_present=False
        )
        
        expected_str = f"EPP du {self.date_entretien.strftime('%d/%m/%Y')} - {self.patient_femme.nom_complet}"
        self.assertEqual(str(entretien), expected_str)
    
    def test_proprietes_affichage(self):
        """Test des propriétés d'affichage"""
        entretien = EntretienPrenatalPrecoce.objects.create(
            patient=self.patient_femme,
            date_entretien=self.date_entretien,
            conjoint_present=True,
            lieu_accouchement_prevu='Maternité CHT',
            semaines_amenorrhee='20 SA'
        )
        
        # Test sa_affichage_court
        self.assertEqual(entretien.sa_affichage_court, '20 SA')
        
        # Test entretien_resume
        resume = entretien.entretien_resume
        self.assertIn('Lieu: Maternité CHT', resume)
        self.assertIn('Conjoint présent', resume)
        self.assertIn('SA: 20 SA', resume)
    
    def test_est_dans_periode_optimale(self):
        """Test de la propriété est_dans_periode_optimale"""
        # Test période optimale (20 SA)
        entretien = EntretienPrenatalPrecoce.objects.create(
            patient=self.patient_femme,
            date_entretien=self.patient_femme.date_debut_grossesse + timedelta(days=140),  # 20 SA
            conjoint_present=False
        )
        self.assertTrue(entretien.est_dans_periode_optimale)
        
        # Test hors période optimale (30 SA) - Recréer l'entretien au lieu de modifier
        entretien_30sa = EntretienPrenatalPrecoce.objects.create(
            patient=self.patient_femme,
            date_entretien=self.patient_femme.date_debut_grossesse + timedelta(days=210),  # 30 SA
            conjoint_present=False
        )
        self.assertFalse(entretien_30sa.est_dans_periode_optimale)
        
        # Test limite basse (16 SA)
        entretien_16sa = EntretienPrenatalPrecoce.objects.create(
            patient=self.patient_femme,
            date_entretien=self.patient_femme.date_debut_grossesse + timedelta(days=112),  # 16 SA
            conjoint_present=False
        )
        self.assertTrue(entretien_16sa.est_dans_periode_optimale)
        
        # Test limite haute (28 SA)
        entretien_28sa = EntretienPrenatalPrecoce.objects.create(
            patient=self.patient_femme,
            date_entretien=self.patient_femme.date_debut_grossesse + timedelta(days=196),  # 28 SA
            conjoint_present=False
        )
        self.assertTrue(entretien_28sa.est_dans_periode_optimale)
    
    def test_indicateur_periode(self):
        """Test de la propriété indicateur_periode"""
        # Test période optimale
        entretien = EntretienPrenatalPrecoce.objects.create(
            patient=self.patient_femme,
            date_entretien=self.patient_femme.date_debut_grossesse + timedelta(days=140),  # 20 SA
            conjoint_present=False
        )
        self.assertEqual(entretien.indicateur_periode, 'optimal')
        
        # Test hors période - Créer un nouvel entretien
        entretien_hors_periode = EntretienPrenatalPrecoce.objects.create(
            patient=self.patient_femme,
            date_entretien=self.patient_femme.date_debut_grossesse + timedelta(days=300),  # ~43 SA
            conjoint_present=False
        )
        self.assertEqual(entretien_hors_periode.indicateur_periode, 'limite')
    
    def test_meta_options(self):
        """Test des options Meta"""
        entretien = EntretienPrenatalPrecoce()
        meta = entretien._meta
        
        self.assertEqual(meta.verbose_name, "6.1.4 Entretien Prénatal Précoce")
        self.assertEqual(meta.verbose_name_plural, "6.1.4 Entretiens Prénataux Précoces")
        self.assertEqual(meta.ordering, ['-date_entretien', '-created_at'])
    
    def test_relations_cascade(self):
        """Test des relations et suppression en cascade"""
        entretien = EntretienPrenatalPrecoce.objects.create(
            patient=self.patient_femme,
            sage_femme=self.sage_femme,
            date_entretien=self.date_entretien,
            conjoint_present=False
        )
        
        entretien_id = entretien.id
        
        # Suppression de la patiente doit supprimer l'entretien (CASCADE)
        self.patient_femme.delete()
        with self.assertRaises(EntretienPrenatalPrecoce.DoesNotExist):
            EntretienPrenatalPrecoce.objects.get(id=entretien_id)
    
    def test_relations_set_null(self):
        """Test des relations SET_NULL"""
        entretien = EntretienPrenatalPrecoce.objects.create(
            patient=self.patient_femme,
            sage_femme=self.sage_femme,
            date_entretien=self.date_entretien,
            conjoint_present=False
        )
        
        # Suppression de la sage-femme doit mettre le champ à NULL
        self.sage_femme.delete()
        entretien.refresh_from_db()
        self.assertIsNone(entretien.sage_femme)
    
    def test_performance_requetes(self):
        """Test performance des requêtes avec select_related"""
        EntretienPrenatalPrecoce.objects.create(
            patient=self.patient_femme,
            sage_femme=self.sage_femme,
            date_entretien=self.date_entretien,
            conjoint_present=False
        )
        
        # Test avec select_related
        with self.assertNumQueries(1):
            entretiens = list(
                EntretienPrenatalPrecoce.objects
                .select_related('patient', 'sage_femme')
                .all()
            )
            # Accéder aux propriétés ne doit pas générer de requêtes supplémentaires
            for entretien in entretiens:
                _ = entretien.patient.nom_complet
                if entretien.sage_femme:
                    _ = entretien.sage_femme.nom