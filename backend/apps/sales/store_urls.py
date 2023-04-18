"""artconomy URL Configuration
"""
from apps.sales.views.main import ProductPreview, StorePreview
from django.urls import path

app_name = "sales"

# These URLs/views are for the purpose of getting Meta tag preview information.
# Trailing slashes are not added because the frontend does not use them.


urlpatterns = [
    path("<username>", StorePreview.as_view(), name="store_preview"),
    path("<username>/", StorePreview.as_view(), name="store_preview"),
    path("<username>/iframe", StorePreview.as_view(), name="store_preview_iframe"),
    path("<username>/iframe/", StorePreview.as_view(), name="store_preview_iframe"),
    path(
        "<username>/product/<int:product_id>",
        ProductPreview.as_view(),
        name="product_preview",
    ),
    path(
        "<username>/product/<int:product_id>/",
        ProductPreview.as_view(),
        name="product_preview",
    ),
]
