from __future__ import annotations

from django import forms

from .models import RestaurantTable


class RestaurantTableForm(forms.ModelForm):
    class Meta:
        model = RestaurantTable
        fields = ("name", "capacity", "status", "is_active", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            else:
                widget.attrs.setdefault("class", "form-control")

