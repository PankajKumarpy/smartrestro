from django.contrib import admin

from .models import RestaurantTable


@admin.register(RestaurantTable)
class RestaurantTableAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity", "status", "is_active")
    list_filter = ("status", "is_active")
    search_fields = ("name",)
