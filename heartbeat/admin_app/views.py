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
from decimal import Decimal
from product_management.models import Category, Product
from django.db.models import Sum
from django.db.models.functions import Coalesce
from datetime import datetime as dt
from django.utils import timezone

from order.models import *
from django.core.paginator import EmptyPage,PageNotAnInteger, Paginator
from django.urls import reverse
from user_app.models import Address

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
        orders = Order.objects.exclude(payment__payment_status="FAILED").order_by("-created_at")
        if request.method == 'POST':
            # Get the form data
            date = request.POST.get('date')
            payment_status = request.POST.get('payment_status')
            if date and payment_status:
                orders = Order.objects.filter(created_at__contains=date,payment__payment_status = payment_status)
                print("order_product_status",orders)

                print("YES date",date)
            elif payment_status:
                print("yes paymant status",payment_status)
                orders = Order.objects.filter(payment__payment_status = payment_status)
                print(orders)

            elif date:
                orders = Order.objects.filter(created_at__contains=date)

        current_year = dt.now().year
        current_month = dt.now().month

        total_earnings = OrderProduct.objects.filter(
        created_at__year=current_year,
        created_at__month=current_month,
        order_status='Delivered'
        ).aggregate(total_earnings=Sum('grand_total'))

        # If there are no earnings for the month, set total_earnings to 0
        total_earnings = total_earnings['total_earnings'] if total_earnings['total_earnings'] else 0

        top_selling_products = OrderProduct.objects.filter(order_status='Delivered') \
        .values('product_variant', 'product_id') \
        .annotate(total_quantity=Coalesce(Sum('quantity'), 0)) \
        .order_by('-total_quantity')[:10]

        top_10_product = []
        top_selling_brands = []
        top_selling_categories = []
        for i in top_selling_products:
            product_variant = i['product_variant']
            product_name = product_variant[10:] if len(product_variant) > 10 else product_variant
            product = Product.objects.get(product_name__contains=product_name)
            top_10_product.append(product)
            top_selling_brands.append(product.brand) 
            top_selling_categories.append(product.category)

        top_selling_brands = list(set(top_selling_brands))
        top_selling_categories = list(set(top_selling_categories))

        top_10_product = list(set(top_10_product))

        payment = Payment.objects.distinct("payment_status")
        categories = Category.objects.filter(is_active = True)
        order_products = OrderProduct.objects.filter(order_status = "Delivered")
        products = Product.objects.all()
        categories = Category.objects.all()

        revenue = 0
        for i in order_products:
            revenue += i.grand_total


        chart_month = []
        new_users = []
        orders_count= []
        for month in range(1, 13):
            c = 0
            user_count = 0
            order_c = 0
            for item in OrderProduct.objects.filter(order_status="Delivered"):
                if item.created_at.month == month:
                    c += item.quantity
                    order_c += 1

            chart_month.append(c)
            for user in Account.objects.all():
                if user.joined_on.month == month:
                    user_count += 1
            new_users.append(user_count)

            # Count orders with payment status "SUCCESS" for the month
            for order in Order.objects.filter(payment__payment_status="SUCCESS", created_at__month=month):
                order_c += 1

            orders_count.append(order_c)


        total_orders = len(orders)
        paginator = Paginator(orders, 6)
        page = request.GET.get('page')
        paged_orders = paginator.get_page(page)
        context = {
            "paged_orders":paged_orders,
            "revenue":revenue,
            "total_orders":total_orders,
            "total_products":len(products),
            "total_categories":len(categories),
            "chart_month":chart_month,
            "new_users":new_users,
            "orders_count":orders_count,
            'categories':categories,
            'payment':payment,
            "top_selling_products":top_10_product,
            "top_selling_brands":top_selling_brands,
            "top_selling_categories":top_selling_categories,
            "total_earnings":total_earnings,

        }
        return render(request,"admin_side/admin_dashboard.html", context)
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

        
############## Order Management ##########################


def order_list(request):
    if request.user.is_authenticated and request.user.is_superadmin:

        order_list = OrderProduct.objects.all().order_by("-created_at")
        order = Order.objects.all().order_by("-created_at")

        paginator = Paginator(order, 6)
        page = request.GET.get('page')
        paged_orders = paginator.get_page(page)


        context = {
            "paged_orders":paged_orders,
            'order':order,
        }
        return render(request,'admin_side/order_list.html', context)
    return redirect('admin_login')


def order_details(request, user_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        user = Account.objects.get(id=user_id)

        orders = OrderProduct.objects.filter(user__id=user.id).order_by("-created_at")
        order_products_calc = OrderProduct.objects.filter(user__id=user.id, order_status__in=["New", "Accepted", "Delivered"], order__payment__payment_status__in=["SUCCESS", "PENDING"]).order_by("-created_at")
        order = Order.objects.filter(user_id=user.id)
        total_user_orders = Order.objects.filter(user=user_id)

        try:
            user_address = Address.objects.get(is_default=True, account=user)
        except Address.DoesNotExist:
            user_address = None
        
        total_product_price = Decimal(0)
        grant_total = Decimal(0)

        for i in order_products_calc:
            if i.grand_total is not None:
                grant_total += i.grand_total
            total_product_price += i.product_price

        context = {
            "orders": orders,
            "order": order,
            "user_address": user_address,
            "user": user,
            "grant_total": grant_total,
            "total_product_price": total_product_price
        }

        return render(request, 'admin_side/order_details.html', context)
    return redirect('admin_login')


def change_order_status(request, order_id, status, user_id):
    if request.user.is_authenticated and request.user.is_superadmin:

        order_product = get_object_or_404(OrderProduct, id=order_id)

        order_product.order_status = status
        order_product.save()
        if status == "Cancelled Admin":
            order = Order.objects.get(order_number = order_product.order)

        elif status == "Delivered":
            order = Order.objects.get(order_number = order_product.order)
            if order.payment.payment_method.method_name == "CASH ON DELIVERY":
                order_product.is_paid = True
                order_product.save()
                order.payment.amount_paid = order_product.grand_total
                order.save()


        # Redirect to some page after changing status
        return redirect(reverse('order_details', kwargs={'user_id': user_id}))
    return redirect('admin_login')


def order_list_details(request,id):
    if request.user.is_authenticated and request.user.is_superadmin:
        order = Order.objects.get(id = id)
        order_products = OrderProduct.objects.filter(order = order)
        user_id = order.user.id
        user = Account.objects.get(id = user_id)

        try:
            user_address = Address.objects.get(is_default = True, account = user)
        except:
            user_address = None
        total_product_price = 0
        grant_total = 0
        discount = 0
        for i in order_products:
            total_product_price += i.grand_total
        if total_product_price > order.order_total:
            order_total =  order.order_total
            coupon_discount = total_product_price-order_total
        shipping_address = order.shipping_address
        try:
            context={
                'order':order,
                'order_products':order_products,
                'user':user,
                'shipping_address':shipping_address,
                'coupon_discount':coupon_discount,
                'order_total':order_total,
                'total_product_price':total_product_price
            }
        except:
            context={
                'order':order,
                'order_products':order_products,
                'user':user,
                'shipping_address':shipping_address,
                'total_product_price':total_product_price
            }


        return render(request,'admin_side/order_list_details.html',context)
    return redirect('admin_login')

import datetime

def sales_report(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        start_date_value = ""
        end_date_value = ""
        order_products = OrderProduct.objects.none()  # Initialize as empty queryset
        
        try:
            orders = Order.objects.filter(is_ordered=True).order_by('-created_at')
            order_products = OrderProduct.objects.filter(order__payment__payment_status__in=["SUCCESS"], order_status__in=["Delivered", "Accepted", "New"])

            total_amount = 0
            for i in order_products:
                total_amount += i.grand_total

        except Exception as e:
            print("its exception", str(e))

        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            start_date_value = start_date
            end_date_value = end_date
            if start_date and end_date:
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

                # Convert to timezone-aware datetime objects
                start_date = timezone.make_aware(start_date)
                end_date = timezone.make_aware(end_date)

                order_products = order_products.filter(created_at__range=(start_date, end_date))
                total_amount = 0
                for i in order_products:
                    if i.grand_total is not None:
                        total_amount += i.grand_total
    
        context = {
            'orders': order_products,
            'start_date_value': start_date_value,
            'end_date_value': end_date_value,
            'total_amount': total_amount
        }

        return render(request, 'admin_side/sales_report.html', context)
    return redirect('admin_login')







        



