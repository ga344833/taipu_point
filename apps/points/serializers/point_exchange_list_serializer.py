from rest_framework import serializers
from apps.points.models import PointExchange
from apps.products.serializers import ProductSerializer


class PointExchangeListSerializer(serializers.ModelSerializer):
    """
    點數兌換紀錄查詢序列化器
    
    用於查詢和顯示兌換紀錄，包含商品資訊和狀態顯示。
    """
    
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
        help_text="交換狀態顯示名稱",
    )
    
    product = ProductSerializer(
        read_only=True,
        help_text="兌換商品資訊",
    )
    
    user_username = serializers.CharField(
        source="user.username",
        read_only=True,
        help_text="兌換會員帳號",
    )
    
    user_email = serializers.EmailField(
        source="user.email",
        read_only=True,
        help_text="兌換會員 Email",
    )
    
    class Meta:
        model = PointExchange
        fields = [
            "id",
            "exchange_code",
            "user",
            "user_username",
            "user_email",
            "product",
            "quantity",
            "points_spent",
            "status",
            "status_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "exchange_code",
            "user",
            "user_username",
            "user_email",
            "product",
            "quantity",
            "points_spent",
            "status",
            "status_display",
            "created_at",
            "updated_at",
        ]


class PointExchangeVerifySerializer(serializers.ModelSerializer):
    """
    點數兌換核銷序列化器
    
    用於店家或管理員核銷兌換紀錄，僅允許更新 status 欄位。
    """
    
    class Meta:
        model = PointExchange
        fields = ["status"]
        
    def validate_status(self, value):
        """驗證狀態變更是否合法"""
        instance = self.instance
        
        # 只允許從 PENDING 改為 VERIFIED
        if instance.status == "VERIFIED" and value == "PENDING":
            raise serializers.ValidationError("已核銷的紀錄無法改回待核銷狀態")
        
        return value
