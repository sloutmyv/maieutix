"""
Tests pour le modèle PeriodeActivite
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from core.models import SageFemme, PeriodeActivite


class PeriodeActiviteModelTest(TestCase):
    """Tests pour le modèle PeriodeActivite"""
    
    def setUp(self):
        """Configuration des tests"""
        self.sage_femme = SageFemme.objects.create(
            nom="Test",
            prenom="Sage",
            titre="Sage-femme",
            telephone="123456789",
            email="test@example.com",
            numero_cafat="12345",
            ridet="67890",
            rib="123456789",
            banque="Test Bank",
            situation="titulaire"
        )
        
        self.aujourd_hui = timezone.now().date()
        self.hier = self.aujourd_hui - timedelta(days=1)
        self.demain = self.aujourd_hui + timedelta(days=1)
        self.dans_une_semaine = self.aujourd_hui + timedelta(days=7)
    
    def test_creation_periode_basique(self):
        """Test de création d'une période basique"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.aujourd_hui,
            commentaire="Test période"
        )
        
        self.assertEqual(periode.sage_femme, self.sage_femme)
        self.assertEqual(periode.date_debut, self.aujourd_hui)
        self.assertIsNone(periode.date_fin)
        self.assertEqual(periode.commentaire, "Test période")
    
    def test_str_representation(self):
        """Test de la représentation string"""
        # Période sans fin
        periode_sans_fin = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.aujourd_hui
        )
        expected = f"{self.sage_femme} - Depuis le {self.aujourd_hui}"
        self.assertEqual(str(periode_sans_fin), expected)
        
        # Période avec fin
        periode_avec_fin = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier,
            date_fin=self.demain
        )
        expected = f"{self.sage_femme} - {self.hier} au {self.demain}"
        self.assertEqual(str(periode_avec_fin), expected)
    
    def test_validation_date_fin_posterieure(self):
        """Test que la date de fin doit être postérieure à la date de début"""
        periode = PeriodeActivite(
            sage_femme=self.sage_femme,
            date_debut=self.aujourd_hui,
            date_fin=self.hier  # Date de fin antérieure
        )
        
        with self.assertRaises(ValidationError) as context:
            periode.full_clean()
        
        self.assertIn('date_fin', context.exception.message_dict)
    
    def test_validation_date_fin_egale_debut(self):
        """Test que la date de fin ne peut pas être égale à la date de début"""
        periode = PeriodeActivite(
            sage_femme=self.sage_femme,
            date_debut=self.aujourd_hui,
            date_fin=self.aujourd_hui  # Date de fin égale
        )
        
        with self.assertRaises(ValidationError) as context:
            periode.full_clean()
        
        self.assertIn('date_fin', context.exception.message_dict)
    
    def test_chevauchement_periodes(self):
        """Test de détection des chevauchements entre périodes fermées"""
        # Créer une première période fermée
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.aujourd_hui,
            date_fin=self.dans_une_semaine
        )
        
        # Tenter de créer une période fermée qui chevauche
        periode_chevauche = PeriodeActivite(
            sage_femme=self.sage_femme,
            date_debut=self.demain,  # Chevauche avec la première
            date_fin=self.dans_une_semaine + timedelta(days=3)
        )
        
        with self.assertRaises(ValidationError) as context:
            periode_chevauche.full_clean()
        
        self.assertIn('__all__', context.exception.message_dict)
    
    def test_pas_chevauchement_periodes_consecutives(self):
        """Test que des périodes consécutives ne sont pas considérées comme chevauchantes"""
        # Créer une première période
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier,
            date_fin=self.aujourd_hui
        )
        
        # Créer une période qui commence le lendemain (pas de chevauchement)
        periode_consecutive = PeriodeActivite(
            sage_femme=self.sage_femme,
            date_debut=self.demain
        )
        
        # Ne devrait pas lever d'exception
        try:
            periode_consecutive.full_clean()
        except ValidationError:
            self.fail("Des périodes consécutives ne devraient pas être considérées comme chevauchantes")
    
    def test_est_active_periode_en_cours(self):
        """Test pour une période en cours (sans date de fin)"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier  # Commencée hier, sans fin
        )
        
        self.assertTrue(periode.est_active)
        self.assertTrue(periode.est_en_cours)
    
    def test_est_active_periode_avec_fin_future(self):
        """Test pour une période avec date de fin dans le futur"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier,
            date_fin=self.demain
        )
        
        self.assertTrue(periode.est_active)
    
    def test_est_active_periode_terminee(self):
        """Test pour une période terminée"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier - timedelta(days=7),
            date_fin=self.hier
        )
        
        self.assertFalse(periode.est_active)
    
    def test_est_active_periode_future(self):
        """Test pour une période qui n'a pas encore commencé"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.demain,
            date_fin=self.dans_une_semaine
        )
        
        self.assertFalse(periode.est_active)
    
    def test_duree_jours_periode_avec_fin(self):
        """Test du calcul de durée pour une période avec fin"""
        debut = date(2024, 1, 1)
        fin = date(2024, 1, 10)
        
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=debut,
            date_fin=fin
        )
        
        self.assertEqual(periode.duree_jours, 9)  # 10 - 1 = 9 jours
    
    def test_duree_jours_periode_en_cours(self):
        """Test du calcul de durée pour une période en cours"""
        debut = self.aujourd_hui - timedelta(days=5)
        
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=debut
        )
        
        self.assertEqual(periode.duree_jours, 5)
    
    def test_statut_display_active_sans_fin(self):
        """Test de l'affichage du statut pour une période active sans fin"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier
        )
        
        self.assertEqual(periode.statut_display, "Active (en cours)")
    
    def test_statut_display_active_avec_fin(self):
        """Test de l'affichage du statut pour une période active avec fin"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier,
            date_fin=self.demain
        )
        
        expected = f"Active jusqu'au {self.demain}"
        self.assertEqual(periode.statut_display, expected)
    
    def test_statut_display_terminee(self):
        """Test de l'affichage du statut pour une période terminée"""
        fin = self.hier
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier - timedelta(days=7),
            date_fin=fin
        )
        
        expected = f"Terminée le {fin}"
        self.assertEqual(periode.statut_display, expected)
    
    def test_statut_display_a_venir(self):
        """Test de l'affichage du statut pour une période à venir"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.demain,
            date_fin=self.dans_une_semaine
        )
        
        self.assertEqual(periode.statut_display, "À venir")
    
    def test_ordering_par_defaut(self):
        """Test de l'ordre par défaut (date_debut DESC)"""
        # Créer plusieurs périodes fermées pour éviter les conflits de validation
        periode1 = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.aujourd_hui,
            date_fin=self.aujourd_hui + timedelta(days=1)
        )
        periode2 = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.demain,
            date_fin=self.demain + timedelta(days=1)
        )
        periode3 = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier,
            date_fin=self.hier + timedelta(days=1)
        )
        
        periodes = list(PeriodeActivite.objects.all())
        
        # Vérifier l'ordre : plus récent d'abord
        self.assertEqual(periodes[0], periode2)  # demain
        self.assertEqual(periodes[1], periode1)  # aujourd'hui
        self.assertEqual(periodes[2], periode3)  # hier
    
    def test_interdiction_double_periode_ouverte(self):
        """Test qu'on ne peut pas créer deux périodes ouvertes pour la même sage-femme"""
        # Créer une première période ouverte
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier
        )
        
        # Tenter de créer une seconde période ouverte
        periode_invalide = PeriodeActivite(
            sage_femme=self.sage_femme,
            date_debut=self.aujourd_hui
        )
        
        with self.assertRaises(ValidationError) as context:
            periode_invalide.full_clean()
        
        self.assertIn('Une période d\'activité ouverte existe déjà', str(context.exception))
    
    def test_creation_periode_fermee_avec_periode_ouverte_existante(self):
        """Test qu'on peut créer une période fermée non-chevauchante même avec une période ouverte"""
        # Créer une période ouverte
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.aujourd_hui
        )
        
        # Créer une période fermée dans le passé (non-chevauchante)
        periode_passee = PeriodeActivite(
            sage_femme=self.sage_femme,
            date_debut=self.hier - timedelta(days=7),
            date_fin=self.hier - timedelta(days=1)
        )
        
        # Ne devrait pas lever d'exception
        try:
            periode_passee.full_clean()
        except ValidationError:
            self.fail("Une période fermée non-chevauchante devrait être autorisée")
    
    def test_interdiction_periode_fermee_chevauchante_avec_periode_ouverte(self):
        """Test qu'on ne peut pas créer une période fermée qui chevauche avec une période ouverte"""
        # Créer une période ouverte
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier
        )
        
        # Tenter de créer une période fermée qui chevauche
        periode_chevauchante = PeriodeActivite(
            sage_femme=self.sage_femme,
            date_debut=self.aujourd_hui,  # Chevauche avec la période ouverte
            date_fin=self.demain
        )
        
        with self.assertRaises(ValidationError) as context:
            periode_chevauchante.full_clean()
        
        self.assertIn('chevauche avec la période ouverte existante', str(context.exception))
    
    def test_fermeture_periode_sans_creer_chevauchement(self):
        """Test qu'on peut fermer une période ouverte si ça ne crée pas de chevauchement"""
        # Créer une période ouverte
        periode_ouverte = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier
        )
        
        # Créer une période fermée dans le futur
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.dans_une_semaine,
            date_fin=self.dans_une_semaine + timedelta(days=2)
        )
        
        # Fermer la période ouverte avec une date qui ne crée pas de chevauchement
        periode_ouverte.date_fin = self.dans_une_semaine - timedelta(days=1)
        
        # Ne devrait pas lever d'exception
        try:
            periode_ouverte.full_clean()
        except ValidationError:
            self.fail("Fermer une période sans créer de chevauchement devrait être autorisé")
    
    def test_fermeture_periode_avec_chevauchement(self):
        """Test qu'on ne peut pas fermer une période si ça crée un chevauchement"""
        # Créer une période ouverte
        periode_ouverte = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier
        )
        
        # Créer une période fermée dans le futur
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.dans_une_semaine,
            date_fin=self.dans_une_semaine + timedelta(days=2)
        )
        
        # Tenter de fermer la période ouverte avec une date qui crée un chevauchement
        periode_ouverte.date_fin = self.dans_une_semaine + timedelta(days=1)  # Chevauche
        
        with self.assertRaises(ValidationError) as context:
            periode_ouverte.full_clean()
        
        self.assertIn('crée un chevauchement', str(context.exception))
    
    def test_verbose_names_avec_numerotation(self):
        """Test que les verbose names incluent la numérotation pour l'admin"""
        self.assertEqual(PeriodeActivite._meta.verbose_name, "2.1 Période d'activité")
        self.assertEqual(PeriodeActivite._meta.verbose_name_plural, "2.1 Périodes d'activité")