"""artconomy URL Configuration
"""
from django.conf.urls import url

from apps.accounts.views import register_dwolla

urlpatterns = [
    url('^v1/register_dwolla/', register_dwolla, name='register_dwolla'),
]
