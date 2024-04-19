from .models import Cart, CartItem
# from .views import _cart_id

def counter(request):
    current_user = request.user
    if current_user.is_authenticated:
        
        try:
            cart= Cart.objects.get(user=current_user)
        except Cart.DoesNotExist:
            # For anonymous users, use some other logic to identify the cart (if needed)
            cart= Cart.objects.create(user=current_user)

        cart_count = 0
        if 'admin' in request.path:
            return {}
        
        elif 'admin-default' in request.path:
            return {}

        else:
            try:
            
                cart_items = CartItem.objects.all().filter(cart=cart)
                for cart_item in cart_items:
                    cart_count += cart_item.quantity

            except Cart.DoesNotExist:
                cart_count=0
    else:
        cart_count=0

    
    return dict(cart_count=cart_count)  #, cart_items=cart_items