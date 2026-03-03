from __future__ import annotations

from django import forms

from .models import Invoice, PaymentMode, TaxConfig


class InvoicePaymentForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ("discount", "payment_mode")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["payment_mode"].required = True
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")


class TaxConfigForm(forms.ModelForm):
    class Meta:
        model = TaxConfig
        fields = ("gst_rate", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            else:
                widget.attrs.setdefault("class", "form-control")

