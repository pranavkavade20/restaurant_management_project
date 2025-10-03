from django.db import models
from multiselectfield import MultiSelectField
# Feedback model
class Feedback(models.Model):
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Show first 40 chars in admin/listing
        return self.comment[:40] or "Feedback"

# Contact us model for user.
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

# Restaurant Address
class Address(models.Model):
    address = models.CharField(max_length=255)   # Street address
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)   
    # Kept as CharField to allow codes like "02115" or "12345-6789"
    created_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}"

# Restaurant model

class Restaurant(models.Model):
    # ------------------------
    # Basic restaurant details
    # ------------------------
    name = models.CharField(max_length=200, help_text="Name of the restaurant")
    phone = models.CharField(max_length=15, help_text="Contact number")
    address = models.OneToOneField(
        Address,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="One-to-one mapping with Address"
    )

    # ------------------------
    # Opening hours per day
    # Example: {"Monday": "9 AM - 10 PM", "Tuesday": "Closed"}
    # ------------------------
    opening_hours = models.JSONField(default=dict, blank=True)

    # ------------------------
    # Operating days (business days)
    # ------------------------
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


# MenuCategoru model
class MenuCategory(models.Model):
    """
    Represents categories for the restaurant's menu 
    (e.g., Appetizers, Main Courses, Desserts).
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,  # Improves lookup performance
        verbose_name="Category Name"
    )

    class Meta:
        verbose_name = "Menu Category"
        verbose_name_plural = "Menu Categories"
        ordering = ["name"]  # Sort categories alphabetically

    def __str__(self):
        return self.name
