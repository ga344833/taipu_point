"""
JWT 認證相關 View

繼承 djangorestframework-simplejwt 的內建 View，添加詳細的 API 文件說明。
"""

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    tags=["使用者認證"],
    summary="登入取得 JWT Token",
    description="""
    使用者登入端點，驗證帳號密碼後返回 Access Token 和 Refresh Token。
    
    **使用流程**：
    1. 使用帳號密碼登入，取得 access 和 refresh token
    2. 在後續 API 請求的 Header 中加入：`Authorization: Bearer <access_token>`
    3. Access Token 有效期為 1 小時
    4. 當 Access Token 過期時，使用 Refresh Token 刷新取得新的 Token
    
    **注意事項**：
    - Access Token 用於 API 請求認證，有效期 1 小時
    - Refresh Token 用於刷新 Access Token，有效期 7 天
    - 每次刷新時會產生新的 Refresh Token，舊的會被加入黑名單
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "使用者帳號",
                    "example": "admin",
                },
                "password": {
                    "type": "string",
                    "format": "password",
                    "description": "使用者密碼",
                    "example": "admin12345!",
                },
            },
            "required": ["username", "password"],
        }
    },
    responses={
        200: {
            "description": "登入成功，返回 Access Token 和 Refresh Token",
            "content": {
                "application/json": {
                    "example": {
                        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY5MjM3MTIxLCJpYXQiOjE3NjkyMzM1MjEsImp0aSI6Ijc1YTVjZTBmOTQ0OTQ0ZGQ4YzFhZjM5YjFkNWV1YTAyIiwidXNlcl9pZCI6MX0.IazSrXhChY3-TbuIZHIu2DoKANQbuDqtbFtPpG5RC-s",
                        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2OTgzODMyMSwiaWF0IjoxNzY5MjMzNTIxLCJqdGkiOiJjYjI2NjMzYTczMWU0MzNmODY1MDcyZDMwZjE1Zjg1YiIsInVzZXJfaWQiOjF9.ZjA-x9yECKgdu6SguDhBTs4hhe7q1IjMSxnfwljnZLQ",
                    }
                }
            },
        },
        401: {
            "description": "帳號或密碼錯誤",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No active account found with the given credentials",
                    }
                }
            },
        },
    },
    examples=[
        OpenApiExample(
            "登入範例",
            value={
                "username": "admin",
                "password": "admin12345!",
            },
            request_only=True,
        ),
        OpenApiExample(
            "成功回應",
            value={
                "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            },
            response_only=True,
        ),
    ],
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    自訂登入 View
    
    繼承 TokenObtainPairView，添加詳細的 API 文件說明。
    驗證使用者帳號密碼後返回 Access Token 和 Refresh Token。
    """


@extend_schema(
    tags=["使用者認證"],
    summary="刷新 Access Token",
    description="""
    使用 Refresh Token 取得新的 Access Token 和 Refresh Token。
    
    **使用時機**：
    - 當 Access Token 過期時（1 小時後）
    - API 請求返回 401 Unauthorized 時
    
    **使用流程**：
    1. 使用過期的 Access Token 請求 API，收到 401 錯誤
    2. 使用 Refresh Token 呼叫此端點，取得新的 Access Token 和 Refresh Token
    3. 使用新的 Access Token 繼續 API 請求
    
    **注意事項**：
    - Refresh Token 有效期為 7 天
    - 每次刷新會產生新的 Refresh Token，舊的會被加入黑名單
    - 如果 Refresh Token 也過期，需要重新登入
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "refresh": {
                    "type": "string",
                    "description": "Refresh Token（從登入端點取得）",
                    "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                },
            },
            "required": ["refresh"],
        }
    },
    responses={
        200: {
            "description": "刷新成功，返回新的 Access Token 和 Refresh Token",
            "content": {
                "application/json": {
                    "example": {
                        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    }
                }
            },
        },
        401: {
            "description": "Refresh Token 無效或已過期",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Token is invalid or expired",
                    }
                }
            },
        },
    },
    examples=[
        OpenApiExample(
            "刷新 Token 範例",
            value={
                "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            },
            request_only=True,
        ),
        OpenApiExample(
            "成功回應",
            value={
                "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            },
            response_only=True,
        ),
    ],
)
class CustomTokenRefreshView(TokenRefreshView):
    """
    自訂刷新 Token View
    
    繼承 TokenRefreshView，添加詳細的 API 文件說明。
    使用 Refresh Token 取得新的 Access Token 和 Refresh Token。
    """


@extend_schema(
    tags=["使用者認證"],
    summary="驗證 Token 有效性",
    description="""
    檢查 Token 是否有效（未過期、格式正確）。
    
    **使用時機**：
    - 前端需要檢查 Token 是否仍然有效
    - 在應用程式啟動時驗證保存的 Token
    
    **使用流程**：
    1. 將要驗證的 Token（Access 或 Refresh）傳送給此端點
    2. 如果 Token 有效，返回 HTTP 200（空回應）
    3. 如果 Token 無效或過期，返回 HTTP 401 錯誤
    
    **注意事項**：
    - 可以驗證 Access Token 或 Refresh Token
    - 有效時返回空物件 `{}`
    - 無效時返回錯誤訊息
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "token": {
                    "type": "string",
                    "description": "要驗證的 Token（Access 或 Refresh Token）",
                    "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                },
            },
            "required": ["token"],
        }
    },
    responses={
        200: {
            "description": "Token 有效",
            "content": {
                "application/json": {
                    "example": {},
                }
            },
        },
        401: {
            "description": "Token 無效或已過期",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Token is invalid or expired",
                    }
                }
            },
        },
    },
    examples=[
        OpenApiExample(
            "驗證 Token 範例",
            value={
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Token 有效",
            value={},
            response_only=True,
        ),
        OpenApiExample(
            "Token 無效",
            value={
                "detail": "Token is invalid or expired",
            },
            response_only=True,
        ),
    ],
)
class CustomTokenVerifyView(TokenVerifyView):
    """
    自訂驗證 Token View
    
    繼承 TokenVerifyView，添加詳細的 API 文件說明。
    檢查 Token 是否有效（未過期、格式正確）。
    """
