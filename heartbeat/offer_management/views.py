
from django.shortcuts import render, redirect
from .models import ReferralOffer, ReferralUser
from django.contrib import messages
from .models import *
from .forms import CategoryOfferForm
import string
import random
from decimal import Decimal
from product_management.models import Product_Variant,Product


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


def category_offer(request):
    if request.method == 'POST':
        form = CategoryOfferForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category offer created successfully.')
            return redirect('offer_management:category_offer')
        else:
            # Form is not valid, handle errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CategoryOfferForm()

    category_offers = CategoryOffer.objects.all().order_by("id")
    categories = Category.objects.all()
    context = {
        'form': form,
        'category_offers': category_offers,
        'categories': categories,
    }
    return render(request, 'admin_side/category_offer.html', context)

def deactivate_category_offer(request,id):
    try:
        cat_offer = CategoryOffer.objects.get(id = id)
        if cat_offer.is_active == True:
            cat_offer.is_active = False
            product12 = Product.objects.filter(category = cat_offer.category)
            print("ppppppppppppppp",product12)
            product_variant = []
            for i in product12:
                product_variant.append(Product_Variant.objects.filter(product = i))
            print("FFDDDDDD",product_variant)
            # discount = cat_offer.discount_percentage
            for pro in product_variant:
                for p in pro:
                    p.sale_price+=p.offer_discount

                    print(p.sale_price,p.offer_discount,p.product.product_name)
                    p.offer_discount = 0
                    p.save()
                print("productttttt",pro)
        else:
            cat_offer.is_active = True
        cat_offer.save()
        messages.success(request,"Category Offer is Activated")
    except Exception as e:
        print(str(e))

    return redirect("offer_management:category_offer")


def delete_category_offer(request,id):
    try:
        cat_offer = CategoryOffer.objects.get(id = id)
        cat_offer.delete()
        messages.success(request,"Category Offer Deleted")
    except:
        pass

    return redirect("offer_management:category_offer")
