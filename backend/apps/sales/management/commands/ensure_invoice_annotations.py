from apps.lib.models import ref_for_instance
from apps.sales.models import Deliverable, TransactionRecord
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        for deliverable in Deliverable.objects.exclude(invoice__isnull=True):
            deliverable_ref = ref_for_instance(deliverable)
            invoice_ref = ref_for_instance(deliverable.invoice)
            for transaction in TransactionRecord.objects.filter(
                targets=deliverable_ref
            ):
                transaction.targets.add(invoice_ref)
