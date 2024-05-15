from django.urls import path
from order import views

app_name = 'order'

urlpatterns = [
    path('order_place_cod/', views.order_place_cod, name = 'order_place_cod'),  
    path('profile_order_details/<int:id>/', views.profile_order_details, name = 'profile_order_details'), 
    path('cancel_product/<int:item_id>/', views.cancel_product, name='cancel_product'),
    path('return_product/<int:item_id>/', views.return_product, name='return_product'), 
    path('order_place_razorpay/', views.order_place_razorpay, name='order_place_razorpay'), 
    path('order_success/<razorpay_order_id>/<payment_id>/<signature>/', views.order_success, name='order_success'),
    path('paymentfail/', views.paymentfail, name='paymentfail'),
    path('payment_fail_order/', views.payment_fail_order, name='payment_fail_order'),
    path('checkout_razorpay/', views.checkout_razorpay, name='checkout_razorpay'),
    path('repay_payment/<int:id>/', views.repay_payment, name='repay_payment'),
    path('repayment_handler/', views.repayment_handler, name='repayment_handler'),
    path('repayment_success/<params_dict>/<id>/', views.repayment_success, name='repayment_success'),
    path('get_invoice/<int:id>/', views.get_invoice, name='get_invoice'),
]