# Rest Framework Settings
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "utils.pagination.DemoPageNumberPagination",
    "EXCEPTION_HANDLER": "utils.custom_exception_handler.custom_exception_handler",
}

# JWT Settings
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv(".env")

# 取得 SECRET_KEY（與 base.py 中的邏輯一致）
# 由於設定檔載入順序，這裡需要重新讀取環境變數
# 或者可以直接使用 SECRET_KEY（因為 base.py 已經導入）
# 為了避免循環導入，使用 os.getenv 重新讀取
_JWT_SIGNING_KEY = os.getenv("SECRET_KEY", "django-insecure-change-this-in-production")

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": _JWT_SIGNING_KEY,  # 使用 SECRET_KEY
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# Spectacular Settings (Swagger)
SPECTACULAR_SETTINGS = {
    "TITLE": "點數兌換贈品系統 API",
    "VERSION": "1.0.0",
    "DESCRIPTION": "點數兌換贈品系統後端 API 文件",
    "SERVE_INCLUDE_SCHEMA": False,
}


