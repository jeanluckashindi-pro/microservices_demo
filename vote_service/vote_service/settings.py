"""
VOTE SERVICE - Settings
Ce microservice gère les votes sur des sujets/candidats.
Il communique avec le USER SERVICE pour valider les tokens JWT
et avec le NOTIFICATION SERVICE pour envoyer des alertes.
"""
import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'vote-service-secret-key-change-in-prod')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'votes',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'vote_service.urls'

TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates',
               'DIRS': [], 'APP_DIRS': True,
               'OPTIONS': {'context_processors': [
                   'django.template.context_processors.request',
                   'django.contrib.auth.context_processors.auth',
                   'django.contrib.messages.context_processors.messages',
               ]}}]

WSGI_APPLICATION = 'vote_service.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'votes_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ============================================================
# COMMUNICATION INTER-SERVICES
# Ces URLs sont injectées via variables d'environnement.
# En Docker Compose : le nom du service Docker est utilisé comme hostname.
# En Kubernetes    : le nom du Service K8s est utilisé comme hostname.
# ============================================================
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://user-service:8000')
NOTIFICATION_SERVICE_URL = os.environ.get('NOTIFICATION_SERVICE_URL', 'http://notification-service:8002')

CORS_ALLOW_ALL_ORIGINS = True
STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
