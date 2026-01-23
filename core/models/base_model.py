from django.db import models


class BaseModel(models.Model):
    """
    基本模型樣板，提供共用的時間戳記欄位

    包含:
    - 創建時間 (created_at)
    - 修改時間 (updated_at)
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="創建時間",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="修改時間",
    )

    class Meta:
        abstract = True


