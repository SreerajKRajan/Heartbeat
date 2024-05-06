from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.http import JsonResponse
import razorpay
from django.conf import settings
from wallet.models import Wallet,WalletTransaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages



# Create your views here.

@login_required
def wallet(request):
    user = request.user

    if request.method == 'POST':
        amount = int(request.POST.get('amount', 0)) * 100  # Amount in paisa
        client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
        
        payment_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': 'wallet_fund',  # Update as needed
            'payment_capture': 1  # Auto-capture payment
        }

        try:
            payment = client.order.create(data=payment_data)

            return JsonResponse({'success': True,'order_id': payment['id'],'amount': payment['amount'],})
        except Exception as e:
            print(str(e))
            return JsonResponse({'success': False, 'error': str(e)})

    try:
        user_wallet = Wallet.objects.get(user=user)
        wallet_transaction = WalletTransaction.objects.filter(wallet=user_wallet).order_by('-id')
        context = {
            'user': user,
            'user_wallet': user_wallet,
            'wallet_transaction': wallet_transaction,
        }

        return render(request, 'user_side/wallet.html', context)
    except Wallet.DoesNotExist:
        user_wallet = Wallet.objects.create(user=user, balance=0)
        context = {
            'user': user,
            'user_wallet': user_wallet,
        }

        return render(request, 'user_side/wallet.html', context)
    except Exception as e:
        # Handle other exceptions as needed
        return JsonResponse({'success': False, 'error': str(e)})
    


@csrf_exempt
def wallet_handler(request):

    if request.method == "POST":
        try:
            payment_id        = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature         = request.POST.get('razorpay_signature', '')
            amount = request.GET.get('amount', '') 

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
            result = client.utility.verify_payment_signature(params_dict)
            
            if not result :
                return redirect('wallet:wallet_faild')
            else:
                try:

                    return redirect('wallet:wallet_success',payment_id,amount)
                except Exception as e:
                    print("exception:   ",str(e))
            
        except Exception as e:
            print('Exception:', str(e))
            return redirect('wallet:wallet_faild')

    redirect("wallet:wallet")



# def wallet_faild(request):
#     return render(request,'userside/wallet-fail.html')


def wallet_success(request,payment_id,amount):
    user = request.user
    wallet = Wallet.objects.get(user=user)
    
    WalletTransaction.objects.create(
        wallet = wallet,
        transaction_type = "CREDIT",
        wallet_payment_id = payment_id,
        amount = int(amount),
    )
    wallet.balance += int(amount)
    wallet.save()
            

    
    messages.success(request,"Amount added successfully")
    return redirect("wallet_app:wallet")