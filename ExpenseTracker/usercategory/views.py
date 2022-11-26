from django.shortcuts import render, redirect
from django.contrib import messages
from expense.models import Category

# Create your views here.

def index(request):
    usercategories = Category.objects.filter(owner=request.user,type="local")
    context = {
        'usercategories' : usercategories
    }
    return render(request,'usercategory/index.html',context)

def add_category(request):
    usercategories = Category.objects.filter(owner=request.user,type="local")
    context={
            'usercategories' : usercategories,
    }
    if request.method == 'GET':
        return render(request, 'usercategory/add_category.html',context)

    if request.method == 'POST':
        usercategory = request.POST['category']

        if not usercategory:
            messages.error(request,'Category is required')
            return render(request, 'usercategory/add_category.html',context)
        try:
            Category.objects.create(name=usercategory,owner=request.user,type="local")
        except:
            messages.error(request,'Category already exist') 
            return render(request, 'usercategory/add_category.html')
        messages.success(request,'Category saved successfully')
        return redirect('usercategory')

def edit_category(request,id):
    usercategories = Category.objects.get(pk=id)
    context={
            'usercategories' : usercategories,
    }
    if request.method == 'GET':
        return render(request, 'usercategory/edit_category.html',context)

    if request.method == 'POST':
        usercategory = request.POST['category']

        if not usercategory:
            messages.error(request,'Category is required')
            return render(request, 'usercategory/edit_category.html',context)
        
        usercategories.owner = request.user
        usercategories.name = usercategory
        usercategories.type = "local"

        usercategories.save()

        messages.success(request,'Category saved successfully')
        return redirect('usercategory')

def delete_category(request,id):
    usercategory=Category.objects.get(pk=id)
    usercategory.delete()
    messages.success(request,'Category removed')
    return redirect('usercategory')