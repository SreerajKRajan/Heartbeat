from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('order_place_cod/', views.order_place_cod, name = 'order_place_cod'),  
    path('profile_order_details/<int:id>/', views.profile_order_details, name = 'profile_order_details'), 
    path('cancel_product/<int:item_id>/', views.cancel_product, name='cancel_product'),
    path('return_product/<int:item_id>/', views.return_product, name='return_product'), 
]