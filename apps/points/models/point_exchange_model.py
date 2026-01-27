from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.models.base_model import BaseModel
from apps.products.models import Product


class ExchangeStatusChoices(models.TextChoices):
    """交換狀態選項"""
    PENDING = "PENDING", _("待核銷")
    VERIFIED = "VERIFIED", _("已核銷")


class PointExchange(BaseModel):
    """
    點數兌換紀錄模型
    
    記錄會員使用點數兌換商品的完整資訊，包含交換序號供店家核銷使用。
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="point_exchanges",
        help_text="兌換會員",
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="exchanges",
        help_text="兌換商品",
    )
    
    exchange_code = models.CharField(
        max_length=20,
        unique=True,
        help_text="交換序號，用於店家核銷（格式：EX + 日期 + 隨機碼）",
    )
    
    points_spent = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="消費點數，紀錄當時交換的點數價格",
    )
    
    status = models.CharField(
        max_length=20,
        choices=ExchangeStatusChoices.choices,
        default=ExchangeStatusChoices.PENDING,
        help_text="交換狀態：PENDING=待核銷, VERIFIED=已核銷",
    )
    
    class Meta:
        db_table = "point_exchanges"
        verbose_name = "點數兌換紀錄"
        verbose_name_plural = "點數兌換紀錄"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["product", "status"]),
            models.Index(fields=["exchange_code"]),
            models.Index(fields=["status"]),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.exchange_code})"
