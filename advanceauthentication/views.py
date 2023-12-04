from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.core.mail import send_mail
from authentication import settings

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

        # check username or email already exists or not and check username length and check it is alphanumeric or not

        if User.objects.filter(username=username).exists():
            messages.error(request," username is already exists")
            return redirect('/signup/')

        elif User.objects.filter(email=email).exists():
            messages.error(request," email is already exists")
            return redirect('/signup/')

        elif len(username)>10:
            messages.warning(request," username must be at least 10 characters")

        elif not username.isalnum():
            messages.error(request," username must be alpha numeric")
            return redirect('/signup/')

        # create user

        elif password == confpassword:
            myuser=User.objects.create(username=username,email=email,first_name=fname,last_name=lname)
        # save user password
            myuser.set_password(password)
            myuser.save()
            messages.success(request,"account created successfully , we have send you confirmation email. please confirm your email first .")

        # welcome mail
            subject = "Welcome to this app"
            message = f'Hi {myuser.first_name}, thank you for registering in this app .'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [myuser.email]
            send_mail( subject, message, email_from, recipient_list,fail_silently=True )

            return redirect('/signin/')

        else:
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
        if myuser := authenticate(username=username, password=password):
            login(request,myuser)
            messages.success(request,f'welcome {username}')
            return redirect("/")
        else:
            messages.error(request,"invalid password")



    return render(request, "authentication/signin.html")

def signout(request):
   logout(request)
   return redirect("/signin/")