from rest_framework import serializers
from apps.points.models import PointTransaction


class PointTransactionSerializer(serializers.ModelSerializer):
    """
    點數交易紀錄序列化器
    
    用於查詢交易紀錄，包含所有交易資訊。
    """
    
    tx_type_display = serializers.CharField(
        source="get_tx_type_display",
        read_only=True,
        help_text="交易類型顯示名稱",
    )
    
    class Meta:
        model = PointTransaction
        fields = [
            "id",
            "amount",
            "tx_type",
            "tx_type_display",
            "is_success",
            "balance_after",
            "memo",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "amount",
            "tx_type",
            "tx_type_display",
            "is_success",
            "balance_after",
            "memo",
            "created_at",
        ]
