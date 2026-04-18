from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from menu.models import Product
from orders.cart import Cart
from orders.models import Order

from .serializers import OrderSerializer, ProductSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).prefetch_related("variants")
    serializer_class = ProductSerializer


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.select_related("customer").prefetch_related("items__variant__product")
    serializer_class = OrderSerializer


class CartAPIView(APIView):
    def get(self, request):
        cart = Cart(request)
        items = [
            {
                "variant_id": item["variant"].id,
                "product": item["variant"].product.name,
                "size": item["variant"].get_size_display(),
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
                "line_total": item["line_total"],
            }
            for item in cart
        ]
        return Response({"items": items, "total": cart.get_total_price()})
