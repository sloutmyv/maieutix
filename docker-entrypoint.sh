#!/bin/bash

# Script d'entrée pour le conteneur Django

set -e

echo "Attendre que PostgreSQL soit prêt..."
while ! nc -z db 5432; do
  echo "PostgreSQL n'est pas encore prêt - attendre..."
  sleep 1
done

echo "PostgreSQL est prêt!"

# Appliquer les migrations
echo "Application des migrations..."
python manage.py migrate --noinput

# Collecter les fichiers statiques
echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Créer un superutilisateur si il n'existe pas
echo "Création du superutilisateur par défaut..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@maieutix.com', 'admin123')
    print('Superutilisateur créé: admin/admin123')
else:
    print('Superutilisateur existe déjà')
EOF

echo "Démarrage du serveur de production avec Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 maieutix.wsgi:application