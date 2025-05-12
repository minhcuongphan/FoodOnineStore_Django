from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('index/', views.coupons_list, name='coupons_list'),
    path('add/', views.add_coupon, name='add_coupon'),
    path('edit/<int:coupon_id>/', views.edit_coupon, name='edit_coupon'),
    path('delete/<int:coupon_id>/', views.delete_coupon, name='delete_coupon'),

    # API URLs
    path('api/delete/<int:coupon_id>/', api_views.delete_coupon_api, name='delete_coupon_api'),
]