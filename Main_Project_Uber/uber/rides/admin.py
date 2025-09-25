from django.contrib import admin
from .models import Ride ,RideFeedback

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    """Admin configuration for the Ride model."""

    # Fields to display in the list view
    list_display = (
        'id',
        'rider',
        'driver',
        'status',
        'payment_status',
        'fare',
        'requested_at',
        'completed_at',
        'paid_at',
    )

    # Fields that can be clicked to go to the edit page
    list_display_links = ('id', 'rider', 'driver')

    # Filters for the right sidebar
    list_filter = ('status', 'payment_status', 'payment_method', 'requested_at', 'completed_at')

    # Searchable fields
    search_fields = (
        'rider__user__username',
        'driver__user__username',
        'pickup_address',
        'dropoff_address',
    )

    # Ordering by default
    ordering = ('-requested_at',)

    # Read-only fields (timestamps should not be edited manually)
    readonly_fields = ('requested_at', 'completed_at', 'paid_at')

    # Field grouping in detail view
    fieldsets = (
        ('Ride Info', {
            'fields': ('rider', 'driver', 'status', 'fare', 'payment_status', 'payment_method')
        }),
        ('Addresses', {
            'fields': ('pickup_address', 'dropoff_address', ('pickup_lat', 'pickup_lng'), ('drop_lat', 'drop_lng'))
        }),
        ('Timestamps', {
            'fields': ('requested_at', 'completed_at', 'paid_at')
        }),
    )

    # Optional: enable autocomplete for foreign keys if you have many riders/drivers
    autocomplete_fields = ('rider', 'driver')


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
