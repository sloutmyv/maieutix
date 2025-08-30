"""
Tests pour les vues d'administration des sage-femmes.
"""
from django.test import TestCase, Client
from django.urls import reverse
from authentication.models import SageFemmeUser
import json
from datetime import date, timedelta
from core.models.sagefemme import SageFemme
from core.models.periode_activite import PeriodeActivite


class BaseAdministrationTest(TestCase):
    """Classe de base pour les tests d'administration"""
    
    def setUp(self):
        """Configuration de base pour tous les tests"""
        self.client = Client()
        
        # Créer un superutilisateur pour les tests
        self.superuser = SageFemmeUser.objects.create_superuser(
            email='admin@test.nc',
            password='testpass123'
        )
        
        # Données de base pour créer une sage-femme
        self.sage_femme_data = {
            'nom': 'Dupont',
            'prenom': 'Marie',
            'titre': 'Sage-femme libérale',
            'telephone': '98.12.34.56',
            'email': 'marie.dupont@test.nc',
            'rue': '123 Rue de la Paix',
            'code_postal': '98800',
            'ville': 'Nouméa',
            'numero_cafat': '123456789',
            'ridet': '0123456.001',
            'rib': 'FR76 3000 3000 1234 5678 9012 345',
            'banque': 'BCI',
            'situation': 'titulaire'
        }
        
        self.today = date.today()


class AdministrationSagesFemmesViewTest(BaseAdministrationTest):
    """Tests pour la vue principale des sage-femmes"""
    
    def test_vue_sages_femmes_sans_authentification(self):
        """Test d'accès à la vue sans authentification"""
        url = reverse('administration:administration_sages_femmes')
        response = self.client.get(url)
        
        # Devrait rediriger vers la page de connexion
        self.assertEqual(response.status_code, 302)
    
    def test_vue_sages_femmes_avec_superuser(self):
        """Test d'accès à la vue avec superutilisateur"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:administration_sages_femmes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Administration - Sages Femmes')
    
    def test_vue_sages_femmes_contexte(self):
        """Test du contexte de la vue principale"""
        # Créer quelques sage-femmes
        sage_femme1 = SageFemme.objects.create(**self.sage_femme_data)
        
        data2 = self.sage_femme_data.copy()
        data2.update({
            'nom': 'Martin',
            'prenom': 'Julie',
            'email': 'julie.martin@test.nc',
            'numero_cafat': '987654321',
            'ridet': '0987654.001'
        })
        sage_femme2 = SageFemme.objects.create(**data2)
        
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:administration_sages_femmes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('sagefemmes', response.context)
        self.assertEqual(len(response.context['sagefemmes']), 2)
        self.assertIn('page_title', response.context)
        self.assertEqual(response.context['section'], 'administration')


class SageFemmeListViewTest(BaseAdministrationTest):
    """Tests pour la vue de liste HTMX des sage-femmes"""
    
    def setUp(self):
        super().setUp()
        
        # Créer des sage-femmes de test
        self.sage_femme1 = SageFemme.objects.create(**self.sage_femme_data)
        
        data2 = self.sage_femme_data.copy()
        data2.update({
            'nom': 'Martin',
            'prenom': 'Julie',
            'email': 'julie.martin@test.nc',
            'numero_cafat': '987654321',
            'ridet': '0987654.001',
            'situation': 'collaborateur'
        })
        self.sage_femme2 = SageFemme.objects.create(**data2)
    
    def test_liste_sage_femmes_get(self):
        """Test de récupération de la liste des sage-femmes"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.sage_femme1.nom_complet)
        self.assertContains(response, self.sage_femme2.nom_complet)
    
    def test_recherche_par_nom(self):
        """Test de recherche par nom"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_list')
        response = self.client.get(url, {'search': 'Dupont'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.sage_femme1.nom_complet)
        self.assertNotContains(response, self.sage_femme2.nom_complet)
    
    def test_recherche_par_prenom(self):
        """Test de recherche par prénom"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_list')
        response = self.client.get(url, {'search': 'Julie'})
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.sage_femme1.nom_complet)
        self.assertContains(response, self.sage_femme2.nom_complet)
    
    def test_recherche_par_email(self):
        """Test de recherche par email"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_list')
        response = self.client.get(url, {'search': 'julie.martin'})
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.sage_femme1.nom_complet)
        self.assertContains(response, self.sage_femme2.nom_complet)
    
    def test_filtre_par_situation(self):
        """Test de filtrage par situation"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_list')
        response = self.client.get(url, {'situation': 'titulaire'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.sage_femme1.nom_complet)
        self.assertNotContains(response, self.sage_femme2.nom_complet)


class SageFemmeCreateViewTest(BaseAdministrationTest):
    """Tests pour la création de sage-femmes"""
    
    def test_get_formulaire_creation(self):
        """Test d'affichage du formulaire de création"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ajouter une sage-femme')
        self.assertContains(response, 'form')
    
    def test_creation_sage_femme_valide(self):
        """Test de création d'une sage-femme avec des données valides"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_create')
        response = self.client.post(url, self.sage_femme_data)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la sage-femme a été créée
        self.assertTrue(SageFemme.objects.filter(email='marie.dupont@test.nc').exists())
        
        # Vérifier qu'une période d'activité a été créée automatiquement
        sage_femme = SageFemme.objects.get(email='marie.dupont@test.nc')
        self.assertEqual(sage_femme.periodes_activite.count(), 1)
        
        # Vérifier la réponse HTMX
        content = response.content.decode()
        self.assertIn('window.showNotification', content)
        self.assertIn('créée avec succès', content)
    
    def test_creation_sage_femme_donnees_invalides(self):
        """Test de création avec des données invalides"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_create')
        
        # Données invalides (email manquant)
        data = self.sage_femme_data.copy()
        del data['email']
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la sage-femme n'a pas été créée
        self.assertFalse(SageFemme.objects.filter(nom='Dupont').exists())
        
        # Vérifier que le formulaire est renvoyé avec des erreurs
        self.assertContains(response, 'form')
    
    def test_creation_remplacant_avec_remplacement_de(self):
        """Test de création d'un remplaçant"""
        # Créer d'abord un titulaire
        titulaire = SageFemme.objects.create(**self.sage_femme_data)
        
        # Données pour le remplaçant
        data = self.sage_femme_data.copy()
        data.update({
            'nom': 'Remplacant',
            'prenom': 'Sophie',
            'email': 'sophie.remplacant@test.nc',
            'numero_cafat': '555666777',
            'ridet': '0555666.001',
            'situation': 'remplacant',
            'remplacement_de': titulaire.pk
        })
        
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_create')
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que le remplaçant a été créé
        remplacant = SageFemme.objects.get(email='sophie.remplacant@test.nc')
        self.assertEqual(remplacant.situation, 'remplacant')
        self.assertEqual(remplacant.remplacement_de, titulaire)


class SageFemmeUpdateViewTest(BaseAdministrationTest):
    """Tests pour la modification de sage-femmes"""
    
    def setUp(self):
        super().setUp()
        self.sage_femme = SageFemme.objects.create(**self.sage_femme_data)
        
        # Créer quelques périodes
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=60),
            date_fin=self.today - timedelta(days=30),
            commentaire='Période passée'
        )
        
        self.periode_actuelle = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=20),
            commentaire='Période actuelle'
        )
    
    def test_get_formulaire_modification(self):
        """Test d'affichage du formulaire de modification"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_update', args=[self.sage_femme.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Modifier la sage-femme')
        self.assertContains(response, self.sage_femme.nom)
        self.assertContains(response, self.sage_femme.prenom)
    
    def test_modification_sage_femme_valide(self):
        """Test de modification avec des données valides"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_update', args=[self.sage_femme.pk])
        
        data = self.sage_femme_data.copy()
        data.update({
            'nom': 'Nouveau Nom',
            'prenom': 'Nouveau Prénom'
        })
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la sage-femme a été modifiée
        self.sage_femme.refresh_from_db()
        self.assertEqual(self.sage_femme.nom, 'NOUVEAU NOM')
        self.assertEqual(self.sage_femme.prenom, 'Nouveau Prénom')
        
        # Vérifier la réponse HTMX
        content = response.content.decode()
        self.assertIn('window.showNotification', content)
        self.assertIn('modifiée avec succès', content)
    
    def test_modification_periodes_activite(self):
        """Test de modification des périodes d'activité dans le formulaire"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_update', args=[self.sage_femme.pk])
        
        # Données incluant modification de période
        data = self.sage_femme_data.copy()
        nouvelle_date_debut = self.today - timedelta(days=15)
        nouvelle_date_fin = self.today + timedelta(days=15)
        
        data.update({
            f'debut_{self.periode_actuelle.pk}': nouvelle_date_debut.strftime('%Y-%m-%d'),
            f'fin_{self.periode_actuelle.pk}': nouvelle_date_fin.strftime('%Y-%m-%d')
        })
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la période a été modifiée
        self.periode_actuelle.refresh_from_db()
        self.assertEqual(self.periode_actuelle.date_debut, nouvelle_date_debut)
        self.assertEqual(self.periode_actuelle.date_fin, nouvelle_date_fin)
    
    def test_modification_donnees_invalides(self):
        """Test de modification avec des données invalides"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_update', args=[self.sage_femme.pk])
        
        # Email invalide
        data = self.sage_femme_data.copy()
        data['email'] = 'email_invalide'
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la sage-femme n'a pas été modifiée
        self.sage_femme.refresh_from_db()
        self.assertEqual(self.sage_femme.email, 'marie.dupont@test.nc')
        
        # Vérifier que le formulaire est renvoyé avec des erreurs
        self.assertContains(response, 'form')


class SageFemmeDeleteViewTest(BaseAdministrationTest):
    """Tests pour la suppression de sage-femmes"""
    
    def setUp(self):
        super().setUp()
        self.sage_femme = SageFemme.objects.create(**self.sage_femme_data)
    
    def test_suppression_sage_femme_get_non_autorise(self):
        """Test que GET n'est pas autorisé pour la suppression"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_delete', args=[self.sage_femme.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
    
    def test_suppression_sage_femme_delete(self):
        """Test de suppression avec méthode DELETE"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_delete', args=[self.sage_femme.pk])
        
        # Utiliser une requête AJAX avec le header CSRF approprié
        response = self.client.delete(
            url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            HTTP_X_CSRFTOKEN='test'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la sage-femme a été supprimée
        self.assertFalse(SageFemme.objects.filter(pk=self.sage_femme.pk).exists())
        
        # Vérifier la réponse HTMX
        content = response.content.decode()
        self.assertIn('window.showNotification', content)
        self.assertIn('supprimée avec succès', content)
    
    def test_suppression_sage_femme_inexistante(self):
        """Test de suppression d'une sage-femme inexistante"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_delete', args=[9999])
        
        response = self.client.delete(
            url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 404)


class SageFemmeDetailViewTest(BaseAdministrationTest):
    """Tests pour la vue de détail des sage-femmes"""
    
    def setUp(self):
        super().setUp()
        self.sage_femme = SageFemme.objects.create(**self.sage_femme_data)
        
        # Créer des périodes variées
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=90),
            date_fin=self.today - timedelta(days=60),
            commentaire='Période terminée'
        )
        
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=30),
            commentaire='Période en cours'
        )
        
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today + timedelta(days=30),
            commentaire='Période future'
        )
    
    def test_detail_sage_femme(self):
        """Test de la vue de détail"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_detail', args=[self.sage_femme.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.sage_femme.nom_complet)
        self.assertContains(response, self.sage_femme.titre)
        
        # Vérifier que les périodes sont affichées
        self.assertContains(response, 'Période terminée')
        self.assertContains(response, 'Période en cours')
        self.assertContains(response, 'Période future')
    
    def test_detail_avec_statuts_periodes(self):
        """Test que les statuts des périodes sont correctement affichés"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_detail', args=[self.sage_femme.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les différents statuts dans la réponse
        content = response.content.decode()
        
        # Une période doit être marquée comme "En cours"
        self.assertIn('En cours', content)
        
        # Une période doit être marquée comme "Passé"
        self.assertIn('Passé', content)
        
        # Une période doit être marquée comme "À venir"
        self.assertIn('À venir', content)
    
    def test_detail_sage_femme_inexistante(self):
        """Test de détail pour une sage-femme inexistante"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_detail', args=[9999])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)


class ErrorHandlingTest(BaseAdministrationTest):
    """Tests de gestion d'erreurs"""
    
    def test_gestion_erreur_serveur(self):
        """Test que les erreurs serveur sont gérées"""
        # Ce test pourrait nécessiter de mocker des exceptions
        pass
    
    def test_validation_csrf(self):
        """Test de validation CSRF"""
        # Créer un client avec vérification CSRF activée
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:sagefemme_create')
        
        # Utiliser des données uniques pour ce test
        csrf_test_data = self.sage_femme_data.copy()
        csrf_test_data['email'] = 'csrf_test@test.nc'
        csrf_test_data['numero_cafat'] = 'CSRF123456789'
        csrf_test_data['ridet'] = 'CSRF123456'
        
        # Essayer de poster sans token CSRF
        response = csrf_client.post(url, csrf_test_data)
        
        # Devrait échouer sans token CSRF approprié
        self.assertIn(response.status_code, [403, 400])