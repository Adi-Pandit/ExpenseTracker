from django.urls import path
from . import views

urlpatterns = [
    path('overview',views.index,name='overview'),
    #path('budget_expense_summary', views.budget_expense_summary, name="budget_expense_summary"),
]
