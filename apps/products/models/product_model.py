from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from core.models.base_model import BaseModel


class Product(BaseModel):
    """
    商品模型
    
    用於店家上架商品，包含商品名稱、所需點數、庫存等核心欄位。
    未來將整合權限控制，確保僅店家/管理者可操作。
    """
    
    store = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        help_text="所屬店家",
    )
    
    name = models.CharField(
        max_length=200,
        help_text="商品名稱",
    )
    
    required_points = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="兌換所需點數，不得為負數",
    )
    
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="庫存數量，不得為負數",
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="上架狀態，True=上架, False=下架（軟刪除）",
    )
    
    memo = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text="商品備註",
    )
    
    class Meta:
        db_table = "products"
        verbose_name = "商品"
        verbose_name_plural = "商品"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["store", "is_active"]),
            models.Index(fields=["is_active"]),
        ]
    
    def __str__(self):
        return f"{self.name} (店家: {self.store.username}, 點數: {self.required_points})"
