from django.urls import path

from .views import (
    MaterialCreateView,
    MaterialListView,
    MaterialUpdateView,
    RecipeCreateView,
    RecipeEditView,
    RecipeListView,
    StockMovementCreateView,
    SupplierCreateView,
    SupplierListView,
    SupplierUpdateView,
)


app_name = "inventory"

urlpatterns = [
    path("", MaterialListView.as_view(), name="material_list"),
    path("materials/new/", MaterialCreateView.as_view(), name="material_create"),
    path("materials/<int:pk>/edit/", MaterialUpdateView.as_view(), name="material_update"),

    path("suppliers/", SupplierListView.as_view(), name="supplier_list"),
    path("suppliers/new/", SupplierCreateView.as_view(), name="supplier_create"),
    path("suppliers/<int:pk>/edit/", SupplierUpdateView.as_view(), name="supplier_update"),

    path("movements/new/", StockMovementCreateView.as_view(), name="movement_create"),

    path("recipes/", RecipeListView.as_view(), name="recipe_list"),
    path("recipes/new/", RecipeCreateView.as_view(), name="recipe_create"),
    path("recipes/<int:pk>/edit/", RecipeEditView.as_view(), name="recipe_edit"),
]

