from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.orders.models import Order


class PaymentMode(models.TextChoices):
    CASH = "CASH", "Cash"
    UPI = "UPI", "UPI"
    CARD = "CARD", "Card"


class InvoiceStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    PAID = "PAID", "Paid"
    VOID = "VOID", "Void"


class TaxConfig(models.Model):
    """
    Simple single-row tax configuration (GST).
    """

    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("5.00"))
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"GST {self.gst_rate}%"

    @classmethod
    def current_gst_rate(cls) -> Decimal:
        obj = cls.objects.filter(is_active=True).order_by("-updated_at").first()
        return (obj.gst_rate if obj else Decimal("0.00"))


class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name="invoice")

    invoice_no = models.CharField(max_length=30, unique=True, db_index=True)
    status = models.CharField(max_length=10, choices=InvoiceStatus.choices, default=InvoiceStatus.DRAFT, db_index=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    payment_mode = models.CharField(max_length=10, choices=PaymentMode.choices, blank=True, default="")
    paid_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="invoices_created"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.invoice_no

    def recalc(self) -> None:
        self.subtotal = self.order.subtotal
        taxable = max(self.subtotal - (self.discount or Decimal("0.00")), Decimal("0.00"))
        self.gst_amount = (taxable * (self.gst_rate / Decimal("100.00"))).quantize(Decimal("0.01"))
        self.total = (taxable + self.gst_amount).quantize(Decimal("0.01"))

    @staticmethod
    def generate_invoice_no() -> str:
        today = timezone.localdate()
        prefix = today.strftime("INV%Y%m%d")
        last = (
            Invoice.objects.filter(invoice_no__startswith=prefix)
            .order_by("-invoice_no")
            .values_list("invoice_no", flat=True)
            .first()
        )
        seq = 1
        if last and "-" in last:
            try:
                seq = int(last.split("-")[-1]) + 1
            except ValueError:
                seq = 1
        return f"{prefix}-{seq:04d}"


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    mode = models.CharField(max_length=10, choices=PaymentMode.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=80, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.mode} {self.amount}"
