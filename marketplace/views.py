from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from vendor.models import Vendor
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from .models import Cart
from .context_processors import get_cart_amounts, get_cart_counter
from django.contrib.auth.decorators import login_required

def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    context = {
        'vendors': vendors,
        'vendors_count': vendors.count()
    }

    return render(request, 'marketplace/listings.html', context)

def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )

    cart_items = Cart.objects.filter(user=request.user) if request.user.is_authenticated else None

    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items
    }

    return render(request, 'marketplace/vendor_detail.html', context)

def add_to_cart(request, food_id):
    if request.user.is_authenticated == False:
        return JsonResponse({
                'status': 'Failed',
                'message': 'Please log in to continue',
                'error_type': 'login_required'
        })

    if request.is_ajax() == False:
        return JsonResponse({
            'status': 'Failed',
            'message': 'Invalid request!'
        })

    try:
        # check if the food item exists
        fooditem = FoodItem.objects.get(id=food_id)
        # check if the user has already added that food to the cart
        try:
            chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
            # increase the cart quantity
            chkCart.quantity += 1
            chkCart.save()
            status = 'Success'
            message = 'Increased the cart quantity!'
        except:
            chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
            status = 'Success'
            message = 'Added the food to the cart!'

        return JsonResponse({
            'status': status,
            'message': message,
            'cart_counter': get_cart_counter(request),
            'qty': chkCart.quantity,
            'cart_amounts': get_cart_amounts(request)
        })
    except:
        return JsonResponse({
            'status': 'Failed',
            'message': 'The food does not exist!'
        })

def decrease_cart(request, food_id):
    if request.user.is_authenticated == False:
        return JsonResponse({
                'status': 'Failed',
                'message': 'Please log in to continue',
                'error_type': 'login_required'
        })

    if request.is_ajax() == False:
        return JsonResponse({
            'status': 'Failed',
            'message': 'Invalid request!'
        })

    try:
        # check if the food item exists
        fooditem = FoodItem.objects.get(id=food_id)
        # check if the user has already added that food to the cart
        try:
            chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
            if chkCart.quantity > 1:
                # descrease the cart quantity
                chkCart.quantity -= 1
                chkCart.save()
            else:
                chkCart.delete()
                chkCart.quantity = 0

            status = 'Success'
            message = 'Decreased the cart quantity!'
            cart_counter = get_cart_counter(request)
            qty = chkCart.quantity
            cart_amounts = get_cart_amounts(request)
        except:
            status = 'Failed'
            message = 'You don not have this item in your cart!'
            cart_counter = 0
            qty = 0
            cart_amounts = []

        return JsonResponse({
            'status': status,
            'message': message,
            'cart_counter': cart_counter,
            'qty': qty,
            'cart_amounts': cart_amounts
        })
    except:
        return JsonResponse({
            'status': 'Failed',
            'message': 'The food does not exist!'
        })

@login_required(login_url= 'login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items': cart_items
    }

    return render(request, 'marketplace/cart.html', context)

def delete_cart(request, cart_id):
    if request.user.is_authenticated == False:
        return JsonResponse({
                'status': 'Failed',
                'message': 'Please log in to continue',
                'error_type': 'login_required'
        })

    if request.is_ajax() == False:
        return JsonResponse({
            'status': 'Failed',
            'message': 'Invalid request!'
        })

    try:
        # check if the cart item exists
        cart_item = Cart.objects.get(user=request.user, id=cart_id)
        if cart_item:
            cart_item.delete()

        return JsonResponse({
            'status': 'Success',
            'message': 'Cart item has been deleted!',
            'cart_counter': get_cart_counter(request),
            'cart_amounts': get_cart_amounts(request)
        })
    except:
        return JsonResponse({
            'status': 'Failed',
            'message': 'The cart item does not exist!'
        })