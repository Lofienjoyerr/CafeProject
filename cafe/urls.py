from django.urls import path, include
from rest_framework import routers

from cafe.views import OrdersViewSet, ItemsViewSet, CalcRevenueView

router = routers.SimpleRouter()
router.register("orders", OrdersViewSet)
router.register("items", ItemsViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("revenue/", CalcRevenueView.as_view(), name='calc_revenue'),
]
