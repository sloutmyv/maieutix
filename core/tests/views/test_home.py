from django.test import TestCase, Client


class HomeViewTest(TestCase):
    """Tests for the home view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
    
    def test_home_view_get(self):
        """Test GET request to home view"""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello World')
        self.assertContains(response, 'Bienvenue sur Maieutix')
    
    def test_home_view_template_used(self):
        """Test that correct template is used"""
        response = self.client.get('/')
        
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertTemplateUsed(response, 'core/base.html')
    
    def test_home_view_context(self):
        """Test home view context data"""
        response = self.client.get('/')
        
        # Check that page loads without errors
        self.assertEqual(response.status_code, 200)
        
        # Check HTML content includes our frontend stack
        self.assertContains(response, 'tailwind')  # Tailwind CSS
        self.assertContains(response, 'htmx')      # HTMX
        self.assertContains(response, 'alpine')    # Alpine.js
    
    def test_home_view_navigation_links(self):
        """Test navigation links are present"""
        response = self.client.get('/')
        
        self.assertContains(response, 'href="/"')         # Home link
        self.assertContains(response, 'href="/admin/"')   # Admin link
    
    def test_home_view_responsive_design(self):
        """Test responsive design elements are present"""
        response = self.client.get('/')
        
        # Check for responsive grid classes
        self.assertContains(response, 'md:grid-cols-3')
        self.assertContains(response, 'max-w-7xl')
    
    def test_home_view_color_theme(self):
        """Test color theme is applied"""
        response = self.client.get('/')
        
        # Check custom CSS is loaded
        self.assertContains(response, 'core/css/custom.css')
        
        # Check theme colors are used
        self.assertContains(response, 'text-primary')
        self.assertContains(response, 'bg-primary')