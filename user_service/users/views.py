"""
USER SERVICE - Views
Les vues DRF (ViewSets) exposent les endpoints REST.
"""
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, RegisterSerializer


class RegisterView(generics.CreateAPIView):
    """
    POST /api/users/register/
    Inscription d'un nouvel utilisateur. Aucune authentification requise.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/users/{id}/   → retourne le profil d'un utilisateur
    PUT  /api/users/{id}/   → met à jour le profil
    Requiert un token JWT valide dans le header: Authorization: Bearer <token>
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class MeView(APIView):
    """
    GET /api/users/me/
    Retourne les infos de l'utilisateur connecté (extrait du token JWT).
    Utilisé par les AUTRES microservices pour valider un token et récupérer l'identité.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserListView(generics.ListAPIView):
    """
    GET /api/users/list/
    Liste tous les utilisateurs. Réservé à l'admin.
    """
    queryset = User.objects.all().select_related('profile')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
