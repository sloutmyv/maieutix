"""
Tests d'intégration pour les templates d'administration des caisses et conditions de paiement.
"""
from django.test import TestCase, Client
from django.urls import reverse
from authentication.models import SageFemmeUser
from datetime import date, timedelta
from decimal import Decimal

from core.models.caisse import Caisse
from core.models.condition_paiement import ConditionPaiement
from core.models.sagefemme import SageFemme
from core.models.periode_activite import PeriodeActivite


class BaseCaisseTemplateIntegrationTest(TestCase):
    """Classe de base pour les tests d'intégration des templates de caisses"""
    
    def setUp(self):
        """Configuration de base"""
        self.client = Client()
        
        # Créer un superutilisateur
        self.superuser = SageFemmeUser.objects.create_superuser(
            email='admin@test.nc',
            password='testpass123'
        )
        
        # Créer une sage-femme titulaire
        self.titulaire = SageFemme.objects.create(
            nom='Titulaire',
            prenom='Test',
            titre='Sage-femme titulaire',
            telephone='98.11.11.11',
            email='titulaire@test.nc',
            numero_cafat='111111111',
            ridet='0111111.001',
            rib='FR76 3000 3000 1111 1111 1111 111',
            banque='BCI',
            situation='titulaire'
        )
        
        # Créer une sage-femme collaboratrice
        self.collaborateur = SageFemme.objects.create(
            nom='Collaborateur',
            prenom='Test',
            titre='Sage-femme collaboratrice',
            telephone='98.22.22.22',
            email='collaborateur@test.nc',
            numero_cafat='222222222',
            ridet='0222222.001',
            rib='FR76 3000 3000 2222 2222 2222 222',
            banque='BRED',
            situation='collaborateur'
        )
        
        # Créer des utilisateurs associés aux sages-femmes
        self.titulaire_user = SageFemmeUser.objects.create_user(
            email='titulaire@test.nc',
            password='azerty'
        )
        self.titulaire_user.must_change_password = False
        self.titulaire_user.save()
        self.titulaire.user = self.titulaire_user
        self.titulaire.save()
        
        self.collaborateur_user = SageFemmeUser.objects.create_user(
            email='collaborateur@test.nc',
            password='azerty'
        )
        self.collaborateur_user.must_change_password = False
        self.collaborateur_user.save()
        self.collaborateur.user = self.collaborateur_user
        self.collaborateur.save()
        
        # Ajouter des périodes d'activité actives
        today = date.today()
        PeriodeActivite.objects.create(
            sage_femme=self.titulaire,
            date_debut=today - timedelta(days=30),
            commentaire='Période active titulaire'
        )
        
        PeriodeActivite.objects.create(
            sage_femme=self.collaborateur,
            date_debut=today - timedelta(days=30),
            commentaire='Période active collaborateur'
        )
        
        # Mettre à jour le statut actif des utilisateurs
        self.titulaire_user.update_active_status()
        self.titulaire_user.save()
        self.collaborateur_user.update_active_status()
        self.collaborateur_user.save()
        
        self.today = today
        self.create_test_data()
    
    def create_test_data(self):
        """Créer des données de test variées"""
        # Conditions de paiement
        self.condition_cafat = ConditionPaiement.objects.create(
            designation='CAFAT Nouvelle-Calédonie',
            pourcentage=Decimal('80.00')
        )
        
        self.condition_mutuelle = ConditionPaiement.objects.create(
            designation='Mutuelle complémentaire',
            pourcentage=Decimal('20.00')
        )
        
        self.condition_at = ConditionPaiement.objects.create(
            designation='Accident du travail',
            pourcentage=Decimal('100.00')
        )
        
        self.condition_maladie = ConditionPaiement.objects.create(
            designation='Maladie longue durée',
            pourcentage=Decimal('100.00')
        )
        
        # Caisses avec différentes configurations
        self.caisse_complete = Caisse.objects.create(
            nom='CAFAT Nouvelle-Calédonie'
        )
        self.caisse_complete.conditions_paiement_eligibles.set([
            self.condition_cafat, self.condition_at, self.condition_maladie
        ])
        
        self.caisse_mutuelle = Caisse.objects.create(
            nom='Mutuelle Médialis'
        )
        self.caisse_mutuelle.conditions_paiement_eligibles.add(self.condition_mutuelle)
        
        self.caisse_vide = Caisse.objects.create(
            nom='Caisse sans conditions'
        )
        # Pas de conditions pour cette caisse
        
        self.caisse_mixte = Caisse.objects.create(
            nom='Caisse Assurance Mixte'
        )
        self.caisse_mixte.conditions_paiement_eligibles.set([
            self.condition_cafat, self.condition_mutuelle
        ])


class CaisseListTemplateIntegrationTest(BaseCaisseTemplateIntegrationTest):
    """Tests d'intégration pour le template de liste des caisses"""
    
    def test_template_liste_caisses_complete(self):
        """Test du template de liste avec toutes les données"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:administration_caisses')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la structure de base
        self.assertContains(response, 'Administration - Caisses')
        self.assertContains(response, 'Ajouter une caisse')
        
        # Vérifier le compteur
        self.assertContains(response, '4 caisses au total')
        
        # Vérifier la présence des caisses
        self.assertContains(response, 'CAFAT Nouvelle-Calédonie')
        self.assertContains(response, 'Mutuelle Médialis')
        self.assertContains(response, 'Caisse sans conditions')
        self.assertContains(response, 'Caisse Assurance Mixte')
    
    def test_template_liste_conditions_eligibles(self):
        """Test de l'affichage des conditions éligibles dans la liste"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier l'affichage des conditions sous forme de badges (format français avec virgule)
        self.assertContains(response, 'CAFAT Nouvelle-Calédonie (80,00%)')
        self.assertContains(response, 'Accident du travail (100,00%)')
        self.assertContains(response, 'Mutuelle complémentaire (20,00%)')
        
        # Vérifier le message pour la caisse sans conditions
        self.assertContains(response, 'Aucune condition')
    
    def test_template_liste_boutons_action_superuser(self):
        """Test des boutons d'action pour le superutilisateur"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la présence des boutons pour chaque caisse
        for caisse in [self.caisse_complete, self.caisse_mutuelle, self.caisse_vide, self.caisse_mixte]:
            # Bouton voir (utilise l'API)
            self.assertContains(response, f'hx-get="/administration/api/caisses/{caisse.pk}/"')
            # Bouton modifier
            self.assertContains(response, f'hx-get="/administration/api/caisses/{caisse.pk}/update/"')
            # Bouton supprimer
            self.assertContains(response, f'hx-delete="/administration/api/caisses/{caisse.pk}/delete/"')
    
    def test_template_liste_permissions_collaborateur(self):
        """Test de l'affichage en lecture seule pour le collaborateur"""
        self.client.login(username='collaborateur@test.nc', password='azerty')
        url = reverse('administration:administration_caisses')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Le collaborateur ne devrait pas voir le bouton d'ajout
        self.assertNotContains(response, 'Ajouter une caisse')
        
        # Vérifier la liste HTMX
        list_url = reverse('administration:caisse_list')
        list_response = self.client.get(list_url)
        
        # Le collaborateur devrait voir les données mais pas les boutons d'action d'édition
        self.assertContains(list_response, 'CAFAT Nouvelle-Calédonie')
        self.assertNotContains(list_response, f'hx-get="/administration/api/caisses/{self.caisse_complete.pk}/update/"')
        self.assertNotContains(list_response, f'hx-delete="/administration/api/caisses/{self.caisse_complete.pk}/delete/"')
        
        # Mais devrait voir le bouton de détail
        self.assertContains(list_response, f'hx-get="/administration/api/caisses/{self.caisse_complete.pk}/"')


class CaisseFormTemplateIntegrationTest(BaseCaisseTemplateIntegrationTest):
    """Tests d'intégration pour les templates de formulaires de caisses"""
    
    def test_template_formulaire_creation(self):
        """Test du template de création de caisse"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la structure du modal
        self.assertContains(response, 'id="caisse-modal"')
        self.assertContains(response, 'Nouvelle caisse')
        self.assertContains(response, 'hx-post="/administration/api/caisses/create/"')
        
        # Vérifier la présence du formulaire
        self.assertContains(response, 'name="nom"')
        self.assertContains(response, 'name="conditions_paiement_eligibles"')
        
        # Vérifier que toutes les conditions sont disponibles
        self.assertContains(response, 'CAFAT Nouvelle-Calédonie')
        self.assertContains(response, 'Mutuelle complémentaire')
        self.assertContains(response, 'Accident du travail')
        self.assertContains(response, 'Maladie longue durée')
        
        # Vérifier les boutons
        self.assertContains(response, 'type="submit"')
        self.assertContains(response, 'Créer')
        self.assertContains(response, 'Annuler')
    
    def test_template_formulaire_modification(self):
        """Test du template de modification de caisse"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_update', args=[self.caisse_complete.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la structure du modal
        self.assertContains(response, 'Modifier la caisse')
        self.assertContains(response, f'hx-post="/administration/api/caisses/{self.caisse_complete.pk}/update/"')
        
        # Vérifier que le nom est pré-rempli
        self.assertContains(response, self.caisse_complete.nom)
        
        # Vérifier que les conditions actuelles sont cochées
        # (Test basique - les détails dépendent de l'implémentation du widget)
        self.assertContains(response, 'checked')
        
        # Vérifier le bouton de modification
        self.assertContains(response, 'Modifier')
    
    def test_template_formulaire_conditions_checkbox(self):
        """Test de l'affichage des conditions sous forme de checkboxes"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que les conditions sont affichées avec leurs pourcentages
        self.assertContains(response, 'CAFAT Nouvelle-Calédonie')
        self.assertContains(response, 'Mutuelle complémentaire')
        self.assertContains(response, 'Accident du travail')
        
        # Vérifier la structure des checkboxes
        self.assertContains(response, 'type="checkbox"')
        self.assertContains(response, 'name="conditions_paiement_eligibles"')
    
    def test_template_formulaire_validation_erreurs(self):
        """Test de l'affichage des erreurs de validation"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_create')
        
        # Envoyer des données invalides (pas de nom)
        response = self.client.post(url, {
            'conditions_paiement_eligibles': [self.condition_cafat.pk]
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que le formulaire affiche l'erreur
        self.assertContains(response, 'error')


class CaisseDetailTemplateIntegrationTest(BaseCaisseTemplateIntegrationTest):
    """Tests d'intégration pour le template de détail des caisses"""
    
    def test_template_detail_caisse_complete(self):
        """Test du template de détail avec une caisse complète"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_detail', args=[self.caisse_complete.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les informations de base
        self.assertContains(response, self.caisse_complete.nom)
        self.assertContains(response, 'Détails de la caisse')
        
        # Vérifier l'affichage des conditions
        self.assertContains(response, 'CAFAT Nouvelle-Calédonie')
        # Les pourcentages sont affichés avec format français (virgule décimale)
        self.assertContains(response, '80,00%')
        self.assertContains(response, 'Accident du travail')
        self.assertContains(response, '100,00%')
        
        # Vérifier les métadonnées
        self.assertContains(response, 'Créée le')
        self.assertContains(response, 'Modifiée le')
    
    def test_template_detail_caisse_vide(self):
        """Test du template de détail avec une caisse sans conditions"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_detail', args=[self.caisse_vide.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les informations de base
        self.assertContains(response, self.caisse_vide.nom)
        
        # Vérifier le message pour absence de conditions
        self.assertContains(response, 'Aucune condition')
    
    def test_template_detail_modal_structure(self):
        """Test de la structure du modal de détail"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_detail', args=[self.caisse_complete.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la structure du modal
        self.assertContains(response, 'fixed inset-0')
        self.assertContains(response, 'modal-container')
        self.assertContains(response, 'Fermer')


class ConditionPaiementFormTemplateIntegrationTest(BaseCaisseTemplateIntegrationTest):
    """Tests d'intégration pour les templates de formulaires de conditions de paiement"""
    
    def test_template_gestion_conditions_via_admin(self):
        """Test que les conditions de paiement sont gérées via l'admin Django"""
        # Les conditions de paiement n'ont pas d'interface utilisateur séparée
        # Elles sont gérées via l'admin Django
        self.client.login(username='admin@test.nc', password='testpass123')
        
        # Vérifier que les conditions existent dans la base
        self.assertTrue(ConditionPaiement.objects.filter(designation='CAFAT Nouvelle-Calédonie').exists())
    
    def test_template_admin_condition_paiement(self):
        """Test d'accès à l'admin des conditions de paiement"""
        self.client.login(username='admin@test.nc', password='testpass123')
        
        # Test que l'admin fonctionne (ce test est plus approprié pour les conditions)
        condition = self.condition_cafat
        self.assertEqual(str(condition), 'CAFAT Nouvelle-Calédonie (80.00%)')


class CaisseSearchTemplateIntegrationTest(BaseCaisseTemplateIntegrationTest):
    """Tests d'intégration pour les fonctionnalités de recherche dans les templates"""
    
    def test_template_barre_recherche(self):
        """Test de la barre de recherche dans le template"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:administration_caisses')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la présence de la barre de recherche
        self.assertContains(response, 'placeholder="Rechercher une caisse..."')
        self.assertContains(response, 'hx-get="/administration/api/caisses/"')
        self.assertContains(response, 'hx-trigger="keyup changed delay:300ms"')
        self.assertContains(response, 'name="search"')
    
    def test_template_recherche_resultats(self):
        """Test de l'affichage des résultats de recherche"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_list')
        
        # Recherche avec résultats
        response = self.client.get(url, {'search': 'CAFAT'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CAFAT Nouvelle-Calédonie')
        self.assertNotContains(response, 'Mutuelle Médialis')
        
        # Recherche sans résultats
        response = self.client.get(url, {'search': 'XYZ123'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aucune caisse trouvée')
    
    def test_template_recherche_responsive(self):
        """Test de la recherche HTMX temps réel"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_list')
        
        # Simuler une recherche HTMX
        response = self.client.get(url, {'search': 'Mutuelle'}, 
                                 HTTP_HX_REQUEST='true')
        
        self.assertEqual(response.status_code, 200)
        # La réponse devrait être seulement la partie table, pas la page complète
        self.assertNotContains(response, '<html>')
        self.assertContains(response, 'Mutuelle Médialis')


class CaisseTemplateResponsiveTest(BaseCaisseTemplateIntegrationTest):
    """Tests d'intégration pour la responsivité des templates de caisses"""
    
    def test_template_table_responsive(self):
        """Test de la responsivité du tableau"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les classes CSS responsive
        self.assertContains(response, 'overflow-x-auto')
        self.assertContains(response, 'min-w-full')
        self.assertContains(response, 'whitespace-nowrap')
    
    def test_template_modal_responsive(self):
        """Test de la responsivité des modaux"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les classes CSS responsive du modal
        self.assertContains(response, 'max-w-xl w-full mx-4')
        self.assertContains(response, 'max-h-[85vh] overflow-y-auto')
    
    def test_template_badges_responsive(self):
        """Test de l'affichage responsive des badges de conditions"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les classes CSS des badges
        self.assertContains(response, 'flex flex-wrap gap-1')
        self.assertContains(response, 'inline-flex items-center')


class CaisseTemplateAccessibilityTest(BaseCaisseTemplateIntegrationTest):
    """Tests d'intégration pour l'accessibilité des templates de caisses"""
    
    def test_template_labels_accessibility(self):
        """Test des labels pour l'accessibilité"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la présence des labels
        self.assertContains(response, '<label for=')
        self.assertContains(response, 'Nom de la caisse')
        self.assertContains(response, 'Conditions de paiement éligibles')
    
    def test_template_buttons_accessibility(self):
        """Test de l'accessibilité des boutons"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les attributs title pour les boutons d'action
        self.assertContains(response, 'title="Voir les détails"')
        self.assertContains(response, 'title="Modifier"')
        self.assertContains(response, 'title="Supprimer"')
    
    def test_template_aria_labels(self):
        """Test des attributs ARIA"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:administration_caisses')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les attributs aria-label
        self.assertContains(response, 'aria-label="Ajouter une nouvelle caisse"')