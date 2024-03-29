from django.shortcuts import render, redirect
from .models import Budget, Budget_amount
from django.core.paginator import Paginator
from expense.models import Category,Expense
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from django.http import JsonResponse, HttpResponse
import csv
import datetime
import calendar
import xlwt
from datetime import date
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum
from django.template.defaulttags import register
# Create your views here.

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@login_required(login_url='/authentication/login')
def search_budget(request):
    if request.method=='POST':
        search_str=json.loads(request.body).get('searchText')
        budget=Budget.objects.filter(amount__istartswith=search_str, owner=request.user) | Budget.objects.filter(date__istartswith=search_str, owner=request.user) | Budget.objects.filter(description__icontains=search_str, owner=request.user) | Budget.objects.filter(source__istartswith=search_str, owner=request.user)
        data = budget.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    #categories = Source.objects.all()
    currentDate = date.today()
    month = currentDate.strftime("%B")
    year = currentDate.strftime("%Y")
    budgetset = "set"
    try:
        budgets = Budget.objects.get(owner=request.user,month=month,year=year)
        budget_amount = Budget_amount.objects.filter(budget_id=budgets.id)
        context={
            'budgets': budgets,
            'month': month,
            'budget_amount': budget_amount,
            'budgetset': budgetset
        }
        return render(request, 'budget/index.html', context)
    except:
        context={
            'budgetset': 'notset'
        }
        return render(request, 'budget/index.html', context)

@login_required(login_url='/authentication/login')
def add_budget(request):
    categories = Category.objects.filter(type='global')
    usercategories = Category.objects.filter(type='local',owner=request.user)
    currentDate = date.today()
    month = currentDate.strftime("%B")
    year = currentDate.strftime("%Y")
    context={
            'categories': categories,
            'usercategories': usercategories,
            'month' : month,
            'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'budget/add_budget.html',context)

    if request.method == 'POST':
        amountCategory = request.POST.getlist('category')
        print(amountCategory)
        categoryList = list(categories)
        for category in usercategories:
            categoryList.append(category)
        final = dict(zip(categoryList, amountCategory))
        Budget.objects.create(month=month,year=year,owner=request.user)
        budget_last = Budget.objects.last()
        print(budget_last)
        for k,v in final.items():
            Budget_amount.objects.create(category=k,amount=v,budget_id=budget_last.id) 
        messages.success(request,'Budget saved successfully')
        return redirect('budget')

@login_required(login_url='/authentication/login')
def budget_edit(request, id):
    budget_amount=Budget_amount.objects.get(pk=id)
    context = {
        'budget_amount': budget_amount,
    }
    if request.method=='GET':
        return render(request, 'budget/edit_budget.html',context)
    if request.method=='POST':
        newamount = request.POST['category']
        budget_amount.amount=newamount
        budget_amount.save()
        messages.success(request,'Budget Amount Updated successfully')
        return redirect('budget')
        #messages.info(request,'Handling post form')
        #return render(request, 'budget/edit_budget.html',context)"""

@login_required(login_url='/authentication/login')
def delete_budget(request,id):
    budget=Budget.objects.get(pk=id)
    budget.delete()
    Budget_amount.objects.filter(budget_id=id).delete()
    messages.success(request,'Budget deleted successfully')
    return redirect('budget')

def budget_source_summary(request):
    currentDate = date.today()
    monthName = currentDate.strftime("%B")
    month = int(currentDate.strftime("%m"))
    year = int(currentDate.strftime("%Y"))
    day = int(currentDate.strftime("%d"))
    first, last = calendar.monthrange(year, month)
    category = request.POST.get('category',False)
    print(category)
    finalrep={'Budget amount':1000,'Spend amount':200,'Remaining amount':800}
    return JsonResponse({'budget_source_data': finalrep},safe=False)

@login_required(login_url='/authentication/login')
def bstats_view(request):
    currentDate = date.today()
    monthName = currentDate.strftime("%B")
    month = int(currentDate.strftime("%m"))
    year = int(currentDate.strftime("%Y"))
    day = int(currentDate.strftime("%d"))
    first, last = calendar.monthrange(year, month)
    start_date = datetime.datetime(year, month, 1)
    print(start_date)
    last_date = datetime.datetime(year, month, last)
    print(last_date)
    categoryTable = {}
    BudgetTable = {}
    remainingAmt = {} 
    categoryList = []
    msg = 'set'
    if day in range(1,last+1):
        try :
            Budget_id = Budget.objects.get(owner=request.user, month=monthName, year=year)
        except:
            context = {
                'msg' : 'unset'
            }
            return render(request, 'budget/bstats.html', context)
        BudgetCategory = Budget_amount.objects.filter(budget_id=Budget_id.id)
        categoryList = []
        for category in BudgetCategory:
            if category.category not in categoryList:
                categoryList.append(category.category)
        print(categoryList)
        for category in categoryList:
            amount = 0
            budget_amount = Budget_amount.objects.get(category=category,budget_id=Budget_id.id)
            expenses = Expense.objects.filter(owner=request.user,category=category,date__gte=start_date,date__lte=last_date)
            for expense in expenses:
                amount += expense.amount
            categoryTable[category] = amount
            BudgetTable[category] = budget_amount.amount
            remainingAmt[category] = budget_amount.amount-amount  
    
    budgetTable = {}
    for k,v in BudgetTable.items():
        if v==0:
            del categoryTable[k]
            del remainingAmt[k]
            categoryList.remove(k)
        else:
            budgetTable[k] = v

    print(categoryTable)
    print(budgetTable)
    print(remainingAmt)  

    context = {
        'categoryList': categoryList,
        'categoryTable': categoryTable,
        'monthname': monthName,
        'budgetTable': budgetTable, 
        'remainingAmt': remainingAmt,
        'msg' : msg,
    }
    return render(request, 'budget/bstats.html', context)

def budget_history(request):
    budgets = Budget.objects.filter(owner=request.user)
    budget_months = []
    budget_years = []
    for budget in budgets:
        budget_months.append(budget.month)
        if budget.year not in budget_years:
            budget_years.append(budget.year)
    context = {
        'budget_months': budget_months,
        'budget_years': budget_years,
        'value': 'unset',
    }
    if request.method == 'GET':
        return render(request, 'budget/budget_history.html',context)

    if request.method == 'POST':
        return render(request, 'budget/display_budget.html')

def display_budget(request):
    month = request.POST['Month']
    year = request.POST['Year']
    budget = Budget.objects.get(owner=request.user,month=month,year=year)
    budget_amount = Budget_amount.objects.filter(budget_id=budget.id)
    context = {
        'budget_amount': budget_amount,
        'value': 'set',
        'month': month,
        'year': year
    }
    return render(request, 'budget/display_budget.html',context)