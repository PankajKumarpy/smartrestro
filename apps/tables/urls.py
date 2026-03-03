from django.urls import path

from .views import TableCreateView, TableListView, TableSetStatusView, TableUpdateView


app_name = "tables"

urlpatterns = [
    path("", TableListView.as_view(), name="table_list"),
    path("new/", TableCreateView.as_view(), name="table_create"),
    path("<int:pk>/edit/", TableUpdateView.as_view(), name="table_update"),
    path("<int:pk>/set-status/", TableSetStatusView.as_view(), name="table_set_status"),
]

