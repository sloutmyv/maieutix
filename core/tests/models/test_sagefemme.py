"""
Tests pour le modèle SageFemme.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from core.models.sagefemme import SageFemme


class SageFemmeModelTest(TestCase):
    """Tests du modèle SageFemme"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.sage_femme_data = {
            'nom': 'Dupont',
            'prenom': 'Marie',
            'titre': 'Sage-femme diplômée',
            'telephone': '687123456',
            'email': 'marie.dupont@test.nc',
            'numero_cafat': '123456789',
            'ridet': 'RIDET123456',
            'rib': 'FR1234567890123456789012345',
            'banque': 'BCI',
            'situation': 'titulaire'
        }

    def test_creation_sage_femme_valide(self):
        """Test de création d'une sage-femme avec des données valides"""
        sage_femme = SageFemme.objects.create(**self.sage_femme_data)
        
        self.assertEqual(sage_femme.nom, 'Dupont')
        self.assertEqual(sage_femme.prenom, 'Marie')
        self.assertEqual(sage_femme.situation, 'titulaire')
        self.assertIsNotNone(sage_femme.created_at)
        self.assertIsNotNone(sage_femme.updated_at)

    def test_str_representation(self):
        """Test de la représentation string du modèle"""
        sage_femme = SageFemme.objects.create(**self.sage_femme_data)
        expected = "Dupont Marie (Titulaire)"
        self.assertEqual(str(sage_femme), expected)

    def test_nom_complet_property(self):
        """Test de la propriété nom_complet"""
        sage_femme = SageFemme.objects.create(**self.sage_femme_data)
        self.assertEqual(sage_femme.nom_complet, "Marie Dupont")

    def test_adresse_complete_property_avec_adresse(self):
        """Test de la propriété adresse_complete avec adresse renseignée"""
        data = self.sage_femme_data.copy()
        data.update({
            'rue': '123 Rue de la République',
            'code_postal': '98800',
            'ville': 'Nouméa'
        })
        sage_femme = SageFemme.objects.create(**data)
        
        expected = "123 Rue de la République, 98800 Nouméa"
        self.assertEqual(sage_femme.adresse_complete, expected)

    def test_adresse_complete_property_sans_adresse(self):
        """Test de la propriété adresse_complete sans adresse"""
        sage_femme = SageFemme.objects.create(**self.sage_femme_data)
        self.assertEqual(sage_femme.adresse_complete, "Adresse non renseignée")

    def test_champs_obligatoires(self):
        """Test que les champs obligatoires sont requis"""
        champs_obligatoires = [
            'nom', 'prenom', 'titre', 'telephone', 'email', 
            'numero_cafat', 'ridet', 'rib', 'banque', 'situation'
        ]
        
        for champ in champs_obligatoires:
            data = self.sage_femme_data.copy()
            del data[champ]
            
            with self.assertRaises(ValidationError):
                SageFemme.objects.create(**data)

    def test_champs_optionnels(self):
        """Test que les champs d'adresse sont optionnels"""
        sage_femme = SageFemme.objects.create(**self.sage_femme_data)
        
        self.assertIsNone(sage_femme.rue)
        self.assertIsNone(sage_femme.code_postal)
        self.assertIsNone(sage_femme.ville)

    def test_choix_situation_valides(self):
        """Test des choix valides pour le champ situation"""
        # Créer un titulaire qui servira de référence pour les remplaçants
        titulaire = SageFemme.objects.create(**self.sage_femme_data)
        
        situations_valides = ['titulaire', 'collaborateur', 'remplacant']
        
        for situation in situations_valides:
            data = self.sage_femme_data.copy()
            data['situation'] = situation
            data['email'] = f'test_{situation}@example.com'  # Email unique
            data['numero_cafat'] = f'{situation}123456789'  # CAFAT unique
            data['ridet'] = f'RIDET{situation}123456'  # RIDET unique
            
            if situation == 'remplacant':
                # Les remplaçants ont besoin d'un remplacement_de
                data['remplacement_de'] = titulaire
            
            sage_femme = SageFemme.objects.create(**data)
            self.assertEqual(sage_femme.situation, situation)

    def test_situation_invalide(self):
        """Test avec une situation invalide"""
        data = self.sage_femme_data.copy()
        data['situation'] = 'situation_invalide'
        
        with self.assertRaises(ValidationError):
            sage_femme = SageFemme(**data)
            sage_femme.full_clean()

    def test_email_format_invalide(self):
        """Test avec un email au format invalide"""
        data = self.sage_femme_data.copy()
        data['email'] = 'email_invalide'
        
        with self.assertRaises(ValidationError):
            sage_femme = SageFemme(**data)
            sage_femme.full_clean()

    def test_jours_activite_cumules_sans_periode(self):
        """Test que jours_activite_cumules retourne 0 sans période"""
        sage_femme = SageFemme.objects.create(**self.sage_femme_data)
        self.assertEqual(sage_femme.jours_activite_cumules, 0)
    
    def test_statut_activite_sans_periode(self):
        """Test que statut_activite retourne 'Inactif' sans période"""
        sage_femme = SageFemme.objects.create(**self.sage_femme_data)
        self.assertEqual(sage_femme.statut_activite, "Inactif")

    def test_meta_ordering(self):
        """Test de l'ordre par défaut"""
        # Créer plusieurs sages-femmes avec des noms distincts
        zebra = SageFemme.objects.create(
            **{**self.sage_femme_data, 'nom': 'Zebra', 'prenom': 'Alice', 'email': 'alice@test.nc'}
        )
        alpha = SageFemme.objects.create(
            **{**self.sage_femme_data, 'nom': 'Alpha', 'prenom': 'Bob', 'email': 'bob@test.nc'}
        )
        dupont = SageFemme.objects.create(**self.sage_femme_data)
        
        # Récupérer seulement les enregistrements créés dans ce test
        created_ids = [zebra.pk, alpha.pk, dupont.pk]
        sages_femmes = list(SageFemme.objects.filter(pk__in=created_ids).order_by('nom', 'prenom'))
        
        # Vérifier l'ordre par nom puis prénom
        self.assertEqual(sages_femmes[0].nom, 'Alpha')
        self.assertEqual(sages_femmes[1].nom, 'Dupont')
        self.assertEqual(sages_femmes[2].nom, 'Zebra')

    def test_verbose_names(self):
        """Test des noms verbeux du modèle"""
        self.assertEqual(SageFemme._meta.verbose_name, '2. Sage-femme')
        self.assertEqual(SageFemme._meta.verbose_name_plural, '2. Sages-femmes')


class SageFemmeRemplacantTest(TestCase):
    """Tests spécifiques aux remplaçants"""

    def setUp(self):
        """Configuration pour les tests de remplaçants"""
        # Créer un gérant
        self.titulaire = SageFemme.objects.create(
            nom='Titulaire',
            prenom='Pierre',
            titre='Sage-femme titulaire',
            telephone='687111111',
            email='pierre.titulaire@test.nc',
            numero_cafat='111111111',
            ridet='RIDET111111',
            rib='FR1111111111111111111111111',
            banque='BCI',
            situation='titulaire'
        )
        
        # Créer un collaborateur
        self.collaborateur = SageFemme.objects.create(
            nom='Collaborateur',
            prenom='Julie',
            titre='Sage-femme collaboratrice',
            telephone='687222222',
            email='julie.collaborateur@test.nc',
            numero_cafat='222222222',
            ridet='RIDET222222',
            rib='FR2222222222222222222222222',
            banque='BCI',
            situation='collaborateur'
        )

    def test_creation_remplacant_valide(self):
        """Test de création d'un remplaçant valide"""
        remplacant = SageFemme.objects.create(
            nom='Remplacant',
            prenom='Sophie',
            titre='Sage-femme remplaçante',
            telephone='687333333',
            email='sophie.remplacant@test.nc',
            numero_cafat='333333333',
            ridet='RIDET333333',
            rib='FR3333333333333333333333333',
            banque='BCI',
            situation='remplacant',
            remplacement_de=self.titulaire,
            etat_recapitulatif_commun=True,
            bons_depot_communs=True
        )
        
        self.assertEqual(remplacant.situation, 'remplacant')
        self.assertEqual(remplacant.remplacement_de, self.titulaire)
        self.assertTrue(remplacant.etat_recapitulatif_commun)
        self.assertTrue(remplacant.bons_depot_communs)

    def test_remplacant_sans_remplacement_de(self):
        """Test qu'un remplaçant doit avoir un remplacement_de"""
        with self.assertRaises(ValidationError) as context:
            remplacant = SageFemme(
                nom='Remplacant',
                prenom='Sophie',
                titre='Sage-femme remplaçante',
                telephone='687333333',
                email='sophie.remplacant@test.nc',
                numero_cafat='333333333',
                ridet='RIDET333333',
                rib='FR3333333333333333333333333',
                banque='BCI',
                situation='remplacant'
                # remplacement_de manquant
            )
            remplacant.full_clean()
        
        self.assertIn('remplacement_de', context.exception.message_dict)

    def test_titulaire_avec_remplacement_de(self):
        """Test qu'un titulaire ne peut pas avoir de remplacement_de"""
        with self.assertRaises(ValidationError) as context:
            titulaire = SageFemme(
                nom='Titulaire2',
                prenom='Paul',
                titre='Sage-femme titulaire',
                telephone='687444444',
                email='paul.titulaire@test.nc',
                numero_cafat='444444444',
                ridet='RIDET444444',
                rib='FR4444444444444444444444444',
                banque='BCI',
                situation='titulaire',
                remplacement_de=self.titulaire  # Ne devrait pas être permis
            )
            titulaire.full_clean()
        
        self.assertIn('remplacement_de', context.exception.message_dict)

    def test_collaborateur_avec_remplacement_de(self):
        """Test qu'un collaborateur ne peut pas avoir de remplacement_de"""
        with self.assertRaises(ValidationError) as context:
            collaborateur = SageFemme(
                nom='Collaborateur2',
                prenom='Anne',
                titre='Sage-femme collaboratrice',
                telephone='687555555',
                email='anne.collaborateur@test.nc',
                numero_cafat='555555555',
                ridet='RIDET555555',
                rib='FR5555555555555555555555555',
                banque='BCI',
                situation='collaborateur',
                remplacement_de=self.titulaire  # Ne devrait pas être permis
            )
            collaborateur.full_clean()
        
        self.assertIn('remplacement_de', context.exception.message_dict)

    def test_remplacant_de_remplacant_interdit(self):
        """Test qu'un remplaçant ne peut pas remplacer un autre remplaçant"""
        # Créer un premier remplaçant
        remplacant1 = SageFemme.objects.create(
            nom='Remplacant1',
            prenom='Sophie',
            titre='Sage-femme remplaçante',
            telephone='687333333',
            email='sophie.remplacant@test.nc',
            numero_cafat='333333333',
            ridet='RIDET333333',
            rib='FR3333333333333333333333333',
            banque='BCI',
            situation='remplacant',
            remplacement_de=self.titulaire
        )
        
        # Tenter de créer un remplaçant du remplaçant
        with self.assertRaises(ValidationError) as context:
            remplacant2 = SageFemme(
                nom='Remplacant2',
                prenom='Claire',
                titre='Sage-femme remplaçante',
                telephone='687666666',
                email='claire.remplacant@test.nc',
                numero_cafat='666666666',
                ridet='RIDET666666',
                rib='FR6666666666666666666666666',
                banque='BCI',
                situation='remplacant',
                remplacement_de=remplacant1  # Ne devrait pas être permis
            )
            remplacant2.full_clean()
        
        self.assertIn('remplacement_de', context.exception.message_dict)

    def test_save_nettoie_champs_remplacant(self):
        """Test que save() nettoie les champs spécifiques aux remplaçants pour les non-remplaçants"""
        # Créer un titulaire avec des champs de remplaçant (ne devrait pas être permis)
        titulaire = SageFemme(
            nom='Titulaire3',
            prenom='Marc',
            titre='Sage-femme titulaire',
            telephone='687777777',
            email='marc.titulaire@test.nc',
            numero_cafat='777777777',
            ridet='RIDET777777',
            rib='FR7777777777777777777777777',
            banque='BCI',
            situation='titulaire',
            remplacement_de=self.titulaire,  # Sera nettoyé
            etat_recapitulatif_commun=True,  # Sera nettoyé
            bons_depot_communs=True  # Sera nettoyé
        )
        
        titulaire.save()
        
        # Vérifier que les champs ont été nettoyés
        self.assertIsNone(titulaire.remplacement_de)
        self.assertFalse(titulaire.etat_recapitulatif_commun)
        self.assertFalse(titulaire.bons_depot_communs)

    def test_champs_remplacant_par_defaut_false(self):
        """Test que les champs spécifiques aux remplaçants sont False par défaut"""
        sage_femme = SageFemme.objects.create(
            nom='Test',
            prenom='Test',
            titre='Test',
            telephone='687000000',
            email='test@test.nc',
            numero_cafat='000000000',
            ridet='RIDET000000',
            rib='FR0000000000000000000000000',
            banque='BCI',
            situation='titulaire'
        )
        
        self.assertFalse(sage_femme.etat_recapitulatif_commun)
        self.assertFalse(sage_femme.bons_depot_communs)
        self.assertIsNone(sage_femme.remplacement_de)


class SageFemmeActiviteTest(TestCase):
    """Tests pour la logique d'activité des sage-femmes basée sur les périodes"""
    
    def setUp(self):
        """Configuration pour les tests d'activité"""
        from core.models.periode_activite import PeriodeActivite
        from datetime import date, timedelta
        
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
        
        self.today = date.today()
        self.PeriodeActivite = PeriodeActivite
    
    def test_est_actuellement_active_sans_periode(self):
        """Test qu'une sage-femme sans période n'est pas active"""
        self.assertFalse(self.sage_femme.est_actuellement_active)
    
    def test_est_actuellement_active_avec_periode_en_cours(self):
        """Test qu'une sage-femme avec période en cours est active"""
        from datetime import timedelta
        
        # Créer une période qui a commencé il y a 30 jours et n'a pas de fin
        self.PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=30)
        )
        
        self.assertTrue(self.sage_femme.est_actuellement_active)
    
    def test_est_actuellement_active_avec_periode_future(self):
        """Test qu'une sage-femme avec période future n'est pas active"""
        from datetime import timedelta
        
        # Créer une période qui commencera dans 30 jours
        self.PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today + timedelta(days=30)
        )
        
        self.assertFalse(self.sage_femme.est_actuellement_active)
    
    def test_est_actuellement_active_avec_periode_terminee(self):
        """Test qu'une sage-femme avec période terminée n'est pas active"""
        from datetime import timedelta
        
        # Créer une période terminée
        self.PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=60),
            date_fin=self.today - timedelta(days=30)
        )
        
        self.assertFalse(self.sage_femme.est_actuellement_active)
    
    def test_jours_activite_cumules_periode_en_cours(self):
        """Test du calcul des jours cumulés avec période en cours"""
        from datetime import timedelta
        
        # Période commencée il y a 30 jours (sans fin)
        self.PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=30)
        )
        
        # 30 jours + aujourd'hui = 31 jours
        self.assertEqual(self.sage_femme.jours_activite_cumules, 31)
    
    def test_jours_activite_cumules_periode_terminee(self):
        """Test du calcul des jours cumulés avec période terminée"""
        from datetime import timedelta
        
        # Période de 30 jours terminée
        debut = self.today - timedelta(days=60)
        fin = self.today - timedelta(days=30)
        self.PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=debut,
            date_fin=fin
        )
        
        # 31 jours (60-30+1)
        expected_days = (fin - debut).days + 1
        self.assertEqual(self.sage_femme.jours_activite_cumules, expected_days)
    
    def test_jours_activite_cumules_plusieurs_periodes(self):
        """Test du calcul des jours cumulés avec plusieurs périodes"""
        from datetime import timedelta
        
        # Première période terminée (30 jours)
        self.PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=90),
            date_fin=self.today - timedelta(days=60)
        )
        
        # Deuxième période en cours (20 jours)
        self.PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=20)
        )
        
        # 31 jours (première période) + 21 jours (période en cours) = 52 jours
        self.assertEqual(self.sage_femme.jours_activite_cumules, 52)
    
    def test_jours_activite_cumules_ignore_periode_future(self):
        """Test que les périodes futures ne sont pas comptées"""
        from datetime import timedelta
        
        # Période en cours
        self.PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=10)
        )
        
        # Période future (ne doit pas être comptée)
        self.PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today + timedelta(days=30)
        )
        
        # Seule la période en cours compte : 11 jours
        self.assertEqual(self.sage_femme.jours_activite_cumules, 11)
    
    def test_statut_activite_avec_periode_en_cours(self):
        """Test du statut avec période en cours"""
        from datetime import timedelta
        
        self.PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=30)
        )
        
        self.assertEqual(self.sage_femme.statut_activite, "Actif")
    
    def test_statut_activite_avec_periode_future(self):
        """Test du statut avec période future"""
        from datetime import timedelta
        
        future_date = self.today + timedelta(days=30)
        self.PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=future_date
        )
        
        expected = f"Inactif (reprend le {future_date})"
        self.assertEqual(self.sage_femme.statut_activite, expected)
    
    def test_periode_activite_actuelle_avec_periode_en_cours(self):
        """Test de la propriété periode_activite_actuelle"""
        from datetime import timedelta
        
        periode = self.PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=30)
        )
        
        self.assertEqual(self.sage_femme.periode_activite_actuelle, periode)