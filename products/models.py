from django.db import models
from decimal import Decimal
from home.utils import calculate_discount  

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

    # 🔹 Field for marking daily specials
    is_daily_special = models.BooleanField(
        default=False,
        help_text="Mark this item as a daily special"
    )

    # 🔹 Field for availability
    is_available = models.BooleanField(
        default=True,
        help_text="Indicates whether the menu item is currently available"
    )

    # 🔹 New field for discount percentage
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Discount percentage for this item (e.g., 10 for 10%)"
    )

    class Meta:
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} --> {self.price}"

    # ✅ Method to calculate final price considering discount
    def get_final_price(self) -> Decimal:
        """
        Calculate the final price of the menu item after applying any discount.

        Returns:
            Decimal: The discounted price (if applicable).
        """
        # Ensure discount is within valid range
        if self.discount_percentage <= 0:
            return self.price

        # Use reusable utility function to calculate discount
        final_price = calculate_discount(
            float(self.price),
            float(self.discount_percentage)
        )

        # Return as Decimal to stay consistent with model field type
        return Decimal(final_price).quantize(Decimal("0.01"))


