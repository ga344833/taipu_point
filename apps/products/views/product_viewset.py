from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from utils.views import ModelViewSet
from apps.products.models import Product
from apps.products.serializers import ProductSerializer
from apps.products.filters import ProductFilter
from core.permissions import IsStore, IsProductOwner


@extend_schema(
    tags=["商品管理"],
    description="商品 CRUD API，查詢不需要登入，建立需要店家權限，修改需要是商品擁有者",
)
class ProductViewSet(ModelViewSet):
    """
    商品 ViewSet
    
    提供商品的 CRUD 操作：
    - List/Retrieve: 查詢商品列表/詳情（不需要登入）
    - Create: 建立商品（需要登入且為店家）
    - Update: 更新商品（需要登入且為商品擁有者或管理者）
    - Destroy: 軟刪除商品（需要登入且為商品擁有者或管理者）
    
    權限控制：
    - 查詢：AllowAny（不需要登入）
    - 建立：IsAuthenticated + IsStore（需要是店家）
    - 更新/刪除：IsAuthenticated + IsProductOwner（需要是商品擁有者或管理者）
    """
    
    queryset = Product.objects.select_related("store").all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    search_fields = ["name", "memo"]
    ordering_fields = ["created_at", "updated_at", "required_points", "stock"]
    ordering = ["-created_at"]
    
    def get_permissions(self):
        """
        動態設定權限
        
        - List/Retrieve: 不需要登入（AllowAny）
        - Create: 需要登入且為店家（IsAuthenticated + IsStore）
        - Update/Delete: 需要登入且為商品擁有者或管理者（IsAuthenticated + IsProductOwner）
        """
        if self.action in ['list', 'retrieve']:
            # 查詢商品不需要登入
            return [AllowAny()]
        elif self.action == 'create':
            # 建立商品需要是店家
            return [IsAuthenticated(), IsStore()]
        else:
            # 更新/刪除需要是商品擁有者或管理者
            return [IsAuthenticated(), IsProductOwner()]
    
    def get_queryset(self):
        """
        優化查詢：使用 select_related 避免 N+1 查詢問題
        
        技術說明：
        - select_related: 用於 ForeignKey 和 OneToOneField，使用 SQL JOIN 一次取得關聯資料
        - 避免在序列化時對每個商品都查詢一次 store 的資料
        """
        queryset = super().get_queryset()
        return queryset.select_related("store")
    
    def perform_create(self, serializer):
        """
        建立商品時自動設定 store 為當前登入用戶
        
        注意：權限檢查已透過 get_permissions() 中的 IsStore 處理
        """
        serializer.save(store=self.request.user)
    
    @extend_schema(
        summary="刪除商品（軟刪除）",
        description="軟刪除商品，僅將 is_active 設為 False，不實際刪除資料",
    )
    def destroy(self, request, *args, **kwargs):
        """
        軟刪除商品
        
        不實際刪除資料，僅將 is_active 設為 False。
        權限檢查已透過 get_permissions() 中的 IsProductOwner 處理。
        """
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active"])
        
        return Response(status=status.HTTP_204_NO_CONTENT)
