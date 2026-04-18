from django.urls import path

from .views import (
    cart_add,
    cart_detail,
    cart_remove,
    cart_update,
    checkout,
    customer_login,
    customer_logout,
    customer_signup,
    order_success,
    order_tracking,
)

urlpatterns = [
    path("cart/", cart_detail, name="cart"),
    path("cart/add/<int:variant_id>/", cart_add, name="cart-add"),
    path("cart/remove/<int:variant_id>/", cart_remove, name="cart-remove"),
    path("cart/update/<int:variant_id>/", cart_update, name="cart-update"),
    path("checkout/", checkout, name="checkout"),
    path("account/signup/", customer_signup, name="customer-signup"),
    path("account/login/", customer_login, name="customer-login"),
    path("account/logout/", customer_logout, name="customer-logout"),
    path("success/<str:tracking_code>/", order_success, name="order-success"),
    path("tracking/", order_tracking, name="order-tracking"),
]
