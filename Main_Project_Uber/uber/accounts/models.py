from django.db import models
from django.contrib.auth.models import User


class Rider(models.Model):
    """Model representing a Rider linked to Django's User."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="rider_profile")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    preferred_payment_method = models.CharField(max_length=50, blank=True, null=True)
    default_pickup_location = models.CharField(max_length=255, blank=True, null=True)
    profile_photo = models.ImageField(upload_to="rider_profiles/", blank=True, null=True)

    def __str__(self):
        return f"Rider: {self.user.username}"


class Driver(models.Model):
    """Model representing a Driver linked to Django's User."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="driver_profile")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    vehicle_make = models.CharField(max_length=50, blank=True, null=True)
    vehicle_model = models.CharField(max_length=50, blank=True, null=True)
    vehicle_number_plate = models.CharField(max_length=20, blank=True, null=True, unique=True)
    driver_license_number = models.CharField(max_length=30, blank=True, null=True, unique=True)
    availability_status = models.BooleanField(default=False)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    profile_photo = models.ImageField(upload_to="driver_profiles/", blank=True, null=True)

    def __str__(self):
        return f"Driver: {self.user.username} ({self.vehicle_number_plate})"
