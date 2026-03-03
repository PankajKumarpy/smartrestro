from __future__ import annotations

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView, View

from apps.inventory.services import InsufficientStockError, MissingRecipeError, validate_stock_for_order
from apps.tables.models import TableStatus
from apps.users.models import UserRole
from apps.users.permissions import RoleRequiredMixin

from .forms import OrderAddItemForm, OrderCreateForm
from .models import KitchenItemStatus, Order, OrderItem, OrderStatus


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"
    paginate_by = 15

    def get_queryset(self):
        qs = (
            Order.objects.select_related("table", "created_by")
            .prefetch_related("items__menu_item")
            .order_by("-created_at")
        )
        status = self.request.GET.get("status")
        if status in OrderStatus.values:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["order_status_choices"] = OrderStatus.choices
        return ctx


class OrderCreateView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = "orders/order_create.html"
    required_roles = (UserRole.ADMIN, UserRole.MANAGER, UserRole.WAITER)

    def get(self, request, *args, **kwargs):
        return self.render_to_response({"form": OrderCreateForm()})

    def post(self, request, *args, **kwargs):
        form = OrderCreateForm(request.POST)
        if not form.is_valid():
            return self.render_to_response({"form": form})
        order = form.save(commit=False)
        order.created_by = request.user
        order.save()

        # Mark table occupied as soon as an order starts.
        order.table.status = TableStatus.OCCUPIED
        order.table.save(update_fields=["status"])

        messages.success(request, f"Order #{order.pk} created. Add items now.")
        return HttpResponseRedirect(reverse("orders:order_detail", args=[order.pk]))


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.select_related("table", "created_by").prefetch_related("items__menu_item")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["add_item_form"] = OrderAddItemForm()
        return ctx


class OrderAddItemView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_roles = (UserRole.ADMIN, UserRole.MANAGER, UserRole.WAITER)

    def post(self, request, pk: int):
        order = get_object_or_404(Order, pk=pk)
        if order.status not in (OrderStatus.PENDING, OrderStatus.PREPARING):
            messages.error(request, "Cannot modify items for this order.")
            return HttpResponseRedirect(reverse("orders:order_detail", args=[order.pk]))

        form = OrderAddItemForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Please select a valid item and quantity.")
            return HttpResponseRedirect(reverse("orders:order_detail", args=[order.pk]))

        menu_item = form.cleaned_data["menu_item"]
        qty = int(form.cleaned_data["quantity"])

        with transaction.atomic():
            item, created = OrderItem.objects.select_for_update().get_or_create(
                order=order,
                menu_item=menu_item,
                defaults={"quantity": qty, "unit_price": menu_item.price},
            )
            if not created:
                item.quantity += qty
                item.unit_price = menu_item.price
                item.save(update_fields=["quantity", "unit_price"])

            order.recalc_totals()
            order.save(update_fields=["subtotal"])

        messages.success(request, f"Added {menu_item.name} x{qty}.")
        return HttpResponseRedirect(reverse("orders:order_detail", args=[order.pk]))


class OrderUpdateItemQtyView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_roles = (UserRole.ADMIN, UserRole.MANAGER, UserRole.WAITER)

    def post(self, request, pk: int, item_pk: int):
        order = get_object_or_404(Order, pk=pk)
        item = get_object_or_404(OrderItem, pk=item_pk, order=order)
        try:
            qty = int(request.POST.get("quantity", "1"))
        except ValueError:
            qty = 1
        qty = max(qty, 1)

        with transaction.atomic():
            item.quantity = qty
            item.save(update_fields=["quantity"])
            order.recalc_totals()
            order.save(update_fields=["subtotal"])

        messages.success(request, f"Updated {item.menu_item.name} quantity.")
        return HttpResponseRedirect(reverse("orders:order_detail", args=[order.pk]))


class OrderRemoveItemView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_roles = (UserRole.ADMIN, UserRole.MANAGER, UserRole.WAITER)

    def post(self, request, pk: int, item_pk: int):
        order = get_object_or_404(Order, pk=pk)
        item = get_object_or_404(OrderItem, pk=item_pk, order=order)
        with transaction.atomic():
            item.delete()
            order.recalc_totals()
            order.save(update_fields=["subtotal"])
        messages.success(request, "Item removed.")
        return HttpResponseRedirect(reverse("orders:order_detail", args=[order.pk]))


class OrderSendToKitchenView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_roles = (UserRole.ADMIN, UserRole.MANAGER, UserRole.WAITER)

    def post(self, request, pk: int):
        order = get_object_or_404(Order, pk=pk)
        if not order.items.exists():
            messages.error(request, "Add at least one item before sending to kitchen.")
            return HttpResponseRedirect(reverse("orders:order_detail", args=[order.pk]))

        try:
            validate_stock_for_order(order)
        except (InsufficientStockError, MissingRecipeError) as exc:
            messages.error(request, str(exc))
            return HttpResponseRedirect(reverse("orders:order_detail", args=[order.pk]))

        with transaction.atomic():
            order.ensure_kot_number()
            order.status = OrderStatus.PREPARING
            order.save(update_fields=["kot_number", "status"])

            order.items.filter(kitchen_status=KitchenItemStatus.PENDING).update(
                kitchen_status=KitchenItemStatus.PREPARING
            )

        messages.success(request, f"Sent to kitchen. KOT #{order.kot_number}.")
        return HttpResponseRedirect(reverse("orders:order_detail", args=[order.pk]))


class KitchenBoardView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    template_name = "orders/kitchen_board.html"
    context_object_name = "orders"
    paginate_by = 20
    required_roles = (UserRole.ADMIN, UserRole.MANAGER, UserRole.KITCHEN)

    def get_queryset(self):
        return (
            Order.objects.filter(status=OrderStatus.PREPARING)
            .select_related("table")
            .prefetch_related("items__menu_item")
            .order_by("created_at")
        )


class KitchenMarkItemReadyView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_roles = (UserRole.ADMIN, UserRole.MANAGER, UserRole.KITCHEN)

    def post(self, request, pk: int, item_pk: int):
        order = get_object_or_404(Order, pk=pk)
        item = get_object_or_404(OrderItem, pk=item_pk, order=order)
        with transaction.atomic():
            item.mark_ready()
            item.save(update_fields=["kitchen_status", "prepared_at"])

            if not order.items.exclude(kitchen_status=KitchenItemStatus.READY).exists():
                order.status = OrderStatus.SERVED
                order.save(update_fields=["status"])

        messages.success(request, f"Marked {item.menu_item.name} ready.")
        return HttpResponseRedirect(reverse("orders:kitchen_board"))


class OrderMarkCompletedView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_roles = (UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER)

    def post(self, request, pk: int):
        order = get_object_or_404(Order, pk=pk)
        if order.status != OrderStatus.SERVED:
            messages.error(request, "Only served orders can be billed and completed.")
            return HttpResponseRedirect(reverse("orders:order_detail", args=[order.pk]))

        messages.success(request, "Proceed to billing.")
        return HttpResponseRedirect(reverse("billing:invoice_create_for_order", args=[order.pk]))
