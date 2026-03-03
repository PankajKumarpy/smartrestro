from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.menu.models import MenuItem
from apps.tables.models import RestaurantTable


class OrderStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PREPARING = "PREPARING", "Preparing"
    SERVED = "SERVED", "Served"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class KitchenItemStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PREPARING = "PREPARING", "Preparing"
    READY = "READY", "Ready"


class Order(models.Model):
    table = models.ForeignKey(RestaurantTable, on_delete=models.PROTECT, related_name="orders")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders_created"
    )

    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING, db_index=True
    )
    kot_number = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    notes = models.CharField(max_length=250, blank=True, default="")

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    stock_deducted = models.BooleanField(default=False, db_index=True)
    stock_deducted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Order #{self.pk} - {self.table.name}"

    def recalc_totals(self) -> None:
        subtotal = Decimal("0.00")
        for item in self.items.all():
            subtotal += item.line_total
        self.subtotal = subtotal

    def ensure_kot_number(self) -> None:
        if self.kot_number:
            return
        today = timezone.localdate()
        last = (
            Order.objects.filter(created_at__date=today, kot_number__isnull=False)
            .order_by("-kot_number")
            .values_list("kot_number", flat=True)
            .first()
        )
        self.kot_number = (last or 0) + 1


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT, related_name="order_items")

    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    kitchen_status = models.CharField(
        max_length=20,
        choices=KitchenItemStatus.choices,
        default=KitchenItemStatus.PENDING,
        db_index=True,
    )
    prepared_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["order", "menu_item"], name="uniq_order_item_menuitem"),
        ]

    def __str__(self) -> str:
        return f"{self.menu_item.name} x {self.quantity}"

    @property
    def line_total(self) -> Decimal:
        return (self.unit_price or Decimal("0.00")) * Decimal(self.quantity or 0)

    def mark_ready(self) -> None:
        self.kitchen_status = KitchenItemStatus.READY
        self.prepared_at = timezone.now()
