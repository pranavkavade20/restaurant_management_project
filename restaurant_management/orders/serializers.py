from rest_framework import serializers
from .models import Order, OrderItem,OrderStatus
from products.models import MenuItem

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "name", "image", "price"]

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["menu_item_name", "quantity", "item_total"]

    def get_item_total(self, obj):
        return obj.get_item_total()

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.username", read_only=True)
    order_status = serializers.CharField(source="order_status.name", read_only=True)

    class Meta:
        model = Order
        fields = ["id", "customer_name", "total_amount", "order_status", "created_at", "order_items"]

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ["id", "name"]

class OrderDetailSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    customer = serializers.StringRelatedField(read_only=True)
    order_status = OrderStatusSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "customer", "total_amount", "order_status", "created_at", "order_items"]
