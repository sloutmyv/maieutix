# Utiliser Python 3.12 comme image de base
FROM python:3.12-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Créer un utilisateur non-root
RUN groupadd -r django && useradd -r -g django django

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Copier et configurer le script d'entrée
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Créer les répertoires nécessaires
RUN mkdir -p /app/staticfiles /app/media

# Changer les permissions
RUN chown -R django:django /app

# Basculer vers l'utilisateur django
USER django

# Exposer le port
EXPOSE 8000

# Commande par défaut
CMD ["/app/docker-entrypoint.sh"]