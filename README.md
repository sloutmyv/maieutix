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

4. **Configurer les variables d'environnement**
   ```bash
   # Le fichier .env contient déjà les variables par défaut pour le développement
   # Modifiez les valeurs selon vos besoins
   ```

5. **Appliquer les migrations**
   ```bash
   python manage.py migrate
   ```

6. **Créer un superutilisateur**
   ```bash
   python manage.py createsuperuser
   ```

7. **Lancer le serveur de développement**
   ```bash
   python manage.py runserver
   ```

## Commandes utiles

- `python manage.py runserver` - Démarrer le serveur de développement
- `python manage.py migrate` - Appliquer les migrations
- `python manage.py makemigrations` - Créer de nouvelles migrations
- `python manage.py createsuperuser` - Créer un utilisateur administrateur
- `python manage.py collectstatic` - Collecter les fichiers statiques
- `python manage.py test` - Exécuter les tests

## Technologies utilisées

- **Django 5.0** - Framework web Python
- **python-decouple** - Gestion des variables d'environnement
- **SQLite** - Base de données par défaut (développement)
- **PostgreSQL** - Base de données recommandée pour la production

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

## Application Core

L'application `core` contient les fonctionnalités principales du projet. Elle est déjà configurée et prête à être développée.