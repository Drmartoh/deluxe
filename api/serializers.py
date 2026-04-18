from rest_framework import serializers

from menu.models import Product, ProductVariant
from orders.models import Order, OrderItem


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ["id", "size", "price", "is_default"]


class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "description", "category", "variants"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="variant.product.name", read_only=True)
    size = serializers.CharField(source="variant.get_size_display", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "size", "quantity", "unit_price", "line_total"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "tracking_code",
            "customer",
            "status",
            "payment_method",
            "subtotal",
            "delivery_fee",
            "total",
            "created_at",
            "items",
        ]
