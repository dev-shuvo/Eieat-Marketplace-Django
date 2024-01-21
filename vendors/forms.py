from django import forms
from .models import Vendor, Category, Food, OpeningHour
from accounts.validators import allow_only_images_validator


class VendorForm(forms.ModelForm):
    vendor_license = forms.FileField(
        widget=forms.FileInput(attrs={"class": "btn btn-danger w-100"}),
        validators=[allow_only_images_validator],
    )

    class Meta:
        model = Vendor
        fields = ["vendor_name", "vendor_license"]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["category_name", "description"]


class FoodForm(forms.ModelForm):
    image = forms.FileField(
        widget=forms.FileInput(attrs={"class": "btn btn-danger w-100"}),
        validators=[allow_only_images_validator],
    )

    class Meta:
        model = Food
        fields = [
            "category",
            "food_name",
            "description",
            "image",
            "is_available",
            "price",
        ]


class OpeningHourForm(forms.ModelForm):
    class Meta:
        model = OpeningHour
        fields = ["day", "from_hour", "to_hour", "is_closed"]
