from django.shortcuts import render, redirect
from cart.models import *
from .models import *
from user_app.models import *
from django.contrib import messages
from decimal import Decimal
from django.contrib.auth.decorators import login_required



# Create your views here.
@login_required
def order_place_cod(request):
    user_id = request.user.id

    payment_methods_instance = PaymentMethod.objects.get(method_name="CASH ON DELIVERY")

    user_instance = Account.objects.get(id=user_id)

    try:
        address = Address.objects.get(is_default=True, account=user_instance)
    except Address.DoesNotExist:
        address = None
        messages.error(request, 'Address not added')

    try:
        cart = Cart.objects.get(user=user_instance)
    except Cart.DoesNotExist:
        # messages.error(request, 'No active cart found')
        return redirect('user_app:shop')  # Redirect to shopping page if no active cart found

    cart_items = CartItem.objects.filter(cart=cart, is_active=True)

    total_with_original_price = 0
    total = 0
    quantity = 0

    for cart_item in cart_items:
        total += cart_item.sub_total()
        total_with_original_price += (cart_item.product.max_price * cart_item.quantity)
        quantity += cart_item.quantity
    total_float = float(total)

    address1 = [address.first_name, address.street_address, address.town_city, address.district, address.state, address.pin_code, address.phone_number]

    payment = Payment.objects.create(user=user_instance, payment_method=payment_methods_instance, amount_paid=total_float, payment_status='SUCCESS')

    draft_order = Order.objects.create(
        user=user_instance,
        shipping_address=address1,
        order_total=total_float,
        is_ordered=True,
        payment=payment,
        grand_total=total_float
    )

    for cart_item in cart_items:
        product = cart_item.product
        product.stock -= cart_item.quantity
        product.save()

    for cart_item in cart_items:
        OrderProduct.objects.create(
            order=draft_order,
            user=user_instance,
            product_variant=cart_item.product.product.product_name,
            product_id=cart_item.product.product.id,
            quantity=cart_item.quantity,
            product_price=float(cart_item.product.sale_price),
            images=cart_item.product.thumbnail_image,
            ordered=True,
        )

    cart_items.delete()
    cart.delete()

    order_details = OrderProduct.objects.filter(order=draft_order)

    context = {
        'order_details': order_details,
        'total_float': total_float,  # Pass total_float to the template
    }

    return render(request, 'user_side/order_success.html', context)

@login_required
def profile_order_details(request, id):
    order = Order.objects.get(id = id)
    order_products1 = OrderProduct.objects.filter(order = order)
    order_products_deliverd = OrderProduct.objects.filter(order = order,order_status = "Delivered")
    
    order_products = OrderProduct.objects.filter(order = order).first()
    product_ispaid = True
    if len(order_products1) == len(order_products_deliverd):
        product_ispaid1 = True
    else:
        product_ispaid1 = False
    for i in order_products1:
        if i.order.payment.is_paid == False:
            product_ispaid = False
    # if order_products.grand_totol < order_products.product_price:
    if order.grand_total < order.order_total:
        
        order_actual_total = 0
        for i in order_products1:
            order_actual_total += i.product_price
        

        context = {
                'order_dtails':order,
                'order_products':order_products1,
                'product_total':order.order_total,
                'grand_total':order.grand_total,
                'product_ispaid':product_ispaid1
            }
    else:
        context = {
            'order_dtails':order,
            'order_products':order_products,
            'order_products':order_products1,
            'grand_total':order.grand_total,
            "product_ispaid":product_ispaid1,
        }

    return render(request,'user_side/profile_order_details.html', context)
@login_required
def cancel_product(request, item_id):
    try:
        ordered_product = OrderProduct.objects.get(id=item_id)
        ordered_product_quantity = ordered_product.quantity

        order = Order.objects.get(id=ordered_product.order.id)
        
        # Access the product_variant attribute and handle AttributeError if it's not an object
        try:
            product_variant = ordered_product.product_variant
            product_variant.stock += ordered_product_quantity
            product_variant.save()
        except AttributeError:
            # Handle the case where product_variant is not an object
            # This could involve fetching the actual Product_Variant instance based on the string value,
            # or handling it in another appropriate way based on your application logic.
            pass

        ordered_product.order_status = "Cancelled User"
        ordered_product.save()

        payment_method = PaymentMethod.objects.get(method_name=order.payment.payment_method.method_name)
        
        return redirect("order:profile_order_details", order.id)
    
    except OrderProduct.DoesNotExist:
        # Handle the case where the OrderProduct with the given id does not exist
        # This could involve redirecting the user to an appropriate page or showing an error message
        pass





@login_required
def return_product(request,item_id):
    ordered_product = OrderProduct.objects.get(id = item_id)
    ordered_product.order_status = "Returned User"
    ordered_product.save()

    order = Order.objects.get(id=ordered_product.order.id)

    product_id = ordered_product.product_id
    product_variant = Product_Variant.objects.get(id = product_id)
    product_variant.stock += ordered_product.quantity
    product_variant.save()

    return redirect("order:profile_order_details", order.id)