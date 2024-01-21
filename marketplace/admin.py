from django.contrib import admin
from .models import Cart, Tax


class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "food", "quantity", "modified_at")
    search_fields = ("user__email__icontains", "user__username__icontains")


class TaxAdmin(admin.ModelAdmin):
    list_display = ("tax_type", "tax_percentage", "is_active")


admin.site.register(Cart, CartAdmin)
admin.site.register(Tax, TaxAdmin)
