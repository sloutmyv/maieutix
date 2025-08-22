# Guide de Développement - Maieutix

## Core Technologies

### Backend
- **Django 5.2.5** + **Gunicorn** + **PostgreSQL** + **psycopg[binary] v3**
- **python-decouple** for environment variables
- **DEBUG=False** by default (production-like development)

### Frontend
- **Tailwind CSS** (utility-first styling)
- **HTMX** (AJAX interactions via HTML attributes)
- **Alpine.js** (lightweight reactivity)

### Infrastructure
- **Docker Compose** with 3 services: Django + PostgreSQL + Nginx
- **Nginx** (reverse proxy + static/media files)
- **Persistent volumes** for DB, static, media

### Principe de Design
- Comprehensive design principles in `/context/design-principles.md`
- Brand style guide in `/context/style-guide.md`
- When making visual (front-end, UI/UX) changes, always refer to these files for guidance

## Architecture Modulaire
Chaque composant métier suit une structure organisée :

```
core/
├── models/domaine.py      # Data logic
├── views/domaine.py       # Business logic + HTMX responses
├── admin/domaine.py       # Admin interface
└── templates/core/domaine/ # UI templates
    ├── list.html
    ├── detail.html
    └── form.html
```

### Conventions de Développement

1. **Modularité** : Chaque domaine métier dans sa propre structure
2. **Séparation des responsabilités** : Models, Views, Admin, Templates séparés
3. **Nommage cohérent** : Utiliser le nom du domaine pour tous les fichiers
4. **Templates** : Organisation hiérarchique dans templates/core/

## Commandes Utiles

### Docker
```bash
# Lancer l'environnement de développement
docker-compose up -d --build

# Voir les logs
docker-compose logs -f web

# Accéder au conteneur Django
docker-compose exec web bash

# Migrations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Collecte des fichiers statiques
docker-compose exec web python manage.py collectstatic --noinput
```

### Lint et Tests
```bash
# TODO: Ajouter les commandes de lint/test quand configurées
```