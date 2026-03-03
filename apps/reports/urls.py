from django.urls import path

from .views import DailyClosingPdfView, DailyClosingView


app_name = "reports"

urlpatterns = [
    path("daily-closing/", DailyClosingView.as_view(), name="daily_closing"),
    path("daily-closing/pdf/", DailyClosingPdfView.as_view(), name="daily_closing_pdf"),
]

