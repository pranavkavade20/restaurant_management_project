from django.db import models
from django.utils import timezone

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
