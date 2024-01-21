from django.db import models
from accounts.models import User
from vendors.views import Food


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Cart"

    def __str__(self):
        return self.user.email


class Tax(models.Model):
    tax_type = models.CharField(max_length=20, unique=True)
    tax_percentage = models.DecimalField(decimal_places=2, max_digits=4)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.tax_type
