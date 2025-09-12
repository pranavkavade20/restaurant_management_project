from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import Rider, Driver ,Ride

class UserSerializer(serializers.ModelSerializer):
    """Base serializer for Django User."""

    class Meta:
        model = User
        fields = ("id", "username", "email")

class RiderRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for registering Riders."""

    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Rider
        fields = (
            "username",
            "email",
            "password",
            "phone_number",
            "preferred_payment_method",
            "default_pickup_location",
        )

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def create(self, validated_data):
        username = validated_data.pop("username")
        email = validated_data.pop("email")
        password = validated_data.pop("password")

        user = User.objects.create_user(username=username, email=email, password=password)
        rider = Rider.objects.create(user=user, **validated_data)
        return rider

class DriverRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for registering Drivers."""

    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Driver
        fields = (
            "username",
            "email",
            "password",
            "phone_number",
            "vehicle_make",
            "vehicle_model",
            "vehicle_number_plate",
            "driver_license_number",
        )

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def create(self, validated_data):
        username = validated_data.pop("username")
        email = validated_data.pop("email")
        password = validated_data.pop("password")

        user = User.objects.create_user(username=username, email=email, password=password)
        driver = Driver.objects.create(user=user, **validated_data)
        return driver

class RideRequestSerializer(serializers.ModelSerializer):
    """
    Serializer used by riders to request a new ride.
    The rider and timestamps are set server-side.
    """

    class Meta:
        model = Ride
        read_only_fields = ("id", "status", "requested_at", "updated_at", "driver", "rider")
        fields = (
            "id",
            "pickup_address",
            "dropoff_address",
            "pickup_lat",
            "pickup_lng",
            "drop_lat",
            "drop_lng",
            "status",
            "requested_at",
            "updated_at",
        )

    def validate(self, attrs):
        """
        Basic validation: coordinates must be provided and not identical.
        Extend this as needed (range checks, geospatial validation, etc.).
        """
        if (
            attrs.get("pickup_lat") == attrs.get("drop_lat")
            and attrs.get("pickup_lng") == attrs.get("drop_lng")
        ):
            raise serializers.ValidationError("Pickup and drop coordinates cannot be identical.")
        return attrs

class RiderLoginSerializer(TokenObtainPairSerializer):
    """
    Custom JWT login serializer for Riders.
    Ensures the authenticated user has a Rider profile.
    """

    def validate(self, attrs):
        data = super().validate(attrs)

        if not hasattr(self.user, "rider_profile"):
            raise serializers.ValidationError("This account is not registered as a Rider.")

        # Optional: add rider info into response
        data.update({
            "user_id": self.user.id,
            "username": self.user.username,
            "role": "rider"
        })
        return data

class DriverLoginSerializer(TokenObtainPairSerializer):
    """
    Custom JWT login serializer for Drivers.
    Ensures the authenticated user has a Driver profile.
    """

    def validate(self, attrs):
        data = super().validate(attrs)

        if not hasattr(self.user, "driver_profile"):
            raise serializers.ValidationError("This account is not registered as a Driver.")

        # Optional: add driver info into response
        data.update({
            "user_id": self.user.id,
            "username": self.user.username,
            "role": "driver"
        })
        return data

class LogoutSerializer(serializers.Serializer):
    """
    Serializer for logging out users by blacklisting their refresh token.
    """
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            raise serializers.ValidationError("Invalid or expired refresh token.")

class RideSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying Ride instances (for drivers and riders).
    Includes nested user info for clarity.
    """

    rider_username = serializers.SerializerMethodField()
    driver_username = serializers.SerializerMethodField()

    class Meta:
        model = Ride
        fields = (
            "id",
            "rider",
            "rider_username",
            "driver",
            "driver_username",
            "pickup_address",
            "dropoff_address",
            "pickup_lat",
            "pickup_lng",
            "drop_lat",
            "drop_lng",
            "status",
            "requested_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_rider_username(self, obj):
        return obj.rider.user.username if obj.rider and obj.rider.user else None

    def get_driver_username(self, obj):
        return obj.driver.user.username if obj.driver and obj.driver.user else None
