from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order

from .models import RawMaterial, Recipe, RecipeItem, StockMovement, StockMovementType


class InsufficientStockError(Exception):
    pass


class MissingRecipeError(Exception):
    pass


def compute_required_materials_for_order(order: Order) -> dict[int, Decimal]:
    """
    Returns {RawMaterial.id: total_required_qty}.
    Raises MissingRecipeError if any ordered menu item has no recipe.
    """
    required: dict[int, Decimal] = defaultdict(lambda: Decimal("0.000"))
    items = order.items.select_related("menu_item").all()

    for it in items:
        try:
            recipe = it.menu_item.recipe
        except Recipe.DoesNotExist as exc:
            raise MissingRecipeError(f"Missing recipe for menu item: {it.menu_item.name}") from exc

        lines = recipe.lines.select_related("material").all()
        for line in lines:
            required[line.material_id] += (line.quantity_required * Decimal(it.quantity))

    return dict(required)


@transaction.atomic
def validate_stock_for_order(order: Order) -> None:
    """
    Validates that required raw materials exist and are sufficient *right now*.
    Does not change any stock.
    """
    required = compute_required_materials_for_order(order)
    if not required:
        return

    materials = (
        RawMaterial.objects.select_for_update()
        .filter(id__in=required.keys(), is_active=True)
        .in_bulk()
    )
    missing = [mid for mid in required.keys() if mid not in materials]
    if missing:
        raise InsufficientStockError("Some raw materials are missing/inactive.")

    for mid, qty_needed in required.items():
        if materials[mid].quantity_in_stock < qty_needed:
            raise InsufficientStockError(
                f"Insufficient stock for {materials[mid].name}. Needed {qty_needed}, available {materials[mid].quantity_in_stock}."
            )


@transaction.atomic
def deduct_stock_for_order(order: Order, *, created_by, note: str = "") -> None:
    """
    Deduct stock for an order exactly once.
    Creates StockMovement (OUT) rows and updates RawMaterial.quantity_in_stock.
    """
    order = Order.objects.select_for_update().get(pk=order.pk)
    if order.stock_deducted:
        return

    required = compute_required_materials_for_order(order)
    if not required:
        order.stock_deducted = True
        order.stock_deducted_at = timezone.now()
        order.save(update_fields=["stock_deducted", "stock_deducted_at"])
        return

    materials = (
        RawMaterial.objects.select_for_update()
        .filter(id__in=required.keys(), is_active=True)
        .in_bulk()
    )

    missing = [mid for mid in required.keys() if mid not in materials]
    if missing:
        raise InsufficientStockError("Some raw materials are missing/inactive.")

    # Validate stock sufficiency first
    for mid, qty_needed in required.items():
        if materials[mid].quantity_in_stock < qty_needed:
            raise InsufficientStockError(
                f"Insufficient stock for {materials[mid].name}. Needed {qty_needed}, available {materials[mid].quantity_in_stock}."
            )

    # Apply deduction + movements
    for mid, qty_needed in required.items():
        material = materials[mid]
        material.quantity_in_stock -= qty_needed
        material.save(update_fields=["quantity_in_stock"])
        StockMovement.objects.create(
            material=material,
            movement_type=StockMovementType.OUT,
            quantity=qty_needed,
            note=note or f"Auto-deduct for Order #{order.pk}",
            created_by=created_by,
        )

    order.stock_deducted = True
    order.stock_deducted_at = timezone.now()
    order.save(update_fields=["stock_deducted", "stock_deducted_at"])

