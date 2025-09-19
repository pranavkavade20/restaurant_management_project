# Built in modules.
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from utils.geo_utils import calculate_distance

# Local modules.
from .models import Ride, RideFeedback

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

class LocationUpdateSerializer(serializers.Serializer):
    """
    Serializer for driver location updates.
    Expects latitude and longitude (floats) and optionally the ride_id for verification.
    """
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    ride_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        lat = attrs.get("latitude")
        lng = attrs.get("longitude")

        # basic bounds validation
        if not (-90.0 <= lat <= 90.0):
            raise serializers.ValidationError({"latitude": "Latitude must be between -90 and 90."})
        if not (-180.0 <= lng <= 180.0):
            raise serializers.ValidationError({"longitude": "Longitude must be between -180 and 180."})
        return attrs

class RideTrackSerializer(serializers.Serializer):
    """
    Minimal serializer returned to riders when tracking a ride.
    """
    driver_latitude = serializers.FloatField(allow_null=True)
    driver_longitude = serializers.FloatField(allow_null=True)
    status = serializers.CharField()
    driver_id = serializers.IntegerField(allow_null=True)
    updated_at = serializers.DateTimeField()

class RideHistorySerializer(serializers.ModelSerializer):
    """
    Serializer used for ride history responses.
    Keeps the payload minimal and front-end friendly.
    """
    pickup = serializers.CharField(source="pickup_address", read_only=True)
    drop = serializers.CharField(source="dropoff_address", read_only=True)
    driver = serializers.SerializerMethodField()
    rider = serializers.SerializerMethodField()

    class Meta:
        model = Ride
        fields = (
            "id",
            "pickup",
            "drop",
            "status",
            "requested_at",
            "driver",
            "rider",
        )
        read_only_fields = fields

    def get_driver(self, obj):
        """Return assigned driver's username or null."""
        driver = getattr(obj, "driver", None)
        if driver and getattr(driver, "user", None):
            return driver.user.username
        return None

    def get_rider(self, obj):
        """Return rider's username or null (useful for driver history)."""
        rider = getattr(obj, "rider", None)
        if rider and getattr(rider, "user", None):
            return rider.user.username
        return None

class RideFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideFeedback
        fields = ["id", "ride", "rating", "comment", "is_driver", "submitted_at"]
        read_only_fields = ["id", "is_driver", "submitted_at", "ride"]

    rating = serializers.IntegerField(min_value=1, max_value=5)

    def validate(self, attrs):
        request = self.context.get("request")
        ride = self.context.get("ride")  # Passed from view
        user = request.user if request else None

        if ride is None:
            raise ValidationError(_("Ride is required."))

        # 1. Ride must be completed
        if ride.status != Ride.Status.COMPLETED:
            raise ValidationError(_("Ride is not completed yet."))

        # 2. User must be part of the ride
        is_driver = hasattr(user, "driver") or hasattr(user, "driver_profile")
        is_rider = hasattr(user, "rider") or hasattr(user, "rider_profile")

        if is_driver and ride.driver and ride.driver.user == user:
            role = True
        elif is_rider and ride.rider and ride.rider.user == user:
            role = False
        else:
            raise PermissionDenied(_("You are not part of this ride."))

        # 3. Feedback must not already exist
        if RideFeedback.objects.filter(ride=ride, is_driver=role).exists():
            raise ValidationError(_("Feedback already submitted."))

        # Save role in serializer context
        attrs["is_driver"] = role
        attrs["ride"] = ride
        attrs["submitted_by"] = user
        return attrs

    def create(self, validated_data):
        return RideFeedback.objects.create(**validated_data)

class FareCalculationSerializer(serializers.ModelSerializer):
    """
    Serializer to calculate and save fare for completed rides.
    """

    class Meta:
        model = Ride
        fields = ["id", "status", "fare", "pickup_lat", "pickup_lng", "drop_lat", "drop_lng"]

    def validate(self, attrs):
        ride = self.instance

        if ride.status != Ride.Status.COMPLETED:
            raise serializers.ValidationError("Fare can only be calculated for COMPLETED rides.")

        if ride.fare is not None:
            raise serializers.ValidationError("Fare has already been calculated for this ride.")

        return attrs

    def update(self, instance, validated_data):
        base_fare = Decimal("50.00")
        per_km_rate = Decimal("10.00")
        surge_multiplier = Decimal("1.0")  # make dynamic later

        distance_km = Decimal(
            calculate_distance(
                instance.pickup_lat, instance.pickup_lng,
                instance.drop_lat, instance.drop_lng
            )
        )

        fare = base_fare + (distance_km * per_km_rate * surge_multiplier)

        instance.fare = round(fare, 2)
        instance.save(update_fields=["fare"])
        return instance
