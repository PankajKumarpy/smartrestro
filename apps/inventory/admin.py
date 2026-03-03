from django.contrib import admin

from .models import RawMaterial, Recipe, RecipeItem, StockMovement, Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "phone", "email")


@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "unit", "quantity_in_stock", "min_stock_level", "supplier", "is_active")
    list_filter = ("unit", "is_active")
    search_fields = ("name",)
    autocomplete_fields = ("supplier",)


class RecipeItemInline(admin.TabularInline):
    model = RecipeItem
    extra = 0
    autocomplete_fields = ("material",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("menu_item", "updated_at")
    inlines = [RecipeItemInline]
    autocomplete_fields = ("menu_item",)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("material", "movement_type", "quantity", "created_by", "created_at")
    list_filter = ("movement_type", "created_at")
    search_fields = ("material__name", "note")
    autocomplete_fields = ("material", "created_by")
