import string
import secrets
from .models import Coupon

def generate_coupon_code(length: int = 10) -> str:
    """
    Generate a unique alphanumeric coupon code.
    Ensures uniqueness by checking against the Coupon model.
    """
    alphabet = string.ascii_uppercase + string.digits

    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(length))
        if not Coupon.objects.filter(code=code).exists():
            return code
