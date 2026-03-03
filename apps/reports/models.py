from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models


class Expense(models.Model):
    date = models.DateField(db_index=True)
    title = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    note = models.CharField(max_length=250, blank=True, default="")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="expenses_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.date})"
