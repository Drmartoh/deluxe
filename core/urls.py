from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import (
    admin_dashboard,
    announcement_delete,
    announcement_edit,
    announcements_admin,
    categories_admin,
    category_delete,
    category_edit,
    customers_admin,
    home,
    orders_admin,
    payments_admin,
    product_delete,
    product_edit,
    products_admin,
    variant_delete,
    variant_edit,
    variants_admin,
)

urlpatterns = [
    path("", home, name="home"),
    path(
        "staff/login/",
        LoginView.as_view(template_name="core/staff_login.html", redirect_authenticated_user=True),
        name="staff-login",
    ),
    path("staff/logout/", LogoutView.as_view(), name="staff-logout"),
    path("dashboard/", admin_dashboard, name="admin-dashboard"),
    path("dashboard/categories/", categories_admin, name="admin-categories"),
    path("dashboard/categories/<int:pk>/edit/", category_edit, name="admin-category-edit"),
    path("dashboard/categories/<int:pk>/delete/", category_delete, name="admin-category-delete"),
    path("dashboard/products/", products_admin, name="admin-products"),
    path("dashboard/products/<int:pk>/edit/", product_edit, name="admin-product-edit"),
    path("dashboard/products/<int:pk>/delete/", product_delete, name="admin-product-delete"),
    path("dashboard/variants/", variants_admin, name="admin-variants"),
    path("dashboard/variants/<int:pk>/edit/", variant_edit, name="admin-variant-edit"),
    path("dashboard/variants/<int:pk>/delete/", variant_delete, name="admin-variant-delete"),
    path("dashboard/orders/", orders_admin, name="admin-orders"),
    path("dashboard/announcements/", announcements_admin, name="admin-announcements"),
    path(
        "dashboard/announcements/<int:pk>/edit/",
        announcement_edit,
        name="admin-announcement-edit",
    ),
    path(
        "dashboard/announcements/<int:pk>/delete/",
        announcement_delete,
        name="admin-announcement-delete",
    ),
    path("dashboard/customers/", customers_admin, name="admin-customers"),
    path("dashboard/payments/", payments_admin, name="admin-payments"),
]
