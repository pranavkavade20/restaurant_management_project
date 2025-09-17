from rest_framework import serializers
from .models import MenuCategory
from products.models import MenuItem

class MenuCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for MenuCategory model.
    """
    class Meta:
        model = MenuCategory
        fields = ['id', 'name']  # expose id for frontend mapping

class MenuItemSerializer(serializers.ModelSerializer):
    """
    Serializer for MenuItem model.
    """
    category = serializers.StringRelatedField()
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = MenuItem
        fields = ["id", "name", "description", "price", "category", "image"]
