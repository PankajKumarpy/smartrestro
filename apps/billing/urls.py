from django.urls import path

from .views import (
    InvoiceCreateForOrderView,
    InvoiceDetailView,
    InvoiceListView,
    TaxConfigUpdateView,
)


app_name = "billing"

urlpatterns = [
    path("", InvoiceListView.as_view(), name="invoice_list"),
    path("invoice/<int:pk>/", InvoiceDetailView.as_view(), name="invoice_detail"),
    path("order/<int:order_pk>/invoice/", InvoiceCreateForOrderView.as_view(), name="invoice_create_for_order"),
    path("tax/", TaxConfigUpdateView.as_view(), name="tax_config"),
]

