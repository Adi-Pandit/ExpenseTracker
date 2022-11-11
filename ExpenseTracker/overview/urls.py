from django.urls import path
from . import views

urlpatterns = [
    path('overview',views.index,name='overview'),
    path('income_expense_summary', views.income_expense_summary, name="income_expense_summary"),
]
