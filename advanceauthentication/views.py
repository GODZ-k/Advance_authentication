from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
def home(request):
    return render(request, 'authentication/index.html')

def signup(request):
    if request.method == "POST":
        username=request.POST.get('username')
        fname=request.POST.get('fname')
        lname=request.POST.get('lname')
        email=request.POST.get('email')
        password=request.POST.get('password')
        confpassword=request.POST.get('confirmpassword')

        # check username or email already exists or not


        # create user

        if password == confpassword:
            myuser=User.objects.create(username=username,email=email,first_name=fname,last_name=lname)
        # save user password
            myuser.set_password(password)
            myuser.save()
            messages.success(request,"account created successfully")
            return redirect('/signin/')

        messages.error(request,"confirm password does not match")

    return render(request, "authentication/signup.html")

def signin(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        # check user is exist or not
        myuser=User.objects.filter(username=username)

        if not myuser.exists():
            messages.error(request,"user does not exist")
            return redirect('/signin/')
        myuser = authenticate(username=username, password=password)
        if myuser:
            login(request,myuser)
            messages.success(request,"Welcome")
            return redirect("/")
        else:
            messages.error(request,"invalid password")



    return render(request, "authentication/signin.html")

def signout(request):
   logout(request)
   return redirect("/signin/")