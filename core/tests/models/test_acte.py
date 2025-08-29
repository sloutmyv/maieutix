"""
Tests pour les modèles Acte et TarifPeriode
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from core.models.acte import Acte, TarifPeriode


class ActeModelTests(TestCase):
    """Tests pour le modèle Acte"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.acte = Acte.objects.create(
            code='CSF',
            libelle='Consultation Sage-Femme'
        )
    
    def test_str_method(self):
        """Test de la représentation string"""
        expected = 'CSF - Consultation Sage-Femme'
        self.assertEqual(str(self.acte), expected)
    
    def test_str_method_long_libelle(self):
        """Test str avec libellé long (troncature à 50 caractères)"""
        acte = Acte.objects.create(
            code='VGC',
            libelle='Visite gynécologique complète avec examen approfondi et conseils'
        )
        # Le modèle tronque à 50 caractères depuis le début du libellé
        expected = 'VGC - Visite gynécologique complète avec examen approfon'
        self.assertEqual(str(acte), expected)
    
    def test_clean_method_code_with_spaces(self):
        """Test que les codes avec espaces sont rejetés"""
        acte = Acte(code='CS F', libelle='Test')
        with self.assertRaises(ValidationError) as context:
            acte.clean()
        self.assertIn('code', context.exception.message_dict)
    
    def test_unique_code_constraint(self):
        """Test que le code est unique"""
        with self.assertRaises(Exception):
            Acte.objects.create(
                code='CSF',  # Code déjà utilisé
                libelle='Autre consultation'
            )
    
    def test_tarif_actuel_property_no_tarif(self):
        """Test propriété tarif_actuel sans tarif"""
        self.assertIsNone(self.acte.tarif_actuel)
    
    def test_tarif_actuel_property_with_current_tarif(self):
        """Test propriété tarif_actuel avec tarif actuel"""
        today = timezone.now().date()
        tarif = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=today - timedelta(days=30)
        )
        self.assertEqual(self.acte.tarif_actuel, tarif)
    
    def test_tarif_actuel_property_with_future_tarif(self):
        """Test propriété tarif_actuel avec tarif futur uniquement"""
        today = timezone.now().date()
        TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=today + timedelta(days=30)
        )
        self.assertIsNone(self.acte.tarif_actuel)
    
    def test_tarif_actuel_property_with_expired_tarif(self):
        """Test propriété tarif_actuel avec tarif expiré"""
        today = timezone.now().date()
        TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=today - timedelta(days=60),
            date_fin=today - timedelta(days=30)
        )
        self.assertIsNone(self.acte.tarif_actuel)
    
    def test_cout_conventionnel_actuel_property(self):
        """Test propriété cout_conventionnel_actuel"""
        today = timezone.now().date()
        TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=today - timedelta(days=30)
        )
        self.assertEqual(self.acte.cout_conventionnel_actuel, Decimal('5000'))
    
    def test_cout_conventionnel_actuel_property_no_tarif(self):
        """Test propriété cout_conventionnel_actuel sans tarif"""
        self.assertIsNone(self.acte.cout_conventionnel_actuel)


class TarifPeriodeModelTests(TestCase):
    """Tests pour le modèle TarifPeriode"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.acte = Acte.objects.create(
            code='CSF',
            libelle='Consultation Sage-Femme'
        )
        self.today = timezone.now().date()
    
    def test_str_method_with_date_fin(self):
        """Test représentation string avec date de fin"""
        tarif = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today,
            date_fin=self.today + timedelta(days=30)
        )
        expected = f'CSF - 5000 XPF (du {self.today} au {self.today + timedelta(days=30)})'
        self.assertEqual(str(tarif), expected)
    
    def test_str_method_without_date_fin(self):
        """Test représentation string sans date de fin"""
        tarif = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today
        )
        expected = f'CSF - 5000 XPF (à partir du {self.today})'
        self.assertEqual(str(tarif), expected)
    
    def test_clean_method_date_fin_before_date_debut(self):
        """Test validation date_fin avant date_debut"""
        tarif = TarifPeriode(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today,
            date_fin=self.today - timedelta(days=1)
        )
        with self.assertRaises(ValidationError) as context:
            tarif.clean()
        self.assertIn('date_fin', context.exception.message_dict)
    
    def test_clean_method_overlapping_periods(self):
        """Test validation des périodes qui se chevauchent"""
        # Créer première période
        TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today,
            date_fin=self.today + timedelta(days=30)
        )
        
        # Tenter de créer une période qui chevauche
        tarif2 = TarifPeriode(
            acte=self.acte,
            cout_xpf=6000,
            date_debut=self.today + timedelta(days=15),
            date_fin=self.today + timedelta(days=45)
        )
        
        with self.assertRaises(ValidationError):
            tarif2.clean()
    
    def test_clean_method_non_overlapping_periods(self):
        """Test validation des périodes qui ne se chevauchent pas"""
        # Créer première période
        TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today,
            date_fin=self.today + timedelta(days=30)
        )
        
        # Créer période suivante (ne chevauche pas)
        tarif2 = TarifPeriode(
            acte=self.acte,
            cout_xpf=6000,
            date_debut=self.today + timedelta(days=31),
            date_fin=self.today + timedelta(days=60)
        )
        
        # Ne devrait pas lever d'erreur
        tarif2.clean()
    
    def test_periods_overlap_method(self):
        """Test de la méthode _periods_overlap"""
        periode1 = TarifPeriode(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today,
            date_fin=self.today + timedelta(days=30)
        )
        
        periode2 = TarifPeriode(
            acte=self.acte,
            cout_xpf=6000,
            date_debut=self.today + timedelta(days=15),
            date_fin=self.today + timedelta(days=45)
        )
        
        self.assertTrue(periode1._periods_overlap(periode2))
    
    def test_periods_no_overlap_method(self):
        """Test de la méthode _periods_overlap sans chevauchement"""
        periode1 = TarifPeriode(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today,
            date_fin=self.today + timedelta(days=30)
        )
        
        periode2 = TarifPeriode(
            acte=self.acte,
            cout_xpf=6000,
            date_debut=self.today + timedelta(days=31),
            date_fin=self.today + timedelta(days=60)
        )
        
        self.assertFalse(periode1._periods_overlap(periode2))
    
    def test_est_actuel_property_current_period(self):
        """Test propriété est_actuel pour période actuelle"""
        tarif = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today - timedelta(days=10)
        )
        self.assertTrue(tarif.est_actuel)
    
    def test_est_actuel_property_future_period(self):
        """Test propriété est_actuel pour période future"""
        tarif = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today + timedelta(days=10)
        )
        self.assertFalse(tarif.est_actuel)
    
    def test_est_actuel_property_expired_period(self):
        """Test propriété est_actuel pour période expirée"""
        tarif = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today - timedelta(days=30),
            date_fin=self.today - timedelta(days=10)
        )
        self.assertFalse(tarif.est_actuel)
    
    def test_statut_property_futur(self):
        """Test propriété statut pour période future"""
        tarif = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today + timedelta(days=10)
        )
        self.assertEqual(tarif.statut, 'Futur')
    
    def test_statut_property_actuel(self):
        """Test propriété statut pour période actuelle"""
        tarif = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today - timedelta(days=10)
        )
        self.assertEqual(tarif.statut, 'Actuel')
    
    def test_statut_property_expire(self):
        """Test propriété statut pour période expirée"""
        tarif = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today - timedelta(days=30),
            date_fin=self.today - timedelta(days=10)
        )
        self.assertEqual(tarif.statut, 'Expiré')
    
    def test_ordering_by_date_debut_desc(self):
        """Test tri par date_debut décroissante"""
        tarif1 = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today - timedelta(days=30)
        )
        tarif2 = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=6000,
            date_debut=self.today - timedelta(days=10)
        )
        
        tarifs = list(TarifPeriode.objects.all())
        self.assertEqual(tarifs[0], tarif2)  # Plus récent en premier
        self.assertEqual(tarifs[1], tarif1)
    
    def test_meta_verbose_names(self):
        """Test des noms verbose du modèle"""
        self.assertEqual(TarifPeriode._meta.verbose_name, '3.1 Tarif Acte')
        self.assertEqual(TarifPeriode._meta.verbose_name_plural, '3.1 Tarifs Actes')
    
    def test_database_constraints(self):
        """Test des contraintes de base de données"""
        # Test contrainte date_fin >= date_debut
        with self.assertRaises(Exception):
            TarifPeriode.objects.create(
                acte=self.acte,
                cout_xpf=5000,
                date_debut=self.today,
                date_fin=self.today - timedelta(days=1)
            )


class ActeTarifPeriodeIntegrationTests(TestCase):
    """Tests d'intégration entre Acte et TarifPeriode"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.acte = Acte.objects.create(
            code='CSF',
            libelle='Consultation Sage-Femme'
        )
        self.today = timezone.now().date()
    
    def test_cascade_delete_acte(self):
        """Test suppression en cascade des tarifs lors de suppression d'un acte"""
        TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today
        )
        
        self.assertEqual(TarifPeriode.objects.count(), 1)
        self.acte.delete()
        self.assertEqual(TarifPeriode.objects.count(), 0)
    
    def test_related_name_tarifs_periodes(self):
        """Test du related_name pour accéder aux tarifs depuis un acte"""
        tarif1 = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today - timedelta(days=30)
        )
        tarif2 = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=6000,
            date_debut=self.today
        )
        
        tarifs = list(self.acte.tarifs_periodes.all())
        self.assertIn(tarif1, tarifs)
        self.assertIn(tarif2, tarifs)
        self.assertEqual(len(tarifs), 2)
    
    def test_multiple_actes_with_tarifs(self):
        """Test plusieurs actes avec leurs tarifs respectifs"""
        acte2 = Acte.objects.create(
            code='VGC',
            libelle='Visite gynécologique complète'
        )
        
        # Tarifs pour acte1
        TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today
        )
        
        # Tarifs pour acte2
        TarifPeriode.objects.create(
            acte=acte2,
            cout_xpf=8000,
            date_debut=self.today
        )
        
        self.assertEqual(self.acte.tarifs_periodes.count(), 1)
        self.assertEqual(acte2.tarifs_periodes.count(), 1)
        self.assertEqual(self.acte.tarif_actuel.cout_xpf, Decimal('5000'))
        self.assertEqual(acte2.tarif_actuel.cout_xpf, Decimal('8000'))