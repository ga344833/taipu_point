from rest_framework import serializers
from apps.products.models import Product


class PointExchangeSerializer(serializers.Serializer):
    """
    點數兌換序列化器
    
    接收 product_id 並驗證有效性。
    """
    
    product_id = serializers.IntegerField(
        help_text="商品 ID",
    )
    
    def validate_product_id(self, value):
        """驗證商品是否存在且有效"""
        try:
            product = Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("商品不存在")
        
        # 檢查商品是否上架
        if not product.is_active:
            raise serializers.ValidationError("商品已下架，無法兌換")
        
        # 檢查庫存
        if product.stock <= 0:
            raise serializers.ValidationError("商品庫存不足，無法兌換")
        
        return value
