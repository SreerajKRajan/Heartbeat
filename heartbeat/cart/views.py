from django.shortcuts import render,redirect
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from .models import *
from product_management.models import *
from user_app.models import *
from django.http import JsonResponse
# from orders.models import Payment
from django.contrib import messages
from django.core.cache import cache
from django.http import JsonResponse
import json
from django.utils import timezone
from decimal import Decimal
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
# Create your views here.

@login_required(login_url='user_app:login_page')
def add_cart(request, product_id):
    current_user = request.user
    product = Product_Variant.objects.get(id=product_id)
    try:
        cart= Cart.objects.get(user=current_user)
    except Cart.DoesNotExist:
        # For anonymous users, use some other logic to identify the cart (if needed)
        cart= Cart.objects.create(user=current_user)
    # try:
    #     cart = Cart.objects.get(id=_cart_id(request))
    # except Cart.DoesNotExist:
    #    pass
    # cart.save()

    try:
        cart_item = CartItem.objects.get(product=product , cart=cart) #,user = current_user
        if cart_item.quantity < product.stock:
            cart_item.quantity +=1
            cart_item.save()
        else:
            messages.error(request,"No more stock available for this product")
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity = 1,
            # user = current_user
        )
        cart_item.save()
        
    return redirect('cart:cart')
    


def cart(request, total=0, quantity=0, cart_items=None):
    current_user = request.user
    if current_user.is_authenticated:
        try:
            cart= Cart.objects.get(user=current_user)
        except Cart.DoesNotExist:
            # For anonymous users, use some other logic to identify the cart (if needed)
            cart= Cart.objects.create(user=current_user)


        
        cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('id') #,user = current_user
        for cart_item in cart_items:
            total += (cart_item.product.sale_price * cart_item.quantity)
            quantity += cart_item.quantity

        context={
            'total': total,
            'quantity' : quantity,
            'cart_items' : cart_items
        }
    else:
        context = {}
    
    return render(request, 'user_side/cart.html', context)


def remove_cart(request, product_id):
    current_user = request.user
    try:
        cart= Cart.objects.get(user=current_user)
    except Cart.DoesNotExist:
        pass

    product = get_object_or_404(Product_Variant, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity>1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart:cart')


def remove_cart_item(request, product_id):
    current_user = request.user
    try:
        cart= Cart.objects.get(user=current_user)
    except Cart.DoesNotExist:
        pass

    product = get_object_or_404(Product_Variant, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart:cart')


def checkout(request, total=0, quantity=0, cart_items=None):
    current_user = request.user
    try:
        cart= Cart.objects.get(user=current_user)
    except Cart.DoesNotExist:
        pass

    cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('id') #,user = current_user
    print('cart_items checkout',cart_items)
    for cart_item in cart_items:
        total += (cart_item.product.sale_price * cart_item.quantity)
        print('  checkout total checkout',total)
        quantity += cart_item.quantity
        print('  checkout quantity checkout',quantity)
        
    try:
        address = Address.objects.filter(account=current_user)
        
    except Address.DoesNotExist:
        address = None

    print('  checkout total',total,'  checkout quantity',quantity)

    for cart_item in cart_items:
        if cart_item.quantity <= cart_item.product.stock:
            context={
                'total': total,
                'quantity' : quantity,
                'cart_items' : cart_items,
                'address':address,
            }
            return render(request,'user_side/checkout.html',context)

        else:
            
            messages.error(request,f"Insufficient quantity. Reduce quantity to {cart_item.product.stock} to proceed!!")
            return redirect('cart:cart')