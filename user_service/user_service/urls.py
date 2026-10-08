"""
USER SERVICE - URLs
Toutes les routes de ce microservice commencent par /api/users/
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Endpoints JWT : login → retourne access + refresh token
    path('api/users/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Endpoints CRUD utilisateurs
    path('api/users/', include('users.urls')),
]
