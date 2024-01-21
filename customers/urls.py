from django.urls import path
from accounts import views as AccountViews
from .views import *

urlpatterns = [
    path("", AccountViews.customer_dashboard),
    path("customer-profile/", customer_profile, name="customer_profile"),
    path("my-orders/", my_orders, name="customer_my_orders"),
    path(
        "order-details/<int:order_number>/",
        order_details,
        name="customer_order_details",
    ),
    path("change-password/", change_password, name="customer_change_password"),
]
