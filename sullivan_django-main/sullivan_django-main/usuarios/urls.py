# usuarios/urls.py
from django.urls import path
from .views import CustomTokenObtainPairView, register_user
from .views_password_reset import PasswordResetRequestAPI, PasswordResetConfirmAPI

# from rest_framework.routers import DefaultRouter
# router = DefaultRouter()
# router.register(r'', CustomTokenObtainPairView)
urlpatterns = [
    path('register/', register_user, name='register_user'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/password-reset/', PasswordResetRequestAPI.as_view(), name='password-reset'),
    path('auth/password-reset/confirm/', PasswordResetConfirmAPI.as_view(), name='password-reset-confirm'),
]
