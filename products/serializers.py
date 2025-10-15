from rest_framework import serializers
from .models import MenuItem,Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
        
class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'

class MenuItemAvailabilitySerializer(serializers.ModelSerializer):
    """
    Serializer for updating the availability status of a menu item.
    """
    class Meta:
        model = MenuItem
        fields = ["id", "name", "is_available"]
