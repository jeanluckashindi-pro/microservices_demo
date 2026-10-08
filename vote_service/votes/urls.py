"""
VOTE SERVICE - URLs
Définit les routes de l'application votes.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TopicViewSet, VoteView, ResultsView

# Le router génère automatiquement les URLs CRUD pour TopicViewSet
router = DefaultRouter()
router.register(r'topics', TopicViewSet, basename='topic')

urlpatterns = [
    # Routes générées par le router : /topics/, /topics/<pk>/
    path('', include(router.urls)),
    # Route pour voter sur un topic
    path('topics/<int:topic_id>/vote/', VoteView.as_view(), name='vote'),
    # Route pour voir les résultats d'un topic
    path('topics/<int:topic_id>/results/', ResultsView.as_view(), name='results'),
]
