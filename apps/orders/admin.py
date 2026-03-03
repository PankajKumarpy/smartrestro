from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ("menu_item",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "table", "status", "kot_number", "subtotal", "created_at")
    list_filter = ("status",)
    search_fields = ("id", "table__name")
    inlines = [OrderItemInline]

