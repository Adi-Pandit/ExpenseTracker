from django.shortcuts import render
import datetime
from expense.models import Expense
from budget.models import Budget, Budget_amount
from django.db.models import Sum
from django.http import JsonResponse
from datetime import date
import calendar

# Create your views here.
def index(request):
    currentDate = date.today()
    monthName = currentDate.strftime("%B")
    month = int(currentDate.strftime("%m"))
    year = int(currentDate.strftime("%Y"))
    first, last = calendar.monthrange(year, month)
    start_date = datetime.datetime(year, month, first)
    last_date = datetime.datetime(year, month, last)
    expenseMonth = Expense.objects.filter(owner=request.user,date__gte=start_date,date__lte=last_date)
    sumMonthExpense = expenseMonth.aggregate(Sum('amount'))
    for value in sumMonthExpense.values():
        sumMonthExpense=value

    budget = Budget.objects.get(owner=request.user, month=monthName, year=year)
    budget_amount = Budget_amount.objects.filter(budget_id=budget.id)
    Total_budget = 0
    for amt in budget_amount:
        Total_budget += amt.amount
    
    percentage = (sumMonthExpense/Total_budget)*100
    rem_percentage = 100-percentage

    todays_date = datetime.date.today()
    today = todays_date-datetime.timedelta(days=0)
    expenseToday = Expense.objects.filter(owner=request.user,date__gte=today,date__lte=todays_date)
    sumTodayExpense= expenseToday.aggregate(Sum('amount'))
    for value in sumTodayExpense.values():
        sumTodayExpense=value

    context = {
        'sumMonthExpense': sumMonthExpense,
        'expenseCount': expenseToday.count,
        'sumTodayExpense': sumTodayExpense,
        'Total_budget': Total_budget,
        'percentage': percentage,
        'rem_percentage': rem_percentage,
        'monthName': monthName
    }
    return render(request, 'overview/index.html', context)

def budget_expense_summary(request):
    TotalExpense = Expense.objects.filter(owner=request.user)
    sumExpense = TotalExpense.aggregate(Sum('amount'))
    for value in sumExpense.values():
        sumExpense=value

    currentDate = date.today()
    monthName = currentDate.strftime("%B")
    year = int(currentDate.strftime("%Y"))
    budget = Budget.objects.get(owner=request.user, month=monthName, year=year)
    budget_amount = Budget_amount.objects.filter(budget_id=budget.id)
    Total_budget = 0
    for amt in budget_amount:
        Total_budget += amt.amount

    finalrep={'Expense':sumExpense,'Budget':Total_budget,'Balance':Total_budget-sumExpense}

    return JsonResponse({'expense_budget_data': finalrep},safe=False)