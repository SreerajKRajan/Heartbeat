from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.cache import never_cache,cache_control
from django.utils import timezone
import datetime
import random
from . models import Account
from django.core.mail import send_mail
from product_management.models import *


# Create your views here.


def shop(request):

    products = Product.objects.all()
    category = Category.objects.all()
    brand    = Brand.objects.all()
    colour   = Colour.objects.all()
    product_variant = Product_Variant.objects.all()
    context ={
        'category': category,
        'brand':brand,
        'products':products,
        'colour': colour,
        'product_variant': product_variant

    }
  
    return render(request, 'user_side/shop.html', context)

def cart(request):
    return render(request, 'user_side/cart.html')

def blog(request):
    return render(request, 'user_side/blog.html')

def about(request):
    return render(request, 'user_side/about.html')

def contact(request):
    return render(request, 'user_side/contact.html')

def product_details(request,product_id):
    product = Product_Variant.objects.get(id = product_id)
    # product_variant = Product_Variant.objects.all()


    return render(request, 'user_side/product_detail.html',{"product":product})

@never_cache
def signup_page(request):
    # if request.user.is_authenticated:
    #     return redirect('home')

    # def send_otp(email):
    # otp_value = str(random.randint(100000, 999999))
    # request.session['otp_session'] = otp_value
    # request.session['otp_timestamp'] = str(timezone.now())
    # request.session['email_session'] = email
    # request.session.modified = True
    # send_mail(
    #     'OTP verification from Heartbeat',
    #     f"Dear User, \n\n One-Time Password (OTP) for verification is:{otp_value}. \n\n Please use above OTP to complete your signup to Heartbeat website",
    #     'heartbeatofficial2820@gmail.com',
    #     [email],
    #     fail_silently=False
    # )


    if request.method == "POST":
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if Account.objects.filter(username = uname).exists():
            messages.warning(request, 'User already exists')
            return redirect('user_app:signup_page')
        
        if ' ' in uname:
            messages.warning(request, 'Username cannot have whitespace')
            return redirect('user_app:signup_page')
        
        if Account.objects.filter(email = email).exists():
            messages.warning(request, 'User already exists')
            return redirect('user_app:signup_page')
        
        print('password before', pass1)
        if ' ' in pass1:
            messages.warning(request, 'Password cannot have whitespaces')
            return redirect('user_app:signup_page')
        print('password after', pass1)

        if not email or '@' not in email:
            messages.warning(request, 'Email is not in correct format')
            return redirect('user_app:signup_page')
        

        if pass1 != pass2:
            messages.warning(request, 'Password is incorrect')
            return redirect('user_app:signup_page')
        
        if len(pass1) < 8:
            messages.warning(request, 'Password should be of 8 character')
            return redirect('user_app:signup_page')
        
        else:
            user = Account.objects.create_user(username = uname, email = email, password = pass1)
            user.is_active = False
            user.is_admin = False
            user.is_superuser = False
            user.is_staff = False
            user.save()

        otp_value = str(random.randint(100000, 999999))
        request.session['otp_session'] = otp_value
        request.session['otp_timestamp'] = str(timezone.now())
        request.session['email_session'] = email
        request.session.modified = True
        send_mail(
            'OTP verification from Heartbeat',
            f"Dear User, \n\n One-Time Password (OTP) for verification is:{otp_value}. \n\n Please use above OTP to complete your signup to Heartbeat website",
            'heartbeatofficial2820@gmail.com',
            [email],
            fail_silently=False
    )
        

        # request.session['username'] = uname
        # request.session['password'] = pass1
        # request.session['email_session'] = email
        # user = User.objects.create_user(username=uname,password=pass1,email=email)
        # user.save()

        
    #     return redirect('user_app:user_otp')
    # return render(request, 'user_side/signup.html')


    #     else:
    #         my_user = User.objects.create_user(uname, email, pass1)
    #         my_user.save()
    #         print(my_user)
    #         return redirect('login')
        
    # return render(request, 'user_side/signup.html')


# def user_otp(request):
    # def send_otp(email):
    #     otp_value = random.randint(100000, 999999)
    #     request.session['otp_session'] = otp_value
    #     request.session['otp_timestamp'] = timezone.now()
    #     request.session['email_session'] = email
    #     request.session.modified = True


        # send_mail(
        #     'OTP verification from Heartbeat',
        #     f"Dear User, \n\n One-Time Password (OTP) for verification is:{otp_value}. \n\n Please use above OTP to complete your signup to Heartbeat website",
        #     'heartbeatofficial2820@gmail.com',
        #     [email],
        #     fail_silently=False
        # )
    
        return render(request,'user_side/otp.html', {'email':email})
    return render(request,'user_side/signup.html')

@never_cache
def resend_otp(request):
    if request.method =="POST":
        email = request.POST.get('email')
        if email:
            if Account.objects.filter(email = email).exists():
                def send_otp(email):
                    otp_value = random.randint(100000, 999999)
                    request.session['otp_session'] = otp_value
                    request.session['otp_timestamp'] = timezone.now()
                    request.session['email_session'] = email
                    request.session.modified = True

                send_otp(email)
                messages.success(request, "OTP has been resent. Check your email.")
            else:
                messages.warning(request, "User with this email does not exist.")

    return redirect('user_app:signup_page')


@never_cache
def otp_verification(request):
    # uname = request.session.get('username')
    # email_session = request.session.get('email')
    # password = request.session.get('password')
    # print(uname)
    # print(email_session)
    if request.method == "POST":
        # uname = request.POST.get('username')
        # email = request.POST.get('email')
        # pass1 = request.POST.get('password1')
                                 
        otp_entered = request.POST.get('otp_entered')
        if 'otp_session' in request.session:
            otp_session = request.session['otp_session']
        if 'email_session' in request.session:

            email = request.session['email_session']
        print(otp_entered,otp_session)

        if str(otp_entered) == str(otp_session):
            customer = Account.objects.get(email = email)
            customer.is_active = True
            customer.save()

            subject = "Successful Login - Heartbeatofficial"
            sender_email = "heartbeatofficial2820@gmail.com"
            message = "Dear Customer,\n\nYour login to Heatbeat was successful.\n\nThank you for choosing Heartbeat."
            send_mail(subject, message, sender_email, [email])
            login(request, customer)
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect('user_app:home')
        else:
            messages.error(request, "Wrong Entry")

    if 'otp_session' in request.session:
        otp_timestamp = request.session.get('otp_timestamp')
        current_time = timezone.now()
        time_difference = current_time - otp_timestamp
        time_difference_minutes = time_difference.total_seconds() / 60

        # If more than 5 minutes have passed, generate and send a new OTP
        # if time_difference_minutes > 5:
        #     def send_otp(email):
        #         otp_value = random.randint(100000, 999999)
        #         request.session['otp_session'] = otp_value
        #         request.session['otp_timestamp'] = timezone.now()
        #         request.session['email_session'] = email
        #         request.session.modified = True

        #     send_otp(email)
        #     messages.warning(request, "OTP expired. A new OTP has been send to your email.")


        context = {'email': email}

    return render(request, 'user_side/otp.html', context)
        #     customer = authenticate(request, username = uname, password = password)
        #     print(customer)
        #     if customer is not None:
        #         login(request, customer)
        #         return redirect('user_app:home')
        #     else:
        #         messages.error(request, "Invalid OTP. Please enter again.")
        #         return redirect('user_app:otp_verification')
        # return render(request, 'user_side:otp.html',{'email': email_session})



@never_cache
def login_page(request):
    if request.user.is_authenticated:
        return redirect('user_app:home')
    if request.method == "POST":
        # uname = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email,password)
        user = authenticate(request, email = email, password = password)
        print(user)
        if user is not None and  user.is_blocked == False and user.is_superadmin == False:
            # user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            # if request.GET.get('next'):
            #     return redirect(request.GET.get('next'))
            # else:
            return redirect('user_app:home')

        elif user is not None and user.is_blocked == True:
            messages.error(request,'You are Blocked!')
            return redirect('user_app:login_page')
            
        else:
            messages.warning(request, "Invalid credentials!!")
            return redirect('user_app:login_page')
    return render(request, 'user_side/login.html')


# @never_cache
def home(request):
   
    # if request.user.is_authenticated:
    #     if request.user.is_superuser:
    #         return redirect('admin')
    #     else:
    #         return render(request, 'user_side/home.html')
    return render(request, 'user_side/home.html')
@never_cache
def forget(request):
    return render(request, 'user_side/forget.html')
@never_cache
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        # messages.success(request, ("You Were Logged Out!"))
    return redirect('user_app:login_page')
