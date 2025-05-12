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
from orders.models import Order, OrderedFood
from django.core.paginator import Paginator
from .forms import CsvUploadForm
from django.views.decorators.csrf import csrf_protect
import csv
import io
import json

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
    error_csv_available = False

    #print log histories of each category
    # for category in categories:
    #     print(f"Category: {category.category_name}")
    #     history = category.history.all().order_by('-history_date')  # Order by most recent history
    #     print(f"history: {history}")
    #     if history:
    #         for i in range(len(history) - 1):
    #             current_record = history[i]
    #             previous_record = history[i + 1]
    #             print(f"History Date: {current_record.history_date}")
    #             print(f"Old Value: {previous_record.description}")
    #             print(f"New Value: {current_record.description}")
    #             print(f"Updated By: {current_record.history_user}")

    # if request.method == "POST":
    #     error_csv_available = 'error_csv' in request.session
    #     valid_rows = [] if 'valid_rows' not in request.session else request.session['valid_rows']

    #     if error_csv_available:
    #         messages.error(request, 'Failed to import the csv file.')
    #     else:
    #         messages.success(request, f'Successfully imported {valid_rows} valid rows.')

    return render(request, 'vendor/menu_builder.html', {
        'error_csv_available': error_csv_available,
        'categories': categories
    })

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=get_vendor(request), category=category).order_by('id')
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

def order_details(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order, fooditem__vendor=get_vendor(request))
    except:
        return redirect('vendor')

    context = {
        'order': order,
        'ordered_food': ordered_food,
        'subtotal': order.get_total_by_vendor()['subtotal'],
        'tax_data': order.get_total_by_vendor()['tax_dict'],
        'grand_total': order.get_total_by_vendor()['grand_total'],
    }

    return render(request, 'vendor/order_details.html', context)

def my_orders(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')

    paginator = Paginator(orders, 10)  # Show 10 contacts per page.
    page_number = request.GET.get("page")
    paginated_orders = paginator.get_page(page_number)

    context = {
        'paginated_orders': paginated_orders
    }

    return render(request, 'vendor/my_orders.html', context)

@csrf_protect
def validate_and_import_csv(request):
    if request.method == 'POST':
        form = CsvUploadForm(request.POST, request.FILES)
        if form.is_valid():
            errors = form.cleaned_data['errors']
            valid_rows = form.cleaned_data['valid_rows']

            # If there are errors, generate error CSV and return
            if errors:
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(['row_number', 'errors', 'error_columns', 'vendor_id', 'category_id', 'food_title', 'slug', 'description', 'price'])
                for error in errors:
                    row_data = error['row_data']
                    writer.writerow([
                        error['row_number'],
                        error['errors'],
                        error['error_columns'],
                        row_data.get('vendor_id', ''),
                        row_data.get('category_id', ''),
                        row_data.get('food_title', ''),
                        row_data.get('slug', ''),
                        row_data.get('description', ''),
                        row_data.get('price', '')
                    ])

                # Store error CSV in session
                request.session['error_csv'] = output.getvalue()
                request.session['error_csv_filename'] = 'import_errors.csv'

                return JsonResponse({
                    'status': 'error',
                    'errors': [{'row_number': e['row_number'], 'errors': e['errors'], 'error_columns': e['error_columns']} for e in errors],
                    'error_csv_available': True
                })
            else:
                # If all rows are valid, import them using bulk operations
                try:
                    request.session['valid_rows'] = len(valid_rows)

                    # Prepare objects for bulk_create and bulk_update
                    food_items_to_create = []
                    food_items_to_update = []

                    existing_slugs = set(FoodItem.objects.filter(slug__in=[row['slug'] for row in valid_rows]).values_list('slug', flat=True))

                    for row in valid_rows:
                        food_item = FoodItem(
                            slug=row['slug'],
                            vendor_id=int(row['vendor_id']),
                            category_id=int(row['category_id']),
                            food_title=row['food_title'],
                            description=row['description'],
                            price=float(row['price']),
                        )
                        if row['slug'] in existing_slugs:
                            food_items_to_update.append(food_item)
                        else:
                            food_items_to_create.append(food_item)

                    # Perform bulk_create and bulk_update
                    if food_items_to_create:
                        FoodItem.objects.bulk_create(food_items_to_create, batch_size=1000)
                    if food_items_to_update:
                        FoodItem.objects.bulk_update(
                            food_items_to_update,
                            fields=['vendor_id', 'category_id', 'food_title', 'description', 'price'],
                            batch_size=1000
                        )

                    # Clear session data
                    request.session.pop('error_csv', None)
                    request.session.pop('error_csv_filename', None)

                    return JsonResponse({
                        'status': 'success',
                        'message': f'Successfully imported {len(valid_rows)} valid rows.',
                        'redirect_url': '/vendor/menu-builder/'
                    })
                except Exception as e:
                    return JsonResponse({
                        'status': 'error',
                        'errors': [{'row_number': 0, 'errors': f'Import error: {str(e)}', 'error_columns': ''}]
                    }, status=500)
        else:
            return JsonResponse({
                'status': 'error',
                'errors': form.errors.get_json_data()
            }, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

def download_error_csv(request):
    if 'error_csv' not in request.session:
        messages.error(request, 'No error CSV available.')
        return redirect('import_result')

    error_csv_content = request.session['error_csv']
    filename = request.session['error_csv_filename']

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )
    response.write(error_csv_content)

    # Clear session data
    request.session.pop('error_csv', None)
    request.session.pop('error_csv_filename', None)

    return response

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def revision_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category_histories = []
    history = category.history.all().order_by('-history_date')  # Order by most recent history

    for i in range(len(history) - 1):
        current_record = history[i]
        previous_record = history[i + 1]

        # Compare fields and log changes
        changes = []
        for field in ['category_name', 'description']:  # List all fields you want to track
            old_value = getattr(previous_record, field, None)
            new_value = getattr(current_record, field, None)
            if old_value != new_value:  # Check if the field value has changed
                changes.append({
                    'field': field,
                    'old_value': old_value,
                    'new_value': new_value,
                })

        category_histories.append({
            'history_date': current_record.history_date,
            'updated_by': current_record.history_user,
            'changes': changes,
        })

    context = {
        'category_histories': category_histories,
    }

    return render(request, 'vendor/revision_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def revision_food(request, pk=None):
    fooditem = get_object_or_404(FoodItem, pk=pk)
    fooditem_histories = []
    history = fooditem.history.all().order_by('-history_date')  # Order by most recent history


    # Handle the case where there is only one historical record

    print("History: ", history)
    print("History count: ", history.count())

    for i in range(len(history) - 1):
        current_record = history[i]
        previous_record = history[i + 1]

        # Compare fields and log changes
        changes = []
        for field in ['category', 'food_title', 'description', 'price', 'image', 'is_available']:  # List all fields you want to track
            old_value = getattr(previous_record, field, None)
            new_value = getattr(current_record, field, None)
            if old_value != new_value:  # Check if the field value has changed
                changes.append({
                    'field': field,
                    'old_value': old_value,
                    'new_value': new_value,
                })

        fooditem_histories.append({
            'history_date': current_record.history_date,
            'updated_by': current_record.history_user,
            'changes': changes,
        })

    context = {
        'fooditem_histories': fooditem_histories,
    }

    return render(request, 'vendor/revision_food.html', context)