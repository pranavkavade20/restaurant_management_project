# utils/email.py
import logging
from django.core.mail import send_mail, BadHeaderError
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.conf import settings

logger = logging.getLogger(__name__)

def send_order_confirmation_email(order_id: int, customer_email: str, order_details: str) -> dict:
    """
    Sends an order confirmation email to the customer.

    Args:
        order_id (int): ID of the order.
        customer_email (str): Customer's email address.
        order_details (str): A string containing order summary/details.

    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        # Validate email
        validate_email(customer_email)
        
        subject = f"Order Confirmation - Order #{order_id}"
        message = (
            f"Dear Customer,\n\n"
            f"Thank you for your order!\n\n"
            f"Order ID: {order_id}\n"
            f"Order Details:\n{order_details}\n\n"
            f"We will notify you once your order is shipped.\n\n"
            f"Best regards,\n"
            f"{settings.DEFAULT_FROM_EMAIL}"
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [customer_email]

        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False
        )

        return {'success': True, 'message': 'Order confirmation email sent successfully.'}

    except ValidationError:
        error_msg = f"Invalid email address: {customer_email}"
        logger.error(error_msg)
        return {'success': False, 'message': error_msg}

    except BadHeaderError:
        error_msg = "Invalid header found in the email."
        logger.error(error_msg)
        return {'success': False, 'message': error_msg}

    except Exception as e:
        logger.exception(f"Error sending order confirmation email: {e}")
        return {'success': False, 'message': 'An unexpected error occurred while sending email.'}
