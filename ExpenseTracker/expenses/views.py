from unicodedata import category
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category,Expense
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse,HttpResponse
from usercategory.models import UserCategory
from datetime import datetime
import datetime
import csv
import xlwt
from django.template.loader import render_to_string
import os
#os.add_dll_directory(rb"C:\Program Files\GTK3-Runtime Win64\bin")
from weasyprint import HTML
import tempfile
from django.db.models import Sum 
import pdb
# Create your views here.

def home(request):
    return render(request, 'expenses/home.html')

@login_required(login_url='/authentication/login')
def search_expenses(request):
    if request.method=='POST':
        search_str=json.loads(request.body).get('searchText')
        expenses=Expense.objects.filter(amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(date__istartswith=search_str, owner=request.user) | Expense.objects.filter(description__icontains=search_str, owner=request.user) | Expense.objects.filter(category__istartswith=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 8)
    page_list = []
    for i in range(1,paginator.num_pages+1):
        page_list.append(i)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator,page_number)
    context={
        'expenses': expenses,
        'page_obj': page_obj,
        'page_list': page_list 
    }
    return render(request, 'expenses/index.html', context)

@login_required(login_url='/authentication/login')
def add_expenses(request):
    categories = Category.objects.all()
    usercategories = UserCategory.objects.filter(owner=request.user)
    context={
            'categories': categories,
            'usercategories' : usercategories,
            'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expenses.html',context)

    if request.method == 'POST':
        amount=request.POST['amount']

        if not amount:
            messages.error(request,'Amount is required')
            return render(request, 'expenses/add_expenses.html',context)

        description=request.POST['description']
        date=request.POST['expense_date']
        category=request.POST['category']

        if not description:
            messages.error(request,'Description is required')
            return render(request, 'expenses/add_expenses.html',context)

        Expense.objects.create(owner=request.user,amount=amount,date=date,category=category,description=description)
        messages.success(request,'Expense saved successfully')
        return redirect('expenses')

@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense=Expense.objects.get(pk=id)
    categories=Category.objects.all()
    usercategories = UserCategory.objects.filter(owner=request.user)
    context = {
        'expense': expense,
        'values': expense,
        'categories':categories,
        'usercategories' : usercategories,
    }
    if request.method=='GET':
        return render(request, 'expenses/edit-expense.html',context)
    if request.method=='POST':
        amount=request.POST['amount']

        if not amount:
            messages.error(request,'Amount is required')
            return render(request, 'expenses/edit-expense.html',context)

        description=request.POST['description']
        date=request.POST['expense_date']
        category=request.POST['category']

        if not description:
            messages.error(request,'Description is required')
            return render(request, 'expenses/edit-expense.html',context)

        if not date:
            messages.error(request,'Date is required')
            return render(request, 'expenses/edit-expense.html',context)

        expense.owner=request.user
        expense.amount=amount
        expense.date=date 
        expense.category=category 
        expense.description=description

        expense.save()
        messages.success(request,'Expense Updated successfully')
        return redirect('expenses')


        #messages.info(request,'Handling post form')
        #return render(request, 'expenses/edit-expense.html',context)

@login_required(login_url='/authentication/login')
def delete_expense(request,id):
    expense=Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request,'Expense removed')
    return redirect('expenses')

@login_required(login_url='/authentication/login')
def expense_category_summary(request):
        start_date = request.POST.get('startdate',False)
        end_date = request.POST.get('enddate',False)
        """if not start_date:
            messages.success(request,'Expense Updated successfully')
            return render(request, 'expenses/stats.html')
        if not end_date:
            messages.success(request,'Expense Updated successfully')
            redirect('stats')"""
        if not start_date:
            if not end_date:
                todays_date = datetime.date.today()
                six_months_ago = todays_date-datetime.timedelta(days=30*6)
                expenses = Expense.objects.filter(owner=request.user,date__gte=six_months_ago,date__lte=todays_date)
                finalrep={}

                TotalExpense = Expense.objects.filter(owner=request.user)
                sumExpense = TotalExpense.aggregate(Sum('amount'))
                for value in sumExpense.values():
                    sumExpense=value

                def get_category(expense):
                    return expense.category

                def get_expense_category_amount(category):
                    global TotalAmount
                    amount = 0
                    filtered_by_category = expenses.filter(category=category)
                    for item in filtered_by_category:
                        amount += item.amount
                    return round((amount/sumExpense)*100,2)

                category_list = list(set(map(get_category, expenses)))
                for x in expenses:
                    for y in category_list:
                        finalrep[y]=get_expense_category_amount(y)
                return JsonResponse({'expense_category_data': finalrep},safe=False)
        """if start_date==None:
            messages.success(request,'Expense Updated successfully')
            redirect('stats')
        EndDate = datetime.strptime(end_date,'%d-%m-%Y')
        StartDate = datetime.strptime(start_date,'%d-%m-%Y')
        expenses = Expense.objects.filter(owner=request.user,date__gte=StartDate,date__lte=EndDate)
        finalrep={}
        TotalExpense = Expense.objects.filter(owner=request.user)
        sumExpense = TotalExpense.aggregate(Sum('amount'))
        for value in sumExpense.values():
            sumExpense=value

        def get_category(expense):
            return expense.category

        def get_expense_category_amount(category):
            global TotalAmount
            amount = 0
            filtered_by_category = expenses.filter(category=category)
            for item in filtered_by_category:
                amount += item.amount
            return round((amount/sumExpense)*100,2)

        category_list = list(set(map(get_category, expenses)))
        for x in expenses:
            for y in category_list:
                finalrep[y]=get_expense_category_amount(y)
        return JsonResponse({'expense_category_data': finalrep},safe=False)"""


@login_required(login_url='/authentication/login')
def stats_view(request):
    todays_date = datetime.date.today()
    today = todays_date-datetime.timedelta(days=0)
    expenseToday = Expense.objects.filter(owner=request.user,date__gte=today,date__lte=todays_date)
    sumToday= expenseToday.aggregate(Sum('amount'))
    for value in sumToday.values():
        sumToday=value

    week = todays_date-datetime.timedelta(days=7)
    expenseWeek = Expense.objects.filter(owner=request.user,date__gte=week,date__lte=todays_date)
    sumWeek= expenseWeek.aggregate(Sum('amount'))
    for value in sumWeek.values():
        sumWeek=value

    month = todays_date-datetime.timedelta(days=30)
    expenseMonth = Expense.objects.filter(owner=request.user,date__gte=month,date__lte=todays_date)
    sumMonth= expenseMonth.aggregate(Sum('amount'))
    for value in sumMonth.values():
        sumMonth=value

    year = todays_date-datetime.timedelta(days=365)
    expenseYear = Expense.objects.filter(owner=request.user,date__gte=year,date__lte=todays_date)
    sumYear= expenseYear.aggregate(Sum('amount'))
    for value in sumYear.values():
        sumYear=value

    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user,date__gte=six_months_ago,date__lte=todays_date)
    finalrep = {}
    def get_category(expense):
        return expense.category

    def get_expense_category_amount(category):
        global TotalAmount
        amount = 0
        filtered_by_category = expenses.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount

    category_list = list(set(map(get_category, expenses)))
    for x in expenses:
        for y in category_list:
            finalrep[y]=get_expense_category_amount(y)
    #categories = list(Expense.category)
    context={
        'sumToday':sumToday,
        'sumWeek':sumWeek,
        'sumMonth':sumMonth, 
        'sumYear':sumYear,
        'finalrep':finalrep,
    }
    return render(request, 'expenses/stats.html', context)

@login_required(login_url='/authentication/login')
def export_csv(request):
    response =  HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename=Expenses/'+str(datetime.datetime.now())+'.csv'
    writer=csv.writer(response)
    writer.writerow(['Amount','Description','Category','Date'])
    expenses=Expense.objects.filter(owner=request.user)
    for expense in expenses:
        writer.writerow([expense.amount,expense.description,expense.category,expense.date])
    return response

@login_required(login_url='/authentication/login')
def export_excel(request):
    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=Expenses/'+str(datetime.datetime.now())+'.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Amount','Description','Category','Date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    
    font_style = xlwt.XFStyle()
    rows = Expense.objects.filter(owner=request.user).values_list('amount','description','category','date')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)
    return response

@login_required(login_url='/authentication/login')
def export_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename=Expenses/'+str(datetime.datetime.now())+'.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    expenses=Expense.objects.filter(owner=request.user)

    sum=expenses.aggregate(Sum('amount'))

    html_string = render_to_string('expenses/pdf-output.html',{'expenses':expenses,'total':sum['amount__sum']})
    html = HTML(string=html_string)
    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        #output=open(output.name, 'rb')
        output.seek(0)
        response.write(output.read())
    return response

@login_required(login_url='/authentication/login')
def expense_summary_today(request):
    todays_date = datetime.date.today()
    today = todays_date-datetime.timedelta(days=1)
    expenses = Expense.objects.filter(owner=request.user,date__gte=today,date__lte=todays_date)
    sumToday=expenses.aggregate(Sum('amount'))
    context={
        'sumToday':sumToday,
    }
    return render(request, 'expenses/stats.html', context)


