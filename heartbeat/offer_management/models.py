from django.db import models
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from product_management.models import Category
from django.utils import timezone
from django.core.exceptions import ValidationError
from user_app.models import Account
import random
import string


# Create your models here.
class CategoryOffer(models.Model):
    offer_name           = models.CharField(max_length=100)
    expire_date          = models.DateField()
    category             = models.ForeignKey(Category, on_delete=models.CASCADE)  # ForeignKey relationship with Category
    discount_percentage  = models.DecimalField(max_digits=5, decimal_places=0)
    is_active            = models.BooleanField(default=True)
    
    def __str__(self):
        return self.offer_name



########### referal offer ############

from django.db import models
from django.utils import timezone
import random
import string



class ReferralOffer(models.Model):
    expire_date = models.DateField()
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    limit = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def is_offer_active(self):
        """
        Check if the referral offer is active based on the expire_date.
        """
        return self.is_active and self.expire_date >= timezone.now().date()

class ReferralUser(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    count = models.IntegerField()
    code = models.CharField(max_length=8, unique=True, null=True)  # Assuming code is a string
    is_active = models.BooleanField(default=True)

    def generate_referral_code(self, length=8):
        """
        Generate a random referral code.
        """
        characters = string.ascii_letters + string.digits
        code = ''.join(random.choices(characters, k=length))
        return code

    def save(self, *args, **kwargs):
        # Check if the referral offer is active before saving
        referral_offer = ReferralOffer.objects.first()  # Assuming there's only one ReferralOffer object
        if referral_offer and not referral_offer.is_offer_active():
            # Offer is expired, deactivate the user
            self.is_active = False

        # Generate a new referral code if not provided
        if not self.code:
            self.code = self.generate_referral_code()

        super().save(*args, **kwargs)



    def __str__(self):
        return str(self.code)