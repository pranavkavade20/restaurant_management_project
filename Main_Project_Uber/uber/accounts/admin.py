from django.contrib import admin
from .models import Rider, Driver


@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    """Admin configuration for Rider model."""

    list_display = ("id", "user", "phone_number", "preferred_payment_method", "default_pickup_location")
    search_fields = ("user__username", "user__email", "phone_number")
    list_filter = ("preferred_payment_method",)
    ordering = ("id",)


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    """Admin configuration for Driver model."""

    list_display = (
        "id",
        "user",
        "phone_number",
        "vehicle_make",
        "vehicle_model",
        "vehicle_number_plate",
        "availability_status",
    )
    search_fields = (
        "user__username",
        "user__email",
        "phone_number",
        "vehicle_number_plate",
        "driver_license_number",
    )
    list_filter = ("availability_status", "vehicle_make")
    ordering = ("id",)
