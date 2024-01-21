from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from orders.models import Order, OrderedFood
from .forms import VendorForm, CategoryForm, FoodForm, OpeningHourForm
from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import User, UserProfile
from .models import Vendor, Category, Food, OpeningHour
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import restrict_vendor
from django.template.defaultfilters import slugify
import requests


def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor


@login_required(login_url="login")
@user_passes_test(restrict_vendor)
def vendor_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        user_form = UserInfoForm(request.POST, instance=request.user)

        if profile_form.is_valid() and vendor_form.is_valid() and user_form.is_valid():
            profile_form.save()
            vendor_form.save()
            user_form.save()

            address = profile_form.cleaned_data["address"]
            nominatim_url = "https://nominatim.openstreetmap.org/search"
            params = {"q": address, "format": "json"}
            response = requests.get(nominatim_url, params=params)
            data = response.json()

            profile.latitude = data[0]["lat"]
            profile.longitude = data[0]["lon"]
            profile.save()

            messages.success(request, "Profile has been updated.")
            return redirect("vendor_profile")
        else:
            if "profile_photo" in profile_form.errors:
                for error in profile_form.errors["profile_photo"]:
                    messages.error(request, error)

            elif "cover_photo" in profile_form.errors:
                for error in profile_form.errors["cover_photo"]:
                    messages.error(request, error)

            elif "vendor_license" in vendor_form.errors:
                for error in vendor_form.errors["vendor_license"]:
                    messages.error(request, error)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)
        user_form = UserInfoForm(instance=request.user)

    data = {
        "profile_form": profile_form,
        "vendor_form": vendor_form,
        "user_form": user_form,
        "profile": profile,
        "vendor": vendor,
    }
    return render(request, "vendors/vendor_profile.html", data)


@login_required(login_url="login")
@user_passes_test(restrict_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor)

    data = {
        "categories": categories,
    }
    return render(request, "vendors/menu_builder.html", data)


@login_required(login_url="login")
@user_passes_test(restrict_vendor)
def foods_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    foods = Food.objects.filter(vendor=vendor, category=category)

    data = {
        "foods": foods,
        "category": category,
    }
    return render(request, "vendors/foods_by_category.html", data)


@login_required(login_url="login")
@user_passes_test(restrict_vendor)
def add_category(request):
    if request.method == "POST":
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_name = category_form.cleaned_data["category_name"]
            category = category_form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            category_form.save()
            messages.success(request, "Category added successfully.")
            return redirect("menu_builder")
    else:
        category_form = CategoryForm()
    data = {
        "category_form": category_form,
    }
    return render(request, "vendors/add_category.html", data)


@login_required(login_url="login")
@user_passes_test(restrict_vendor)
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category_form = CategoryForm(request.POST, instance=category)
        if category_form.is_valid():
            category_name = category_form.cleaned_data["category_name"]
            category = category_form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            category_form.save()
            messages.success(request, "Category updated successfully.")
            return redirect("menu_builder")
    else:
        category_form = CategoryForm(instance=category)
    data = {
        "category": category,
        "category_form": category_form,
    }
    return render(request, "vendors/edit_category.html", data)


@login_required(login_url="login")
@user_passes_test(restrict_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category deleted successfully.")
    return redirect("menu_builder")


@login_required(login_url="login")
@user_passes_test(restrict_vendor)
def add_food(request):
    if request.method == "POST":
        food_form = FoodForm(request.POST, request.FILES)
        if food_form.is_valid():
            food_name = food_form.cleaned_data["food_name"]
            food = food_form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food_name)
            food_form.save()
            messages.success(request, "Food added successfully.")
            return redirect("foods_by_category", food.category.id)
    else:
        food_form = FoodForm()
        food_form.fields["category"].queryset = Category.objects.filter(
            vendor=get_vendor(request)
        )
    data = {
        "food_form": food_form,
    }
    return render(request, "vendors/add_food.html", data)


@login_required(login_url="login")
@user_passes_test(restrict_vendor)
def edit_food(request, pk=None):
    food = get_object_or_404(Food, pk=pk)
    if request.method == "POST":
        food_form = FoodForm(request.POST, request.FILES, instance=food)
        if food_form.is_valid():
            food_name = food_form.cleaned_data["food_name"]
            food = food_form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food_name)
            food_form.save()
            messages.success(request, "Food updated successfully.")
            return redirect("foods_by_category", food.category.id)
    else:
        food_form = FoodForm(instance=food)
        food_form.fields["category"].queryset = Category.objects.filter(
            vendor=get_vendor(request)
        )
    data = {
        "food": food,
        "food_form": food_form,
    }
    return render(request, "vendors/edit_food.html", data)


@login_required(login_url="login")
@user_passes_test(restrict_vendor)
def delete_food(request, pk=None):
    food = get_object_or_404(Food, pk=pk)
    food.delete()
    messages.success(request, "Food deleted successfully.")
    return redirect("foods_by_category", food.category.id)


@login_required(login_url="login")
@user_passes_test(restrict_vendor)
def opening_hours(request):
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    form = OpeningHourForm()

    data = {
        "opening_hours": opening_hours,
        "form": form,
    }
    return render(request, "vendors/opening_hours.html", data)


def add_opening_hours(request):
    if request.user.is_authenticated:
        if (
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            and request.method == "POST"
        ):
            day = request.POST.get("day")
            from_hour = request.POST.get("from_hour")
            to_hour = request.POST.get("to_hour")
            is_closed = request.POST.get("is_closed")

            try:
                opening_hours = OpeningHour.objects.create(
                    vendor=get_vendor(request),
                    day=day,
                    from_hour=from_hour,
                    to_hour=to_hour,
                    is_closed=is_closed,
                )
                if opening_hours:
                    day = OpeningHour.objects.get(id=opening_hours.id)
                    if day.is_closed:
                        response = {
                            "status": "Success",
                            "id": opening_hours.id,
                            "day": day.get_day_display(),
                            "is_closed": "Closed",
                        }
                    else:
                        response = {
                            "status": "Success",
                            "id": opening_hours.id,
                            "day": day.get_day_display(),
                            "from_hour": opening_hours.from_hour,
                            "to_hour": opening_hours.to_hour,
                        }
                return JsonResponse(response)
            except IntegrityError as e:
                return JsonResponse(
                    {
                        "status": "Failed",
                        "message": from_hour
                        + " - "
                        + to_hour
                        + " already exists for this day!",
                    }
                )
        else:
            return JsonResponse(
                {
                    "status": "Failed",
                    "message": "Invalid request!",
                }
            )


def delete_opening_hours(request, pk):
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            opening_hour = get_object_or_404(OpeningHour, pk=pk)
            opening_hour.delete()

            return JsonResponse(
                {
                    "status": "Success",
                    "id": pk,
                }
            )


@login_required(login_url="login")
def order_details(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_foods = OrderedFood.objects.filter(
            order=order, food__vendor=get_vendor(request)
        )
    except:
        return redirect("vendor")

    data = {
        "order": order,
        "ordered_foods": ordered_foods,
        "subtotal": order.get_total_by_vendor()["subtotal"],
        "tax_dict": order.get_total_by_vendor()["tax_dict"],
        "grand_total": order.get_total_by_vendor()["grand_total"],
    }
    return render(request, "vendors/order_details.html", data)


@login_required(login_url="login")
@user_passes_test(restrict_vendor)
def vendor_orders(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by(
        "-created_at"
    )
    data = {
        "orders": orders,
    }
    return render(request, "vendors/vendor_orders.html", data)


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

    return render(request, "vendors/change_password.html")
