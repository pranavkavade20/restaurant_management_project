from django.db import models
from django.contrib.auth.models import User
from products.models import MenuItem
from django.conf import settings 
# Order model that store the orders.
class Order(models.Model):
    # Choices that show status realted to order_status.
    STATUS_CHOICES = [
        ('PENDING','Pending'),
        ('PROCESSING','Processing'),
        ('DELIVERED','Delivered'),
        ('CANCELLED','Cancelled'),
    ]

    # This field connected to User. 
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders') 
    # It store decimal field to store total price of menu.
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # It store status of order.
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    # It store the time at the created of Order.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Return username(customer) with id
        return f"Order #{self.id} by {self.customer.username}"

# OrderItem field related to Order for storing order item specifically.
class OrderItem(models.Model):
    # It store order items spcifically related to order model.
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    # This help to store menu specifically in OrderItem model. This connected to Item model which has menus.
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    # It store quantiy of items.
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        # Returns quantity of menu items.
        return f"{self.quantity} X {self.menu_item.name} (Order # {self.order.id})"
    
    def get_item_total(self): 
        # Returns total price of menu_item with help of quantity.
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
