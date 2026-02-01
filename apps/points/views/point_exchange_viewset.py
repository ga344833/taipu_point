from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter
from utils.views import ModelViewSet
from apps.points.models import PointExchange, ExchangeStatusChoices
from apps.points.serializers import (
    PointExchangeListSerializer,
    PointExchangeVerifySerializer,
)
from apps.users.models import RoleChoices
from core.permissions import IsStoreOrAdmin


@extend_schema(
    tags=["點數管理"],
    description="查詢和管理點數兌換紀錄，不同角色有不同的查詢範圍和權限",
)
class PointExchangeViewSet(ModelViewSet):
    """
    點數兌換紀錄 ViewSet
    
    提供兌換紀錄的查詢和核銷功能：
    - List: 查詢兌換紀錄列表（根據角色過濾）
    - Retrieve: 查詢單一兌換紀錄（根據角色過濾）
    - Update/Partial Update: 核銷兌換紀錄（僅 STORE 和 ADMIN）
    
    權限控制：
    - MEMBER：僅能查看自己的兌換紀錄
    - STORE：僅能查看自己商品的兌換紀錄，可以核銷自己商品的兌換紀錄
    - ADMIN：可以查看所有兌換紀錄，可以核銷任何兌換紀錄
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = PointExchangeListSerializer
    search_fields = ["exchange_code", "user__username", "product__name"]
    ordering_fields = ["created_at", "points_spent", "status"]
    ordering = ["-created_at"]
    
    def get_queryset(self):
        """
        根據用戶角色過濾查詢集
        
        - MEMBER：僅能查看自己的兌換紀錄
        - STORE：僅能查看自己商品的兌換紀錄
        - ADMIN：可以查看所有兌換紀錄
        """
        queryset = PointExchange.objects.select_related(
            "user", "product", "product__store"
        ).all()
        
        if self.request.user.role == RoleChoices.MEMBER:
            # 會員：只看自己的兌換紀錄
            queryset = queryset.filter(user=self.request.user)
        elif self.request.user.role == RoleChoices.STORE:
            # 店家：只看自己商品的兌換紀錄
            queryset = queryset.filter(product__store=self.request.user)
        # ADMIN 可以查看所有兌換紀錄，不需要過濾
        
        return queryset
    
    def get_serializer_class(self):
        """
        根據 action 返回不同的 Serializer
        
        - list/retrieve: 使用 PointExchangeListSerializer（查詢用）
        - update/partial_update: 使用 PointExchangeVerifySerializer（核銷用）
        """
        if self.action in ['update', 'partial_update']:
            return PointExchangeVerifySerializer
        return PointExchangeListSerializer
    
    def get_permissions(self):
        """
        動態設定權限
        
        - List/Retrieve: 需要登入（IsAuthenticated）
        - Update/Partial Update: 需要登入且為店家或管理員（IsAuthenticated + IsStore 或 IsAdmin）
        """
        if self.action in ['list', 'retrieve', 'lookup_by_code']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            # 核銷功能需要是店家或管理員
            return [IsAuthenticated(), IsStoreOrAdmin()]
        return super().get_permissions()
    
    @extend_schema(
        summary="查詢兌換紀錄列表",
        description="""
        查詢點數兌換紀錄列表，根據角色過濾：
        - MEMBER：僅能查看自己的兌換紀錄
        - STORE：僅能查看自己商品的兌換紀錄
        - ADMIN：可以查看所有兌換紀錄
        """,
        parameters=[
            OpenApiParameter(
                name="status",
                type=str,
                location=OpenApiParameter.QUERY,
                description="交換狀態篩選（PENDING=待核銷, VERIFIED=已核銷）",
                required=False,
            ),
            OpenApiParameter(
                name="product",
                type=int,
                location=OpenApiParameter.QUERY,
                description="商品 ID 篩選（店家可用）",
                required=False,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        """查詢兌換紀錄列表"""
        queryset = self.get_queryset()
        
        # 過濾狀態
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 過濾商品（店家可用）
        product_id = request.query_params.get("product")
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # 設定過濾後的 queryset
        self.queryset = queryset
        
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="查詢單一兌換紀錄",
        description="查詢單一兌換紀錄詳情，根據角色過濾",
    )
    def retrieve(self, request, *args, **kwargs):
        """查詢單一兌換紀錄"""
        instance = self.get_object()
        
        # 額外權限檢查（雖然 get_queryset 已經過濾，但為了安全再加一層）
        if request.user.role == RoleChoices.MEMBER and instance.user != request.user:
            return Response(
                {"detail": "您沒有權限查看此兌換紀錄"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.user.role == RoleChoices.STORE and instance.product.store != request.user:
            return Response(
                {"detail": "您沒有權限查看此兌換紀錄"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="核銷兌換紀錄",
        description="""
        核銷兌換紀錄，將狀態從 PENDING 改為 VERIFIED。
        
        權限：
        - STORE：僅能核銷自己商品的兌換紀錄
        - ADMIN：可以核銷任何兌換紀錄
        
        注意：已核銷的紀錄無法改回待核銷狀態。
        """,
        request=PointExchangeVerifySerializer,
        responses={200: PointExchangeListSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        """
        核銷兌換紀錄（部分更新）
        
        僅允許更新 status 欄位，將 PENDING 改為 VERIFIED。
        """
        instance = self.get_object()
        
        # 權限檢查：STORE 只能核銷自己商品的兌換紀錄
        if request.user.role == RoleChoices.STORE:
            if instance.product.store != request.user:
                return Response(
                    {"detail": "您只能核銷自己商品的兌換紀錄"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # 檢查狀態是否為 PENDING
        if instance.status != ExchangeStatusChoices.PENDING:
            return Response(
                {"detail": f"此兌換紀錄狀態為 {instance.get_status_display()}，無法核銷"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        
        # 更新狀態為 VERIFIED
        serializer.save(status=ExchangeStatusChoices.VERIFIED)
        
        return Response(
            {
                "message": "核銷成功",
                "exchange": PointExchangeListSerializer(instance).data
            },
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        summary="根據交換序號查詢兌換紀錄",
        description="""
        根據交換序號（exchange_code）查詢兌換紀錄。
        
        使用場景：會員出示交換序號時，店家可以快速查詢並核銷。
        
        權限：
        - STORE：僅能查詢自己商品的兌換紀錄
        - ADMIN：可以查詢任何兌換紀錄
        """,
        parameters=[
            OpenApiParameter(
                name="code",
                type=str,
                location=OpenApiParameter.QUERY,
                description="交換序號（exchange_code）",
                required=True,
            ),
        ],
        responses={200: PointExchangeListSerializer},
    )
    @action(detail=False, methods=['get'], url_path='lookup-by-code')
    def lookup_by_code(self, request):
        """
        根據交換序號查詢兌換紀錄
        
        用於店家核銷時快速查詢。
        """
        exchange_code = request.query_params.get("code")
        
        if not exchange_code:
            return Response(
                {"detail": "請提供交換序號（code 參數）"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            exchange = PointExchange.objects.select_related(
                "user", "product", "product__store"
            ).get(exchange_code=exchange_code)
        except PointExchange.DoesNotExist:
            return Response(
                {"detail": "找不到此交換序號的兌換紀錄"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 權限檢查
        if request.user.role == RoleChoices.MEMBER:
            # 會員只能查看自己的
            if exchange.user != request.user:
                return Response(
                    {"detail": "您沒有權限查看此兌換紀錄"},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif request.user.role == RoleChoices.STORE:
            # 店家只能查看自己商品的
            if exchange.product.store != request.user:
                return Response(
                    {"detail": "您沒有權限查看此兌換紀錄"},
                    status=status.HTTP_403_FORBIDDEN
                )
        # ADMIN 可以查看任何兌換紀錄
        
        serializer = self.get_serializer(exchange)
        return Response(serializer.data, status=status.HTTP_200_OK)
