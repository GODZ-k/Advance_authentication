from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.core.mail import send_mail
from authentication import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage,send_mail
from .tokens import generate_token

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
            myuser=User.objects.create(username=username,
                email=email,
                first_name=fname,
                last_name=lname)

        # save user password

            myuser.set_password(password)
            myuser.is_active=False
            myuser.save()
            messages.success(request,"account created successfully , we have send you confirmation email. please confirm your email first .")

        # welcome mail

            subject = "Welcome to this app"
            message = f'Hi {myuser.first_name}, thank you for registering in this app .'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [myuser.email]
            send_mail( subject, message, email_from, recipient_list,fail_silently=True )

        # Email confirmation Email

            current_site = get_current_site(request)
            confemail_subject = "Confirm your email - django login"
            message2 = render_to_string("email_confirmation.html",
                                        {
                                            'name': myuser.first_name,
                                            'domain':current_site.domain,
                                            'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
                                            'token':generate_token.make_token(myuser),
                                        })


            email=EmailMessage(
                confemail_subject,
                message2,
                settings.EMAIL_HOST_USER,
                [myuser.email],
            )

            email.fail_silently = True
            email.send()


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



def activate(request,uidb64,token):
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        myuser=User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser=None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active=True
        myuser.save()
        login(request,myuser)
        return redirect('home')
    else:
        return render(request,'activation_fail.html')