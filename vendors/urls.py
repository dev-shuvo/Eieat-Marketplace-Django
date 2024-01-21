from django.urls import path
from .views import *
from accounts import views as AccountViews

urlpatterns = [
    path("", AccountViews.vendor_dashboard),
    path("vendor-profile/", vendor_profile, name="vendor_profile"),
    path("menu-builder/", menu_builder, name="menu_builder"),
    path(
        "menu-builder/category/<int:pk>/", foods_by_category, name="foods_by_category"
    ),
    path("menu-builder/category/add/", add_category, name="add_category"),
    path("menu-builder/category/edit/<int:pk>/", edit_category, name="edit_category"),
    path(
        "menu-builder/category/delete/<int:pk>/",
        delete_category,
        name="delete_category",
    ),
    path("menu-builder/food/add/", add_food, name="add_food"),
    path("menu-builder/food/edit/<int:pk>/", edit_food, name="edit_food"),
    path(
        "menu-builder/food/delete/<int:pk>/",
        delete_food,
        name="delete_food",
    ),
    path("opening-hours/", opening_hours, name="opening_hours"),
    path("opening-hours/add/", add_opening_hours, name="add_opening_hours"),
    path(
        "opening-hours/delete/<int:pk>/",
        delete_opening_hours,
        name="delete_opening_hours",
    ),
    path(
        "order-details/<int:order_number>/", order_details, name="vendor_order_details"
    ),
    path("orders/", vendor_orders, name="vendor_orders"),
    path("change-password/", change_password, name="vendor_change_password"),
]
