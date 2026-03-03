from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.users.models import UserRole
from apps.users.permissions import RoleRequiredMixin

from .filters import MenuItemFilter
from .forms import CategoryForm, MenuItemForm
from .models import Category, MenuItem


class CategoryListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Category
    template_name = "menu/category_list.html"
    context_object_name = "categories"
    paginate_by = 10
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)


class CategoryCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "menu/category_form.html"
    success_url = reverse_lazy("menu:category_list")
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def form_valid(self, form):
        messages.success(self.request, "Category created.")
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "menu/category_form.html"
    success_url = reverse_lazy("menu:category_list")
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def form_valid(self, form):
        messages.success(self.request, "Category updated.")
        return super().form_valid(form)


class MenuItemListView(LoginRequiredMixin, ListView):
    model = MenuItem
    template_name = "menu/item_list.html"
    context_object_name = "items"
    paginate_by = 12

    def get_filter(self):
        return MenuItemFilter(self.request.GET, queryset=MenuItem.objects.select_related("category"))

    def get_queryset(self):
        return self.get_filter().qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter"] = self.get_filter()
        return ctx


class MenuItemCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = "menu/item_form.html"
    success_url = reverse_lazy("menu:item_list")
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def form_valid(self, form):
        messages.success(self.request, "Menu item created.")
        return super().form_valid(form)


class MenuItemUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = "menu/item_form.html"
    success_url = reverse_lazy("menu:item_list")
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def form_valid(self, form):
        messages.success(self.request, "Menu item updated.")
        return super().form_valid(form)


class MenuItemDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = MenuItem
    template_name = "menu/item_confirm_delete.html"
    success_url = reverse_lazy("menu:item_list")
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def form_valid(self, form):
        messages.success(self.request, "Menu item deleted.")
        return super().form_valid(form)
