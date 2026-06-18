from django.urls import path
from . import views

app_name = "expense"

urlpatterns = [
    path(
        "notifications/",
        views.NotificationListView.as_view(),
        name="api-notifications",
    ),
    path(
        "notifications/<uuid:pk>/read/",
        views.NotificationReadView.as_view(),
        name="api-notification-read",
    ),
    path("accounts/", views.AccountListCreateView.as_view(), name="api-accounts"),
    path(
        "accounts/<uuid:pk>/",
        views.AccountDetailView.as_view(),
        name="api-account-detail",
    ),
    path(
        "recurring/",
        views.RecurringExpenseListCreateView.as_view(),
        name="api-recurring",
    ),
    path(
        "recurring/<uuid:pk>/",
        views.RecurringExpenseDetailView.as_view(),
        name="api-recurring-detail",
    ),
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
    path("export/", views.ExpenseExportView.as_view(), name="api-export-query"),
]
