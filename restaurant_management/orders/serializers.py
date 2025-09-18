from rest_framework import serializers
from .models import Order, OrderItem

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
