from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.models.base_model import BaseModel


class TransactionTypeChoices(models.TextChoices):
    """交易類型選項"""
    DEPOSIT = "DEPOSIT", _("儲值")
    REDEMPTION = "REDEMPTION", _("兌換")


class PointTransaction(BaseModel):
    """
    點數交易紀錄模型
    
    記錄所有點數異動，包含儲值、兌換等操作。
    使用資料庫事務確保 UserPoints 餘額更新與交易紀錄的一致性。
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="point_transactions",
        help_text="所屬用戶",
    )
    
    amount = models.IntegerField(
        help_text="異動點數（儲值為正數，兌換為負數）",
    )
    
    tx_type = models.CharField(
        max_length=20,
        choices=TransactionTypeChoices.choices,
        help_text="交易類型：DEPOSIT=儲值, REDEMPTION=兌換",
    )
    
    is_success = models.BooleanField(
        default=True,
        help_text="交易狀態，True=成功, False=失敗",
    )
    
    balance_after = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="異動後餘額，用於後續對帳審核",
    )
    
    memo = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text="備註",
    )
    
    class Meta:
        db_table = "point_transactions"
        verbose_name = "點數交易紀錄"
        verbose_name_plural = "點數交易紀錄"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "tx_type"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["is_success"]),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_tx_type_display()} {self.amount} 點 ({'成功' if self.is_success else '失敗'})"
