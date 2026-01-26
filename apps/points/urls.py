from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.points.views import PointDepositView, PointTransactionViewSet

app_name = "points"

router = DefaultRouter()
router.register(r"points/transactions", PointTransactionViewSet, basename="point-transaction")

urlpatterns = [
    path("points/deposit/", PointDepositView.as_view(), name="point-deposit"),
    path("", include(router.urls)),
]


