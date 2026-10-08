"""
USER SERVICE - Models
On utilise le modèle User natif de Django, étendu avec un profil.
"""
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Extension du modèle User Django.
    Relation OneToOne : chaque User a exactement un UserProfile.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f"Profil de {self.user.username}"
