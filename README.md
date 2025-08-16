# Maieutix

Un projet Django pour la gestion et le développement d'applications web.

## Structure du projet

```
maieutix/
├── core/                   # Application principale
│   ├── migrations/        # Migrations de base de données
│   ├── admin.py          # Interface d'administration
│   ├── apps.py           # Configuration de l'application
│   ├── models.py         # Modèles de données
│   ├── tests.py          # Tests unitaires
│   └── views.py          # Vues de l'application
├── maieutix/              # Configuration du projet Django
│   ├── settings.py       # Configuration unifiée
│   ├── urls.py           # Configuration des URLs
│   ├── wsgi.py           # Configuration WSGI
│   └── asgi.py           # Configuration ASGI
├── docker-compose.yml     # Configuration Docker
├── Dockerfile            # Image Docker Django
├── nginx.conf            # Configuration Nginx
├── docker-entrypoint.sh  # Script de démarrage
├── manage.py             # Script de gestion Django
└── requirements.txt      # Dépendances Python
```

## Installation avec Docker

Ce projet utilise Docker pour une configuration simplifiée et cohérente.

### Déploiement rapide
```bash
# Cloner le projet
git clone <url-du-repo>
cd maieutix

# Déployer l'application
docker-compose up -d --build

# Accéder à l'application
# http://localhost/ (Page d'accueil Hello World)
# http://localhost/admin/ (Interface admin - admin/admin123)
```

## Technologies utilisées

### Backend
- **Django 5.2.5** - Framework web Python
- **python-decouple** - Gestion des variables d'environnement
- **psycopg[binary]** - Adaptateur PostgreSQL moderne (version 3)
- **PostgreSQL** - Base de données
- **Gunicorn** - Serveur WSGI pour la production

### Frontend
- **Tailwind CSS** - Framework CSS utility-first
- **HTMX** - Interactions AJAX modernes
- **Alpine.js** - Réactivité côté client légère

### Infrastructure
- **Nginx** - Serveur web et proxy inverse
- **Docker** - Containerisation et déploiement

## Notes importantes

### Base de données
- PostgreSQL avec psycopg[binary] (version 3)
- Superutilisateur par défaut : `admin` / `admin123`

### Configuration
- Configuration unifiée dans `maieutix/settings.py`
- Variables d'environnement gérées via python-decouple
- Mode production activé par défaut dans Docker (`DEBUG=False`)

### Prérequis
- Docker et Docker Compose installés

### Commandes Docker essentielles
```bash
# Démarrer les services
docker-compose up -d --build

# Voir les logs
docker-compose logs -f
docker-compose logs -f web    # Logs Django uniquement
docker-compose logs -f db     # Logs PostgreSQL uniquement

# Arrêter les services
docker-compose down

# Redémarrer un service
docker-compose restart web

# Accéder aux conteneurs
docker-compose exec web bash     # Conteneur Django
docker-compose exec db psql -U maieutix_user maieutix_prod  # Base de données

# Sauvegarder la base de données
docker-compose exec db pg_dump -U maieutix_user maieutix_prod > backup.sql

# Supprimer tout (attention: données perdues!)
docker-compose down -v
```

### Configuration Docker
- **services** : Django + PostgreSQL + Nginx
- **volumes** : Données persistantes (DB, static, media)
- **networks** : Communication sécurisée entre conteneurs
- **healthchecks** : Surveillance automatique des services

### Variables importantes (docker-compose.yml)
```yaml
environment:
  - SECRET_KEY=your-secret-key-change-in-production
  - DEBUG=False
  - ALLOWED_HOSTS=localhost,127.0.0.1
  - POSTGRES_PASSWORD=maieutix_password
```

### Services exposés
- **Port 80** : Application complète (Nginx + Django)
- **Page d'accueil** : `http://localhost/` (Hello World)
- **Administration** : `http://localhost/admin/` (admin/admin123)
- **Volumes persistants** : Base de données, fichiers media et static

## Application Core

L'application `core` contient les fonctionnalités principales du projet avec une architecture modulaire :

```
core/
├── models/
│   ├── __init__.py           # Import centralisé des modèles
│   └── cabinet.py            # Modèle Cabinet (singleton)
├── admin/
│   ├── __init__.py           # Import centralisé des admins
│   └── cabinet.py            # Interface admin Cabinet
├── templates/core/           # Templates Django
└── static/core/              # CSS/JS personnalisés
```

### Fonctionnalités
- **Cabinet** : Modèle singleton (un seul cabinet par application)
- **Architecture modulaire** : Séparation models/admin par domaine
- **Interface moderne** : Tailwind CSS + HTMX + Alpine.js
- **Timezone** : UTC+11 (Pacific/Noumea)

### Développement
- **Design** : Interface sobre et épurée
- **Palette de couleurs** : Thème Voyages (#2D4B73, #253C59, #99B4BF, #D9BA23, #BF8D30)
- **Guide complet** : Voir `CLAUDE.md` pour les détails de développement