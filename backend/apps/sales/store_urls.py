"""artconomy URL Configuration
"""
from django.urls import path

from apps.sales.views import ProductPreview, StorePreview

app_name = "sales"

# These URLs/views are for the purpose of getting Meta tag preview information.


urlpatterns = [
    path('<username>/iframe/', StorePreview.as_view(), name='store_preview'),
    path('<username>/product/<product_id>', ProductPreview.as_view(), name='product_preview'),
]
