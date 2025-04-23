from django.urls import path
from . import views
from accounts import views as AccountViews

urlpatterns = [
    path('', AccountViews.vendorDashboard, name='vendor'),
    path('profile/', views.vprofile, name='vprofile'),
    path('menu-builder/', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>/', views.fooditems_by_category, name='fooditems_by_category'),

    #Category CRUD
    path('menu-builder/category/add/', views.add_category, name='add_category'),
    path('menu-builder/category/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('menu-builder/category/delete/<int:pk>/', views.delete_category, name='delete_category'),

    #Food CRUD
    path('menu-builder/food/add/', views.add_food, name='add_food'),
    path('menu-builder/food/edit/<int:pk>/', views.edit_food, name='edit_food'),
    path('menu-builder/food/delete/<int:pk>/', views.delete_food, name='delete_food'),
    # path('menu-builder/food/import', views.import_food_item, name='import_food_item'),
    # path('menu-builder/food/download-error-csv/', views.download_error_csv, name='download_error_csv'),

    path('menu-builder/food/upload-csv/', views.validate_and_import_csv, name='validate_and_import_csv'),
    path('menu-builder/food/download-error-csv/', views.download_error_csv, name='download_error_csv'),

    #Opening hour
    path('opening-hours', views.opening_hours, name='opening_hours'),
    path('opening-hours/add/', views.add_opening_hours, name='add_opening_hours'),
    path('opening-hours/delete/<int:pk>', views.delete_opening_hours, name='delete_opening_hours'),

    path('order-details/<int:order_number>/', views.order_details, name='vendor_order_details'),
    path('my_orders/', views.my_orders, name='vendor_my_orders')
]
