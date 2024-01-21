from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from marketplace import views as MarketplaceViews

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),
    path("", include("accounts.urls")),
    path("marketplace/", include("marketplace.urls")),
    path("search/", MarketplaceViews.search, name="search"),
    path("checkout/", MarketplaceViews.checkout, name="checkout"),
    path("", include("orders.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
