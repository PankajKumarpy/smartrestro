from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.views.generic import View

from apps.billing.models import Invoice, InvoiceStatus, PaymentMode
from apps.orders.models import OrderItem, OrderStatus
from apps.users.models import UserRole
from apps.users.permissions import RoleRequiredMixin

from .forms import ExpenseForm, ReportDateForm
from .models import Expense
from .pdf import render_daily_closing_pdf


class DailyClosingView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_roles = (UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER)

    def get_date(self, request):
        form = ReportDateForm(request.GET or None)
        if form.is_valid():
            return form.cleaned_data["date"], form
        return timezone.localdate(), ReportDateForm(initial={"date": timezone.localdate()})

    def get(self, request):
        date, date_form = self.get_date(request)
        ctx = self._build_context(date, date_form=date_form, expense_form=ExpenseForm(initial={"date": date}))
        return TemplateResponse(request, "reports/daily_closing.html", ctx)

    def post(self, request):
        date, date_form = self.get_date(request)
        expense_form = ExpenseForm(request.POST)
        if expense_form.is_valid():
            exp = expense_form.save(commit=False)
            exp.created_by = request.user
            exp.save()
            messages.success(request, "Expense recorded.")
            return redirect(f"{reverse('reports:daily_closing')}?date={date.isoformat()}")

        ctx = self._build_context(date, date_form=date_form, expense_form=expense_form)
        return TemplateResponse(request, "reports/daily_closing.html", ctx)

    def _build_context(self, date, *, date_form, expense_form):
        paid_invoices = Invoice.objects.filter(status=InvoiceStatus.PAID, paid_at__date=date)
        totals = paid_invoices.aggregate(total_sales=Sum("total"), total_orders=Count("id"))
        total_sales = totals["total_sales"] or Decimal("0.00")
        total_orders = totals["total_orders"] or 0

        breakdown = (
            paid_invoices.values("payment_mode")
            .annotate(amount=Sum("total"), count=Count("id"))
            .order_by("payment_mode")
        )

        expenses_qs = Expense.objects.filter(date=date).order_by("-created_at")
        total_expenses = expenses_qs.aggregate(s=Sum("amount"))["s"] or Decimal("0.00")

        net_profit = total_sales - total_expenses

        # Most sold item for the day (based on completed orders tied to paid invoices)
        order_ids = paid_invoices.values_list("order_id", flat=True)
        top_item = (
            OrderItem.objects.filter(order_id__in=order_ids)
            .values("menu_item__name")
            .annotate(qty=Sum("quantity"))
            .order_by("-qty")
            .first()
        )

        return {
            "date": date,
            "date_form": date_form,
            "expense_form": expense_form,
            "expenses": expenses_qs,
            "total_sales": total_sales,
            "total_orders": total_orders,
            "breakdown": breakdown,
            "total_expenses": total_expenses,
            "net_profit": net_profit,
            "top_item": top_item,
        }


class DailyClosingPdfView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_roles = (UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER)

    def get(self, request):
        date_str = request.GET.get("date")
        date = timezone.localdate()
        if date_str:
            try:
                date = datetime.fromisoformat(date_str).date()
            except ValueError:
                date = timezone.localdate()

        paid_invoices = Invoice.objects.filter(status=InvoiceStatus.PAID, paid_at__date=date)
        totals = paid_invoices.aggregate(total_sales=Sum("total"), total_orders=Count("id"))
        total_sales = totals["total_sales"] or Decimal("0.00")
        total_orders = totals["total_orders"] or 0

        expenses_qs = Expense.objects.filter(date=date)
        total_expenses = expenses_qs.aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
        net_profit = total_sales - total_expenses

        breakdown = paid_invoices.values("payment_mode").annotate(amount=Sum("total")).order_by("payment_mode")
        breakdown_lines = []
        for row in breakdown:
            mode = row["payment_mode"] or "-"
            breakdown_lines.append((f"Sales ({mode})", f"₹{row['amount'] or Decimal('0.00')}"))

        lines = [
            ("Total sales", f"₹{total_sales}"),
            ("Total paid invoices", str(total_orders)),
            ("Total expenses", f"₹{total_expenses}"),
            ("Net profit", f"₹{net_profit}"),
            *breakdown_lines,
        ]

        pdf_bytes = render_daily_closing_pdf(
            title="Daily Closing Report",
            date_str=date.strftime("%d %b %Y"),
            lines=lines,
        )

        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = f'attachment; filename="daily-closing-{date.isoformat()}.pdf"'
        return resp
