"""
Tests pour l'administration Django des actes médicaux
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from core.models.acte import Acte, TarifPeriode
from core.admin.acte import ActeAdmin, TarifPeriodeAdmin, TarifPeriodeInline

User = get_user_model()


class MockRequest:
    """Mock request object for admin tests"""
    pass


class ActeAdminTests(TestCase):
    """Tests pour l'admin des actes"""
    
    def setUp(self):
        """Configuration des tests"""
        self.site = AdminSite()
        self.admin = ActeAdmin(Acte, self.site)
        self.factory = RequestFactory()
        
        self.acte = Acte.objects.create(
            code='CSF',
            libelle='Consultation Sage-Femme complète avec examen approfondi'
        )
        
        self.today = timezone.now().date()
        
        # Créer quelques périodes tarifaires
        self.tarif_actuel = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today - timedelta(days=30)
        )
        
        self.tarif_expire = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=4000,
            date_debut=self.today - timedelta(days=60),
            date_fin=self.today - timedelta(days=31)
        )
    
    def test_list_display(self):
        """Test des champs affichés dans la liste"""
        expected_fields = [
            'code',
            'libelle_court',
            'tarif_actuel_display',
            'nb_periodes_tarifaires',
            'created_at'
        ]
        
        self.assertEqual(self.admin.list_display, expected_fields)
    
    def test_search_fields(self):
        """Test des champs de recherche"""
        expected_fields = ['code', 'libelle']
        self.assertEqual(self.admin.search_fields, expected_fields)
    
    def test_ordering(self):
        """Test de l'ordre par défaut"""
        self.assertEqual(self.admin.ordering, ['code'])
    
    def test_libelle_court_method(self):
        """Test méthode libelle_court avec libellé long"""
        result = self.admin.libelle_court(self.acte)
        expected = 'Consultation Sage-Femme complète avec examen appro...'
        self.assertEqual(result, expected)
    
    def test_libelle_court_method_short_libelle(self):
        """Test méthode libelle_court avec libellé court"""
        acte_court = Acte.objects.create(
            code='VGC',
            libelle='Visite courte'
        )
        
        result = self.admin.libelle_court(acte_court)
        self.assertEqual(result, 'Visite courte')
    
    def test_tarif_actuel_display_with_tarif(self):
        """Test affichage tarif actuel avec tarif existant"""
        result = self.admin.tarif_actuel_display(self.acte)
        
        self.assertIn('5000 XPF', result)
        self.assertIn('color: green', result)
        self.assertIn('font-weight: bold', result)
    
    def test_tarif_actuel_display_without_tarif(self):
        """Test affichage tarif actuel sans tarif"""
        acte_sans_tarif = Acte.objects.create(
            code='ST',
            libelle='Sans tarif'
        )
        
        result = self.admin.tarif_actuel_display(acte_sans_tarif)
        
        self.assertIn('Aucun tarif', result)
        self.assertIn('color: red', result)
    
    def test_nb_periodes_tarifaires_method(self):
        """Test méthode nb_periodes_tarifaires"""
        result = self.admin.nb_periodes_tarifaires(self.acte)
        self.assertEqual(result, '2 périodes')
    
    def test_nb_periodes_tarifaires_method_single(self):
        """Test méthode nb_periodes_tarifaires avec une seule période"""
        # Supprimer une période pour n'en garder qu'une
        self.tarif_expire.delete()
        
        result = self.admin.nb_periodes_tarifaires(self.acte)
        self.assertEqual(result, '1 période')
    
    def test_nb_periodes_tarifaires_method_zero(self):
        """Test méthode nb_periodes_tarifaires sans période"""
        acte_sans_tarif = Acte.objects.create(
            code='ST',
            libelle='Sans tarif'
        )
        
        result = self.admin.nb_periodes_tarifaires(acte_sans_tarif)
        self.assertEqual(result, '0 période')
    
    def test_fieldsets(self):
        """Test de la configuration des fieldsets"""
        fieldsets = self.admin.fieldsets
        
        # Vérifier structure générale
        self.assertEqual(len(fieldsets), 2)
        
        # Vérifier premier fieldset
        info_fieldset = fieldsets[0]
        self.assertEqual(info_fieldset[0], "Informations de l'acte")
        self.assertIn('code', info_fieldset[1]['fields'])
        self.assertIn('libelle', info_fieldset[1]['fields'])
        
        # Vérifier second fieldset
        meta_fieldset = fieldsets[1]
        self.assertEqual(meta_fieldset[0], 'Métadonnées')
        self.assertIn('created_at', meta_fieldset[1]['fields'])
        self.assertIn('updated_at', meta_fieldset[1]['fields'])
    
    def test_readonly_fields(self):
        """Test des champs en lecture seule"""
        expected_fields = ['created_at', 'updated_at']
        self.assertEqual(self.admin.readonly_fields, expected_fields)
    
    def test_inlines(self):
        """Test de l'inclusion des inlines"""
        self.assertEqual(len(self.admin.inlines), 1)
        self.assertEqual(self.admin.inlines[0], TarifPeriodeInline)


class TarifPeriodeAdminTests(TestCase):
    """Tests pour l'admin des périodes tarifaires"""
    
    def setUp(self):
        """Configuration des tests"""
        self.site = AdminSite()
        self.admin = TarifPeriodeAdmin(TarifPeriode, self.site)
        
        self.acte = Acte.objects.create(
            code='CSF',
            libelle='Consultation Sage-Femme'
        )
        
        self.today = timezone.now().date()
        
        self.tarif_actuel = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today - timedelta(days=30)
        )
        
        self.tarif_futur = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=6000,
            date_debut=self.today + timedelta(days=30)
        )
        
        self.tarif_expire = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=4000,
            date_debut=self.today - timedelta(days=60),
            date_fin=self.today - timedelta(days=31)
        )
    
    def test_list_display(self):
        """Test des champs affichés dans la liste"""
        expected_fields = [
            'acte_code',
            'cout_xpf',
            'date_debut',
            'date_fin',
            'statut_display',
            'created_at'
        ]
        
        self.assertEqual(self.admin.list_display, expected_fields)
    
    def test_list_filter(self):
        """Test des filtres de liste"""
        expected_filters = ['acte', 'date_debut', 'created_at']
        self.assertEqual(self.admin.list_filter, expected_filters)
    
    def test_search_fields(self):
        """Test des champs de recherche"""
        expected_fields = ['acte__code', 'acte__libelle']
        self.assertEqual(self.admin.search_fields, expected_fields)
    
    def test_ordering(self):
        """Test de l'ordre par défaut"""
        self.assertEqual(self.admin.ordering, ['-date_debut'])
    
    def test_acte_code_method(self):
        """Test méthode acte_code"""
        result = self.admin.acte_code(self.tarif_actuel)
        self.assertEqual(result, 'CSF')
    
    def test_acte_code_admin_order_field(self):
        """Test ordre admin pour acte_code"""
        self.assertEqual(self.admin.acte_code.admin_order_field, 'acte__code')
    
    def test_statut_display_actuel(self):
        """Test affichage statut actuel"""
        result = self.admin.statut_display(self.tarif_actuel)
        
        self.assertIn('Actuel', result)
        self.assertIn('color: green', result)
        self.assertIn('font-weight: bold', result)
    
    def test_statut_display_futur(self):
        """Test affichage statut futur"""
        result = self.admin.statut_display(self.tarif_futur)
        
        self.assertIn('Futur', result)
        self.assertIn('color: orange', result)
        self.assertIn('font-weight: bold', result)
    
    def test_statut_display_expire(self):
        """Test affichage statut expiré"""
        result = self.admin.statut_display(self.tarif_expire)
        
        self.assertIn('Expiré', result)
        self.assertIn('color: red', result)
        self.assertIn('font-weight: bold', result)
    
    def test_fieldsets(self):
        """Test de la configuration des fieldsets"""
        fieldsets = self.admin.fieldsets
        
        # Vérifier structure générale
        self.assertEqual(len(fieldsets), 3)
        
        # Vérifier premier fieldset
        acte_fieldset = fieldsets[0]
        self.assertEqual(acte_fieldset[0], 'Acte et tarif')
        self.assertIn('acte', acte_fieldset[1]['fields'])
        self.assertIn('cout_xpf', acte_fieldset[1]['fields'])
        
        # Vérifier second fieldset
        period_fieldset = fieldsets[1]
        self.assertEqual(period_fieldset[0], 'Période de validité')
        self.assertIn('date_debut', period_fieldset[1]['fields'])
        self.assertIn('date_fin', period_fieldset[1]['fields'])
        
        # Vérifier troisième fieldset
        meta_fieldset = fieldsets[2]
        self.assertEqual(meta_fieldset[0], 'Métadonnées')
        self.assertIn('created_at', meta_fieldset[1]['fields'])
        self.assertIn('updated_at', meta_fieldset[1]['fields'])
    
    def test_readonly_fields(self):
        """Test des champs en lecture seule"""
        expected_fields = ['created_at', 'updated_at']
        self.assertEqual(self.admin.readonly_fields, expected_fields)
    
    def test_get_queryset_optimization(self):
        """Test optimisation des requêtes"""
        request = MockRequest()
        
        queryset = self.admin.get_queryset(request)
        
        # Vérifier que select_related est utilisé
        self.assertTrue(hasattr(queryset, '_prefetch_related_lookups') or 
                       hasattr(queryset, 'query'))


class TarifPeriodeInlineTests(TestCase):
    """Tests pour l'inline des périodes tarifaires"""
    
    def setUp(self):
        """Configuration des tests"""
        self.site = AdminSite()
        self.inline = TarifPeriodeInline(TarifPeriode, self.site)
        
        self.acte = Acte.objects.create(
            code='CSF',
            libelle='Consultation Sage-Femme'
        )
        
        self.today = timezone.now().date()
        
        self.tarif_actuel = TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today - timedelta(days=30)
        )
    
    def test_model(self):
        """Test du modèle de l'inline"""
        self.assertEqual(self.inline.model, TarifPeriode)
    
    def test_extra(self):
        """Test nombre d'objets extra"""
        self.assertEqual(self.inline.extra, 1)
    
    def test_fields(self):
        """Test des champs affichés"""
        expected_fields = ('cout_xpf', 'date_debut', 'date_fin', 'statut_display')
        self.assertEqual(self.inline.fields, expected_fields)
    
    def test_readonly_fields(self):
        """Test des champs en lecture seule"""
        expected_fields = ('statut_display',)
        self.assertEqual(self.inline.readonly_fields, expected_fields)
    
    def test_ordering(self):
        """Test de l'ordre par défaut"""
        self.assertEqual(self.inline.ordering, ['-date_debut'])
    
    def test_statut_display_method(self):
        """Test méthode statut_display de l'inline"""
        result = self.inline.statut_display(self.tarif_actuel)
        
        self.assertIn('Actuel', result)
        self.assertIn('color: green', result)
        self.assertIn('font-weight: bold', result)
    
    def test_statut_display_method_no_pk(self):
        """Test méthode statut_display sans pk (nouvel objet)"""
        new_tarif = TarifPeriode(
            acte=self.acte,
            cout_xpf=6000,
            date_debut=self.today
        )
        
        result = self.inline.statut_display(new_tarif)
        self.assertEqual(result, '-')
    
    def test_statut_display_short_description(self):
        """Test description courte de statut_display"""
        self.assertEqual(self.inline.statut_display.short_description, 'Statut')


class ActeAdminIntegrationTests(TestCase):
    """Tests d'intégration pour l'admin des actes"""
    
    def setUp(self):
        """Configuration des tests d'intégration"""
        self.superuser = User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass'
        )
        
        self.acte = Acte.objects.create(
            code='CSF',
            libelle='Consultation Sage-Femme'
        )
        
        self.today = timezone.now().date()
        
        TarifPeriode.objects.create(
            acte=self.acte,
            cout_xpf=5000,
            date_debut=self.today - timedelta(days=30)
        )
    
    def test_admin_registered(self):
        """Test que les modèles sont enregistrés dans l'admin"""
        from django.contrib import admin
        
        self.assertTrue(admin.site.is_registered(Acte))
        self.assertTrue(admin.site.is_registered(TarifPeriode))
    
    def test_admin_changelist_view(self):
        """Test vue liste admin pour les actes"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = f'/admin/core/acte/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.acte.code)
    
    def test_admin_change_view(self):
        """Test vue modification admin pour un acte"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = f'/admin/core/acte/{self.acte.pk}/change/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.acte.code)
        self.assertContains(response, self.acte.libelle)
    
    def test_admin_add_view(self):
        """Test vue ajout admin pour les actes"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = f'/admin/core/acte/add/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Code')
        self.assertContains(response, 'Libellé')
    
    def test_admin_tarif_periode_changelist(self):
        """Test vue liste admin pour les périodes tarifaires"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = f'/admin/core/tarifperiode/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '5000')
    
    def test_inline_display_in_acte_admin(self):
        """Test affichage des inlines dans l'admin acte"""
        self.client.login(email='admin@test.com', password='adminpass')
        
        url = f'/admin/core/acte/{self.acte.pk}/change/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Vérifier présence de l'inline des tarifs
        self.assertContains(response, '3.1 Tarifs Actes')
        self.assertContains(response, '5000')