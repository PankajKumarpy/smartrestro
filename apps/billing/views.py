from __future__ import annotations

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, UpdateView, View

from apps.inventory.services import InsufficientStockError, MissingRecipeError
from apps.orders.models import Order
from apps.users.models import UserRole
from apps.users.permissions import RoleRequiredMixin

from .forms import InvoicePaymentForm, TaxConfigForm
from .models import Invoice, TaxConfig
from .services import create_or_get_invoice_for_order, mark_invoice_paid


class InvoiceListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Invoice
    template_name = "billing/invoice_list.html"
    context_object_name = "invoices"
    paginate_by = 15
    required_roles = (UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER)

    def get_queryset(self):
        return Invoice.objects.select_related("order", "order__table").order_by("-created_at")


class InvoiceDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    model = Invoice
    template_name = "billing/invoice_detail.html"
    context_object_name = "invoice"
    required_roles = (UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER)

    def get_queryset(self):
        return Invoice.objects.select_related("order", "order__table").prefetch_related("order__items__menu_item")


class InvoiceCreateForOrderView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_roles = (UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER)

    def get(self, request, order_pk: int):
        order = get_object_or_404(Order, pk=order_pk)
        invoice = create_or_get_invoice_for_order(order, created_by=request.user)
        form = InvoicePaymentForm(instance=invoice)
        return TemplateResponse(
            request,
            "billing/invoice_pay.html",
            {"order": order, "invoice": invoice, "form": form},
        )

    def post(self, request, order_pk: int):
        order = get_object_or_404(Order, pk=order_pk)
        invoice = create_or_get_invoice_for_order(order, created_by=request.user)
        form = InvoicePaymentForm(request.POST, instance=invoice)
        if not form.is_valid():
            return TemplateResponse(
                request, "billing/invoice_pay.html", {"order": order, "invoice": invoice, "form": form}
            )

        discount = form.cleaned_data.get("discount") or Decimal("0.00")
        mode = form.cleaned_data["payment_mode"]

        try:
            invoice = mark_invoice_paid(invoice, discount=discount, payment_mode=mode, paid_by=request.user)
        except (InsufficientStockError, MissingRecipeError) as exc:
            messages.error(request, str(exc))
            return TemplateResponse(
                request, "billing/invoice_pay.html", {"order": order, "invoice": invoice, "form": form}
            )

        messages.success(request, f"Payment recorded. Invoice {invoice.invoice_no} is paid.")
        return HttpResponseRedirect(reverse("billing:invoice_detail", args=[invoice.pk]))


class TaxConfigUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = TaxConfig
    form_class = TaxConfigForm
    template_name = "billing/tax_config_form.html"
    success_url = reverse_lazy("billing:invoice_list")
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def get_object(self, queryset=None):
        obj = TaxConfig.objects.order_by("-updated_at").first()
        if obj:
            return obj
        return TaxConfig.objects.create(gst_rate=Decimal("5.00"), is_active=True)

    def form_valid(self, form):
        messages.success(self.request, "GST settings updated.")
        return super().form_valid(form)
