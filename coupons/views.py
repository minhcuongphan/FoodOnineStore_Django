from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.models import User
from django.core.exceptions import PermissionDenied
from .forms import CouponForm
from django.contrib import messages
from .models import Coupon
from django.core.paginator import Paginator

# Create your views here.

def check_role_vendor(user):
    if user.role == User.Vendor:
        return True
    else:
        raise PermissionDenied

def coupons_list(request):
    coupons = Coupon.objects.all().order_by('-id')
    paginator = Paginator(coupons, 10)
    page_number = request.GET.get("page")
    paginated_coupons = paginator.get_page(page_number)
    context = {
        'paginated_coupons': paginated_coupons,
    }

    return render(request, 'coupons/coupons_list.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_coupon(request):
        if request.method == 'POST':
            form = CouponForm(request.POST)
            if form.is_valid():
                # food_title = form.cleaned_data['food_title']
                # food = form.save(commit=False)
                # food.vendor = get_vendor(request)
                # food.slug = slugify(food_title)
                form.save()
                messages.success(request, 'Coupon added successfully')
                return redirect('coupons_list')
            else:
                print(form.errors)
        else:
            form = CouponForm()
            # # modify this form
            # form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))

        context = {
            'form': form,
        }

        return render(request, 'coupons/add_coupon.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_coupon(request, coupon_id):
    print('edit_coupon')
    print(coupon_id)
    coupon = Coupon.objects.get(id=coupon_id)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon updated successfully')
            return redirect('coupons_list')
        else:
            print(form.errors)
    else:
        form = CouponForm(instance=coupon)

    context = {
        'form': form,
        'coupon': coupon,
    }

    return render(request, 'coupons/edit_coupon.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_coupon(request, coupon_id):
    pass
    # coupon = Coupon.objects.get(id=coupon_id)
    # if request.method == 'POST':
    #     coupon.delete()
    #     messages.success(request, 'Coupon deleted successfully')
    #     return redirect('coupons_list')

    # context = {
    #     'coupon': coupon,
    # }

    # return render(request, 'coupons/delete_coupon.html', context)