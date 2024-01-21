from django.urls import path, include
from .views import *

urlpatterns = [
    path("", my_account),
    path("customer-registration/", customer_reg, name="customer_reg"),
    path("vendor-registration/", vendor_reg, name="vendor_reg"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("my-account/", my_account, name="my_account"),
    path("customer-dashboard/", customer_dashboard, name="customer_dashboard"),
    path("vendor-dashboard/", vendor_dashboard, name="vendor_dashboard"),
    path("activate/<uidb64>/<token>/", activate, name="activate"),
    path("forgot-password/", forgot_password, name="forgot_password"),
    path(
        "reset-password/validate/<uidb64>/<token>/",
        password_validate,
        name="password_validate",
    ),
    path("reset-password/", reset_password, name="reset_password"),
    path("vendor/", include("vendors.urls")),
    path("customer/", include("customers.urls")),
]
