"""
NOTIFICATION SERVICE - URLs racine
Routes principales du service de notifications.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Toutes les routes de l'app notifications sous /api/notifications/
    path('api/notifications/', include('notifications.urls')),
]
