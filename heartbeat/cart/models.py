from django.db import models
from user_app.models import Account
from product_management.models import *

# Create your models here.

class Cart(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    coupon = models.ForeignKey(UserCoupon,on_delete=models.SET_NULL,null=True)
    coupon_applied = models.ForeignKey(Coupon,on_delete=models.CASCADE, default = None,null = True)
    coupon_discount = models.IntegerField(default = 0)
    date_added = models.DateField(auto_now_add=True)
    total_after_discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))


    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        if self.coupon_applied is None:
            self.coupon_discount = 0
        super(Cart, self).save(*args,**kwargs)
    

class CartItem(models.Model):
    product = models.ForeignKey(Product_Variant, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.sale_price * self.quantity
    
    def __str__(self):
        return str(self.product)
    

class Wishlist(models.Model):
    user = models.OneToOneField(Account,on_delete=models.CASCADE)
    date_added = models.DateField(auto_now_add=True)
    
    def __str__(self): 
        return str(self.user)
    
    def get_items_count(self):
       return self.wishlistitem_set.filter(is_active=True).count()

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist,on_delete=models.CASCADE)
    product = models.ForeignKey(Product_Variant,on_delete=models.CASCADE, related_name = 'wishlist')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.product)