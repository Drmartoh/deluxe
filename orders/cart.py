from menu.models import ProductVariant


CART_SESSION_KEY = "cart"


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(CART_SESSION_KEY, {})
        if CART_SESSION_KEY not in self.session:
            self.session[CART_SESSION_KEY] = self.cart

    def add(self, variant_id, quantity=1, override_quantity=False):
        variant_key = str(variant_id)
        if variant_key not in self.cart:
            self.cart[variant_key] = {"quantity": 0}
        if override_quantity:
            self.cart[variant_key]["quantity"] = quantity
        else:
            self.cart[variant_key]["quantity"] += quantity
        self.save()

    def remove(self, variant_id):
        variant_key = str(variant_id)
        if variant_key in self.cart:
            del self.cart[variant_key]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        if CART_SESSION_KEY in self.session:
            del self.session[CART_SESSION_KEY]
            self.session.modified = True

    def __iter__(self):
        variant_ids = self.cart.keys()
        variants = ProductVariant.objects.filter(id__in=variant_ids).select_related(
            "product"
        )
        cart_copy = self.cart.copy()
        for variant in variants:
            cart_copy[str(variant.id)]["variant"] = variant
            cart_copy[str(variant.id)]["unit_price"] = variant.price
            cart_copy[str(variant.id)]["line_total"] = variant.price * cart_copy[str(variant.id)][
                "quantity"
            ]
            yield cart_copy[str(variant.id)]

    def get_total_price(self):
        return sum(item["line_total"] for item in self)

    def get_count(self):
        return sum(item["quantity"] for item in self.cart.values())
