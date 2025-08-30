"""
Tests d'intégration pour les templates d'administration des sage-femmes.
"""
from django.test import TestCase, Client
from django.urls import reverse
from authentication.models import SageFemmeUser
from datetime import date, timedelta
from core.models.sagefemme import SageFemme
from core.models.periode_activite import PeriodeActivite


class BaseTemplateIntegrationTest(TestCase):
    """Classe de base pour les tests d'intégration des templates"""
    
    def setUp(self):
        """Configuration de base"""
        self.client = Client()
        
        # Créer un superutilisateur
        self.superuser = SageFemmeUser.objects.create_superuser(
            email='admin@test.nc',
            password='testpass123'
        )
        
        self.today = date.today()
        
        # Créer des sage-femmes de test avec différentes situations
        self.create_test_data()
    
    def create_test_data(self):
        """Créer des données de test variées"""
        # Sage-femme titulaire active
        self.titulaire_active = SageFemme.objects.create(
            nom='Titulaire',
            prenom='Marie',
            titre='Sage-femme titulaire',
            telephone='98.11.11.11',
            email='marie.titulaire@test.nc',
            rue='123 Rue de la Paix',
            code_postal='98800',
            ville='Nouméa',
            numero_cafat='111111111',
            ridet='0111111.001',
            rib='FR76 3000 3000 1111 1111 1111 111',
            banque='BCI',
            situation='titulaire'
        )
        
        # Période active pour le titulaire
        PeriodeActivite.objects.create(
            sage_femme=self.titulaire_active,
            date_debut=self.today - timedelta(days=30),
            commentaire='Période active'
        )
        
        # Sage-femme collaborateur inactive
        self.collaborateur_inactif = SageFemme.objects.create(
            nom='Collaborateur',
            prenom='Julie',
            titre='Sage-femme collaboratrice',
            telephone='98.22.22.22',
            email='julie.collaborateur@test.nc',
            numero_cafat='222222222',
            ridet='0222222.001',
            rib='FR76 3000 3000 2222 2222 2222 222',
            banque='BRED',
            situation='collaborateur'
        )
        
        # Période terminée pour le collaborateur
        PeriodeActivite.objects.create(
            sage_femme=self.collaborateur_inactif,
            date_debut=self.today - timedelta(days=90),
            date_fin=self.today - timedelta(days=30),
            commentaire='Période terminée'
        )
        
        # Remplaçant
        self.remplacant = SageFemme.objects.create(
            nom='Remplacant',
            prenom='Sophie',
            titre='Sage-femme remplaçante',
            telephone='98.33.33.33',
            email='sophie.remplacant@test.nc',
            numero_cafat='333333333',
            ridet='0333333.001',
            rib='FR76 3000 3000 3333 3333 3333 333',
            banque='BNC',
            situation='remplacant',
            remplacement_de=self.titulaire_active,
            etat_recapitulatif_commun=True,
            bons_depot_communs=True
        )
        
        # Période en cours pour le remplaçant
        PeriodeActivite.objects.create(
            sage_femme=self.remplacant,
            date_debut=self.today - timedelta(days=10),
            date_fin=self.today + timedelta(days=20),
            commentaire='Remplacement temporaire'
        )


class SagesFemmesListTemplateTest(BaseTemplateIntegrationTest):
    """Tests d'intégration pour le template de liste des sage-femmes"""
    
    def test_affichage_liste_complete(self):
        """Test de l'affichage complet de la liste"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:administration_sages_femmes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que toutes les sage-femmes sont affichées
        self.assertContains(response, self.titulaire_active.nom_complet)
        self.assertContains(response, self.collaborateur_inactif.nom_complet)
        self.assertContains(response, self.remplacant.nom_complet)
        
        # Vérifier les éléments de l'interface
        self.assertContains(response, 'Administration - Sages Femmes')
        self.assertContains(response, 'Ajouter')
        self.assertContains(response, 'Rechercher')
    
    def test_affichage_statuts_activite(self):
        """Test de l'affichage des statuts d'activité"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:administration_sages_femmes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les badges de statut
        self.assertContains(response, 'Actif')  # Pour titulaire et remplaçant
        self.assertContains(response, 'Inactif')  # Pour collaborateur
        
        # Vérifier les couleurs des badges
        content = response.content.decode()
        self.assertIn('bg-green', content)
        self.assertIn('text-green', content)
        self.assertIn('bg-red', content)
        self.assertIn('text-red', content)
    
    def test_boutons_actions(self):
        """Test de l'affichage des boutons d'action"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:administration_sages_femmes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les boutons d'action pour chaque sage-femme
        content = response.content.decode()
        
        # Vérifier présence d'icônes SVG des actions
        self.assertIn('<svg', content)
        self.assertIn('viewBox', content)


class SageFemmeFormTemplateTest(BaseTemplateIntegrationTest):
    """Tests d'intégration pour les templates de formulaire"""
    
    def test_formulaire_creation_affichage(self):
        """Test de l'affichage du formulaire de création"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier le titre du modal
        self.assertContains(response, 'Ajouter')
        
        # Vérifier les champs principaux
        fields_to_check = [
            'nom', 'prenom', 'titre', 'telephone', 'email',
            'rue', 'code_postal', 'ville',
            'numero_cafat', 'ridet', 'rib', 'banque',
            'situation'
        ]
        
        for field in fields_to_check:
            self.assertContains(response, f'name="{field}"')
        
        # Vérifier les boutons
        self.assertContains(response, 'Annuler')
        self.assertContains(response, 'Ajouter')
    
    def test_formulaire_gestion_situation_remplacant(self):
        """Test de la gestion dynamique des champs remplaçant"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les champs spécifiques aux remplaçants
        self.assertContains(response, 'remplacement_de')
        self.assertContains(response, 'etat_recapitulatif_commun')
        self.assertContains(response, 'bons_depot_communs')


class SageFemmeDetailTemplateTest(BaseTemplateIntegrationTest):
    """Tests d'intégration pour le template de détail"""
    
    def test_detail_informations_generales(self):
        """Test de l'affichage des informations générales"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_detail', args=[self.titulaire_active.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les informations principales
        self.assertContains(response, self.titulaire_active.nom_complet)
        self.assertContains(response, self.titulaire_active.titre)
        self.assertContains(response, self.titulaire_active.telephone)
        self.assertContains(response, self.titulaire_active.email)
        
        # Vérifier les informations professionnelles
        self.assertContains(response, self.titulaire_active.numero_cafat)
        self.assertContains(response, self.titulaire_active.ridet)
    
    def test_detail_remplacant_informations(self):
        """Test de l'affichage spécifique pour un remplaçant"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_detail', args=[self.remplacant.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les informations de remplacement
        self.assertContains(response, 'Remplaçant')
        self.assertContains(response, 'Remplace')
        self.assertContains(response, self.titulaire_active.nom_complet)


class ResponsiveTemplateTest(BaseTemplateIntegrationTest):
    """Tests de responsive design et d'accessibilité"""
    
    def test_classes_responsive(self):
        """Test de la présence des classes responsive"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:administration_sages_femmes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les classes Tailwind responsive
        content = response.content.decode()
        self.assertIn('max-w-7xl', content)         # Container responsive
        self.assertIn('overflow-x-auto', content)   # Tableau responsive
    
    def test_accessibility_attributes(self):
        """Test des attributs d'accessibilité"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:administration_sages_femmes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode()
        
        # Vérifier les attributs d'accessibilité
        self.assertIn('title="', content)           # Tooltips
        self.assertIn('aria-', content)             # Attributs ARIA si présents


class JavaScriptIntegrationTest(BaseTemplateIntegrationTest):
    """Tests d'intégration JavaScript et HTMX"""
    
    def test_htmx_attributes_presence(self):
        """Test de la présence des attributs HTMX"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:administration_sages_femmes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode()
        
        # Vérifier les attributs HTMX présents dans cette page
        htmx_attributes = [
            'hx-get', 'hx-delete',
            'hx-target', 'hx-swap', 'hx-trigger',
            'hx-confirm'
        ]
        
        for attr in htmx_attributes:
            self.assertIn(attr, content)
    
    def test_javascript_functions_presence(self):
        """Test de la présence des fonctions JavaScript essentielles"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_update', args=[self.titulaire_active.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode()
        
        # Vérifier présence de comportements JavaScript
        js_present = any(js in content for js in ["onclick=", "onchange=", "hx-"])
        self.assertTrue(js_present)


class ErrorHandlingTemplateTest(BaseTemplateIntegrationTest):
    """Tests de gestion d'erreurs dans les templates"""
    
    def test_template_404_handling(self):
        """Test de gestion des erreurs 404"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_detail', args=[9999])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_template_with_missing_data(self):
        """Test de template avec des données manquantes"""
        # Créer une sage-femme avec des données minimales
        sage_femme_minimale = SageFemme.objects.create(
            nom='Minimal',
            prenom='Test',
            titre='Test',
            telephone='98.99.99.99',
            email='minimal@test.nc',
            numero_cafat='999999999',
            ridet='0999999.001',
            rib='FR76 3000 3000 9999 9999 9999 999',
            banque='Test',
            situation='titulaire'
        )
        
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_detail', args=[sage_femme_minimale.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que le template gère les champs optionnels vides
        content = response.content.decode()
        self.assertIn('MINIMAL', content)  # Le nom est affiché en majuscules
        self.assertIn('Test', content)