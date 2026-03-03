from __future__ import annotations

from django import forms

from .models import Category, MenuItem


def _apply_bootstrap(form: forms.Form) -> None:
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs.setdefault("class", "form-check-input")
        elif isinstance(widget, forms.ClearableFileInput):
            widget.attrs.setdefault("class", "form-control")
        else:
            widget.attrs.setdefault("class", "form-control")


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "description", "is_active")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_bootstrap(self)


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ("category", "name", "description", "price", "is_available", "image")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_bootstrap(self)

