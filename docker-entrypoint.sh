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

# Création automatique du superutilisateur désactivée
# Utilisez admin@maieutix.nc avec mot de passe azerty si besoin

echo "Démarrage du serveur de production avec Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 maieutix.wsgi:application