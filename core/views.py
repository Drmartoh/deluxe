from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from core.forms import (
    AnnouncementForm,
    CategoryForm,
    OrderStatusForm,
    ProductForm,
    ProductVariantForm,
)
from menu.models import Category
from menu.models import Product
from menu.models import ProductVariant
from orders.models import Customer, Order, OrderItem, Payment

from .models import Announcement


def staff_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('staff-login')}?next={request.path}")
        if not request.user.is_staff:
            messages.error(request, "You are not allowed to access admin panel.")
            return redirect("home")
        return view_func(request, *args, **kwargs)

    return _wrapped


def paginate(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def home(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:6]
    announcements = Announcement.objects.filter(is_active=True)[:3]
    context = {
        "featured_products": featured_products,
        "announcements": announcements,
    }
    return render(request, "core/home.html", context)


@staff_required
def admin_dashboard(request):
    total_orders = Order.objects.count()
    revenue = Order.objects.filter(status=Order.Status.DELIVERED).aggregate(
        total=Sum("total")
    )["total"] or 0
    active_orders = Order.objects.exclude(status=Order.Status.DELIVERED).count()
    today = timezone.localdate()
    orders_today = Order.objects.filter(created_at__date=today).count()
    catalog_items = Product.objects.filter(is_active=True).count()
    popular_qs = (
        OrderItem.objects.values("variant__product__name")
        .annotate(total_qty=Sum("quantity"))
        .order_by("-total_qty")[:5]
    )
    popular_list = list(popular_qs)
    popular_max_qty = max((row["total_qty"] for row in popular_list), default=1)
    return render(
        request,
        "core/admin_dashboard.html",
        {
            "page_title": "Overview",
            "total_orders": total_orders,
            "revenue": revenue,
            "active_orders": active_orders,
            "orders_today": orders_today,
            "catalog_items": catalog_items,
            "popular_items": popular_list,
            "popular_max_qty": popular_max_qty,
        },
    )


@staff_required
@permission_required("menu.view_category", raise_exception=True)
def categories_admin(request):
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "name")
    allowed_sort = {"name", "-name", "created_at", "-created_at"}
    if sort not in allowed_sort:
        sort = "name"
    categories = Category.objects.all()
    if query:
        categories = categories.filter(name__icontains=query)
    categories = categories.order_by(sort)
    categories_page = paginate(request, categories, per_page=8)
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category saved.")
        return redirect("admin-categories")
    return render(
        request,
        "adminpanel/categories.html",
        {
            "categories": categories_page,
            "form": form,
            "page_title": "Categories",
            "q": query,
            "sort": sort,
        },
    )


@staff_required
@permission_required("menu.change_category", raise_exception=True)
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category updated.")
        return redirect("admin-categories")
    return render(
        request,
        "adminpanel/form_page.html",
        {"form": form, "page_title": "Edit Category", "back_url": "admin-categories"},
    )


@require_POST
@staff_required
@permission_required("menu.delete_category", raise_exception=True)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.info(request, "Category deleted.")
    return redirect("admin-categories")


@staff_required
@permission_required("menu.view_product", raise_exception=True)
def products_admin(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    sort = request.GET.get("sort", "-created_at")
    allowed_sort = {"name", "-name", "created_at", "-created_at"}
    if sort not in allowed_sort:
        sort = "-created_at"
    products = Product.objects.select_related("category").all()
    if query:
        products = products.filter(name__icontains=query)
    if category:
        products = products.filter(category_id=category)
    products = products.order_by(sort)
    products_page = paginate(request, products, per_page=8)
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Product saved.")
        return redirect("admin-products")
    return render(
        request,
        "adminpanel/products.html",
        {
            "products": products_page,
            "form": form,
            "page_title": "Products",
            "categories": Category.objects.all(),
            "q": query,
            "sort": sort,
            "category_filter": category,
        },
    )


@staff_required
@permission_required("menu.change_product", raise_exception=True)
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Product updated.")
        return redirect("admin-products")
    return render(
        request,
        "adminpanel/form_page.html",
        {"form": form, "page_title": "Edit Product", "back_url": "admin-products"},
    )


@require_POST
@staff_required
@permission_required("menu.delete_product", raise_exception=True)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.info(request, "Product deleted.")
    return redirect("admin-products")


@staff_required
@permission_required("menu.view_productvariant", raise_exception=True)
def variants_admin(request):
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "product__name")
    allowed_sort = {"product__name", "-product__name", "price", "-price", "size", "-size"}
    if sort not in allowed_sort:
        sort = "product__name"
    variants = ProductVariant.objects.select_related("product").all()
    if query:
        variants = variants.filter(product__name__icontains=query)
    variants = variants.order_by(sort)
    variants_page = paginate(request, variants, per_page=10)
    form = ProductVariantForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Variant saved.")
        return redirect("admin-variants")
    return render(
        request,
        "adminpanel/variants.html",
        {
            "variants": variants_page,
            "form": form,
            "page_title": "Product Variants",
            "q": query,
            "sort": sort,
        },
    )


@staff_required
@permission_required("menu.change_productvariant", raise_exception=True)
def variant_edit(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)
    form = ProductVariantForm(request.POST or None, instance=variant)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Variant updated.")
        return redirect("admin-variants")
    return render(
        request,
        "adminpanel/form_page.html",
        {"form": form, "page_title": "Edit Variant", "back_url": "admin-variants"},
    )


@require_POST
@staff_required
@permission_required("menu.delete_productvariant", raise_exception=True)
def variant_delete(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)
    variant.delete()
    messages.info(request, "Variant deleted.")
    return redirect("admin-variants")


@staff_required
@permission_required("orders.view_order", raise_exception=True)
def orders_admin(request):
    if request.method == "POST":
        if not request.user.has_perm("orders.change_order"):
            messages.error(request, "You do not have permission to update orders.")
            return redirect("admin-orders")

        action = request.POST.get("action")
        if action == "bulk_status":
            ids = request.POST.getlist("selected_ids")
            if not ids and request.POST.get("selected_ids_csv"):
                ids = [
                    item
                    for item in request.POST.get("selected_ids_csv", "").split(",")
                    if item
                ]
            status = request.POST.get("bulk_status")
            valid_statuses = {choice[0] for choice in Order.Status.choices}
            if ids and status in valid_statuses:
                updated = Order.objects.filter(id__in=ids).update(status=status)
                messages.success(request, f"{updated} orders updated.")
            else:
                messages.error(request, "Invalid bulk update request.")
            return redirect("admin-orders")

        if action == "single_status":
            order_id = request.POST.get("order_id")
            status = request.POST.get("status")
            valid_statuses = {choice[0] for choice in Order.Status.choices}
            if order_id and status in valid_statuses:
                Order.objects.filter(id=order_id).update(status=status)
                messages.success(request, f"Order #{order_id} status updated.")
            else:
                messages.error(request, "Invalid status update.")
            return redirect("admin-orders")

        messages.error(request, "Unknown action.")
        return redirect("admin-orders")

    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    sort = request.GET.get("sort", "-created_at")
    allowed_sort = {"created_at", "-created_at", "total", "-total", "status", "-status"}
    if sort not in allowed_sort:
        sort = "-created_at"
    orders = (
        Order.objects.select_related("customer", "payment")
        .prefetch_related("items__variant__product")
        .all()
    )
    if query:
        orders = orders.filter(customer__name__icontains=query)
    if status:
        orders = orders.filter(status=status)
    orders = orders.order_by(sort)
    orders_page = paginate(request, orders, per_page=10)
    return render(
        request,
        "adminpanel/orders.html",
        {
            "orders": orders_page,
            "status_choices": Order.Status.choices,
            "page_title": "Orders",
            "q": query,
            "status_filter": status,
            "sort": sort,
        },
    )


@staff_required
@permission_required("core.view_announcement", raise_exception=True)
def announcements_admin(request):
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "-created_at")
    allowed_sort = {"title", "-title", "created_at", "-created_at"}
    if sort not in allowed_sort:
        sort = "-created_at"
    announcements = Announcement.objects.all()
    if query:
        announcements = announcements.filter(title__icontains=query)
    announcements = announcements.order_by(sort)
    announcements_page = paginate(request, announcements, per_page=8)
    form = AnnouncementForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Announcement saved.")
        return redirect("admin-announcements")
    return render(
        request,
        "adminpanel/announcements.html",
        {
            "announcements": announcements_page,
            "form": form,
            "page_title": "Announcements",
            "q": query,
            "sort": sort,
        },
    )


@staff_required
@permission_required("core.change_announcement", raise_exception=True)
def announcement_edit(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    form = AnnouncementForm(request.POST or None, instance=announcement)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Announcement updated.")
        return redirect("admin-announcements")
    return render(
        request,
        "adminpanel/form_page.html",
        {"form": form, "page_title": "Edit Announcement", "back_url": "admin-announcements"},
    )


@require_POST
@staff_required
@permission_required("core.delete_announcement", raise_exception=True)
def announcement_delete(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    announcement.delete()
    messages.info(request, "Announcement deleted.")
    return redirect("admin-announcements")


@staff_required
@permission_required("orders.view_customer", raise_exception=True)
def customers_admin(request):
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "-created_at")
    allowed_sort = {"name", "-name", "created_at", "-created_at"}
    if sort not in allowed_sort:
        sort = "-created_at"
    customers = Customer.objects.all()
    if query:
        customers = customers.filter(name__icontains=query)
    customers = customers.order_by(sort)
    customers_page = paginate(request, customers, per_page=12)
    return render(
        request,
        "adminpanel/customers.html",
        {"customers": customers_page, "page_title": "Customers", "q": query, "sort": sort},
    )


@staff_required
@permission_required("orders.view_payment", raise_exception=True)
def payments_admin(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    sort = request.GET.get("sort", "-created_at")
    allowed_sort = {"created_at", "-created_at", "amount", "-amount", "status", "-status"}
    if sort not in allowed_sort:
        sort = "-created_at"
    payments = Payment.objects.select_related("order", "order__customer").all()
    if query:
        payments = payments.filter(order__customer__name__icontains=query)
    if status:
        payments = payments.filter(status=status)
    payments = payments.order_by(sort)
    payments_page = paginate(request, payments, per_page=12)
    return render(
        request,
        "adminpanel/payments.html",
        {
            "payments": payments_page,
            "page_title": "Payments",
            "q": query,
            "status_filter": status,
            "sort": sort,
            "payment_status_choices": Payment.Status.choices,
        },
    )
