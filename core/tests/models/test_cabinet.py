from django.test import TestCase
from django.core.exceptions import ValidationError
from core.models import Cabinet


class CabinetModelTest(TestCase):
    """Tests for the Cabinet singleton model"""
    
    def setUp(self):
        """Set up test data"""
        # Clean up before each test
        pass
    
    def test_cabinet_creation(self):
        """Test creating a cabinet with valid data"""
        cabinet = Cabinet.objects.create(
            titre="Cabinet Test",
            rue="123 Rue de la Paix",
            code_postal="98800",
            ville="Nouméa",
            telephone="05 05 05 05 05",
            email="test@cabinet.nc"
        )
        
        self.assertEqual(cabinet.titre, "Cabinet Test")
        self.assertEqual(cabinet.rue, "123 Rue de la Paix")
        self.assertEqual(cabinet.code_postal, "98800")
        self.assertEqual(cabinet.ville, "Nouméa")
        self.assertEqual(cabinet.telephone, "05 05 05 05 05")
        self.assertEqual(cabinet.email, "test@cabinet.nc")
        self.assertIsNotNone(cabinet.created_at)
        self.assertIsNotNone(cabinet.updated_at)
    
    def test_cabinet_str_representation(self):
        """Test string representation of cabinet"""
        cabinet = Cabinet.objects.create(
            titre="Mon Cabinet",
            rue="456 Avenue",
            code_postal="98800",
            ville="Nouméa",
            telephone="05 05 05 05 05",
            email="contact@cabinet.nc"
        )
        self.assertEqual(str(cabinet), "Mon Cabinet")
    
    def test_singleton_pattern_creation(self):
        """Test that only one cabinet can be created"""
        # Create first cabinet
        Cabinet.objects.create(
            titre="Premier Cabinet",
            rue="123 Rue",
            code_postal="98800",
            ville="Nouméa",
            telephone="05 05 05 05 05",
            email="premier@cabinet.nc"
        )
        
        # Try to create second cabinet should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            cabinet2 = Cabinet(
                titre="Deuxième Cabinet",
                rue="456 Avenue",
                code_postal="98800",
                ville="Nouméa",
                telephone="05 05 05 05 06",
                email="deuxieme@cabinet.nc"
            )
            cabinet2.save()
        
        self.assertIn("Il ne peut y avoir qu'un seul cabinet.", str(context.exception))
        # Verify only one cabinet exists
        self.assertEqual(Cabinet.objects.count(), 1)
    
    def test_cabinet_update_allowed(self):
        """Test that updating existing cabinet is allowed"""
        cabinet = Cabinet.objects.create(
            titre="Cabinet Original",
            rue="123 Rue",
            code_postal="98800",
            ville="Nouméa",
            telephone="05 05 05 05 05",
            email="original@cabinet.nc"
        )
        
        # Update cabinet
        cabinet.titre = "Cabinet Modifié"
        cabinet.email = "modifie@cabinet.nc"
        cabinet.save()  # Should not raise exception
        
        # Refresh from database
        cabinet.refresh_from_db()
        self.assertEqual(cabinet.titre, "Cabinet Modifié")
        self.assertEqual(cabinet.email, "modifie@cabinet.nc")
        # Still only one cabinet
        self.assertEqual(Cabinet.objects.count(), 1)
    
    def test_cabinet_deletion_prevented(self):
        """Test that cabinet deletion is prevented"""
        cabinet = Cabinet.objects.create(
            titre="Cabinet à Supprimer",
            rue="123 Rue",
            code_postal="98800",
            ville="Nouméa",
            telephone="05 05 05 05 05",
            email="supprimer@cabinet.nc"
        )
        
        # Try to delete should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            cabinet.delete()
        
        self.assertIn("Le cabinet ne peut pas être supprimé.", str(context.exception))
        # Verify cabinet still exists
        self.assertEqual(Cabinet.objects.count(), 1)
    
    def test_get_instance_creates_cabinet(self):
        """Test get_instance method creates cabinet if none exists"""
        # No cabinet exists
        self.assertEqual(Cabinet.objects.count(), 0)
        
        # Get instance should create one
        cabinet = Cabinet.get_instance()
        
        self.assertIsNotNone(cabinet)
        self.assertEqual(cabinet.titre, "Mon Cabinet")
        self.assertEqual(Cabinet.objects.count(), 1)
    
    def test_get_instance_returns_existing(self):
        """Test get_instance method returns existing cabinet"""
        # Create cabinet first
        existing_cabinet = Cabinet.objects.create(
            titre="Cabinet Existant",
            rue="123 Rue",
            code_postal="98800",
            ville="Nouméa",
            telephone="05 05 05 05 05",
            email="existant@cabinet.nc"
        )
        
        # Get instance should return existing one
        cabinet = Cabinet.get_instance()
        
        self.assertEqual(cabinet.id, existing_cabinet.id)
        self.assertEqual(cabinet.titre, "Cabinet Existant")
        self.assertEqual(Cabinet.objects.count(), 1)
    
    def test_cabinet_required_fields(self):
        """Test cabinet with empty required fields"""
        cabinet = Cabinet.objects.create(
            titre="",
            rue="",
            code_postal="",
            ville="",
            telephone="",
            email="test@example.com"  # Email is required by EmailField
        )
        
        # Should be able to create with empty fields (except email)
        self.assertEqual(cabinet.titre, "")
        self.assertEqual(cabinet.rue, "")
    
    def test_cabinet_meta_configuration(self):
        """Test model meta configuration"""
        self.assertEqual(Cabinet._meta.verbose_name, "1. Cabinet")
        self.assertEqual(Cabinet._meta.verbose_name_plural, "1. Cabinet")
        self.assertEqual(Cabinet._meta.ordering, ['titre'])