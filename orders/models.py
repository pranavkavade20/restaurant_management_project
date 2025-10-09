from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from products.models import MenuItem
from .utils import generate_unique_order_id


class OrderStatus(models.Model):
    """
    Represents different statuses of an order 
    (e.g., Pending, Processing, Delivered, Cancelled).
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Order Status"
    )

    class Meta:
        verbose_name = "Order Status"
        verbose_name_plural = "Order Statuses"
        ordering = ["id"]

    def __str__(self):
        return self.name


# ✅ Custom QuerySet for chaining and efficient querying
class OrderQuerySet(models.QuerySet):
    def by_status(self, status_name: str):
        """Filter orders by a given status name (case-insensitive)."""
        return self.filter(order_status__iexact=status_name)

    def pending(self):
        """Return all pending orders."""
        return self.by_status("Pending")

    def processing(self):
        """Return all processing orders."""
        return self.by_status("Processing")

    def delivered(self):
        """Return all delivered orders."""
        return self.by_status("Delivered")

    def cancelled(self):
        """Return all cancelled orders."""
        return self.by_status("Cancelled")

    def active(self):
        """Return active orders (Pending or Processing)."""
        return self.filter(order_status__in=["Pending", "Processing"])


# ✅ Custom Manager using OrderQuerySet
class OrderManager(models.Manager):
    """
    Custom manager for the Order model providing
    status-based and active order retrieval.
    """
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def get_by_status(self, status_name: str):
        """Retrieve all orders by a specific status."""
        return self.get_queryset().by_status(status_name)

    def get_pending_orders(self):
        """Shortcut for pending orders."""
        return self.get_queryset().pending()

    def get_processing_orders(self):
        """Shortcut for processing orders."""
        return self.get_queryset().processing()

    def get_delivered_orders(self):
        """Shortcut for delivered orders."""
        return self.get_queryset().delivered()

    def get_cancelled_orders(self):
        """Shortcut for cancelled orders."""
        return self.get_queryset().cancelled()

    def get_active_orders(self):
        """Shortcut for active (Pending or Processing) orders."""
        return self.get_queryset().active()


class Order(models.Model):
    """
    Stores a single order placed by a customer.
    Links to `User` for customer, and tracks status via OrderStatus.
    """
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    custom_order_id = models.CharField(
        max_length=12,
        unique=True,
        editable=False,
        null=True,
        help_text="Unique alphanumeric ID for the order"
    )

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        help_text="The customer who placed the order"
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total amount for this order"
    )

    order_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending",
        help_text="Current status of the order"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ Attach the new custom manager here
    objects = OrderManager()

    def __str__(self):
        return f"Order #{self.custom_order_id or self.id} by {self.customer.username}"

    def calculate_total(self) -> Decimal:
        """
        Calculates total only if the order has a primary key.
        Avoids querying reverse FK on unsaved objects.
        """
        if not self.pk:
            return Decimal("0.00")
        total = sum((item.item_total for item in self.order_items.all()), Decimal("0.00"))
        self.total_amount = total
        return total

    def save(self, *args, **kwargs):
        # Assign a unique order ID if missing
        if not self.custom_order_id:
            self.custom_order_id = generate_unique_order_id()

        # Save the order first to ensure PK exists for reverse FK
        super().save(*args, **kwargs)

        # Recalculate total if there are order items
        total = self.calculate_total()
        if total != self.total_amount:
            Order.objects.filter(pk=self.pk).update(total_amount=total)


class OrderItem(models.Model):
    """
    Represents an item within a specific Order.
    Links to a MenuItem and tracks quantity ordered.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_items",
        help_text="The order this item belongs to"
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        help_text="The menu item included in this order"
    )
    quantity = models.PositiveIntegerField(default=1, help_text="Quantity of this menu item")

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} (Order #{self.order.id})"

    @property
    def item_total(self):
        """Return total price for this menu item."""
        return self.menu_item.price * self.quantity


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart of {self.user}"

    @property
    def total_items(self):
        return sum(i.quantity for i in self.items.all())

    @property
    def total_price(self):
        return sum(i.menu_item.price * i.quantity for i in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.menu_item.name} ({self.quantity})"

    @property
    def subtotal(self):
        return self.menu_item.price * self.quantity


class Coupon(models.Model):
    """
    Represents discount coupons used in orders.
    """
    code = models.CharField(
        max_length=15,
        unique=True,
        db_index=True,
        verbose_name="Coupon Code"
    )
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Discount value in percentage (e.g., 10.00 for 10%)"
    )
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        ordering = ["-valid_from"]

    def __str__(self):
        return f"{self.code} ({self.discount}% off)"
