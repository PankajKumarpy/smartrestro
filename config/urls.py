from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from apps.users.views import DashboardView, HomeRedirectView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", HomeRedirectView.as_view(), name="home"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),

    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("users/", include(("apps.users.urls", "users"), namespace="users")),
    path("menu/", include(("apps.menu.urls", "menu"), namespace="menu")),
    path("tables/", include(("apps.tables.urls", "tables"), namespace="tables")),
    path("orders/", include(("apps.orders.urls", "orders"), namespace="orders")),
    path("billing/", include(("apps.billing.urls", "billing"), namespace="billing")),
    path("inventory/", include(("apps.inventory.urls", "inventory"), namespace="inventory")),
    path("reports/", include(("apps.reports.urls", "reports"), namespace="reports")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
