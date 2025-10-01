# home/utils.py

from django.core.mail import EmailMessage
from django.conf import settings
import logging
import asyncio

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
