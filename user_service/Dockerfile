# ============================================================
# USER SERVICE - Dockerfile
# Image Python slim pour réduire la taille de l'image finale.
# ============================================================
FROM python:3.11-slim

WORKDIR /app

# Copier et installer les dépendances d'abord (cache Docker layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Port exposé (documentation — le mapping réel est dans docker-compose)
EXPOSE 8000

# Démarrage via gunicorn (serveur WSGI de production)
CMD ["gunicorn", "user_service.wsgi:application", "--bind", "0.0.0.0:8000"]
