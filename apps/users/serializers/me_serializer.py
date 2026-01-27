from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class MeSerializer(serializers.ModelSerializer):
    """
    當前登入用戶個人資料序列化器
    
    包含用戶基本資訊和點數餘額。
    """
    
    balance = serializers.IntegerField(
        source='points.balance',
        read_only=True,
        help_text="點數餘額",
    )
    
    role_display = serializers.CharField(
        source='get_role_display',
        read_only=True,
        help_text="角色顯示名稱",
    )
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'role',
            'role_display',
            'balance',
            'date_joined',
        ]
        read_only_fields = [
            'id',
            'username',
            'email',
            'role',
            'role_display',
            'balance',
            'date_joined',
        ]
