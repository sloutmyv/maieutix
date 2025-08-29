"""
Tests d'intégration pour les templates des actes médicaux
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from bs4 import BeautifulSoup

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
        
        self.tarif_futur = TarifPeriode.objects.create(
            acte=self.acte_avec_tarif,
            cout_xpf=6000,
            date_debut=self.today + timedelta(days=30),
            date_fin=self.today + timedelta(days=60)
        )
        
        self.tarif_expire = TarifPeriode.objects.create(
            acte=self.acte_avec_tarif,
            cout_xpf=4000,
            date_debut=self.today - timedelta(days=60),
            date_fin=self.today - timedelta(days=31)
        )
        
        # Éviter la redirection vers changement de mot de passe
        self.user.must_change_password = False
        self.user.save()
        
        self.client.login(email='titulaire@test.com', password='testpass123')
    
    def test_actes_main_template_structure(self):
        """Test structure principale du template actes.html"""
        url = reverse('administration:administration_actes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Vérifier présence des éléments principaux
        self.assertIsNotNone(soup.find('h1'))
        self.assertIn('Administration - Actes', soup.find('h1').get_text())
        
        # Vérifier bouton d'ajout
        add_button = soup.find('button', {'hx-get': reverse('administration:acte_create')})
        self.assertIsNotNone(add_button)
        self.assertIn('Ajouter un acte', add_button.get_text())
        
        # Vérifier barre de recherche
        search_input = soup.find('input', {'name': 'search'})
        self.assertIsNotNone(search_input)
        self.assertEqual(search_input.get('placeholder'), 'Rechercher un acte...')
        
        # Vérifier présence du tableau
        table = soup.find('table')
        self.assertIsNotNone(table)
        
        # Vérifier les en-têtes de colonne
        headers = [th.get_text().strip() for th in soup.find_all('th')]
        expected_headers = ['Code', 'Libellé', 'Convention actuel', 'Actions']
        for header in expected_headers:
            self.assertIn(header, headers)
    
    def test_acte_table_content(self):
        """Test contenu du tableau des actes"""
        url = reverse('administration:administration_actes')
        response = self.client.get(url)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Vérifier présence des actes dans le tableau
        self.assertIn('CSF', response.content.decode())
        self.assertIn('VGC', response.content.decode())
        self.assertIn('Consultation Sage-Femme', response.content.decode())
        
        # Vérifier affichage des tarifs
        self.assertIn('5000 XPF', response.content.decode())  # Tarif actuel
        self.assertIn('Pas de tarif', response.content.decode())  # Acte sans tarif
        
        # Vérifier boutons d'action
        view_buttons = soup.find_all('button', {'title': 'Voir les détails et tarifs'})
        edit_buttons = soup.find_all('button', {'title': 'Modifier'})
        delete_buttons = soup.find_all('button', {'title': 'Supprimer'})
        
        self.assertEqual(len(view_buttons), 2)  # 2 actes
        self.assertEqual(len(edit_buttons), 2)
        self.assertEqual(len(delete_buttons), 2)
    
    def test_acte_detail_template_structure(self):
        """Test structure du template acte_detail.html"""
        url = reverse('administration:acte_detail', kwargs={'pk': self.acte_avec_tarif.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Vérifier titre modal
        title = soup.find('h3', {'id': 'modal-title'})
        self.assertIsNotNone(title)
        self.assertIn(f'Acte : {self.acte_avec_tarif.code}', title.get_text())
        
        # Vérifier informations de base
        self.assertIn(self.acte_avec_tarif.code, response.content.decode())
        self.assertIn(self.acte_avec_tarif.libelle, response.content.decode())
        self.assertIn('5000 XPF', response.content.decode())  # Tarif actuel
        
        # Vérifier tableau des conventions tarifaires
        table = soup.find('table')
        self.assertIsNotNone(table)
        
        # Vérifier en-têtes du tableau des tarifs
        headers = [th.get_text().strip() for th in soup.find_all('th')]
        expected_headers = ['Période', 'Convention (XPF)', 'Statut']
        for header in expected_headers:
            self.assertIn(header, headers)
        
        # Vérifier affichage des différents statuts
        self.assertIn('Actuel', response.content.decode())
        self.assertIn('Futur', response.content.decode())
        self.assertIn('Expiré', response.content.decode())
        
        # Vérifier bouton modifier (recherche par contenu textuel)
        all_buttons = soup.find_all('button')
        modify_button = next((btn for btn in all_buttons if 'Modifier' in btn.get_text()), None)
        self.assertIsNotNone(modify_button)
    
    def test_acte_form_template_structure_create(self):
        """Test structure du template acte_form.html en création"""
        url = reverse('administration:acte_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Vérifier titre modal
        title = soup.find('h3', {'id': 'modal-title'})
        self.assertIsNotNone(title)
        self.assertIn('Nouveau acte', title.get_text())
        
        # Vérifier présence du formulaire
        form = soup.find('form')
        self.assertIsNotNone(form)
        
        # Vérifier les champs du formulaire
        code_input = soup.find('input', {'name': 'code'})
        libelle_textarea = soup.find('textarea', {'name': 'libelle'})
        
        self.assertIsNotNone(code_input)
        self.assertIsNotNone(libelle_textarea)
        
        # Vérifier bouton de soumission
        submit_button = soup.find('button', {'type': 'submit'})
        self.assertIsNotNone(submit_button)
        self.assertIn('Créer', submit_button.get_text())
    
    def test_acte_form_template_structure_update(self):
        """Test structure du template acte_form.html en modification"""
        url = reverse('administration:acte_update', kwargs={'pk': self.acte_avec_tarif.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Vérifier titre modal
        title = soup.find('h3', {'id': 'modal-title'})
        self.assertIsNotNone(title)
        self.assertIn(f'Modifier l\'acte : {self.acte_avec_tarif.code}', title.get_text())
        
        # Vérifier que les champs sont pré-remplis
        code_input = soup.find('input', {'name': 'code'})
        libelle_textarea = soup.find('textarea', {'name': 'libelle'})
        
        self.assertEqual(code_input.get('value'), self.acte_avec_tarif.code)
        self.assertIn(self.acte_avec_tarif.libelle, libelle_textarea.get_text())
        
        # Vérifier section des conventions tarifaires (visible uniquement en modification)
        conventions_section = soup.find('h4', string=lambda text: text and 'Conventions tarifaires' in text)
        self.assertIsNotNone(conventions_section)
        
        # Vérifier bouton ajouter convention
        add_tarif_button = soup.find('button', {'onclick': lambda x: x and 'showAddTarifModal' in x})
        self.assertIsNotNone(add_tarif_button)
        self.assertIn('Ajouter convention', add_tarif_button.get_text())
        
        # Vérifier tableau des tarifs existants
        tarif_table = soup.find('table', class_='min-w-full divide-y divide-gray-300')
        self.assertIsNotNone(tarif_table)
        
        # Vérifier boutons d'action pour les tarifs
        edit_tarif_buttons = soup.find_all('button', {'onclick': lambda x: x and 'showEditTarifModal' in x})
        delete_tarif_buttons = soup.find_all('button', {'onclick': lambda x: x and 'deleteTarif' in x})
        
        self.assertEqual(len(edit_tarif_buttons), 3)  # 3 tarifs
        self.assertEqual(len(delete_tarif_buttons), 3)
        
        # Vérifier bouton de soumission
        submit_button = soup.find('button', {'type': 'submit'})
        self.assertIsNotNone(submit_button)
        self.assertIn('Modifier', submit_button.get_text())
    
    def test_acte_partial_table_template(self):
        """Test template partiel acte_table.html"""
        url = reverse('administration:acte_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Vérifier structure du tableau
        table = soup.find('table')
        self.assertIsNotNone(table)
        
        # Vérifier les en-têtes
        headers = [th.get_text().strip() for th in soup.find_all('th')]
        expected_headers = ['Code', 'Libellé', 'Convention actuel', 'Actions']
        for header in expected_headers:
            self.assertIn(header, headers)
        
        # Vérifier contenu des lignes
        rows = soup.find_all('tr')[1:]  # Exclure l'en-tête
        self.assertEqual(len(rows), 2)  # 2 actes
        
        # Vérifier le contenu de toutes les lignes
        all_rows_text = ' '.join(row.get_text() for row in rows)
        self.assertIn('CSF', all_rows_text)
        self.assertIn('VGC', all_rows_text)
        self.assertIn('5000 XPF', all_rows_text)
        self.assertIn('Pas de tarif', all_rows_text)
    
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
        
        # Test recherche sans résultat
        response = self.client.get(url, {'search': 'inexistant'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Aucun acte trouvé', response.content.decode())
    
    def test_navigation_integration(self):
        """Test intégration de la navigation"""
        # S'assurer que l'utilisateur peut accéder à l'administration
        self.user.is_superuser = True
        self.user.save()
        
        # Vérifier navigation dans base.html
        url = reverse('administration:administration_actes')
        response = self.client.get(url)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Vérifier menu Administration (recherche flexible)
        all_elements = soup.find_all(['button', 'a'])
        admin_menu = next((elem for elem in all_elements if 'Administration' in elem.get_text()), None)
        self.assertIsNotNone(admin_menu)
        
        # Vérifier lien vers actes dans le menu déroulant
        actes_link = soup.find('a', {'href': reverse('administration:administration_actes')})
        self.assertIsNotNone(actes_link)
        self.assertIn('Actes', actes_link.get_text())
    
    def test_modal_container_integration(self):
        """Test intégration du conteneur de modales"""
        url = reverse('administration:administration_actes')
        response = self.client.get(url)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Vérifier présence du conteneur modal
        modal_container = soup.find('div', {'id': 'modal-container'})
        self.assertIsNotNone(modal_container)
    
    def test_javascript_integration(self):
        """Test intégration du JavaScript dans les templates"""
        url = reverse('administration:acte_update', kwargs={'pk': self.acte_avec_tarif.pk})
        response = self.client.get(url)
        
        content = response.content.decode()
        
        # Vérifier présence des fonctions JavaScript
        self.assertIn('function showAddTarifModal', content)
        self.assertIn('function showEditTarifModal', content)
        self.assertIn('function closeSubModal', content)
        self.assertIn('function addTarif', content)
        self.assertIn('function editTarif', content)
        self.assertIn('function deleteTarif', content)
        
        # Vérifier URLs des API dans le JavaScript
        self.assertIn('/administration/actes/', content)
        self.assertIn('/administration/tarifs/', content)
    
    def test_css_classes_integration(self):
        """Test intégration des classes CSS"""
        url = reverse('administration:administration_actes')
        response = self.client.get(url)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Vérifier classes Tailwind principales
        self.assertIsNotNone(soup.find(class_='max-w-7xl'))  # Container principal
        self.assertIsNotNone(soup.find(class_='bg-gradient-to-r'))  # Header avec gradient
        self.assertIsNotNone(soup.find(class_='text-3xl'))  # Titre
        self.assertIsNotNone(soup.find(class_='card'))  # Carte pour le tableau
        
        # Vérifier classes de boutons
        buttons = soup.find_all('button')
        for button in buttons:
            classes = button.get('class', [])
            # Vérifier qu'au moins un bouton a les bonnes classes
            if 'inline-flex' in classes and 'items-center' in classes:
                break
        else:
            self.fail("Aucun bouton avec les classes Tailwind appropriées trouvé")
    
    def test_responsive_design_classes(self):
        """Test classes CSS pour le design responsive"""
        url = reverse('administration:administration_actes')
        response = self.client.get(url)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Vérifier classes responsive existantes
        self.assertIsNotNone(soup.find(class_='overflow-x-auto'))  # Tableau scrollable
        self.assertIsNotNone(soup.find(class_='max-w-7xl'))  # Container responsive
        self.assertIsNotNone(soup.find(class_='mx-auto'))  # Centrage responsive
    
    def test_accessibility_features(self):
        """Test fonctionnalités d'accessibilité"""
        url = reverse('administration:acte_detail', kwargs={'pk': self.acte_avec_tarif.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Vérifier attributs ARIA
        modal = soup.find('div', {'role': 'dialog'})
        self.assertIsNotNone(modal)
        self.assertEqual(modal.get('aria-modal'), 'true')
        
        # Vérifier labelledby
        labelledby = soup.find('div', {'aria-labelledby': 'modal-title'})
        self.assertIsNotNone(labelledby)
        
        # Vérifier qu'il y a des boutons (pas forcément avec title)
        buttons = soup.find_all('button')
        self.assertGreater(len(buttons), 0)
    
    def test_error_handling_display(self):
        """Test affichage des erreurs dans les templates"""
        # Test avec formulaire invalide
        url = reverse('administration:acte_create')
        data = {
            'code': '',  # Code vide pour générer une erreur
            'libelle': 'Test'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Ce champ est obligatoire', response.content.decode())
        
        soup = BeautifulSoup(response.content, 'html.parser')
        error_message = soup.find('p', class_='text-red-600')
        self.assertIsNotNone(error_message)