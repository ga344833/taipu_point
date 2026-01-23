from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from core.models.base_model import BaseModel


class UserPoints(BaseModel):
    """
    使用者點數錢包模型
    
    與 User 建立 One-to-One 關係，用於存放使用者的點數餘額。
    系統會在 User 建立時自動建立對應的 UserPoints 紀錄。
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="points",
        help_text="所屬用戶",
    )
    
    balance = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="點數餘額，不得為負數",
    )
    
    is_locked = models.BooleanField(
        default=False,
        help_text="錢包鎖定狀態，True=鎖定（禁止交易）, False=正常",
    )
    
    class Meta:
        db_table = "user_points"
        verbose_name = "使用者點數"
        verbose_name_plural = "使用者點數"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.user.username} - 餘額: {self.balance} 點"
    
    def lock(self):
        """鎖定錢包"""
        self.is_locked = True
        self.save(update_fields=["is_locked"])
    
    def unlock(self):
        """解鎖錢包"""
        self.is_locked = False
        self.save(update_fields=["is_locked"])
