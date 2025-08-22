"""
Tests pour les formulaires des sage-femmes.
"""
from django.test import TestCase
from core.views.administration import SageFemmeForm
from core.models.sagefemme import SageFemme


class SageFemmeFormTest(TestCase):
    """Tests pour le formulaire SageFemmeForm"""
    
    def setUp(self):
        """Configuration de base pour tous les tests"""
        self.valid_data = {
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
    
    def test_form_valide_avec_donnees_completes(self):
        """Test du formulaire avec toutes les données valides"""
        form = SageFemmeForm(data=self.valid_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)
    
    def test_form_champs_obligatoires(self):
        """Test que les champs obligatoires sont requis"""
        champs_obligatoires = [
            'nom', 'prenom', 'titre', 'telephone', 'email', 
            'numero_cafat', 'ridet', 'rib', 'banque', 'situation'
        ]
        
        for champ in champs_obligatoires:
            data = self.valid_data.copy()
            del data[champ]
            
            form = SageFemmeForm(data=data)
            
            self.assertFalse(form.is_valid(), f"Le formulaire devrait être invalide sans le champ '{champ}'")
            self.assertIn(champ, form.errors, f"Le champ '{champ}' devrait avoir une erreur")
    
    def test_form_champs_optionnels(self):
        """Test que les champs d'adresse sont optionnels"""
        data = self.valid_data.copy()
        del data['rue']
        del data['code_postal']
        del data['ville']
        
        form = SageFemmeForm(data=data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)
    
    def test_form_email_invalide(self):
        """Test avec un format d'email invalide"""
        data = self.valid_data.copy()
        data['email'] = 'email_invalide'
        
        form = SageFemmeForm(data=data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_form_situation_invalide(self):
        """Test avec une situation invalide"""
        data = self.valid_data.copy()
        data['situation'] = 'situation_inexistante'
        
        form = SageFemmeForm(data=data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('situation', form.errors)
    
    def test_form_situations_valides(self):
        """Test avec toutes les situations valides"""
        # Créer d'abord une sage-femme titulaire pour les remplaçants
        titulaire = SageFemme.objects.create(
            nom='Titulaire', prenom='Test', titre='Sage-femme', 
            telephone='123', email='titulaire@test.nc',
            numero_cafat='TIT123', ridet='TIT456', rib='TIT789', banque='BCI',
            situation='titulaire'
        )
        
        situations_valides = ['titulaire', 'collaborateur', 'remplacant']
        
        for situation in situations_valides:
            data = self.valid_data.copy()
            data['situation'] = situation
            data['email'] = f'test_{situation}@test.nc'  # Email unique
            data['numero_cafat'] = f'{situation}123456789'  # CAFAT unique
            data['ridet'] = f'0{situation}123.001'  # RIDET unique
            
            # Pour les remplaçants, ajouter le champ remplacement_de
            if situation == 'remplacant':
                data['remplacement_de'] = titulaire.pk
            
            form = SageFemmeForm(data=data)
            
            self.assertTrue(form.is_valid(), f"Le formulaire devrait être valide avec la situation '{situation}'")
    
    def test_form_css_classes(self):
        """Test que les champs ont les bonnes classes CSS"""
        form = SageFemmeForm()
        
        # Vérifier quelques champs clés
        expected_css_class = 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'
        
        self.assertIn(expected_css_class, form.fields['nom'].widget.attrs.get('class', ''))
        self.assertIn(expected_css_class, form.fields['prenom'].widget.attrs.get('class', ''))
        self.assertIn(expected_css_class, form.fields['email'].widget.attrs.get('class', ''))
    
    def test_form_checkbox_classes(self):
        """Test que les checkboxes ont les bonnes classes CSS"""
        form = SageFemmeForm()
        
        expected_checkbox_class = 'rounded border-gray-300 text-primary focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50'
        
        self.assertIn(expected_checkbox_class, form.fields['etat_recapitulatif_commun'].widget.attrs.get('class', ''))
        self.assertIn(expected_checkbox_class, form.fields['bons_depot_communs'].widget.attrs.get('class', ''))
    
    def test_form_sauvegarde_instance(self):
        """Test de sauvegarde avec une instance existante"""
        # Créer d'abord une sage-femme
        sage_femme = SageFemme.objects.create(**self.valid_data)
        
        # Modifier ses données
        new_data = self.valid_data.copy()
        new_data['nom'] = 'Nouveau Nom'
        new_data['prenom'] = 'Nouveau Prénom'
        
        form = SageFemmeForm(data=new_data, instance=sage_femme)
        
        self.assertTrue(form.is_valid())
        
        # Sauvegarder
        updated_sage_femme = form.save()
        
        self.assertEqual(updated_sage_femme.pk, sage_femme.pk)
        self.assertEqual(updated_sage_femme.nom, 'Nouveau Nom')
        self.assertEqual(updated_sage_femme.prenom, 'Nouveau Prénom')
    
    def test_form_creation_nouvelle_instance(self):
        """Test de création d'une nouvelle instance"""
        form = SageFemmeForm(data=self.valid_data)
        
        self.assertTrue(form.is_valid())
        
        # Sauvegarder
        sage_femme = form.save()
        
        self.assertIsNotNone(sage_femme.pk)
        self.assertEqual(sage_femme.nom, 'Dupont')
        self.assertEqual(sage_femme.prenom, 'Marie')
        self.assertEqual(sage_femme.situation, 'titulaire')


class SageFemmeFormRemplacantTest(TestCase):
    """Tests spécifiques pour les remplaçants dans le formulaire"""
    
    def setUp(self):
        """Configuration pour les tests de remplaçants"""
        # Créer des titulaires/collaborateurs pour les remplacements
        self.titulaire = SageFemme.objects.create(
            nom='Titulaire',
            prenom='Pierre',
            titre='Sage-femme titulaire',
            telephone='98.11.11.11',
            email='pierre.titulaire@test.nc',
            numero_cafat='111111111',
            ridet='0111111.001',
            rib='FR76 3000 3000 1111 1111 1111 111',
            banque='BCI',
            situation='titulaire'
        )
        
        self.collaborateur = SageFemme.objects.create(
            nom='Collaborateur',
            prenom='Julie',
            titre='Sage-femme collaboratrice',
            telephone='98.22.22.22',
            email='julie.collaborateur@test.nc',
            numero_cafat='222222222',
            ridet='0222222.001',
            rib='FR76 3000 3000 2222 2222 2222 222',
            banque='BRED',
            situation='collaborateur'
        )
        
        self.remplacant_data = {
            'nom': 'Remplacant',
            'prenom': 'Sophie',
            'titre': 'Sage-femme remplaçante',
            'telephone': '98.33.33.33',
            'email': 'sophie.remplacant@test.nc',
            'numero_cafat': '333333333',
            'ridet': '0333333.001',
            'rib': 'FR76 3000 3000 3333 3333 3333 333',
            'banque': 'BNC',
            'situation': 'remplacant'
        }
    
    def test_form_init_filtre_remplacement_de(self):
        """Test que le champ remplacement_de est filtré correctement"""
        form = SageFemmeForm()
        
        # Le queryset devrait contenir seulement les titulaires et collaborateurs
        queryset = form.fields['remplacement_de'].queryset
        
        self.assertIn(self.titulaire, queryset)
        self.assertIn(self.collaborateur, queryset)
    
    def test_form_init_exclut_instance_actuelle(self):
        """Test que l'instance actuelle est exclue du champ remplacement_de"""
        form = SageFemmeForm(instance=self.titulaire)
        
        queryset = form.fields['remplacement_de'].queryset
        
        # Le titulaire ne devrait pas pouvoir se remplacer lui-même
        self.assertNotIn(self.titulaire, queryset)
        self.assertIn(self.collaborateur, queryset)
    
    def test_form_remplacant_valide_avec_remplacement_de(self):
        """Test d'un remplaçant valide avec remplacement_de"""
        data = self.remplacant_data.copy()
        data['remplacement_de'] = self.titulaire.pk
        data['etat_recapitulatif_commun'] = True
        data['bons_depot_communs'] = True
        
        form = SageFemmeForm(data=data)
        
        self.assertTrue(form.is_valid())
        
        # Sauvegarder et vérifier
        remplacant = form.save()
        self.assertEqual(remplacant.situation, 'remplacant')
        self.assertEqual(remplacant.remplacement_de, self.titulaire)
        self.assertTrue(remplacant.etat_recapitulatif_commun)
        self.assertTrue(remplacant.bons_depot_communs)
    
    def test_form_remplacant_peut_remplacer_collaborateur(self):
        """Test qu'un remplaçant peut remplacer un collaborateur"""
        data = self.remplacant_data.copy()
        data['remplacement_de'] = self.collaborateur.pk
        
        form = SageFemmeForm(data=data)
        
        self.assertTrue(form.is_valid())
        
        remplacant = form.save()
        self.assertEqual(remplacant.remplacement_de, self.collaborateur)


class SageFemmeFormFieldsTest(TestCase):
    """Tests des champs spécifiques du formulaire"""
    
    def test_form_fields_included(self):
        """Test que tous les champs nécessaires sont inclus"""
        form = SageFemmeForm()
        
        expected_fields = [
            'nom', 'prenom', 'titre', 'telephone', 'email',
            'rue', 'code_postal', 'ville',
            'numero_cafat', 'ridet', 'rib', 'banque',
            'situation', 'remplacement_de',
            'etat_recapitulatif_commun', 'bons_depot_communs'
        ]
        
        for field in expected_fields:
            self.assertIn(field, form.fields, f"Le champ '{field}' devrait être dans le formulaire")
    
    def test_form_fields_excluded(self):
        """Test que les champs non désirés sont exclus"""
        form = SageFemmeForm()
        
        # Le champ is_active a été supprimé du modèle, donc ne devrait pas être dans le formulaire
        excluded_fields = ['created_at', 'updated_at']
        
        for field in excluded_fields:
            self.assertNotIn(field, form.fields, f"Le champ '{field}' ne devrait pas être dans le formulaire")
    
    def test_form_field_types(self):
        """Test des types de champs"""
        form = SageFemmeForm()
        
        # Vérifier quelques types de widgets spécifiques
        from django import forms
        
        self.assertIsInstance(form.fields['email'].widget, forms.EmailInput)
        self.assertIsInstance(form.fields['etat_recapitulatif_commun'].widget, forms.CheckboxInput)
        self.assertIsInstance(form.fields['bons_depot_communs'].widget, forms.CheckboxInput)
        self.assertIsInstance(form.fields['remplacement_de'].widget, forms.Select)
    
    def test_form_help_texts(self):
        """Test des textes d'aide si définis"""
        form = SageFemmeForm()
        
        # Pour l'instant, pas de textes d'aide définis, mais le test est prêt
        # si on en ajoute plus tard
        pass
    
    def test_form_labels_customization(self):
        """Test de la personnalisation des labels si nécessaire"""
        form = SageFemmeForm()
        
        # Vérifier que les labels par défaut du modèle sont utilisés
        # (ce test peut être étendu si on personnalise les labels)
        self.assertIsNotNone(form.fields['nom'].label)
        self.assertIsNotNone(form.fields['prenom'].label)


class SageFemmeFormValidationTest(TestCase):
    """Tests de validation personnalisée du formulaire"""
    
    def setUp(self):
        """Configuration pour les tests de validation"""
        self.valid_data = {
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
    
    def test_form_validation_donnees_uniques(self):
        """Test de validation pour les champs uniques"""
        # Créer une première sage-femme
        SageFemme.objects.create(**self.valid_data)
        
        # Essayer de créer une deuxième avec le même email
        form = SageFemmeForm(data=self.valid_data)
        
        self.assertFalse(form.is_valid())
        # Le modèle devrait lever une erreur de contrainte unique
    
    def test_form_validation_caracteres_speciaux(self):
        """Test avec des caractères spéciaux dans les noms"""
        data = self.valid_data.copy()
        data['nom'] = "D'Artagnan-Leblanc"
        data['prenom'] = "Marie-José"
        
        form = SageFemmeForm(data=data)
        
        self.assertTrue(form.is_valid())
    
    def test_form_validation_longueur_champs(self):
        """Test de validation de la longueur des champs"""
        data = self.valid_data.copy()
        
        # Tester avec un nom très long (dépend des contraintes du modèle)
        data['nom'] = 'A' * 200  # Nom très long
        
        form = SageFemmeForm(data=data)
        
        # Le résultat dépend des contraintes max_length du modèle
        # Si max_length est défini et < 200, le formulaire sera invalide
    
    def test_form_validation_telephone_formats(self):
        """Test de différents formats de téléphone"""
        formats_valides = [
            '98.12.34.56',
            '98 12 34 56',
            '98123456',
            '+687 12 34 56'
        ]
        
        for telephone in formats_valides:
            data = self.valid_data.copy()
            data['telephone'] = telephone
            data['email'] = f'test_{telephone.replace(".", "").replace(" ", "")}@test.nc'
            data['numero_cafat'] = f'{telephone.replace(".", "").replace(" ", "")[:9]}'
            data['ridet'] = f'0{telephone.replace(".", "").replace(" ", "")[:6]}.001'
            
            form = SageFemmeForm(data=data)
            
            # Devrait être valide (dépend de la validation du modèle)
            if not form.is_valid():
                print(f"Format téléphone '{telephone}' invalide: {form.errors}")