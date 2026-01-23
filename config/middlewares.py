import logging
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from threading import local
from typing import Optional


logger = logging.getLogger("django.db")
_user = local()


class LogApiEndpointMiddleware(MiddlewareMixin):
    """記錄 API 端點的中間件"""
    
    def process_request(self, request):
        logger.debug(f"API: {request.path}")


class CurrentUserMiddleware:
    """
    當前用戶中間件
    從 JWT token 中解析用戶資訊，並提供線程本地儲存
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        User = get_user_model()
        authorization_header = request.headers.get("Authorization", "")
        logger.debug(f"Authorization header: {authorization_header}")

        try:
            if not authorization_header:
                logger.debug("No Authorization header found")
                return self.get_response(request)

            # Handle token with "token" prefix, "Basic" prefix, or no prefix
            if authorization_header.startswith("token "):
                access_token = authorization_header.split(" ")[1]
                logger.debug("Token format: prefixed with 'token'")
            elif authorization_header.startswith("Basic "):
                access_token = authorization_header.split(" ")[1]
                logger.debug("Token format: prefixed with 'Basic'")
            elif authorization_header.startswith("Bearer "):
                access_token = authorization_header.split(" ")[1]
                logger.debug("Token format: prefixed with 'Bearer'")
            else:
                access_token = authorization_header
                logger.debug("Token format: no prefix")

            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])

            user_id = payload.get("user_id")
            if not user_id:
                logger.warning("No user_id in token payload")
                return self.get_response(request)

            user = User.objects.filter(id=user_id).first()
            if user:
                self.set_current_user(user)
                logger.debug(f"User {user.id} authenticated successfully")
            else:
                logger.warning(f"User with id {user_id} not found")

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in CurrentUserMiddleware: {str(e)}")

        try:
            response = self.get_response(request)
            return response
        finally:
            if hasattr(_user, "value"):
                del _user.value

    @staticmethod
    def set_current_user(user: AbstractUser) -> None:
        """設置當前用戶"""
        _user.value = user

    @staticmethod
    def get_current_user() -> Optional[AbstractUser]:
        """取得當前用戶"""
        return getattr(_user, "value", None)


