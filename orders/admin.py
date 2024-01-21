from django.contrib import admin
from .models import Payment, Order, OrderedFood


class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "transaction_id", "amount", "status")
    search_fields = (
        "user__email__icontains",
        "user__username__icontains",
        "transaction_id",
    )


class OrderedFoodAdmin(admin.ModelAdmin):
    list_display = (
        "food",
        "order",
        "quantity",
        "payment",
        "user",
        "price",
        "amount",
        "created_at",
    )
    list_display_links = (
        "food",
        "order",
    )


class OrderedFoodInline(admin.TabularInline):
    model = OrderedFood
    readonly_fields = (
        "food",
        "quantity",
        "order",
        "payment",
        "user",
        "price",
        "amount",
    )
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "name",
        "phone_number",
        "email",
        "total",
        "order_placed_to",
        "is_ordered",
    )
    search_fields = (
        "order_number",
        "phone_number",
        "email",
    )
    inlines = [OrderedFoodInline]


admin.site.register(OrderedFood, OrderedFoodAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
