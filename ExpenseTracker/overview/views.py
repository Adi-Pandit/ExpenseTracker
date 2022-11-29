from django.shortcuts import render
import datetime
from expense.models import Expense, Category
from budget.models import Budget, Budget_amount
from django.db.models import Sum
from django.http import JsonResponse
from datetime import date
import calendar
from collections import OrderedDict

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

    categories = Category.objects.filter(type='global')
    usercategories = Category.objects.filter(type='local',owner=request.user)
    categoryList = []
    categoryDict = {}
    for category in categories:
        categoryList.append(category.name)
        categoryDict[category.name] = 0
    for category in usercategories:
        categoryList.append(category.name)
        categoryDict[category.name] = 0
    categoryList.sort()
    categoryString = ""
    for category in categoryList:
        categoryString += category+"," 

    CategoryDict = dict(sorted(categoryDict.items()))
    print(CategoryDict)

    today = datetime.date.today()
    first = today.replace(day=1)
    last_month_last_date = first - datetime.timedelta(days=1)
    lastMonth = last_month_last_date.strftime("%B")
    last_month_first_date = last_month_last_date.replace(day=1)
    seclast_month_last_date = last_month_first_date - datetime.timedelta(days=1)
    secLastMonth = seclast_month_last_date.strftime("%B")
    seclast_month_first_date = seclast_month_last_date.replace(day=1)
    
    expenseLastMonth = Expense.objects.filter(owner=request.user,date__gte=last_month_first_date,date__lte=last_month_last_date)
    expenseSecLastMonth = Expense.objects.filter(owner=request.user,date__gte=seclast_month_first_date,date__lte=seclast_month_last_date)

    CurrentCategoryDict = CategoryDict.copy()
    for expense in expenseMonth:
        CurrentCategoryDict[expense.category] += expense.amount 
    CurrentCategoryList = list(CurrentCategoryDict.values())
    CurrentCategoryString = ""
    for amount in CurrentCategoryList:
        CurrentCategoryString += str(amount)+"," 

    LastCategoryDict = CategoryDict.copy()
    for expense in expenseLastMonth:
        LastCategoryDict[expense.category] += expense.amount
    LastCategoryList = list(LastCategoryDict.values())
    LastCategoryString = ""
    for amount in LastCategoryList:
        LastCategoryString += str(amount)+","

    SecLastCategoryDict = CategoryDict.copy()
    for expense in expenseSecLastMonth:
        SecLastCategoryDict[expense.category] += expense.amount
    SecLastCategoryList = list(SecLastCategoryDict.values())
    SecLastCategoryString = ""
    for amount in SecLastCategoryList:
        SecLastCategoryString += str(amount)+","

    context = {
        'sumMonthExpense': sumMonthExpense,
        'expenseCount': expenseToday.count,
        'sumTodayExpense': sumTodayExpense,
        'Total_budget': Total_budget,
        'percentage': percentage,
        'rem_percentage': rem_percentage,
        'monthName': monthName,
        'categoryString': categoryString,
        'lastMonth': lastMonth,
        'secLastMonth': secLastMonth,
        'CurrentCategoryString': CurrentCategoryString,
        'LastCategoryString': LastCategoryString,
        'SecLastCategoryString': SecLastCategoryString
    }
    return render(request, 'overview/index.html', context)

def budget_expense_summary(request):
    currentDate = date.today()
    month = int(currentDate.strftime("%m"))
    year = int(currentDate.strftime("%Y"))
    first, last = calendar.monthrange(year, month)
    start_date = datetime.datetime(year, month, first)
    last_date = datetime.datetime(year, month, last)
    TotalExpense = Expense.objects.filter(owner=request.user,date__gte=start_date,date__lte=last_date)
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