"""
VOTE SERVICE - Serializers
Convertisseurs entre objets Python (modèles Django) et JSON (API REST).
"""
from rest_framework import serializers
from .models import Topic, Vote


class TopicSerializer(serializers.ModelSerializer):
    """
    Serializer complet pour un Topic.
    vote_count est un champ calculé (annoté ou property).
    """
    # Champ en lecture seule : calculé via la property du modèle
    vote_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Topic
        fields = ['id', 'title', 'description', 'created_by_user_id', 'created_at', 'is_active', 'vote_count']
        read_only_fields = ['id', 'created_at', 'created_by_user_id']


class VoteSerializer(serializers.ModelSerializer):
    """
    Serializer complet pour un Vote (lecture).
    """
    class Meta:
        model = Vote
        fields = ['id', 'topic', 'user_id', 'choice', 'voted_at']
        read_only_fields = ['id', 'voted_at']


class CreateVoteSerializer(serializers.Serializer):
    """
    Serializer pour la création d'un vote.
    user_id est injecté depuis le token JWT dans la vue, pas fourni par le client.
    """
    topic = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all())
    choice = serializers.ChoiceField(choices=['for', 'against', 'abstain'])
