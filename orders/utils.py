# orders/utils.py
import string
import secrets
from datetime import date
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone


# -------------------------
# Coupon code utility
# -------------------------
def generate_coupon_code(length: int = 10) -> str:
    from .models import Coupon  # lazy import

    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(length))
        if not Coupon.objects.filter(code=code).exists():
            return code


# -------------------------
# Unique order id utility
# -------------------------
def generate_unique_order_id(length: int = 8) -> str:
    from .models import Order  # lazy import

    characters = string.ascii_uppercase + string.digits
    while True:
        order_id = "".join(secrets.choice(characters) for _ in range(length))
        if not Order.objects.filter(custom_order_id=order_id).exists():
            return order_id


# -------------------------
# Daily sales helper
# -------------------------
def get_daily_sales_total(target_date: date) -> float:
    from .models import Order  # lazy import

    if not isinstance(target_date, date):
        raise ValueError("The 'target_date' must be a datetime.date instance.")

    result = (
        Order.objects.filter(created_at__date=target_date)
        .aggregate(total_sum=Sum("total_amount"))
        .get("total_sum")
    )
    return float(result or 0)


# -------------------------
# Discount utility (NEW)
# -------------------------
def calculate_discount(amount: Decimal, coupon=None) -> Decimal:
    """
    Calculate discount amount for a given monetary amount using a Coupon.

    Args:
        amount (Decimal): The original amount (subtotal).
        coupon (Coupon instance or coupon code string or None): Coupon to apply.

    Returns:
        Decimal: Discount amount (not the final total). Returns Decimal('0.00') if no valid discount.
    """
    from .models import Coupon  # lazy import to avoid circular imports
    from django.utils import timezone

    if amount is None:
        return Decimal("0.00")

    # Ensure Decimal
    if not isinstance(amount, Decimal):
        try:
            amount = Decimal(str(amount))
        except Exception:
            return Decimal("0.00")

    # Resolve coupon input types
    coupon_obj = None
    if coupon is None:
        return Decimal("0.00")
    if isinstance(coupon, str):
        coupon_obj = Coupon.objects.filter(code__iexact=coupon).first()
    else:
        # assume it's a Coupon instance
        coupon_obj = coupon

    if not coupon_obj:
        return Decimal("0.00")

    # Validate coupon active state and date range
    now = timezone.now()
    if not getattr(coupon_obj, "is_active", False):
        return Decimal("0.00")
    valid_from = getattr(coupon_obj, "valid_from", None)
    valid_to = getattr(coupon_obj, "valid_to", None)
    if valid_from and valid_from > now:
        return Decimal("0.00")
    if valid_to and valid_to < now:
        return Decimal("0.00")

    # Calculate percentage discount
    try:
        discount_pct = Decimal(coupon_obj.discount) / Decimal("100")
    except Exception:
        return Decimal("0.00")

    discount_amount = (amount * discount_pct).quantize(Decimal("0.01"))
    # Cap discount to not exceed the amount
    if discount_amount > amount:
        return amount
    return discount_amount
