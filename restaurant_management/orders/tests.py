# orders/tests.py
from django.test import TestCase
from decimal import Decimal
from account.models import User
from products.models import MenuItem
from .models import Order, OrderItem, OrderStatus

# orders/tests.py

class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")

        # Prevent duplicate unique constraint error
        self.status, _ = OrderStatus.objects.get_or_create(name="Pending")

        self.menu_item1 = MenuItem.objects.create(name="Pizza", price=Decimal("200.00"))
        self.menu_item2 = MenuItem.objects.create(name="Burger", price=Decimal("100.00"))

        self.order = Order.objects.create(customer=self.user, order_status=self.status)

        OrderItem.objects.create(order=self.order, menu_item=self.menu_item1, quantity=2)
        OrderItem.objects.create(order=self.order, menu_item=self.menu_item2, quantity=3)
