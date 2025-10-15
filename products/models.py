from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    """
    Represents a food or drink item available on the restaurant menu.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="menu_images/", blank=True, null=True)
    category = models.ForeignKey(
        "home.MenuCategory",
        on_delete=models.CASCADE,
        related_name="items"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # 🔹 New field for marking daily specials
    is_daily_special = models.BooleanField(
        default=False,
        help_text="Mark this item as a daily special"
    )

    # 🔹 New field for availability
    is_available = models.BooleanField(
        default=True,
        help_text="Indicates whether the menu item is currently available"
    )

    class Meta:
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} --> {self.price}"

