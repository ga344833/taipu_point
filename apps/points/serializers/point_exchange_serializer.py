from rest_framework import serializers
from apps.products.models import Product


class PointExchangeSerializer(serializers.Serializer):
    """
    點數兌換序列化器
    
    接收 product_id 和 quantity，驗證商品有效性和數量範圍。
    庫存檢查在 View 中使用 select_for_update() 鎖定後進行，避免競態條件。
    """
    
    product_id = serializers.IntegerField(
        help_text="商品 ID",
    )
    
    quantity = serializers.IntegerField(
        default=1,
        min_value=1,
        max_value=5,
        help_text="兌換數量（1-5，預設為 1）",
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
        
        # 注意：庫存檢查在 View 中使用 select_for_update() 鎖定後進行
        # 這裡只做基本驗證，避免競態條件
        
        return value
