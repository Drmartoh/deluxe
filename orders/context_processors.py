from .cart import Cart
from .customer_session import get_logged_in_customer


def cart_data(request):
    cart = Cart(request)
    customer_account = get_logged_in_customer(request)
    return {
        "cart_count": cart.get_count(),
        "cart_total": cart.get_total_price(),
        "customer_account": customer_account,
    }
