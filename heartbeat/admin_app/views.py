from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from user_app.models import Account
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
from django.db.models import Q
from product_management.models import Category


# Create your views here.

@never_cache
def admin_login(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin_dashboard')
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
            messages.warning(request, "Invalid Credentials")
            return redirect('admin_login')
    return render(request, 'admin_side/admin_login.html')


def admin_dashboard(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        return render(request,"admin_side/admin_dashboard.html")
    return redirect('admin_login')


def admin_logout(request):
    logout(request)
    messages.success(request,'Successfuly Logged Out')
    return redirect('user_app:home')


################# User Management #######################################################

def all_users(request):
    if request.user.is_authenticated and request.user.is_superadmin :
        query = request.GET.get('q')
        if query:
            data = Account.objects.filter(Q(username__icontains = query) | Q(email__icontains = query)).exclude(is_superadmin = True).order_by('id')
        else:    
            data = Account.objects.all().order_by('id').exclude(is_superadmin=True)
        context={'users': data}
        return render(request,"admin_side/users_list.html", context=context)
    return redirect('admin_login')


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

def user_details(request):
    if request.user.is_authenticated and request.user.is_superadmin:
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
    return redirect('admin_login')




################# Category Management #############################################################

def manage_category(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        categories = Category.objects.all().order_by('id')
        categoy_count = categories.count()
    
        context = {
            'categories': categories,
            'category_count': categoy_count
        }
        return render(request, 'admin_side/categorymanagement.html', context)
    return redirect('admin_login')


def add_category(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        if request.method == "POST":
            category_name = request.POST.get('category_name')

            if Category.objects.filter(category_name = category_name).exists():
                messages.warning(request, 'Cqtegory already exists')
                return redirect('add_category')

            category = Category(
                category_name = category_name,
                )
            category.save()
            return redirect('manage_category')
        return render(request, 'admin_side/add_category.html')
    return redirect('admin_login')


def edit_category(request, category_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        category = Category.objects.get(id = category_id)
        context = {'category':category}
        # context = {'categories': categories}
        if request.method == "POST":
            category_name = request.POST.get('category_name')
            category.category_name = category_name
            category.save()

            messages.success(request, 'Category Edited.')
            return redirect('manage_category')
        return render(request, 'admin_side/edit_category.html', context)
    return redirect('admin_login')


################### Category Available ###############################

def list_category(request, category_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        category = Category.objects.get(id = category_id)
        category.is_active = True
        category.save()
        return redirect('manage_category')
    return redirect('admin_login')


################### Category Unavaliable ###############################

def unlist_category(request, category_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        category = Category.objects.get(id = category_id)
        category.is_active = False
        category.save()
        return redirect('manage_category')
    return redirect('admin_login')

        



        



