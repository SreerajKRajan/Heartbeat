from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('cart/', views.cart, name = 'cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name = 'add_cart'),
    path('remove_cart/<int:product_id>/', views.remove_cart, name = 'remove_cart'),
    path('remove_cart_item/<int:product_id>/', views.remove_cart_item, name = 'remove_cart_item'),
    path('checkout/', views.checkout, name = 'checkout'), 

    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('cancel_coupon/', views.cancel_coupon, name='cancel_coupon'),

    ############### Wishlist #########################

    path('wishlist/',views.wishlist, name='wishlist'),
    path('add_wishlist/<int:id>/',views.add_wishlist, name='add_wishlist'),
    path('wishlist_remove/<int:id>/',views.remove_wishlist, name='remove_wishlist'),  
]