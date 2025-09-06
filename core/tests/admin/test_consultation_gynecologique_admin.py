"""
Tests pour l'interface admin ConsultationGynecologique
Tests de configuration et fonctionnalités admin
"""

from django.test import TestCase, Client
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import date, timedelta
from django.utils.html import strip_tags

from core.models import ConsultationGynecologique, Patient, Caisse, SageFemme, Antecedents
from core.admin import ConsultationGynecologiqueAdmin
from authentication.models import SageFemmeUser


User = get_user_model()


class ConsultationGynecologiqueAdminTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.site = AdminSite()
        self.admin = ConsultationGynecologiqueAdmin(ConsultationGynecologique, self.site)
        
        # Créer un superutilisateur
        self.superuser = SageFemmeUser.objects.create_superuser(
            email='admin@maieutix.nc',
            password='adminpass123'
        )
        
        # Créer une sage-femme
        self.sage_femme = SageFemme.objects.create(
            user=self.superuser,
            nom='Martin',
            prenom='Dr Sophie',
            titre='Sage-Femme',
            telephone='0987654321',
            email='sophie.martin@test.com',
            numero_cafat='12345',
            ridet='RIDET123',
            rib='RIB123456789',
            banque='BCI',
            situation='titulaire'
        )
        
        # Créer une caisse
        self.caisse = Caisse.objects.create(
            nom="CAFAT"
        )
        
        # Créer des patients
        self.patient_femme = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse
        )
        
        # Créer des antécédents avec taille
        self.antecedents = Antecedents.objects.create(
            patient=self.patient_femme,
            taille=1.65
        )
        
        # Créer des consultations de test
        self.consultation_normale = ConsultationGynecologique.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today(),
            tension_systolique=110,
            tension_diastolique=70,
            poids=65.5,
            motif="Consultation de routine",
            examen="RAS",
            prescription="Aucune",
            notes="Patiente en bonne santé",
            created_by=self.sage_femme
        )
        
        self.consultation_hypertension = ConsultationGynecologique.objects.create(
            patient=self.patient_femme,
            date_consultation=date.today() - timedelta(days=7),
            tension_systolique=150,
            tension_diastolique=95,
            poids=66.0,
            motif="Contrôle tension",
            examen="Hypertension détectée",
            prescription="Traitement antihypertenseur",
            created_by=self.sage_femme
        )
        
        # Client pour les tests d'interface
        self.client = Client()
        self.client.login(email='admin@maieutix.nc', password='adminpass123')

    def test_admin_configuration(self):
        """Test de la configuration de base de l'admin"""
        # Vérifier list_display
        expected_list_display = [
            'patient_link',
            'date_consultation_formatted',
            'motif_court',
            'tension_affichage',
            'poids_affichage',
            'created_at_formatted'
        ]
        self.assertEqual(self.admin.list_display, expected_list_display)
        
        # Vérifier list_filter
        expected_list_filter = [
            'date_consultation',
            'created_at',
            'patient__caisse',
        ]
        self.assertEqual(self.admin.list_filter, expected_list_filter)
        
        # Vérifier search_fields
        expected_search_fields = [
            'patient__nom',
            'patient__prenom',
            'motif',
            'examen',
            'prescription'
        ]
        self.assertEqual(self.admin.search_fields, expected_search_fields)

    def test_admin_ordering(self):
        """Test de l'ordering dans l'admin"""
        expected_ordering = ['-date_consultation', '-created_at']
        self.assertEqual(self.admin.ordering, expected_ordering)

    def test_admin_readonly_fields(self):
        """Test des champs readonly"""
        expected_readonly = [
            'tension_interpretation_display',
            'imc_display',
            'resume_consultation_display',
            'created_at',
            'updated_at'
        ]
        self.assertEqual(self.admin.readonly_fields, expected_readonly)

    def test_admin_fieldsets(self):
        """Test de la structure des fieldsets"""
        fieldsets = self.admin.fieldsets
        
        # Vérifier le nombre de fieldsets
        self.assertEqual(len(fieldsets), 5)
        
        # Vérifier les noms des fieldsets
        fieldset_names = [fieldset[0] for fieldset in fieldsets]
        expected_names = [
            'Informations générales',
            'Constantes vitales',
            'Consultation',
            'Résumé',
            'Métadonnées'
        ]
        self.assertEqual(fieldset_names, expected_names)

    def test_patient_link_method(self):
        """Test de la méthode patient_link"""
        link_html = self.admin.patient_link(self.consultation_normale)
        
        # Vérifier que le lien contient le nom du patient
        self.assertIn('Marie Dupont', link_html)
        self.assertIn('target="_blank"', link_html)
        self.assertIn('<a href=', link_html)

    def test_date_consultation_formatted_method(self):
        """Test de la méthode date_consultation_formatted"""
        formatted_date = self.admin.date_consultation_formatted(self.consultation_normale)
        expected_date = date.today().strftime('%d/%m/%Y')
        self.assertEqual(formatted_date, expected_date)

    def test_motif_court_method(self):
        """Test de la méthode motif_court"""
        # Test avec motif court
        motif_court = self.admin.motif_court(self.consultation_normale)
        self.assertEqual(motif_court, "Consultation de routine")
        
        # Test avec motif long
        consultation_long_motif = ConsultationGynecologique(
            patient=self.patient_femme,
            motif="Consultation pour des douleurs abdominales persistantes depuis plusieurs semaines avec symptômes associés"
        )
        motif_tronque = self.admin.motif_court(consultation_long_motif)
        self.assertTrue(motif_tronque.endswith('...'))
        self.assertEqual(len(motif_tronque), 53)  # 50 + "..."

    def test_tension_affichage_method(self):
        """Test de la méthode tension_affichage"""
        # Test avec tension normale
        tension_html = self.admin.tension_affichage(self.consultation_normale)
        self.assertIn('110/70 mmHg', strip_tags(tension_html))
        self.assertIn('color: green', tension_html)  # Tension normale
        
        # Test avec hypertension
        tension_hyper_html = self.admin.tension_affichage(self.consultation_hypertension)
        self.assertIn('150/95 mmHg', strip_tags(tension_hyper_html))
        self.assertIn('color: red', tension_hyper_html)  # Hypertension

    def test_poids_affichage_method(self):
        """Test de la méthode poids_affichage"""
        poids_html = self.admin.poids_affichage(self.consultation_normale)
        
        # Vérifier le poids
        self.assertIn('65.5 kg', strip_tags(poids_html))
        
        # Vérifier l'IMC (doit être calculé avec taille 1.65m)
        expected_imc = round(65.5 / (1.65 ** 2), 1)
        self.assertIn(f'IMC: {expected_imc}', strip_tags(poids_html))

    def test_created_at_formatted_method(self):
        """Test de la méthode created_at_formatted"""
        formatted_datetime = self.admin.created_at_formatted(self.consultation_normale)
        
        # Vérifier le format
        self.assertRegex(formatted_datetime, r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}')

    def test_tension_interpretation_display_method(self):
        """Test de la méthode tension_interpretation_display"""
        # Test avec tension normale
        interpretation_html = self.admin.tension_interpretation_display(self.consultation_normale)
        self.assertIn('Tension normale', strip_tags(interpretation_html))
        self.assertIn('color: green', interpretation_html)
        
        # Test avec hypertension
        interpretation_hyper_html = self.admin.tension_interpretation_display(self.consultation_hypertension)
        self.assertIn('Hypertension', strip_tags(interpretation_hyper_html))
        self.assertIn('color: red', interpretation_hyper_html)

    def test_imc_display_method(self):
        """Test de la méthode imc_display"""
        imc_html = self.admin.imc_display(self.consultation_normale)
        
        # Calculer l'IMC attendu
        expected_imc = round(65.5 / (1.65 ** 2), 1)
        
        # Vérifier l'affichage
        self.assertIn(str(expected_imc), strip_tags(imc_html))
        
        # Vérifier l'interprétation (IMC normal)
        if 18.5 <= expected_imc < 25:
            self.assertIn('Poids normal', strip_tags(imc_html))
            self.assertIn('color: green', imc_html)

    def test_resume_consultation_display_method(self):
        """Test de la méthode resume_consultation_display"""
        resume_html = self.admin.resume_consultation_display(self.consultation_normale)
        
        # Vérifier le contenu du résumé
        resume_text = strip_tags(resume_html)
        self.assertIn('Consultation de routine', resume_text)
        self.assertIn('110/70 mmHg', resume_text)
        self.assertIn('65.5kg', resume_text)

    def test_get_queryset_optimization(self):
        """Test de l'optimisation des requêtes"""
        request = type('MockRequest', (), {})()
        request.user = self.superuser
        
        queryset = self.admin.get_queryset(request)
        
        # Vérifier que select_related est utilisé
        select_related = queryset.query.select_related
        self.assertTrue('patient' in select_related)
        # La structure peut être différente selon la version de Django

    def test_marquer_consultation_complete_action(self):
        """Test de l'action marquer_consultation_complete"""
        request = type('MockRequest', (), {})()
        request.user = self.superuser
        
        # Mock message_user
        messages = []
        def mock_message_user(request, message):
            messages.append(message)
        self.admin.message_user = mock_message_user
        
        # Exécuter l'action
        queryset = ConsultationGynecologique.objects.filter(id=self.consultation_normale.id)
        self.admin.marquer_consultation_complete(request, queryset)
        
        # Vérifier que la note a été ajoutée
        self.consultation_normale.refresh_from_db()
        self.assertIn('CONSULTATION COMPLÈTE', self.consultation_normale.notes)
        
        # Vérifier le message
        self.assertEqual(len(messages), 1)
        self.assertIn('1 consultation(s) marquée(s)', messages[0])

    def test_exporter_consultations_action(self):
        """Test de l'action exporter_consultations"""
        request = type('MockRequest', (), {})()
        request.user = self.superuser
        
        # Mock message_user
        messages = []
        def mock_message_user(request, message):
            messages.append(message)
        self.admin.message_user = mock_message_user
        
        # Exécuter l'action
        queryset = ConsultationGynecologique.objects.all()
        self.admin.exporter_consultations(request, queryset)
        
        # Vérifier le message
        self.assertEqual(len(messages), 1)
        self.assertIn('2 consultation(s) sélectionnée(s)', messages[0])

    def test_get_form_customization(self):
        """Test de la personnalisation du formulaire"""
        request = type('MockRequest', (), {})()
        request.user = self.superuser
        
        form_class = self.admin.get_form(request)
        form = form_class()
        
        # Vérifier que la date max est définie
        if 'date_consultation' in form.base_fields:
            max_date = form.base_fields['date_consultation'].widget.attrs.get('max')
            self.assertIsNotNone(max_date)

    def test_admin_interface_integration(self):
        """Test d'intégration de l'interface admin"""
        # Accéder à la liste des consultations
        list_url = reverse('admin:core_consultationgynecologique_changelist')
        response = self.client.get(list_url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que les consultations apparaissent
        self.assertContains(response, 'Consultation de routine')
        self.assertContains(response, 'Contrôle tension')

    def test_admin_detail_view_integration(self):
        """Test de la vue détail dans l'admin"""
        detail_url = reverse('admin:core_consultationgynecologique_change', 
                           args=[self.consultation_normale.id])
        response = self.client.get(detail_url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que les champs readonly apparaissent
        self.assertContains(response, 'normale')  # Interprétation  
        self.assertContains(response, 'IMC')  # IMC display

    def test_admin_search_functionality(self):
        """Test de la fonctionnalité de recherche"""
        list_url = reverse('admin:core_consultationgynecologique_changelist')
        
        # Recherche par nom de patient
        response = self.client.get(list_url, {'q': 'Dupont'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Consultation de routine')
        
        # Recherche par motif
        response = self.client.get(list_url, {'q': 'routine'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Consultation de routine')

    def test_admin_filter_functionality(self):
        """Test des filtres de l'admin"""
        list_url = reverse('admin:core_consultationgynecologique_changelist')
        
        # Filtre par date
        today = date.today()
        response = self.client.get(list_url, {
            'date_consultation__year': today.year,
            'date_consultation__month': today.month,
            'date_consultation__day': today.day
        })
        self.assertEqual(response.status_code, 200)

    def test_admin_list_per_page(self):
        """Test de la pagination"""
        self.assertEqual(self.admin.list_per_page, 25)

    def test_admin_date_hierarchy(self):
        """Test de la hiérarchie de dates"""
        self.assertEqual(self.admin.date_hierarchy, 'date_consultation')

    def test_admin_actions_list(self):
        """Test de la liste des actions"""
        expected_actions = ['marquer_consultation_complete', 'exporter_consultations']
        self.assertEqual(self.admin.actions, expected_actions)

    def test_admin_media_configuration(self):
        """Test de la configuration des médias"""
        # Vérifier que les fichiers CSS et JS sont configurés
        self.assertIn('admin/css/consultation_gynecologique.css', self.admin.Media.css['all'])
        self.assertIn('admin/js/consultation_gynecologique.js', self.admin.Media.js)

    def test_admin_verbose_names(self):
        """Test des noms verbose dans l'admin"""
        # Tester les descriptions courtes des méthodes
        self.assertEqual(self.admin.patient_link.short_description, "Patiente")
        self.assertEqual(self.admin.date_consultation_formatted.short_description, "Date")
        self.assertEqual(self.admin.motif_court.short_description, "Motif")
        self.assertEqual(self.admin.tension_affichage.short_description, "Tension")
        self.assertEqual(self.admin.poids_affichage.short_description, "Poids")

    def test_admin_order_fields(self):
        """Test des champs de tri"""
        # Vérifier que les méthodes ont des champs de tri définis
        self.assertEqual(self.admin.patient_link.admin_order_field, 'patient__nom')
        self.assertEqual(self.admin.date_consultation_formatted.admin_order_field, 'date_consultation')
        self.assertEqual(self.admin.motif_court.admin_order_field, 'motif')
        self.assertEqual(self.admin.tension_affichage.admin_order_field, 'tension_systolique')
        self.assertEqual(self.admin.poids_affichage.admin_order_field, 'poids')