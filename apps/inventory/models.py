from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.menu.models import MenuItem


class Unit(models.TextChoices):
    KG = "KG", "Kg"
    GM = "GM", "Gram"
    LTR = "LTR", "Liter"
    ML = "ML", "ML"
    PCS = "PCS", "Pieces"


class Supplier(models.Model):
    name = models.CharField(max_length=150, unique=True)
    phone = models.CharField(max_length=20, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    address = models.TextField(blank=True, default="")

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class RawMaterial(models.Model):
    name = models.CharField(max_length=150, unique=True)
    unit = models.CharField(max_length=10, choices=Unit.choices, default=Unit.PCS)

    quantity_in_stock = models.DecimalField(max_digits=14, decimal_places=3, default=Decimal("0.000"))
    min_stock_level = models.DecimalField(max_digits=14, decimal_places=3, default=Decimal("0.000"))

    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="materials")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_active", "name"]),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def is_low_stock(self) -> bool:
        return self.quantity_in_stock <= self.min_stock_level


class StockMovementType(models.TextChoices):
    IN = "IN", "Stock In"
    OUT = "OUT", "Stock Out"


class StockMovement(models.Model):
    material = models.ForeignKey(RawMaterial, on_delete=models.PROTECT, related_name="movements")
    movement_type = models.CharField(max_length=10, choices=StockMovementType.choices, db_index=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=3)
    note = models.CharField(max_length=250, blank=True, default="")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="stock_movements"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.material.name} {self.movement_type} {self.quantity}"


class Recipe(models.Model):
    """
    One recipe per menu item, with multiple raw-material lines.
    """

    menu_item = models.OneToOneField(MenuItem, on_delete=models.CASCADE, related_name="recipe")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Recipe for {self.menu_item.name}"


class RecipeItem(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="lines")
    material = models.ForeignKey(RawMaterial, on_delete=models.PROTECT, related_name="recipe_lines")
    quantity_required = models.DecimalField(max_digits=14, decimal_places=3)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["recipe", "material"], name="uniq_recipe_material"),
        ]

    def __str__(self) -> str:
        return f"{self.material.name} {self.quantity_required}{self.material.unit}"
