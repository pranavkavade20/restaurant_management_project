from rest_framework import serializers
from .models import Ride

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
