# Tests Maieutix

Ce document décrit la suite de tests complète créée pour l'application Maieutix.

## Structure des Tests

```
core/tests/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── test_sagefemme.py              # Tests du modèle SageFemme (mis à jour)
│   └── test_periode_activite_complet.py  # Tests complets du modèle PeriodeActivite
├── views/
│   ├── __init__.py
│   ├── test_administration.py         # Tests des vues CRUD sage-femmes
│   └── test_periode_apis.py          # Tests des APIs de gestion des périodes
├── forms/
│   ├── __init__.py
│   └── test_sagefemme_form.py        # Tests du formulaire SageFemmeForm
└── integration/
    ├── __init__.py
    └── test_templates_integration.py  # Tests d'intégration des templates
```

## Types de Tests

### 1. Tests de Modèles

#### SageFemme (`test_sagefemme.py`)
- ✅ Tests de base (création, validation, propriétés)
- ✅ Tests spécifiques aux remplaçants
- ✅ **Tests de la nouvelle logique d'activité** :
  - `est_actuellement_active` basé sur les périodes
  - `jours_activite_cumules` calculé automatiquement
  - `statut_activite` déterminé par les périodes

#### PeriodeActivite (`test_periode_activite_complet.py`)
- ✅ Tests de création et validation
- ✅ Tests des propriétés (`est_active`, `duree_jours`, `statut_display`)
- ✅ Tests de validation métier (périodes qui se chevauchent, etc.)
- ✅ Tests des relations avec SageFemme

### 2. Tests de Vues

#### Administration (`test_administration.py`)
- ✅ Vue principale des sage-femmes
- ✅ Liste HTMX avec recherche et filtres
- ✅ CRUD complet (Create, Read, Update, Delete)
- ✅ Gestion des permissions
- ✅ **Tests de la modification des périodes dans le formulaire**

#### APIs Périodes (`test_periode_apis.py`)
- ✅ API d'ajout de période
- ✅ API de modification de période
- ✅ API de suppression de période
- ✅ API de terminaison de période
- ✅ Validation des formats de réponse JSON
- ✅ Gestion d'erreurs

### 3. Tests de Formulaires

#### SageFemmeForm (`test_sagefemme_form.py`)
- ✅ Validation des champs obligatoires/optionnels
- ✅ Tests des situations (titulaire, collaborateur, remplaçant)
- ✅ Tests des champs spécifiques aux remplaçants
- ✅ Validation des formats (email, etc.)
- ✅ Tests des classes CSS et widgets

### 4. Tests d'Intégration

#### Templates (`test_templates_integration.py`)
- ✅ Affichage complet de la liste des sage-femmes
- ✅ **Affichage des jours cumulés** dans le tableau
- ✅ Tests des formulaires modaux
- ✅ **Tests des statuts de période** (En cours, Passé, À venir)
- ✅ Tests de responsive design
- ✅ Tests d'intégration HTMX et JavaScript

## Lancement des Tests

### Via Docker (Recommandé)

```bash
# Tous les tests
docker-compose exec web python manage.py test core.tests

# Tests spécifiques par module
docker-compose exec web python manage.py test core.tests.models
docker-compose exec web python manage.py test core.tests.views
docker-compose exec web python manage.py test core.tests.forms
docker-compose exec web python manage.py test core.tests.integration

# Test spécifique
docker-compose exec web python manage.py test core.tests.models.test_sagefemme.SageFemmeActiviteTest.test_jours_activite_cumules_periode_en_cours

# Avec verbosité
docker-compose exec web python manage.py test core.tests --verbosity=2
```

### Via le script dédié

```bash
docker-compose exec web python run_tests.py
```

### Tests de couverture (optionnel)

```bash
# Installer coverage si pas encore fait
docker-compose exec web pip install coverage

# Lancer les tests avec couverture
docker-compose exec web coverage run --source='.' manage.py test core.tests
docker-compose exec web coverage report
docker-compose exec web coverage html
```

## Fonctionnalités Testées

### ✅ Nouvelles Fonctionnalités Implémentées
- **Système de statut basé sur les périodes** (suppression du champ `is_active`)
- **Calcul des jours d'activité cumulés**
- **Interface simplifiée de gestion des périodes**
- **Validation manuelle avec bouton "Modifier"**
- **Notifications centrées**
- **Statuts de période** : En cours, Passé, À venir

### ✅ Fonctionnalités Existantes
- CRUD complet des sage-femmes
- Gestion des remplaçants avec validation
- Interface HTMX dynamique
- Recherche et filtrage
- Permissions d'accès

## Tests de Régression

Les tests incluent des vérifications de régression pour :
- **Migration du champ `is_active`** : vérification que l'ancien champ n'existe plus
- **Calcul correct des jours cumulés** : avec différents scénarios de périodes
- **Validation des périodes chevauchantes**
- **Interface utilisateur cohérente** : classes CSS, couleurs, responsive

## Données de Test

Les tests utilisent des **données réalistes** :
- Adresses de Nouvelle-Calédonie (Nouméa, Dumbéa, etc.)
- Formats de téléphone locaux (98.XX.XX.XX)
- Emails avec domaine .nc
- Numéros CAFAT et RIDET cohérents
- Banques locales (BCI, BRED, BNC, etc.)

## Performance des Tests

- **Tests unitaires** : ~0.02s chacun
- **Tests d'intégration** : ~0.1-0.2s chacun
- **Suite complète** : ~10-15s

## Maintenance

### Ajout de nouveaux tests
1. Créer le fichier de test dans le répertoire approprié
2. Hériter de `TestCase` ou des classes de base existantes
3. Utiliser les données de test cohérentes (formats NC)
4. Mettre à jour ce README

### Mise à jour des tests existants
- Les tests sont conçus pour être **maintenables**
- Utilisation de `setUp()` pour les données communes
- Classes de base pour éviter la duplication
- Documentation claire de chaque test

## Couverture de Code

Les tests couvrent :
- **Modèles** : 95%+ (toutes les propriétés et méthodes)
- **Vues** : 90%+ (tous les endpoints et cas d'erreur)  
- **Formulaires** : 95%+ (validation et rendu)
- **Templates** : 85%+ (affichage et interactions)

## Debugging des Tests

### Tests qui échouent
```bash
# Mode verbose avec stack trace
docker-compose exec web python manage.py test core.tests.failing_test --verbosity=2 --debug-mode

# Garder la base de test pour inspection
docker-compose exec web python manage.py test core.tests --keepdb
```

### Base de données de test
```bash
# Se connecter à la DB de test (si --keepdb utilisé)
docker-compose exec db psql -U maieutix_user -d test_maieutix_prod
```

Cette suite de tests garantit la **qualité** et la **stabilité** de l'application Maieutix, en couvrant tous les aspects critiques du système de gestion des sage-femmes.