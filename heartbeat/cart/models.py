from django.db import models
from user_app.models import Account
from product_management.models import Product_Variant

# Create your models here.

class Cart(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    

class CartItem(models.Model):
    product = models.ForeignKey(Product_Variant, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.sale_price * self.quantity
    
    def __str__(self):
        return str(self.product)