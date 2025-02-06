from django.shortcuts import render, get_object_or_404, redirect

from menu.forms import CategoryForm, FoodItemForm
from .forms import VendorForm, OpeningHourForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile, User
from vendor.models import Vendor, OpeningHour
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from menu.models import Category, FoodItem
from django.template.defaultfilters import slugify
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError

def get_vendor(request):
    return Vendor.objects.get(user=request.user)

def check_role_vendor(user):
    if user.role == User.Vendor:
        return True
    else:
        raise PermissionDenied

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Settings updated successfully')
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor
    }

    return render(request, 'vendor/vprofile.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    categories = Category.objects.filter(vendor=get_vendor(request)).order_by('created_at')
    context = {
        'categories': categories
    }

    return render(request, 'vendor/menu_builder.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=get_vendor(request), category=category)
    context = {
        'fooditems': fooditems,
        'category': category
    }

    return render(request, 'vendor/fooditems_by_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'Category added successfully')
            return redirect('menu_builder')
    else:
        form = CategoryForm()

    context = {
        'form': form
    }

    return render(request, 'vendor/add_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'Category updated successfully')
            return redirect('menu_builder')
    else:
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category': category
    }
    return render(request, 'vendor/edit_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category deleted successfully')

    return redirect('menu_builder')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food_title)
            form.save()
            messages.success(request, 'Food item added successfully')
            return redirect('fooditems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
        # modify this form
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))

    context = {
        'form': form,
    }

    return render(request, 'vendor/add_food.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food_title)
            form.save()
            messages.success(request, 'Food item updated successfully')
            return redirect('fooditems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm(instance=food)
        # modify this form
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))

    context = {
        'form': form,
        'food': food
    }

    return render(request, 'vendor/edit_food.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, 'Food item deleted successfully')

    return redirect('fooditems_by_category', food.category.id)

def opening_hours(request):
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    context = {
        'form': OpeningHourForm(),
        'opening_hours': opening_hours
    }

    return render(request, 'vendor/opening_hours.html', context)
def add_opening_hours(request):
    commonValidations(request)

    day         = request.POST.get('day')
    from_hour   = request.POST.get('from_hour')
    to_hour     = request.POST.get('to_hour')
    is_closed   = request.POST.get('is_closed')

    hour_id         = 0
    open_day        = ''
    is_closed_hour  = ''
    open_from_hour  = ''
    open_to_hour    = ''

    try:
        opening_hour = OpeningHour.objects.create(
            vendor=get_vendor(request),
            day=day,
            from_hour=from_hour,
            to_hour=to_hour,
            is_closed=is_closed
        )

        day = OpeningHour.objects.get(id=opening_hour.id)

        status = 'Success'
        message = 'Created a new opening hour successfylly!'
        hour_id = opening_hour.id
        open_day = day.get_day_display()
        is_closed_hour = 'Closed' if day.is_closed else ''
        open_from_hour = '' if day.is_closed else opening_hour.from_hour
        open_to_hour = '' if day.is_closed else opening_hour.to_hour
    except IntegrityError as e:
        status = 'Failed'
        message = from_hour + ' - ' + to_hour + ' already exists for this day!'

    return JsonResponse({
        'status': status,
        'message': message,
        'id': hour_id,
        'day': open_day,
        'is_closed': is_closed_hour,
        'from_hour': open_from_hour,
        'to_hour': open_to_hour
    })

def delete_opening_hours(request, pk):
    commonValidations(request)
    try:
        # check if the opening hour exists
        opening_hour = OpeningHour.objects.get(vendor=get_vendor(request), id=pk)
        if opening_hour:
            opening_hour.delete()

        return JsonResponse({
            'status': 'Success',
            'message': 'Opening hour has been deleted!'
        })
    except:
        return JsonResponse({
            'status': 'Failed',
            'message': 'The opening hour does not exist!'
        })


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