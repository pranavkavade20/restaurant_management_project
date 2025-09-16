from django.contrib import admin
from .models import Order,OrderStatus

# Register the order model
admin.site.register(Order)

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    """
    Admin configuration for OrderStatus model.
    """
    list_display = ("id", "name")   # Show ID and status name
    search_fields = ("name",)       # Enable search by status name
    ordering = ("id",)              # Keep order of creation
