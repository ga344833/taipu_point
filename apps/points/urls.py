from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.points.views import (
    PointDepositView,
    PointTransactionViewSet,
    PointExchangeView,
    PointExchangeViewSet,
)

app_name = "points"

router = DefaultRouter()
router.register(r"points/transactions", PointTransactionViewSet, basename="point-transaction")
router.register(r"points/exchanges", PointExchangeViewSet, basename="point-exchange")

urlpatterns = [
    path("points/deposit/", PointDepositView.as_view(), name="point-deposit"),
    path("points/exchange/", PointExchangeView.as_view(), name="point-exchange"),
    path("", include(router.urls)),
]


