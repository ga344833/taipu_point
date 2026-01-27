import secrets
from datetime import datetime
from django.db import transaction
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.users.models import RoleChoices, UserPoints
from apps.products.models import Product
from apps.points.models import (
    PointTransaction,
    TransactionTypeChoices,
    PointExchange,
    ExchangeStatusChoices,
)
from apps.points.serializers import PointExchangeSerializer


def generate_exchange_code():
    """
    生成交換序號
    
    格式：EX + YYYYMMDD + 6位隨機碼
    範例：EX20260126A1B2C3
    """
    date_str = datetime.now().strftime("%Y%m%d")
    random_code = secrets.token_hex(3).upper()  # 6 位隨機碼（大寫）
    return f"EX{date_str}{random_code}"


@extend_schema(
    tags=["點數管理"],
    summary="會員兌換商品",
    description="會員使用點數兌換商品，使用資料庫事務確保庫存、餘額更新與交易紀錄的一致性",
)
class PointExchangeView(CreateAPIView):
    """
    點數兌換 View
    
    僅限已登入的 MEMBER 存取。
    使用 transaction.atomic() 與 select_for_update() 確保高併發環境下的資料一致性。
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = PointExchangeSerializer
    
    def create(self, request, *args, **kwargs):
        """
        執行兌換操作
        
        1. 檢查用戶是否為 MEMBER
        2. 驗證商品有效性（存在、上架、有庫存）
        3. 使用 select_for_update() 鎖定 Product 和 UserPoints
        4. 在事務中：扣庫存、扣餘額、建立 PointExchange、建立 PointTransaction
        """
        # 檢查用戶角色
        if request.user.role != RoleChoices.MEMBER:
            return Response(
                {"detail": "僅會員可進行兌換操作"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product_id = serializer.validated_data["product_id"]
        quantity = serializer.validated_data.get("quantity", 1)
        
        # 使用資料庫事務確保一致性
        with transaction.atomic():
            # 1. 鎖定並取得商品（先鎖定商品，避免死鎖）
            try:
                product = Product.objects.select_for_update().get(
                    id=product_id,
                    is_active=True
                )
            except Product.DoesNotExist:
                return Response(
                    {"detail": "商品不存在或已下架"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 2. 驗證庫存是否足夠（在鎖定後檢查，避免競態條件）
            if product.stock < quantity:
                return Response(
                    {
                        "detail": "商品庫存不足，無法兌換",
                        "required": quantity,
                        "available": product.stock,
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 3. 鎖定並取得用戶點數
            user_points = UserPoints.objects.select_for_update().get(
                user=request.user
            )
            
            # 4. 檢查錢包是否鎖定
            if user_points.is_locked:
                return Response(
                    {"detail": "錢包已鎖定，無法進行兌換操作"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 5. 計算總點數並驗證餘額是否足夠
            required_points_per_item = product.required_points
            total_points_required = required_points_per_item * quantity
            balance_before = user_points.balance  # 記錄原始餘額
            
            if balance_before < total_points_required:
                return Response(
                    {
                        "detail": "點數餘額不足",
                        "required": total_points_required,
                        "balance": balance_before,
                        "quantity": quantity,
                        "points_per_item": required_points_per_item,
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 6. 計算新餘額
            new_balance = balance_before - total_points_required
            
            # 7. 更新庫存
            product.stock -= quantity
            product.save(update_fields=["stock"])
            
            # 8. 更新餘額
            user_points.balance = new_balance
            user_points.save(update_fields=["balance"])
            
            # 9. 生成交換序號（確保唯一性）
            exchange_code = generate_exchange_code()
            # 如果序號已存在，重新生成（機率極低）
            while PointExchange.objects.filter(exchange_code=exchange_code).exists():
                exchange_code = generate_exchange_code()
            
            # 10. 建立兌換紀錄（一次兌換建立一筆紀錄，包含 quantity）
            point_exchange = PointExchange.objects.create(
                user=request.user,
                product=product,
                exchange_code=exchange_code,
                quantity=quantity,
                points_spent=total_points_required,
                status=ExchangeStatusChoices.PENDING,
            )
            
            # 11. 建立交易紀錄（amount 為負數，表示扣點）
            point_transaction = PointTransaction.objects.create(
                user=request.user,
                amount=-total_points_required,  # 負數表示扣點
                tx_type=TransactionTypeChoices.REDEMPTION,
                is_success=True,
                balance_after=new_balance,
                memo=f"兌換商品：{product.name} x{quantity}",
            )
        
        return Response(
            {
                "message": "兌換成功",
                "exchange_id": point_exchange.id,
                "exchange_code": exchange_code,
                "product": {
                    "id": product.id,
                    "name": product.name,
                },
                "quantity": quantity,
                "points_spent": total_points_required,
                "balance_before": balance_before,
                "balance_after": new_balance,
                "transaction_id": point_transaction.id,
            },
            status=status.HTTP_201_CREATED
        )
