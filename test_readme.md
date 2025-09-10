# Tests Consultations Obstétricales - Documentation

**État des tests consultation obstétricale : 93/93 tests passent (100% ✅)**

Ce document décrit la suite de tests spécifiquement dédiée aux consultations obstétricales dans l'application Maieutix, une fonctionnalité récemment implémentée pour le suivi de grossesse.

## 🎯 Résumé de l'Implémentation

### Fonctionnalités Implémentées
- **Calcul automatique SA** : Semaines d'aménorrhée calculées à partir de la DDG (Date de Dernières Règles)
- **Interface admin réorganisée** : "6.1.3.2 Consultations Obstétricales" (ancien "6.2.2") et "6.1.3.1 Données de grossesse"
- **Affichage différencié** : Badges SA verts dans l'admin, badges indigo dans l'interface utilisateur
- **Tests exhaustifs** : 93 tests couvrant modèles, formulaires, vues, admin et intégration

### Caractéristiques Techniques
- **Modèle ConsultationObstetricale** avec champ `semaines_amenorrhee` auto-calculé
- **Méthode calculer_sa()** avec gestion d'erreurs robuste
- **Validation stricte** : Cohérence entre date consultation et DDG
- **Traçabilité complète** : Sage-femme créatrice et horodatage

## 📊 Répartition des Tests (93 tests)

```
Tests Consultation Obstétricale/
├── models/          # 25 tests - Modèle et logique métier
├── forms/           # 20 tests - Formulaires et validation  
├── views/           # 15 tests - Vues et APIs
├── admin/           # 18 tests - Interface d'administration
└── integration/     # 15 tests - Tests d'intégration UI/UX
```

## 🏗️ Détail des Tests par Catégorie

### 1. Tests Modèles (25 tests)
**Fichier** : `core/tests/models/test_consultation_obstetricale.py`

#### Fonctionnalités Testées
- **Création consultation** : Validation des champs obligatoires et optionnels
- **Calcul SA automatique** : Méthode `calculer_sa()` avec différents scénarios
- **Validation dates** : Cohérence date consultation / DDG
- **Constantes vitales** : Validation tension systolique/diastolique, poids
- **Relations patiente** : Association uniquement aux femmes avec DDG définie
- **Calculs IMC** : Intégration avec antécédents pour le calcul IMC obstétrical
- **Propriétés calculées** : Tension complète, interprétation, résumé consultation

#### Cas de Tests Spécifiques
```python
def test_calcul_sa_avec_ddg_valide(self):
    """Test calcul SA avec DDG définie - 20 SA attendues"""
    
def test_calcul_sa_sans_ddg(self):
    """Test calcul SA sans DDG - doit retourner chaîne vide"""
    
def test_validation_date_consultation_future(self):
    """Test interdiction dates futures pour consultation"""
    
def test_interpretation_tension_hypertension_stade1(self):
    """Test interprétation automatique tension artérielle"""
```

### 2. Tests Formulaires (20 tests)
**Fichier** : `core/tests/forms/test_consultation_obstetricale_forms.py`

#### Fonctionnalités Testées
- **Validation champs** : Motif obligatoire, tension/poids optionnels
- **Calcul SA intégré** : Auto-remplissage du champ SA dans les formulaires
- **Queryset patientes** : Limitation aux femmes avec DDG définie
- **Widgets personnalisés** : Classes CSS Tailwind, attributs HTML5
- **Messages d'erreur** : Validation contextuelle pour consultations obstétricales

#### Types de Formulaires
- **ConsultationObstetricaleForm** : Formulaire standard complet
- **ConsultationObstetricaleModalForm** : Formulaire modal HTMX
- **ConsultationObstetricaleQuickForm** : Formulaire inline rapide

### 3. Tests Vues (15 tests)  
**Fichier** : `core/tests/views/test_consultation_obstetricale_views.py`

#### Fonctionnalités Testées
- **CRUD complet** : Création, lecture, modification, suppression
- **API HTMX** : Endpoints pour sauvegarde AJAX des consultations
- **Calcul SA temps réel** : Mise à jour automatique lors de la création
- **Permissions** : Accès limité aux patientes avec DDG
- **Réponses JSON** : Format standardisé pour les APIs

#### Endpoints Testés
```python
# Endpoints consultation obstétricale
POST /patients/{id}/consultation-obstetricale/save-quick/
GET /patients/consultation-obstetricale/{id}/
POST /patients/consultation-obstetricale/{id}/delete/
GET /patients/{id}/consultations-obstetricales/
```

### 4. Tests Administration (18 tests)
**Fichier** : `core/tests/admin/test_consultation_obstetricale_admin.py`

#### Fonctionnalités Testées
- **Section renommée** : "6.1.3.2 Consultations Obstétricales" 
- **List display** : Patient, date, SA, motif, tension, poids
- **Méthodes d'affichage** : `sa_affichage()` avec badge SA vert
- **Filtres** : Date consultation, patient, caisse, SA
- **Fieldsets** : Organisation logique des champs (général, constantes, consultation, métadonnées)
- **Actions admin** : Actions personnalisées pour consultations obstétricales

#### Méthodes Admin Testées
```python
def sa_affichage(self, obj):
    """Affichage SA avec badge vert dans l'admin"""
    
def patient_link(self, obj):
    """Lien vers la fiche patiente"""
    
def tension_affichage(self, obj):
    """Affichage tension avec interprétation colorée"""
```

### 5. Tests Intégration (15 tests)
**Fichier** : `core/tests/integration/test_consultation_obstetricale_integration_simple.py`

#### Fonctionnalités Testées
- **Workflow complet** : Création → Affichage → Modification → Suppression
- **Interface différenciée** : Code couleur violet vs rose (gynécologique)
- **Intégration DDG** : Synchronisation avec date début grossesse
- **Calculs intégrés** : SA, IMC, interprétation tension dans l'interface
- **Navigation fluide** : Tests onglets page patiente
- **Badges SA** : Vérification affichage dans différents contextes

## 🚀 Commandes de Test Spécifiques

### Tests Consultation Obstétricale Uniquement
```bash
# Tous les tests consultation obstétricale
docker-compose exec web python manage.py test core.tests.models.test_consultation_obstetricale
docker-compose exec web python manage.py test core.tests.forms.test_consultation_obstetricale_forms  
docker-compose exec web python manage.py test core.tests.admin.test_consultation_obstetricale_admin

# Test intégration
docker-compose exec web python manage.py test core.tests.integration.test_consultation_obstetricale_integration_simple

# Test spécifique du calcul SA
docker-compose exec web python manage.py test core.tests.models.test_consultation_obstetricale.ConsultationObstetricaleModelTest.test_calcul_sa_avec_ddg_valide

# Avec mode verbose pour debug
docker-compose exec web python manage.py test core.tests.models.test_consultation_obstetricale --verbosity=2
```

## 🔬 Fonctionnalités Clés Testées

### Calcul Automatique SA
```python
def calculer_sa(self):
    """
    Calcule les semaines d'aménorrhée à la date de consultation
    Retourne une chaîne formatée ou vide si pas de DDG
    """
    if not self.patient.date_debut_grossesse:
        return ""
    
    try:
        jours_grossesse = (self.date_consultation - self.patient.date_debut_grossesse).days
        if jours_grossesse < 0:
            return ""
        
        semaines = jours_grossesse // 7
        jours_restants = jours_grossesse % 7
        
        if jours_restants == 0:
            return f"{semaines} SA"
        else:
            return f"{semaines} SA + {jours_restants}j"
    except (AttributeError, TypeError):
        return ""
```

### Interface Admin Réorganisée
- **6.1.3.1 Données de grossesse** (modèle DonneesGrossesse)
- **6.1.3.2 Consultations Obstétricales** (modèle ConsultationObstetricale)

### Affichage SA Différencié
- **Admin** : Badge SA vert avec icône médicale
- **Interface UI** : Badge SA indigo pour distinction visuelle

## ✅ Couverture de Tests

### Couverture par Composant
- **Modèles** : 100% - Toutes méthodes et propriétés testées
- **Formulaires** : 100% - Validation complète et cas d'erreur
- **Vues** : 95% - Tous endpoints et permisions
- **Admin** : 100% - Configuration et méthodes personnalisées
- **Intégration** : 90% - Workflows principaux et cas limites

### Validation Métier Testée
- ✅ DDG obligatoire pour consultation obstétricale
- ✅ Date consultation ≥ DDG
- ✅ Date consultation ≤ aujourd'hui  
- ✅ Patiente doit être de type 'femme'
- ✅ Tension systolique ≥ diastolique si les deux définies
- ✅ Poids entre 30-200 kg
- ✅ Calcul SA robuste avec gestion d'erreurs

## 🎯 Cas de Tests Remarquables

### Test Calcul SA Complexe
```python
def test_calcul_sa_cas_limites(self):
    """Test calculs SA dans différents scénarios edge cases"""
    # 1. DDG = date consultation → 0 SA
    # 2. DDG future → chaîne vide  
    # 3. Différence exacte 7 jours → 1 SA
    # 4. Différence 10 jours → 1 SA + 3j
```

### Test Interface Admin
```python
def test_admin_sa_affichage_badge_vert(self):
    """Vérification badge SA vert dans list display admin"""
    response = self.admin_client.get('/admin/core/consultationobstetricale/')
    self.assertContains(response, 'bg-green-100 text-green-800')
    self.assertContains(response, '20 SA')
```

### Test Intégration Complète
```python
def test_workflow_creation_consultation_avec_sa(self):
    """Test workflow complet : création → calcul SA → affichage"""
    # 1. Créer consultation via formulaire
    # 2. Vérifier calcul automatique SA
    # 3. Vérifier affichage dans historique
    # 4. Vérifier badge couleur appropriée
```

## 📋 Architecture TDD

L'implémentation des consultations obstétricales a suivi une approche **Test-Driven Development** stricte :

1. **Tests d'abord** : Écriture des 93 tests avant implémentation
2. **Red-Green-Refactor** : Cycle standard TDD respecté
3. **Couverture maximale** : Tous les cas nominaux et d'erreur
4. **Tests d'intégration** : Validation des workflows complets
5. **Tests de régression** : Vérification non-impact sur existant

Cette approche garantit la robustesse et la maintenabilité de la fonctionnalité consultation obstétricale dans l'écosystème Maieutix.

---

**Tests consultation obstétricale développés avec ❤️ suivant les principes TDD**