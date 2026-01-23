from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class RoleChoices(models.TextChoices):
    """使用者角色選項"""
    MEMBER = "MEMBER", _("一般會員")
    STORE = "STORE", _("店家")
    ADMIN = "ADMIN", _("管理者")


class User(AbstractUser):
    """
    客製化使用者模型
    
    繼承 Django 的 AbstractUser，提供完整的基礎欄位：
    - username: 帳號（用於系統登入）
    - password: 加密密碼
    - email: 電子郵件
    - first_name, last_name: 姓名
    - is_active: 是否啟用（AbstractUser 已有）
    - is_staff: 後台權限（AbstractUser 已有）
    - date_joined: 註冊時間（AbstractUser 已有）
    
    額外新增欄位：
    - role: 使用者身分（MEMBER:會員, STORE:店家, ADMIN:管理者）
    - is_enable: 帳號狀態（是否已停用）
    - memo: 備註
    """
    
    # id 使用 Django 預設的 AutoField (BigAutoField)
    # 不需要額外定義，AbstractUser 已提供
    
    role = models.CharField(
        max_length=10,
        choices=RoleChoices.choices,
        default=RoleChoices.MEMBER,
        help_text="使用者身分：MEMBER=一般會員, STORE=店家, ADMIN=管理者",
    )
    
    is_enable = models.BooleanField(
        default=True,
        help_text="帳號狀態，True=啟用, False=停用",
    )
    
    memo = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text="備註",
    )
    
    class Meta:
        db_table = "users"
        verbose_name = "使用者"
        verbose_name_plural = "使用者"
        ordering = ["-date_joined"]
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
