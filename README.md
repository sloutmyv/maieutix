# Maieutix

**Plateforme de gestion pour sages-femmes en Nouvelle-Calédonie**

Un projet Django moderne pour la gestion des activités professionnelles des sages-femmes, développé avec une architecture modulaire et une interface utilisateur intuitive.

## Statut du Projet ✅

- **Tests** : 698/698 tests passent (100% ✅)
- **Authentification** : Système complet avec gestion des périodes d'activité
- **Interface** : Design moderne avec Tailwind CSS + HTMX + Alpine.js
- **Architecture** : Modulaire et extensible
- **Production Ready** : Configuration Docker optimisée

## 🔑 Identifiants de Connexion

**Superutilisateur Django Admin** :
- Email : admin@maieutix.nc
- Mot de passe : azerty

**Note** : Seules les sages-femmes avec des périodes d'activité actives peuvent se connecter au système.

## Fonctionnalités Principales

### 🏥 Gestion du Cabinet
- **Cabinet unique** : Configuration singleton avec informations centralisées
- **Interface dédiée** : Accès via l'administration Django
- **Validation stricte** : Un seul cabinet par instance

### 👩‍⚕️ Gestion des Sages-Femmes
- **Profils complets** : Informations personnelles et professionnelles
- **Trois statuts** : Titulaire, Collaborateur, Remplaçant
- **Gestion des remplacements** : Logique métier complète avec validations
- **Authentification** : Comptes utilisateurs automatiques

### 📅 Périodes d'Activité
- **Gestion intelligente** : Statut automatique basé sur les périodes
- **Validation métier** : Anti-chevauchement et période unique ouverte
- **Interface intuitive** : Statuts colorés et gestion HTMX
- **API REST** : Endpoints complets pour manipulation des données

### 🩺 Gestion des Actes Médicaux
- **Nomenclature complète** : Code et libellé des actes
- **Conventions tarifaires** : Gestion des tarifs par périodes avec interface minimaliste
- **Historique tarifaire** : Évolution des coûts dans le temps
- **Interface dédiée** : CRUD complet avec modales HTMX compactes

### 📋 Gestion des Prestations
- **Prestations par cadre d'exercice** : Organisation structurée des prestations
- **Champs étendus** : Suffixe, origine (LM/AT/MT/GP), statut actif/inactif, prescription obligatoire
- **Calculs automatiques** : Tarifs calculés automatiquement (cotation × coût conventionnel)
- **Interface moderne** : Formulaires et vues de détail avec design cohérent harmonisé
- **Recherche globale** : Recherche sur actes, cadres d'exercice, désignations et suffixes
- **Tri interactif** : Tri par colonnes cliquables (cadre, désignation, origine, acte, suffixe, prescription, cotation)
- **Filtrage intelligent** : Les prestations inactives sont automatiquement masquées
- **Affichage complet** : Désignations affichées intégralement sans troncature

### 📋 Gestion des Cadres d'Exercice
- **Configuration flexible** : Définition des différents cadres d'exercice
- **Administration simple** : Gestion via l'interface Django Admin uniquement
- **Structure modulaire** : Label et description pour chaque cadre

### 💰 Gestion des Caisses et Conditions de Paiement
- **Conditions de paiement personnalisables** : Définition de conditions avec désignation et pourcentage
- **Caisses configurables** : Association des caisses aux conditions de paiement éligibles
- **Interface dédiée** : CRUD complet avec modales HTMX pour gestion intuitive
- **Permissions différenciées** : Accès lecture seule pour collaborateurs, accès complet pour titulaires
- **Gestion par cases à cocher** : Sélection multiple des conditions éligibles par caisse

### 🔐 Authentification et Permissions Avancées
- **Accès conditionnel** : Seules les sages-femmes avec période active peuvent se connecter
- **Modèle utilisateur personnalisé** : `SageFemmeUser` basé sur email
- **Mise à jour automatique** : Statut utilisateur synchronisé avec les périodes
- **Permissions à deux niveaux** : Accès lecture pour tous, écriture pour titulaires
- **Gestion automatique des comptes** : Création automatique d'utilisateurs lors de l'ajout de sages-femmes

## Technologies Utilisées

### Backend
- **Django 5.2.5** + **Gunicorn** + **PostgreSQL** + **psycopg[binary] v3**
- **python-decouple** pour les variables d'environnement
- **DEBUG=False** par défaut (configuration production)

### Frontend
- **Tailwind CSS** - Framework CSS utility-first avec design minimaliste
- **HTMX** - Interactions AJAX modernes via attributs HTML
- **Alpine.js** - Réactivité côté client légère
- **Filtres Django personnalisés** - Formatage automatique de texte

### Infrastructure
- **Docker Compose** avec 3 services : Django + PostgreSQL + Nginx
- **Nginx** - Reverse proxy + service des fichiers statiques/media
- **Volumes persistants** pour DB, static et media

## Installation et Déploiement

### Déploiement Rapide
```bash
# Cloner le projet
git clone <url-du-repo>
cd maieutix

# Déployer l'application
docker-compose up -d --build

# L'application est disponible sur :
# http://localhost/ - Page d'accueil
# http://localhost/administration/sages-femmes/ - Gestion des sages-femmes
# http://localhost/admin/ - Interface Django Admin
```

### Première Connexion
```bash
# Créer un superutilisateur (optionnel, un admin existe déjà)
docker-compose exec web python manage.py createsuperuser

# Connexion admin par défaut :
# Email : admin@maieutix.nc
# Mot de passe : azerty
```

## Structure du Projet

```
maieutix/
├── core/                          # Application principale
│   ├── models/                    # Modèles de données modulaires
│   │   ├── cabinet.py             # Gestion du cabinet (singleton)
│   │   ├── sagefemme.py           # Gestion des sages-femmes
│   │   ├── periode_activite.py    # Gestion des périodes d'activité
│   │   ├── acte.py               # Gestion des actes et tarifs
│   │   ├── prestation.py          # Gestion des prestations
│   │   ├── cadre_exercice.py     # Gestion des cadres d'exercice
│   │   ├── condition_paiement.py  # Gestion des conditions de paiement
│   │   └── caisse.py             # Gestion des caisses
│   ├── views/                     # Vues organisées par domaine
│   │   ├── administration.py      # Interface d'administration
│   │   └── home.py               # Page d'accueil
│   ├── admin/                     # Configuration admin modulaire
│   │   ├── cabinet.py             # Admin Cabinet
│   │   ├── sagefemme.py           # Admin SageFemme  
│   │   ├── periode_activite.py    # Admin PeriodeActivite
│   │   ├── acte.py               # Admin Actes et Tarifs
│   │   ├── prestation.py          # Admin Prestations
│   │   ├── cadre_exercice.py     # Admin Cadres d'exercice
│   │   ├── condition_paiement.py  # Admin Conditions de paiement
│   │   └── caisse.py             # Admin Caisses
│   ├── tests/                     # Tests organisés (327 tests ✅)
│   │   ├── models/                # Tests des modèles
│   │   ├── views/                 # Tests des vues
│   │   ├── admin/                 # Tests de l'interface admin
│   │   └── integration/           # Tests d'intégration
│   ├── templates/core/            # Templates organisés
│   │   ├── base.html              # Template de base
│   │   ├── home.html              # Page d'accueil
│   │   ├── auth/                  # Templates d'authentification
│   │   └── administration/        # Templates d'administration
│   └── static/core/               # Assets statiques
├── authentication/                # Application d'authentification
│   ├── models.py                  # SageFemmeUser (modèle personnalisé)
│   ├── views.py                   # Vues de connexion/déconnexion
│   └── tests.py                   # Tests d'authentification (28 tests ✅)
├── context/                       # Documentation projet
│   ├── design-principles.md       # Principes de design
│   └── style-guide.md             # Guide de style
├── CLAUDE.md                      # Guide de développement complet
└── tests_readme.md               # Documentation des tests
```

## URLs Principales

- **/** - Page d'accueil avec navigation
- **/administration/sages-femmes/** - Interface de gestion des sages-femmes
- **/administration/actes/** - Interface de gestion des actes médicaux
- **/administration/prestations/** - Interface de gestion des prestations
- **/administration/caisses/** - Interface de gestion des caisses
- **/auth/connexion/** - Page de connexion
- **/auth/deconnexion/** - Déconnexion
- **/admin/** - Interface Django Admin

## API Administration

### Périodes d'Activité
- `POST /administration/sage-femme/{id}/periode/ajouter/` - Ajouter période
- `POST /administration/periode/{id}/modifier/` - Modifier période  
- `DELETE /administration/periode/{id}/supprimer/` - Supprimer période
- `POST /administration/periode/{id}/terminer/` - Terminer période

### CRUD Sages-Femmes (HTMX)
- `GET /administration/sages-femmes/list/` - Liste avec recherche/filtres
- `GET /administration/sage-femme/create/` - Formulaire création
- `GET /administration/sage-femme/{id}/update/` - Formulaire modification
- `GET /administration/sage-femme/{id}/detail/` - Vue détaillée
- `DELETE /administration/sage-femme/{id}/delete/` - Suppression

### CRUD Actes Médicaux (HTMX)
- `GET /administration/actes/list/` - Liste avec recherche
- `GET /administration/acte/create/` - Formulaire création
- `GET /administration/acte/{id}/update/` - Formulaire modification  
- `GET /administration/acte/{id}/detail/` - Vue détaillée
- `DELETE /administration/acte/{id}/delete/` - Suppression

### CRUD Prestations (HTMX)
- `GET /administration/prestations/list/` - Liste avec recherche globale et tri interactif
- `GET /administration/prestation/create/` - Formulaire création
- `GET /administration/prestation/{id}/update/` - Formulaire modification
- `GET /administration/prestation/{id}/detail/` - Vue détaillée
- `DELETE /administration/prestation/{id}/delete/` - Suppression

### CRUD Caisses (HTMX)
- `GET /administration/caisses/list/` - Liste avec recherche et compteurs
- `GET /administration/caisse/create/` - Formulaire création avec conditions éligibles
- `GET /administration/caisse/{id}/update/` - Formulaire modification
- `GET /administration/caisse/{id}/detail/` - Vue détaillée avec conditions associées
- `DELETE /administration/caisse/{id}/delete/` - Suppression

### Tarifs et Conventions
- `POST /administration/actes/{id}/ajouter-tarif/` - Ajouter période tarifaire
- `POST /administration/tarifs/{id}/modifier/` - Modifier période tarifaire
- `DELETE /administration/tarifs/{id}/supprimer/` - Supprimer période tarifaire

## Sauvegarde et Restauration

### Sauvegarde PostgreSQL (Recommandée)
```bash
# Sauvegarde complète avec horodatage
docker-compose exec db pg_dump -U maieutix_user -d maieutix_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Sauvegarde compressée (recommandée pour la production)
docker-compose exec db pg_dump -U maieutix_user -d maieutix_prod | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Sauvegarde avec structure + données séparées
docker-compose exec db pg_dump -U maieutix_user -d maieutix_prod --schema-only > schema_backup.sql
docker-compose exec db pg_dump -U maieutix_user -d maieutix_prod --data-only > data_backup.sql
```

### Restauration
```bash
# Restauration complète (base vide ou existante)
cat backup_20250830_073317.sql | docker-compose exec -T db psql -U maieutix_user -d maieutix_prod

# Alternative avec redirection
docker-compose exec db psql -U maieutix_user -d maieutix_prod < backup_20250830_073317.sql

# Restauration d'une sauvegarde compressée
zcat backup_20250830_073317.sql.gz | docker-compose exec -T db psql -U maieutix_user -d maieutix_prod
```

### Sauvegarde Django (Fixtures)
```bash
# Export au format JSON (lisible)
docker-compose exec web python manage.py dumpdata --natural-foreign --natural-primary --indent=2 > backup.json

# Export par application
docker-compose exec web python manage.py dumpdata core > core_backup.json
docker-compose exec web python manage.py dumpdata authentication > auth_backup.json

# Import des fixtures
docker-compose exec web python manage.py loaddata backup.json
```

### Notes Importantes
- **Utilisateurs inclus** : Les sauvegardes PostgreSQL incluent tous les comptes utilisateurs (superuser + sages-femmes)
- **Mots de passe** : Les mots de passe sont sauvegardés de manière sécurisée (hashés)
- **Données complètes** : Structure + données + contraintes + index
- **Permissions** : Tous les groupes et permissions Django

## Commandes Utiles

### Docker
```bash
# Gestion des services
docker-compose up -d --build       # Démarrer
docker-compose logs -f web          # Logs Django
docker-compose restart web          # Redémarrer Django
docker-compose down                 # Arrêter

# Accès aux conteneurs  
docker-compose exec web bash        # Shell Django
docker-compose exec web python manage.py shell  # Shell Django
docker-compose exec db psql -U maieutix_user maieutix_prod  # PostgreSQL
```

### Django
```bash
# Tests
docker-compose exec web python manage.py test                    # Tous les tests
docker-compose exec web python manage.py test --failfast         # Arrêt au premier échec
docker-compose exec web python manage.py test core.tests         # Tests core uniquement

# Migrations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Static files
docker-compose exec web python manage.py collectstatic --noinput
```

## Configuration

### Variables d'Environnement
```yaml
# Dans docker-compose.yml
environment:
  - SECRET_KEY=your-secret-key-here
  - DEBUG=False                    # Production par défaut
  - ALLOWED_HOSTS=localhost,127.0.0.1
  - POSTGRES_PASSWORD=maieutix_password
  - TZ=Pacific/Noumea             # Timezone NC (UTC+11)
```

### Base de Données
- **PostgreSQL 13** avec psycopg v3
- **Utilisateur** : `maieutix_user`
- **Base** : `maieutix_prod`
- **Volumes persistants** pour conservation des données

## Tests et Qualité

### Couverture de Tests : 100% ✅
- **698 tests** tous passent
- **Tests unitaires** : Modèles, vues, admin
- **Tests d'intégration** : Templates, navigation, API
- **Tests fonctionnels** : Authentification, permissions à deux niveaux
- **Tests de validation** : Règles métier, contraintes DB

### Organisation des Tests
```
core/tests/
├── models/                    # Tests des modèles (120+ tests)
├── views/                     # Tests des vues (130+ tests)  
├── admin/                     # Tests de l'admin (50+ tests)
└── integration/              # Tests d'intégration (27+ tests)
authentication/tests.py        # Tests d'authentification (28 tests)
```

Pour plus de détails, voir `tests_readme.md`.

## Architecture et Design

### Principes de Design
- **Modulaire** : Séparation claire des responsabilités
- **Extensible** : Architecture permettant l'ajout de nouvelles fonctionnalités
- **Testable** : Couverture de tests complète
- **Maintenable** : Code documenté et structuré

### Palette de Couleurs
- **Primary** : #2D4B73 (Bleu foncé)
- **Secondary** : #253C59 (Bleu plus foncé)
- **Accent** : #99B4BF (Bleu clair)
- **Highlight** : #D9BA23 (Jaune)
- **Warning** : #BF8D30 (Orange)

### Composants UI
- **Navigation** : Navbar responsive avec logo
- **Modals** : Formulaires en overlay avec HTMX
- **Tables** : Listes avec tri interactif, recherche et pagination
- **Tri dynamique** : En-têtes cliquables avec indicateurs visuels (▲▼)
- **Notifications** : Système de feedback utilisateur
- **Statuts** : Badges colorés pour les états
- **Interface harmonisée** : Design cohérent entre toutes les pages d'administration

## Règles Métier

### Périodes d'Activité
1. **Une seule période ouverte** par sage-femme (sans date de fin)
2. **Anti-chevauchement** : Aucune période ne peut se chevaucher
3. **Statut automatique** : Calculé en temps réel
4. **Mise à jour du compte** : Statut utilisateur synchronisé automatiquement

### Authentification
- **Email obligatoire** pour la connexion
- **Seules les sages-femmes actives** peuvent se connecter
- **Création automatique** des comptes lors de l'ajout d'une sage-femme
- **Mot de passe par défaut** : `azerty` (à changer lors de la première connexion)

### Permissions à Deux Niveaux
| Type d'utilisateur | Menu Admin | Voir listes | Voir détails | Créer | Modifier | Supprimer | Django Admin |
|---------------------|------------|-------------|--------------|-------|----------|-----------|--------------|
| **Superuser**       | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Titulaire**       | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Collaborateur**   | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Remplaçant**      | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

## Développement

### Ajout de Fonctionnalités
1. **Suivre l'architecture modulaire** (models/views/admin/tests séparés)
2. **Écrire les tests d'abord** (TDD encouragé)
3. **Respecter les conventions** définies dans `CLAUDE.md`
4. **Tester l'intégration** avec les fonctionnalités existantes

### Guide Complet
Consultez `CLAUDE.md` pour :
- Guide de développement détaillé
- Conventions de code
- Architecture modulaire
- Commandes Docker
- Bonnes pratiques

## Support et Documentation

- **CLAUDE.md** : Guide de développement complet
- **tests_readme.md** : Documentation détaillée des tests  
- **context/design-principles.md** : Principes de design
- **context/style-guide.md** : Guide de style visuel

## Sécurité

- **CSRF Protection** : Activée sur toutes les vues
- **Authentification requise** : Pour toutes les vues d'administration
- **Validation stricte** : Côté serveur et client
- **Configuration production** : DEBUG=False par défaut

---

**Projet développé avec ❤️ pour les sages-femmes de Nouvelle-Calédonie**