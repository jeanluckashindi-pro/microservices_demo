"""
VOTE SERVICE - Views
Expose les endpoints REST pour les topics et les votes.
L'authentification est gérée localement via SimpleJWT (pas d'appel au user_service).
"""
import requests
from django.conf import settings
from django.db.models import Count, Q
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Topic, Vote
from .serializers import TopicSerializer, VoteSerializer, CreateVoteSerializer


class TopicViewSet(viewsets.ModelViewSet):
    """
    ViewSet CRUD pour les Topics.
    - Lecture (list/retrieve) : tout le monde (IsAuthenticatedOrReadOnly)
    - Création/modification/suppression : admin uniquement
    """
    queryset = Topic.objects.all().order_by('-created_at')
    serializer_class = TopicSerializer

    def get_permissions(self):
        """
        Permissions dynamiques selon l'action.
        Les actions 'dangereuses' sont réservées aux admins.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        """
        Lors de la création, on injecte l'ID de l'utilisateur connecté
        comme créateur du topic (extrait du token JWT par SimpleJWT).
        """
        serializer.save(created_by_user_id=self.request.user.id)


class VoteView(APIView):
    """
    POST /api/votes/topics/<topic_id>/vote/
    Permet à un utilisateur authentifié de voter sur un topic.
    Appelle le notification_service en fire-and-forget après le vote.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, topic_id):
        """Enregistre ou met à jour le vote de l'utilisateur sur un topic."""
        # Récupération du topic
        try:
            topic = Topic.objects.get(pk=topic_id)
        except Topic.DoesNotExist:
            return Response({'error': 'Topic introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        # Vérification que le topic est actif
        if not topic.is_active:
            return Response(
                {'error': 'Ce topic est clôturé, vous ne pouvez plus voter.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validation du choix soumis
        serializer = CreateVoteSerializer(data={'topic': topic_id, 'choice': request.data.get('choice')})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Création ou mise à jour du vote (update_or_create gère l'unicité)
        vote, created = Vote.objects.update_or_create(
            topic=topic,
            user_id=request.user.id,
            defaults={'choice': serializer.validated_data['choice']}
        )

        # Notification asynchrone en fire-and-forget
        # Si le notification_service est indisponible, l'erreur est ignorée silencieusement.
        self._notify_vote_cast(request.user.id, topic, vote)

        action = 'créé' if created else 'mis à jour'
        response_serializer = VoteSerializer(vote)
        return Response(
            {'message': f'Vote {action} avec succès.', 'vote': response_serializer.data},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    def _notify_vote_cast(self, user_id, topic, vote):
        """
        Envoie une notification au notification_service.
        Fire-and-forget : toute exception est silencieusement ignorée.
        """
        try:
            notification_url = settings.NOTIFICATION_SERVICE_URL + '/api/notifications/create/'
            payload = {
                'user_id': user_id,
                'event_type': 'vote_cast',
                'message': f'Vous avez voté "{vote.get_choice_display()}" sur le topic "{topic.title}".',
            }
            # Timeout court pour ne pas bloquer la réponse
            requests.post(notification_url, json=payload, timeout=2)
        except Exception:
            # Erreur ignorée : la notification est non-critique
            pass


class ResultsView(APIView):
    """
    GET /api/votes/topics/<topic_id>/results/
    Retourne le décompte des votes (pour/contre/abstention) sur un topic.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, topic_id):
        """Calcule et retourne les résultats d'un topic."""
        try:
            topic = Topic.objects.get(pk=topic_id)
        except Topic.DoesNotExist:
            return Response({'error': 'Topic introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        # Comptage agrégé en base (une seule requête SQL)
        counts = topic.votes.values('choice').annotate(count=Count('choice'))
        results = {'for': 0, 'against': 0, 'abstain': 0}
        for entry in counts:
            results[entry['choice']] = entry['count']

        return Response({
            'topic_id': topic_id,
            'topic_title': topic.title,
            'is_active': topic.is_active,
            'total_votes': sum(results.values()),
            'results': results,
        })
