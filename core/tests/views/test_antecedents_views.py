"""
Tests pour les vues des antécédents et API endpoints
Tests complets des fonctionnalités AJAX et HTMX
"""

import json
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from core.models import Patient, Caisse, Antecedents, FrottisCV, SageFemme, PeriodeActivite


class AntecedentsViewsTest(TestCase):
    
    def setUp(self):
        """Configuration des données de test"""
        self.client = Client()
        
        # Créer une caisse
        self.caisse = Caisse.objects.create(
            nom="CAFAT"
        )
        
        # Créer une sage-femme et période d'activité
        self.sagefemme = SageFemme.objects.create(
            nom="Martin",
            prenom="Sophie",
            titre="Sage-femme",
            telephone="0123456789",
            email="sophie.martin@test.com",
            numero_cafat="SF123456",
            ridet="123456789",
            rib="FR123456789",
            banque="BNC",
            situation="titulaire"
        )
        
        self.periode = PeriodeActivite.objects.create(
            sage_femme=self.sagefemme,
            date_debut=date.today()
        )
        
        # Créer l'utilisateur associé à la sage-femme
        User = get_user_model()
        self.user = User.objects.create_user(
            email="sophie.martin@test.com",
            password="testpass123",
            must_change_password=False
        )
        self.sagefemme.user = self.user
        self.sagefemme.save()
        
        # Se connecter
        self.client.login(email="sophie.martin@test.com", password="testpass123")
        
        # Créer une patiente
        self.patiente = Patient.objects.create(
            type_patient='femme',
            nom='Dupont',
            prenom='Marie',
            date_naissance=date(1990, 5, 15),
            telephone='0123456789',
            caisse=self.caisse
        )
        
        # Créer des antécédents
        self.antecedents = Antecedents.objects.create(
            patient=self.patiente,
            taille=1.65,
            poids=60.0,
            medecin_traitant="Dr. Martin"
        )
    
    def test_patient_antecedents_view_get_existing(self):
        """Test récupération des antécédents existants via API GET"""
        url = reverse('patients:patient_antecedents', args=[self.patiente.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content)
        
        # Vérifier la structure de la réponse
        self.assertIn('antecedents', data)
        self.assertIn('frottis', data)
        
        # Vérifier les données des antécédents
        antecedents_data = data['antecedents']
        self.assertEqual(antecedents_data['taille'], 1.65)
        self.assertEqual(antecedents_data['poids'], 60.0)
        self.assertEqual(antecedents_data['medecin_traitant'], "Dr. Martin")
        self.assertIsNone(antecedents_data['gynecologue'])
        
        # Vérifier que la liste des frottis est vide
        self.assertEqual(data['frottis'], [])
    
    def test_patient_antecedents_view_get_with_frottis(self):
        """Test récupération des antécédents avec frottis via API GET"""
        # Ajouter des frottis
        frottis1 = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2023, 6, 15),
            resultat="Normal - ancien"
        )
        
        frottis2 = FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2024, 3, 10),
            resultat="Normal - récent"
        )
        
        url = reverse('patients:patient_antecedents', args=[self.patiente.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Vérifier les frottis
        frottis_data = data['frottis']
        self.assertEqual(len(frottis_data), 2)
        
        # Le plus récent devrait être en premier (ordering par -date_frottis)
        self.assertEqual(frottis_data[0]['date_frottis'], '2024-03-10')
        self.assertEqual(frottis_data[0]['resultat'], "Normal - récent")
        self.assertEqual(frottis_data[1]['date_frottis'], '2023-06-15')
        self.assertEqual(frottis_data[1]['resultat'], "Normal - ancien")
    
    def test_patient_antecedents_view_get_no_antecedents(self):
        """Test récupération API quand aucun antécédent n'existe"""
        # Créer une patiente sans antécédents
        patiente_sans_antecedents = Patient.objects.create(
            type_patient='femme',
            nom='Durand',
            prenom='Claire',
            date_naissance=date(1985, 8, 20),
            telephone='0987654321',
            caisse=self.caisse
        )
        
        url = reverse('patients:patient_antecedents', args=[patiente_sans_antecedents.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Vérifier que les antécédents sont null et frottis vide
        self.assertIsNone(data['antecedents'])
        self.assertEqual(data['frottis'], [])
    
    def test_patient_antecedents_view_bebe_forbidden(self):
        """Test que l'API antécédents refuse les bébés"""
        bebe = Patient.objects.create(
            type_patient='bebe',
            nom='Dupont',
            prenom='Lucas',
            date_naissance=date.today(),
            mere=self.patiente,
            caisse=self.caisse
        )
        
        url = reverse('patients:patient_antecedents', args=[bebe.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_patient_antecedents_view_patient_not_found(self):
        """Test API avec patient inexistant"""
        url = reverse('patients:patient_antecedents', args=[99999])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_save_antecedents_view_post_create_new(self):
        """Test sauvegarde création nouveaux antécédents via API POST"""
        # Supprimer les antécédents existants
        self.antecedents.delete()
        
        url = reverse('patients:save_antecedents')
        data = {
            'patient_id': self.patiente.pk,
            'taille': '1.70',
            'poids': '65.0',
            'medecin_traitant': 'Dr. Rousseau',
            'gynecologue': 'Dr. Bernard',
            'allergie': 'Pénicilline',
            'asthme': 'true',
            'diabete': 'false',
            'hta': 'true',
            'atcd_obstetricaux': 'G1P0',
            'fcv_notes': 'Suivi régulier',
            'contraception': 'Pilule'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Vérifier que les antécédents ont été créés
        antecedents = Antecedents.objects.get(patient=self.patiente)
        self.assertEqual(antecedents.taille, 1.70)
        self.assertEqual(antecedents.poids, 65.0)
        self.assertEqual(antecedents.medecin_traitant, 'Dr. Rousseau')
        self.assertEqual(antecedents.gynecologue, 'Dr. Bernard')
        self.assertEqual(antecedents.allergie, 'Pénicilline')
        self.assertTrue(antecedents.asthme)
        self.assertFalse(antecedents.diabete)
        self.assertTrue(antecedents.hta)
        self.assertEqual(antecedents.atcd_obstetricaux, 'G1P0')
        self.assertEqual(antecedents.fcv_notes, 'Suivi régulier')
        self.assertEqual(antecedents.contraception, 'Pilule')
    
    def test_save_antecedents_view_post_update_existing(self):
        """Test sauvegarde modification antécédents existants via API POST"""
        url = reverse('patients:save_antecedents')
        data = {
            'patient_id': self.patiente.pk,
            'taille': '1.68',
            'poids': '62.5',
            'medecin_traitant': 'Dr. Martin Modifié',
            'gynecologue': 'Dr. Nouveau',
            'epilepsie': 'true',
            'infection_urinaire': 'false'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Recharger les antécédents
        self.antecedents.refresh_from_db()
        
        # Vérifier les modifications
        self.assertEqual(self.antecedents.taille, 1.68)
        self.assertEqual(self.antecedents.poids, 62.5)
        self.assertEqual(self.antecedents.medecin_traitant, 'Dr. Martin Modifié')
        self.assertEqual(self.antecedents.gynecologue, 'Dr. Nouveau')
        self.assertTrue(self.antecedents.epilepsie)
        self.assertFalse(self.antecedents.infection_urinaire)
    
    def test_save_antecedents_view_post_with_frottis(self):
        """Test sauvegarde avec frottis via API POST"""
        url = reverse('patients:save_antecedents')
        data = {
            'patient_id': self.patiente.pk,
            'taille': '1.65',
            'poids': '60.0',
            'frottis_date_0': '2024-03-15',
            'frottis_resultat_0': 'Normal - Premier frottis',
            'frottis_date_1': '2024-06-20',
            'frottis_resultat_1': 'Normal - Deuxième frottis',
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Vérifier que les frottis ont été créés
        frottis_list = list(self.antecedents.frottis.all().order_by('date_frottis'))
        self.assertEqual(len(frottis_list), 2)
        
        self.assertEqual(frottis_list[0].date_frottis, date(2024, 3, 15))
        self.assertEqual(frottis_list[0].resultat, 'Normal - Premier frottis')
        self.assertEqual(frottis_list[1].date_frottis, date(2024, 6, 20))
        self.assertEqual(frottis_list[1].resultat, 'Normal - Deuxième frottis')
    
    def test_save_antecedents_view_post_replace_frottis(self):
        """Test que les nouveaux frottis remplacent les anciens"""
        # Créer des frottis existants
        FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2023, 1, 10),
            resultat="Ancien frottis 1"
        )
        
        FrottisCV.objects.create(
            antecedents=self.antecedents,
            date_frottis=date(2023, 6, 15),
            resultat="Ancien frottis 2"
        )
        
        self.assertEqual(self.antecedents.frottis.count(), 2)
        
        # Sauvegarder avec de nouveaux frottis
        url = reverse('patients:save_antecedents')
        data = {
            'patient_id': self.patiente.pk,
            'frottis_date_0': '2024-01-10',
            'frottis_resultat_0': 'Nouveau frottis unique',
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que seul le nouveau frottis existe
        frottis_list = list(self.antecedents.frottis.all())
        self.assertEqual(len(frottis_list), 1)
        self.assertEqual(frottis_list[0].resultat, 'Nouveau frottis unique')
    
    def test_save_antecedents_view_post_missing_patient_id(self):
        """Test sauvegarde sans patient_id"""
        url = reverse('patients:save_antecedents')
        data = {
            'taille': '1.65',
            'poids': '60.0'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['error'], 'Patient ID manquant')
    
    def test_save_antecedents_view_post_invalid_patient_id(self):
        """Test sauvegarde avec patient_id inexistant"""
        url = reverse('patients:save_antecedents')
        data = {
            'patient_id': 99999,
            'taille': '1.65'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)
    
    def test_save_antecedents_view_post_bebe_forbidden(self):
        """Test sauvegarde refuse les bébés"""
        bebe = Patient.objects.create(
            type_patient='bebe',
            nom='Dupont',
            prenom='Lucas',
            date_naissance=date.today(),
            mere=self.patiente,
            caisse=self.caisse
        )
        
        url = reverse('patients:save_antecedents')
        data = {
            'patient_id': bebe.pk,
            'taille': '0.5'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)
    
    def test_save_antecedents_view_post_invalid_data(self):
        """Test sauvegarde avec données invalides"""
        url = reverse('patients:save_antecedents')
        data = {
            'patient_id': self.patiente.pk,
            'taille': 'invalid_float',
            'poids': '60.0'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)
    
    def test_save_antecedents_view_csrf_required(self):
        """Test que CSRF token est requis"""
        client = Client(enforce_csrf_checks=True)
        client.login(email="sophie.martin@test.com", password="testpass123")
        
        url = reverse('patients:save_antecedents')
        data = {
            'patient_id': self.patiente.pk,
            'taille': '1.65'
        }
        
        response = client.post(url, data)
        self.assertEqual(response.status_code, 403)
    
    def test_antecedents_views_require_login(self):
        """Test que les vues nécessitent une authentification"""
        self.client.logout()
        
        # Test vue GET antécédents
        url = reverse('patients:patient_antecedents', args=[self.patiente.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirection vers login
        
        # Test vue POST sauvegarde
        url = reverse('patients:save_antecedents')
        response = self.client.post(url, {'patient_id': self.patiente.pk})
        self.assertEqual(response.status_code, 302)  # Redirection vers login
    
    def test_antecedents_views_method_restrictions(self):
        """Test restrictions de méthodes HTTP"""
        # GET antécédents - autorise seulement GET
        url = reverse('patients:patient_antecedents', args=[self.patiente.pk])
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
        
        # POST sauvegarde - autorise seulement POST
        url = reverse('patients:save_antecedents')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
    
    def test_save_antecedents_boolean_field_conversion(self):
        """Test conversion correcte des champs booléens"""
        url = reverse('patients:save_antecedents')
        
        # Test avec valeurs 'true'/'false' en string
        data = {
            'patient_id': self.patiente.pk,
            'asthme': 'true',
            'diabete': 'false',
            'hta': 'true',
            'epilepsie': 'false',
            'atcd_fam_diabete': 'true',
            'atcd_fam_cancer_sein': 'false'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        
        self.antecedents.refresh_from_db()
        
        # Vérifier conversions
        self.assertTrue(self.antecedents.asthme)
        self.assertFalse(self.antecedents.diabete)
        self.assertTrue(self.antecedents.hta)
        self.assertFalse(self.antecedents.epilepsie)
        self.assertTrue(self.antecedents.atcd_fam_diabete)
        self.assertFalse(self.antecedents.atcd_fam_cancer_sein)
    
    def test_save_antecedents_empty_frottis_handling(self):
        """Test gestion des frottis vides ou incomplets"""
        url = reverse('patients:save_antecedents')
        data = {
            'patient_id': self.patiente.pk,
            'frottis_date_0': '2024-03-15',
            'frottis_resultat_0': 'Normal complet',
            'frottis_date_1': '2024-06-20',
            'frottis_resultat_1': '',  # Résultat vide
            'frottis_date_2': '',  # Date vide
            'frottis_resultat_2': 'Résultat sans date',
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        
        # Seul le premier frottis complet devrait être sauvegardé
        frottis_list = list(self.antecedents.frottis.all())
        self.assertEqual(len(frottis_list), 1)
        self.assertEqual(frottis_list[0].resultat, 'Normal complet')
    
    def test_save_antecedents_numeric_field_validation(self):
        """Test validation des champs numériques"""
        url = reverse('patients:save_antecedents')
        
        # Test avec valeurs valides
        data = {
            'patient_id': self.patiente.pk,
            'taille': '1.65',
            'poids': '60.5'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        
        self.antecedents.refresh_from_db()
        self.assertEqual(self.antecedents.taille, 1.65)
        self.assertEqual(self.antecedents.poids, 60.5)
    
    def test_save_antecedents_empty_numeric_fields(self):
        """Test gestion des champs numériques vides"""
        url = reverse('patients:save_antecedents')
        data = {
            'patient_id': self.patiente.pk,
            'taille': '',  # Vide
            'poids': '',   # Vide
            'medecin_traitant': 'Dr. Test'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        
        self.antecedents.refresh_from_db()
        # Les champs vides devraient rester inchangés ou être None
        self.assertEqual(self.antecedents.medecin_traitant, 'Dr. Test')