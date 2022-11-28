from django.shortcuts import render
import datetime
from expense.models import Expense, Category
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

    '''categories = Category.objects.filter(type='global')
    usercategories = Category.objects.filter(type='local',owner=request.user)
    categoryList = ""
    for category in categories:
        categoryList += str(category)+","
    for category in usercategories:
        categoryList += str(category)+","'''
    
    today = datetime.date.today()
    first = today.replace(day=1)
    last_month_last_date = first - datetime.timedelta(days=1)
    lastMonth = last_month_last_date.strftime("%B")
    last_month_first_date = last_month_last_date.replace(day=1)
    seclast_month_last_date = last_month_first_date - datetime.timedelta(days=1)
    secLastMonth = seclast_month_last_date.strftime("%B")
    seclast_month_first_date = seclast_month_last_date.replace(day=1)
    print(last_month_first_date)
    print(last_month_last_date)
    print(seclast_month_first_date)
    print(seclast_month_last_date)

    categoryList = ""
    expenseMonthList = ""
    for expense in expenseMonth:
        expenseMonthList += str(expense.amount)+","
        categoryList += expense.category+","

    expenseLastMonth = Expense.objects.filter(owner=request.user,date__gte=last_month_first_date,date__lte=last_month_last_date)


    context = {
        'sumMonthExpense': sumMonthExpense,
        'expenseCount': expenseToday.count,
        'sumTodayExpense': sumTodayExpense,
        'Total_budget': Total_budget,
        'percentage': percentage,
        'rem_percentage': rem_percentage,
        'monthName': monthName,
        'categoryList': categoryList,
        'lastMonth': lastMonth,
        'secLastMonth': secLastMonth,
        'expenseMonthList': expenseMonthList
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