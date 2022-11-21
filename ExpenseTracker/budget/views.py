from django.shortcuts import render, redirect
from .models import Budget, Budget_amount
from django.core.paginator import Paginator
from usercategory.models import UserCategory
from expenses.models import Category,Expense
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
    categories = Category.objects.all()
    usercategories = UserCategory.objects.filter(owner=request.user)
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
        messages.success(request,'Budget Updated successfully')
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

"""def budget_source_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    budgets = Budget.objects.filter(owner=request.user)
    finalrep={}

    category = request.POST[]
    return JsonResponse({'budget_source_data': finalrep},safe=False)"""

@login_required(login_url='/authentication/login')
def bstats_view(request):
    currentDate = date.today()
    monthName = currentDate.strftime("%B")
    month = int(currentDate.strftime("%m"))
    year = int(currentDate.strftime("%Y"))
    day = int(currentDate.strftime("%d"))
    first, last = calendar.monthrange(year, month)
    categoryTable = {}
    budgetTable = {}
    if day in range(first,last+1):
        categoryList = list(Category.objects.all())
        usercategory = list(UserCategory.objects.filter(owner=request.user))
        for category in usercategory:
            categoryList.append(category)
        for category in categoryList:
            amount = 0
            Budget_id = Budget.objects.get(owner=request.user,month=monthName,year=year)
            budget_amount = Budget_amount.objects.get(category=category,budget_id=Budget_id.id)
            expenses = Expense.objects.filter(category=category)
            for expense in expenses:
                amount += expense.amount
            categoryTable[category] = amount
            budgetTable[category] = budget_amount.amount
    context = {
        'categoryTable': categoryTable,
        'monthname': monthName,
        'budgetTable': budgetTable
    }
    return render(request, 'budget/bstats.html', context)
    #return render(request, 'budget/istats.html')
"""
@login_required(login_url='/authentication/login')
def bexport_csv(request):
    response =  HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename=Income/'+str(datetime.datetime.now())+'.csv'
    writer=csv.writer(response)
    writer.writerow(['Amount','Description','Source','Date'])
    userincome=Budget.objects.filter(owner=request.user)
    for budget in userincome:
        writer.writerow([budget.amount,budget.description,budget.source,budget.date])
    return response

def bexport_excel(request):
    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=Income/'+str(datetime.datetime.now())+'.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Income')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Amount','Description','Source','Date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
        
    font_style = xlwt.XFStyle()
    rows = Budget.objects.filter(owner=request.user).values_list('amount','description','source','date')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)
    return response

@login_required(login_url='/authentication/login')
def bexport_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename=Income/'+str(datetime.datetime.now())+'.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    budgets=Budget.objects.filter(owner=request.user)

    sum=budgets.aggregate(Sum('amount'))

    html_string = render_to_string('budget/bpdf_output.html',{'budgets':budgets,'total':sum['amount__sum']})
    html = HTML(string=html_string)
    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        #output=open(output.name, 'rb')
        output.seek(0)
        response.write(output.read())
    return response"""