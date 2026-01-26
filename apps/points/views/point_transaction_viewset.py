from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from utils.views import ModelViewSet
from apps.points.models import PointTransaction
from apps.points.serializers import PointTransactionSerializer
from apps.users.models import RoleChoices


@extend_schema(
    tags=["點數管理"],
    description="查詢點數交易紀錄，MEMBER 僅能查看自己的交易紀錄",
)
class PointTransactionViewSet(ModelViewSet):
    """
    點數交易紀錄 ViewSet
    
    提供交易紀錄的查詢功能：
    - List: 查詢交易紀錄列表（MEMBER 僅能查看自己的）
    - Retrieve: 查詢單一交易紀錄（MEMBER 僅能查看自己的）
    
    權限控制：
    - MEMBER：僅能查看自己的交易紀錄
    - ADMIN：可以查看所有交易紀錄（用於對帳、異常處理等）
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = PointTransactionSerializer
    search_fields = ["memo"]
    ordering_fields = ["created_at", "amount"]
    ordering = ["-created_at"]
    
    def get_queryset(self):
        """
        根據用戶角色過濾查詢集
        
        - MEMBER：僅能查看自己的交易紀錄
        - ADMIN：可以查看所有交易紀錄
        """
        queryset = PointTransaction.objects.select_related("user").all()
        
        # MEMBER 僅能查看自己的交易紀錄
        if self.request.user.role == RoleChoices.MEMBER:
            queryset = queryset.filter(user=self.request.user)
        # ADMIN 可以查看所有交易紀錄
        # 注意：STORE 角色目前不允許查看交易紀錄
        
        return queryset
    
    @extend_schema(
        summary="查詢交易紀錄列表",
        description="查詢點數交易紀錄列表，MEMBER 僅能查看自己的交易紀錄",
        parameters=[
            OpenApiParameter(
                name="tx_type",
                type=str,
                location=OpenApiParameter.QUERY,
                description="交易類型篩選（DEPOSIT=儲值, REDEMPTION=兌換）",
                required=False,
            ),
            OpenApiParameter(
                name="is_success",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="交易狀態篩選（true=成功, false=失敗）",
                required=False,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        """查詢交易紀錄列表"""
        queryset = self.get_queryset()
        
        # 過濾交易類型
        tx_type = request.query_params.get("tx_type")
        if tx_type:
            queryset = queryset.filter(tx_type=tx_type)
        
        # 過濾交易狀態
        is_success = request.query_params.get("is_success")
        if is_success is not None:
            is_success_bool = is_success.lower() == "true"
            queryset = queryset.filter(is_success=is_success_bool)
        
        # 設定過濾後的 queryset
        self.queryset = queryset
        
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="查詢單一交易紀錄",
        description="查詢單一交易紀錄詳情，MEMBER 僅能查看自己的交易紀錄",
    )
    def retrieve(self, request, *args, **kwargs):
        """查詢單一交易紀錄"""
        instance = self.get_object()
        
        # MEMBER 只能查看自己的交易紀錄
        if request.user.role == RoleChoices.MEMBER and instance.user != request.user:
            return Response(
                {"detail": "您沒有權限查看此交易紀錄"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().retrieve(request, *args, **kwargs)
