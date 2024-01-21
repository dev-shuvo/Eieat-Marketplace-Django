from django.contrib import admin
from .models import Vendor, Category, Food, OpeningHour


class VendorAdmin(admin.ModelAdmin):
    prepopulated_fields = {"vendor_slug": ("vendor_name",)}
    list_display = ("user", "vendor_name", "is_approved", "is_top", "created_at")
    list_display_links = ("user", "vendor_name")
    list_editable = ("is_approved", "is_top")
    search_fields = (
        "user__email__icontains",
        "user__username__icontains",
        "vendor_name",
    )


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("category_name",)}
    list_display = ("category_name", "vendor", "modified_at")
    search_fields = ("category_name", "vendor__vendor_name")


class FoodAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("food_name",)}
    list_display = (
        "food_name",
        "category",
        "vendor",
        "price",
        "is_available",
        "modified_at",
    )
    search_fields = (
        "food_title",
        "category__category_name",
        "vendor__vendor_name",
    )
    list_filter = ("is_available",)


class OpeningHourAdmin(admin.ModelAdmin):
    list_display = ("vendor", "day", "from_hour", "to_hour", "is_closed")
    search_fields = ("vendor__vendor_name",)


admin.site.register(Vendor, VendorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Food, FoodAdmin)
admin.site.register(OpeningHour, OpeningHourAdmin)
