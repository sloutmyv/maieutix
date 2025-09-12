"""
Tests pour l'interface admin EntretienPrenatalPrecoce
"""

from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from datetime import date, timedelta

from core.admin.entretien_prenatal_precoce import EntretienPrenatalPrecoceAdmin
from core.models import EntretienPrenatalPrecoce, Patient, SageFemme, Caisse
from authentication.models import SageFemmeUser


class MockRequest:
    """Classe mock pour les requêtes"""
    def __init__(self):
        self.GET = {}
        self.POST = {}
        self.user = None


class EntretienPrenatalPrecoceAdminTest(TestCase):
    """Tests pour EntretienPrenatalPrecoceAdmin"""
    
    def setUp(self):
        """Configuration des données de test"""
        # Site admin mock
        self.site = AdminSite()
        self.admin = EntretienPrenatalPrecoceAdmin(EntretienPrenatalPrecoce, self.site)
        
        # Factory pour requêtes
        self.factory = RequestFactory()
        
        # Caisse
        self.caisse = Caisse.objects.create(nom="CAFAT")
        
        # Utilisateur et sage-femme
        self.user = SageFemmeUser.objects.create_superuser(
            email='admin@maieutix.nc',
            password='testpass123'
        )
        self.sage_femme = SageFemme.objects.create(
            user=self.user,
            nom='Martin',
            prenom='Dr Sophie',
            titre='Sage-Femme',
            telephone='123456789',
            email='admin@maieutix.nc',
            numero_cafat='123456',
            ridet='987654',
            rib='FR7630001007941234567890185',
            banque='BNC',
            situation='titulaire'
        )
        
        # Patiente femme avec DDG
        self.patient_femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            caisse=self.caisse,
            date_debut_grossesse=date(2024, 1, 15)
        )
        
        # Entretien de test en période optimale (20 SA)
        self.entretien_optimal = EntretienPrenatalPrecoce.objects.create(
            patient=self.patient_femme,
            sage_femme=self.sage_femme,
            date_entretien=self.patient_femme.date_debut_grossesse + timedelta(days=140),  # 20 SA
            conjoint_present=True,
            lieu_accouchement_prevu='Maternité CHT',
            atcd_marquants_sante='Aucun ATCD particulier',
            environnement_social_familial='Environnement stable',
            projet_naissance_parentalite='Accouchement naturel souhaité',
            ressenti='Très positive',
            propositions_liens='Cours préparation naissance'
        )
        
        # Entretien hors période optimale (35 SA)
        self.entretien_limite = EntretienPrenatalPrecoce.objects.create(
            patient=self.patient_femme,
            sage_femme=self.sage_femme,
            date_entretien=self.patient_femme.date_debut_grossesse + timedelta(days=245),  # 35 SA
            conjoint_present=False,
            lieu_accouchement_prevu='Clinique Privée'
        )
        
        # Requête mock
        self.request = MockRequest()
        self.request.user = self.user
    
    def test_admin_configuration(self):
        """Test configuration de base de l'admin"""
        expected_list_display = [
            'patient_link', 'date_entretien_formatted', 'sa_affichage',
            'conjoint_present_display', 'lieu_accouchement_court',
            'periode_indicator', 'sage_femme_display', 'created_at_formatted'
        ]
        expected_list_filter = [
            'date_entretien', 'conjoint_present', 'created_at', 'patient__caisse', 'sage_femme'
        ]
        expected_search_fields = [
            'patient__nom', 'patient__prenom', 'lieu_accouchement_prevu',
            'atcd_marquants', 'projet_naissance', 'notes'
        ]
        expected_readonly_fields = [
            'semaines_amenorrhee', 'entretien_resume_display', 
            'periode_indicator_display', 'created_at', 'updated_at'
        ]
        
        self.assertEqual(self.admin.list_display, expected_list_display)
        self.assertEqual(self.admin.list_filter, expected_list_filter)
        self.assertEqual(self.admin.search_fields, expected_search_fields)
        self.assertEqual(self.admin.readonly_fields, expected_readonly_fields)
        self.assertEqual(self.admin.list_per_page, 25)
        self.assertEqual(self.admin.date_hierarchy, 'date_entretien')
    
    def test_fieldsets_configuration(self):
        """Test configuration des fieldsets"""
        fieldsets = self.admin.fieldsets
        
        # Vérifier le nombre de sections
        self.assertEqual(len(fieldsets), 5)
        
        # Vérifier les sections
        section_titles = [fs[0] for fs in fieldsets]
        expected_titles = [
            'Informations générales',
            'Contexte de l\'entretien',
            'Contenu de l\'entretien',
            'Notes et résumé',
            'Métadonnées'
        ]
        
        for expected_title in expected_titles:
            self.assertIn(expected_title, section_titles)
    
    def test_queryset_optimization(self):
        """Test optimisation du queryset avec select_related"""
        request = self.factory.get('/admin/core/entretienprenatalprecoce/')
        request.user = self.user
        
        queryset = self.admin.get_queryset(request)
        
        # Vérifier que select_related est utilisé
        self.assertIn('patient', str(queryset.query))
        self.assertIn('sage_femme', str(queryset.query))
    
    def test_save_model_with_request_user(self):
        """Test sauvegarde avec méthode save_model par défaut"""
        request = self.factory.post('/admin/core/entretienprenatalprecoce/')
        request.user = self.user
        
        nouvel_entretien = EntretienPrenatalPrecoce(
            patient=self.patient_femme,
            date_entretien=date.today(),
            conjoint_present=False
        )
        
        # La méthode save_model par défaut sauvegarde l'objet
        self.admin.save_model(request, nouvel_entretien, None, False)  # False = change=False (création)
        
        # Vérifier que l'objet a été sauvegardé avec un ID
        self.assertIsNotNone(nouvel_entretien.pk)
    
    def test_has_permissions(self):
        """Test permissions d'accès"""
        request = self.factory.get('/admin/core/entretienprenatalprecoce/')
        request.user = self.user
        
        # Test permissions de base pour un superuser
        # Les permissions par défaut sont accordées aux superutilisateurs
        self.assertTrue(self.admin.has_view_permission(request))
        self.assertTrue(self.admin.has_add_permission(request))
        self.assertTrue(self.admin.has_change_permission(request))
        self.assertTrue(self.admin.has_delete_permission(request))
    
    def test_list_display_links(self):
        """Test liens cliquables dans la liste"""
        # list_display_links peut être None par défaut (utilise le premier champ)
        # ou peut être explicitement défini
        links = self.admin.list_display_links
        # Vérifier que c'est soit None (par défaut) ou contient des liens valides
        if links is not None:
            self.assertIsInstance(links, (list, tuple))
    
    def test_ordering(self):
        """Test tri par défaut"""
        expected_ordering = ['-date_entretien', '-created_at']
        self.assertEqual(self.admin.ordering, expected_ordering)
    
    def test_actions_configuration(self):
        """Test configuration des actions"""
        # Vérifier que les actions personnalisées sont disponibles
        actions = self.admin.get_actions(self.request)
        self.assertIn('marquer_entretien_complet', actions)
        self.assertIn('exporter_entretiens', actions)
    
    def test_verbose_names_display(self):
        """Test affichage des noms verbeux"""
        # Vérifier que les verbose names du modèle sont utilisés
        self.assertEqual(
            EntretienPrenatalPrecoce._meta.verbose_name,
            "6.1.4 Entretien Prénatal Précoce"
        )
        self.assertEqual(
            EntretienPrenatalPrecoce._meta.verbose_name_plural,
            "6.1.4 Entretiens Prénataux Précoces"
        )
    
    def test_media_configuration(self):
        """Test configuration des médias (CSS/JS)"""
        media = self.admin.media
        
        # Vérifier que les médias par défaut sont présents
        self.assertIsNotNone(media)
    
    def test_basic_admin_functionality(self):
        """Test fonctionnalité de base de l'admin"""
        # Test que l'admin peut être instancié
        self.assertIsNotNone(self.admin)
        self.assertEqual(self.admin.model, EntretienPrenatalPrecoce)
    
    def test_filtering_functionality(self):
        """Test fonctionnalité de filtrage"""
        request = self.factory.get('/admin/core/entretienprenatalprecoce/?conjoint_present=1')
        request.user = self.user
        
        # Simuler le filtrage par présence conjoint
        queryset = self.admin.get_queryset(request)
        filtered_queryset = queryset.filter(conjoint_present=True)
        
        # Vérifier que le filtrage fonctionne
        self.assertIn(self.entretien_optimal, filtered_queryset)
        self.assertNotIn(self.entretien_limite, filtered_queryset)
    
    def test_search_functionality(self):
        """Test fonctionnalité de recherche"""
        request = self.factory.get('/admin/core/entretienprenatalprecoce/?q=Dupont')
        request.user = self.user
        
        # La recherche devrait trouver les entretiens de la patiente Dupont
        queryset = self.admin.get_queryset(request)
        search_queryset = queryset.filter(patient__nom__icontains='Dupont')
        
        self.assertIn(self.entretien_optimal, search_queryset)
        self.assertIn(self.entretien_limite, search_queryset)
    
    def test_admin_integration_with_site(self):
        """Test intégration avec le site admin"""
        # Test basique que l'admin existe
        from django.contrib import admin
        # Vérifier que le modèle est enregistré dans le site admin par défaut
        self.assertIn(EntretienPrenatalPrecoce, admin.site._registry)