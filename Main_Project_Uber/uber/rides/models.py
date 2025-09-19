from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

# Explicit imports from accounts app
from accounts.models import Rider, Driver


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

    # Foreign keys to accounts app
    rider = models.ForeignKey(
        Rider,
        related_name="rides",
        on_delete=models.CASCADE,
        help_text="Rider who requested the ride.",
    )
    driver = models.ForeignKey(
        Driver,
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

    # Status of the ride
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.REQUESTED,
    )

    # Fare pricing
    fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Final fare after ride completion.",
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

class RideFeedback(models.Model):
    """
    Stores ratings and reviews for completed rides.
    Both rider and driver can leave feedback (one each).
    """
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name="feedbacks")
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ride_feedbacks"
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    is_driver = models.BooleanField(
        help_text="True if feedback left by driver, False if left by rider"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ride", "is_driver"],
                name="unique_feedback_per_user_type"
            )
        ]
        ordering = ["-submitted_at"]

    def __str__(self):
        role = "Driver" if self.is_driver else "Rider"
        return f"Feedback by {role} ({self.submitted_by.username}) for Ride {self.ride.id}"
