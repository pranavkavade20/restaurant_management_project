from django.contrib import admin
from .models import *

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

admin.site.register(Contact)
admin.site.register(Address)
admin.site.register(Restaurant)