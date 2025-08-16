from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from core.models import Cabinet
from core.admin import CabinetAdmin


class CabinetAdminTest(TestCase):
    """Tests for the Cabinet admin interface"""
    
    def setUp(self):
        """Set up test data"""
        # Clean up before each test
        pass
        
        # Create admin site and admin instance
        self.site = AdminSite()
        self.admin = CabinetAdmin(Cabinet, self.site)
        
        # Create request factory
        self.factory = RequestFactory()
        
        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
    
    def test_has_add_permission_no_cabinet(self):
        """Test add permission when no cabinet exists"""
        request = self.factory.get('/admin/core/cabinet/')
        request.user = self.superuser
        
        # Should have add permission when no cabinet exists
        self.assertTrue(self.admin.has_add_permission(request))
    
    def test_has_add_permission_cabinet_exists(self):
        """Test add permission when cabinet already exists"""
        # Create cabinet
        Cabinet.objects.create(
            titre="Cabinet Test",
            rue="123 Rue",
            code_postal="98800",
            ville="Nouméa",
            telephone="05 05 05 05 05",
            email="test@cabinet.nc"
        )
        
        request = self.factory.get('/admin/core/cabinet/')
        request.user = self.superuser
        
        # Should not have add permission when cabinet exists
        self.assertFalse(self.admin.has_add_permission(request))
    
    def test_has_delete_permission_always_false(self):
        """Test delete permission is always False"""
        request = self.factory.get('/admin/core/cabinet/')
        request.user = self.superuser
        
        # Should never have delete permission
        self.assertFalse(self.admin.has_delete_permission(request))
        
        # Even with object
        cabinet = Cabinet.objects.create(
            titre="Cabinet Test",
            rue="123 Rue",
            code_postal="98800",
            ville="Nouméa",
            telephone="05 05 05 05 05",
            email="test@cabinet.nc"
        )
        self.assertFalse(self.admin.has_delete_permission(request, cabinet))
    
    def test_changelist_view_no_cabinet(self):
        """Test changelist view redirects to add when no cabinet exists"""
        request = self.factory.get('/admin/core/cabinet/')
        request.user = self.superuser
        
        response = self.admin.changelist_view(request)
        
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.url.endswith('/cabinet/add/'))
    
    def test_changelist_view_cabinet_exists(self):
        """Test changelist view redirects to change when cabinet exists"""
        cabinet = Cabinet.objects.create(
            titre="Cabinet Test",
            rue="123 Rue",
            code_postal="98800",
            ville="Nouméa",
            telephone="05 05 05 05 05",
            email="test@cabinet.nc"
        )
        
        request = self.factory.get('/admin/core/cabinet/')
        request.user = self.superuser
        
        response = self.admin.changelist_view(request)
        
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.url.endswith(f'/cabinet/{cabinet.id}/change/'))
    
    def test_response_add_redirect(self):
        """Test response after adding cabinet redirects to change view"""
        cabinet = Cabinet.objects.create(
            titre="Cabinet Test",
            rue="123 Rue",
            code_postal="98800",
            ville="Nouméa",
            telephone="05 05 05 05 05",
            email="test@cabinet.nc"
        )
        
        request = self.factory.post('/admin/core/cabinet/add/')
        request.user = self.superuser
        
        response = self.admin.response_add(request, cabinet)
        
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.url.endswith(f'/cabinet/{cabinet.id}/change/'))
    
    def test_response_change_stays_on_page(self):
        """Test response after changing cabinet stays on same page"""
        cabinet = Cabinet.objects.create(
            titre="Cabinet Test",
            rue="123 Rue",
            code_postal="98800",
            ville="Nouméa",
            telephone="05 05 05 05 05",
            email="test@cabinet.nc"
        )
        
        request = self.factory.post(f'/admin/core/cabinet/{cabinet.id}/change/')
        request.user = self.superuser
        
        response = self.admin.response_change(request, cabinet)
        
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, '.')
    
    def test_admin_configuration(self):
        """Test admin configuration settings"""
        expected_list_display = ['titre', 'ville', 'telephone', 'email', 'updated_at']
        expected_search_fields = ['titre', 'ville', 'telephone', 'email']
        expected_ordering = ['titre']
        
        self.assertEqual(self.admin.list_display, expected_list_display)
        self.assertEqual(self.admin.search_fields, expected_search_fields)
        self.assertEqual(self.admin.ordering, expected_ordering)
        
        # Test fieldsets structure
        self.assertIsNotNone(self.admin.fieldsets)
        self.assertEqual(len(self.admin.fieldsets), 3)
        
        # Check fieldset names
        fieldset_names = [fieldset[0] for fieldset in self.admin.fieldsets]
        expected_names = ['Informations générales', 'Adresse', 'Contact']
        self.assertEqual(fieldset_names, expected_names)