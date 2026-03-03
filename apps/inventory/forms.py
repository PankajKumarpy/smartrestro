from __future__ import annotations

from django import forms
from django.forms import inlineformset_factory

from apps.menu.models import MenuItem

from .models import RawMaterial, Recipe, RecipeItem, StockMovement, Supplier


def _apply_bootstrap(form: forms.Form) -> None:
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs.setdefault("class", "form-check-input")
        elif isinstance(widget, forms.Select):
            widget.attrs.setdefault("class", "form-select")
        else:
            widget.attrs.setdefault("class", "form-control")


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ("name", "phone", "email", "address", "is_active")
        widgets = {"address": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_bootstrap(self)


class RawMaterialForm(forms.ModelForm):
    class Meta:
        model = RawMaterial
        fields = ("name", "unit", "quantity_in_stock", "min_stock_level", "supplier", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_bootstrap(self)


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ("material", "movement_type", "quantity", "note")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_bootstrap(self)


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ("menu_item",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["menu_item"].queryset = MenuItem.objects.order_by("name")
        _apply_bootstrap(self)


RecipeItemFormSet = inlineformset_factory(
    Recipe,
    RecipeItem,
    fields=("material", "quantity_required"),
    extra=3,
    can_delete=True,
)

