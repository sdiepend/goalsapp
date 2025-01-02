from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpoints for each app
    path('api/users/', include('users.urls')),
    path('api/goals/', include('goals.urls')),
    path('api/standards/', include('standards.urls')),
    path('api/gamification/', include('gamification.urls')),
]
