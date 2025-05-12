from django import forms
from .models import Coupon

#create a form for the coupon model
class CouponForm(forms.ModelForm):
    valid_from = forms.DateTimeField(required=True, label='Valid From', widget=forms.DateInput(attrs={'type': 'date'}))
    valid_to = forms.DateTimeField(required=True, label='Valid To', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Coupon
        fields = [
            'code',
            'discount_type',
            'amount',
            'valid_from',
            'valid_to',
            'max_uses',
            'min_cart_value',
            'active'
        ]

