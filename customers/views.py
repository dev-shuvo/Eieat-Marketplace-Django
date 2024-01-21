import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.forms import UserProfileForm, UserInfoForm
from accounts.models import User, UserProfile
from django.contrib import messages
from django.db.models import Sum
from orders.models import Order, OrderedFood


@login_required(login_url="login")
def customer_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)

        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, "Profile has been updated.")
            return redirect("customer_profile")
        else:
            if "profile_photo" in profile_form.errors:
                for error in profile_form.errors["profile_photo"]:
                    messages.error(request, error)

            elif "cover_photo" in profile_form.errors:
                for error in profile_form.errors["cover_photo"]:
                    messages.error(request, error)

    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)

    data = {
        "profile_form": profile_form,
        "user_form": user_form,
        "profile": profile,
    }
    return render(request, "customers/customer_profile.html", data)


@login_required(login_url="login")
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by(
        "-created_at"
    )
    data = {
        "orders": orders,
    }
    return render(request, "customers/my_orders.html", data)


@login_required(login_url="login")
def order_details(request, order_number):
    order = Order.objects.get(order_number=order_number, is_ordered=True)
    ordered_foods = OrderedFood.objects.filter(order=order)
    tax_dict = order.tax_data
    tax_dict = json.loads(tax_dict)
    subtotal = ordered_foods.aggregate(Sum("amount"))["amount__sum"] or 0

    data = {
        "order": order,
        "ordered_foods": ordered_foods,
        "tax_dict": tax_dict,
        "subtotal": subtotal,
    }
    return render(request, "customers/order_details.html", data)


@login_required(login_url="login")
def change_password(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]

        user = User.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            check_password = user.check_password(current_password)
            if check_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password changed successfully.")
                return redirect("login")
            else:
                messages.error(request, "The password you entered was incorrect!")
                return redirect("change_password")
        else:
            messages.error(request, "Passwords do not match!")
            return redirect("change_password")

    return render(request, "customers/change_password.html")
