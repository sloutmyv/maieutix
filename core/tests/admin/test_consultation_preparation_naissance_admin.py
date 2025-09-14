"""
Tests pour l'interface admin de ConsultationPreparationNaissance
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
    Patient, ConsultationPreparationNaissance, SageFemme,
    Caisse, ConditionPaiement, PeriodeActivite
)
from core.admin.consultation_preparation_naissance import ConsultationPreparationNaissanceAdmin
from authentication.models import SageFemmeUser

User = get_user_model()


class ConsultationPreparationNaissanceAdminTest(TestCase):
    """Tests pour l'admin ConsultationPreparationNaissance"""
    
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
            caisse=self.caisse,
            date_debut_grossesse=date(2024, 1, 1)
        )
        
        # Créer des consultations de test
        self.consultation1 = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today() - timedelta(days=7),
            theme_aborde="Respiration et relaxation - un thème très long qui va être tronqué",
            a_prevoir="Revoir les exercices - une description très longue qui va être tronquée également",
            created_by=self.sage_femme
        )
        
        self.consultation2 = ConsultationPreparationNaissance.objects.create(
            patient=self.patiente,
            date_consultation=date.today() - timedelta(days=3),
            theme_aborde="Allaitement maternel",
            created_by=self.sage_femme
        )
        
        # Instance de l'admin
        self.admin = ConsultationPreparationNaissanceAdmin(ConsultationPreparationNaissance, self.site)
        
        # Se connecter en tant qu'admin
        self.client.login(email="admin@test.com", password="adminpass123")
    
    def test_admin_list_display(self):
        """Test affichage de la liste admin"""
        response = self.client.get(reverse('admin:core_consultationpreparationnaissance_changelist'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Julie Martin')
        self.assertContains(response, 'Respiration et relaxation')
        self.assertContains(response, 'Allaitement maternel')
        
        # Vérifier la présence des colonnes
        self.assertContains(response, 'Date consultation')
        self.assertContains(response, 'SA')
        self.assertContains(response, 'Sage-femme')
    
    def test_admin_list_filter(self):
        """Test filtres de la liste"""
        response = self.client.get(
            reverse('admin:core_consultationpreparationnaissance_changelist'),
            {'date_consultation__gte': date.today() - timedelta(days=5)}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Allaitement maternel')
        self.assertNotContains(response, 'Respiration et relaxation')
    
    def test_admin_search(self):
        """Test recherche dans l'admin"""
        response = self.client.get(
            reverse('admin:core_consultationpreparationnaissance_changelist'),
            {'q': 'allaitement'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Allaitement maternel')
        self.assertNotContains(response, 'Respiration et relaxation')
    
    def test_admin_search_patient_name(self):
        """Test recherche par nom de patiente"""
        response = self.client.get(
            reverse('admin:core_consultationpreparationnaissance_changelist'),
            {'q': 'Martin'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Julie Martin')
        self.assertContains(response, 'Respiration et relaxation')
        self.assertContains(response, 'Allaitement maternel')
    
    def test_admin_changelist_view(self):
        """Test vue détaillée d'une consultation"""
        response = self.client.get(
            reverse('admin:core_consultationpreparationnaissance_change', args=[self.consultation1.id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Respiration et relaxation')
        self.assertContains(response, 'Revoir les exercices')
        self.assertContains(response, 'Julie Martin')
    
    def test_admin_readonly_fields(self):
        """Test champs en lecture seule"""
        response = self.client.get(
            reverse('admin:core_consultationpreparationnaissance_change', args=[self.consultation1.id])
        )
        
        self.assertEqual(response.status_code, 200)
        # Vérifier que les champs readonly sont présents  
        self.assertContains(response, 'Semaines d')
        self.assertContains(response, 'Résumé consultation')
        self.assertContains(response, 'Créé le')
        self.assertContains(response, 'Modifié le')
    
    def test_admin_fieldsets(self):
        """Test organisation des fieldsets"""
        response = self.client.get(
            reverse('admin:core_consultationpreparationnaissance_change', args=[self.consultation1.id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Informations générales')
        self.assertContains(response, 'Contenu de la consultation')
        self.assertContains(response, 'Résumé')
        self.assertContains(response, 'Métadonnées')
    
    # Tests des méthodes d'affichage personnalisées
    def test_patient_link_method(self):
        """Test méthode patient_link"""
        link = self.admin.patient_link(self.consultation1)
        
        self.assertIn('Julie Martin', link)
        self.assertIn('href=', link)
        self.assertIn('target="_blank"', link)
    
    def test_patient_link_method_no_patient(self):
        """Test méthode patient_link sans patient"""
        consultation_no_patient = Mock()
        consultation_no_patient.patient = None
        
        link = self.admin.patient_link(consultation_no_patient)
        self.assertEqual(link, "-")
    
    def test_date_consultation_formatted_method(self):
        """Test méthode date_consultation_formatted"""
        formatted_date = self.admin.date_consultation_formatted(self.consultation1)
        
        expected_date = self.consultation1.date_consultation.strftime('%d/%m/%Y')
        self.assertEqual(formatted_date, expected_date)
    
    def test_date_consultation_formatted_method_no_date(self):
        """Test méthode date_consultation_formatted sans date"""
        consultation_no_date = Mock()
        consultation_no_date.date_consultation = None
        
        formatted_date = self.admin.date_consultation_formatted(consultation_no_date)
        self.assertEqual(formatted_date, "-")
    
    def test_sa_affichage_method(self):
        """Test méthode sa_affichage"""
        sa_display = self.admin.sa_affichage(self.consultation1)
        
        self.assertIn('span', sa_display)
        self.assertIn('background-color: #e8f5e8', sa_display)
        self.assertIn(self.consultation1.semaines_amenorrhee, sa_display)
    
    def test_sa_affichage_method_no_sa(self):
        """Test méthode sa_affichage sans SA"""
        consultation_no_sa = Mock()
        consultation_no_sa.semaines_amenorrhee = None
        
        sa_display = self.admin.sa_affichage(consultation_no_sa)
        self.assertEqual(sa_display, "-")
    
    def test_theme_aborde_court_method(self):
        """Test méthode theme_aborde_court avec troncature"""
        theme_court = self.admin.theme_aborde_court(self.consultation1)
        
        # Le thème long devrait être tronqué
        self.assertIn('Respiration et relaxation', theme_court)
        self.assertIn('...', theme_court)
        self.assertIn('title=', theme_court)
    
    def test_theme_aborde_court_method_court(self):
        """Test méthode theme_aborde_court avec thème court"""
        theme_court = self.admin.theme_aborde_court(self.consultation2)
        
        # Le thème court ne devrait pas être tronqué
        self.assertIn('Allaitement maternel', theme_court)
        self.assertNotIn('...', theme_court)
    
    def test_theme_aborde_court_method_empty(self):
        """Test méthode theme_aborde_court vide"""
        consultation_empty = Mock()
        consultation_empty.theme_aborde = ""
        
        theme_court = self.admin.theme_aborde_court(consultation_empty)
        self.assertEqual(theme_court, "-")
    
    def test_a_prevoir_court_method(self):
        """Test méthode a_prevoir_court avec troncature"""
        prevoir_court = self.admin.a_prevoir_court(self.consultation1)
        
        # Le texte long devrait être tronqué
        self.assertIn('Revoir les exercices', prevoir_court)
        self.assertIn('...', prevoir_court)
        self.assertIn('title=', prevoir_court)
    
    def test_a_prevoir_court_method_empty(self):
        """Test méthode a_prevoir_court vide"""
        consultation_empty = Mock()
        consultation_empty.a_prevoir = ""
        
        prevoir_court = self.admin.a_prevoir_court(consultation_empty)
        self.assertEqual(prevoir_court, "-")
    
    def test_created_by_display_method(self):
        """Test méthode created_by_display"""
        created_by = self.admin.created_by_display(self.consultation1)
        
        self.assertEqual(created_by, "Marie DUPONT")
    
    def test_created_by_display_method_no_creator(self):
        """Test méthode created_by_display sans créateur"""
        consultation_no_creator = Mock()
        consultation_no_creator.created_by = None
        
        created_by = self.admin.created_by_display(consultation_no_creator)
        self.assertEqual(created_by, "-")
    
    def test_created_at_formatted_method(self):
        """Test méthode created_at_formatted"""
        formatted_created = self.admin.created_at_formatted(self.consultation1)
        
        expected_format = self.consultation1.created_at.strftime('%d/%m/%Y %H:%M')
        self.assertEqual(formatted_created, expected_format)
    
    def test_consultation_resume_display_method(self):
        """Test méthode consultation_resume_display"""
        resume_display = self.admin.consultation_resume_display(self.consultation1)
        
        self.assertIn('background-color: #f8f9fa', resume_display)
        self.assertIn('border-left: 3px solid #22c55e', resume_display)
        self.assertIn('Résumé', resume_display)
        self.assertIn(self.consultation1.consultation_resume, resume_display)
    
    def test_get_queryset_optimization(self):
        """Test optimisation des requêtes dans get_queryset"""
        request = Mock()
        queryset = self.admin.get_queryset(request)
        
        # Vérifier que les select_related sont appliqués
        self.assertIn('patient', str(queryset.query))
        self.assertIn('caisse', str(queryset.query))
        self.assertIn('created_by', str(queryset.query))
    
    def test_action_marquer_consultation_complete(self):
        """Test action marquer_consultation_complete"""
        request = HttpRequest()
        request.method = 'POST'
        request.user = self.admin_user
        
        # Ajouter le storage des messages
        setattr(request, 'session', {})
        setattr(request, '_messages', FallbackStorage(request))
        
        queryset = ConsultationPreparationNaissance.objects.filter(id=self.consultation1.id)
        
        # Exécuter l'action
        self.admin.marquer_consultation_complete(request, queryset)
        
        # Vérifier que la consultation a été modifiée
        self.consultation1.refresh_from_db()
        self.assertIn('CONSULTATION COMPLÈTE', self.consultation1.a_prevoir)
    
    def test_action_marquer_consultation_complete_deja_complete(self):
        """Test action sur consultation déjà complète"""
        # Marquer d'abord comme complète
        self.consultation1.a_prevoir = "Test CONSULTATION COMPLÈTE"
        self.consultation1.save()
        
        request = HttpRequest()
        request.method = 'POST'
        request.user = self.admin_user
        setattr(request, 'session', {})
        setattr(request, '_messages', FallbackStorage(request))
        
        queryset = ConsultationPreparationNaissance.objects.filter(id=self.consultation1.id)
        
        # Exécuter l'action
        self.admin.marquer_consultation_complete(request, queryset)
        
        # La consultation ne devrait pas être modifiée à nouveau
        self.consultation1.refresh_from_db()
        self.assertEqual(self.consultation1.a_prevoir.count('CONSULTATION COMPLÈTE'), 1)
    
    def test_action_exporter_consultations(self):
        """Test action exporter_consultations"""
        request = HttpRequest()
        request.method = 'POST'
        request.user = self.admin_user
        setattr(request, 'session', {})
        setattr(request, '_messages', FallbackStorage(request))
        
        queryset = ConsultationPreparationNaissance.objects.filter(
            id__in=[self.consultation1.id, self.consultation2.id]
        )
        
        # Exécuter l'action (placeholder)
        self.admin.exporter_consultations(request, queryset)
        
        # Vérifier que l'action s'exécute sans erreur
        # (C'est un placeholder, donc pas de vérification fonctionnelle)
        self.assertTrue(True)
    
    def test_get_form_date_max(self):
        """Test configuration du formulaire avec date max"""
        request = Mock()
        form_class = self.admin.get_form(request)
        
        # Vérifier que la date max est configurée
        if 'date_consultation' in form_class.base_fields:
            max_date = form_class.base_fields['date_consultation'].widget.attrs.get('max')
            self.assertIsNotNone(max_date)
    
    def test_admin_ordering(self):
        """Test ordre d'affichage dans l'admin"""
        self.assertEqual(self.admin.ordering, ['-date_consultation', '-created_at'])
    
    def test_admin_date_hierarchy(self):
        """Test hiérarchie de dates"""
        self.assertEqual(self.admin.date_hierarchy, 'date_consultation')
    
    def test_admin_list_per_page(self):
        """Test pagination"""
        self.assertEqual(self.admin.list_per_page, 25)
    
    def test_admin_media_files(self):
        """Test fichiers média CSS/JS"""
        media = self.admin.media
        
        self.assertIn('admin/css/consultation_preparation_naissance.css', media._css.get('all', []))
        self.assertIn('admin/js/consultation_preparation_naissance.js', media._js)
    
    def test_admin_add_consultation(self):
        """Test ajout de consultation via admin"""
        data = {
            'patient': self.patiente.id,
            'date_consultation': date.today().isoformat(),
            'theme_aborde': 'Nouveau thème admin',
            'a_prevoir': 'Nouveaux points',
            'created_by': self.sage_femme.id
        }
        
        response = self.client.post(
            reverse('admin:core_consultationpreparationnaissance_add'),
            data
        )
        
        # Vérifier la redirection après succès
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la consultation a été créée
        consultation = ConsultationPreparationNaissance.objects.filter(
            theme_aborde='Nouveau thème admin'
        ).first()
        self.assertIsNotNone(consultation)
        self.assertEqual(consultation.patient, self.patiente)
    
    def test_admin_edit_consultation(self):
        """Test modification de consultation via admin"""
        data = {
            'patient': self.patiente.id,
            'date_consultation': self.consultation1.date_consultation.isoformat(),
            'theme_aborde': 'Thème modifié admin',
            'a_prevoir': self.consultation1.a_prevoir,
            'created_by': self.sage_femme.id
        }
        
        response = self.client.post(
            reverse('admin:core_consultationpreparationnaissance_change', args=[self.consultation1.id]),
            data
        )
        
        # Vérifier la redirection après succès
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la consultation a été modifiée
        self.consultation1.refresh_from_db()
        self.assertEqual(self.consultation1.theme_aborde, 'Thème modifié admin')
    
    def test_admin_delete_consultation(self):
        """Test suppression de consultation via admin"""
        consultation_id = self.consultation1.id
        
        response = self.client.post(
            reverse('admin:core_consultationpreparationnaissance_delete', args=[consultation_id]),
            {'post': 'yes'}  # Confirmation de suppression
        )
        
        # Vérifier la redirection après succès
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la consultation a été supprimée
        with self.assertRaises(ConsultationPreparationNaissance.DoesNotExist):
            ConsultationPreparationNaissance.objects.get(id=consultation_id)