from django.db import transaction
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.users.models import RoleChoices, UserPoints
from apps.points.models import PointTransaction, TransactionTypeChoices
from apps.points.serializers import PointDepositSerializer


@extend_schema(
    tags=["點數管理"],
    summary="會員儲值",
    description="會員點數儲值功能，使用資料庫事務確保餘額更新與交易紀錄的一致性",
)
class PointDepositView(CreateAPIView):
    """
    點數儲值 View
    
    僅限已登入的 MEMBER 存取。
    使用 select_for_update() 悲觀鎖，防止餘額更新時的競爭條件。
    使用 transaction.atomic() 確保 UserPoints 餘額更新與 PointTransaction 建立的一致性。
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = PointDepositSerializer
    
    def create(self, request, *args, **kwargs):
        """
        執行儲值操作
        
        1. 檢查用戶是否為 MEMBER
        2. 使用 select_for_update() 鎖定 UserPoints
        3. 在事務中更新餘額並建立交易紀錄
        """
        # 檢查用戶角色
        if request.user.role != RoleChoices.MEMBER:
            return Response(
                {"detail": "僅會員可進行儲值操作"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount = serializer.validated_data["amount"]
        memo = serializer.validated_data.get("memo", "")
        
        # 使用資料庫事務確保一致性
        with transaction.atomic():
            # 使用 select_for_update() 鎖定 UserPoints，防止競爭條件
            user_points = UserPoints.objects.select_for_update().get(
                user=request.user
            )
            
            # 檢查錢包是否鎖定
            if user_points.is_locked:
                return Response(
                    {"detail": "錢包已鎖定，無法進行儲值操作"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 計算新餘額
            new_balance = user_points.balance + amount
            
            # 更新餘額
            user_points.balance = new_balance
            user_points.save(update_fields=["balance"])
            
            # 建立交易紀錄
            transaction_record = PointTransaction.objects.create(
                user=request.user,
                amount=amount,
                tx_type=TransactionTypeChoices.DEPOSIT,
                is_success=True,
                balance_after=new_balance,
                memo=memo,
            )
        
        return Response(
            {
                "message": "儲值成功",
                "transaction_id": transaction_record.id,
                "amount": amount,
                "balance_before": user_points.balance - amount,
                "balance_after": new_balance,
            },
            status=status.HTTP_201_CREATED
        )
