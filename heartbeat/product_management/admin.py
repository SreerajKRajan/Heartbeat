from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(Colour)
admin.site.register(Product_Variant)
admin.site.register(Additional_Product_Image)
admin.site.register(Coupon)
admin.site.register(UserCoupon)
