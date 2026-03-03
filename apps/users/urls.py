from django.urls import path

from .views import RestaurantSignupView, StaffCreateView, StaffListView, StaffUpdateView


app_name = "users"

urlpatterns = [
    path("signup/", RestaurantSignupView.as_view(), name="signup"),
    path("staff/", StaffListView.as_view(), name="staff_list"),
    path("staff/new/", StaffCreateView.as_view(), name="staff_create"),
    path("staff/<int:pk>/edit/", StaffUpdateView.as_view(), name="staff_update"),
]

