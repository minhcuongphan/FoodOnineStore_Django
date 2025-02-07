from .models import Cart, Tax
from menu.models import FoodItem

def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
        except:
            cart_count = 0

    return dict(cart_count=cart_count)

def get_cart_amounts(request):
    subtotal    = 0
    tax         = 0
    grandtotal  = 0
    tax_dict    = {}
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            fooditem = FoodItem.objects.get(pk=item.fooditem.id)
            subtotal += (fooditem.price * item.quantity)

        taxes = Tax.objects.filter(is_active=True)
        for tax in taxes:
            tax_type = tax.tax_type
            tax_percentage = tax.tax_percentage
            tax_amount = round((tax_percentage * subtotal)/100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): tax_amount}})

        tax = sum(x for key in tax_dict.values() for x in key.values())
        grandtotal = subtotal + tax

    return dict(subtotal = subtotal, tax = tax, grandtotal = grandtotal, tax_dict=tax_dict)