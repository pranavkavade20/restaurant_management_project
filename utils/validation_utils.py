import logging
from email_validator import validate_email, EmailNotValidError

# Configure logger
logger = logging.getLogger(__name__)

def is_valid_email(email: str) -> bool:
    """
    Validate an email address using Python's email-validator library.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if valid, False otherwise.

    This function checks the syntax of an email using the `email-validator` library.
    It avoids regex-based pitfalls and ensures more accurate validation for modern email formats.
    """
    try:
        # validate_email() raises EmailNotValidError if invalid
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError as e:
        logger.warning(f"Invalid email attempted: {email}. Reason: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error while validating email: {email}. Error: {e}")
        return False
