"""
Tests complets pour le modèle PeriodeActivite.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import date, timedelta
from core.models.sagefemme import SageFemme
from core.models.periode_activite import PeriodeActivite


class PeriodeActiviteModelTest(TestCase):
    """Tests du modèle PeriodeActivite"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.sage_femme = SageFemme.objects.create(
            nom='Test',
            prenom='Marie',
            titre='Sage-femme test',
            telephone='687123456',
            email='marie.test@example.nc',
            numero_cafat='123456789',
            ridet='RIDET123456',
            rib='FR1234567890123456789012345',
            banque='BCI',
            situation='titulaire'
        )
        
        self.today = timezone.now().date()
        self.periode_data = {
            'sage_femme': self.sage_femme,
            'date_debut': self.today,
            'commentaire': 'Test période'
        }

    def test_creation_periode_valide(self):
        """Test de création d'une période avec des données valides"""
        periode = PeriodeActivite.objects.create(**self.periode_data)
        
        self.assertEqual(periode.sage_femme, self.sage_femme)
        self.assertEqual(periode.date_debut, self.today)
        self.assertIsNone(periode.date_fin)
        self.assertEqual(periode.commentaire, 'Test période')

    def test_str_representation(self):
        """Test de la représentation string du modèle"""
        periode = PeriodeActivite.objects.create(**self.periode_data)
        expected = f"Marie TEST - Du {self.today.strftime('%d/%m/%Y')} (en cours)"
        self.assertEqual(str(periode), expected)

    def test_str_representation_avec_fin(self):
        """Test de la représentation string avec date de fin"""
        fin = self.today + timedelta(days=30)
        data = self.periode_data.copy()
        data['date_fin'] = fin
        
        periode = PeriodeActivite.objects.create(**data)
        expected = f"Marie TEST - Du {self.today.strftime('%d/%m/%Y')} au {fin.strftime('%d/%m/%Y')}"
        self.assertEqual(str(periode), expected)

    def test_champs_obligatoires(self):
        """Test que les champs obligatoires sont requis"""
        # sage_femme obligatoire
        with self.assertRaises(IntegrityError):
            PeriodeActivite.objects.create(
                date_debut=self.today,
                commentaire='Test'
            )
    
    def test_date_debut_obligatoire(self):
        """Test que date_debut est obligatoire"""
        # date_debut obligatoire
        with self.assertRaises(IntegrityError):
            PeriodeActivite.objects.create(
                sage_femme=self.sage_femme,
                commentaire='Test'
            )

    def test_commentaire_optionnel(self):
        """Test que le commentaire est optionnel"""
        data = self.periode_data.copy()
        del data['commentaire']
        
        periode = PeriodeActivite.objects.create(**data)
        self.assertEqual(periode.commentaire, '')

    def test_date_fin_optionnelle(self):
        """Test que la date de fin est optionnelle"""
        periode = PeriodeActivite.objects.create(**self.periode_data)
        self.assertIsNone(periode.date_fin)

    def test_meta_ordering(self):
        """Test de l'ordre par défaut (date_debut décroissant)"""
        # Créer plusieurs périodes
        periode1 = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=30),
            commentaire='Période 1'
        )
        periode2 = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today,
            commentaire='Période 2'
        )
        periode3 = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=10),
            commentaire='Période 3'
        )
        
        periodes = list(PeriodeActivite.objects.all())
        
        # Vérifier l'ordre : plus récent en premier
        self.assertEqual(periodes[0], periode2)  # Aujourd'hui
        self.assertEqual(periodes[1], periode3)  # Il y a 10 jours
        self.assertEqual(periodes[2], periode1)  # Il y a 30 jours

    def test_verbose_names(self):
        """Test des noms verbeux du modèle"""
        self.assertEqual(PeriodeActivite._meta.verbose_name, '2.1 Période d\'activité')
        self.assertEqual(PeriodeActivite._meta.verbose_name_plural, '2.1 Périodes d\'activité')


class PeriodeActivitePropertyTest(TestCase):
    """Tests des propriétés du modèle PeriodeActivite"""

    def setUp(self):
        """Configuration pour les tests de propriétés"""
        self.sage_femme = SageFemme.objects.create(
            nom='Test',
            prenom='Marie',
            titre='Sage-femme test',
            telephone='687123456',
            email='marie.test@example.nc',
            numero_cafat='123456789',
            ridet='RIDET123456',
            rib='FR1234567890123456789012345',
            banque='BCI',
            situation='titulaire'
        )
        self.today = timezone.now().date()

    def test_est_active_periode_en_cours(self):
        """Test qu'une période sans date de fin commencée est active"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=10)
        )
        
        self.assertTrue(periode.est_active)

    def test_est_active_periode_future(self):
        """Test qu'une période future n'est pas active"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today + timedelta(days=10)
        )
        
        self.assertFalse(periode.est_active)

    def test_est_active_periode_terminee(self):
        """Test qu'une période terminée n'est pas active"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=30),
            date_fin=self.today - timedelta(days=10)
        )
        
        self.assertFalse(periode.est_active)

    def test_est_active_periode_se_termine_aujourd_hui(self):
        """Test qu'une période qui se termine aujourd'hui est encore active"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=30),
            date_fin=self.today
        )
        
        self.assertTrue(periode.est_active)

    def test_est_active_periode_commence_aujourd_hui(self):
        """Test qu'une période qui commence aujourd'hui est active"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today
        )
        
        self.assertTrue(periode.est_active)

    def test_est_en_cours_alias(self):
        """Test que est_en_cours est un alias de est_active"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=10)
        )
        
        self.assertEqual(periode.est_active, periode.est_en_cours)

    def test_duree_jours_periode_en_cours(self):
        """Test du calcul de durée pour une période en cours"""
        debut = self.today - timedelta(days=30)
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=debut
        )
        
        expected_duree = (self.today - debut).days + 1  # Calcul inclusif
        self.assertEqual(periode.duree_jours, expected_duree)

    def test_duree_jours_periode_terminee(self):
        """Test du calcul de durée pour une période terminée"""
        debut = self.today - timedelta(days=60)
        fin = self.today - timedelta(days=30)
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=debut,
            date_fin=fin
        )
        
        expected_duree = (fin - debut).days + 1  # Calcul inclusif
        self.assertEqual(periode.duree_jours, expected_duree)

    def test_statut_display_periode_active_sans_fin(self):
        """Test du statut display pour période active sans fin"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=10)
        )
        
        self.assertEqual(periode.statut_display, "Active (en cours)")

    def test_statut_display_periode_active_avec_fin(self):
        """Test du statut display pour période active avec fin future"""
        fin = self.today + timedelta(days=30)
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=10),
            date_fin=fin
        )
        
        expected = f"Active jusqu'au {fin}"
        self.assertEqual(periode.statut_display, expected)

    def test_statut_display_periode_terminee(self):
        """Test du statut display pour période terminée"""
        fin = self.today - timedelta(days=10)
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=30),
            date_fin=fin
        )
        
        expected = f"Terminée le {fin}"
        self.assertEqual(periode.statut_display, expected)

    def test_statut_display_periode_future(self):
        """Test du statut display pour période future"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today + timedelta(days=30)
        )
        
        self.assertEqual(periode.statut_display, "À venir")


class PeriodeActiviteValidationTest(TestCase):
    """Tests de validation du modèle PeriodeActivite"""

    def setUp(self):
        """Configuration pour les tests de validation"""
        self.sage_femme = SageFemme.objects.create(
            nom='Test',
            prenom='Marie',
            titre='Sage-femme test',
            telephone='687123456',
            email='marie.test@example.nc',
            numero_cafat='123456789',
            ridet='RIDET123456',
            rib='FR1234567890123456789012345',
            banque='BCI',
            situation='titulaire'
        )
        self.today = timezone.now().date()

    def test_validation_date_fin_avant_debut(self):
        """Test que la date de fin ne peut pas être avant le début"""
        with self.assertRaises(ValidationError) as context:
            periode = PeriodeActivite(
                sage_femme=self.sage_femme,
                date_debut=self.today,
                date_fin=self.today - timedelta(days=1)
            )
            periode.full_clean()
        
        self.assertIn('date_fin', context.exception.message_dict)

    def test_validation_date_fin_egale_debut(self):
        """Test que la date de fin peut être égale au début"""
        periode = PeriodeActivite(
            sage_femme=self.sage_femme,
            date_debut=self.today,
            date_fin=self.today
        )
        
        # Ne doit pas lever d'erreur
        periode.full_clean()
        periode.save()
        
        self.assertEqual(periode.date_fin, self.today)

    def test_validation_periodes_chevauchantes(self):
        """Test de la validation des périodes qui se chevauchent"""
        # Créer une première période
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=30),
            date_fin=self.today + timedelta(days=30)
        )
        
        # Tenter de créer une période qui chevauche
        with self.assertRaises(ValidationError) as context:
            periode = PeriodeActivite(
                sage_femme=self.sage_femme,
                date_debut=self.today - timedelta(days=10),
                date_fin=self.today + timedelta(days=10)
            )
            periode.full_clean()
        
        error_message = str(context.exception.message_dict)
        self.assertIn('période existante', error_message.lower())

    def test_validation_periodes_consecutives_autorisees(self):
        """Test que des périodes consécutives sont autorisées"""
        # Créer une première période
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=60),
            date_fin=self.today - timedelta(days=30)
        )
        
        # Créer une période qui commence le jour suivant
        periode = PeriodeActivite(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=29),
            date_fin=self.today
        )
        
        # Ne doit pas lever d'erreur
        periode.full_clean()
        periode.save()
        
        self.assertIsNotNone(periode.pk)

    def test_validation_plusieurs_periodes_sans_fin(self):
        """Test qu'on ne peut avoir qu'une seule période sans fin par sage-femme"""
        # Créer une première période sans fin
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=30)
        )
        
        # Tenter de créer une deuxième période sans fin
        with self.assertRaises(ValidationError) as context:
            periode = PeriodeActivite(
                sage_femme=self.sage_femme,
                date_debut=self.today
            )
            periode.full_clean()
        
        error_message = str(context.exception.message_dict)
        self.assertIn('période en cours', error_message.lower())

    def test_save_modification_commentaire(self):
        """Test de modification du commentaire"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today,
            commentaire='Initial'
        )
        
        initial_commentaire = periode.commentaire
        
        periode.commentaire = 'Modifié'
        periode.save()
        
        # Vérifier que le commentaire a bien été modifié
        periode.refresh_from_db()
        self.assertNotEqual(periode.commentaire, initial_commentaire)
        self.assertEqual(periode.commentaire, 'Modifié')


class PeriodeActiviteRelationTest(TestCase):
    """Tests des relations du modèle PeriodeActivite"""

    def setUp(self):
        """Configuration pour les tests de relations"""
        self.sage_femme = SageFemme.objects.create(
            nom='Test',
            prenom='Marie',
            titre='Sage-femme test',
            telephone='687123456',
            email='marie.test@example.nc',
            numero_cafat='123456789',
            ridet='RIDET123456',
            rib='FR1234567890123456789012345',
            banque='BCI',
            situation='titulaire'
        )
        self.today = timezone.now().date()

    def test_relation_sage_femme(self):
        """Test de la relation avec SageFemme"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today
        )
        
        # Test relation directe
        self.assertEqual(periode.sage_femme, self.sage_femme)
        
        # Test relation inverse
        self.assertIn(periode, self.sage_femme.periodes_activite.all())

    def test_suppression_cascade(self):
        """Test que la suppression d'une sage-femme supprime ses périodes"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today
        )
        
        periode_id = periode.pk
        
        # Supprimer la sage-femme
        self.sage_femme.delete()
        
        # Vérifier que la période a été supprimée
        with self.assertRaises(PeriodeActivite.DoesNotExist):
            PeriodeActivite.objects.get(pk=periode_id)

    def test_related_name(self):
        """Test du nom de la relation inverse"""
        periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today
        )
        
        # Utiliser le related_name
        periodes = self.sage_femme.periodes_activite.all()
        self.assertEqual(len(periodes), 1)
        self.assertEqual(periodes[0], periode)