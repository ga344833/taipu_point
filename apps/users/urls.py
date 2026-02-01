from django.urls import path, include
from apps.users.views import (
    UserRegisterView,
    MeView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
)

app_name = "users"

urlpatterns = [
    # 使用者認證
    path("auth/register/", UserRegisterView.as_view(), name="user-register"),
    # JWT Token 端點（使用自訂 View，包含詳細 API 文件說明）
    path("auth/token/", CustomTokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("auth/token/refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
    path("auth/token/verify/", CustomTokenVerifyView.as_view(), name="token-verify"),
    # 使用者個人資料
    path("users/me/", MeView.as_view(), name="user-me"),
]


