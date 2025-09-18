from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# User Profile model for saving information of authenticated users.

class UserProfile(models.Model):
    """
    Extends the built-in User model to store additional user information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: +9999999999. Up to 15 digits allowed."
            )
        ]
    )

    def __str__(self):
        return self.user.username

