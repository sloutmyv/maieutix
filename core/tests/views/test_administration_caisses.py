"""
Tests pour les vues d'administration des caisses et conditions de paiement.
"""
from django.test import TestCase, Client
from django.urls import reverse
from authentication.models import SageFemmeUser
import json
from decimal import Decimal

from core.models.caisse import Caisse
from core.models.condition_paiement import ConditionPaiement
from core.models.sagefemme import SageFemme
from core.models.periode_activite import PeriodeActivite
from datetime import date, timedelta


class BaseCaisseAdministrationTest(TestCase):
    """Classe de base pour les tests d'administration des caisses"""
    
    def setUp(self):
        """Configuration de base pour tous les tests"""
        self.client = Client()
        
        # Créer un superutilisateur
        self.superuser = SageFemmeUser.objects.create_superuser(
            email='admin@test.nc',
            password='testpass123'
        )
        
        # Créer une sage-femme titulaire pour les tests de permissions
        self.titulaire = SageFemme.objects.create(
            nom='Titulaire',
            prenom='Test',
            titre='Sage-femme titulaire',
            telephone='98.11.11.11',
            email='titulaire@test.nc',
            numero_cafat='111111111',
            ridet='0111111.001',
            rib='FR76 3000 3000 1111 1111 1111 111',
            banque='BCI',
            situation='titulaire'
        )
        
        # Créer une sage-femme collaboratrice
        self.collaborateur = SageFemme.objects.create(
            nom='Collaborateur',
            prenom='Test',
            titre='Sage-femme collaboratrice',
            telephone='98.22.22.22',
            email='collaborateur@test.nc',
            numero_cafat='222222222',
            ridet='0222222.001',
            rib='FR76 3000 3000 2222 2222 2222 222',
            banque='BRED',
            situation='collaborateur'
        )
        
        # Créer des utilisateurs associés aux sages-femmes
        self.titulaire_user = SageFemmeUser.objects.create_user(
            email='titulaire@test.nc',
            password='azerty'
        )
        self.titulaire_user.must_change_password = False
        self.titulaire_user.save()
        self.titulaire.user = self.titulaire_user
        self.titulaire.save()
        
        self.collaborateur_user = SageFemmeUser.objects.create_user(
            email='collaborateur@test.nc',
            password='azerty'
        )
        self.collaborateur_user.must_change_password = False
        self.collaborateur_user.save()
        self.collaborateur.user = self.collaborateur_user
        self.collaborateur.save()
        
        # Ajouter des périodes d'activité actives
        today = date.today()
        PeriodeActivite.objects.create(
            sage_femme=self.titulaire,
            date_debut=today - timedelta(days=30),
            commentaire='Période active titulaire'
        )
        PeriodeActivite.objects.create(
            sage_femme=self.collaborateur,
            date_debut=today - timedelta(days=30),
            commentaire='Période active collaborateur'
        )
        
        # Mettre à jour le statut actif des utilisateurs
        self.titulaire_user.update_active_status()
        self.titulaire_user.save()
        self.collaborateur_user.update_active_status()
        self.collaborateur_user.save()
        
        # Créer des conditions de paiement pour les tests
        self.condition1 = ConditionPaiement.objects.create(
            designation='CAFAT Standard',
            pourcentage=Decimal('80.00')
        )
        self.condition2 = ConditionPaiement.objects.create(
            designation='Mutuelle complémentaire',
            pourcentage=Decimal('20.00')
        )
        self.condition3 = ConditionPaiement.objects.create(
            designation='Accident du travail',
            pourcentage=Decimal('100.00')
        )
        
        # Données de test pour les caisses
        self.caisse_data = {
            'nom': 'CAFAT Test',
            'conditions_paiement_eligibles': [self.condition1.pk, self.condition2.pk]
        }


class AdministrationCaissesViewTest(BaseCaisseAdministrationTest):
    """Tests pour la vue principale des caisses"""
    
    def test_vue_caisses_sans_authentification(self):
        """Test d'accès à la vue sans authentification"""
        url = reverse('administration:administration_caisses')
        response = self.client.get(url)
        
        # Devrait rediriger vers la page de connexion
        self.assertEqual(response.status_code, 302)
    
    def test_vue_caisses_avec_superuser(self):
        """Test d'accès à la vue avec superutilisateur"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:administration_caisses')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Administration - Caisses')
    
    def test_vue_caisses_avec_titulaire(self):
        """Test d'accès à la vue avec sage-femme titulaire"""
        self.client.login(username='titulaire@test.nc', password='azerty')
        url = reverse('administration:administration_caisses')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Le titulaire devrait avoir accès à la vue
        self.assertContains(response, 'Ajouter une caisse')
    
    def test_vue_caisses_avec_collaborateur(self):
        """Test d'accès à la vue avec sage-femme collaboratrice"""
        self.client.login(username='collaborateur@test.nc', password='azerty')
        url = reverse('administration:administration_caisses')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Le collaborateur devrait avoir accès en lecture seule
        self.assertNotContains(response, 'Ajouter une caisse')
    
    def test_vue_caisses_contexte(self):
        """Test du contexte de la vue principale"""
        # Créer quelques caisses
        caisse1 = Caisse.objects.create(nom='Caisse 1')
        caisse1.conditions_paiement_eligibles.add(self.condition1)
        
        caisse2 = Caisse.objects.create(nom='Caisse 2')
        caisse2.conditions_paiement_eligibles.add(self.condition2, self.condition3)
        
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:administration_caisses')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('caisses', response.context)
        self.assertEqual(len(response.context['caisses']), 2)
        self.assertIn('page_title', response.context)
        self.assertEqual(response.context['section'], 'administration')


class CaisseListViewTest(BaseCaisseAdministrationTest):
    """Tests pour la vue de liste HTMX des caisses"""
    
    def setUp(self):
        super().setUp()
        
        # Créer des caisses de test
        self.caisse1 = Caisse.objects.create(nom='CAFAT NC')
        self.caisse1.conditions_paiement_eligibles.add(self.condition1, self.condition3)
        
        self.caisse2 = Caisse.objects.create(nom='Mutuelle Médialis')
        self.caisse2.conditions_paiement_eligibles.add(self.condition2)
        
        self.caisse3 = Caisse.objects.create(nom='Caisse Autonome')
        # Pas de conditions pour caisse3
    
    def test_liste_caisses_avec_superuser(self):
        """Test de la liste HTMX avec superutilisateur"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CAFAT NC')
        self.assertContains(response, 'Mutuelle Médialis')
        self.assertContains(response, 'Caisse Autonome')
    
    def test_liste_caisses_avec_recherche(self):
        """Test de la recherche dans la liste"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_list')
        response = self.client.get(url, {'search': 'CAFAT'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CAFAT NC')
        self.assertNotContains(response, 'Mutuelle Médialis')
        self.assertNotContains(response, 'Caisse Autonome')
    
    def test_liste_caisses_vide(self):
        """Test de la liste avec aucune caisse"""
        # Supprimer toutes les caisses
        Caisse.objects.all().delete()
        
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aucune caisse trouvée')
    
    def test_liste_caisses_permissions_collaborateur(self):
        """Test que le collaborateur voit la liste mais sans boutons d'action"""
        self.client.login(username='collaborateur@test.nc', password='azerty')
        url = reverse('administration:caisse_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CAFAT NC')
        # Pas de boutons de modification/suppression pour les collaborateurs
        self.assertNotContains(response, 'hx-get="/administration/api/caisses/' + str(self.caisse1.pk) + '/update/"')


class CaisseCreateViewTest(BaseCaisseAdministrationTest):
    """Tests pour la création de caisses"""
    
    def test_create_caisse_get_avec_superuser(self):
        """Test GET de création avec superutilisateur"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nouvelle caisse')
        self.assertContains(response, 'conditions_paiement_eligibles')
    
    def test_create_caisse_post_valide(self):
        """Test POST de création avec données valides"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_create')
        response = self.client.post(url, self.caisse_data)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la caisse a été créée
        self.assertTrue(Caisse.objects.filter(nom='CAFAT Test').exists())
        caisse = Caisse.objects.get(nom='CAFAT Test')
        self.assertEqual(caisse.conditions_paiement_eligibles.count(), 2)
    
    def test_create_caisse_post_invalide(self):
        """Test POST de création avec données invalides"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_create')
        
        # Données invalides (pas de nom)
        invalid_data = {'conditions_paiement_eligibles': [self.condition1.pk]}
        response = self.client.post(url, invalid_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')
        # Vérifier que la caisse n'a pas été créée
        self.assertFalse(Caisse.objects.filter(nom='').exists())
    
    def test_create_caisse_permission_denied_collaborateur(self):
        """Test que le collaborateur ne peut pas créer de caisse"""
        self.client.login(username='collaborateur@test.nc', password='azerty')
        url = reverse('administration:caisse_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 403)


class CaisseUpdateViewTest(BaseCaisseAdministrationTest):
    """Tests pour la modification de caisses"""
    
    def setUp(self):
        super().setUp()
        self.caisse = Caisse.objects.create(nom='Caisse à modifier')
        self.caisse.conditions_paiement_eligibles.add(self.condition1)
    
    def test_update_caisse_get_avec_superuser(self):
        """Test GET de modification avec superutilisateur"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_update', args=[self.caisse.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Modifier la caisse')
        self.assertContains(response, self.caisse.nom)
    
    def test_update_caisse_post_valide(self):
        """Test POST de modification avec données valides"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_update', args=[self.caisse.pk])
        
        update_data = {
            'nom': 'Caisse modifiée',
            'conditions_paiement_eligibles': [self.condition2.pk, self.condition3.pk]
        }
        response = self.client.post(url, update_data)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les modifications
        self.caisse.refresh_from_db()
        self.assertEqual(self.caisse.nom, 'Caisse modifiée')
        self.assertEqual(self.caisse.conditions_paiement_eligibles.count(), 2)
        self.assertNotIn(self.condition1, self.caisse.conditions_paiement_eligibles.all())
    
    def test_update_caisse_permission_denied_collaborateur(self):
        """Test que le collaborateur ne peut pas modifier de caisse"""
        self.client.login(username='collaborateur@test.nc', password='azerty')
        url = reverse('administration:caisse_update', args=[self.caisse.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 403)


class CaisseDetailViewTest(BaseCaisseAdministrationTest):
    """Tests pour la vue de détail des caisses"""
    
    def setUp(self):
        super().setUp()
        self.caisse = Caisse.objects.create(nom='Caisse détail')
        self.caisse.conditions_paiement_eligibles.add(self.condition1, self.condition2)
    
    def test_detail_caisse_avec_superuser(self):
        """Test de détail avec superutilisateur"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_detail', args=[self.caisse.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.caisse.nom)
        self.assertContains(response, 'CAFAT Standard')
        self.assertContains(response, 'Mutuelle complémentaire')
    
    def test_detail_caisse_avec_collaborateur(self):
        """Test que le collaborateur peut voir les détails"""
        self.client.login(username='collaborateur@test.nc', password='azerty')
        url = reverse('administration:caisse_detail', args=[self.caisse.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.caisse.nom)
    
    def test_detail_caisse_inexistante(self):
        """Test de détail avec une caisse inexistante"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_detail', args=[99999])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)


class CaisseDeleteViewTest(BaseCaisseAdministrationTest):
    """Tests pour la suppression de caisses"""
    
    def setUp(self):
        super().setUp()
        self.caisse = Caisse.objects.create(nom='Caisse à supprimer')
    
    def test_delete_caisse_avec_superuser(self):
        """Test de suppression avec superutilisateur"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_delete', args=[self.caisse.pk])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la suppression
        self.assertFalse(Caisse.objects.filter(pk=self.caisse.pk).exists())
    
    def test_delete_caisse_permission_denied_collaborateur(self):
        """Test que le collaborateur ne peut pas supprimer de caisse"""
        self.client.login(username='collaborateur@test.nc', password='azerty')
        url = reverse('administration:caisse_delete', args=[self.caisse.pk])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 403)
    
    def test_delete_caisse_inexistante(self):
        """Test de suppression avec une caisse inexistante"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_delete', args=[99999])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 404)


class CaisseIntegrationTest(BaseCaisseAdministrationTest):
    """Tests d'intégration pour les caisses"""
    
    def test_workflow_complet_caisse(self):
        """Test d'un workflow complet : création -> modification -> suppression"""
        self.client.login(username='admin@test.nc', password='testpass123')
        
        # 1. Créer une caisse
        create_url = reverse('administration:caisse_create')
        create_data = {
            'nom': 'Caisse Workflow',
            'conditions_paiement_eligibles': [self.condition1.pk]
        }
        response = self.client.post(create_url, create_data)
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la création
        caisse = Caisse.objects.get(nom='Caisse Workflow')
        self.assertEqual(caisse.conditions_paiement_eligibles.count(), 1)
        
        # 2. Modifier la caisse
        update_url = reverse('administration:caisse_update', args=[caisse.pk])
        update_data = {
            'nom': 'Caisse Workflow Modifiée',
            'conditions_paiement_eligibles': [self.condition1.pk, self.condition2.pk]
        }
        response = self.client.post(update_url, update_data)
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la modification
        caisse.refresh_from_db()
        self.assertEqual(caisse.nom, 'Caisse Workflow Modifiée')
        self.assertEqual(caisse.conditions_paiement_eligibles.count(), 2)
        
        # 3. Supprimer la caisse
        delete_url = reverse('administration:caisse_delete', args=[caisse.pk])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la suppression
        self.assertFalse(Caisse.objects.filter(pk=caisse.pk).exists())
    
    def test_caisse_avec_condition_supprimee(self):
        """Test du comportement d'une caisse quand une de ses conditions est supprimée"""
        # Créer une caisse avec des conditions
        caisse = Caisse.objects.create(nom='Caisse Test Suppression')
        caisse.conditions_paiement_eligibles.add(self.condition1, self.condition2)
        
        # Supprimer une condition directement (simuler suppression via admin Django)
        condition_id = self.condition1.pk
        self.condition1.delete()
        
        # Vérifier que la caisse existe toujours mais n'a plus que une condition
        caisse.refresh_from_db()
        self.assertEqual(caisse.conditions_paiement_eligibles.count(), 1)
        self.assertEqual(caisse.conditions_paiement_eligibles.first(), self.condition2)


class CaisseSearchTest(BaseCaisseAdministrationTest):
    """Tests pour les fonctionnalités de recherche des caisses"""
    
    def setUp(self):
        super().setUp()
        
        # Créer plusieurs caisses pour les tests de recherche
        self.caisse_cafat = Caisse.objects.create(nom='CAFAT Nouvelle-Calédonie')
        self.caisse_cafat.conditions_paiement_eligibles.add(self.condition1)
        
        self.caisse_mutuelle = Caisse.objects.create(nom='Mutuelle Médialis NC')
        self.caisse_mutuelle.conditions_paiement_eligibles.add(self.condition2)
        
        self.caisse_autre = Caisse.objects.create(nom='Assurance Santé Plus')
        self.caisse_autre.conditions_paiement_eligibles.add(self.condition3)
    
    def test_recherche_par_nom_partiel(self):
        """Test de recherche par nom partiel"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_list')
        
        # Recherche "CAFAT"
        response = self.client.get(url, {'search': 'CAFAT'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CAFAT Nouvelle-Calédonie')
        self.assertNotContains(response, 'Mutuelle Médialis')
        self.assertNotContains(response, 'Assurance Santé')
    
    def test_recherche_insensible_casse(self):
        """Test de recherche insensible à la casse"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_list')
        
        # Recherche "mutuelle" en minuscules
        response = self.client.get(url, {'search': 'mutuelle'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mutuelle Médialis')
    
    def test_recherche_vide(self):
        """Test avec recherche vide"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_list')
        
        response = self.client.get(url, {'search': ''})
        self.assertEqual(response.status_code, 200)
        # Devrait afficher toutes les caisses
        self.assertContains(response, 'CAFAT Nouvelle-Calédonie')
        self.assertContains(response, 'Mutuelle Médialis')
        self.assertContains(response, 'Assurance Santé')
    
    def test_recherche_aucun_resultat(self):
        """Test de recherche sans résultat"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:caisse_list')
        
        response = self.client.get(url, {'search': 'XYZ123'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aucune caisse trouvée')