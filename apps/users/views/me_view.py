from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from apps.users.serializers import MeSerializer

User = get_user_model()


@extend_schema(
    tags=["使用者管理"],
    summary="查詢當前登入用戶個人資料",
    description="查詢當前登入用戶的基本資訊和點數餘額，僅限已登入用戶存取",
)
class MeView(RetrieveAPIView):
    """
    當前登入用戶個人資料查詢 View
    
    提供當前登入用戶的基本資訊（username, email, role）和點數餘額。
    使用 select_related("points") 優化查詢，避免 N+1 問題。
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = MeSerializer
    
    def get_object(self):
        """
        取得當前登入用戶
        
        使用 select_related("points") 優化查詢，確保一次查詢就取得 UserPoints 資料。
        """
        return User.objects.select_related("points").get(id=self.request.user.id)
