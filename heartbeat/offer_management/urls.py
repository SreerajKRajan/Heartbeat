from django.urls import path
from . import views

app_name = 'offer_management'

urlpatterns = [
    path('referral_offer/', views.referral_offer, name = 'referral_offer'),  
    path('change_offer_status/<int:id>/', views.change_offer_status, name = 'change_offer_status'), 
    path('delete_referral_offer/<int:id>/', views.delete_referral_offer, name='delete_referral_offer'),
]