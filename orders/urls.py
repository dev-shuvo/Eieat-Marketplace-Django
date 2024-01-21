from django.urls import path
from .views import *

urlpatterns = [
    path("place-order/", place_order, name="place_order"),
    path("payment/", payment, name="payment"),
    path("payment/success/", payment_success, name="payment_success"),
    path("payment/cancel/", payment_cancel, name="payment_cancel"),
    path(
        "order-complete/<str:order_number>/<str:transaction_id>/",
        order_complete,
        name="order_complete",
    ),
]
