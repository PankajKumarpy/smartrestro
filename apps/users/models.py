from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    MANAGER = "MANAGER", "Manager"
    WAITER = "WAITER", "Waiter"
    KITCHEN = "KITCHEN", "Kitchen Staff"
    CASHIER = "CASHIER", "Cashier"


class Restaurant(models.Model):
    """
    Simple restaurant profile.

    In a multi-tenant deployment each restaurant owner gets one Restaurant row.
    """

    name = models.CharField(max_length=150, unique=True)
    address = models.CharField(max_length=255, blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    """
    Custom user model with a 'role' and optional restaurant.

    - Restaurant owners are ADMINs linked as the primary owner in signup flow.
    - Other staff can be attached to the same restaurant from the admin panel.
    """

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.WAITER,
        db_index=True,
    )
    phone = models.CharField(max_length=20, blank=True, default="")
    restaurant = models.ForeignKey(
        Restaurant,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )

    class Meta:
        indexes = [
            models.Index(fields=["role", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.get_full_name() or self.username
