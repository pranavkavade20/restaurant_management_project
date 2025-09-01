from django.db import models

# Feedback model
class Feedback(models.Model):
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Show first 40 chars in admin/listing
        return self.comment[:40] or "Feedback"

# Contact us model
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
