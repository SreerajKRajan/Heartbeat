from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.cache import never_cache,cache_control
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
import datetime
import random
from . models import *
from django.shortcuts import get_object_or_404
# from django.db.models import Q
from django.core.mail import send_mail
from product_management.models import *
from order.models import *
from django.http import JsonResponse
import json


# Create your views here.

def shop(request):
    query = request.GET.get('q')
    products = Product.objects.filter(is_available=True)
    category = Category.objects.filter(is_active=True)
    brand = Brand.objects.all()
    colour = Colour.objects.all()

    dicti = {}

    if query:
        # If there's a search query, filter products based on the existence of any related variants that match the query
        products = products.filter(
            Q(product_name__icontains=query) |
            Q(brand__brand_name__icontains=query) |
            Q(category__category_name__icontains=query)
        ).distinct()

    for product in products:
        product_variant = product.products.first()  # Get the first product variant related to the product

        if product_variant:
            variant_images = Additional_Product_Image.objects.filter(product_variant=product_variant)
            dicti[product_variant] = list(variant_images)

    context ={
        'category': category,
        'brand': brand,
        'products': products,
        'colour': colour,
        'product_variant': dicti
    }

    return render(request, 'user_side/shop.html', context)




def categories(request,category_id):
    category = Category.objects.get(id = category_id)
    product_variant = 0

    product_variant = Product_Variant.objects.filter(is_active = True, product__category = category, product__is_available = True)
    # for i in product_variant:
    #     print("PPPPPP",i.product.product_name)
    # print("product variant",product_variant)
    cat = Category.objects.filter(is_active = True)
    context = {"category": cat,
               "product_variant":product_variant,
               }
    return render(request, 'user_side/shop.html', context)


def product_details(request, product_id):
    product = Product_Variant.objects.get(id=product_id)
    p_id = product.product_id
    product_variant_select = Product_Variant.objects.filter(product_id=p_id)
    variant_images = Additional_Product_Image.objects.filter(product_variant=product)

    # Get related products based on the category of the current product
    related_products = Product_Variant.objects.filter(
        product__category=product.product.category  # Filter products by the same category
    ).exclude(id=product_id)  # Exclude the current product from related products

    
    for i in product_variant_select:
        i.apply_category_offer_discount()


    print("product check",product)

    context = {
        "product": product,
        'variant_images': variant_images,
        'product_variant_select': product_variant_select,
        'related_products': related_products  # Pass related products to the template
    }
    return render(request, 'user_side/product_detail.html', context)

def user_profile(request):
    if request.user.is_authenticated:
        user = request.user
        user_address = Address.objects.filter(account=user)
        context = {
            'user': user,
            'user_address': user_address
        }

        return render(request, 'user_side/user_profile.html', context)
    return redirect("user_app:login_page")

@login_required
@never_cache 
def address(request):
    user = request.user.id
    user_address = Address.objects.filter(account=user).order_by('-created_at')
    user_detail= Account.objects.filter(id=user)
    # order_dtails=OrderProduct.objects.filter(user=user).count()

   
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_address_id = data.get('addressId')

        # print(selected_address_id)
        if selected_address_id:
            try:
                selected_address = Address.objects.get(pk=selected_address_id)
                selected_address.is_default = True
                selected_address.save()

                # Update other addresses to set is_default=False
                Address.objects.filter(account=user).exclude(pk=selected_address_id).update(is_default=False)

                return JsonResponse({'success': True, 'message': 'Address set as default successfully'})
            except Address.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Selected address not found'})
        else:
            return JsonResponse({'success': False, 'message': 'No address ID provided'})

    context = {'user_address': user_address,
               'user': user_detail,
            #    'order_dtails' : order_dtails
            }

        
    return render(request,'user_side/address.html',context)


@login_required
@never_cache
def profile_orders(request):
    current_user = request.user
    orders = Order.objects.filter(user=current_user).order_by("-created_at")
    
    # Initialize an empty list to store order products
    order_products = []

    for order in orders:
        # Get the order products for each order
        products_for_order = OrderProduct.objects.filter(order=order)
        order_products.append(products_for_order)

    for order in orders:
        if order.payment:
            print(order.payment.payment_method.method_name)
        else:
            print("No payment found for order #", order.order_number)
    
    
    for order, order_product_list in zip(orders, order_products):
        if order.payment.payment_method == "CASH ON DELIVERY":
            all_delivered = all(product.order_status == "Delivered" for product in order_product_list)
            if all_delivered:
                order.payment.payment_status = "SUCCESS"
            else:
                order.payment.payment_status = "PENDING"
            order.save()

    # Paginate the orders
    paginator = Paginator(orders, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)    

    context = {
        'orders': paged_products,
        'order_products': order_products
    }
    return render(request, 'user_side/profile_orders.html', context)


def add_address(request):
    if request.method == "POST":
        first_name       = request.POST.get('first_name')
        last_name        = request.POST.get('last_name')
        phone_number     = request.POST.get('phone_number')
        town_city        = request.POST.get('town_city')
        street_address   = request.POST.get('street_address')
        district         = request.POST.get('district')
        state            = request.POST.get('state')
        pin_code         = request.POST.get('pin_code')

        user = request.user
        address = Address.objects.create(account=user,first_name=first_name,last_name=last_name,phone_number=phone_number,town_city=town_city,street_address=street_address,district=district,state=state,pin_code=pin_code)
        make_default = request.POST.get('make_default')
        is_default = make_default == 'on'
        address.is_default = is_default
        address.save()
        return redirect('user_app:address')
        
    return render(request, 'user_side/add_address.html')

@login_required
@never_cache
def edit_address(request, id):
    user = request.user
    address = get_object_or_404(Address, id=id)
    
    if request.method == 'POST':

        address.first_name = request.POST.get('first_name')
        address.last_name = request.POST.get('last_name')
        address.phone_number = request.POST.get('phone_number')
        address.street_address = request.POST.get('street_address')
        address.town_city = request.POST.get('town_city')
        address.district = request.POST.get('district')
        address.state = request.POST.get('state')
        address.pin_code = request.POST.get('pin_code')
        address.save()


        return redirect('user_app:address')

    context = {
        'address': address
    }
    return render(request, 'user_side/edit_address.html', context)



@login_required
@never_cache
def delete_address(request, id):

    addresses = get_object_or_404(Address, id=id)
    addresses.delete()
    
    return redirect('user_app:address')


@never_cache
def signup_page(request):
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
        
        if not all([uname, pass1, pass2, email]):
            messages.warning(request, "Please fill the all fields")
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
            messages.warning(request, 'Password should be of 8 characters')
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
    
        return render(request,'user_side/otp.html', {'email':email})
    return render(request,'user_side/signup.html')



@never_cache
def resend_otp(request):
    if request.method == "POST":
        # Retrieve the email from the session
        email = request.session.get('email_session')
        if email:
            # Generate a new OTP value
            new_otp_value = str(random.randint(100000, 999999))

            # Send OTP via email
            subject = "Resend OTP - Heartbeatofficial"
            sender_email = "heartbeatofficial2820@gmail.com"
            message = f"Dear Customer,\n\nYour new OTP for Heartbeat is: {new_otp_value}\n\nThank you for choosing Heartbeat."
            send_mail(subject, message, sender_email, [email])

            # Update session with the new OTP value
            request.session['otp_session'] = new_otp_value
            request.session['otp_timestamp'] = str(timezone.now())
            request.session.modified = True

            return JsonResponse({'status': 'success'})  # Return success JSON response
        else:
            return JsonResponse({'status': 'error', 'message': 'Email not found in session.'})  # Return error JSON response

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})  # Return error JSON response




@never_cache
def otp_verification(request):
    uname = request.session.get('username')
    email_session = request.session.get('email')
    password = request.session.get('password')
    print(uname)
    print(email_session)
    if request.method == "POST":
        otp_entered = request.POST.get('otp_entered')
        otp_session = request.session.get('otp_session')
        email = request.session.get('email_session')
        print(otp_entered, otp_session)

        if str(otp_entered) == str(otp_session):
            customer = Account.objects.get(email=email)
            customer.is_active = True
            customer.save()

            # Use authenticate with request, username, and password
            user = authenticate(request, email=email, password=password)
            
            # Use the authenticated user to log in
            if user:
                login(request, user)

            subject = "Successful Login - Heartbeatofficial"
            sender_email = "heartbeatofficial2820@gmail.com"
            message = "Dear Customer,\n\nYour login to Heartbeat was successful.\n\nThank you for choosing Heartbeat."
            send_mail(subject, message, sender_email, [email])

            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect('user_app:login_page')
        else:
            messages.warning(request, "Wrong Entry")

    if 'otp_session' in request.session:
        otp_timestamp_str  = request.session.get('otp_timestamp')
        otp_timestamp = timezone.datetime.strptime(otp_timestamp_str, "%Y-%m-%d %H:%M:%S.%f%z")
        current_time = timezone.now()
        time_difference = current_time - otp_timestamp
        time_difference_minutes = time_difference.total_seconds() / 60

    return render(request, 'user_side/otp.html', {'email': email})




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
            messages.warning(request,'You are Blocked!')
            return redirect('user_app:login_page')
            
        else:
            messages.warning(request, "Invalid credentials!!")
            return redirect('user_app:login_page')
    return render(request, 'user_side/login.html')



@never_cache
def home(request):
    if request.user.is_authenticated:
        # Check if the user is blocked
        if request.user.is_blocked:
            logout(request)  # Log out the user
            return redirect('user_app:login_page')
        
    products = Product.objects.filter(is_available=True)
    category = Category.objects.filter(is_active=True)
    brand    = Brand.objects.all()
    colour   = Colour.objects.all()

    dicti = {}

    for product in products:
        product_variant = Product_Variant.objects.filter(product=product, is_active = True).order_by("created_at").first()

        if product_variant:
            variant_images = Additional_Product_Image.objects.filter(product_variant=product_variant)
            dicti[product_variant] = list(variant_images)

    # print(dicti)

    context ={
        'category': category,
        'brand':brand,
        'products':products,
        'colour': colour,
        'product_variant': dicti

    }
    
    return render(request, 'user_side/home.html', context)


@never_cache
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        if not all([email,pass1, pass2]):
            messages.warning(request, "Please fill the all fields")
            return redirect('user_app:forgot_password')

        if pass1 != pass2:
            messages.warning(request, "Password is incorrect")
            return redirect('user_app:forgot_password')
        if len(pass1) < 8:
            messages.warning(request, "Password should be of 8 characters")
            return redirect('user_app:forgot_password')
        if ' ' in pass1:
            messages.warning(request, 'Password cannot have whitespaces')
            return redirect('user_app:forgot_password')
        
        if Account.objects.filter(email = email).exists():
            otp_value = str(random.randint(100000, 999999))
            request.session['otp_session'] = otp_value
            request.session['email_session'] = email
            request.session['pass_session'] = pass1
            request.session.modified = True

            send_mail(
                'OTP verification from Heartbeat',
                f"Dear User, \n\n One-Time Password (OTP) for verification is:{otp_value}. \n\n Please use above OTP to complete your reset password",
                "heartbeatofficial2820@gmail.com",
                [email],
                fail_silently=False
            )
            return render(request, "user_side/forgot_otp.html", {'email': email})
        else:
            messages.warning(request, "User does not exists with this email address")
            return redirect('user_app:forgot_password')
    return render(request,'user_side/forgot_password.html')


@never_cache
def forgot_otp_verification(request):
    email_session = request.session.get('email_session')
    pass_session = request.session.get('pass_session')
    if request.method == "POST":
        otp_entered = request.POST.get('otp_entered')
        otp_session = request.session.get('otp_session')

        if str(otp_entered) == str(otp_session):
            new_pass = Account.objects.get(email = email_session)
            new_pass.set_password(pass_session)
            new_pass.save()
            print("Password updated successfully")
            return redirect('user_app:login_page')
        else:
            messages.warning(request, "Wrong Entry")
            return render(request, 'user_side/forgot_otp.html')
    return render(request, 'user_side/forgot_otp.html')


@never_cache
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        # messages.success(request, ("You Were Logged Out!"))
    return redirect('user_app:login_page')

def cart(request):      
    return render(request, 'user_side/cart.html')

def blog(request):
    return render(request, 'user_side/blog.html')

def about(request):
    return render(request, 'user_side/about.html')

def contact(request):
    return render(request, 'user_side/contact.html')
