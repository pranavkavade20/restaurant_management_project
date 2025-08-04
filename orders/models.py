from django.db import models
from django.core.validatiors import RegexValidator
from django.contrib.auth.models import User

# Menu model create for store menu.
class Menu(modes.Model):
    # Store Menu Item.
    name = models.CharField(max_length=150)
    # Store Price.
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str_(self):
        return self.name

# Order model that store the orders.
class Order(models.Model):
    # Choices that show status realted to order_status.
    STATUS_CHOICES =[
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
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')

    # This help to store menu specifically in OrderItem model. This connected to menu model which has menus.
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE)

    # It store quantiy of items.
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        # Returns quantity of menu items.
        return f"{self.quantity} X {self.menu_item.name}"
    
    def get_item_total(self):
        # Returns total price of menu_item with help of quantity.

        return self.menu_item.price * self.quantity

