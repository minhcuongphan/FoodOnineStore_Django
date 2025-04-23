from django import forms
from .models import Vendor, OpeningHour
from accounts.validators import allow_only_images_validator
import csv
import re
from menu.models import FoodItem

class VendorForm(forms.ModelForm):
    vendor_license = forms.FileField(widget=forms.FileInput(
        attrs={'class': 'btn btn-info'}),
        validators=[allow_only_images_validator]
    )
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']

class OpeningHourForm(forms.ModelForm):
    class Meta:
        model = OpeningHour
        fields = ['day', 'from_hour', 'to_hour', 'is_closed']

class CsvUploadForm(forms.Form):
    csv_file = forms.FileField(label='Upload CSV File')

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError('Please upload a valid CSV file.')

        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            required_columns = {'vendor_id', 'category_id', 'food_title', 'slug', 'description', 'price'}
            if not required_columns.issubset(reader.fieldnames):
                raise forms.ValidationError('CSV file is missing required columns.')

            errors = []
            valid_rows = []
            slug_pattern = re.compile(r'^[a-z0-9-]+$')
            slugs_seen = set(FoodItem.objects.values_list('slug', flat=True))
            row_number = 1

            for row in reader:
                row_errors = []
                error_columns = set()

                try:
                    # Validate vendor_id
                    if not row['vendor_id'].isdigit() or int(row['vendor_id']) <= 0:
                        row_errors.append('vendor_id must be a positive integer')
                        error_columns.add('vendor_id')

                    # Validate category_id
                    if not row['category_id'].isdigit() or int(row['category_id']) <= 0:
                        row_errors.append('category_id must be a positive integer')
                        error_columns.add('category_id')

                    # Validate food_title
                    if not row['food_title'].strip():
                        row_errors.append('food_title cannot be empty')
                        error_columns.add('food_title')

                    # Validate slug
                    slug = row['slug'].strip()
                    if not slug:
                        row_errors.append('slug cannot be empty')
                        error_columns.add('slug')
                    elif not slug_pattern.match(slug):
                        row_errors.append('slug must contain only lowercase letters, numbers, or hyphens')
                        error_columns.add('slug')
                    # elif slug in slugs_seen:
                    #     row_errors.append(f'slug "{slug}" is not unique')
                    #     error_columns.add('slug')
                    else:
                        slugs_seen.add(slug)

                    # Validate description
                    if not row['description'].strip():
                        row_errors.append('description cannot be empty')
                        error_columns.add('description')

                    # Validate price
                    try:
                        price = float(row['price'])
                        if price <= 0:
                            row_errors.append('price must be a positive number')
                            error_columns.add('price')
                    except (ValueError, TypeError):
                        row_errors.append('price must be a valid number')
                        error_columns.add('price')

                    if not row_errors:
                        valid_rows.append(row)
                    else:
                        errors.append({
                            'row_number': row_number,
                            'errors': '; '.join(row_errors),
                            'error_columns': ', '.join(error_columns),
                            'row_data': row
                        })

                except KeyError as e:
                    errors.append({
                        'row_number': row_number,
                        'errors': f'Missing column: {e}',
                        'error_columns': str(e),
                        'row_data': row
                    })

                row_number += 1

            # Store errors and valid rows for use in the view
            self.cleaned_data['errors'] = errors
            self.cleaned_data['valid_rows'] = valid_rows

        except UnicodeDecodeError:
            raise forms.ValidationError('Unable to decode CSV file. Ensure it is UTF-8 encoded.')
        except Exception as e:
            raise forms.ValidationError(f'Error processing CSV file: {e}')

        # Reset file pointer
        csv_file.seek(0)
        return csv_file