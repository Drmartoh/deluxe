from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CartAPIView, OrderViewSet, ProductViewSet

router = DefaultRouter()
router.register("products", ProductViewSet, basename="api-products")
router.register("orders", OrderViewSet, basename="api-orders")

urlpatterns = router.urls + [
    path("cart/", CartAPIView.as_view(), name="api-cart"),
]
