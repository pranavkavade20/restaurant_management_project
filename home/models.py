# home/models.py
from django.db import models
from multiselectfield import MultiSelectField


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
