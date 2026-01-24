from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.users.serializers import UserRegisterSerializer


@extend_schema(
    tags=["使用者認證"],
    summary="使用者註冊",
    description="允許使用者選擇身分（MEMBER/STORE）進行註冊，註冊成功後會自動建立對應的點數錢包",
)
class UserRegisterView(CreateAPIView):
    """
    使用者註冊 View
    
    開放註冊功能，允許使用者選擇 MEMBER 或 STORE 身分進行註冊。
    註冊成功後會自動觸發 Signal 建立對應的 UserPoints 紀錄。
    
    注意：不允許註冊為 ADMIN，管理者帳號需由系統管理員建立。
    """
    
    permission_classes = [AllowAny]  # 免登入即可存取
    serializer_class = UserRegisterSerializer
    
    def create(self, request, *args, **kwargs):
        """
        建立使用者
        
        使用 create_user 方法，密碼會自動加密。
        註冊成功後會自動觸發 Signal 建立 UserPoints。
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(
            {
                "message": "註冊成功",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                }
            },
            status=status.HTTP_201_CREATED
        )
