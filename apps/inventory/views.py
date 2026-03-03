from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, View

from apps.users.models import UserRole
from apps.users.permissions import RoleRequiredMixin

from .forms import (
    RawMaterialForm,
    RecipeForm,
    RecipeItemFormSet,
    StockMovementForm,
    SupplierForm,
)
from .models import RawMaterial, Recipe, StockMovement, Supplier


class MaterialListView(LoginRequiredMixin, ListView):
    model = RawMaterial
    template_name = "inventory/material_list.html"
    context_object_name = "materials"
    paginate_by = 15

    def get_queryset(self):
        return RawMaterial.objects.select_related("supplier").order_by("name")


class MaterialCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = RawMaterial
    form_class = RawMaterialForm
    template_name = "inventory/material_form.html"
    success_url = reverse_lazy("inventory:material_list")
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def form_valid(self, form):
        messages.success(self.request, "Raw material created.")
        return super().form_valid(form)


class MaterialUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = RawMaterial
    form_class = RawMaterialForm
    template_name = "inventory/material_form.html"
    success_url = reverse_lazy("inventory:material_list")
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def form_valid(self, form):
        messages.success(self.request, "Raw material updated.")
        return super().form_valid(form)


class SupplierListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Supplier
    template_name = "inventory/supplier_list.html"
    context_object_name = "suppliers"
    paginate_by = 12
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)


class SupplierCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "inventory/supplier_form.html"
    success_url = reverse_lazy("inventory:supplier_list")
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def form_valid(self, form):
        messages.success(self.request, "Supplier created.")
        return super().form_valid(form)


class SupplierUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "inventory/supplier_form.html"
    success_url = reverse_lazy("inventory:supplier_list")
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def form_valid(self, form):
        messages.success(self.request, "Supplier updated.")
        return super().form_valid(form)


class StockMovementCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = StockMovement
    form_class = StockMovementForm
    template_name = "inventory/movement_form.html"
    success_url = reverse_lazy("inventory:material_list")
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def form_valid(self, form):
        movement = form.save(commit=False)
        movement.created_by = self.request.user
        movement.save()

        # Apply stock update
        material = movement.material
        if movement.movement_type == "IN":
            material.quantity_in_stock += movement.quantity
        else:
            material.quantity_in_stock -= movement.quantity
        material.save(update_fields=["quantity_in_stock"])

        messages.success(self.request, "Stock movement recorded.")
        return HttpResponseRedirect(self.get_success_url())


class RecipeListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Recipe
    template_name = "inventory/recipe_list.html"
    context_object_name = "recipes"
    paginate_by = 12
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def get_queryset(self):
        return Recipe.objects.select_related("menu_item").order_by("menu_item__name")


class RecipeCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "inventory/recipe_form.html"
    success_url = reverse_lazy("inventory:recipe_list")
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def form_valid(self, form):
        messages.success(self.request, "Recipe created. Add raw materials now.")
        resp = super().form_valid(form)
        return HttpResponseRedirect(reverse("inventory:recipe_edit", args=[self.object.pk]))


class RecipeEditView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_roles = (UserRole.ADMIN, UserRole.MANAGER)

    def get(self, request, pk: int):
        recipe = get_object_or_404(Recipe, pk=pk)
        form = RecipeForm(instance=recipe)
        formset = RecipeItemFormSet(instance=recipe)
        return self._render(recipe, form, formset)

    def post(self, request, pk: int):
        recipe = get_object_or_404(Recipe, pk=pk)
        form = RecipeForm(request.POST, instance=recipe)
        formset = RecipeItemFormSet(request.POST, instance=recipe)
        if not (form.is_valid() and formset.is_valid()):
            return self._render(recipe, form, formset)

        with transaction.atomic():
            form.save()
            formset.save()

        messages.success(request, "Recipe updated.")
        return HttpResponseRedirect(reverse("inventory:recipe_list"))

    def _render(self, recipe, form, formset):
        return TemplateResponse(
            self.request,
            "inventory/recipe_edit.html",
            {"recipe": recipe, "form": form, "formset": formset},
        )
