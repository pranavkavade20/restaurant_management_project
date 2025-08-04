from django.db import models
from django.core.validatiors import RegexValidator

"""
User Profile model for saving information of authenticated users.
"""
class UserProfile(models.Model):
    # Save the name of user.
    name = models.CharField(max_length=50)
    # Email of user for logging.     
    email = models.EmailField(max_length=25, unique=True)
    # Phone number of user with validation/
    phone_number = models.CharField(
        max_length=15, # Adjust the length of phone number digits.
        validatiors=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$', # regex for international phone numbers
                message = "Phone number must be entered in the format : +9999999999. Up to digits allowed."
            )
        ],
        unique=True
    )

class Order(models.Model):
    customer = 
    order_items =
    total_amount =
    order_status =