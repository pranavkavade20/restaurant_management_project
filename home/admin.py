from django.contrib import admin
from .models import *

# Feedback model is registered.
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("id","created_at")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

# Contact model is registered.
admin.site.register(Contact)
# Address model is registered.
admin.site.register(Address)