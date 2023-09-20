from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model

user=get_user_model()
def index(request):
    return render(request, 'index.html')

def conferences(request):
    # conferences = Conference.objects.all()
    return render(request, 'view_conferences.html')

@login_required
def author(request):
    return render(request, 'authrs-view.html')

@login_required
def reviewer(request):
    return render(request, 'reviewer-view.html')

@login_required
def programChair(request):
    return render(request, 'program_chair.html')

def signup(request):
    if request.method == 'POST':
            formal_title = request.POST["designation"]
            first_name= request.POST["fname"]
            last_name= request.POST["lname"]
            email= request.POST["email"]
            phone= request.POST["phone"]
            prof= request.POST['profession']
            afiliation=request.POST['afiliation']
            role=request.POST['role']
            password = request.POST["pass"]
            cpassword=request.POST["cpass"]
            if password==cpassword:
             User = user.objects.create_user(formal_title=formal_title,first_name=first_name,last_name=last_name,email=email,phone=phone,profession=prof,afiliation=afiliation,role=role,password=password)
             User.save()
             login(request, User)
             return redirect('CMS:profile')
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
            email=request.POST["email"]
            password=request.POST["pass"]
            user = authenticate(request,email=email,password=password)
            if user is not None:
             login(request, user) 
             return redirect('CMS:profile')
            else:
                raise ValueError("Invalid credentials")
    return render(request, 'login.html')


def profile(request):
    return render(request, 'profile.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('/')