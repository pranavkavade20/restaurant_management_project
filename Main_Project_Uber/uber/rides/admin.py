from django.contrib import admin
from .models import Ride

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    """Admin settings for Ride model for easier debugging and monitoring."""
    list_display = ("id", "rider", "driver", "status", "pickup_address", "dropoff_address", "requested_at")
    list_filter = ("status", "requested_at")
    search_fields = ("rider__user__username", "driver__user__username", "pickup_address", "dropoff_address")
    ordering = ("-requested_at",)
