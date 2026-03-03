from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.inventory.services import InsufficientStockError, MissingRecipeError, deduct_stock_for_order
from apps.orders.models import Order, OrderStatus
from apps.tables.models import TableStatus

from .models import Invoice, InvoiceStatus, Payment, PaymentMode, TaxConfig


@transaction.atomic
def create_or_get_invoice_for_order(order: Order, *, created_by) -> Invoice:
    order = Order.objects.select_for_update().get(pk=order.pk)
    try:
        return order.invoice
    except Invoice.DoesNotExist:
        pass

    invoice = Invoice(
        order=order,
        invoice_no=Invoice.generate_invoice_no(),
        status=InvoiceStatus.DRAFT,
        gst_rate=TaxConfig.current_gst_rate(),
        created_by=created_by,
    )
    invoice.recalc()
    invoice.save()
    return invoice


@transaction.atomic
def mark_invoice_paid(invoice: Invoice, *, discount: Decimal, payment_mode: str, paid_by) -> Invoice:
    invoice = Invoice.objects.select_for_update().select_related("order").get(pk=invoice.pk)
    if invoice.status == InvoiceStatus.PAID:
        return invoice

    if payment_mode not in PaymentMode.values:
        raise ValueError("Invalid payment mode.")

    invoice.discount = discount or Decimal("0.00")
    invoice.gst_rate = TaxConfig.current_gst_rate()
    invoice.recalc()

    # Critical section: validate + deduct stock before confirming payment.
    deduct_stock_for_order(invoice.order, created_by=paid_by, note=f"Invoice {invoice.invoice_no}")

    invoice.status = InvoiceStatus.PAID
    invoice.payment_mode = payment_mode
    invoice.paid_at = timezone.now()
    invoice.save(
        update_fields=[
            "discount",
            "gst_rate",
            "gst_amount",
            "total",
            "status",
            "payment_mode",
            "paid_at",
        ]
    )

    Payment.objects.create(invoice=invoice, mode=payment_mode, amount=invoice.total)

    # Mark order completed after successful payment + stock deduction.
    invoice.order.status = OrderStatus.COMPLETED
    invoice.order.save(update_fields=["status"])

    invoice.order.table.status = TableStatus.AVAILABLE
    invoice.order.table.save(update_fields=["status"])

    return invoice

