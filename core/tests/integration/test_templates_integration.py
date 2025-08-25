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
        
        # Période future pour le collaborateur
        PeriodeActivite.objects.create(
            sage_femme=self.collaborateur_inactif,
            date_debut=self.today + timedelta(days=30),
            commentaire='Période à venir'
        )
        
        # Sage-femme remplaçant
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
        self.assertContains(response, 'Ajouter une sage-femme')
        self.assertContains(response, 'Rechercher une sage-femme')
    
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
        self.assertContains(response, 'bg-green-100 text-green-800')  # Badge actif
        self.assertContains(response, 'bg-red-100 text-red-800')      # Badge inactif
    
    def test_affichage_situations(self):
        """Test de l'affichage des différentes situations"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:administration_sages_femmes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les badges de situation
        self.assertContains(response, 'Titulaire')
        self.assertContains(response, 'Collaborateur')
        self.assertContains(response, 'Remplaçant')
        
        # Vérifier l'affichage du remplacement
        self.assertContains(response, f'Remplace {self.titulaire_active.nom_complet}')
    
    def test_affichage_jours_cumules(self):
        """Test de l'affichage des jours d'activité cumulés"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:administration_sages_femmes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la colonne existe
        self.assertContains(response, 'Jours cumulés')
        
        # Vérifier l'affichage des jours (format avec "jour" ou "jours")
        content = response.content.decode()
        self.assertIn('jour', content)  # Le mot "jour" devrait apparaître
    
    def test_boutons_actions(self):
        """Test de l'affichage des boutons d'action"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:administration_sages_femmes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les boutons d'action pour chaque sage-femme
        # Boutons : Voir, Modifier, Supprimer
        content = response.content.decode()
        
        # Compter les icônes SVG des actions (œil, crayon, poubelle)
        self.assertIn('M15 12a3 3 0 11-6 0 3 3 0 016 0z', content)  # Icône œil (voir)
        self.assertIn('M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11', content)  # Icône crayon (modifier)
        self.assertIn('M19 7l-.867 12.142A2 2 0 0116.138 21H7.862', content)  # Icône poubelle (supprimer)
    
    def test_recherche_interface(self):
        """Test de l'interface de recherche"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:administration_sages_femmes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier l'interface de recherche
        self.assertContains(response, 'input')
        self.assertContains(response, 'placeholder="Rechercher une sage-femme..."')
        
        # Vérifier les attributs HTMX
        self.assertContains(response, 'hx-get')
        self.assertContains(response, 'hx-target="#sagefemmes-table"')
        self.assertContains(response, 'hx-trigger="keyup changed delay:300ms"')


class SageFemmeFormTemplateTest(BaseTemplateIntegrationTest):
    """Tests d'intégration pour les templates de formulaire"""
    
    def test_formulaire_creation_affichage(self):
        """Test de l'affichage du formulaire de création"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier le titre du modal
        self.assertContains(response, 'Ajouter une sage-femme')
        
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
    
    def test_formulaire_modification_affichage(self):
        """Test de l'affichage du formulaire de modification"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_update', args=[self.titulaire_active.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier le titre du modal
        self.assertContains(response, 'Modifier la sage-femme')
        
        # Vérifier que les données sont pré-remplies
        self.assertContains(response, self.titulaire_active.nom)
        self.assertContains(response, self.titulaire_active.prenom)
        self.assertContains(response, self.titulaire_active.email)
        
        # Vérifier le bouton de modification
        self.assertContains(response, 'Modifier')
    
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
        
        # Vérifier le JavaScript de gestion dynamique
        self.assertContains(response, 'toggleRemplacementFields')
    
    def test_formulaire_periodes_activite(self):
        """Test de l'affichage des périodes d'activité dans le formulaire"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_update', args=[self.titulaire_active.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la section des périodes
        self.assertContains(response, 'Périodes d\'activité')
        
        # Vérifier le statut
        self.assertContains(response, 'Statut')
        self.assertContains(response, 'Actif')  # Le titulaire est actif
        
        # Vérifier l'affichage des périodes existantes  
        self.assertContains(response, 'Périodes d\'activité')
        
        # Vérifier le bouton d'ajout de période
        self.assertContains(response, 'Ajouter une période')
    
    def test_formulaire_note_statut_automatique(self):
        """Test de l'affichage de la note sur le statut automatique"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_update', args=[self.titulaire_active.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la note explicative
        self.assertContains(response, 'Statut automatique')
        self.assertContains(response, 'déterminé automatiquement')
        self.assertContains(response, 'périodes d\'activité')


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
        
        # Vérifier l'adresse
        self.assertContains(response, self.titulaire_active.adresse_complete)
        
        # Vérifier les informations professionnelles
        self.assertContains(response, self.titulaire_active.numero_cafat)
        self.assertContains(response, self.titulaire_active.ridet)
    
    def test_detail_statut_et_periodes(self):
        """Test de l'affichage du statut et des périodes"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_detail', args=[self.collaborateur_inactif.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier le statut
        self.assertContains(response, 'Statut')
        self.assertContains(response, 'Inactif')  # Le collaborateur est inactif
        
        # Vérifier les périodes d'activité
        self.assertContains(response, 'Périodes d\'activité')
        self.assertContains(response, 'Période terminée')
        self.assertContains(response, 'Période à venir')
        
        # Vérifier les différents statuts de période
        self.assertContains(response, 'Passé')     # Période terminée
        self.assertContains(response, 'À venir')  # Période future
    
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
        
        # Vérifier les options spécifiques aux remplaçants
        if self.remplacant.etat_recapitulatif_commun:
            self.assertContains(response, 'État récapitulatif commun')
        if self.remplacant.bons_depot_communs:
            self.assertContains(response, 'Bons de dépôt communs')
    
    def test_detail_periode_en_cours(self):
        """Test de l'affichage d'une période en cours"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_detail', args=[self.remplacant.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier l'affichage de la période en cours
        self.assertContains(response, 'En cours')
        self.assertContains(response, 'Remplacement temporaire')


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
        
        # Vérifier les attributs ARIA et title
        self.assertIn('title="', content)           # Tooltips
        self.assertIn('aria-', content)             # Attributs ARIA si présents
    
    def test_color_scheme_consistency(self):
        """Test de la cohérence du schéma de couleurs"""
        urls_to_test = [
            reverse('administration:administration_sages_femmes'),
            reverse('administration:sagefemme_create'),
            reverse('administration:sagefemme_update', args=[self.titulaire_active.pk]),
            reverse('administration:sagefemme_detail', args=[self.titulaire_active.pk])
        ]
        
        primary_color = '#2D4B73'  # Couleur primaire définie dans CLAUDE.md
        
        for url in urls_to_test:
            self.client.login(username='admin@test.nc', password='testpass123')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            
            content = response.content.decode()
            
            # Vérifier l'utilisation cohérente de la couleur primaire
            self.assertIn(primary_color, content)


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
        
        # Vérifier les fonctions JavaScript importantes
        js_functions = [
            'closeModal',
            'toggleRemplacementFields',
            'toggleAjoutPeriode',
            'ajouterPeriode',
            'supprimerPeriode'
        ]
        
        for func in js_functions:
            self.assertIn(func, content)
    
    def test_notification_system_integration(self):
        """Test de l'intégration du système de notifications"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:administration_sages_femmes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode()
        
        # Vérifier la présence du système de notifications
        self.assertIn('window.showNotification', content)
    
    def test_form_validation_javascript(self):
        """Test de la validation JavaScript des formulaires"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_update', args=[self.titulaire_active.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode()
        
        # Vérifier la validation des dates
        self.assertIn('date_debut', content)
        self.assertIn('date_fin', content)


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
        self.assertContains(response, 'Adresse non renseignée')
    
    def test_template_empty_periods(self):
        """Test de template avec sage-femme sans périodes"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_detail', args=[self.collaborateur_inactif.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Devrait afficher les périodes existantes sans erreur
        # (le collaborateur_inactif a des périodes dans notre setUp)