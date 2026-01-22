from django.db import models
from django.conf import settings


class BaseModel(models.Model):
    """
    基本模型樣板，提供共用的基本欄位

    包含:
    - 創建時間
    - 創建者
    - 修改時間
    - 修改者
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="創建時間",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
        help_text="創建者",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True,
        help_text="修改時間",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
        help_text="修改者",
    )

    def save(self, *args, **kwargs):
        """
        自動記錄創建者和修改者
        需要在 middleware 中設定當前用戶
        """
        from config.middlewares import CurrentUserMiddleware
        
        user = CurrentUserMiddleware.get_current_user()

        if not self.pk or not self.created_by:  # create 時
            self.created_by = user
        else:  # update 時
            self.updated_by = user
        
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

