from datetime import date
from django.shortcuts import redirect, render, get_object_or_404
from accounts.models import UserProfile
from orders.forms import OrderForm
from vendors.views import Vendor, Category, Food
from django.db.models import Prefetch
from django.http import JsonResponse
from .models import Cart
from .context_processors import get_cart_counter, get_cart_amounts
from django.contrib.auth.decorators import login_required
from vendors.models import OpeningHour
from django.db.models import Q
from geopy.distance import geodesic


def marketplace(request):
    all_vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)

    vendors_with_categories = {}
    for vendor in all_vendors:
        categories = Category.objects.filter(vendor=vendor)
        vendors_with_categories[vendor] = {
            "categories": categories,
        }

    vendors_count = all_vendors.count()
    data = {
        "vendors_with_categories": vendors_with_categories,
        "vendors_count": vendors_count,
    }
    return render(request, "marketplace/listings.html", data)


def vendor_details(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch("foods", queryset=Food.objects.filter(is_available=True))
    )
    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by(
        "day", "-from_hour"
    )
    today = date.today().isoweekday()
    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    data = {
        "vendor": vendor,
        "categories": categories,
        "cart_items": cart_items,
        "opening_hours": opening_hours,
        "current_opening_hours": current_opening_hours,
    }
    return render(request, "marketplace/vendor_details.html", data)


def add_to_cart(request, id):
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            try:
                food = Food.objects.get(id=id)
                try:
                    check_cart = Cart.objects.get(user=request.user, food=food)
                    check_cart.quantity += 1
                    check_cart.save()
                    return JsonResponse(
                        {
                            "status": "Success",
                            "message": "Quantity updated.",
                            "cart_counter": get_cart_counter(request),
                            "qty": check_cart.quantity,
                            "cart_amounts": get_cart_amounts(request),
                        }
                    )
                except:
                    check_cart = Cart.objects.create(
                        user=request.user, food=food, quantity=1
                    )
                    return JsonResponse(
                        {
                            "status": "Success",
                            "message": "Added to cart successfully.",
                            "cart_counter": get_cart_counter(request),
                            "qty": check_cart.quantity,
                            "cart_amounts": get_cart_amounts(request),
                        }
                    )
            except:
                return JsonResponse(
                    {
                        "status": "Failed",
                        "message": "This item does not exist!",
                    }
                )
        else:
            return JsonResponse(
                {
                    "status": "Failed",
                    "message": "Invalid request!",
                }
            )
    else:
        return JsonResponse(
            {
                "status": "Login_required",
                "message": "Please login to continue!",
            }
        )


def minus_from_cart(request, id):
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            try:
                food = Food.objects.get(id=id)
                try:
                    check_cart = Cart.objects.get(user=request.user, food=food)
                    if check_cart.quantity > 1:
                        check_cart.quantity -= 1
                        check_cart.save()
                    else:
                        check_cart.delete()
                        check_cart.quantity = 0
                    return JsonResponse(
                        {
                            "status": "Success",
                            "message": "Quantity updated.",
                            "cart_counter": get_cart_counter(request),
                            "qty": check_cart.quantity,
                            "cart_amounts": get_cart_amounts(request),
                        }
                    )
                except:
                    return JsonResponse(
                        {
                            "status": "Failed",
                            "message": "You do not have this item in your cart!",
                        }
                    )
            except:
                return JsonResponse(
                    {
                        "status": "Failed",
                        "message": "This item does not exist!",
                    }
                )
        else:
            return JsonResponse(
                {
                    "status": "Failed",
                    "message": "Invalid request!",
                }
            )
    else:
        return JsonResponse(
            {
                "status": "Login_required",
                "message": "Please login to continue!",
            }
        )


@login_required(login_url="login")
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("-created_at")
    data = {
        "cart_items": cart_items,
    }
    return render(request, "marketplace/cart.html", data)


def delete_cart_item(request, id):
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            try:
                cart_item = Cart.objects.get(user=request.user, id=id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse(
                        {
                            "status": "Success",
                            "message": "Item has been deleted from your cart.",
                            "cart_counter": get_cart_counter(request),
                            "cart_amounts": get_cart_amounts(request),
                        }
                    )
            except:
                return JsonResponse(
                    {
                        "status": "Failed",
                        "message": "This item does not exist!",
                    }
                )

        else:
            return JsonResponse(
                {
                    "status": "Failed",
                    "message": "Invalid request!",
                }
            )


def search(request):
    latitude = float(request.GET["lat"])
    longitude = float(request.GET["lon"])
    radius = float(request.GET["radius"])
    keyword = request.GET["keyword"]

    vendors_by_food = Food.objects.filter(
        food_name__icontains=keyword, is_available=True
    ).values_list("vendor", flat=True)

    vendors = Vendor.objects.filter(
        Q(id__in=vendors_by_food)
        | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True)
    ).select_related("user_profile")

    location = (latitude, longitude)
    filtered_vendors = []

    for vendor in vendors:
        vendor_latitude = vendor.user_profile.latitude
        vendor_longitude = vendor.user_profile.longitude
        vendor_location = (vendor_latitude, vendor_longitude)
        distance = geodesic(location, vendor_location).km

        if distance <= radius:
            filtered_vendors.append(vendor)

    vendors_with_categories = {}
    for vendor in filtered_vendors:
        categories = Category.objects.filter(vendor=vendor)
        vendors_with_categories[vendor] = {
            "categories": categories,
            "distance": distance,
        }

    vendors_count = len(filtered_vendors)

    data = {
        "vendors_with_categories": vendors_with_categories,
        "vendors_count": vendors_count,
    }

    return render(request, "marketplace/listings.html", data)


@login_required(login_url="login")
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("created_at")
    order_form = OrderForm()
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("marketplace")
    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "phone_number": request.user.phone_number,
        "email": request.user.email,
        "address": user_profile.address,
        "country": user_profile.country,
        "state": user_profile.state,
        "city": user_profile.city,
        "pin_code": user_profile.pin_code,
    }
    order_form = OrderForm(initial=default_values)
    data = {
        "order_form": order_form,
        "cart_items": cart_items,
    }
    return render(request, "marketplace/checkout.html", data)
