import logging
from email_validator import validate_email, EmailNotValidError

# Configure logger
logger = logging.getLogger(__name__)

def is_valid_email(email: str) -> bool:
    """
    Validate an email address using Python's email-validator library.

    Args:
        email (str): Email address to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        # validate_email will raise EmailNotValidError if not valid
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError as e:
        logger.warning(f"Invalid email attempted: {email}. Reason: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error while validating email: {email}. Error: {e}")
        return False
