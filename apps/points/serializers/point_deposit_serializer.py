from rest_framework import serializers
from django.core.validators import MinValueValidator
from apps.points.models import TransactionTypeChoices


class PointDepositSerializer(serializers.Serializer):
    """
    點數儲值序列化器
    
    驗證儲值金額必須大於 0。
    """
    
    amount = serializers.IntegerField(
        min_value=1,
        help_text="儲值金額（必須大於 0）",
    )
    
    memo = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=300,
        help_text="備註（可選）",
    )
    
    def validate_amount(self, value):
        """驗證儲值金額（Serializer 層驗證）"""
        if value <= 0:
            raise serializers.ValidationError("儲值金額必須大於 0")
        return value
