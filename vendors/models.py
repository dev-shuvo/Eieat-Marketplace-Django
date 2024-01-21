from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification
from datetime import date, datetime, time


class Vendor(models.Model):
    user = models.OneToOneField(User, related_name="user", on_delete=models.CASCADE)
    user_profile = models.OneToOneField(
        UserProfile, related_name="userProfile", on_delete=models.CASCADE
    )
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to="vendors/licenses")
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_top = models.BooleanField(default=False)

    def is_open(self):
        today = date.today().isoweekday()
        current_opening_hours = OpeningHour.objects.filter(vendor=self, day=today)
        current_time = datetime.now().strftime("%H:%M:%S")
        is_open = None
        for time in current_opening_hours:
            if not time.is_closed:
                start_time = str(datetime.strptime(time.from_hour, "%I:%M %p").time())
                end_time = str(datetime.strptime(time.to_hour, "%I:%M %p").time())

                if current_time > start_time and current_time < end_time:
                    is_open = True
                    break
                else:
                    is_open = False
        return is_open

    def __str__(self):
        return self.vendor_name

    def save(self, *args, **kwargs):
        if self.pk is not None:
            original_status = Vendor.objects.get(pk=self.pk)

            if original_status.is_approved != self.is_approved:
                mail_template = "accounts/emails/vendor_approval_email.html"
                context = {
                    "user": self.user,
                    "is_approved": self.is_approved,
                    "to_email": self.user.email,
                }
                if self.is_approved == True:
                    mail_subject = "Congratulations! Your restaurant has been approved."
                    send_notification(mail_subject, mail_template, context)
                else:
                    mail_subject = "We're sorry! You are not eligible for publishing your restaurant on our marketplace."
                    send_notification(mail_subject, mail_template, context)

        return super(Vendor, self).save(*args, **kwargs)


class Category(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category_name = models.CharField(unique=True, max_length=50)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_name

    def clean(self):
        self.category_name = self.category_name.capitalize()


class Food(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="foods"
    )
    food_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=250, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="food_images")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.food_name


class OpeningHour(models.Model):
    DAYS = [
        (1, ("Monday")),
        (2, ("Tuesday")),
        (3, ("Wednesday")),
        (4, ("Thursday")),
        (5, ("Friday")),
        (6, ("Saturday")),
        (7, ("Sunday")),
    ]
    HOUR_OF_DAY_24 = [
        (
            time(hour, minute).strftime("%I:%M %p"),
            time(hour, minute).strftime("%I:%M %p"),
        )
        for hour in range(0, 24)
        for minute in (0, 30)
    ]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    to_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ("day", "-from_hour")
        unique_together = ("vendor", "day", "from_hour", "to_hour")

    def __str__(self):
        return self.get_day_display()
