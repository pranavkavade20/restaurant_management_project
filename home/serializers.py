from rest_framework import serializers
from .models import MenuCategory, Contact,Table,UserReview,Restaurant
from products.models import MenuItem

class MenuCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for MenuCategory model.
    Includes name and optional description.
    """

    class Meta:
        model = MenuCategory
        fields = ["id", "name", "description"]


class MenuItemSerializer(serializers.ModelSerializer):
    """
    Serializer for MenuItem model (optional if already exists elsewhere).
    """
    category = MenuCategorySerializer(read_only=True)

    class Meta:
        model = MenuItem
        fields = ["id", "name", "description", "price", "image", "category", "created_at"]


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




class UserReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for UserReview model.
    Handles serialization and validation for user-submitted reviews.
    """

    user = serializers.StringRelatedField(read_only=True)  # show username instead of ID
    menu_item = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserReview
        fields = ["id", "user", "menu_item", "rating", "comment", "review_date"]

    def validate_rating(self, value):
        """Ensure the rating is between 1 and 5."""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

class RestaurantSerializer(serializers.ModelSerializer):
    """
    Serializer for Restaurant model to return detailed restaurant information.
    """
    class Meta:
        model = Restaurant
        fields = [
            'id',
            'name',
            'phone',
            'address',
            'opening_hours',
            'operating_days',
        ]
