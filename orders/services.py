from decimal import Decimal
from uuid import uuid4

from .models import Payment


def generate_tracking_code():
    return uuid4().hex[:10].upper()


def simulate_mpesa_stk_push(order):
    """
    Placeholder for M-Pesa STK push integration.
    Replace this with Daraja API calls in production.
    """
    transaction_id = f"MPESA-{uuid4().hex[:12].upper()}"
    return {
        "status": Payment.Status.SUCCESS,
        "transaction_id": transaction_id,
        "message": "STK push request accepted.",
        "amount": Decimal(order.total),
    }
