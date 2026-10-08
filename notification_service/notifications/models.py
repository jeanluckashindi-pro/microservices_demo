"""
NOTIFICATION SERVICE - Modèles
Définit l'entité Notification.
"""
from django.db import models


class Notification(models.Model):
    """
    Représente une notification envoyée à un utilisateur.
    user_id référence l'ID de l'user dans le user_service (pas de FK cross-service).
    event_type permet de catégoriser la notification (ex: 'vote_cast', 'topic_created').
    """
    user_id = models.IntegerField(verbose_name="ID utilisateur")
    event_type = models.CharField(max_length=100, verbose_name="Type d'événement")
    message = models.TextField(verbose_name="Message")
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créée le")

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    def __str__(self):
        status = 'lue' if self.is_read else 'non lue'
        return f"[{self.event_type}] user#{self.user_id} ({status})"
