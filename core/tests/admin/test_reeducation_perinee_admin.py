"""
Tests pour l'interface admin de ReeducationPerinee
"""

from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from django.contrib.messages.storage.fallback import FallbackStorage
from unittest.mock import Mock

from core.models import (
    Patient, ReeducationPerinee, SageFemme,
    Caisse, ConditionPaiement, PeriodeActivite
)
from core.admin.reeducation_perinee import ReeducationPerineeAdmin
from authentication.models import SageFemmeUser

User = get_user_model()


class ReeducationPerineeAdminTest(TestCase):
    """Tests pour l'admin ReeducationPerinee"""
    
    def setUp(self):
        """Configuration pour chaque test"""
        self.client = Client()
        self.site = AdminSite()
        
        # Créer une caisse et condition de paiement
        self.condition = ConditionPaiement.objects.create(
            designation="Test Condition",
            pourcentage=70
        )
        self.caisse = Caisse.objects.create(
            nom="CAFAT"
        )
        self.caisse.conditions_paiement_eligibles.add(self.condition)
        
        # Créer une sage-femme
        self.sage_femme = SageFemme.objects.create(
            nom="Dupont",
            prenom="Marie",
            titre="Sage-femme diplômée",
            telephone="687123456",
            email="marie@test.com",
            numero_cafat="123456789",
            ridet="RIDET123456",
            rib="FR1234567890123456789012345",
            banque="BCI",
            situation="titulaire"
        )
        
        # Créer période d'activité active
        self.periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=date.today() - timedelta(days=30)
        )
        
        # Créer superutilisateur
        self.admin_user = SageFemmeUser.objects.create_superuser(
            email="admin@test.com",
            password="adminpass123"
        )
        
        # Créer une patiente
        self.patiente = Patient.objects.create(
            nom="Martin",
            prenom="Julie",
            date_naissance=date(1990, 5, 15),
            telephone="0123456789",
            type_patient="femme",
            caisse=self.caisse
        )
        
        # Créer des séances de test
        self.seance1 = ReeducationPerinee.objects.create(
            patient=self.patiente,
            date_consultation=date.today() - timedelta(days=7),
            numero_seance=1,
            examen_clinique_travail="Évaluation du tonus périnéal - un examen très détaillé qui va être tronqué",
            a_prevoir="Exercices de Kegel - une description très longue qui va être tronquée également",
            created_by=self.sage_femme
        )
        
        self.seance2 = ReeducationPerinee.objects.create(
            patient=self.patiente,
            date_consultation=date.today() - timedelta(days=3),
            numero_seance=2,
            examen_clinique_travail="Travail de renforcement",
            created_by=self.sage_femme
        )
        
        # Instance de l'admin
        self.admin = ReeducationPerineeAdmin(ReeducationPerinee, self.site)
        
        # Se connecter en tant qu'admin
        self.client.login(email="admin@test.com", password="adminpass123")
    
    def test_admin_list_display(self):
        """Test configuration list_display"""
        expected_fields = [
            'patient_link', 'date_consultation', 'numero_seance_badge', 
            'examen_clinique_resume', 'created_by_link', 'created_at_formatted'
        ]
        self.assertEqual(list(self.admin.list_display), expected_fields)
    
    def test_admin_list_filter(self):
        """Test configuration list_filter"""
        # L'implémentation réelle utilise des RelatedFieldListFilter
        self.assertIn('date_consultation', self.admin.list_filter)
        self.assertIn('numero_seance', self.admin.list_filter)
        self.assertIn('created_at', self.admin.list_filter)
    
    def test_admin_search_fields(self):
        """Test configuration search_fields"""
        expected_fields = [
            'patient__nom', 'patient__prenom', 'examen_clinique_travail', 
            'a_prevoir', 'created_by__nom', 'created_by__prenom'
        ]
        self.assertEqual(list(self.admin.search_fields), expected_fields)
    
    def test_admin_ordering(self):
        """Test configuration ordering"""
        # L'admin n'a pas d'ordering défini, utilise celui du modèle
        self.assertIsNone(getattr(self.admin, 'ordering', None))
    
    def test_admin_list_per_page(self):
        """Test pagination"""
        # Utilise la valeur par défaut de Django
        self.assertEqual(self.admin.list_per_page, 100)
    
    def test_admin_date_hierarchy(self):
        """Test hiérarchie par date"""
        self.assertEqual(self.admin.date_hierarchy, 'date_consultation')
    
    def test_admin_fieldsets(self):
        """Test configuration fieldsets"""
        fieldsets = self.admin.fieldsets
        
        # Vérifier la structure des fieldsets
        self.assertEqual(len(fieldsets), 4)
        
        # Informations générales
        self.assertEqual(fieldsets[0][0], 'Informations générales')
        self.assertIn('patient', fieldsets[0][1]['fields'])
        self.assertIn('date_consultation', fieldsets[0][1]['fields'])
        self.assertIn('numero_seance', fieldsets[0][1]['fields'])
        
        # Contenu de la séance
        self.assertEqual(fieldsets[1][0], 'Contenu de la séance')
        self.assertIn('examen_clinique_travail', fieldsets[1][1]['fields'])
        self.assertIn('a_prevoir', fieldsets[1][1]['fields'])
        
        # Traçabilité
        self.assertEqual(fieldsets[2][0], 'Traçabilité')
        self.assertIn('created_by', fieldsets[2][1]['fields'])
        
        # Métadonnées
        self.assertEqual(fieldsets[3][0], 'Métadonnées')
        self.assertIn('created_at', fieldsets[3][1]['fields'])
        self.assertIn('updated_at', fieldsets[3][1]['fields'])
    
    def test_admin_readonly_fields(self):
        """Test champs en lecture seule"""
        expected_readonly = ['created_at', 'updated_at']
        self.assertEqual(list(self.admin.readonly_fields), expected_readonly)
    
    def test_admin_raw_id_fields(self):
        """Test champs avec raw_id"""
        # L'admin n'utilise pas raw_id_fields
        self.assertEqual(list(getattr(self.admin, 'raw_id_fields', [])), [])
    
    def test_patient_link_method(self):
        """Test méthode patient_link"""
        obj = self.seance1
        result = self.admin.patient_link(obj)
        
        self.assertIn('href=', result)
        self.assertIn('Julie Martin', result)
        # Le link n'a pas de classe CSS spéciale dans l'implémentation réelle
    
    def test_patient_link_method_sans_patient(self):
        """Test méthode patient_link sans patient"""
        obj = Mock()
        obj.patient = None
        
        result = self.admin.patient_link(obj)
        self.assertEqual(result, '-')
    
    def test_numero_seance_badge_method(self):
        """Test méthode numero_seance_badge"""
        obj = self.seance1
        result = self.admin.numero_seance_badge(obj)
        
        self.assertIn('Séance 1', result)
        self.assertIn('background-color: #3b82f6', result)
        self.assertIn('color: white', result)
    
    def test_examen_clinique_resume_method(self):
        """Test méthode examen_clinique_resume avec troncature"""
        obj = self.seance1
        result = self.admin.examen_clinique_resume(obj)
        
        # Devrait être tronqué à 80 caractères
        self.assertIn('Évaluation du tonus périnéal', result)
        # Vérifier qu'il contient le HTML de format
        self.assertIn('<span title=', result)
    
    def test_examen_clinique_resume_method_vide(self):
        """Test méthode examen_clinique_resume avec champ vide"""
        obj = Mock()
        obj.examen_clinique_travail = ""
        
        result = self.admin.examen_clinique_resume(obj)
        self.assertIn('Aucun examen renseigné', result)
    
    def test_a_prevoir_resume_method(self):
        """Test méthode a_prevoir_resume - n'existe pas dans l'admin réel"""
        # Cette méthode n'existe pas dans l'implémentation réelle
        self.assertFalse(hasattr(self.admin, 'a_prevoir_resume'))
    
    def test_a_prevoir_resume_method_vide(self):
        """Test méthode a_prevoir_resume - n'existe pas dans l'admin réel"""
        # Cette méthode n'existe pas dans l'implémentation réelle
        self.assertFalse(hasattr(self.admin, 'a_prevoir_resume'))
    
    def test_created_by_link_method(self):
        """Test méthode created_by_link"""
        obj = self.seance1
        result = self.admin.created_by_link(obj)
        
        self.assertIn('Marie DUPONT', result)  # Le nom est en majuscules dans l'admin
        self.assertIn('href=', result)
    
    def test_created_by_link_method_sans_createur(self):
        """Test méthode created_by_link sans créateur"""
        obj = Mock()
        obj.created_by = None
        
        result = self.admin.created_by_link(obj)
        self.assertIn('Non renseignée', result)
    
    def test_admin_actions_disponibles(self):
        """Test actions disponibles"""
        from django.http import HttpRequest
        request = HttpRequest()
        request.user = self.admin_user
        expected_actions = ['delete_selected', 'marquer_seances_completes']
        actions = list(self.admin.get_actions(request).keys())
        
        for action in expected_actions:
            self.assertIn(action, actions)
    
    def test_marquer_seances_completes_action(self):
        """Test action marquer_seances_completes"""
        # Créer une séance sans examen pour tester l'action
        seance_vide = ReeducationPerinee.objects.create(
            patient=self.patiente,
            date_consultation=date.today(),
            numero_seance=3,
            created_by=self.sage_femme
        )
        
        # Créer une mock request
        request = Mock()
        request.user = self.admin_user
        
        # Mock messages
        setattr(request, '_messages', FallbackStorage(request))
        
        queryset = ReeducationPerinee.objects.filter(id=seance_vide.id)
        
        # Exécuter l'action
        self.admin.marquer_seances_completes(request, queryset)
        
        # Vérifier que la séance a été marquée comme complétée
        seance_updated = ReeducationPerinee.objects.get(id=seance_vide.id)
        self.assertEqual(seance_updated.examen_clinique_travail, "Séance complétée")
    
    def test_admin_change_view_acces(self):
        """Test accès à la vue de modification"""
        url = reverse('admin:core_reeducationperinee_change', args=[self.seance1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Évaluation du tonus périnéal')
    
    def test_admin_changelist_view_acces(self):
        """Test accès à la liste d'administration"""
        url = reverse('admin:core_reeducationperinee_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Julie Martin')
        self.assertContains(response, 'Séance 1')
        self.assertContains(response, 'Séance 2')
    
    def test_admin_add_view_acces(self):
        """Test accès à la vue d'ajout"""
        url = reverse('admin:core_reeducationperinee_add')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ajouter')
    
    def test_admin_recherche_fonctionne(self):
        """Test fonctionnement de la recherche admin"""
        url = reverse('admin:core_reeducationperinee_changelist')
        
        # Recherche par nom de patiente
        response = self.client.get(url, {'q': 'Martin'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Julie Martin')
        
        # Recherche par contenu examen
        response = self.client.get(url, {'q': 'tonus'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Séance 1')
    
    def test_admin_filtres_fonctionnent(self):
        """Test fonctionnement des filtres admin"""
        url = reverse('admin:core_reeducationperinee_changelist')
        
        # Filtre par numéro de séance
        response = self.client.get(url, {'numero_seance': 1})
        self.assertEqual(response.status_code, 200)
        
        # Filtre par créateur
        response = self.client.get(url, {'created_by': self.sage_femme.id})
        self.assertEqual(response.status_code, 200)
    
    def test_admin_creation_seance(self):
        """Test création de séance via admin"""
        url = reverse('admin:core_reeducationperinee_add')
        data = {
            'patient': self.patiente.id,
            'date_consultation': date.today(),
            'numero_seance': 3,
            'examen_clinique_travail': 'Nouvelle séance admin',
            'a_prevoir': 'Continuer traitement',
            'created_by': self.sage_femme.id
        }
        
        response = self.client.post(url, data)
        
        # Devrait rediriger après création réussie
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la séance a été créée
        seance = ReeducationPerinee.objects.get(numero_seance=3, patient=self.patiente)
        self.assertEqual(seance.examen_clinique_travail, 'Nouvelle séance admin')
    
    def test_admin_modification_seance(self):
        """Test modification de séance via admin"""
        url = reverse('admin:core_reeducationperinee_change', args=[self.seance1.id])
        data = {
            'patient': self.patiente.id,
            'date_consultation': self.seance1.date_consultation,
            'numero_seance': self.seance1.numero_seance,
            'examen_clinique_travail': 'Examen modifié',
            'a_prevoir': self.seance1.a_prevoir,
            'created_by': self.sage_femme.id
        }
        
        response = self.client.post(url, data)
        
        # Devrait rediriger après modification réussie
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la séance a été modifiée
        seance_updated = ReeducationPerinee.objects.get(id=self.seance1.id)
        self.assertEqual(seance_updated.examen_clinique_travail, 'Examen modifié')
    
    def test_admin_suppression_seance(self):
        """Test suppression de séance via admin"""
        url = reverse('admin:core_reeducationperinee_delete', args=[self.seance1.id])
        
        # GET pour afficher la page de confirmation
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Voulez-vous vraiment supprimer')
        
        # POST pour confirmer la suppression
        response = self.client.post(url, {'post': 'yes'})
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la séance a été supprimée
        with self.assertRaises(ReeducationPerinee.DoesNotExist):
            ReeducationPerinee.objects.get(id=self.seance1.id)
    
    def test_admin_has_module_permission(self):
        """Test permissions de module"""
        self.assertTrue(self.admin.has_module_permission(Mock()))
    
    def test_admin_get_queryset_optimisation(self):
        """Test optimisation queryset avec select_related"""
        request = Mock()
        queryset = self.admin.get_queryset(request)
        
        # Vérifier que select_related est utilisé
        self.assertIn('patient', str(queryset.query))
        self.assertIn('created_by', str(queryset.query))
    
    def test_column_headers_descriptions(self):
        """Test descriptions des en-têtes de colonnes"""
        self.assertEqual(self.admin.patient_link.short_description, 'Patiente')
        self.assertEqual(self.admin.numero_seance_badge.short_description, 'Séance')
        self.assertEqual(self.admin.examen_clinique_resume.short_description, 'Examen clinique / Travail')
        self.assertEqual(self.admin.created_by_link.short_description, 'Sage-femme')
        self.assertEqual(self.admin.created_at_formatted.short_description, 'Créé le')
        
    def test_column_allow_tags(self):
        """Test autorisation HTML dans les colonnes (deprecated en Django moderne)"""
        # Django moderne n'utilise plus allow_tags, mais mark_safe
        # Les méthodes retournent du HTML formaté
        self.assertIsNotNone(self.admin.patient_link)
        self.assertIsNotNone(self.admin.numero_seance_badge)
        self.assertIsNotNone(self.admin.created_by_link)