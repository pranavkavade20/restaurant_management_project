from django.contrib import admin
from .models import Order,OrderStatus,Coupon

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

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """
    Admin config for managing coupons.
    """
    list_display = ("id", "code", "discount", "is_active", "valid_from", "valid_to")
    search_fields = ("code",)
    list_filter = ("is_active", "valid_from", "valid_to")
    ordering = ("-valid_from",)