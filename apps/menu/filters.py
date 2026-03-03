import django_filters

from .models import MenuItem


class MenuItemFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q", label="Search")

    class Meta:
        model = MenuItem
        fields = ["category", "is_available"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.form.fields.values():
            field.widget.attrs.setdefault("class", "form-select")

    def filter_q(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(name__icontains=value.strip())

