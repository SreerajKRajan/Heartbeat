
from django.shortcuts import render, redirect
from .models import ReferralOffer, ReferralUser
from django.contrib import messages
import string
import random
from decimal import Decimal


def referral_offer(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        if request.method == 'POST':
            expire_date = request.POST.get('expire_date')
            amount = request.POST.get('amount')
            limit = request.POST.get('limit')
            is_active = request.POST.get('is_active', False)
            amount = Decimal(amount)
            # Convert is_active to boolean
            is_active = True if is_active == 'on' else False

            try:
                # Create the ReferralOffer object
                ReferralOffer.objects.create(
                    expire_date=expire_date,
                    amount=amount,
                    limit=limit,
                    is_active=is_active
                )
                messages.success(request, 'Referral Offer created successfully.')
                return redirect('offer_management:referral_offer')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
                return redirect('offer_management:referral_offer')

        referral_offers = ReferralOffer.objects.all()
        context = {
            'referral_offers': referral_offers,
        }
        # If it's a GET request, render the form template
        return render(request, 'admin_side/referral_offer.html',context)
    return redirect('admin_login')

def change_offer_status(request,id):
    try:
        offer = ReferralOffer.objects.get(id=id)
        if offer.is_active == True:
            offer.is_active = False
        else:
            offer.is_active = True
        offer.save()

    except:
        messages.error(request,"Something Went Wrong")
        pass

    return redirect('offer_management:referral_offer')



def delete_referral_offer(request,id):
    try:
        offer = ReferralOffer.objects.get(id = id)
        offer.delete()

    except:
        messages.error(request,"Something Went Wrong")
        pass

    return redirect('offer_management:referral_offer')
