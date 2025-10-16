from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta, time
from multiselectfield import MultiSelectField

from products.models import MenuItem
from .utils import is_restaurant_open  # Import your existing utility

# ------------------------
# Feedback Model
# ------------------------
class Feedback(models.Model):
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment[:40] or "Feedback"


# ------------------------
# Contact Model
# ------------------------
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


# ------------------------
# Address Model
# ------------------------
class Address(models.Model):
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}"


# ------------------------
# Restaurant Model
# ------------------------
class Restaurant(models.Model):
    name = models.CharField(max_length=200, help_text="Name of the restaurant")
    phone = models.CharField(max_length=15, help_text="Contact number")
    address = models.OneToOneField(
        Address,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="One-to-one mapping with Address"
    )

    opening_hours = models.JSONField(default=dict, blank=True)

    DAYS_OF_WEEK = (
        ("Mon", "Monday"),
        ("Tue", "Tuesday"),
        ("Wed", "Wednesday"),
        ("Thu", "Thursday"),
        ("Fri", "Friday"),
        ("Sat", "Saturday"),
        ("Sun", "Sunday"),
    )

    operating_days = MultiSelectField(
        choices=DAYS_OF_WEEK,
        max_length=20,
        blank=True,
        help_text="Days when the restaurant is open (e.g., Mon, Tue, Wed)"
    )
    def get_total_menu_items(self) -> int:
        """
        Returns the total number of menu items currently listed
        for this restaurant.

        Returns:
            int: The total count of menu items in the database.
        """
        total_items = MenuItem.objects.count()
        return total_items
    
    def __str__(self):
        return self.name


# ------------------------
# Menu Category Model
# ------------------------
class MenuCategory(models.Model):
    """
    Represents categories for the restaurant's menu 
    (e.g., Appetizers, Main Courses, Desserts).
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Category Name"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description"
    )

    class Meta:
        verbose_name = "Menu Category"
        verbose_name_plural = "Menu Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ------------------------
# Table Model (NEW)
# ------------------------
class Table(models.Model):
    """
    Represents a dining table in the restaurant.
    Used for reservation and availability tracking.
    """
    table_number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField(help_text="Number of people the table can seat")
    is_available = models.BooleanField(default=True, help_text="Whether the table is currently available")

    def __str__(self):
        return f"Table {self.table_number} (Seats {self.capacity})"


class UserReview(models.Model):
    """
    Stores user reviews for specific menu items.
    Each review is linked to a user and a menu item.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        help_text="The user who submitted this review"
    )

    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="reviews",
        help_text="The menu item being reviewed"
    )

    rating = models.PositiveSmallIntegerField(
        help_text="Rating given by the user (1–5)"
    )

    comment = models.TextField(
        blank=True,
        help_text="Optional text feedback provided by the user"
    )

    review_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the review was submitted"
    )

    class Meta:
        verbose_name = "User Review"
        verbose_name_plural = "User Reviews"
        ordering = ["-review_date"]
        indexes = [
            models.Index(fields=["menu_item"]),
            models.Index(fields=["user"]),
        ]
        unique_together = ("user", "menu_item")  # One review per user per item

    def __str__(self):
        return f"Review by {self.user.username} on {self.menu_item.name} ({self.rating}/5)"

class Reservation(models.Model):
    """
    Represents a restaurant table reservation.
    """
    customer_name = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    table_number = models.PositiveIntegerField()

    def __str__(self):
        return f"Reservation for {self.customer_name} on {self.date} (Table {self.table_number})"

    @classmethod
    def find_available_slots(cls, date, start_range, end_range, slot_duration_minutes=60):
        """
        Finds available reservation slots within a given date and time range.
        Uses the is_restaurant_open() utility to ensure slots are within operating hours.

        Args:
            date (datetime.date): The date to check for available reservations.
            start_range (datetime.time): Start of the desired time range.
            end_range (datetime.time): End of the desired time range.
            slot_duration_minutes (int): Duration of each reservation slot in minutes.

        Returns:
            list: A list of tuples (start_time, end_time) representing available slots.
        """

        # Check if restaurant is open before proceeding
        if not is_restaurant_open():
            return []

        # Fetch existing reservations for that date
        existing_reservations = cls.objects.filter(date=date).order_by("start_time")

        # Generate all possible slots within the provided range
        slots = []
        current_start = datetime.combine(date, start_range)
        end_datetime = datetime.combine(date, end_range)

        while current_start + timedelta(minutes=slot_duration_minutes) <= end_datetime:
            current_end = current_start + timedelta(minutes=slot_duration_minutes)

            # Check if this slot overlaps with any existing reservation
            overlap = existing_reservations.filter(
                start_time__lt=current_end.time(),
                end_time__gt=current_start.time()
            ).exists()

            if not overlap:
                slots.append((current_start.time(), current_end.time()))

            current_start = current_end

        return slots

class OpeningHour(models.Model):
    """
    Represents the restaurant's opening and closing hours for each day of the week.
    """
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK, unique=True)
    opening_time = models.TimeField(help_text="Opening time (HH:MM format)")
    closing_time = models.TimeField(help_text="Closing time (HH:MM format)")

    class Meta:
        verbose_name = "Opening Hour"
        verbose_name_plural = "Opening Hours"
        ordering = ['day']

    def __str__(self):
        return f"{self.day}: {self.opening_time} - {self.closing_time}"
