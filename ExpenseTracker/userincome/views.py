from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from django.http import JsonResponse, HttpResponse
import csv
import datetime
import xlwt
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum
# Create your views here.

def search_income(request):
    if request.method=='POST':
        search_str=json.loads(request.body).get('searchText')
        income=UserIncome.objects.filter(amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(source__istartswith=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator,page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context={
        'income': income,
        'page_obj' : page_obj,
        'currency' : currency
    }
    return render(request, 'income/index.html', context)

@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context={
            'sources': sources,
            'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html',context)

    if request.method == 'POST':
        amount=request.POST['amount']

        if not amount:
            messages.error(request,'Amount is required')
            return render(request, 'income/add_income.html',context)

        description=request.POST['description']
        date=request.POST['income_date']
        source=request.POST['source']

        if not description:
            messages.error(request,'Description is required')
            return render(request, 'income/add_income.html',context)

        UserIncome.objects.create(owner=request.user,amount=amount,date=date,source=source,description=description)
        messages.success(request,'Income saved successfully')
        return redirect('income')

@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income=UserIncome.objects.get(pk=id)
    sources=Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources':sources,
    }
    if request.method=='GET':
        return render(request, 'income/edit_income.html',context)
    if request.method=='POST':
        amount=request.POST['amount']

        if not amount:
            messages.error(request,'Amount is required')
            return render(request, 'income/edit_income.html',context)

        description=request.POST['description']
        date=request.POST['income_date']
        source=request.POST['source']

        if not description:
            messages.error(request,'Description is required')
            return render(request, 'income/edit_income.html',context)

        if not date:
            messages.error(request,'Date is required')
            return render(request, 'income/edit_income.html',context)

        income.amount=amount
        income.date=date 
        income.source=source 
        income.description=description

        income.save()
        messages.success(request,'Record Updated successfully')
        return redirect('income')


        #messages.info(request,'Handling post form')
        #return render(request, 'income/edit_income.html',context)

def delete_income(request,id):
    income=UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request,'record removed')
    return redirect('income')

def income_source_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    incomes = UserIncome.objects.filter(owner=request.user,date__gte=six_months_ago,date__lte=todays_date)
    finalrep={}

    def get_source(income):
        return income.source

    def get_income_source_amount(source):
        amount = 0
        filtered_by_source = incomes.filter(source=source)
        for item in filtered_by_source:
            amount += item.amount
        return amount

    source_list = list(set(map(get_source, incomes)))
    for x in incomes:
        for y in source_list:
            finalrep[y]=get_income_source_amount(y)
    return JsonResponse({'income_source_data': finalrep},safe=False)

def istats_view(request):
    todays_date = datetime.date.today()
    today = todays_date-datetime.timedelta(days=0)
    incomeToday = UserIncome.objects.filter(owner=request.user,date__gte=today,date__lte=todays_date)
    sumToday= incomeToday.aggregate(Sum('amount'))
    for value in sumToday.values():
        sumToday=value

    week = todays_date-datetime.timedelta(days=7)
    incomeWeek = UserIncome.objects.filter(owner=request.user,date__gte=week,date__lte=todays_date)
    sumWeek= incomeWeek.aggregate(Sum('amount'))
    for value in sumWeek.values():
        sumWeek=value

    month = todays_date-datetime.timedelta(days=30)
    incomeMonth = UserIncome.objects.filter(owner=request.user,date__gte=month,date__lte=todays_date)
    sumMonth= incomeMonth.aggregate(Sum('amount'))
    for value in sumMonth.values():
        sumMonth=value

    year = todays_date-datetime.timedelta(days=365)
    incomeYear = UserIncome.objects.filter(owner=request.user,date__gte=year,date__lte=todays_date)
    sumYear= incomeYear.aggregate(Sum('amount'))
    for value in sumYear.values():
        sumYear=value

    context={
        'sumToday':sumToday,
        'sumWeek':sumWeek,
        'sumMonth':sumMonth,
        'sumYear':sumYear,
    }
    return render(request, 'income/istats.html', context)
    #return render(request, 'income/istats.html')

def iexport_csv(request):
    response =  HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename=Income/'+str(datetime.datetime.now())+'.csv'
    writer=csv.writer(response)
    writer.writerow(['Amount','Description','Source','Date'])
    userincome=UserIncome.objects.filter(owner=request.user)
    for income in userincome:
        writer.writerow([income.amount,income.description,income.source,income.date])
    return response

def iexport_excel(request):
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
    rows = UserIncome.objects.filter(owner=request.user).values_list('amount','description','source','date')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)
    return response

def iexport_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename=Income/'+str(datetime.datetime.now())+'.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    incomes=UserIncome.objects.filter(owner=request.user)

    sum=incomes.aggregate(Sum('amount'))

    html_string = render_to_string('income/ipdf_output.html',{'incomes':incomes,'total':sum['amount__sum']})
    html = HTML(string=html_string)
    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        #output=open(output.name, 'rb')
        output.seek(0)
        response.write(output.read())
    return response

def income_summary_today(request):
    pass