from django.urls import path
from . import views

app_name = 'user_app'

urlpatterns = [
    path('', views.home, name = 'home'),
    path('login/', views.login_page, name = 'login_page'),
    path('login/<str:provider>/', views.login_page, name='login_page'),
    path('signup/', views.signup_page, name = 'signup_page'),
    path('forget/', views.forget, name = 'forget'),
    path('logout/', views.user_logout, name = 'user_logout'),
    path('otp_verification/', views.otp_verification, name = 'otp_verification'),
    path('shop/', views.shop, name = 'shop'),
    path('resend_otp/', views.resend_otp, name = 'resend_otp'),
    path('product_details/<int:product_id>/', views.product_details, name = 'product_details'),
    path('categories/<int:category_id>/', views.categories, name = 'categories'),
 ]

