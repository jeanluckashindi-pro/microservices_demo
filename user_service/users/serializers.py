"""
USER SERVICE - Serializers
Les serializers transforment les objets Python/Django ↔ JSON.
C'est le cœur de DRF : ils valident les données entrantes et formatent les sorties.
"""
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer complet avec le profil imbriqué (nested serializer).
    L'API retourne : { id, username, email, profile: { bio, created_at } }
    """
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer dédié à l'inscription.
    Le champ password est write_only : il n'apparaîtra jamais dans les réponses.
    """
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        # create_user() hash le mot de passe automatiquement
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        # Créer automatiquement le profil lié
        UserProfile.objects.create(user=user)
        return user
