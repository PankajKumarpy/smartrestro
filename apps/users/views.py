from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, RedirectView, TemplateView, UpdateView, FormView

from .forms import RestaurantSignupForm, StaffCreateForm, StaffUpdateForm
from .models import Restaurant, User, UserRole
from .permissions import RoleRequiredMixin


class HomeRedirectView(RedirectView):
    pattern_name = "dashboard"

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return super().get_redirect_url(*args, **kwargs)
        return reverse_lazy("login")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "users/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["role"] = getattr(self.request.user, "role", None)
        ctx["restaurant"] = getattr(self.request.user, "restaurant", None)
        # Lightweight analytics widgets (no extra JS libs)
        try:
            from datetime import timedelta
            from decimal import Decimal

            from django.db.models import F, Sum
            from django.utils import timezone

            from apps.billing.models import Invoice, InvoiceStatus
            from apps.inventory.models import RawMaterial
            from apps.orders.models import Order, OrderStatus

            today = timezone.localdate()
            ctx["today_sales"] = (
                Invoice.objects.filter(status=InvoiceStatus.PAID, paid_at__date=today).aggregate(s=Sum("total"))["s"]
                or Decimal("0.00")
            )
            ctx["active_orders"] = Order.objects.filter(
                status__in=[OrderStatus.PENDING, OrderStatus.PREPARING, OrderStatus.SERVED]
            ).count()
            ctx["low_stock_count"] = RawMaterial.objects.filter(
                is_active=True, quantity_in_stock__lte=F("min_stock_level")
            ).count()

            # Sales chart (last 7 days) for manager/admin/cashier dashboards
            if self.request.user.is_superuser or ctx["role"] in {UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER}:
                import json
                days = [today - timedelta(days=i) for i in range(6, -1, -1)]
                sales_map = {
                    row["paid_at__date"]: (row["s"] or Decimal("0.00"))
                    for row in (
                        Invoice.objects.filter(status=InvoiceStatus.PAID, paid_at__date__in=days)
                        .values("paid_at__date")
                        .annotate(s=Sum("total"))
                    )
                }
                ctx["sales_chart_labels"] = json.dumps([d.strftime("%d %b") for d in days])
                ctx["sales_chart_values"] = json.dumps([float(sales_map.get(d, Decimal("0.00"))) for d in days])
        except Exception:
            ctx["today_sales"] = None
            ctx["active_orders"] = None
            ctx["low_stock_count"] = None
            ctx["sales_chart_labels"] = []
            ctx["sales_chart_values"] = []
        return ctx


class RestaurantSignupView(FormView):
    """
    Public signup: create Restaurant + owner (ADMIN) and log in.
    """

    template_name = "users/signup.html"
    form_class = RestaurantSignupForm
    success_url = reverse_lazy("dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return RedirectView.as_view(pattern_name="dashboard")(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    @transaction.atomic
    def form_valid(self, form):
        user = form.create_restaurant_and_owner()
        login(self.request, user)
        messages.success(self.request, "Restaurant account created. Welcome to Smart RMS!")
        return super().form_valid(form)


class StaffListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = User
    template_name = "users/staff_list.html"
    context_object_name = "staff_list"
    paginate_by = 10
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def get_queryset(self):
        return (
            User.objects.filter(is_superuser=False)
            .order_by("role", "username")
        )


class StaffCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = User
    form_class = StaffCreateForm
    template_name = "users/staff_form.html"
    success_url = reverse_lazy("users:staff_list")
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def form_valid(self, form):
        messages.success(self.request, "Staff account created successfully.")
        return super().form_valid(form)


class StaffUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = User
    form_class = StaffUpdateForm
    template_name = "users/staff_form.html"
    success_url = reverse_lazy("users:staff_list")
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def form_valid(self, form):
        messages.success(self.request, "Staff account updated successfully.")
        return super().form_valid(form)
