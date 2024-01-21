import datetime
from django.shortcuts import render, redirect
from orders.models import Order
from vendors.models import Vendor
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages, auth
from vendors.forms import VendorForm
from .utils import detectUser, send_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.template.defaultfilters import slugify


def restrict_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


def restrict_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def customer_reg(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in!")
        return redirect("my_account")
    elif request.method == "POST":
        form = UserForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            user.role = User.CUSTOMER
            user.save()

            mail_subject = "Activate Your Account"
            mail_template = "accounts/emails/account_verification_email.html"
            send_verification_email(request, user, mail_subject, mail_template)

            messages.success(
                request,
                "Your account has been registered successfully. Please check your Email.",
            )

            return redirect("login")
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)
    else:
        form = UserForm()

    data = {
        "form": form,
    }
    return render(request, "accounts/customer_registration.html", data)


def vendor_reg(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in!")
        return redirect("my_account")
    elif request.method == "POST":
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)

        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            user.role = User.VENDOR
            user.save()

            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor_name = v_form.cleaned_data.get("vendor_name")
            vendor.vendor_slug = slugify(vendor_name) + "-" + str(user.id)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            mail_subject = "Activate Your Account"
            mail_template = "accounts/emails/account_verification_email.html"
            send_verification_email(request, user, mail_subject, mail_template)

            messages.success(
                request,
                "Your account has been registered successfully. Please check your Email.",
            )

            return redirect("vendor_reg")
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)
            if "vendor_license" in v_form.errors:
                for error in v_form.errors["vendor_license"]:
                    messages.error(request, error)

    else:
        form = UserForm()
        v_form = VendorForm()

    data = {
        "form": form,
        "v_form": v_form,
    }
    return render(request, "accounts/vendor_registration.html", data)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated successfully.")
        return redirect("my_account")
    else:
        messages.error(request, "Invalid activation link!")


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect("my_account")
        else:
            messages.error(request, "Invalid login credentials!")
            return redirect("login")

    return render(request, "accounts/login.html")


def logout(request):
    auth.logout(request)
    messages.info(request, "You are logged out successfully.")
    return redirect("login")


@login_required(login_url="login")
def my_account(request):
    user = request.user
    redirectUrl = detectUser(user)

    return redirect(redirectUrl)


@login_required(login_url="login")
@user_passes_test(restrict_customer)
def customer_dashboard(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by(
        "-created_at"
    )
    recent_orders = orders[:5]

    data = {
        "orders": orders,
        "recent_orders": recent_orders,
    }
    return render(request, "accounts/customer_dashboard.html", data)


@login_required(login_url="login")
@user_passes_test(restrict_vendor)
def vendor_dashboard(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by(
        "-created_at"
    )
    recent_orders = orders[:5]

    total_revenue = 0

    for order in orders:
        total_revenue += order.get_total_by_vendor()["grand_total"]

    current_month = datetime.datetime.now().month
    current_month_orders = orders.filter(
        vendors__in=[vendor.id], created_at__month=current_month
    )
    current_month_revenue = 0
    for order in current_month_orders:
        current_month_revenue += order.get_total_by_vendor()["grand_total"]

    data = {
        "orders": orders,
        "orders_count": orders.count(),
        "recent_orders": recent_orders,
        "total_revenue": total_revenue,
        "current_month_revenue": current_month_revenue,
    }
    return render(request, "accounts/vendor_dashboard.html", data)


def forgot_password(request):
    if request.method == "POST":
        email = request.POST["email"]

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            mail_subject = "Reset Your Password"
            mail_template = "accounts/emails/reset_password_email.html"
            send_verification_email(request, user, mail_subject, mail_template)

            messages.success(request, "Please, check your inbox.")
            return redirect("login")
        else:
            messages.error(request, "Account does not exist!")
    return render(request, "accounts/forgot_password.html")


def password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        return redirect("reset_password")
    else:
        messages.error(request, "Activation link expired!")


def reset_password(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            pk = request.session.get("uid")
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, "Password changed successfully.")
            return redirect("login")
        else:
            messages.error(request, "Passwords do not match!")
            return redirect("forgot_password")
    return render(request, "accounts/reset_password.html")
