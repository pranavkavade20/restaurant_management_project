# home/utils.py

from django.core.mail import EmailMessage
from django.conf import settings
import logging
import asyncio
from datetime import datetime, time

logger = logging.getLogger(__name__)

async def send_email_async(subject: str, body: str, recipient_list: list, from_email: str = None) -> bool:
    """
    Asynchronously sends an email to the given recipient(s).

    Args:
        subject (str): The email subject line.
        body (str): The body of the email (plain text).
        recipient_list (list): List of recipient email addresses.
        from_email (str, optional): Sender's email address. Defaults to settings.DEFAULT_FROM_EMAIL.

    Returns:
        bool: True if email sent successfully, False otherwise.
    """
    from_email = from_email or settings.DEFAULT_FROM_EMAIL

    try:
        email = EmailMessage(subject=subject, body=body, from_email=from_email, to=recipient_list)
        # Run the blocking send() method in a separate thread
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, email.send, False)
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}: {e}")
        return False


def is_restaurant_open() -> bool:
    """
    Check if the restaurant is currently open based on predefined operating hours.

    Returns:
        bool: True if the restaurant is open, False otherwise.
    """
    # Get current day (0=Monday, 6=Sunday) and current time
    now = datetime.now()
    current_day = now.weekday()
    current_time = now.time()

    # Define operating hours
    # Example: Open 9:00 AM to 10:00 PM (same hours every day)
    opening_hours = {
        0: (time(9, 0), time(22, 0)),  # Monday
        1: (time(9, 0), time(22, 0)),  # Tuesday
        2: (time(9, 0), time(22, 0)),  # Wednesday
        3: (time(9, 0), time(22, 0)),  # Thursday
        4: (time(9, 0), time(22, 0)),  # Friday
        5: (time(10, 0), time(23, 0)), # Saturday
        6: (time(10, 0), time(22, 0)), # Sunday
    }

    # Get today's open and close time
    open_time, close_time = opening_hours.get(current_day, (None, None))

    # If no hours defined, restaurant is closed
    if not open_time or not close_time:
        return False

    # Check if current time is within operating hours
    return open_time <= current_time <= close_time


# home/utils.py
import logging

# Configure logger
logger = logging.getLogger(__name__)

def calculate_discount(original_price, discount_percentage):
    """
    Calculate the discounted price based on the original price and discount percentage.

    Args:
        original_price (float or Decimal): The original price of the item.
        discount_percentage (float): The discount percentage (0-100).

    Returns:
        float: The final discounted price.

    Raises:
        ValueError: If inputs are invalid (e.g., negative price or invalid percentage).
    """
    try:
        # ✅ Convert input to float for safety
        original_price = float(original_price)
        discount_percentage = float(discount_percentage)

        # ✅ Validate inputs
        if original_price < 0:
            raise ValueError("Original price cannot be negative.")
        if not (0 <= discount_percentage <= 100):
            raise ValueError("Discount percentage must be between 0 and 100.")

        # ✅ Calculate discounted price
        discounted_price = original_price * (1 - discount_percentage / 100)
        return round(discounted_price, 2)

    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid discount calculation input: price={original_price}, discount={discount_percentage}. Error: {e}")
        return original_price  # Return original price as fallback
    except Exception as e:
        logger.error(f"Unexpected error during discount calculation: {e}")
        return original_price
