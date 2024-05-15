from django import forms
from .models import CategoryOffer
import datetime

class CategoryOfferForm(forms.ModelForm):
    class Meta:
        model = CategoryOffer
        fields = ['offer_name', 'expire_date', 'category', 'discount_percentage', 'is_active']

    def __init__(self, *args, **kwargs):
        super(CategoryOfferForm, self).__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields for styling
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

        # Optionally, you can customize individual fields further, for example:
        # self.fields['offer_name'].widget.attrs.update({'placeholder': 'Enter offer name'})

    def clean_discount_percentage(self):
        # Custom validation for discount_percentage field
        discount_percentage = self.cleaned_data['discount_percentage']
        if discount_percentage < 0 or discount_percentage > 100:
            raise forms.ValidationError("Discount percentage must be between 0 and 100.")
        return discount_percentage

    def clean_expire_date(self):
        # Custom validation for expire_date field
        expire_date = self.cleaned_data['expire_date']
        if expire_date < datetime.date.today():
            raise forms.ValidationError("Expire date must be a future date.")
        return expire_date