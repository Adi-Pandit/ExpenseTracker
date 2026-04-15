from django.urls import path
from . import views

app_name = "expense"

urlpatterns = [
    path("expenses/", views.ExpenseListCreateView.as_view(), name="api-expenses"),
    path(
        "expenses/<uuid:pk>/",
        views.ExpenseDetailView.as_view(),
        name="api-expense-detail",
    ),
    path("categories/", views.CategoryListCreateView.as_view(), name="api-categories"),
    path(
        "categories/<uuid:pk>/",
        views.CategoryDetailView.as_view(),
        name="api-category-detail",
    ),
    path("stats/", views.ExpenseStatsView.as_view(), name="api-stats"),
    path(
        "export/<str:format_type>/",
        views.ExpenseExportView.as_view(),
        name="api-export",
    ),
]
