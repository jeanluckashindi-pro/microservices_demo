"""
NOTIFICATION SERVICE - Views
Expose les endpoints REST pour créer et consulter les notifications.
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer, CreateNotificationSerializer


class NotificationListView(generics.ListAPIView):
    """
    GET /api/notifications/?user_id=<id>
    Liste les notifications d'un utilisateur spécifique.
    Le user_id est passé en query parameter.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Filtre les notifications par user_id (query param)."""
        user_id = self.request.query_params.get('user_id')
        qs = Notification.objects.all()
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs


class CreateNotificationView(generics.CreateAPIView):
    """
    POST /api/notifications/create/
    Crée une nouvelle notification.
    AllowAny pour que les autres microservices puissent appeler cet endpoint
    sans avoir besoin d'un token JWT (communication service-à-service).
    """
    serializer_class = CreateNotificationSerializer
    permission_classes = [permissions.AllowAny]


class MarkReadView(APIView):
    """
    PUT /api/notifications/<pk>/read/
    Marque une notification comme lue.
    """
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        """Marque la notification identifiée par pk comme lue."""
        try:
            notification = Notification.objects.get(pk=pk)
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notification introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )
        notification.is_read = True
        notification.save()
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)
