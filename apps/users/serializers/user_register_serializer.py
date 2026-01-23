from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.users.models import RoleChoices

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    使用者註冊序列化器
    
    包含密碼確認與 role 驗證。
    註冊時僅允許選擇 MEMBER 或 STORE，不允許註冊為 ADMIN。
    """
    
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="密碼（至少 8 個字元）",
    )
    
    password_confirm = serializers.CharField(
        write_only=True,
        help_text="密碼確認",
    )
    
    role = serializers.ChoiceField(
        choices=[RoleChoices.MEMBER, RoleChoices.STORE],
        default=RoleChoices.MEMBER,
        help_text="使用者身分：MEMBER=一般會員, STORE=店家（不允許註冊為 ADMIN）",
    )
    
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "role",
        ]
        extra_kwargs = {
            "username": {"help_text": "帳號（用於系統登入）"},
            "email": {"required": True, "help_text": "電子郵件"},
        }
    
    def validate_email(self, value):
        """驗證 email 是否已存在"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("此電子郵件已被使用")
        return value
    
    def validate_username(self, value):
        """驗證 username 是否已存在"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("此帳號已被使用")
        return value
    
    def validate(self, attrs):
        """驗證密碼確認是否一致，以及 role 限制"""
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")
        role = attrs.get("role")
        
        # 驗證密碼確認
        if password != password_confirm:
            raise serializers.ValidationError({
                "password_confirm": "密碼與確認密碼不一致"
            })
        
        # 驗證 role 限制（不允許註冊為 ADMIN）
        if role == RoleChoices.ADMIN:
            raise serializers.ValidationError({
                "role": "不允許註冊為管理者，管理者帳號需由系統管理員建立"
            })
        
        return attrs
    
    def create(self, validated_data):
        """建立使用者，密碼會自動加密"""
        # 移除 password_confirm（不需要儲存）
        validated_data.pop("password_confirm", None)
        
        # 使用 create_user 方法，密碼會自動加密
        password = validated_data.pop("password")
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        return user
