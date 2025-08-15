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
│   ├── settings/         # Paramètres du projet (séparés par environnement)
│   │   ├── __init__.py
│   │   ├── base.py       # Paramètres communs
│   │   ├── dev.py        # Paramètres de développement
│   │   └── prod.py       # Paramètres de production
│   ├── urls.py           # Configuration des URLs
│   ├── wsgi.py           # Configuration WSGI
│   └── asgi.py           # Configuration ASGI
├── .env                   # Variables d'environnement (à ne pas commiter)
├── manage.py              # Script de gestion Django
└── requirements.txt       # Dépendances Python
```

## Installation

1. **Cloner le projet**
   ```bash
   git clone <url-du-repo>
   cd maieutix
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer PostgreSQL et les variables d'environnement**
   ```bash
   # Installer PostgreSQL (sur macOS avec Homebrew)
   brew install postgresql
   brew services start postgresql
   
   # Créer la base de données et l'utilisateur
   createdb mydb_dev
   psql mydb_dev -c "CREATE USER myuser_dev WITH PASSWORD 'password_dev';"
   psql mydb_dev -c "GRANT ALL PRIVILEGES ON DATABASE mydb_dev TO myuser_dev;"
   psql mydb_dev -c "ALTER USER myuser_dev CREATEDB;"
   
   # Le fichier .env contient déjà les variables configurées
   ```

5. **Appliquer les migrations**
   ```bash
   python manage.py migrate
   ```

6. **Créer un superutilisateur**
   ```bash
   python manage.py createsuperuser
   # Ou utiliser le superutilisateur par défaut : admin / admin123
   ```

7. **Lancer le serveur de développement**
   ```bash
   python manage.py runserver
   # Accéder à http://127.0.0.1:8000/admin/
   ```

## Commandes utiles

- `python manage.py runserver` - Démarrer le serveur de développement
- `python manage.py migrate` - Appliquer les migrations
- `python manage.py makemigrations` - Créer de nouvelles migrations
- `python manage.py createsuperuser` - Créer un utilisateur administrateur
- `python manage.py collectstatic` - Collecter les fichiers statiques
- `python manage.py test` - Exécuter les tests

## Technologies utilisées

- **Django 5.2.5** - Framework web Python (dernière version)
- **python-decouple** - Gestion des variables d'environnement
- **psycopg[binary]** - Adaptateur PostgreSQL moderne (version 3)
- **PostgreSQL** - Base de données pour développement et production
- **Gunicorn** - Serveur WSGI pour la production
- **Nginx** - Serveur web et proxy inverse

## Notes importantes

### Environnement virtuel
Le projet nécessite un environnement virtuel Python propre. En cas de problème avec psycopg, recréez l'environnement :
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Base de données
- Le projet utilise PostgreSQL en développement et production
- psycopg[binary] (version 3) est utilisé pour une meilleure compatibilité
- Un superutilisateur par défaut est disponible : `admin` / `admin123`

## Configuration des environnements

Le projet utilise une configuration séparée pour les différents environnements :

- **`settings/base.py`** - Configuration commune à tous les environnements
- **`settings/dev.py`** - Configuration spécifique au développement
- **`settings/prod.py`** - Configuration pour la production

### Variables d'environnement

Le fichier `.env` contient les variables d'environnement. Les principales variables sont :

- `SECRET_KEY` - Clé secrète Django
- `DEBUG` - Mode debug (True/False)
- `DJANGO_SETTINGS_MODULE` - Module de settings à utiliser
- `ALLOWED_HOSTS` - Hosts autorisés (séparés par des virgules)
- `LANGUAGE_CODE` - Code de langue par défaut
- `TIME_ZONE` - Fuseau horaire

### Déploiement en production

Pour la production, configurez les variables suivantes dans votre `.env` :

```bash
DEBUG=False
DJANGO_SETTINGS_MODULE=maieutix.settings.prod
ALLOWED_HOSTS=votre-domaine.com
SECRET_KEY=votre-cle-secrete-longue-et-complexe
DB_NAME=maieutix_prod
DB_USER=maieutix_user
DB_PASSWORD=mot-de-passe-securise
DB_HOST=localhost
DB_PORT=5432
```

## Déploiement avec Docker

### Prérequis
- Docker et Docker Compose installés

### Déploiement rapide
```bash
# Cloner le projet
git clone <url-du-repo>
cd maieutix

# Déployer en production
docker-compose up -d --build

# Accéder à l'application
# http://localhost (via Nginx)
# http://localhost/admin/ (Interface admin)
```

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

L'application `core` contient les fonctionnalités principales du projet. Elle est déjà configurée et prête à être développée.