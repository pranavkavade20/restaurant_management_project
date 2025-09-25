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

    class PaymentStatus(models.TextChoices):
        PAID = "PAID", "Paid"
        UNPAID = "UNPAID", "Unpaid"

    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Cash"
        UPI = "UPI", "UPI"
        CARD = "CARD", "Card"

    # Foreign keys
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

    # Addresses
    pickup_address = models.CharField(max_length=255)
    dropoff_address = models.CharField(max_length=255)

    # Coordinates
    pickup_lat = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_lng = models.DecimalField(max_digits=9, decimal_places=6)
    drop_lat = models.DecimalField(max_digits=9, decimal_places=6)
    drop_lng = models.DecimalField(max_digits=9, decimal_places=6)

    # Status
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.REQUESTED,
    )
    completed_at = models.DateTimeField(
        null=True, blank=True, help_text="Timestamp when ride was completed."
    )

    # Fare
    fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Final fare after ride completion.",
    )

    # Payment tracking
    payment_status = models.CharField(
        max_length=8,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
        help_text="Tracks whether the ride is paid or unpaid.",
    )
    payment_method = models.CharField(
        max_length=8,
        choices=PaymentMethod.choices,
        null=True,
        blank=True,
        help_text="Method of payment (Cash, UPI, Card).",
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when payment was confirmed.",
    )

    requested_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["requested_at"]),
            models.Index(fields=["payment_status"]),
        ]

    def save(self, *args, **kwargs):
        # Fetch previous state from DB if it exists
        if self.pk:
            previous = Ride.objects.filter(pk=self.pk).first()
            if previous:
                # If status changed to COMPLETED and completed_at is not set
                if self.status == self.Status.COMPLETED and not previous.status == self.Status.COMPLETED:
                    self.completed_at = timezone.now()
                # If payment_status changed to PAID and paid_at is not set
                if self.payment_status == self.PaymentStatus.PAID and not previous.payment_status == self.PaymentStatus.PAID:
                    self.paid_at = timezone.now()
        else:
            # New ride instance: automatically set completed_at/paid_at if status/payment_status is already set
            if self.status == self.Status.COMPLETED:
                self.completed_at = timezone.now()
            if self.payment_status == self.PaymentStatus.PAID:
                self.paid_at = timezone.now()

        super().save(*args, **kwargs)

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
