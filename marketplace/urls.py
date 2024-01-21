from django.urls import path
from .views import *

urlpatterns = [
    path("", marketplace, name="marketplace"),
    path("cart/", cart, name="cart"),
    path("cart/delete-cart-item/<int:id>/", delete_cart_item, name="delete_cart_item"),
    path("<slug:vendor_slug>/", vendor_details, name="vendor_details"),
    path("add-to-cart/<int:id>/", add_to_cart, name="add_to_cart"),
    path("minus-from-cart/<int:id>/", minus_from_cart, name="minus_from_cart"),
]
