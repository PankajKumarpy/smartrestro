from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.inventory.services import InsufficientStockError, MissingRecipeError, deduct_stock_for_order

from .models import Invoice, InvoiceStatus


@receiver(post_save, sender=Invoice)
def auto_deduct_stock_on_paid_invoice(sender, instance: Invoice, created: bool, **kwargs):
    """
    Safety net for academic requirement: when an invoice is marked PAID (even via admin),
    auto-deduct stock using recipes exactly once.
    """
    if instance.status != InvoiceStatus.PAID:
        return
    if instance.order.stock_deducted:
        return
    try:
        deduct_stock_for_order(instance.order, created_by=instance.created_by, note=f"Invoice {instance.invoice_no}")
    except (InsufficientStockError, MissingRecipeError):
        # Do not crash request/worker due to signal side-effect; main billing flow validates earlier.
        return

