from django.urls import path

from .views import (
    CategoryCreateView,
    CategoryListView,
    CategoryUpdateView,
    MenuItemCreateView,
    MenuItemDeleteView,
    MenuItemListView,
    MenuItemUpdateView,
)


app_name = "menu"

urlpatterns = [
    path("", MenuItemListView.as_view(), name="item_list"),
    path("new/", MenuItemCreateView.as_view(), name="item_create"),
    path("<int:pk>/edit/", MenuItemUpdateView.as_view(), name="item_update"),
    path("<int:pk>/delete/", MenuItemDeleteView.as_view(), name="item_delete"),

    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("categories/new/", CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", CategoryUpdateView.as_view(), name="category_update"),
]

