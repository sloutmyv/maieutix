"""
Tests pour l'interface admin des antécédents et frottis
Tests complets de la configuration admin Django
"""

from datetime import date
from django.test import TestCase, Client
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.admin import ModelAdmin
from core.models import Patient, Caisse, Antecedents, FrottisCV, SageFemme, PeriodeActivite
from core.admin.antecedents import AntecedentsAdmin, FrottisCVAdmin, FrottisCVInline


class MockRequest:
    def __init__(self, user=None):
        self.user = user


class AntecedentsAdminTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.site = AdminSite()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@test.com',
            password='admin123'
        )
        
        self.caisse = Caisse.objects.create(nom="CAFAT")
        
        self.patiente = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse
        )
        
        self.antecedents = Antecedents.objects.create(
            patient=self.patiente,
            taille=1.65,
            poids=60.0,
            medecin_traitant="Dr. Martin",
            gynecologue="Dr. Bernard",
            asthme=True,
            diabete=False,
            hta=True,
            atcd_obstetricaux="G1P1",
            contraception="Pilule"
        )
    
    def test_antecedents_admin_registration(self):
        """Test que AntecedentsAdmin est correctement enregistré"""
        admin = AntecedentsAdmin(Antecedents, self.site)
        self.assertIsInstance(admin, ModelAdmin)
    
    def test_antecedents_admin_list_display(self):
        """Test configuration list_display de AntecedentsAdmin"""
        admin = AntecedentsAdmin(Antecedents, self.site)
        expected_fields = ('patient', 'taille', 'poids', 'imc', 'medecin_traitant', 'updated_at')
        self.assertEqual(admin.list_display, expected_fields)
    
    def test_antecedents_admin_list_filter(self):
        """Test configuration list_filter de AntecedentsAdmin"""
        admin = AntecedentsAdmin(Antecedents, self.site)
        expected_filters = ('asthme', 'diabete', 'hta', 'epilepsie', 'created_at')
        self.assertEqual(admin.list_filter, expected_filters)
    
    def test_antecedents_admin_search_fields(self):
        """Test configuration search_fields de AntecedentsAdmin"""
        admin = AntecedentsAdmin(Antecedents, self.site)
        expected_search = ('patient__nom', 'patient__prenom', 'medecin_traitant', 'gynecologue')
        self.assertEqual(admin.search_fields, expected_search)
    
    def test_antecedents_admin_fieldsets(self):
        """Test configuration fieldsets de AntecedentsAdmin"""
        admin = AntecedentsAdmin(Antecedents, self.site)
        
        # Vérifier que fieldsets est défini
        self.assertIsNotNone(admin.fieldsets)
        self.assertEqual(len(admin.fieldsets), 8)
        
        # Vérifier les titres des sections
        fieldset_titles = [fieldset[0] for fieldset in admin.fieldsets]
        expected_titles = [
            'Patient',
            '6.1.1 Biométrie',
            'Médecins',
            'ATCD Médicaux',
            'ATCD Obstétricaux',
            'FCV',
            'ATCD Familiaux',
            'ATCD Chirurgicaux et Contraception'
        ]
        self.assertEqual(fieldset_titles, expected_titles)
        
        # Vérifier que les sections sont en collapse
        for i in range(1, len(admin.fieldsets)):  # Sauf la première (Patient)
            self.assertIn('collapse', admin.fieldsets[i][1].get('classes', []))
    
    def test_antecedents_admin_inlines(self):
        """Test configuration inlines de AntecedentsAdmin"""
        admin = AntecedentsAdmin(Antecedents, self.site)
        self.assertEqual(admin.inlines, [FrottisCVInline])
    
    def test_antecedents_admin_imc_method(self):
        """Test méthode imc personnalisée de AntecedentsAdmin"""
        admin = AntecedentsAdmin(Antecedents, self.site)
        
        # Test avec taille et poids
        imc_result = admin.imc(self.antecedents)
        expected_imc = round(60.0 / (1.65 ** 2), 2)  # 22.04
        self.assertEqual(imc_result, expected_imc)
        
        # Test sans données
        antecedents_no_data = Antecedents.objects.create(
            patient=Patient.objects.create(
                type_patient='femme',
                nom='Test',
                prenom='Test',
                date_naissance=date(1990, 1, 1),
                caisse=self.caisse
            )
        )
        imc_result_none = admin.imc(antecedents_no_data)
        self.assertIsNone(imc_result_none)
        
        # Vérifier short_description
        self.assertEqual(admin.imc.short_description, 'IMC')
    
    def test_antecedents_model_verbose_names(self):
        """Test verbose_name et verbose_name_plural du modèle"""
        self.assertEqual(Antecedents._meta.verbose_name, "6.1.1 Antécédents")
        self.assertEqual(Antecedents._meta.verbose_name_plural, "6.1.1 Antécédents")


class FrottisCVInlineTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.site = AdminSite()
        
        self.caisse = Caisse.objects.create(nom="CAFAT")
        self.patiente = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse
        )
        
        self.antecedents = Antecedents.objects.create(
            patient=self.patiente,
            taille=1.65,
            poids=60.0
        )
    
    def test_frottis_inline_configuration(self):
        """Test configuration de FrottisCVInline"""
        inline = FrottisCVInline(Antecedents, self.site)
        
        self.assertEqual(inline.model, FrottisCV)
        self.assertEqual(inline.extra, 0)
        self.assertEqual(inline.fields, ('date_frottis', 'resultat'))
        self.assertEqual(inline.ordering, ('-date_frottis',))
    
    def test_frottis_inline_is_tabular(self):
        """Test que FrottisCVInline hérite de TabularInline"""
        from django.contrib.admin import TabularInline
        inline = FrottisCVInline(Antecedents, self.site)
        self.assertIsInstance(inline, TabularInline)


class FrottisCVAdminTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.site = AdminSite()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@test.com',
            password='admin123'
        )
        
        self.caisse = Caisse.objects.create(nom="CAFAT")
        
        self.patiente = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse
        )
        
        self.antecedents = Antecedents.objects.create(
            patient=self.patiente,
            taille=1.65,
            poids=60.0
        )
        
        self.frottis = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2024, 6, 15),
            resultat="Normal - Absence de cellules anormales. Flore lactobacillaire prédominante."
        )
    
    def test_frottis_admin_registration(self):
        """Test que FrottisCVAdmin est correctement enregistré"""
        admin = FrottisCVAdmin(FrottisCV, self.site)
        self.assertIsInstance(admin, ModelAdmin)
    
    def test_frottis_admin_list_display(self):
        """Test configuration list_display de FrottisCVAdmin"""
        admin = FrottisCVAdmin(FrottisCV, self.site)
        expected_fields = ('patient_nom', 'date_frottis', 'resultat_court', 'created_at')
        self.assertEqual(admin.list_display, expected_fields)
    
    def test_frottis_admin_list_filter(self):
        """Test configuration list_filter de FrottisCVAdmin"""
        admin = FrottisCVAdmin(FrottisCV, self.site)
        expected_filters = ('date_frottis', 'created_at')
        self.assertEqual(admin.list_filter, expected_filters)
    
    def test_frottis_admin_search_fields(self):
        """Test configuration search_fields de FrottisCVAdmin"""
        admin = FrottisCVAdmin(FrottisCV, self.site)
        expected_search = ('antecedents__patient__nom', 'antecedents__patient__prenom', 'resultat')
        self.assertEqual(admin.search_fields, expected_search)
    
    def test_frottis_admin_date_hierarchy(self):
        """Test configuration date_hierarchy de FrottisCVAdmin"""
        admin = FrottisCVAdmin(FrottisCV, self.site)
        self.assertEqual(admin.date_hierarchy, 'date_frottis')
    
    def test_frottis_admin_ordering(self):
        """Test configuration ordering de FrottisCVAdmin"""
        admin = FrottisCVAdmin(FrottisCV, self.site)
        self.assertEqual(admin.ordering, ('-date_frottis',))
    
    def test_frottis_admin_fields(self):
        """Test configuration fields de FrottisCVAdmin"""
        admin = FrottisCVAdmin(FrottisCV, self.site)
        expected_fields = ('antecedents', 'date_frottis', 'resultat')
        self.assertEqual(admin.fields, expected_fields)
    
    def test_frottis_admin_patient_nom_method(self):
        """Test méthode patient_nom personnalisée de FrottisCVAdmin"""
        admin = FrottisCVAdmin(FrottisCV, self.site)
        
        patient_nom = admin.patient_nom(self.frottis)
        expected_nom = self.patiente.nom_complet
        self.assertEqual(patient_nom, expected_nom)
        
        # Vérifier short_description et admin_order_field
        self.assertEqual(admin.patient_nom.short_description, 'Patiente')
        self.assertEqual(admin.patient_nom.admin_order_field, 'antecedents__patient__nom')
    
    def test_frottis_admin_resultat_court_method(self):
        """Test méthode resultat_court personnalisée de FrottisCVAdmin"""
        admin = FrottisCVAdmin(FrottisCV, self.site)
        
        # Test avec résultat court
        frottis_court = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2024, 5, 10),
            resultat="Normal"
        )
        
        resultat_court = admin.resultat_court(frottis_court)
        self.assertEqual(resultat_court, "Normal")
        
        # Test avec résultat long (troncature)
        resultat_long = admin.resultat_court(self.frottis)
        expected_truncated = self.frottis.resultat[:50] + "..."
        self.assertEqual(resultat_long, expected_truncated)
        
        # Vérifier short_description
        self.assertEqual(admin.resultat_court.short_description, 'Résultat')
    
    def test_frottis_model_verbose_names(self):
        """Test verbose_name et verbose_name_plural du modèle FrottisCV"""
        self.assertEqual(FrottisCV._meta.verbose_name, "6.1.1.1 Frottis cervico-vaginal")
        self.assertEqual(FrottisCV._meta.verbose_name_plural, "6.1.1.1 Frottis cervico-vaginaux")


class AntecedentsAdminIntegrationTest(TestCase):
    
    def setUp(self):
        """Configuration pour les tests d'intégration admin"""
        self.client = Client()
        
        # Créer superutilisateur
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@test.com',
            password='admin123'
        )
        
        self.client.login(email='admin@test.com', password='admin123')
        
        self.caisse = Caisse.objects.create(nom="CAFAT")
        
        self.patiente = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse
        )
        
        self.antecedents = Antecedents.objects.create(
            patient=self.patiente,
            taille=1.65,
            poids=60.0,
            medecin_traitant="Dr. Martin"
        )
    
    def test_admin_antecedents_changelist_access(self):
        """Test accès à la liste des antécédents dans l'admin"""
        url = reverse('admin:core_antecedents_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.patiente.nom_complet)
    
    def test_admin_antecedents_change_access(self):
        """Test accès à la modification d'antécédents dans l'admin"""
        url = reverse('admin:core_antecedents_change', args=[self.antecedents.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dr. Martin')
        self.assertContains(response, '1.65')
    
    def test_admin_antecedents_add_access(self):
        """Test accès à l'ajout d'antécédents dans l'admin"""
        url = reverse('admin:core_antecedents_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Patient')
        self.assertContains(response, 'Taille')
    
    def test_admin_frottis_changelist_access(self):
        """Test accès à la liste des frottis dans l'admin"""
        # Créer un frottis
        FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2024, 6, 15),
            resultat="Normal"
        )
        
        url = reverse('admin:core_frottiscv_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.patiente.nom_complet)
        self.assertContains(response, '15/06/2024')
    
    def test_admin_frottis_change_access(self):
        """Test accès à la modification d'un frottis dans l'admin"""
        frottis = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2024, 6, 15),
            resultat="Normal - Test admin"
        )
        
        url = reverse('admin:core_frottiscv_change', args=[frottis.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Normal - Test admin')
        self.assertContains(response, '2024-06-15')
    
    def test_admin_antecedents_search_functionality(self):
        """Test fonctionnalité de recherche dans l'admin antécédents"""
        url = reverse('admin:core_antecedents_changelist')
        
        # Recherche par nom de patient
        response = self.client.get(url, {'q': 'Dupont'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.patiente.nom_complet)
        
        # Recherche par médecin
        response = self.client.get(url, {'q': 'Martin'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dr. Martin')
    
    def test_admin_frottis_search_functionality(self):
        """Test fonctionnalité de recherche dans l'admin frottis"""
        frottis = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2024, 6, 15),
            resultat="Normal avec inflammation légère"
        )
        
        url = reverse('admin:core_frottiscv_changelist')
        
        # Recherche par nom de patient
        response = self.client.get(url, {'q': 'Dupont'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.patiente.nom_complet)
        
        # Recherche par résultat
        response = self.client.get(url, {'q': 'inflammation'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'inflammation')
    
    def test_admin_antecedents_filters(self):
        """Test filtres dans l'admin antécédents"""
        url = reverse('admin:core_antecedents_changelist')
        
        # Filtre par asthme=True
        response = self.client.get(url, {'asthme__exact': '1'})
        self.assertEqual(response.status_code, 200)
        
        # Filtre par diabète=False
        response = self.client.get(url, {'diabete__exact': '0'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.patiente.nom_complet)
    
    def test_admin_frottis_date_hierarchy(self):
        """Test hiérarchie de dates dans l'admin frottis"""
        FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2024, 6, 15),
            resultat="Normal"
        )
        
        url = reverse('admin:core_frottiscv_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # La hiérarchie de dates devrait être présente
        self.assertContains(response, '2024')
    
    def test_admin_antecedents_inline_frottis(self):
        """Test inline des frottis dans l'admin antécédents"""
        url = reverse('admin:core_antecedents_change', args=[self.antecedents.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier présence de l'inline des frottis
        self.assertContains(response, 'frottis-group')
        self.assertContains(response, 'Date du frottis')
        self.assertContains(response, 'Résultat')
    
    def test_admin_antecedents_save_functionality(self):
        """Test sauvegarde via l'admin antécédents"""
        url = reverse('admin:core_antecedents_change', args=[self.antecedents.pk])
        
        data = {
            'patient': self.patiente.pk,
            'taille': '1.70',
            'poids': '65.0',
            'medecin_traitant': 'Dr. Martin Modifié',
            'gynecologue': 'Dr. Nouveau',
            'asthme': True,
            'diabete': False,
            'hta': True,
            'epilepsie': False,
            'infection_urinaire': True,
            
            # Données pour l'inline des frottis
            'frottis-TOTAL_FORMS': '1',
            'frottis-INITIAL_FORMS': '0',
            'frottis-MIN_NUM_FORMS': '0',
            'frottis-MAX_NUM_FORMS': '1000',
            'frottis-0-date_frottis': '2024-06-15',
            'frottis-0-resultat': 'Normal - Test via admin',
        }
        
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que les modifications ont été sauvegardées
        self.antecedents.refresh_from_db()
        self.assertEqual(self.antecedents.taille, 1.70)
        self.assertEqual(self.antecedents.medecin_traitant, 'Dr. Martin Modifié')
        self.assertTrue(self.antecedents.asthme)
        
        # Vérifier que le frottis inline a été créé
        frottis = self.antecedents.frottis.first()
        self.assertIsNotNone(frottis)
        self.assertEqual(frottis.resultat, 'Normal - Test via admin')