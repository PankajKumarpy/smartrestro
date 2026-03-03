from __future__ import annotations

from django import forms

from apps.menu.models import MenuItem
from apps.tables.models import RestaurantTable

from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("table", "notes")
        widgets = {"notes": forms.TextInput(attrs={"placeholder": "Optional notes"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["table"].queryset = RestaurantTable.objects.filter(is_active=True).order_by("name")
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class OrderAddItemForm(forms.Form):
    menu_item = forms.ModelChoiceField(queryset=MenuItem.objects.filter(is_available=True))
    quantity = forms.IntegerField(min_value=1, initial=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["menu_item"].widget.attrs.setdefault("class", "form-select")
        self.fields["quantity"].widget.attrs.setdefault("class", "form-control")

