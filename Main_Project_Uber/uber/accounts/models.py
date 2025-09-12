from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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

class Ride(models.Model):
    """
    Represents a ride request in the system.
    A Ride is created by a Rider and may later be assigned to a Driver.
    """

    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        ONGOING = "ONGOING", "Ongoing"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    rider = models.ForeignKey(
        "Rider",
        related_name="rides",
        on_delete=models.CASCADE,
        help_text="Rider who requested the ride.",
    )
    driver = models.ForeignKey(
        "Driver",
        related_name="rides",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Driver assigned to this ride (null until accepted).",
    )

    # Addresses (user-friendly)
    pickup_address = models.CharField(max_length=255)
    dropoff_address = models.CharField(max_length=255)

    # Coordinates
    pickup_lat = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_lng = models.DecimalField(max_digits=9, decimal_places=6)
    drop_lat = models.DecimalField(max_digits=9, decimal_places=6)
    drop_lng = models.DecimalField(max_digits=9, decimal_places=6)

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.REQUESTED,
    )

    requested_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["requested_at"]),
        ]

    def __str__(self):
        return f"Ride({self.pk}) {self.status} - Rider:{self.rider.user.username}"