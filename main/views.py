from datetime import date
from django.shortcuts import render
from vendors.models import Category, Vendor


def index(request):
    top_vendors = Vendor.objects.filter(
        is_approved=True, user__is_active=True, is_top=True
    )[:8]
    new_vendors = Vendor.objects.filter(
        is_approved=True, user__is_active=True
    ).order_by("-created_at")[:6]

    vendors = {}

    for vendor in new_vendors:
        categories = Category.objects.filter(vendor=vendor)
        vendors[vendor] = categories

    data = {
        "top_vendors": top_vendors,
        "vendors": vendors,
    }
    return render(request, "index.html", data)
