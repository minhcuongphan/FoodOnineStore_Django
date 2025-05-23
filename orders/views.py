from django.shortcuts import render, redirect, HttpResponse
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amounts
from .forms import OrderForm
from .models import Order, Payment, OrderedFood
import simplejson as json
from django.db import transaction
from .utils import generate_order_number
from django.http import JsonResponse
from accounts.utils import send_notification
from django.contrib.auth.decorators import login_required
from menu.models import FoodItem
from marketplace.models import Tax

@login_required(login_url= 'login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('marketplace')

    taxes = Tax.objects.filter(is_active=True)

    vendor_ids = []
    sub_total = 0
    k = {}
    total_data = {}
    for i in cart_items:
        vendor_id = i.fooditem.vendor.id
        if vendor_id not in vendor_ids:
            vendor_ids.append(vendor_id)

        fooditem = FoodItem.objects.get(pk=i.fooditem.id, vendor_id__in=vendor_ids)
        if vendor_id in k:
            sub_total = k[vendor_id]
            sub_total += (fooditem.price * i.quantity)
            k[vendor_id] = sub_total
        else:
            sub_total = (fooditem.price * i.quantity)
            k[vendor_id] = sub_total

        # Calculate the tax
        tax_dict = {}
        for tax in taxes:
            tax_type = tax.tax_type
            tax_percentage = tax.tax_percentage
            tax_amount = round((tax_percentage * sub_total)/100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): str(tax_amount)}})

        # Construct total data
        total_data.update({fooditem.vendor.id: {str(sub_total): str(tax_dict)}})


    cart_amounts = get_cart_amounts(request)
    sub_total = cart_amounts['subtotal']
    total_tax = cart_amounts['tax']
    grand_total = cart_amounts['grandtotal']
    tax_data = cart_amounts['tax_dict']

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    userid = str(request.user.id)  # Get the authenticated user's ID
                    discount_code_key = f'discount_code_{userid}'
                    grandtotal_key = f'temp_grandtotal_{userid}'

                    # Check if the discount code is in the request and not empty
                    if request.POST.get('discount_code') == '':
                        request.session.pop(discount_code_key, '')
                        request.session.pop(grandtotal_key, '')

                    discount_code = ''
                    temp_grandtotal = ''
                    # Check if the discount code and grand total are in the session
                    if discount_code_key in request.session and grandtotal_key in request.session:
                        discount_code = request.session.get(discount_code_key, '')
                        temp_grandtotal = request.session.get(grandtotal_key, '')

                    order = Order()
                    order.first_name = form.cleaned_data['first_name']
                    order.last_name = form.cleaned_data['last_name']
                    order.phone = form.cleaned_data['phone']
                    order.email = form.cleaned_data['email']
                    order.address = form.cleaned_data['address']
                    order.country = form.cleaned_data['country']
                    order.state = form.cleaned_data['state']
                    order.city = form.cleaned_data['city']
                    order.pin_code = form.cleaned_data['pin_code']
                    order.user = request.user
                    order.total = temp_grandtotal if discount_code != '' else grand_total
                    order.tax_data = json.dumps(tax_data)
                    order.total_data = json.dumps(total_data)
                    order.total_tax = total_tax
                    order.payment_method = request.POST.get('payment_method')
                    order.save()
                    order.order_number = generate_order_number(order.id)
                    order.vendors.add(*vendor_ids)
                    order.save()

                context = {
                    'order': order,
                    'cart_items': cart_items,
                    'userid': userid,
                    'discount_code': discount_code,
                    'temp_discounted_grandtotal': temp_grandtotal,
                }

                return render(request, 'orders/place_order.html', context)

            except Exception as e:
                print(f"Error placing order: {e}")
                # Handle the error gracefully (e.g., display an error message to the user)
                return render(request, 'orders/place_order.html', {'form': form, 'error_message': 'An error occurred while placing your order.'})

        else:
            print(form.errors)

    return render(request, 'orders/place_order.html')

@login_required(login_url= 'login')
def payments(request):
    # print('request', request.POST)
    # print('payments....')

    try:
        with transaction.atomic():
            commonValidations(request)
            order_number = request.POST.get('order_number')
            transaction_id = request.POST.get('transaction_id')
            payment_method = request.POST.get('payment_method')
            status = request.POST.get('status')

            # print('payments....')
            # print(order_number, transaction_id, payment_method, status)

            order = Order.objects.get(user=request.user, order_number=order_number)
            payment = Payment(
                user=request.user,
                transaction_id = transaction_id,
                payment_method = payment_method,
                amount = order.total,
                status = status
            )
            payment.save()
            # Update the order model
            order.payment = payment
            order.is_ordered = True
            order.save()

            # Move the cart items to ordered food model
            cart_items = Cart.objects.filter(user=request.user)
            for cart_item in cart_items:
                ordered_food = OrderedFood()
                ordered_food.order = order
                ordered_food.payment = payment
                ordered_food.user = request.user
                ordered_food.fooditem = cart_item.fooditem
                ordered_food.quantity = cart_item.quantity
                ordered_food.price = cart_item.fooditem.price
                ordered_food.amount = cart_item.fooditem.price * cart_item.quantity

                ordered_food.save()

            # Send order confirmation email to the customer
            mail_subject = 'Thank you for your order'
            mail_template = 'orders/order_confirmation_email.html'
            context = {
                'user': request.user,
                'order': order,
                'to_email': order.email,
            }
            # send_notification(mail_subject, mail_template, context)
            # Send order received email to the vendors
            mail_subject = 'You have received a new order'
            mail_template = 'orders/new_order_received_email.html'
            to_emails = []
            for cart_item in cart_items:
                if cart_item.fooditem.vendor.user.email not in to_emails:
                    to_emails.append(cart_item.fooditem.vendor.user.email)

            context = {
                'order': order,
                'to_email': to_emails,
            }

            # send_notification(mail_subject, mail_template, context)
            # Clear the cart if the payment is success
            cart_items.delete()

            return JsonResponse({
                'order_number': order.order_number,
                'transaction_id': transaction_id
            })


    except Exception as e:
        print(f"Error payments: {e}")


def commonValidations(request):
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

def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(
            order_number=order_number,
            payment__transaction_id=transaction_id,
            is_ordered=True
        )

        ordered_food = OrderedFood.objects.filter(order=order)
        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)

        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data
        }

        return render(request, 'orders/order_complete.html', context)
    except Exception as e:
        print('Order complete error: %s' % e)
        # return redirect('home')