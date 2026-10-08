"""
NOTIFICATION SERVICE - URLs de l'app notifications
"""
from django.urls import path
from .views import NotificationListView, CreateNotificationView, MarkReadView

urlpatterns = [
    # GET  /api/notifications/           → liste (filtrée par user_id)
    path('', NotificationListView.as_view(), name='notification-list'),
    # POST /api/notifications/create/    → créer une notification (inter-services)
    path('create/', CreateNotificationView.as_view(), name='notification-create'),
    # PUT  /api/notifications/<pk>/read/ → marquer comme lue
    path('<int:pk>/read/', MarkReadView.as_view(), name='notification-mark-read'),
]
