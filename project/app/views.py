from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model,login,authenticate,logout
from django.http import HttpResponse

from .models import *
# Create your views here.

User  = get_user_model()

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request,username=username,password=password)
        if user:
            login(request,user)
            return redirect(admin_dashboard)
        else:
            return redirect(admin_login)
    
    return render(request,'login.html')


def admin_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        user = User.objects.create_user(username=username,password=password,email=email)

        return redirect(admin_login)
    
    return render(request,'register.html')



def admin_dashboard(request):
    if request.user.is_authenticated:
        sessions = Session.objects.filter(admin = request.user,is_active = True)

        return render(request,'dashboard.html',{'code':request.user.admin_code,'sessions':sessions})
    
    else:
        return redirect(admin_register)
    


def join_session(request):
    if request.method == 'POST':
        name = request.POST['name']
        code = request.POST['code']
        try:
            admin = User.objects.get(admin_code = code)
            data=Session.objects.create(admin=admin,student_name = name)
            request.session['sess'] = data.id
            return redirect(session)
        except User.DoesNotExist:
            return HttpResponse('Invaid admin code')

    return render(request,'joinsession.html')


def session(request):
    if 'sess' in request.session:
        sess = Session.objects.get(id=request.session['sess'])

        return render(request, 'session.html', {
            'session': sess,
            'admin_id': sess.admin.id
        })

    return redirect(join_session)

    

def end_session(request,session_id):
    try:
        session = Session.objects.filter(id = session_id).update(is_active = False)
        return redirect(join_session)
    except Session.DoesNotExist:
        return redirect(join_session)
    
