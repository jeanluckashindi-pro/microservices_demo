"""
VOTE SERVICE - Modèles
Définit les entités du domaine vote : Topic (sujet de vote) et Vote (bulletin).
"""
from django.db import models


class Topic(models.Model):
    """
    Représente un sujet sur lequel les utilisateurs peuvent voter.
    created_by_user_id : identifiant de l'utilisateur (vient du user_service via JWT).
    """
    title = models.CharField(max_length=255, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    # On stocke l'ID de l'user venant du user_service (pas de FK cross-service)
    created_by_user_id = models.IntegerField(verbose_name="ID créateur")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Sujet"
        verbose_name_plural = "Sujets"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def vote_count(self):
        """Nombre total de votes sur ce sujet."""
        return self.votes.count()


class Vote(models.Model):
    """
    Représente un bulletin de vote d'un utilisateur sur un Topic.
    Un utilisateur ne peut voter qu'une seule fois par sujet (unique_together).
    """
    CHOICES = [
        ('for', 'Pour'),
        ('against', 'Contre'),
        ('abstain', 'Abstention'),
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='votes')
    # ID de l'utilisateur depuis le user_service (pas de FK cross-service)
    user_id = models.IntegerField(verbose_name="ID utilisateur")
    choice = models.CharField(max_length=10, choices=CHOICES, verbose_name="Choix")
    voted_at = models.DateTimeField(auto_now_add=True, verbose_name="Voté le")

    class Meta:
        verbose_name = "Vote"
        verbose_name_plural = "Votes"
        # Contrainte : un user ne vote qu'une fois par topic
        unique_together = ('topic', 'user_id')

    def __str__(self):
        return f"Vote de user#{self.user_id} sur '{self.topic}' : {self.choice}"
