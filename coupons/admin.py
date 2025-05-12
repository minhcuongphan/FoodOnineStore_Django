from django.contrib import admin
from .models import Coupon

class CustomCouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'amount', 'valid_from', 'valid_to', 'max_uses', 'used_count', 'min_cart_value', 'active')
    search_fields = ('code',)
    # list_filter = ('active', 'discount_type')
    # list_editable = ('discount_type', 'amount', 'valid_from', 'valid_to', 'max_uses', 'used_count', 'min_cart_value', 'active')
    list_per_page = 20
    list_display_links = ('code',)

admin.site.register(Coupon, CustomCouponAdmin)