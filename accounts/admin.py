from django.contrib import admin
from .models import User, UserProfile
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    list_display = ("email", "first_name", "last_name", "username", "role", "is_active")
    ordering = ("-date_joined",)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "country",
        "state",
        "city",
        "pin_code",
        "created_date",
        "modified_date",
    )
    list_filter = (
        "country",
        "state",
        "city",
        "pin_code",
    )
    ordering = ("created_date",)
    search_fields = (
        "user__username__icontains",
        "user__email__icontains",
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
