from django.core.management import BaseCommand
from django.db import transaction

from apps.sales.models import Invoice, PAID, LineItem
from apps.sales.utils import freeze_line_items


class Command(BaseCommand):
    def handle(self, *args, **options):
        line_items = LineItem.objects.filter(frozen_value=None, invoice__status=PAID).distinct('invoice')
        for line_item in line_items:
            with transaction.atomic():
                freeze_line_items(line_item.invoice)
