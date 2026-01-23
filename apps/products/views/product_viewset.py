from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from utils.views import ModelViewSet
from apps.products.models import Product
from apps.products.serializers import ProductSerializer
from apps.products.filters import ProductFilter


@extend_schema(
    tags=["商品管理"],
    description="商品 CRUD API，目前開放所有操作供測試使用；未來將限制僅店家/管理者可操作",
)
class ProductViewSet(ModelViewSet):
    """
    商品 ViewSet
    
    提供商品的 CRUD 操作：
    - List: 查詢商品列表（支援分頁與篩選）
    - Retrieve: 查詢單一商品
    - Create: 建立商品（目前開放，未來限店家）
    - Update: 更新商品（目前開放，未來限店家本身）
    - Destroy: 軟刪除商品（僅修改 is_active）
    
    注意：目前暫不限制權限，供測試使用；未來需掛載 IsStoreUserOrReadOnly 權限。
    """
    
    queryset = Product.objects.select_related("store").all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    search_fields = ["name", "memo"]
    ordering_fields = ["created_at", "updated_at", "required_points", "stock"]
    ordering = ["-created_at"]
    
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
        
        注意：目前暫不檢查用戶角色，未來需加入權限驗證：
        - 檢查用戶是否為店家（role == RoleChoices.STORE）
        - 或檢查用戶是否為管理者（role == RoleChoices.ADMIN）
        """
        # TODO: 未來加入權限檢查
        # if self.request.user.role not in [RoleChoices.STORE, RoleChoices.ADMIN]:
        #     raise PermissionDenied("僅店家和管理者可建立商品")
        
        serializer.save(store=self.request.user)
    
    @extend_schema(
        summary="刪除商品（軟刪除）",
        description="軟刪除商品，僅將 is_active 設為 False，不實際刪除資料",
    )
    def destroy(self, request, *args, **kwargs):
        """
        軟刪除商品
        
        不實際刪除資料，僅將 is_active 設為 False。
        未來需加入權限檢查：僅店家可刪除自己的商品，管理者可刪除任何商品。
        """
        instance = self.get_object()
        
        # TODO: 未來加入權限檢查
        # if instance.store != request.user and request.user.role != RoleChoices.ADMIN:
        #     raise PermissionDenied("僅可刪除自己的商品")
        
        instance.is_active = False
        instance.save(update_fields=["is_active"])
        
        return Response(status=status.HTTP_204_NO_CONTENT)
