from django.db import models

# Feedback model
class Feedback(models.Model):
    # Save comment
    comment = models.TextField()
    # Save current time of comment.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # return first 40 characters on admin dashboard.
        return self.comment[:40] or "Feedback"

# Contact model for Home page.
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Restaurant Address model.
class Address(models.Model):
    address = models.CharField(max_length=255) # Street Address
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    # Kept as CharField to allow codes like "02115" or "12345-67890"
    zip_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now=True) # It save the time when last updated address.

    def __str__(self):
        return f"{self.address},{self.city}, {self.state} {self.zip_code}"