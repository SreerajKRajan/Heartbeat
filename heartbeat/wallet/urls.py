from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('wallet/',views.wallet,name='wallet'),
    path('wallet_handler/',views.wallet_handler,name='wallet_handler'),
    # path('wallet_faild/',views.wallet_faild,name='wallet_faild'),
    path('wallet_success/<str:payment_id>/<str:amount>/',views.wallet_success,name='wallet_success'),
]