CUSTOMER_SESSION_KEY = "customer_id"


def get_logged_in_customer(request):
    customer_id = request.session.get(CUSTOMER_SESSION_KEY)
    if not customer_id:
        return None
    from .models import Customer

    return Customer.objects.filter(id=customer_id).first()
