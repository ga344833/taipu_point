from rest_framework import serializers
from apps.products.models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    商品序列化器
    
    提供商品資料的驗證與轉換功能。
    包含雙重驗證：Model 層與 Serializer 層都驗證 required_points 和 stock 不為負數。
    """
    
    required_points = serializers.IntegerField(
        min_value=0,
        help_text="兌換所需點數，不得為負數",
    )
    
    stock = serializers.IntegerField(
        min_value=0,
        help_text="庫存數量，不得為負數",
    )
    
    store = serializers.PrimaryKeyRelatedField(
        read_only=True,
        help_text="所屬店家（後端自動代入，無需提供）",
    )
    
    class Meta:
        model = Product
        fields = [
            "id",
            "store",
            "name",
            "required_points",
            "stock",
            "is_active",
            "memo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "store", "created_at", "updated_at"]
    
    def validate_required_points(self, value):
        """驗證 required_points 不為負數（Serializer 層驗證）"""
        if value < 0:
            raise serializers.ValidationError("兌換點數不得為負數")
        return value
    
    def validate_stock(self, value):
        """驗證 stock 不為負數（Serializer 層驗證）"""
        if value < 0:
            raise serializers.ValidationError("庫存數量不得為負數")
        return value
