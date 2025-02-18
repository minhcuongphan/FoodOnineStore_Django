from django.urls import path
from accounts import views as AccountViews
from . import views

urlpatterns = [
    path('', AccountViews.custDashboard, name='customer'),
    path('profile/', views.cprofile, name='cprofile'),
    path('my-orders/', views.my_orders, name='customer_my_orders'),
    path('order-details/<int:order_number>', views.order_details, name='order_details'),
]