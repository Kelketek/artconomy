from django.core.management import BaseCommand

from apps.sales.dwolla import update_transfer_status
from apps.sales.models import PaymentRecord


class Command(BaseCommand):
    def handle(self, *args, **options):
        records = PaymentRecord.objects.filter(finalized=False, type=PaymentRecord.DISBURSEMENT_SENT)
        # To be transformed into celery tasks when the time comes.
        for record in records:
            update_transfer_status(record)
