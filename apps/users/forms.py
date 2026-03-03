from __future__ import annotations

from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import Restaurant, User


def _apply_bootstrap(form: forms.Form) -> None:
    for name, field in form.fields.items():
        widget = field.widget
        if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
            widget.attrs.setdefault("class", "form-check-input")
        else:
            widget.attrs.setdefault("class", "form-control")


class StaffCreateForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_bootstrap(self)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "phone", "role", "is_active")


class StaffUpdateForm(UserChangeForm):
    password = None  # hide password hash field

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_bootstrap(self)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "phone", "role", "is_active")


class RestaurantSignupForm(forms.Form):
    """
    Public signup form for a new restaurant + owner account.
    """

    restaurant_name = forms.CharField(label="Restaurant name", max_length=150)
    restaurant_phone = forms.CharField(label="Restaurant phone", max_length=20, required=False)

    owner_username = forms.CharField(label="Owner username", max_length=150)
    owner_email = forms.EmailField(label="Owner email", required=False)
    owner_password1 = forms.CharField(
        label="Password", strip=False, widget=forms.PasswordInput
    )
    owner_password2 = forms.CharField(
        label="Confirm password", strip=False, widget=forms.PasswordInput
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_bootstrap(self)

    def clean_owner_username(self):
        username = self.cleaned_data["owner_username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("owner_password1")
        p2 = cleaned.get("owner_password2")
        if p1 and p2 and p1 != p2:
            self.add_error("owner_password2", "Passwords do not match.")
        return cleaned

    def create_restaurant_and_owner(self) -> User:
        """
        Transaction is handled in the view; this just creates objects.
        """
        restaurant = Restaurant.objects.create(
            name=self.cleaned_data["restaurant_name"],
            phone=self.cleaned_data.get("restaurant_phone", ""),
        )
        user = User.objects.create_user(
            username=self.cleaned_data["owner_username"],
            email=self.cleaned_data.get("owner_email", ""),
            password=self.cleaned_data["owner_password1"],
            role="ADMIN",
            is_staff=True,
            is_superuser=True,
            restaurant=restaurant,
        )
        return user

