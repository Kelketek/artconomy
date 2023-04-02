from django.conf import settings
from django.core.management import BaseCommand
from moneyed import Money

from apps.sales.models import Product


class Command(BaseCommand):
    """

    """
    def handle(self, *args, **options):
        """
        Bumps all prices by $5. This is to be one run once after the plan refactor.

        A more robust dynamic price increaser should perhaps be considered down the line, if inflation keeps up.
        """
        for product in Product.objects.filter(escrow_enabled=True):
            product.base_price += Money('5', 'USD')
            product.save()
