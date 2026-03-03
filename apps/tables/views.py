from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, View

from apps.users.models import UserRole
from apps.users.permissions import RoleRequiredMixin

from .forms import RestaurantTableForm
from .models import RestaurantTable, TableStatus


class TableListView(LoginRequiredMixin, ListView):
    model = RestaurantTable
    template_name = "tables/table_list.html"
    context_object_name = "tables"
    paginate_by = 12

    def get_queryset(self):
        return RestaurantTable.objects.filter(is_active=True).order_by("name")


class TableCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = RestaurantTable
    form_class = RestaurantTableForm
    template_name = "tables/table_form.html"
    success_url = reverse_lazy("tables:table_list")
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def form_valid(self, form):
        messages.success(self.request, "Table created.")
        return super().form_valid(form)


class TableUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = RestaurantTable
    form_class = RestaurantTableForm
    template_name = "tables/table_form.html"
    success_url = reverse_lazy("tables:table_list")
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def form_valid(self, form):
        messages.success(self.request, "Table updated.")
        return super().form_valid(form)


class TableSetStatusView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_roles = (UserRole.ADMIN, UserRole.MANAGER, UserRole.WAITER)

    def post(self, request, pk: int):
        table = RestaurantTable.objects.get(pk=pk)
        status = request.POST.get("status")
        if status in TableStatus.values:
            table.status = status
            table.save(update_fields=["status"])
            messages.success(request, f"Table {table.name} set to {table.get_status_display()}.")
        return HttpResponseRedirect(reverse("tables:table_list"))
