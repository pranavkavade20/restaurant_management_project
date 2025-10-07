from django.contrib import admin
from .models import Feedback, Contact, Address, Restaurant, MenuCategory, Table


# ------------------------
# Feedback Admin
# ------------------------
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """
    Admin configuration for Feedback model.
    """
    list_display = ("id", "short_comment", "created_at")
    search_fields = ("comment",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    def short_comment(self, obj):
        """Display a shortened comment in list view."""
        return obj.comment[:50] + ("..." if len(obj.comment) > 50 else "")
    short_comment.short_description = "Comment"


# ------------------------
# Contact Admin
# ------------------------
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Admin configuration for Contact model.
    """
    list_display = ("id", "name", "email", "submitted_at")
    search_fields = ("name", "email", "message")
    ordering = ("-submitted_at",)
    readonly_fields = ("submitted_at",)


# ------------------------
# Address Admin
# ------------------------
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """
    Admin configuration for Address model.
    """
    list_display = ("id", "address", "city", "state", "zip_code", "created_at")
    search_fields = ("address", "city", "state", "zip_code")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)


# ------------------------
# Restaurant Admin
# ------------------------
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    """
    Admin configuration for Restaurant model.
    """
    list_display = ("id", "name", "phone", "get_address")
    search_fields = ("name", "phone")
    list_filter = ("operating_days",)
    readonly_fields = ()
    
    def get_address(self, obj):
        """Show related address inline."""
        return obj.address or "No Address Assigned"
    get_address.short_description = "Address"


# ------------------------
# Menu Category Admin
# ------------------------
@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for MenuCategory model.
    """
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


# ------------------------
# Table Admin (NEW)
# ------------------------
@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    """
    Admin configuration for Table model.
    """
    list_display = ("id", "table_number", "capacity", "is_available")
    list_filter = ("is_available",)
    search_fields = ("table_number",)
    ordering = ("table_number",)
