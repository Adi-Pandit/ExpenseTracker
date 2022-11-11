from django.shortcuts import render
import datetime
from expenses.models import Expense
from userincome.models import UserIncome
from django.db.models import Sum
from django.http import JsonResponse

# Create your views here.
def index(request):
    TotalExpense = Expense.objects.filter(owner=request.user)
    sumExpense = TotalExpense.aggregate(Sum('amount'))
    for value in sumExpense.values():
        sumExpense=value

    TotalIncome = UserIncome.objects.filter(owner=request.user)
    sumIncome = TotalIncome.aggregate(Sum('amount'))
    for value in sumIncome.values():
        sumIncome=value

    todays_date = datetime.date.today()
    today = todays_date-datetime.timedelta(days=0)
    expenseToday = Expense.objects.filter(owner=request.user,date__gte=today,date__lte=todays_date)
    sumTodayExpense= expenseToday.aggregate(Sum('amount'))
    for value in sumTodayExpense.values():
        sumTodayExpense=value

    incomeToday = UserIncome.objects.filter(owner=request.user,date__gte=today,date__lte=todays_date)
    sumTodayIncome = incomeToday.aggregate(Sum('amount'))
    for value in sumTodayIncome.values():
        sumTodayIncome=value

    context = {
        'sumExpense': sumExpense,
        'sumIncome': sumIncome,
        'expenseCount': expenseToday.count,
        'sumTodayExpense': sumTodayExpense,
        'sumTodayIncome': sumTodayIncome,
        'incomeCount': incomeToday.count,
    }
    return render(request, 'overview/index.html', context)

def income_expense_summary(request):
    TotalExpense = Expense.objects.filter(owner=request.user)
    sumExpense = TotalExpense.aggregate(Sum('amount'))
    for value in sumExpense.values():
        sumExpense=value

    TotalIncome = UserIncome.objects.filter(owner=request.user)
    sumIncome = TotalIncome.aggregate(Sum('amount'))
    for value in sumIncome.values():
        sumIncome=value

    finalrep={'Expense':sumExpense,'Income':sumIncome,'Savings':sumIncome-sumExpense}

    return JsonResponse({'expense_income_data': finalrep},safe=False)