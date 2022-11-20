from django.shortcuts import render
import datetime
from expenses.models import Expense
from budget.models import Budget
from django.db.models import Sum
from django.http import JsonResponse

# Create your views here.
def index(request):
    TotalExpense = Expense.objects.filter(owner=request.user)
    sumExpense = TotalExpense.aggregate(Sum('amount'))
    for value in sumExpense.values():
        sumExpense=value

    """TotalBudget = Budget.objects.filter(owner=request.user)
    sumBudget = TotalBudget.aggregate(Sum('amount'))
    for value in sumBudget.values():
        sumBudget=value"""

    todays_date = datetime.date.today()
    today = todays_date-datetime.timedelta(days=0)
    expenseToday = Expense.objects.filter(owner=request.user,date__gte=today,date__lte=todays_date)
    sumTodayExpense= expenseToday.aggregate(Sum('amount'))
    for value in sumTodayExpense.values():
        sumTodayExpense=value

    """budgetToday = Budget.objects.filter(owner=request.user,date__gte=today,date__lte=todays_date)
    sumTodayBudget = budgetToday.aggregate(Sum('amount'))
    for value in sumTodayBudget.values():
        sumTodayBudget=value"""

    context = {
        'sumExpense': sumExpense,
        #'sumBudget': sumBudget,
        'expenseCount': expenseToday.count,
        'sumTodayExpense': sumTodayExpense,
        #'sumTodayBudget': sumTodayBudget,
        #'incomeCount': budgetToday.count,
    }
    return render(request, 'overview/index.html', context)

"""def budget_expense_summary(request):
    TotalExpense = Expense.objects.filter(owner=request.user)
    sumExpense = TotalExpense.aggregate(Sum('amount'))
    for value in sumExpense.values():
        sumExpense=value

    TotalBudget = Budget.objects.filter(owner=request.user)
    sumBudget = TotalBudget.aggregate(Sum('amount'))
    for value in sumBudget.values():
        sumBudget=value

    finalrep={'Expense':sumExpense,'Budget':sumBudget,'Savings':sumBudget-sumExpense}

    return JsonResponse({'expense_budget_data': finalrep},safe=False)"""