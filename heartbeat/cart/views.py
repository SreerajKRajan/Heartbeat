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
from django.views.decorators.http import require_POST
from django.utils import timezone
from decimal import Decimal
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from wallet.models import Wallet

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
        
    return redirect(request.META.get('HTTP_REFERER', '/'))
    


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

    try:
        address = Address.objects.filter(account=current_user)
        
    except Address.DoesNotExist:
        address = None

    print('  checkout total',total,'  checkout quantity',quantity)

    try:
        user_wallet = Wallet.objects.get(user=current_user)
    except:
        pass

    cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('id') #,user = current_user
    print('cart_items checkout',cart_items)

    if cart.coupon_applied != None:

        for cart_item in cart_items:
            total += (cart_item.product.sale_price * cart_item.quantity)
            print('  checkout total checkout',total)
            quantity += cart_item.quantity
            print('  checkout quantity checkout',quantity)
        total -= cart.coupon_discount
        coupens = Coupon.objects.filter(is_expired = False)
        context = {
            'total':total,
            'quantity':quantity,
            'cart_items':cart_items,
            'coupens':coupens,
            'coupon_discount':cart.coupon_discount,
        }
        return render(request,'user_side/checkout.html',context)

    else:    
        for cart_item in cart_items:
            total += (cart_item.product.sale_price * cart_item.quantity)
            quantity += cart_item.quantity
        coupens = Coupon.objects.filter(is_expired = False)
        if cart_item.quantity <= cart_item.product.stock:
            context={
                'total': total,
                'quantity' : quantity,
                'cart_items' : cart_items,
                'address': address,
                'coupens': coupens,
                'user_wallet': user_wallet,
            }
            return render(request,'user_side/checkout.html',context)
        else:
            messages.error(request,f"Insufficient quantity. Reduce quantity to {cart_item.product.stock} to proceed!!")
            return redirect('cart:cart')
        

@require_POST
@login_required
def apply_coupon(request):
    if request.method == "POST":
        discount_amount = 0 

        data = json.loads(request.body)
        coupon_code = data.get('coupencode')

        try:
            # Attempt to get the Coupon object based on the provided coupon code
            coupon = Coupon.objects.get(coupon_code=coupon_code)

            if coupon.is_expired == False:
                cart_item_instance= CartItem.objects.filter(cart__user=request.user).first()
                cart_item_id = cart_item_instance.id
                cart_item = CartItem.objects.get(id = cart_item_id)
                try:

                    cart = Cart.objects.get(cart_id=cart_item.cart)


                    cart.coupon_applied = coupon
                    cart_item_instance= CartItem.objects.filter(cart__user=request.user)
                    total = 0
                    for cart_item in cart_item_instance:
                        total += cart_item.sub_total()
                    total = Decimal(total)

                    coupon_discount = Decimal(coupon.discount_percentage)
                    discount_amount = (total * coupon_discount) / Decimal(100)
                    total_after_discount = total - discount_amount
                except Exception as e:
                    
                    print("exception cart",str(e))


                try:
                    user_coupon = UserCoupon.objects.get(coupon = coupon, user = request.user)
                except Exception as e:
                    
                    print("exception usercoupon",str(e))
                    user_coupon = UserCoupon.objects.create(user = request.user, coupon = coupon, usage_count = 0)
                if user_coupon.apply_coupon() and total >= float(coupon.minimum_amount):
                    cart.coupon_discount = int(discount_amount)
                    cart.save()
                    request.session['coupon_code'] = coupon_code
                    data={'discount_amount':discount_amount,'discount':coupon.discount_percentage,'success':'Coupon Applied','total':total_after_discount,'coupon_code':coupon_code}
                    return JsonResponse(data,status=200)
                else:
                    if coupon.expire_date < timezone.now().date():
                        data={'error':'Coupon expired'}

                        return JsonResponse(data)
                    elif total < float(coupon.minimum_amount):
                        data={'error':'Minimum amount required'}

                        return JsonResponse(data)
                    elif coupon.total_coupons == 0:
                        data={'error':'Coupon not available'}

                        return JsonResponse(data)
                    
                    elif user_coupon.apply_coupon() == False:
                        data={'error':'Maximum Uses Reached'}
                        return JsonResponse(data)


                    data={'error':'Maximum uses of the coupon reached'}

                    return JsonResponse(data,status=500)


            else:
                data = {'error': 'Coupon is Expired'}
                return JsonResponse(data, status=200)       
        except Coupon.DoesNotExist:
            # Handle the case where the coupon does not exist
            data = {'error': 'Coupon does not exist'}
            return JsonResponse(data, status=200)
    

def cancel_coupon(request):
    cart_item_instance= CartItem.objects.filter(user=request.user).first()
    cart_item_id = cart_item_instance.id
    cart_item = CartItem.objects.get(id = cart_item_id)

    cart = Cart.objects.get(cart_id=cart_item.cart)
    cart.coupon_discount = 0
    cart.coupon_applied = None
    cart.save()
    messages.success(request,"coupen deleted")
    return redirect("cart:cart")
        


def wishlist(request):
    user_wishlist = None
    if request.user.is_authenticated:
        user_id = request.user.id
        user = Account.objects.get(id = user_id)
        try:
            user_wishlist = Wishlist.objects.get(user=user)
        except:
            user_wishlist = Wishlist.objects.create(user=user)

    wishlist_items = WishlistItem.objects.filter(wishlist=user_wishlist)

    context = {
       'wishlist_items':wishlist_items ,
    }
    return render(request,'user_side/wishlist.html',context) 

def add_wishlist(request,id):
    print("gggggg")
    user_id = request.user.id
    user = Account.objects.get(id = user_id)
    product_variant = Product_Variant.objects.get(id=id)

    try:
        user_wishlist = Wishlist.objects.get(user=user)
    except:
        user_wishlist = Wishlist.objects.create(user=user)

    wishlist_items = WishlistItem.objects.filter(wishlist=user_wishlist,product = product_variant)

    if not wishlist_items:
       WishlistItem.objects.create(wishlist=user_wishlist,product = product_variant)
       messages.success(request,'Item is added to your wishlist')
    else:
        messages.error(request,'Item is already in your wishlist')
    return redirect(request.META.get('HTTP_REFERER', '/'))



def remove_wishlist(request,id):
    user_id = request.user.id
    user = Account.objects.get(id = user_id)
    product_variant = Product_Variant.objects.get(id=id)
    user_wishlist = Wishlist.objects.get(user=user)
    wishlist_items = WishlistItem.objects.get(wishlist=user_wishlist,product = product_variant)
    wishlist_items.delete()
    return redirect('cart:wishlist')