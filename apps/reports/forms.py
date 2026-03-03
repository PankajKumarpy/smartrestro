from __future__ import annotations

from django import forms

from .models import Expense


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ("date", "title", "amount", "note")
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            widget.attrs.setdefault("class", "form-control")


class ReportDateForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))

