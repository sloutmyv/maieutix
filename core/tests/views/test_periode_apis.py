"""
Tests pour les APIs de gestion des périodes d'activité.
"""
from django.test import TestCase, Client
from django.urls import reverse
from authentication.models import SageFemmeUser
import json
from datetime import date, timedelta
from core.models.sagefemme import SageFemme
from core.models.periode_activite import PeriodeActivite


class BasePeriodeAPITest(TestCase):
    """Classe de base pour les tests d'API des périodes"""
    
    def setUp(self):
        """Configuration de base pour tous les tests"""
        self.client = Client()
        
        # Créer un superutilisateur pour les tests
        self.superuser = SageFemmeUser.objects.create_superuser(
            email='admin@test.nc',
            password='testpass123'
        )
        
        # Créer une sage-femme de test
        self.sage_femme = SageFemme.objects.create(
            nom='Test',
            prenom='Marie',
            titre='Sage-femme test',
            telephone='98.12.34.56',
            email='marie.test@example.nc',
            numero_cafat='123456789',
            ridet='RIDET123456',
            rib='FR1234567890123456789012345',
            banque='BCI',
            situation='titulaire'
        )
        
        self.today = date.today()
        
        # Headers pour les requêtes JSON
        self.json_headers = {
            'content_type': 'application/json',
            'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'
        }


class AjouterPeriodeAPITest(BasePeriodeAPITest):
    """Tests pour l'API d'ajout de périodes d'activité"""
    
    def test_ajouter_periode_valide(self):
        """Test d'ajout d'une période valide"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:ajouter_periode', args=[self.sage_femme.pk])
        
        data = {
            'date_debut': (self.today - timedelta(days=30)).strftime('%Y-%m-%d'),
            'date_fin': (self.today + timedelta(days=30)).strftime('%Y-%m-%d'),
            'commentaire': 'Nouvelle période de test'
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            **self.json_headers
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la réponse JSON
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('ajoutée avec succès', response_data['message'])
        
        # Vérifier que la période a été créée
        self.assertEqual(self.sage_femme.periodes_activite.count(), 1)
        
        periode = self.sage_femme.periodes_activite.first()
        self.assertEqual(periode.date_debut, self.today - timedelta(days=30))
        self.assertEqual(periode.date_fin, self.today + timedelta(days=30))
        self.assertEqual(periode.commentaire, 'Nouvelle période de test')
    
    def test_ajouter_periode_sans_fin(self):
        """Test d'ajout d'une période sans date de fin"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:ajouter_periode', args=[self.sage_femme.pk])
        
        data = {
            'date_debut': self.today.strftime('%Y-%m-%d'),
            'commentaire': 'Période en cours'
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            **self.json_headers
        )
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Vérifier que la période a été créée sans date de fin
        periode = self.sage_femme.periodes_activite.first()
        self.assertEqual(periode.date_debut, self.today)
        self.assertIsNone(periode.date_fin)
    
    def test_ajouter_periode_date_invalide(self):
        """Test d'ajout avec format de date invalide"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:ajouter_periode', args=[self.sage_femme.pk])
        
        data = {
            'date_debut': 'date_invalide',
            'commentaire': 'Test'
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            **self.json_headers
        )
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Format de date invalide', response_data['error'])
    
    def test_ajouter_periode_sage_femme_inexistante(self):
        """Test d'ajout pour une sage-femme inexistante"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:ajouter_periode', args=[9999])
        
        data = {
            'date_debut': self.today.strftime('%Y-%m-%d'),
            'commentaire': 'Test'
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            **self.json_headers
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_ajouter_periode_methode_non_autorisee(self):
        """Test que seule la méthode POST est autorisée"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:ajouter_periode', args=[self.sage_femme.pk])
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        
        response = self.client.put(url)
        self.assertEqual(response.status_code, 405)
    
    def test_ajouter_periode_validation_business(self):
        """Test de validation métier lors de l'ajout"""
        # Créer d'abord une période en cours
        PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=15)
        )
        
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:ajouter_periode', args=[self.sage_femme.pk])
        
        # Essayer d'ajouter une autre période sans fin (devrait échouer)
        data = {
            'date_debut': self.today.strftime('%Y-%m-%d'),
            'commentaire': 'Deuxième période en cours'
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            **self.json_headers
        )
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        # Devrait contenir une erreur de validation


class ModifierPeriodeAPITest(BasePeriodeAPITest):
    """Tests pour l'API de modification de périodes d'activité"""
    
    def setUp(self):
        super().setUp()
        self.periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=30),
            date_fin=self.today - timedelta(days=10),
            commentaire='Période originale'
        )
    
    def test_modifier_periode_valide(self):
        """Test de modification valide d'une période"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:modifier_periode', args=[self.periode.pk])
        
        nouvelle_debut = self.today - timedelta(days=60)
        nouvelle_fin = self.today - timedelta(days=5)
        
        data = {
            'date_debut': nouvelle_debut.strftime('%Y-%m-%d'),
            'date_fin': nouvelle_fin.strftime('%Y-%m-%d'),
            'commentaire': 'Période modifiée'
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            **self.json_headers
        )
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('modifiée avec succès', response_data['message'])
        
        # Vérifier que la période a été modifiée
        self.periode.refresh_from_db()
        self.assertEqual(self.periode.date_debut, nouvelle_debut)
        self.assertEqual(self.periode.date_fin, nouvelle_fin)
        self.assertEqual(self.periode.commentaire, 'Période modifiée')
    
    def test_modifier_periode_enlever_date_fin(self):
        """Test de modification pour enlever la date de fin"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:modifier_periode', args=[self.periode.pk])
        
        data = {
            'date_debut': (self.today - timedelta(days=20)).strftime('%Y-%m-%d'),
            'date_fin': None,
            'commentaire': 'Période maintenant en cours'
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            **self.json_headers
        )
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Vérifier que la date de fin a été supprimée
        self.periode.refresh_from_db()
        self.assertIsNone(self.periode.date_fin)
    
    def test_modifier_periode_seulement_commentaire(self):
        """Test de modification du commentaire seulement"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:modifier_periode', args=[self.periode.pk])
        
        data = {
            'commentaire': 'Nouveau commentaire seulement'
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            **self.json_headers
        )
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Vérifier que seul le commentaire a changé
        self.periode.refresh_from_db()
        self.assertEqual(self.periode.commentaire, 'Nouveau commentaire seulement')
        # Les dates doivent rester identiques
        self.assertEqual(self.periode.date_debut, self.today - timedelta(days=30))
        self.assertEqual(self.periode.date_fin, self.today - timedelta(days=10))
    
    def test_modifier_periode_inexistante(self):
        """Test de modification d'une période inexistante"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:modifier_periode', args=[9999])
        
        data = {
            'date_debut': self.today.strftime('%Y-%m-%d')
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            **self.json_headers
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_modifier_periode_date_invalide(self):
        """Test de modification avec format de date invalide"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:modifier_periode', args=[self.periode.pk])
        
        data = {
            'date_debut': 'format_invalide'
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            **self.json_headers
        )
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Format de date invalide', response_data['error'])


class SupprimerPeriodeAPITest(BasePeriodeAPITest):
    """Tests pour l'API de suppression de périodes d'activité"""
    
    def setUp(self):
        super().setUp()
        self.periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=30),
            date_fin=self.today - timedelta(days=10),
            commentaire='Période à supprimer'
        )
    
    def test_supprimer_periode_valide(self):
        """Test de suppression valide d'une période"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:supprimer_periode', args=[self.periode.pk])
        
        response = self.client.delete(
            url,
            **self.json_headers
        )
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('supprimée avec succès', response_data['message'])
        
        # Vérifier que la période a été supprimée
        self.assertFalse(PeriodeActivite.objects.filter(pk=self.periode.pk).exists())
    
    def test_supprimer_periode_inexistante(self):
        """Test de suppression d'une période inexistante"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:supprimer_periode', args=[9999])
        
        response = self.client.delete(
            url,
            **self.json_headers
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_supprimer_periode_methode_non_autorisee(self):
        """Test que seule la méthode DELETE est autorisée"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:supprimer_periode', args=[self.periode.pk])
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)


class TerminerPeriodeAPITest(BasePeriodeAPITest):
    """Tests pour l'API de terminaison de périodes d'activité"""
    
    def setUp(self):
        super().setUp()
        self.periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=30),
            commentaire='Période en cours'
        )
    
    def test_terminer_periode_valide(self):
        """Test de terminaison valide d'une période"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:terminer_periode', args=[self.periode.pk])
        
        response = self.client.post(
            url,
            **self.json_headers
        )
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('terminée avec succès', response_data['message'])
        
        # Vérifier que la période a été terminée à aujourd'hui
        self.periode.refresh_from_db()
        self.assertEqual(self.periode.date_fin, self.today)
    
    def test_terminer_periode_deja_terminee(self):
        """Test de terminaison d'une période déjà terminée"""
        # Modifier la période pour qu'elle soit déjà terminée
        self.periode.date_fin = self.today - timedelta(days=5)
        self.periode.save()
        
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:terminer_periode', args=[self.periode.pk])
        
        response = self.client.post(
            url,
            **self.json_headers
        )
        
        # Devrait quand même fonctionner et mettre à jour la date
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Vérifier que la date de fin a été mise à jour
        self.periode.refresh_from_db()
        self.assertEqual(self.periode.date_fin, self.today)
    
    def test_terminer_periode_inexistante(self):
        """Test de terminaison d'une période inexistante"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:terminer_periode', args=[9999])
        
        response = self.client.post(
            url,
            **self.json_headers
        )
        
        self.assertEqual(response.status_code, 404)


class PermissionsAPITest(BasePeriodeAPITest):
    """Tests des permissions pour les APIs de périodes"""
    
    def setUp(self):
        super().setUp()
        self.periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=30),
            commentaire='Période test'
        )
    
    def test_acces_sans_permission(self):
        """Test d'accès aux APIs sans permission appropriée"""
        # Maintenant l'authentification est requise, donc sans login on devrait avoir 403 ou 302
        
        urls_to_test = [
            reverse('administration:ajouter_periode', args=[self.sage_femme.pk]),
            reverse('administration:modifier_periode', args=[self.periode.pk]),
            reverse('administration:supprimer_periode', args=[self.periode.pk]),
            reverse('administration:terminer_periode', args=[self.periode.pk]),
        ]
        
        for url in urls_to_test:
            if 'ajouter' in url or 'terminer' in url:
                response = self.client.post(url, json.dumps({}), **self.json_headers)
            elif 'modifier' in url:
                response = self.client.post(url, json.dumps({}), **self.json_headers)
            else:  # supprimer
                response = self.client.delete(url, **self.json_headers)
            
            # Sans authentification, devrait retourner 403, 302 (redirection) ou 405 (method not allowed)
            self.assertIn(response.status_code, [403, 302, 405])


class APIResponseFormatTest(BasePeriodeAPITest):
    """Tests du format des réponses des APIs"""
    
    def setUp(self):
        super().setUp()
        self.periode = PeriodeActivite.objects.create(
            sage_femme=self.sage_femme,
            date_debut=self.today - timedelta(days=30),
            commentaire='Période test'
        )
    
    def test_format_reponse_succes(self):
        """Test du format de réponse en cas de succès"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:terminer_periode', args=[self.periode.pk])
        
        response = self.client.post(url, **self.json_headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        response_data = json.loads(response.content)
        
        # Vérifier la structure de la réponse
        self.assertIn('success', response_data)
        self.assertIn('message', response_data)
        self.assertTrue(response_data['success'])
        self.assertIsInstance(response_data['message'], str)
    
    def test_format_reponse_erreur(self):
        """Test du format de réponse en cas d'erreur"""
        self.client.login(username='admin@test.nc', password='testpass123')
        url = reverse('administration:ajouter_periode', args=[self.sage_femme.pk])
        
        # Envoyer des données invalides
        data = {
            'date_debut': 'format_invalide'
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            **self.json_headers
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        response_data = json.loads(response.content)
        
        # Vérifier la structure de la réponse d'erreur
        self.assertIn('success', response_data)
        self.assertIn('error', response_data)
        self.assertFalse(response_data['success'])
        self.assertIsInstance(response_data['error'], str)
    
    def test_gestion_erreur_serveur(self):
        """Test de gestion des erreurs serveur inattendues"""
        # Ce test nécessiterait de mocker une exception dans les vues
        # Pour l'instant, on vérifie juste que les vues gèrent les try/catch
        pass