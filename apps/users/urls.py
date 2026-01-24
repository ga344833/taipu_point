from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from apps.users.views import UserRegisterView

app_name = "users"

urlpatterns = [
    # 使用者認證
    path("auth/register/", UserRegisterView.as_view(), name="user-register"),
    # JWT Token 端點（使用 djangorestframework-simplejwt 內建）
    path("auth/token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token-verify"),
]


