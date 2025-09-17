# Maieutix

**Plateforme de gestion pour sages-femmes en Nouvelle-Calédonie**

Un projet Django moderne pour la gestion des activités professionnelles des sages-femmes, développé avec une architecture modulaire et une interface utilisateur intuitive.

## Statut du Projet ✅

- **Tests** : 1135+ tests passent (100% ✅) - Couverture complète avec 435+ nouveaux tests (patients + consultations + rééducation périnée)
- **Gestion Patients** : Système complet avec tests exhaustifs (model/form/view/admin/intégration)
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

### 🏥 Gestion des Patients ✨ NOUVEAU
- **Types de patients** : Femmes et bébés avec logique métier spécialisée et règles d'assurance
- **Relation mère-enfant** : Association automatique des bébés à leur mère avec héritage des informations
- **Recherche intelligente** : Autocomplétion pour la sélection des mères avec pré-remplissage automatique
- **Formulaires adaptatifs** : Champs conditionnels selon le type (masquage nom JF, profession pour bébés)
- **Gestion d'assurance stricte** : Bébés toujours ayants droit, validation des règles métier complètes
- **Sécurisation des dates** : Validation côté serveur et client pour empêcher dates futures
- **Alertes grossesses** : Affichage en rouge des grossesses dépassées avec indicateur visuel
- **Gestion des patients inactifs** : Affichage grisé avec possibilité de réactivation
- **Interface moderne** : Design cohérent avec système de formulaires conditionnels et modales
- **Tests complets** : 104 tests exhaustifs (19 modèles + 19 formulaires + 27 vues + 27 admin + 12 intégration)
- **Consultations obstétricales complètes** : 93 tests dédiés (25 modèles + 20 formulaires + 15 vues + 18 admin + 15 intégration)
- **Validation robuste** : Règles métier strictes avec validation des numéros de téléphone français
- **API REST** : Endpoints pour recherche de mères et récupération de détails pour pré-remplissage
- **Dossiers médicaux complets** : Page de détail avec onglets organisés (Informations, Historique, Échographie, Dossier)
- **Antécédents médicaux** : Formulaire complet avec sections biométrie, ATCD médicaux/obstétricaux/familiaux/chirurgicaux
- **Calcul IMC automatique** : Interface compacte avec calcul temps réel et interprétation (surpoids, normal, etc.)
- **Frottis cervico-vaginaux** : Gestion dynamique des FCV avec ajout/suppression en live
- **Sauvegarde automatique** : Auto-save des antécédents avec feedback utilisateur
- **Interface ultra-compacte** : Design minimaliste optimisé pour l'efficacité médicale
- **Consultations gynécologiques** : Système complet de consultation avec formulaire inline compact
- **Gestion dynamique** : Ajout/suppression de consultations sans rechargement de page
- **Traçabilité complète** : Enregistrement automatique de la sage-femme créatrice et horodatage
- **Interface harmonisée** : Contraste amélioré et design cohérent avec modals de détail minimalistes
- **Consultations obstétricales** ✨ NOUVEAU : Interface pour le suivi de grossesse avec calendrier médical interactif
- **Calendrier de grossesse intelligent** : Calcul automatique des jalons médicaux (HT21, MST2, échographies, HGPO, Rophylac)
- **Gestion DDG dynamique** : Modification de la date de début de grossesse avec synchronisation temps réel
- **Mise à jour sans rechargement** : Interface AJAX pour maintenir l'utilisateur sur l'onglet actuel
- **Données médicales de grossesse** : Formulaire complet avec 3 sections (Obstétrique, Sérologies & Dépistages, Analyses complémentaires)
- **Code couleur médical** : Système intelligent de coloration (vert/orange/rouge) pour surveillance des résultats critiques
- **Auto-sauvegarde** : Sauvegarde automatique des données médicales avec feedback visuel utilisateur
- **Listes déroulantes standardisées** : Valeurs pré-définies pour analyses médicales (GS/Rh, sérologies, etc.)
- **Layout optimisé** : Organisation en 2 lignes de 5 éléments pour la section Sérologies & Dépistages
- **Système de consultations obstétricales** ✨ NOUVEAU : Gestion complète des consultations de suivi de grossesse
- **Interface unifiée** : Formulaires inline identiques aux consultations gynécologiques pour cohérence UX
- **Historique complet** : Affichage chronologique avec détails (TA, poids, IMC, motif, examen, prescription)
- **Actions CRUD complètes** : Création, lecture, modification et suppression avec confirmations utilisateur
- **Calcul automatique SA** ✨ NOUVEAU : Semaines d'Aménorrhée calculées automatiquement à partir de la DDG
- **Affichage SA intégré** : Badge SA visible dans l'historique, détails consultation et interface admin
- **Traçabilité temporelle** : SA enregistrée à chaque consultation pour suivi précis de l'évolution
- **Interface admin réorganisée** : "6.1.3.2 Consultations Obstétricales" et "6.1.3.1 Données de grossesse" (sections renommées)
- **Tests exhaustifs** : 93 tests dédiés couvrant modèles, formulaires, vues, admin et intégration complète
- **Harmonisation visuelle complète** ✨ NOUVEAU : Système de couleurs cohérent par spécialité médicale
- **Code couleurs par section** : Rose pour gynécologique, bleu pour obstétrical, vert pour EPP, violet pour préparation naissance
- **Interface unifiée** : Boutons, formulaires, badges et fonds harmonisés avec les couleurs des logos respectifs
- **Cohérence UX** : Même couleur pour tous les éléments d'une section (boutons, focus, spinners, badges)
- **Entretiens prénataux précoces (EPP)** ✨ NOUVEAU : Système complet de gestion des entretiens prénataux
- **Formulaires EPP** : Interface complète avec calcul automatique SA et validation métier
- **Consultation préparation naissance** ✨ NOUVEAU : Gestion des consultations de préparation à la naissance
- **Rééducation du périnée** ✨ NOUVEAU : Module complet de gestion des séances de rééducation périnéale
- **Interface harmonisée** : Présentation identique aux autres sections avec fond gris et polices cohérentes
- **Gestion des séances** : Numérotation automatique, calcul du prochain numéro, traçabilité complète
- **CRUD complet** : Création, consultation, modification et suppression des séances avec confirmations
- **Modal HTMX** : Interface fluide sans rechargement de page pour toutes les opérations
- **Validation métier** : Restriction aux femmes, dates non futures, numéros de séance ≥ 1
- **Historique détaillé** : Affichage chronologique avec badges de séances et informations complètes
- **Tests exhaustifs** : 135 tests dédiés couvrant modèles, formulaires, vues, admin et intégration complète

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
│   │   ├── caisse.py             # Gestion des caisses
│   │   ├── patient.py            # Gestion des patients
│   │   ├── antecedents.py        # Gestion des antécédents médicaux
│   │   ├── consultation_gynecologique.py  # Gestion des consultations gynécologiques
│   │   ├── consultation_obstetricale.py   # Gestion des consultations obstétricales ✨ NOUVEAU
│   │   └── donnees_grossesse.py           # Gestion des données médicales de grossesse
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
│   │   ├── caisse.py             # Admin Caisses
│   │   ├── patient.py            # Admin Patients
│   │   ├── antecedents.py        # Admin Antécédents médicaux
│   │   ├── consultation_gynecologique.py  # Admin Consultations gynécologiques
│   │   ├── consultation_obstetricale.py   # Admin Consultations obstétricales ✨ NOUVEAU
│   │   └── donnees_grossesse.py           # Admin Données de grossesse
│   ├── tests/                     # Tests organisés (908+ tests ✅)
│   │   ├── models/                # Tests des modèles (144+ tests)
│   │   │   ├── test_patient.py    # 19 tests modèle Patient ✨
│   │   │   └── test_consultation_gynecologique.py  # 24 tests modèle Consultations ✨
│   │   ├── views/                 # Tests des vues (152+ tests)
│   │   │   ├── test_patient_views.py  # 27 tests vues Patient ✨
│   │   │   └── test_consultation_gynecologique_views.py  # 22 tests vues Consultations ✨
│   │   ├── admin/                 # Tests de l'interface admin (77+ tests)
│   │   │   ├── test_patient_admin.py  # 27 tests admin Patient ✨
│   │   │   └── test_consultation_gynecologique_admin.py  # 27 tests admin Consultations ✨
│   │   ├── forms/                 # Tests des formulaires ✨ NOUVEAU
│   │   │   ├── test_patient_forms.py  # 19 tests formulaires Patient
│   │   │   └── test_consultation_gynecologique_forms.py  # 20 tests formulaires Consultations ✨
│   │   └── integration/           # Tests d'intégration (52+ tests)
│   │       ├── test_patient_integration.py  # 12 tests intégration Patient ✨
│   │       └── test_consultation_gynecologique_integration.py  # 13 tests intégration Consultations ✨
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
- **/patients/** - Interface de gestion des patients
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

### CRUD Patients (HTMX) ✨ NOUVEAU
- `GET /patients/` - Liste avec recherche globale et filtrage (inclut patients inactifs)
- `GET /patients/create/` - Formulaire création avec champs conditionnels selon le type
- `GET /patients/{id}/edit/` - Formulaire modification avec validation complète
- `GET /patients/{id}/` - Vue détaillée du patient avec onglets (Informations, Historique, Échographie, Dossier)
- `POST /patients/{id}/toggle-active/` - Activation/désactivation avec JSON response
- `GET /patients/search-meres/` - API autocomplétion pour recherche de mères (femmes actives seulement)
- `GET /patients/{id}/details-for-baby/` - API pour récupération des détails mère (pré-remplissage bébé)
- `GET /patients/{id}/antecedents/` - API pour récupération des antécédents existants
- `POST /patients/save-antecedents/` - API AJAX pour sauvegarde des antécédents avec auto-save
- `GET /patients/{id}/consultations/` - API pour récupération de l'historique des consultations gynécologiques
- `GET /patients/{id}/consultation/quick-form/` - API pour affichage du formulaire de consultation inline
- `POST /patients/{id}/consultation/save-quick/` - API AJAX pour sauvegarde des consultations avec traçabilité
- `GET /patients/consultation/{id}/` - API pour affichage modal de détail d'une consultation
- `POST /patients/consultation/{id}/delete/` - API pour suppression de consultation avec confirmation
- `POST /patients/{id}/update-ddg/` - API AJAX pour mise à jour de la date de début de grossesse ✨ NOUVEAU
- `GET /patients/{id}/reload-pregnancy-calendar/` - API pour rechargement du calendrier de grossesse ✨ NOUVEAU
- `GET /patients/{id}/consultation-obstetricale/quick-form/` - API pour formulaire consultation obstétricale inline ✨ NOUVEAU
- `POST /patients/{id}/consultation-obstetricale/save-quick/` - API AJAX pour sauvegarde consultation obstétricale ✨ NOUVEAU
- `GET /patients/consultation-obstetricale/{id}/` - API pour détail modal consultation obstétricale ✨ NOUVEAU
- `POST /patients/consultation-obstetricale/{id}/delete/` - API pour suppression consultation obstétricale ✨ NOUVEAU
- `GET /patients/{id}/entretien-prenatal-precoce/quick-form/` - API pour formulaire EPP inline ✨ NOUVEAU
- `POST /patients/{id}/entretien-prenatal-precoce/save-quick/` - API AJAX pour sauvegarde EPP ✨ NOUVEAU
- `GET /patients/entretien-prenatal-precoce/{id}/` - API pour détail modal EPP ✨ NOUVEAU
- `POST /patients/entretien-prenatal-precoce/{id}/delete/` - API pour suppression EPP ✨ NOUVEAU
- `GET /reeducation-perinee/modal/{patient_id}/` - API pour formulaire modal rééducation périnée ✨ NOUVEAU
- `POST /reeducation-perinee/save/` - API AJAX pour sauvegarde séances rééducation périnée ✨ NOUVEAU
- `GET /patients/{id}/reeducations-perinee/` - API pour historique rééducation d'une patiente ✨ NOUVEAU
- `GET /reeducation-perinee/{id}/` - API pour détail modal séance rééducation ✨ NOUVEAU
- `POST /reeducation-perinee/{id}/delete/` - API pour suppression séance avec confirmation ✨ NOUVEAU

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
- **1135+ tests** tous passent - +435 tests patients, consultations gynécologiques, obstétricales et rééducation périnée ajoutés
- **Tests unitaires** : Modèles, vues, admin, formulaires
- **Tests d'intégration** : Templates, navigation, API, workflows complets
- **Tests fonctionnels** : Authentification, permissions à deux niveaux
- **Tests de validation** : Règles métier strictes, contraintes DB, validation téléphone français
- **Tests patients exhaustifs** : Création/modification/suppression femmes et bébés, relations mère-enfant
- **Tests consultations gynécologiques** : 106 tests complets (modèles, formulaires, vues, admin, intégration)
- **Tests consultations obstétricales** : 93 tests dédiés avec calcul automatique SA (25 modèles + 20 formulaires + 15 vues + 18 admin + 15 intégration)
- **Tests rééducation périnée** : 135 tests complets (28 modèles + 38 formulaires + 26 vues + 32 admin + 11 intégration)

### Organisation des Tests
```
core/tests/
├── models/                    # Tests des modèles (168+ tests)
│   ├── test_patient.py        # 19 tests Patient ✨
│   ├── test_consultation_gynecologique.py  # 24 tests Consultations gynéco ✨
│   ├── test_consultation_obstetricale.py   # 25 tests Consultations obstétricales ✨
│   └── test_reeducation_perinee.py         # 28 tests Rééducation périnée ✨ NOUVEAU
├── views/                     # Tests des vues (176+ tests)
│   ├── test_patient_views.py  # 27 tests vues Patient ✨
│   ├── test_consultation_gynecologique_views.py  # 22 tests vues Consultations gynéco ✨
│   ├── test_consultation_obstetricale_views.py     # 15 tests vues Consultations obstétricales ✨
│   └── test_reeducation_perinee_views.py           # 26 tests vues Rééducation périnée ✨ NOUVEAU
├── admin/                     # Tests de l'admin (104+ tests)
│   ├── test_patient_admin.py  # 27 tests admin Patient ✨
│   ├── test_consultation_gynecologique_admin.py   # 27 tests admin Consultations gynéco ✨
│   ├── test_consultation_obstetricale_admin.py     # 18 tests admin Consultations obstétricales ✨
│   └── test_reeducation_perinee_admin.py           # 32 tests admin Rééducation périnée ✨ NOUVEAU
├── forms/                     # Tests des formulaires ✨
│   ├── test_patient_forms.py  # 19 tests formulaires Patient
│   ├── test_consultation_gynecologique_forms.py   # 20 tests formulaires Consultations gynéco ✨
│   ├── test_consultation_obstetricale_forms.py     # 20 tests formulaires Consultations obstétricales ✨
│   └── test_reeducation_perinee_forms.py           # 38 tests formulaires Rééducation périnée ✨ NOUVEAU
└── integration/              # Tests d'intégration (71+ tests)
    ├── test_patient_integration.py  # 12 tests intégration Patient ✨
    ├── test_consultation_gynecologique_integration.py  # 13 tests intégration Consultations gynéco ✨
    ├── test_consultation_obstetricale_integration_simple.py  # 15 tests intégration Consultations obstétricales ✨
    └── test_reeducation_perinee_integration.py          # 11 tests intégration Rééducation périnée ✨ NOUVEAU
authentication/tests.py        # Tests d'authentification (28 tests)
```

### Tests Patients - Détails de Couverture ✨
- **Modèles** : Validation des règles métier, relations mère-enfant, calculs d'âge
- **Formulaires** : Validation des champs, widgets, logique conditionnelle selon le type
- **Vues** : CRUD complet, API endpoints, authentification, HTMX responses
- **Admin** : Interface admin, méthodes personnalisées, filtres, recherche, fieldsets
- **Intégration** : Workflows complets, création mère → bébé, activation/désactivation

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

### Système de Couleurs par Spécialité ✨ NOUVEAU
- **Consultations gynécologiques** : Rose (#ec4899) - Couleur chaude et féminine
- **Consultations obstétricales** : Bleu (#3b82f6) - Couleur professionnelle et apaisante
- **Entretiens prénataux précoces** : Vert (#16a34a) - Couleur de vie et de croissance
- **Consultations préparation naissance** : Violet (#7c3aed) - Couleur de transformation et préparation
- **Rééducation du périnée** : Bleu (#2563eb) - Couleur médicale et technique pour la rééducation
- **Harmonisation complète** : Boutons, formulaires, badges, focus, spinners coordonnés par spécialité

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