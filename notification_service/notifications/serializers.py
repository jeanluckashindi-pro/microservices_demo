"""
NOTIFICATION SERVICE - Serializers
Convertisseurs JSON <-> modèles pour les notifications.
"""
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer complet en lecture pour une Notification.
    """
    class Meta:
        model = Notification
        fields = ['id', 'user_id', 'event_type', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class CreateNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création d'une notification.
    Utilisé par les autres microservices qui appellent POST /api/notifications/create/.
    """
    class Meta:
        model = Notification
        fields = ['user_id', 'event_type', 'message']
