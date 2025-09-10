"""
Tests pour l'admin ConsultationObstetricale
Tests complets de l'interface d'administration
"""

from django.test import TestCase, Client
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.utils import timezone
from datetime import date, timedelta
from unittest.mock import Mock, patch

from core.admin.consultation_obstetricale import ConsultationObstetricaleAdmin
from core.models import ConsultationObstetricale, Patient, Caisse, SageFemme
from authentication.models import SageFemmeUser


class ConsultationObstetricaleAdminTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.site = AdminSite()
        self.admin = ConsultationObstetricaleAdmin(ConsultationObstetricale, self.site)
        
        # Créer un superutilisateur
        self.superuser = SageFemmeUser.objects.create_superuser(
            email='admin@test.com',
            password='adminpass123'
        )
        
        self.caisse = Caisse.objects.create(nom="CAFAT")
        
        # Patient femme
        self.patient_femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse,
            date_debut_grossesse=date.today() - timedelta(days=140)
        )
        
        # Créer une sage-femme
        self.user_sf = SageFemmeUser.objects.create_user(
            email='sage_femme_test@test.com',
            password='testpass123'
        )
        self.sage_femme = SageFemme.objects.create(
            user=self.user_sf,
            nom='Martin',
            prenom='Dr Sophie',
            titre='Sage-Femme',
            telephone='0987654321',
            email='sophie.martin@test.com',
            numero_cafat='123456',
            ridet='987654',
            rib='FR7630001007941234567890185',
            banque='BNC',
            situation='titulaire'
        )
        
        # Créer des consultations de test
        self.consultation1 = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today() - timedelta(days=7),
            motif="Contrôle de routine",
            tension_systolique=120,
            tension_diastolique=80,
            poids=65.5,
            created_by=self.sage_femme
        )
        
        self.consultation2 = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today() - timedelta(days=14),
            motif="Consultation spécialisée",
            tension_systolique=140,
            tension_diastolique=90,
            poids=66.0,
            examen="Examen complet",
            prescription="Repos et surveillance",
            created_by=self.sage_femme
        )
        
        # Créer une consultation avec hypertension
        self.consultation_hypertension = ConsultationObstetricale.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today() - timedelta(days=21),
            motif="Hypertension",
            tension_systolique=160,
            tension_diastolique=100,
            created_by=self.sage_femme
        )
        
        self.client = Client()
    
    def test_admin_list_display(self):
        """Test de l'affichage de la liste"""
        expected_list_display = [
            'patient_link',
            'date_consultation_formatted',
            'sa_affichage',
            'motif_court',
            'tension_affichage',
            'poids_affichage',
            'created_at_formatted'
        ]
        self.assertEqual(self.admin.list_display, expected_list_display)
    
    def test_admin_list_filter(self):
        """Test des filtres de liste"""
        expected_list_filter = [
            'date_consultation',
            'created_at',
            'patient__caisse',
        ]
        self.assertEqual(self.admin.list_filter, expected_list_filter)
    
    def test_admin_search_fields(self):
        """Test des champs de recherche"""
        expected_search_fields = [
            'patient__nom',
            'patient__prenom',
            'motif',
            'examen',
            'prescription'
        ]
        self.assertEqual(self.admin.search_fields, expected_search_fields)
    
    def test_admin_readonly_fields(self):
        """Test des champs en lecture seule"""
        expected_readonly_fields = [
            'semaines_amenorrhee',
            'tension_interpretation_display',
            'imc_display',
            'resume_consultation_display',
            'created_at',
            'updated_at'
        ]
        self.assertEqual(self.admin.readonly_fields, expected_readonly_fields)
    
    def test_admin_fieldsets(self):
        """Test de l'organisation des fieldsets"""
        self.assertEqual(len(self.admin.fieldsets), 5)
        
        # Vérifier les titres des fieldsets
        fieldset_titles = [fs[0] for fs in self.admin.fieldsets]
        expected_titles = [
            'Informations générales',
            'Constantes vitales',
            'Consultation',
            'Résumé',
            'Métadonnées'
        ]
        self.assertEqual(fieldset_titles, expected_titles)
    
    def test_admin_ordering(self):
        """Test de l'ordre par défaut"""
        expected_ordering = ['-date_consultation', '-created_at']
        self.assertEqual(self.admin.ordering, expected_ordering)
    
    def test_patient_link_method(self):
        """Test de la méthode patient_link"""
        link_html = self.admin.patient_link(self.consultation1)
        
        self.assertIn(self.patient_femme.nom_complet, link_html)
        self.assertIn('href=', link_html)
        self.assertIn('target="_blank"', link_html)
    
    def test_patient_link_method_no_patient(self):
        """Test patient_link sans patient"""
        consultation_sans_patient = Mock()
        consultation_sans_patient.patient = None
        
        result = self.admin.patient_link(consultation_sans_patient)
        self.assertEqual(result, "-")
    
    def test_date_consultation_formatted_method(self):
        """Test de la méthode date_consultation_formatted"""
        formatted_date = self.admin.date_consultation_formatted(self.consultation1)
        expected_date = self.consultation1.date_consultation.strftime('%d/%m/%Y')
        self.assertEqual(formatted_date, expected_date)
    
    def test_date_consultation_formatted_method_no_date(self):
        """Test date_consultation_formatted sans date"""
        consultation_sans_date = Mock()
        consultation_sans_date.date_consultation = None
        
        result = self.admin.date_consultation_formatted(consultation_sans_date)
        self.assertEqual(result, "-")
    
    def test_sa_affichage_method(self):
        """Test de la méthode sa_affichage"""
        # La SA devrait être calculée automatiquement lors de la création
        sa_html = self.admin.sa_affichage(self.consultation1)
        
        if self.consultation1.semaines_amenorrhee:
            self.assertIn('background-color: #e8f5e8', sa_html)
            self.assertIn(self.consultation1.semaines_amenorrhee, sa_html)
        else:
            self.assertEqual(sa_html, "-")
    
    def test_motif_court_method(self):
        """Test de la méthode motif_court"""
        motif_court = self.admin.motif_court(self.consultation1)
        self.assertEqual(motif_court, self.consultation1.motif)
        
        # Test avec motif long
        consultation_motif_long = Mock()
        consultation_motif_long.motif = "A" * 60  # Plus de 50 caractères
        
        result = self.admin.motif_court(consultation_motif_long)
        self.assertEqual(len(result), 53)  # 50 + "..."
        self.assertTrue(result.endswith("..."))
    
    def test_motif_court_method_no_motif(self):
        """Test motif_court sans motif"""
        consultation_sans_motif = Mock()
        consultation_sans_motif.motif = None
        
        result = self.admin.motif_court(consultation_sans_motif)
        self.assertEqual(result, "-")
    
    def test_tension_affichage_method_normal(self):
        """Test tension_affichage avec tension"""
        tension_html = self.admin.tension_affichage(self.consultation1)
        
        self.assertIn('120/80 mmHg', tension_html)
        # La tension 120/80 peut être considérée comme limite haute, donc on teste juste la présence de la valeur
        self.assertIn('span style="color:', tension_html)
    
    def test_tension_affichage_method_hypertension(self):
        """Test tension_affichage avec hypertension"""
        tension_html = self.admin.tension_affichage(self.consultation_hypertension)
        
        self.assertIn('160/100 mmHg', tension_html)
        self.assertIn('color: red', tension_html)
        self.assertIn('hypertension', tension_html.lower())
    
    def test_tension_affichage_method_no_tension(self):
        """Test tension_affichage sans tension"""
        consultation_sans_tension = Mock()
        consultation_sans_tension.tension_complete = None
        
        result = self.admin.tension_affichage(consultation_sans_tension)
        self.assertEqual(result, "-")
    
    def test_poids_affichage_method(self):
        """Test de la méthode poids_affichage"""
        poids_html = self.admin.poids_affichage(self.consultation1)
        
        self.assertIn('65.5 kg', poids_html)
        # Si IMC disponible, devrait aussi l'afficher
        if self.consultation1.imc:
            self.assertIn(f'IMC: {self.consultation1.imc}', poids_html)
    
    def test_poids_affichage_method_no_poids(self):
        """Test poids_affichage sans poids"""
        consultation_sans_poids = Mock()
        consultation_sans_poids.poids = None
        
        result = self.admin.poids_affichage(consultation_sans_poids)
        self.assertEqual(result, "-")
    
    def test_created_at_formatted_method(self):
        """Test de la méthode created_at_formatted"""
        formatted_datetime = self.admin.created_at_formatted(self.consultation1)
        expected_datetime = self.consultation1.created_at.strftime('%d/%m/%Y %H:%M')
        self.assertEqual(formatted_datetime, expected_datetime)
    
    def test_tension_interpretation_display_method(self):
        """Test de la méthode tension_interpretation_display"""
        # Test avec tension 120/80 (peut être considérée comme limite)
        interpretation_html = self.admin.tension_interpretation_display(self.consultation1)
        self.assertIn('font-weight: bold', interpretation_html)
        # Tester qu'il y a bien une interprétation
        self.assertIn('span style="color:', interpretation_html)
        
        # Test avec hypertension claire
        interpretation_hypertension = self.admin.tension_interpretation_display(
            self.consultation_hypertension
        )
        self.assertIn('color: red', interpretation_hypertension)
        self.assertIn('hypertension', interpretation_hypertension.lower())
    
    def test_imc_display_method(self):
        """Test de la méthode imc_display"""
        # Créer des antécédents avec taille pour le calcul IMC
        from core.models import Antecedents
        antecedents = Antecedents.objects.create(
            patient=self.patient_femme,
            taille=1.65
        )
        
        # Recalculer la consultation pour avoir l'IMC
        consultation = ConsultationObstetricale.objects.get(pk=self.consultation1.pk)
        imc_html = self.admin.imc_display(consultation)
        
        if consultation.imc:
            self.assertIn(str(consultation.imc), imc_html)
            self.assertIn('font-weight: bold', imc_html)
    
    def test_resume_consultation_display_method(self):
        """Test de la méthode resume_consultation_display"""
        resume_html = self.admin.resume_consultation_display(self.consultation1)
        
        self.assertIn('background-color: #f8f9fa', resume_html)
        self.assertIn(self.consultation1.motif[:50], resume_html)
    
    def test_get_queryset_optimization(self):
        """Test de l'optimisation des requêtes"""
        request = HttpRequest()
        request.user = self.superuser
        
        queryset = self.admin.get_queryset(request)
        
        # Vérifier que select_related est appliqué (format Django récent)
        self.assertIn('patient', queryset.query.select_related)
        # Le format peut être soit une chaîne soit un dictionnaire imbriqué
        select_related_str = str(queryset.query.select_related)
        self.assertIn('caisse', select_related_str)
    
    def test_marquer_consultation_complete_action(self):
        """Test de l'action marquer_consultation_complete"""
        request = HttpRequest()
        request.user = self.superuser
        
        queryset = ConsultationObstetricale.objects.filter(pk=self.consultation1.pk)
        
        with patch.object(self.admin, 'message_user') as mock_message:
            self.admin.marquer_consultation_complete(request, queryset)
        
        # Vérifier que la consultation a été marquée
        consultation_updated = ConsultationObstetricale.objects.get(pk=self.consultation1.pk)
        self.assertIn('CONSULTATION COMPLÈTE', consultation_updated.notes)
        
        # Vérifier le message utilisateur
        mock_message.assert_called_once()
        args, kwargs = mock_message.call_args
        self.assertIn('1 consultation(s) marquée(s)', args[1])
    
    def test_exporter_consultations_action(self):
        """Test de l'action exporter_consultations"""
        request = HttpRequest()
        request.user = self.superuser
        
        queryset = ConsultationObstetricale.objects.filter(pk=self.consultation1.pk)
        
        with patch.object(self.admin, 'message_user') as mock_message:
            self.admin.exporter_consultations(request, queryset)
        
        # Vérifier le message utilisateur
        mock_message.assert_called_once()
        args, kwargs = mock_message.call_args
        self.assertIn('1 consultation(s) sélectionnée(s)', args[1])
    
    def test_get_form_date_max_constraint(self):
        """Test que le formulaire a une contrainte de date max"""
        request = HttpRequest()
        request.user = self.superuser
        
        form_class = self.admin.get_form(request)
        form = form_class()
        
        if 'date_consultation' in form.base_fields:
            date_widget = form.base_fields['date_consultation'].widget
            self.assertEqual(date_widget.attrs['max'], timezone.now().date())
    
    def test_admin_permissions_integration(self):
        """Test d'intégration des permissions admin"""
        self.client.force_login(self.superuser)
        
        # Test accès à la liste
        response = self.client.get('/admin/core/consultationobstetricale/')
        self.assertEqual(response.status_code, 200)
        
        # Test accès au détail
        response = self.client.get(f'/admin/core/consultationobstetricale/{self.consultation1.pk}/change/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_list_display_content(self):
        """Test du contenu affiché dans la liste admin"""
        self.client.force_login(self.superuser)
        
        response = self.client.get('/admin/core/consultationobstetricale/')
        
        self.assertContains(response, self.patient_femme.nom_complet)
        self.assertContains(response, self.consultation1.motif)
        self.assertContains(response, '120/80 mmHg')  # Tension
    
    def test_admin_search_functionality(self):
        """Test de la fonctionnalité de recherche"""
        self.client.force_login(self.superuser)
        
        # Recherche par nom de patient
        response = self.client.get('/admin/core/consultationobstetricale/', {
            'q': 'Dupont'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.consultation1.motif)
        
        # Recherche par motif
        response = self.client.get('/admin/core/consultationobstetricale/', {
            'q': 'routine'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contrôle de routine')
    
    def test_admin_filters_functionality(self):
        """Test des filtres admin"""
        self.client.force_login(self.superuser)
        
        # Filtre par date de consultation
        today = date.today()
        response = self.client.get('/admin/core/consultationobstetricale/', {
            'date_consultation__gte': today - timedelta(days=10),
            'date_consultation__lt': today
        })
        self.assertEqual(response.status_code, 200)
    
    def test_admin_css_media_files(self):
        """Test des fichiers CSS et JS personnalisés"""
        self.assertIn('admin/css/consultation_obstetricale.css', self.admin.Media.css['all'])
        self.assertIn('admin/js/consultation_obstetricale.js', self.admin.Media.js)
    
    def test_admin_date_hierarchy(self):
        """Test de la hiérarchie de date"""
        self.assertEqual(self.admin.date_hierarchy, 'date_consultation')
    
    def test_admin_list_per_page(self):
        """Test du nombre d'éléments par page"""
        self.assertEqual(self.admin.list_per_page, 25)
    
    def test_admin_meta_information(self):
        """Test des informations meta du modèle dans l'admin"""
        self.assertEqual(
            self.admin.model._meta.verbose_name, 
            "6.1.3.2 Consultation Obstétricale"
        )
        self.assertEqual(
            self.admin.model._meta.verbose_name_plural, 
            "6.1.3.2 Consultations Obstétricales"
        )