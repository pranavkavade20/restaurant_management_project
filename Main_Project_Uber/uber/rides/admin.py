from django.contrib import admin
from .models import Ride ,RideFeedback

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    """Admin settings for Ride model for easier debugging and monitoring."""
    list_display = ("id", "rider", "driver", "status", "pickup_address", "dropoff_address", "requested_at")
    list_filter = ("status", "requested_at")
    search_fields = ("rider__user__username", "driver__user__username", "pickup_address", "dropoff_address")
    ordering = ("-requested_at",)

@admin.register(RideFeedback)
class RideFeedbackAdmin(admin.ModelAdmin):
    """
    Admin configuration for the RideFeedback model.
    Provides search, filtering, and display options
    for better feedback management in the admin panel.
    """

    list_display = (
        "id",
        "ride",
        "submitted_by",
        "role",
        "rating",
        "submitted_at",
    )
    list_filter = (
        "is_driver",
        "rating",
        "submitted_at",
    )
    search_fields = (
        "ride__id",
        "submitted_by__username",
        "comment",
    )
    readonly_fields = ("submitted_at",)

    def role(self, obj):
        """Custom column to display Rider/Driver instead of boolean."""
        return "Driver" if obj.is_driver else "Rider"
    role.short_description = "Submitted By (Role)"
