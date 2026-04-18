from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from menu.models import ProductVariant

from .cart import Cart
from .customer_session import CUSTOMER_SESSION_KEY, get_logged_in_customer
from .forms import CheckoutForm, CustomerLoginForm, CustomerSignupForm
from .models import Customer, Order, OrderItem, Payment
from .services import generate_tracking_code, simulate_mpesa_stk_push


def cart_detail(request):
    return render(request, "orders/cart.html", {"cart": Cart(request)})


@require_POST
def cart_add(request, variant_id):
    cart = Cart(request)
    variant = get_object_or_404(ProductVariant, id=variant_id)
    quantity = int(request.POST.get("quantity", 1))
    cart.add(variant.id, quantity=quantity)
    messages.success(request, f"Added {variant.product.name} to your cart 🎉")
    return redirect("cart")


def cart_remove(request, variant_id):
    cart = Cart(request)
    cart.remove(variant_id)
    messages.info(request, "Item removed from cart.")
    return redirect("cart")


@require_POST
def cart_update(request, variant_id):
    cart = Cart(request)
    quantity = max(1, int(request.POST.get("quantity", 1)))
    cart.add(variant_id, quantity=quantity, override_quantity=True)
    messages.success(request, "Cart updated.")
    return redirect("cart")


def checkout(request):
    cart = Cart(request)
    if cart.get_count() == 0:
        messages.error(request, "Your cart is empty.")
        return redirect("menu")

    customer = get_logged_in_customer(request)
    if not customer:
        messages.info(request, "Create an account or login to checkout.")
        return redirect("customer-login")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            customer.location = form.cleaned_data["location"]
            customer.save(update_fields=["location"])
            subtotal = Decimal(cart.get_total_price())
            delivery_fee = Decimal("0")
            order = Order.objects.create(
                customer=customer,
                payment_method=form.cleaned_data["payment_method"],
                notes=form.cleaned_data["notes"],
                subtotal=subtotal,
                delivery_fee=delivery_fee,
                total=subtotal + delivery_fee,
                tracking_code=generate_tracking_code(),
            )

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    variant=item["variant"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                    line_total=item["line_total"],
                )

            payment_status = Payment.Status.PENDING
            provider_message = "Awaiting cash payment on delivery."
            transaction_id = ""

            if order.payment_method == Order.PaymentMethod.MPESA:
                mpesa_result = simulate_mpesa_stk_push(order)
                payment_status = mpesa_result["status"]
                provider_message = mpesa_result["message"]
                transaction_id = mpesa_result["transaction_id"]

            Payment.objects.create(
                order=order,
                method=order.payment_method,
                amount=order.total,
                status=payment_status,
                transaction_id=transaction_id,
                provider_message=provider_message,
            )
            cart.clear()
            return redirect("order-success", tracking_code=order.tracking_code)
    else:
        form = CheckoutForm(initial={"location": customer.location})

    return render(
        request,
        "orders/checkout.html",
        {"form": form, "cart": cart, "customer": customer},
    )


def order_success(request, tracking_code):
    order = get_object_or_404(Order, tracking_code=tracking_code)
    return render(request, "orders/success.html", {"order": order})


def order_tracking(request):
    order = None
    tracking_code = request.GET.get("tracking_code")
    if tracking_code:
        order = Order.objects.filter(tracking_code=tracking_code).select_related(
            "customer"
        ).first()
    return render(request, "orders/tracking.html", {"order": order})


def customer_signup(request):
    if get_logged_in_customer(request):
        return redirect("checkout")
    if request.method == "POST":
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            if Customer.objects.filter(phone=form.cleaned_data["phone"]).exists():
                form.add_error("phone", "An account with this phone already exists.")
            else:
                customer = Customer(
                    name=form.cleaned_data["name"],
                    phone=form.cleaned_data["phone"],
                )
                customer.set_pin(form.cleaned_data["pin"])
                customer.save()
                request.session[CUSTOMER_SESSION_KEY] = customer.id
                messages.success(request, "Account created. You are now logged in.")
                next_url = request.GET.get("next") or "checkout"
                return redirect(next_url)
    else:
        form = CustomerSignupForm()
    return render(request, "orders/customer_signup.html", {"form": form})


def customer_login(request):
    if get_logged_in_customer(request):
        return redirect("checkout")
    if request.method == "POST":
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            customer = Customer.objects.filter(phone=form.cleaned_data["phone"]).first()
            if not customer or not customer.check_pin(form.cleaned_data["pin"]):
                form.add_error(None, "Invalid phone or PIN.")
            else:
                request.session[CUSTOMER_SESSION_KEY] = customer.id
                messages.success(request, f"Welcome back, {customer.name}!")
                next_url = request.GET.get("next") or "checkout"
                return redirect(next_url)
    else:
        form = CustomerLoginForm()
    return render(request, "orders/customer_login.html", {"form": form})


@require_POST
def customer_logout(request):
    request.session.pop(CUSTOMER_SESSION_KEY, None)
    messages.info(request, "You are logged out.")
    return redirect("home")
