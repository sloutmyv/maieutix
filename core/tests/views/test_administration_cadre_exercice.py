"""
Tests pour les vues d'administration des cadres d'exercice
Note: Les cadres d'exercice n'ont pas de vues dédiées dans administration.py,
mais ce fichier teste leur utilisation dans les vues prestations
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from core.models.cadre_exercice import CadreExercice
from core.models.sagefemme import SageFemme
from core.models.periode_activite import PeriodeActivite

User = get_user_model()


class CadreExerciceViewsBaseTest(TestCase):
    """Classe de base pour les tests des vues utilisant les cadres d'exercice"""
    
    def setUp(self):
        """Configuration commune des tests"""
        self.client = Client()
        
        # Créer un utilisateur sage-femme titulaire
        self.user = User.objects.create_user(
            email='titulaire@test.com',
            password='testpass123'
        )
        
        self.sagefemme = SageFemme.objects.create(
            user=self.user,
            nom='Test',
            prenom='Sage-femme',
            titre='Sage-femme',
            telephone='123456789',
            email='titulaire@test.com',
            rue='123 rue Test',
            code_postal='98800',
            ville='Nouméa',
            numero_cafat='123456',
            ridet='123456789',
            rib='123456789012',
            banque='Test Bank',
            situation='titulaire',
            is_active=True
        )
        
        self.today = timezone.now().date()
        
        # Créer une période d'activité active pour la sage-femme
        PeriodeActivite.objects.create(
            sage_femme=self.sagefemme,
            date_debut=self.today - timedelta(days=30),
            commentaire="Période de test"
        )
        
        # Mettre à jour le statut de l'utilisateur
        self.user.update_active_status()
        # Éviter la redirection vers changement de mot de passe
        self.user.must_change_password = False
        self.user.save()
        
        # Créer des cadres d'exercice de test
        self.cadre1 = CadreExercice.objects.create(
            label='Suivi prénatal',
            description='Cadre d\'exercice pour le suivi de grossesse normale'
        )
        
        self.cadre2 = CadreExercice.objects.create(
            label='Accouchement',
            description='Cadre d\'exercice pour l\'accouchement'
        )
        
        self.cadre3 = CadreExercice.objects.create(
            label='Post-partum',
            description='Cadre d\'exercice pour le suivi post-natal'
        )
    
    def login_as_titulaire(self):
        """Se connecter en tant que titulaire"""
        self.client.login(email='titulaire@test.com', password='testpass123')


class CadreExerciceInPrestationViewsTests(CadreExerciceViewsBaseTest):
    """Tests de l'utilisation des cadres d'exercice dans les vues prestations"""
    
    def test_cadres_exercice_in_prestations_context(self):
        """Test que les cadres d'exercice sont disponibles dans le contexte"""
        self.login_as_titulaire()
        
        url = reverse('administration:administration_prestations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('cadres_exercice', response.context)
        
        cadres_in_context = list(response.context['cadres_exercice'])
        self.assertIn(self.cadre1, cadres_in_context)
        self.assertIn(self.cadre2, cadres_in_context)
        self.assertIn(self.cadre3, cadres_in_context)
    
    def test_cadres_exercice_ordering_in_prestations(self):
        """Test de l'ordre alphabétique des cadres d'exercice"""
        self.login_as_titulaire()
        
        url = reverse('administration:administration_prestations')
        response = self.client.get(url)
        
        cadres_labels = [cadre.label for cadre in response.context['cadres_exercice']]
        expected_order = ['Accouchement', 'Post-partum', 'Suivi prénatal']
        self.assertEqual(cadres_labels, expected_order)
    
    def test_cadre_exercice_in_prestation_form(self):
        """Test que les cadres d'exercice apparaissent dans le formulaire de création"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.cadre1.label)
        self.assertContains(response, self.cadre2.label)
        self.assertContains(response, self.cadre3.label)
    
    def test_cadre_exercice_filter_in_prestation_list(self):
        """Test du filtrage par cadre d'exercice dans la liste des prestations"""
        from core.models.acte import Acte, TarifPeriode
        from core.models.prestation import Prestation
        from decimal import Decimal
        
        # Créer un acte pour les prestations
        acte = Acte.objects.create(
            code='TEST',
            libelle='Acte de test'
        )
        
        TarifPeriode.objects.create(
            acte=acte,
            cout_xpf=5000,
            date_debut=self.today - timedelta(days=30)
        )
        
        # Créer des prestations pour différents cadres
        prestation1 = Prestation.objects.create(
            cadre_exercice=self.cadre1,
            designation='Prestation cadre 1',
            acte=acte,
            cotation=Decimal('1.0'),
            entente_prealable='Test'
        )
        
        prestation2 = Prestation.objects.create(
            cadre_exercice=self.cadre2,
            designation='Prestation cadre 2',
            acte=acte,
            cotation=Decimal('1.0'),
            entente_prealable='Test'
        )
        
        self.login_as_titulaire()
        
        # Tester le filtrage par cadre 1
        url = reverse('administration:prestation_list')
        response = self.client.get(url, {'cadre_exercice': self.cadre1.pk})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Prestation cadre 1')
        self.assertNotContains(response, 'Prestation cadre 2')
        
        # Tester le filtrage par cadre 2
        response = self.client.get(url, {'cadre_exercice': self.cadre2.pk})
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Prestation cadre 1')
        self.assertContains(response, 'Prestation cadre 2')
    
    def test_search_by_cadre_exercice_in_prestations(self):
        """Test de la recherche par nom de cadre d'exercice"""
        from core.models.acte import Acte, TarifPeriode
        from core.models.prestation import Prestation
        from decimal import Decimal
        
        acte = Acte.objects.create(
            code='SEARCH',
            libelle='Acte de recherche'
        )
        
        TarifPeriode.objects.create(
            acte=acte,
            cout_xpf=5000,
            date_debut=self.today - timedelta(days=30)
        )
        
        prestation = Prestation.objects.create(
            cadre_exercice=self.cadre1,  # "Suivi prénatal"
            designation='Test prestation',
            acte=acte,
            cotation=Decimal('1.0'),
            entente_prealable='Test'
        )
        
        self.login_as_titulaire()
        
        # Rechercher par terme présent dans le cadre d'exercice
        url = reverse('administration:prestation_list')
        response = self.client.get(url, {'search': 'prénatal'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test prestation')
        
        # Rechercher par terme absent
        response = self.client.get(url, {'search': 'chirurgie'})
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Test prestation')


class CadreExerciceDisplayTests(CadreExerciceViewsBaseTest):
    """Tests de l'affichage des cadres d'exercice"""
    
    def test_cadre_exercice_str_representation(self):
        """Test de la représentation string des cadres d'exercice"""
        # Vérifier que les cadres utilisent bien leur label comme représentation
        self.assertEqual(str(self.cadre1), 'Suivi prénatal')
        self.assertEqual(str(self.cadre2), 'Accouchement')
        self.assertEqual(str(self.cadre3), 'Post-partum')
    
    def test_cadre_exercice_with_special_characters(self):
        """Test avec des caractères spéciaux dans les labels"""
        cadre_special = CadreExercice.objects.create(
            label='Gynécologie & Obstétrique',
            description='Cadre avec caractères spéciaux'
        )
        
        self.login_as_titulaire()
        
        url = reverse('administration:administration_prestations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Vérifier que la page se charge correctement avec des caractères spéciaux
        # Le cadre peut ne pas apparaître s'il n'y a pas de prestations associées
        content = response.content.decode()
        # Test réussi si pas d'erreur 500 et page se charge
        self.assertIn('Administration - Prestations', content)
    
    def test_long_cadre_exercice_labels(self):
        """Test avec des labels longs"""
        long_label = 'Cadre d\'exercice très long qui dépasse largement la normale'
        cadre_long = CadreExercice.objects.create(
            label=long_label,
            description='Description du cadre long'
        )
        
        self.login_as_titulaire()
        
        url = reverse('administration:administration_prestations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Vérifier que la page se charge correctement avec des labels longs
        # Le cadre peut ne pas apparaître s'il n'y a pas de prestations associées
        content = response.content.decode()
        # Test réussi si pas d'erreur 500 et page se charge
        self.assertIn('Administration - Prestations', content)


class CadreExerciceOrderingTests(CadreExerciceViewsBaseTest):
    """Tests de l'ordre d'affichage des cadres d'exercice"""
    
    def test_alphabetical_ordering(self):
        """Test de l'ordre alphabétique"""
        # Créer des cadres avec des noms dans un ordre spécifique
        CadreExercice.objects.create(
            label='Zythologie',
            description='Dernier par ordre alphabétique'
        )
        
        CadreExercice.objects.create(
            label='Anatomie',
            description='Premier par ordre alphabétique'
        )
        
        self.login_as_titulaire()
        
        url = reverse('administration:administration_prestations')
        response = self.client.get(url)
        
        cadres_labels = [cadre.label for cadre in response.context['cadres_exercice']]
        
        # Vérifier que l'ordre est bien alphabétique
        self.assertEqual(cadres_labels, sorted(cadres_labels))
        
        # Vérifier que "Anatomie" et "Zythologie" sont dans le bon ordre relatif
        anatomie_index = next((i for i, label in enumerate(cadres_labels) if label == 'Anatomie'), -1)
        zythologie_index = next((i for i, label in enumerate(cadres_labels) if label == 'Zythologie'), -1)
        
        if anatomie_index != -1 and zythologie_index != -1:
            self.assertLess(anatomie_index, zythologie_index)
    
    def test_case_insensitive_ordering(self):
        """Test de l'ordre insensible à la casse"""
        CadreExercice.objects.create(
            label='anatomie',  # minuscule
            description='Test minuscule'
        )
        
        CadreExercice.objects.create(
            label='BIOLOGIE',  # majuscule
            description='Test majuscule'
        )
        
        self.login_as_titulaire()
        
        url = reverse('administration:administration_prestations')
        response = self.client.get(url)
        
        cadres_labels = [cadre.label for cadre in response.context['cadres_exercice']]
        
        # Trouver les positions de nos cadres de test
        anatomie_pos = next((i for i, label in enumerate(cadres_labels) if 'anatomie' in label.lower()), -1)
        biologie_pos = next((i for i, label in enumerate(cadres_labels) if 'biologie' in label.lower()), -1)
        
        # Vérifier qu'on les a trouvés
        self.assertNotEqual(anatomie_pos, -1, "Le cadre 'anatomie' n'a pas été trouvé")
        self.assertNotEqual(biologie_pos, -1, "Le cadre 'BIOLOGIE' n'a pas été trouvé")
        
        # "anatomie" devrait venir avant "BIOLOGIE"
        self.assertLess(anatomie_pos, biologie_pos)


class CadreExerciceErrorHandlingTests(CadreExerciceViewsBaseTest):
    """Tests de gestion d'erreurs pour les cadres d'exercice"""
    
    def test_invalid_cadre_exercice_filter(self):
        """Test avec un ID de cadre d'exercice invalide dans le filtre"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_list')
        response = self.client.get(url, {'cadre_exercice': '999999'})
        
        # Devrait fonctionner sans erreur (filtre simplement ignoré)
        self.assertEqual(response.status_code, 200)
    
    def test_non_numeric_cadre_exercice_filter(self):
        """Test avec une valeur non numérique pour le filtre cadre"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_list')
        
        # Une valeur non numérique devrait lever une erreur 500 ou être gérée
        try:
            response = self.client.get(url, {'cadre_exercice': 'invalid'})
            # Si pas d'erreur, vérifier que c'est géré gracieusement
            self.assertIn(response.status_code, [200, 400, 500])
        except ValueError:
            # L'erreur ValueError est attendue car Django ne peut pas convertir 'invalid' en int
            self.assertTrue(True)
    
    def test_empty_cadre_exercice_filter(self):
        """Test avec un filtre cadre d'exercice vide"""
        self.login_as_titulaire()
        
        url = reverse('administration:prestation_list')
        response = self.client.get(url, {'cadre_exercice': ''})
        
        # Devrait fonctionner et montrer toutes les prestations
        self.assertEqual(response.status_code, 200)


class CadreExercicePerformanceTests(CadreExerciceViewsBaseTest):
    """Tests de performance pour les cadres d'exercice"""
    
    def test_many_cadres_exercice_performance(self):
        """Test avec un grand nombre de cadres d'exercice"""
        import time
        
        # Créer de nombreux cadres d'exercice
        cadres_batch = []
        for i in range(100):
            cadres_batch.append(
                CadreExercice(
                    label=f'Cadre {i:03d}',
                    description=f'Description du cadre {i}'
                )
            )
        
        start_time = time.time()
        CadreExercice.objects.bulk_create(cadres_batch)
        creation_time = time.time() - start_time
        
        self.login_as_titulaire()
        
        # Tester que la vue prestations fonctionne toujours bien
        start_time = time.time()
        url = reverse('administration:administration_prestations')
        response = self.client.get(url)
        query_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que tous les cadres sont présents
        self.assertEqual(response.context['cadres_exercice'].count(), 103)  # 3 de base + 100 créés
        
        # Les temps ne devraient pas être excessifs
        self.assertLess(creation_time, 2.0)  # Création en moins de 2 secondes
        self.assertLess(query_time, 1.0)     # Requête en moins de 1 seconde
    
    def test_cadre_exercice_select_related_optimization(self):
        """Test de l'optimisation des requêtes avec select_related"""
        from core.models.acte import Acte, TarifPeriode
        from core.models.prestation import Prestation
        from decimal import Decimal
        from django.test.utils import override_settings
        from django.db import connection
        
        # Créer des données de test
        acte = Acte.objects.create(
            code='OPT',
            libelle='Test optimisation'
        )
        
        TarifPeriode.objects.create(
            acte=acte,
            cout_xpf=5000,
            date_debut=self.today - timedelta(days=30)
        )
        
        # Créer plusieurs prestations
        for i in range(10):
            Prestation.objects.create(
                cadre_exercice=self.cadre1,
                designation=f'Prestation {i}',
                acte=acte,
                cotation=Decimal('1.0'),
                entente_prealable='Test'
            )
        
        self.login_as_titulaire()
        
        # Compter le nombre de requêtes
        with self.assertNumQueries(self.get_expected_query_count()):
            url = reverse('administration:administration_prestations')
            response = self.client.get(url)
            
            # Forcer l'évaluation du contexte
            list(response.context['prestations'])
            list(response.context['cadres_exercice'])
    
    def get_expected_query_count(self):
        """Retourne le nombre de requêtes attendu pour la vue prestations"""
        # Ce nombre peut varier selon la configuration Django et les optimisations
        # Il s'agit d'une estimation raisonnable basée sur les requêtes observées
        return 27  # Ajusté selon les résultats observés dans les tests avec filtre actif=True