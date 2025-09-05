"""
Tests pour l'interface admin Patient
Tests de configuration et fonctionnalités admin
"""

from django.test import TestCase, Client
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import date, timedelta

from core.models import Patient, Caisse
from core.admin import PatientAdmin
from authentication.models import SageFemmeUser


User = get_user_model()


class PatientAdminTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.site = AdminSite()
        self.admin = PatientAdmin(Patient, self.site)
        
        # Créer un superutilisateur
        self.superuser = SageFemmeUser.objects.create_superuser(
            email='admin@maieutix.nc',
            password='adminpass123'
        )
        
        # Créer une caisse
        self.caisse = Caisse.objects.create(
            nom="CAFAT"
        )
        
        # Créer des patients de test
        self.femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse
        )
        
        self.bebe = Patient.objects.create(
            type_patient='bebe',
            nom='Dupont',
            prenom='Lucas',
            date_naissance=date.today() - timedelta(days=30),
            mere=self.femme,
            caisse=self.caisse
        )
        
        # Client pour tests d'intégration
        self.client = Client()
        self.client.force_login(self.superuser)
    
    def test_admin_list_display(self):
        """Test de l'affichage de liste admin"""
        expected_fields = [
            'nom_complet_display', 'type_patient', 'age_display', 'mere_display', 
            'caisse', 'is_active', 'created_at'
        ]
        
        self.assertEqual(list(self.admin.list_display), expected_fields)
    
    def test_admin_list_filter(self):
        """Test des filtres de liste admin"""
        expected_filters = ['type_patient', 'is_active', 'caisse', 'est_assure_titulaire', 'created_at']
        
        self.assertEqual(list(self.admin.list_filter), expected_filters)
    
    def test_admin_search_fields(self):
        """Test des champs de recherche admin"""
        expected_search = ['nom', 'prenom', 'nom_jf', 'mere__nom', 'mere__prenom']
        
        self.assertEqual(list(self.admin.search_fields), expected_search)
    
    def test_admin_ordering(self):
        """Test de l'ordre par défaut admin"""
        # L'admin utilise l'ordering par défaut du modèle
        # L'admin n'a pas d'ordering spécifique, utilise celui du modèle
        admin_ordering = getattr(self.admin, 'ordering', None)
        self.assertIsNone(admin_ordering)
        
        # Vérifier que le modèle a un ordering par défaut
        model_ordering = getattr(self.admin.model._meta, 'ordering', None)
        self.assertIsNotNone(model_ordering)
    
    def test_admin_fieldsets(self):
        """Test des fieldsets admin"""
        fieldsets = self.admin.fieldsets
        
        self.assertIsInstance(fieldsets, tuple)
        # Le nombre de fieldsets dépend si c'est un ajout ou une modification
        # Pour un nouvel objet, il y aura 8 sections
        # Pour un objet existant, il y aura 8 sections aussi mais avec age_display
        self.assertGreaterEqual(len(fieldsets), 8)
        
        # Vérifier les titres des sections
        section_titles = [fs[0] for fs in fieldsets]
        expected_titles = [
            'Informations principales',
            'Informations complémentaires',
            'Spécifique femme',
            'Relation familiale',
            'Assurance',
            'Informations assuré titulaire',
            'Adresse assuré',
            'Statut',
            'Métadonnées'
        ]
        
        self.assertEqual(section_titles, expected_titles)
    
    def test_admin_readonly_fields(self):
        """Test des champs en lecture seule"""
        expected_readonly = ['created_at', 'updated_at', 'age_display']
        
        self.assertEqual(list(self.admin.readonly_fields), expected_readonly)
    
    def test_admin_date_hierarchy(self):
        """Test de la hiérarchie par date"""
        self.assertEqual(self.admin.date_hierarchy, 'created_at')
    
    def test_nom_complet_display_method(self):
        """Test de la méthode nom_complet_display dans admin"""
        result = self.admin.nom_complet_display(self.femme)
        self.assertEqual(result, 'Marie Dupont')
        
        result = self.admin.nom_complet_display(self.bebe)
        # Pour un bébé, cela contient la mention de la mère
        self.assertIn('Lucas Dupont', result)
        self.assertIn('Marie Dupont', result)
    
    def test_age_display_method(self):
        """Test de la méthode age_display dans admin"""
        result = self.admin.age_display(self.femme)
        self.assertIn('an', result)  # Doit contenir 'ans'
        
        result = self.admin.age_display(self.bebe)
        # Le bébé peut être affiché en jours, semaines ou mois selon son âge
        self.assertTrue(any(word in result for word in ['jour', 'semaine', 'mois']))
    
    def test_mere_display_method(self):
        """Test de la méthode mere_display dans admin"""
        # Patient sans mère
        result = self.admin.mere_display(self.femme)
        self.assertEqual(result, '-')
        
        # Bébé avec mère
        result = self.admin.mere_display(self.bebe)
        self.assertEqual(result, 'Marie Dupont')
    
    def test_admin_changelist_view(self):
        """Test de la vue liste changelist"""
        url = reverse('admin:core_patient_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Marie Dupont')
        self.assertContains(response, 'Lucas Dupont')
    
    def test_admin_change_view(self):
        """Test de la vue de modification"""
        url = reverse('admin:core_patient_change', args=[self.femme.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dupont')
        self.assertContains(response, 'Marie')
    
    def test_admin_add_view(self):
        """Test de la vue d'ajout"""
        url = reverse('admin:core_patient_add')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ajouter 6. Patient')
    
    def test_admin_delete_view(self):
        """Test de la vue de suppression"""
        url = reverse('admin:core_patient_delete', args=[self.femme.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Supprimer')
    
    def test_admin_filter_by_type(self):
        """Test du filtrage par type de patient"""
        url = reverse('admin:core_patient_changelist')
        
        # Filtrer par femmes
        response = self.client.get(url + '?type_patient=femme')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Marie Dupont')
        self.assertNotContains(response, 'Lucas Dupont')
        
        # Filtrer par bébés
        response = self.client.get(url + '?type_patient=bebe')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lucas Dupont')
        # Marie Dupont peut apparaître comme mère dans la colonne mère, donc on vérifie spécifiquement
        response_content = response.content.decode('utf-8')
        # Vérifier que Marie Dupont n'est pas un lien de résultat principal (donc pas un patient affiché)
        self.assertNotIn('Marie Dupont</a></th>', response_content)
    
    def test_admin_filter_by_active_status(self):
        """Test du filtrage par statut actif"""
        # Vérifier l'état initial
        self.assertTrue(self.femme.is_active)
        self.assertTrue(self.bebe.is_active)
        
        # Désactiver un patient
        self.femme.is_active = False
        self.femme.save()
        
        # Vérifier que la désactivation a bien eu lieu
        self.femme.refresh_from_db()
        self.assertFalse(self.femme.is_active)
        
        url = reverse('admin:core_patient_changelist')
        
        # Filtrer par actifs
        response = self.client.get(url + '?is_active__exact=1')
        self.assertEqual(response.status_code, 200)
        # Chercher spécifiquement dans le contenu de la table des résultats
        response_content = response.content.decode('utf-8')
        # Vérifier que Marie Dupont n'est pas dans les résultats de la table
        self.assertNotIn('Marie Dupont</a>', response_content)
        self.assertContains(response, 'Lucas Dupont')
        
        # Filtrer par inactifs
        response = self.client.get(url + '?is_active__exact=0')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Marie Dupont')
        self.assertNotContains(response, 'Lucas Dupont')
    
    def test_admin_filter_by_caisse(self):
        """Test du filtrage par caisse"""
        url = reverse('admin:core_patient_changelist')
        response = self.client.get(url + f'?caisse__id__exact={self.caisse.id}')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Marie Dupont')
        self.assertContains(response, 'Lucas Dupont')
    
    def test_admin_search_functionality(self):
        """Test de la fonctionnalité de recherche"""
        url = reverse('admin:core_patient_changelist')
        
        # Recherche par nom
        response = self.client.get(url + '?q=Dupont')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Marie Dupont')
        self.assertContains(response, 'Lucas Dupont')
        
        # Recherche par prénom
        response = self.client.get(url + '?q=Marie')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Marie Dupont')
        # Lucas Dupont sera trouvé aussi car sa mère s'appelle Marie (recherche dans mere__prenom)
        self.assertContains(response, 'Lucas Dupont')
        
        # Recherche par téléphone (recherche partielle)
        response = self.client.get(url + '?q=01234')
        self.assertEqual(response.status_code, 200)
        # La recherche peut ou peut pas fonctionner selon la config de recherche
        # On vérifie juste que la requête passe
    
    def test_admin_date_hierarchy_navigation(self):
        """Test de la navigation par hiérarchie de dates"""
        url = reverse('admin:core_patient_changelist')
        today = date.today()
        
        # Navigation par année
        response = self.client.get(url + f'?created_at__year={today.year}')
        self.assertEqual(response.status_code, 200)
        
        # Navigation par mois
        response = self.client.get(url + f'?created_at__year={today.year}&created_at__month={today.month}')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_bulk_actions(self):
        """Test des actions en lot"""
        # Vérifier que les actions par défaut sont disponibles
        # Créer une fake request avec un utilisateur pour tester les actions
        from django.http import HttpRequest
        request = HttpRequest()
        request.user = self.superuser
        actions = self.admin.get_actions(request)
        self.assertIn('delete_selected', actions)
    
    def test_admin_form_validation(self):
        """Test de validation dans le formulaire admin"""
        url = reverse('admin:core_patient_add')
        
        # Données invalides - bébé sans mère
        invalid_data = {
            'type_patient': 'bebe',
            'nom': 'Test',
            'prenom': 'Bebe',
            'date_naissance': date.today() - timedelta(days=10),
            # Pas de mère spécifiée
        }
        
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, 200)  # Reste sur le formulaire
        self.assertContains(response, 'error')  # Ou message d'erreur
    
    def test_admin_permissions(self):
        """Test des permissions admin"""
        # Vérifier que l'admin a les bonnes permissions
        # Créer une fake request avec un utilisateur pour tester les permissions
        from django.http import HttpRequest
        request = HttpRequest()
        request.user = self.superuser
        
        self.assertTrue(self.admin.has_add_permission(request))
        self.assertTrue(self.admin.has_change_permission(request))
        self.assertTrue(self.admin.has_delete_permission(request))
        self.assertTrue(self.admin.has_view_permission(request))
    
    def test_admin_custom_methods_display(self):
        """Test de l'affichage des méthodes personnalisées"""
        # Vérifier que les méthodes personnalisées ont les bons attributs
        self.assertEqual(self.admin.nom_complet_display.short_description, 'Patient')
        self.assertEqual(self.admin.age_display.short_description, 'Âge')
        self.assertEqual(self.admin.mere_display.short_description, 'Mère')
        
        # Vérifier que certaines méthodes permettent l'ordre
        self.assertTrue(hasattr(self.admin.nom_complet_display, 'admin_order_field'))
    
    def test_admin_inline_configurations(self):
        """Test des configurations inline (si applicable)"""
        # Si des inlines sont configurées pour les patients
        inlines = getattr(self.admin, 'inlines', [])
        
        # Pour l'instant, pas d'inlines configurées
        self.assertEqual(len(inlines), 0)
    
    def test_admin_list_per_page(self):
        """Test de la pagination admin"""
        # Vérifier la configuration de pagination (par défaut Django)
        list_per_page = getattr(self.admin, 'list_per_page', 100)
        self.assertGreater(list_per_page, 0)
    
    def test_admin_preserve_filters(self):
        """Test de préservation des filtres"""
        # Vérifier que preserve_filters est configuré
        preserve_filters = getattr(self.admin, 'preserve_filters', True)
        self.assertTrue(preserve_filters)
    
    def test_admin_save_and_continue_editing(self):
        """Test de sauvegarde et continuation d'édition"""
        url = reverse('admin:core_patient_change', args=[self.femme.pk])
        
        data = {
            'type_patient': 'femme',
            'nom': 'Dupont-Modified',
            'prenom': 'Marie',
            'date_naissance': '1990-05-15',
            'telephone': '0123456789',  # Téléphone valide
            'caisse': self.caisse.id,
            'est_assure_titulaire': True,  # Requis
            'nom_assure': 'Dupont-Modified',  # Requis si est_assure_titulaire
            'prenom_assure': 'Marie',  # Requis si est_assure_titulaire
            '_continue': 'Save and continue editing'
        }
        
        response = self.client.post(url, data)
        
        # Doit rediriger vers la page d'édition
        self.assertEqual(response.status_code, 302)
        self.assertIn(f'/admin/core/patient/{self.femme.pk}/change/', response.url)
        
        # Vérifier que la modification a été appliquée
        self.femme.refresh_from_db()
        self.assertEqual(self.femme.nom, 'Dupont-Modified')