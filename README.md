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
│   ├── settings.py       # Paramètres du projet
│   ├── urls.py           # Configuration des URLs
│   ├── wsgi.py           # Configuration WSGI
│   └── asgi.py           # Configuration ASGI
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

4. **Appliquer les migrations**
   ```bash
   python manage.py migrate
   ```

5. **Créer un superutilisateur**
   ```bash
   python manage.py createsuperuser
   ```

6. **Lancer le serveur de développement**
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
- **SQLite** - Base de données par défaut (développement)

## Application Core

L'application `core` contient les fonctionnalités principales du projet. Elle est déjà configurée et prête à être développée.