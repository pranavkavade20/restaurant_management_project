from django.db import models

# Menu model
class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="menu_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # only uploads

    def __str__(self):
        return f"{self.name} --> {self.price}"


    