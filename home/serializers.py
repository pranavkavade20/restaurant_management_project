from rest_framework import serializers
from .models import MenuCategory,Contact,Table
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


class ContactSerializer(serializers.ModelSerializer):
    """
    Serializer for handling contact form submissions.
    Ensures proper validation and serialization of incoming data.
    """

    class Meta:
        model = Contact
        fields = ["id", "name", "email", "message", "submitted_at"]
        read_only_fields = ["id", "submitted_at"]

    def validate_name(self, value):
        """Ensure name is not empty or only whitespace."""
        if not value.strip():
            raise serializers.ValidationError("Name cannot be blank.")
        return value

    def validate_message(self, value):
        """Ensure message is not empty (if provided)."""
        if value and not value.strip():
            raise serializers.ValidationError("Message cannot be just whitespace.")
        return value

class TableSerializer(serializers.ModelSerializer):
    """
    Serializer for restaurant tables.
    Exposes basic table details for availability checks.
    """
    class Meta:
        model = Table
        fields = ["id", "table_number", "capacity", "is_available"]

class DailySpecialSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying menu items marked as daily specials.
    """
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = MenuItem
        fields = ["id", "name", "description", "price", "image", "category_name"]
