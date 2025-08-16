# Guide de Développement - Maieutix

## Technologies Frontend

### Stack Technique
```
Frontend
├── Tailwind CSS (Styling)
├── HTMX (AJAX Interactions)
└── Alpine.js (Client Reactivity)
```

### Palette de Couleurs
```css
/* Color Theme */
.Voyages-1-hex { color: #2D4B73; } /* Bleu foncé principal */
.Voyages-2-hex { color: #253C59; } /* Bleu très foncé */
.Voyages-3-hex { color: #99B4BF; } /* Bleu clair/gris */
.Voyages-4-hex { color: #D9BA23; } /* Jaune doré */
.Voyages-5-hex { color: #BF8D30; } /* Orange/brun */
```

### Principe de Design
- **Design sobre et épuré**
- Interface minimaliste et intuitive
- Utilisation cohérente de la palette de couleurs

## Architecture Modulaire

Chaque composant métier suit une structure organisée :

```
core/
├── models/
│   └── domaine.py          # Logique de données
├── views/
│   └── domaine.py          # Logique métier et interaction
├── admin/
│   └── domaine.py          # Configuration interface d'administration
└── templates/core/domaine/  # Interface utilisateur
```

### Conventions de Développement

1. **Modularité** : Chaque domaine métier dans sa propre structure
2. **Séparation des responsabilités** : Models, Views, Admin, Templates séparés
3. **Nommage cohérent** : Utiliser le nom du domaine pour tous les fichiers
4. **Templates** : Organisation hiérarchique dans templates/core/

### Technologies à Intégrer

- **Tailwind CSS** : Framework CSS utility-first pour le styling
- **HTMX** : Interactions AJAX modernes sans JavaScript complexe
- **Alpine.js** : Réactivité côté client légère

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