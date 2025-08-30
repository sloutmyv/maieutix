"""
Tests d'intégration pour les templates des actes médicaux
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from core.models.acte import Acte, TarifPeriode
from core.models.sagefemme import SageFemme

User = get_user_model()


class ActeTemplatesIntegrationTests(TestCase):
    """Tests d'intégration pour les templates des actes"""
    
    def setUp(self):
        """Configuration des tests"""
        self.client = Client()
        
        # Créer un utilisateur sage-femme titulaire
        self.user = User.objects.create_user(
            email='titulaire@test.com',
            password='testpass123'
        )
        
        self.sagefemme = SageFemme.objects.create(
            user=self.user,
            nom='Test',
            prenom='Sage-femme',
            titre='Sage-femme',
            telephone='123456789',
            email='titulaire@test.com',
            rue='123 rue Test',
            code_postal='98800',
            ville='Nouméa',
            numero_cafat='123456',
            ridet='123456789',
            rib='123456789012',
            banque='Test Bank',
            situation='titulaire',
            is_active=True
        )
        
        # Créer des actes de test
        self.acte_avec_tarif = Acte.objects.create(
            code='CSF',
            libelle='Consultation Sage-Femme'
        )
        
        self.acte_sans_tarif = Acte.objects.create(
            code='VGC',
            libelle='Visite gynécologique complète'
        )
        
        self.today = timezone.now().date()
        
        # Créer des tarifs de test
        self.tarif_actuel = TarifPeriode.objects.create(
            acte=self.acte_avec_tarif,
            cout_xpf=5000,
            date_debut=self.today - timedelta(days=30)
        )
        
        # Éviter la redirection vers changement de mot de passe
        self.user.must_change_password = False
        self.user.save()
        
        self.client.login(email='titulaire@test.com', password='testpass123')
    
    def test_actes_main_template_basic_functionality(self):
        """Test fonctionnalité de base du template actes.html"""
        url = reverse('administration:administration_actes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que les actes sont affichés
        content = response.content.decode()
        self.assertIn('CSF', content)
        self.assertIn('VGC', content)
        self.assertIn('Consultation Sage-Femme', content)
        
        # Vérifier présence d'éléments fonctionnels
        self.assertIn('Ajouter', content)
        self.assertIn('Rechercher', content)
    
    def test_acte_detail_basic_functionality(self):
        """Test fonctionnalité de base du template acte_detail.html"""
        url = reverse('administration:acte_detail', kwargs={'pk': self.acte_avec_tarif.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode()
        # Vérifier informations de base
        self.assertIn(self.acte_avec_tarif.code, content)
        self.assertIn(self.acte_avec_tarif.libelle, content)
        self.assertIn('5000 XPF', content)  # Tarif actuel
    
    def test_acte_form_basic_functionality_create(self):
        """Test fonctionnalité de base du formulaire de création"""
        url = reverse('administration:acte_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode()
        # Vérifier présence des champs du formulaire
        self.assertIn('name="code"', content)
        self.assertIn('name="libelle"', content)
        self.assertIn('Ajouter', content)
    
    def test_acte_form_basic_functionality_update(self):
        """Test fonctionnalité de base du formulaire de modification"""
        url = reverse('administration:acte_update', kwargs={'pk': self.acte_avec_tarif.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode()
        # Vérifier que les données sont pré-remplies
        self.assertIn(self.acte_avec_tarif.code, content)
        self.assertIn(self.acte_avec_tarif.libelle, content)
        self.assertIn('Modifier', content)
    
    def test_search_functionality_integration(self):
        """Test intégration de la fonctionnalité de recherche"""
        url = reverse('administration:acte_list')
        
        # Test recherche par code
        response = self.client.get(url, {'search': 'CSF'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('CSF', response.content.decode())
        self.assertNotIn('VGC', response.content.decode())
        
        # Test recherche par libellé
        response = self.client.get(url, {'search': 'gynécologique'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('VGC', response.content.decode())
        self.assertNotIn('CSF', response.content.decode())
    
    def test_error_handling_basic(self):
        """Test gestion d'erreur de base dans les templates"""
        # Test avec formulaire invalide
        url = reverse('administration:acte_create')
        data = {
            'code': '',  # Code vide pour générer une erreur
            'libelle': 'Test'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('obligatoire', response.content.decode())