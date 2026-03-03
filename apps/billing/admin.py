from django.contrib import admin

from .models import Invoice, Payment, TaxConfig


@admin.register(TaxConfig)
class TaxConfigAdmin(admin.ModelAdmin):
    list_display = ("gst_rate", "is_active", "updated_at")
    list_filter = ("is_active",)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_no", "order", "status", "total", "payment_mode", "paid_at", "created_at")
    list_filter = ("status", "payment_mode", "created_at")
    search_fields = ("invoice_no", "order__id")
    autocomplete_fields = ("order", "created_by")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice", "mode", "amount", "created_at")
    list_filter = ("mode", "created_at")
