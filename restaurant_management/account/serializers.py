from django.contrib.auth.models import User
from rest_framework import serializers


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information.
    Only exposes editable fields.
    """
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        extra_kwargs = {
            "email": {"required": True},
        }

    def validate_email(self, value):
        """
        Ensure email is unique across users.
        """
        user = self.context["request"].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value
