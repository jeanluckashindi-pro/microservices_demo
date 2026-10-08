"""
VOTE SERVICE - Admin
Enregistrement des modèles dans l'interface d'administration Django.
"""
from django.contrib import admin
from .models import Topic, Vote


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """Interface admin pour les Topics."""
    list_display = ['title', 'created_by_user_id', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title', 'description']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """Interface admin pour les Votes."""
    list_display = ['topic', 'user_id', 'choice', 'voted_at']
    list_filter = ['choice', 'topic']
    search_fields = ['user_id']
