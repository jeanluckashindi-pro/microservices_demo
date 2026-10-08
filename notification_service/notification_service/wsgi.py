"""
NOTIFICATION SERVICE - WSGI
Point d'entrée WSGI pour les serveurs de production (gunicorn, uWSGI).
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_service.settings')
application = get_wsgi_application()
