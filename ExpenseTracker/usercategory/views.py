from django.shortcuts import render, redirect
from .models import UserCategory
from django.contrib import messages

# Create your views here.

def index(request):
    usercategories = UserCategory.objects.filter(owner=request.user)
    context = {
        'usercategories' : usercategories
    }
    return render(request,'usercategory/index.html',context)

def add_category(request):
    usercategories = UserCategory.objects.filter(owner=request.user)
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
            UserCategory.objects.create(usercategory=usercategory,owner=request.user)
        except:
            messages.error(request,'Category already exist')
            return render(request, 'usercategory/add_category.html')
        messages.success(request,'Category saved successfully')
        return redirect('usercategory')

def delete_category(request,id):
    category=UserCategory.objects.get(pk=id)
    category.delete()
    messages.success(request,'Category removed')
    return redirect('usercategory')