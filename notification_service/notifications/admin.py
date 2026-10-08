"""
NOTIFICATION SERVICE - Admin
Enregistrement du modèle Notification dans l'interface d'administration Django.
"""
from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Interface admin pour les Notifications."""
    list_display = ['user_id', 'event_type', 'is_read', 'created_at']
    list_filter = ['event_type', 'is_read']
    search_fields = ['user_id', 'message']
    readonly_fields = ['created_at']
