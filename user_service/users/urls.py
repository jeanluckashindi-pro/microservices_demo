"""
USER SERVICE - URL routing interne
"""
from django.urls import path
from .views import RegisterView, UserDetailView, MeView, UserListView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),  # POST - inscription
    path('me/', MeView.as_view(), name='me'),                    # GET  - qui suis-je ?
    path('list/', UserListView.as_view(), name='user-list'),     # GET  - liste (admin)
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),  # GET/PUT
]
