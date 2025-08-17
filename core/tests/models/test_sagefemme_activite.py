"""
Tests pour les méthodes d'activité du modèle SageFemme
"""

from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from core.models import SageFemme, PeriodeActivite


class SageFemmeActiviteTest(TestCase):
    """Tests pour les méthodes de gestion d'activité des sages-femmes"""
    
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
            situation="gerant"
        )
        
        self.aujourd_hui = timezone.now().date()
        self.hier = self.aujourd_hui - timedelta(days=1)
        self.demain = self.aujourd_hui + timedelta(days=1)
        self.dans_une_semaine = self.aujourd_hui + timedelta(days=7)
    
    def test_periode_activite_actuelle_sans_periodes(self):
        """Test quand il n'y a aucune période d'activité"""
        self.assertIsNone(self.sage_femme.periode_activite_actuelle)
    
    def test_periode_activite_actuelle_avec_periode_en_cours(self):
        """Test avec une période en cours (sans date de fin)"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier
        )
        
        self.assertEqual(self.sage_femme.periode_activite_actuelle, periode)
    
    def test_periode_activite_actuelle_avec_periode_future(self):
        """Test avec une période qui n'a pas encore commencé"""
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.demain
        )
        
        self.assertIsNone(self.sage_femme.periode_activite_actuelle)
    
    def test_periode_activite_actuelle_avec_periode_terminee(self):
        """Test avec une période terminée"""
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier - timedelta(days=7),
            date_fin=self.hier
        )
        
        self.assertIsNone(self.sage_femme.periode_activite_actuelle)
    
    def test_periode_activite_actuelle_avec_periode_active_avec_fin(self):
        """Test avec une période active ayant une date de fin future"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier,
            date_fin=self.demain
        )
        
        self.assertEqual(self.sage_femme.periode_activite_actuelle, periode)
    
    def test_est_actuellement_active_sans_periodes(self):
        """Test du statut d'activité sans périodes"""
        self.assertFalse(self.sage_femme.est_actuellement_active)
    
    def test_est_actuellement_active_avec_periode_active(self):
        """Test du statut d'activité avec une période active"""
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier
        )
        
        self.assertTrue(self.sage_femme.est_actuellement_active)
    
    def test_est_actuellement_active_avec_periode_terminee(self):
        """Test du statut d'activité avec une période terminée"""
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier - timedelta(days=7),
            date_fin=self.hier
        )
        
        self.assertFalse(self.sage_femme.est_actuellement_active)
    
    def test_statut_activite_desactivee(self):
        """Test du statut quand la sage-femme est désactivée"""
        self.sage_femme.is_active = False
        self.sage_femme.save()
        
        self.assertEqual(self.sage_femme.statut_activite, "Inactive (désactivée)")
    
    def test_statut_activite_sans_periodes(self):
        """Test du statut sans périodes d'activité"""
        expected = "Aucune période d'activité définie"
        self.assertEqual(self.sage_femme.statut_activite, expected)
    
    def test_statut_activite_avec_periode_active(self):
        """Test du statut avec une période active"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier
        )
        
        self.assertEqual(self.sage_femme.statut_activite, periode.statut_display)
    
    def test_statut_activite_avec_periode_future(self):
        """Test du statut avec une période future"""
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.demain
        )
        
        expected = f"Inactive (reprend le {self.demain})"
        self.assertEqual(self.sage_femme.statut_activite, expected)
    
    def test_ajouter_periode_activite(self):
        """Test d'ajout d'une période d'activité"""
        periode = self.sage_femme.ajouter_periode_activite(
            date_debut=self.aujourd_hui,
            date_fin=self.dans_une_semaine,
            commentaire="Test période"
        )
        
        self.assertEqual(periode.sage_femme, self.sage_femme)
        self.assertEqual(periode.date_debut, self.aujourd_hui)
        self.assertEqual(periode.date_fin, self.dans_une_semaine)
        self.assertEqual(periode.commentaire, "Test période")
        
        # Vérifier que la période est sauvegardée
        self.assertTrue(PeriodeActivite.objects.filter(pk=periode.pk).exists())
    
    def test_ajouter_periode_activite_sans_fin(self):
        """Test d'ajout d'une période sans date de fin"""
        periode = self.sage_femme.ajouter_periode_activite(
            date_debut=self.aujourd_hui
        )
        
        self.assertEqual(periode.sage_femme, self.sage_femme)
        self.assertEqual(periode.date_debut, self.aujourd_hui)
        self.assertIsNone(periode.date_fin)
        self.assertEqual(periode.commentaire, "")
    
    def test_get_periodes_actives(self):
        """Test de récupération des périodes actives"""
        # Créer différents types de périodes
        periode_en_cours = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier
        )
        
        periode_future = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.demain,
            date_fin=self.dans_une_semaine
        )
        
        periode_terminee = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier - timedelta(days=7),
            date_fin=self.hier
        )
        
        periodes_actives = self.sage_femme.get_periodes_actives()
        
        self.assertIn(periode_en_cours, periodes_actives)
        self.assertIn(periode_future, periodes_actives)
        self.assertNotIn(periode_terminee, periodes_actives)
    
    def test_get_periodes_passees(self):
        """Test de récupération des périodes passées"""
        # Créer différents types de périodes
        periode_en_cours = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier
        )
        
        periode_future = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.demain,
            date_fin=self.dans_une_semaine
        )
        
        periode_terminee = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier - timedelta(days=7),
            date_fin=self.hier
        )
        
        periodes_passees = self.sage_femme.get_periodes_passees()
        
        self.assertNotIn(periode_en_cours, periodes_passees)
        self.assertNotIn(periode_future, periodes_passees)
        self.assertIn(periode_terminee, periodes_passees)
    
    def test_get_periodes_avec_sage_femme_autre(self):
        """Test que les méthodes ne retournent que les périodes de la bonne sage-femme"""
        # Créer une autre sage-femme
        autre_sage_femme = SageFemme.objects.create(
            nom="Autre",
            prenom="Test",
            titre="Sage-femme",
            telephone="987654321",
            email="autre@example.com",
            numero_cafat="54321",
            ridet="09876",
            rib="987654321",
            banque="Other Bank",
            situation="collaborateur"
        )
        
        # Créer des périodes pour chaque sage-femme
        periode_sage1 = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.hier
        )
        
        periode_sage2 = PeriodeActivite.objects.create(
            sage_femme=autre_sage_femme,
            date_debut=self.hier
        )
        
        # Vérifier que chaque sage-femme ne voit que ses périodes
        periodes_sage1 = self.sage_femme.get_periodes_actives()
        periodes_sage2 = autre_sage_femme.get_periodes_actives()
        
        self.assertIn(periode_sage1, periodes_sage1)
        self.assertNotIn(periode_sage2, periodes_sage1)
        
        self.assertIn(periode_sage2, periodes_sage2)
        self.assertNotIn(periode_sage1, periodes_sage2)