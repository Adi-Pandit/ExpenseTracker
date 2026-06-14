from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("summary", views.DashboardSummaryAPIView.as_view(), name="summary"),
    path("trends", views.DashboardTrendsAPIView.as_view(), name="trends"),
    path("categories", views.DashboardCategoriesAPIView.as_view(), name="categories"),
    path("recent", views.DashboardRecentAPIView.as_view(), name="recent"),
    path("insights", views.DashboardInsightsAPIView.as_view(), name="insights"),
]
