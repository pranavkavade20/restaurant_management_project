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