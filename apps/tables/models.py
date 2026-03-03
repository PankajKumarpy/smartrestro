from django.db import models


class TableStatus(models.TextChoices):
    AVAILABLE = "AVAILABLE", "Available"
    OCCUPIED = "OCCUPIED", "Occupied"
    RESERVED = "RESERVED", "Reserved"


class RestaurantTable(models.Model):
    name = models.CharField(max_length=30, unique=True, help_text="e.g. T1, Table 5")
    capacity = models.PositiveIntegerField(default=4)
    status = models.CharField(
        max_length=20,
        choices=TableStatus.choices,
        default=TableStatus.AVAILABLE,
        db_index=True,
    )
    is_active = models.BooleanField(default=True)
    notes = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
