from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class InsufficientPointsException(APIException):
    """點數不足異常"""
    status_code = 400
    default_detail = _("點數餘額不足")
    default_code = "insufficient_points"


class InsufficientStockException(APIException):
    """庫存不足異常"""
    status_code = 400
    default_detail = _("商品庫存不足")
    default_code = "insufficient_stock"


class ProductNotActiveException(APIException):
    """商品未啟用異常"""
    status_code = 400
    default_detail = _("商品未啟用或已下架")
    default_code = "product_not_active"


class PaymentFailedException(APIException):
    """支付失敗異常"""
    status_code = 400
    default_detail = _("支付處理失敗")
    default_code = "payment_failed"


