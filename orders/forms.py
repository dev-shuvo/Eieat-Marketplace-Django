from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"readonly": "readonly"}))

    class Meta:
        model = Order
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "address",
            "country",
            "state",
            "city",
            "pin_code",
        ]
