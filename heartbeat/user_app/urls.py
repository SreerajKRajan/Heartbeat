from django.urls import path
from . import views

app_name = 'user_app'

urlpatterns = [
    path('', views.home, name = 'home'),
    path('login/', views.login_page, name = 'login_page'),
    path('login/<str:provider>/', views.login_page, name='login_page'),
    path('signup/', views.signup_page, name = 'signup_page'),
    path('forgot-password/', views.forgot_password, name = 'forgot_password'),
    path('forgot-otp-verification/', views.forgot_otp_verification, name = 'forgot_otp_verification'),
    path('logout/', views.user_logout, name = 'user_logout'),
    path('otp_verification/', views.otp_verification, name = 'otp_verification'),


    path('shop/', views.shop, name = 'shop'),
    path('user_profile/', views.user_profile, name = 'user_profile'),
    path('address/', views.address, name = 'address'),
    path('add_address/', views.add_address, name = 'add_address'),
    path('delete_address/<int:id>/', views.delete_address, name = 'delete_address'),
    path('edit_address/<int:id>/', views.edit_address, name = 'edit_address'),
    path('resend_otp/', views.resend_otp, name = 'resend_otp'),
    path('product_details/<int:product_id>/', views.product_details, name = 'product_details'),
    path('categories/<int:category_id>/', views.categories, name = 'categories'),
 ]

