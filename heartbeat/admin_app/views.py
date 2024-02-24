from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from user_app.models import Account
from . models import * 
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json


# Create your views here.

@never_cache
def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin-dashboard')
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email,password)
        user = authenticate(request, email = email, password = password)
        print(user)
        if user is not None and user.is_superadmin:
            login(request, user)
            messages.success(request, 'Successfuly Logged in')
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('admin_login')
    return render(request, 'admin_side/admin_login.html')

@login_required(login_url='admin-login/')
def admin_logout(request):
    logout(request)
    messages.success(request,'Successfuly Logged Out')
    return redirect('user_app:home')

@login_required(login_url='admin-login/')
def all_users(request):
    if request.user.is_authenticated and request.user.is_superadmin :
        # if request.method == 'POST':
    #         search_word = request.POST.get('search-box', '')
    #         data = User.objects.filter(Q(username__icontains=search_word)| Q(email__icontains=search_word)).order_by('id').values()
    #     else:
        data = Account.objects.all().order_by('id').exclude(is_superadmin=True)
        context={'users': data}
        return render(request,"admin_side/users_list.html", context=context)
    return redirect('user_app:signup')


# def activate_user(request, id):
#     current = get_object_or_404(Account, id=id)
#     current.is_active = True
#     current.save()
#     return redirect('all_users')

# def deactivate_user(request, id):
#     current = get_object_or_404(Account, id=id)
#     current.is_active = False
#     current.save()
#     return redirect('all_users')

@login_required(login_url='admin-login/')
def blockuser(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_user_id = data.get('userId')
        print(selected_user_id)

        if selected_user_id:
            try:
                user = Account.objects.get(id=selected_user_id)
                if user.is_blocked:
                    # User is currently blocked, so unblock
                    user.is_blocked = False
                    user.save()
                    message = 'User unblocked successfully'
                else:
                    # User is not blocked, so block
                    user.is_blocked = True
                    user.save()
                    message = 'User blocked successfully'

                return JsonResponse({'success': True, 'message': message})
            except Account.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User not found'})
        else:
            return JsonResponse({'success': False, 'message': 'No user ID provided'})

    return render(request, "admin_side/users_list.html", {})

@login_required(login_url='admin-login/')
def user_details(request):
    user_id = request.GET.get('user_id')
    user = Account.objects.get(id=user_id)
    # address = Address.objects.filter(account=user.id,is_default=True).first()
    # ordered_products = OrderProduct.objects.filter(user=user,ordered=True).order_by('-id')

    context={"user":user}
    #     "user":user,
    #     'address':address,
    #     'ordered_products':ordered_products,
    #     'ordered_products_count':ordered_products.count()
    # }
    return render(request,'admin_side/user_details.html', context)


        

@login_required(login_url='admin-login/')
def admin_dashboard(request):
    if request.user.is_authenticated:
        return render(request,"admin_side/admin_dashboard.html")
    return redirect('admin_login')


def admin_products_list(request):
    return render(request,'admin_side/products_list.html')

def admin_orders(request):
    return render(request,'admin_side/orders.html')

def admin_catagories(request):
    return render(request,'admin_side/categories.html')

# def admin_add_products(request):
#     return render(request,'admin_side/add_product.html')

# def admin_users_list(request):
#     return render(request,'admin_side/users_list.html')

# def admin_logout(request):
#     return render(request,'admin_side/page-account-login.html')

# def admin_dashboard(request):
#     return render(request,'admin_side/base.html')