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
    class Meta:
        model = Order
        fields = ["id", "customer", "total_amount", "order_status", "created_at"]
        read_only_fields = ["id", "customer", "total_amount", "created_at"]


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
        
class OrderStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating the status of an order.
    """
    order_id = serializers.IntegerField()
    new_status = serializers.CharField(max_length=20)

    def validate(self, data):
        # Check if the order exists
        try:
            order = Order.objects.get(pk=data["order_id"])
        except Order.DoesNotExist:
            raise serializers.ValidationError({"order_id": "Invalid order ID."})

        # Validate new status
        valid_statuses = Order.valid_statuses()
        if data["new_status"] not in valid_statuses:
            raise serializers.ValidationError({
                "new_status": f"Invalid status. Allowed values: {', '.join(valid_statuses)}"
            })

        data["order"] = order
        return data