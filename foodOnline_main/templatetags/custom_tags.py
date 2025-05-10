from django import template
from django.utils.dateformat import format as date_format

register = template.Library()

@register.filter(name='format_datetime')
def format_datetime(value, date_format_string="Y-m-d h:i:s"):
    if not value:
        return ""
    return date_format(value, date_format_string)