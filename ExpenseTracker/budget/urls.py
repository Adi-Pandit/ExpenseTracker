from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name='budget'),
    path('add-budget', views.add_budget, name='add-budget'),
    path('edit-budget/<int:id>', views.budget_edit, name='budget-edit'),
    path('budget-delete/<int:id>', views.delete_budget, name='budget-delete'),
    #path('search-budget', csrf_exempt(views.search_budget), name='search_budget'),
    #path('budget_source_summary', views.budget_source_summary, name="budget_source_summary"),
    #path('income_summary_today', views.income_summary_today, name="income_summary_today"),
    #path('stats', views.bstats_view, name='bstats'),
    #path('export_csv', views.bexport_csv, name='bexport-csv'),
    #path('export_excel', views.bexport_excel, name='bexport-excel'),
    #path('export_pdf', views.bexport_pdf, name='bexport-pdf'),
]