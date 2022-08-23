from typing import Any

from django.core.management import BaseCommand
from django.test import RequestFactory

from apps.sales.utils import half_even_context
from apps.sales.views.views import PinterestCatalog


class Command(BaseCommand):
    @half_even_context
    def handle(self, *args: Any, **options: Any):
        request = RequestFactory().get('/api/sales/v1/pinterest-catalog/')
        output = PinterestCatalog.as_view()(request)
        output.render()
        print(output.content.decode('utf-8'))

