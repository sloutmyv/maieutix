"""
Tests pour les modèles Antecedents et FrottisCV
Tests complets des fonctionnalités métier et validations
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date, timedelta
from core.models import Patient, Caisse, Antecedents, FrottisCV


class AntecedentsModelTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.caisse = Caisse.objects.create(
            nom="CAFAT"
        )
        
        self.patiente = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse
        )
        
        self.bebe = Patient.objects.create(
            type_patient='bebe',
            nom='Dupont',
            prenom='Lucas',
            date_naissance=date.today() - timedelta(days=30),
            mere=self.patiente,
            caisse=self.caisse
        )
    
    def test_antecedents_creation_basic(self):
        """Test création basique d'antécédents"""
        antecedents = Antecedents.objects.create(
            patient=self.patiente,
            taille=1.65,
            poids=60.0,
            medecin_traitant="Dr. Martin",
            gynecologue="Dr. Lemaire"
        )
        
        self.assertEqual(antecedents.patient, self.patiente)
        self.assertEqual(antecedents.taille, 1.65)
        self.assertEqual(antecedents.poids, 60.0)
        self.assertEqual(antecedents.medecin_traitant, "Dr. Martin")
        self.assertEqual(antecedents.gynecologue, "Dr. Lemaire")
        self.assertIsNotNone(antecedents.created_at)
        self.assertIsNotNone(antecedents.updated_at)
    
    def test_antecedents_creation_complete(self):
        """Test création complète d'antécédents avec tous les champs"""
        antecedents = Antecedents.objects.create(
            patient=self.patiente,
            taille=1.70,
            poids=65.5,
            medecin_traitant="Dr. Rousseau",
            gynecologue="Dr. Bernard",
            allergie="Pénicilline, pollen",
            asthme=True,
            raa=False,
            diabete=False,
            hta=False,
            epilepsie=False,
            infection_urinaire=True,
            atcd_obstetricaux="G2P1, césarienne en 2020",
            fcv_notes="Suivi régulier, derniers résultats normaux",
            atcd_fam_diabete=True,
            atcd_fam_hta=False,
            atcd_fam_cancer_sein=True,
            atcd_fam_hypercholesterolemie=False,
            atcd_fam_autre="Cancer colorectal (grand-père paternel)",
            atcd_chirurgicaux="Appendicectomie 2015, césarienne 2020",
            contraception="Pilule oestroprogestative"
        )
        
        self.assertEqual(antecedents.allergie, "Pénicilline, pollen")
        self.assertTrue(antecedents.asthme)
        self.assertFalse(antecedents.raa)
        self.assertTrue(antecedents.infection_urinaire)
        self.assertEqual(antecedents.atcd_obstetricaux, "G2P1, césarienne en 2020")
        self.assertTrue(antecedents.atcd_fam_diabete)
        self.assertTrue(antecedents.atcd_fam_cancer_sein)
        self.assertEqual(antecedents.atcd_fam_autre, "Cancer colorectal (grand-père paternel)")
        self.assertEqual(antecedents.contraception, "Pilule oestroprogestative")
    
    def test_antecedents_one_to_one_constraint(self):
        """Test contrainte OneToOne - un patient ne peut avoir qu'un seul antécédent"""
        # Créer le premier antécédent
        Antecedents.objects.create(
            patient=self.patiente,
            taille=1.65,
            poids=60.0
        )
        
        # Tentative de création d'un second antécédent pour le même patient
        with self.assertRaises(IntegrityError):
            Antecedents.objects.create(
                patient=self.patiente,
                taille=1.70,
                poids=65.0
            )
    
    def test_antecedents_taille_validation(self):
        """Test validation des limites de taille"""
        # Taille trop petite
        antecedents = Antecedents(
            patient=self.patiente,
            taille=0.3,  # Inférieur à 0.5
            poids=60.0
        )
        with self.assertRaises(ValidationError):
            antecedents.full_clean()
        
        # Taille trop grande
        antecedents = Antecedents(
            patient=self.patiente,
            taille=3.0,  # Supérieur à 2.5
            poids=60.0
        )
        with self.assertRaises(ValidationError):
            antecedents.full_clean()
        
        # Taille valide
        antecedents = Antecedents(
            patient=self.patiente,
            taille=1.75,
            poids=60.0
        )
        try:
            antecedents.full_clean()
        except ValidationError:
            self.fail("ValidationError raised for valid taille")
    
    def test_antecedents_poids_validation(self):
        """Test validation des limites de poids"""
        # Poids trop faible
        antecedents = Antecedents(
            patient=self.patiente,
            taille=1.65,
            poids=15.0  # Inférieur à 20
        )
        with self.assertRaises(ValidationError):
            antecedents.full_clean()
        
        # Poids trop élevé
        antecedents = Antecedents(
            patient=self.patiente,
            taille=1.65,
            poids=250.0  # Supérieur à 200
        )
        with self.assertRaises(ValidationError):
            antecedents.full_clean()
        
        # Poids valide
        antecedents = Antecedents(
            patient=self.patiente,
            taille=1.65,
            poids=70.0
        )
        try:
            antecedents.full_clean()
        except ValidationError:
            self.fail("ValidationError raised for valid poids")
    
    def test_antecedents_imc_calculation(self):
        """Test calcul de l'IMC"""
        antecedents = Antecedents.objects.create(
            patient=self.patiente,
            taille=1.70,
            poids=68.0
        )
        
        # IMC = poids / (taille²) = 68 / (1.70²) = 68 / 2.89 ≈ 23.5
        expected_imc = 23.5
        self.assertAlmostEqual(antecedents.imc, expected_imc, places=1)
    
    def test_antecedents_imc_no_data(self):
        """Test IMC quand taille ou poids manquent"""
        # Pas de taille
        antecedents = Antecedents.objects.create(
            patient=self.patiente,
            poids=68.0
        )
        self.assertIsNone(antecedents.imc)
        
        # Pas de poids
        antecedents.taille = 1.70
        antecedents.poids = None
        antecedents.save()
        self.assertIsNone(antecedents.imc)
    
    def test_antecedents_imc_interpretation(self):
        """Test interprétation de l'IMC"""
        antecedents = Antecedents.objects.create(
            patient=self.patiente,
            taille=1.70
        )
        
        # Test insuffisance pondérale (IMC < 18.5)
        antecedents.poids = 50.0  # IMC ≈ 17.3
        antecedents.save()
        self.assertEqual(antecedents.imc_interpretation, "Insuffisance pondérale")
        
        # Test poids normal (18.5 ≤ IMC < 25)
        antecedents.poids = 65.0  # IMC ≈ 22.5
        antecedents.save()
        self.assertEqual(antecedents.imc_interpretation, "Poids normal")
        
        # Test surpoids (25 ≤ IMC < 30)
        antecedents.poids = 75.0  # IMC ≈ 26.0
        antecedents.save()
        self.assertEqual(antecedents.imc_interpretation, "Surpoids")
        
        # Test obésité modérée (30 ≤ IMC < 35)
        antecedents.poids = 90.0  # IMC ≈ 31.1
        antecedents.save()
        self.assertEqual(antecedents.imc_interpretation, "Obésité modérée")
        
        # Test obésité sévère (35 ≤ IMC < 40)
        antecedents.poids = 105.0  # IMC ≈ 36.3
        antecedents.save()
        self.assertEqual(antecedents.imc_interpretation, "Obésité sévère")
        
        # Test obésité morbide (IMC ≥ 40)
        antecedents.poids = 120.0  # IMC ≈ 41.5
        antecedents.save()
        self.assertEqual(antecedents.imc_interpretation, "Obésité morbide")
    
    def test_antecedents_imc_interpretation_no_data(self):
        """Test interprétation IMC sans données"""
        antecedents = Antecedents.objects.create(
            patient=self.patiente
        )
        self.assertIsNone(antecedents.imc_interpretation)
    
    def test_antecedents_str_representation(self):
        """Test représentation string des antécédents"""
        antecedents = Antecedents.objects.create(
            patient=self.patiente
        )
        expected_str = f"Antécédents de {self.patiente.nom_complet}"
        self.assertEqual(str(antecedents), expected_str)
    
    def test_antecedents_related_name(self):
        """Test accès via related_name depuis Patient"""
        antecedents = Antecedents.objects.create(
            patient=self.patiente,
            taille=1.65,
            poids=60.0
        )
        
        # Accès depuis le patient
        self.assertEqual(self.patiente.antecedents, antecedents)
    
    def test_antecedents_verbose_names(self):
        """Test des verbose_names du modèle"""
        antecedents = Antecedents()
        
        self.assertEqual(
            antecedents._meta.get_field('taille').verbose_name,
            "Taille (m)"
        )
        self.assertEqual(
            antecedents._meta.get_field('poids').verbose_name,
            "Poids (kg)"
        )
        self.assertEqual(
            antecedents._meta.get_field('medecin_traitant').verbose_name,
            "Médecin traitant"
        )
        self.assertEqual(
            antecedents._meta.get_field('allergie').verbose_name,
            "Allergies"
        )
    
    def test_antecedents_help_texts(self):
        """Test des help_texts du modèle"""
        antecedents = Antecedents()
        
        self.assertEqual(
            antecedents._meta.get_field('taille').help_text,
            "Taille en mètres"
        )
        self.assertEqual(
            antecedents._meta.get_field('poids').help_text,
            "Poids en kilogrammes"
        )
        self.assertEqual(
            antecedents._meta.get_field('allergie').help_text,
            "Détail des allergies connues"
        )


class FrottisCVModelTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.caisse = Caisse.objects.create(
            nom="CAFAT"
        )
        
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
    
    def test_frottis_creation_basic(self):
        """Test création basique d'un frottis"""
        frottis = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2024, 6, 15),
            resultat="Normal - Absence de cellules anormales"
        )
        
        self.assertEqual(frottis.antecedents, self.antecedents)
        self.assertEqual(frottis.date_frottis, date(2024, 6, 15))
        self.assertEqual(frottis.resultat, "Normal - Absence de cellules anormales")
        self.assertIsNotNone(frottis.created_at)
        self.assertIsNotNone(frottis.updated_at)
    
    def test_frottis_creation_complete(self):
        """Test création complète d'un frottis avec résultat détaillé"""
        resultat_detaille = """
        Frottis cervico-vaginal en milieu liquide
        Qualité du prélèvement : Satisfaisante
        Flore : Lactobacilles prédominants
        Épithélium malpighien : Cellules de surface et intermédiaires normales
        Épithélium glandulaire : Quelques cellules endocervicales normales
        Conclusion : Frottis normal, absence de lésion intra-épithéliale
        """
        
        frottis = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2024, 3, 10),
            resultat=resultat_detaille.strip()
        )
        
        self.assertEqual(frottis.resultat, resultat_detaille.strip())
        self.assertEqual(frottis.date_frottis, date(2024, 3, 10))
    
    def test_frottis_multiple_per_antecedents(self):
        """Test création de plusieurs frottis pour les mêmes antécédents"""
        frottis1 = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2023, 6, 15),
            resultat="Normal"
        )
        
        frottis2 = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2024, 6, 15),
            resultat="Normal - Contrôle"
        )
        
        # Vérifier que les deux frottis existent
        frottis_list = list(self.antecedents.frottis.all())
        self.assertEqual(len(frottis_list), 2)
        self.assertIn(frottis1, frottis_list)
        self.assertIn(frottis2, frottis_list)
    
    def test_frottis_ordering(self):
        """Test ordre par défaut des frottis (date décroissante)"""
        # Créer plusieurs frottis avec des dates différentes
        frottis_ancien = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2022, 3, 10),
            resultat="Normal - ancien"
        )
        
        frottis_recent = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2024, 6, 15),
            resultat="Normal - récent"
        )
        
        frottis_moyen = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2023, 9, 20),
            resultat="Normal - moyen"
        )
        
        # Vérifier l'ordre (le plus récent en premier)
        frottis_ordered = list(self.antecedents.frottis.all())
        self.assertEqual(frottis_ordered[0], frottis_recent)
        self.assertEqual(frottis_ordered[1], frottis_moyen)
        self.assertEqual(frottis_ordered[2], frottis_ancien)
    
    def test_frottis_str_representation(self):
        """Test représentation string du frottis"""
        frottis = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2024, 6, 15),
            resultat="Normal"
        )
        
        expected_str = f"Frottis du 15/06/2024 - {self.patiente.nom_complet}"
        self.assertEqual(str(frottis), expected_str)
    
    def test_frottis_cascade_delete_with_antecedents(self):
        """Test suppression en cascade lors de la suppression des antécédents"""
        frottis = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2024, 6, 15),
            resultat="Normal"
        )
        
        frottis_id = frottis.id
        
        # Supprimer les antécédents
        self.antecedents.delete()
        
        # Vérifier que le frottis a été supprimé aussi
        with self.assertRaises(FrottisCV.DoesNotExist):
            FrottisCV.objects.get(id=frottis_id)
    
    def test_frottis_cascade_delete_with_patient(self):
        """Test suppression en cascade lors de la suppression du patient"""
        frottis = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2024, 6, 15),
            resultat="Normal"
        )
        
        frottis_id = frottis.id
        antecedents_id = self.antecedents.id
        
        # Supprimer le patient
        self.patiente.delete()
        
        # Vérifier que les antécédents et le frottis ont été supprimés
        with self.assertRaises(Antecedents.DoesNotExist):
            Antecedents.objects.get(id=antecedents_id)
        
        with self.assertRaises(FrottisCV.DoesNotExist):
            FrottisCV.objects.get(id=frottis_id)
    
    def test_frottis_related_name_access(self):
        """Test accès via related_name depuis Antecedents"""
        frottis1 = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2024, 3, 15),
            resultat="Normal 1"
        )
        
        frottis2 = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2024, 6, 15),
            resultat="Normal 2"
        )
        
        # Accès via related_name 'frottis'
        frottis_list = list(self.antecedents.frottis.all())
        self.assertEqual(len(frottis_list), 2)
        self.assertIn(frottis1, frottis_list)
        self.assertIn(frottis2, frottis_list)
    
    def test_frottis_resultat_max_length(self):
        """Test de la longueur maximale du champ résultat"""
        long_resultat = "A" * 500  # Exactement 500 caractères
        
        frottis = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2024, 6, 15),
            resultat=long_resultat
        )
        
        self.assertEqual(len(frottis.resultat), 500)
        
        # Test avec un résultat trop long
        very_long_resultat = "A" * 501  # 501 caractères
        frottis_too_long = FrottisCV(
            antecedents=self.antecedents,
            date_frottis=date(2024, 6, 16),
            resultat=very_long_resultat
        )
        
        with self.assertRaises(ValidationError):
            frottis_too_long.full_clean()
    
    def test_frottis_verbose_names(self):
        """Test des verbose_names du modèle FrottisCV"""
        frottis = FrottisCV()
        
        self.assertEqual(
            frottis._meta.get_field('antecedents').verbose_name,
            "Antécédents"
        )
        self.assertEqual(
            frottis._meta.get_field('date_frottis').verbose_name,
            "Date du frottis"
        )
        self.assertEqual(
            frottis._meta.get_field('resultat').verbose_name,
            "Résultat"
        )
    
    def test_frottis_help_text(self):
        """Test du help_text du champ résultat"""
        frottis = FrottisCV()
        
        self.assertEqual(
            frottis._meta.get_field('resultat').help_text,
            "Résultat du frottis cervico-vaginal"
        )
    
    def test_frottis_meta_verbose_names(self):
        """Test des verbose_names de la classe Meta"""
        self.assertEqual(
            FrottisCV._meta.verbose_name,
            "6.1.1.1 Frottis cervico-vaginal"
        )
        self.assertEqual(
            FrottisCV._meta.verbose_name_plural,
            "6.1.1.1 Frottis cervico-vaginaux"
        )