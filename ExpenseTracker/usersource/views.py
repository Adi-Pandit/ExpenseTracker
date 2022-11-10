from django.shortcuts import render, redirect
from .models import UserSource
from django.contrib import messages

# Create your views here.

def index(request):
    usersources = UserSource.objects.filter(owner=request.user)
    context = {
        'usersources' : usersources
    }
    return render(request,'usersource/index.html',context)

def add_source(request):
    usersources = UserSource.objects.filter(owner=request.user)
    context={
            'usersources' : usersources,
    }
    if request.method == 'GET':
        return render(request, 'usersource/add_source.html',context)

    if request.method == 'POST':
        usersource = request.POST['source']

        if not usersource:
            messages.error(request,'Source is required')
            return render(request, 'usersource/add_source.html',context)
        try:
            UserSource.objects.create(usersource=usersource,owner=request.user)
        except:
            messages.error(request,'Source already exist')
            return render(request, 'usersource/add_source.html')
        messages.success(request,'Source saved successfully')
        return redirect('usersource')

def delete_source(request,id):
    source=UserSource.objects.get(pk=id)
    source.delete()
    messages.success(request,'Source removed')
    return redirect('usersource')