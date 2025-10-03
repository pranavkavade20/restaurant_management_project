# orders/utils.py
import string
import secrets

def generate_coupon_code(length: int = 10) -> str:
    """
    Generate a unique alphanumeric coupon code.
    Ensures uniqueness by checking against the Coupon model.
    """
    from .models import Coupon  # Lazy import to avoid circular import
    alphabet = string.ascii_uppercase + string.digits

    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(length))
        if not Coupon.objects.filter(code=code).exists():
            return code

def generate_unique_order_id(length: int = 8) -> str:
    """
    Generates a unique short alphanumeric order ID.
    Ensures uniqueness by checking existing Order IDs in the database.

    Args:
        length (int): Length of the generated ID. Default is 8.

    Returns:
        str: Unique order ID.
    """
    from .models import Order  # Lazy import to avoid circular import
    characters = string.ascii_uppercase + string.digits  # e.g., "ABCD1234"
    
    while True:
        order_id = ''.join(secrets.choice(characters) for _ in range(length))
        if not Order.objects.filter(custom_order_id=order_id).exists():
            return order_id
