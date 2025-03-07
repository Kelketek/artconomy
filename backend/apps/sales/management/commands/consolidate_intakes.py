from dateutil.relativedelta import relativedelta
from django.db import transaction
from moneyed import Money

from apps.lib.models import ref_for_instance
from apps.sales.constants import (
    CARD,
    UNPROCESSED_EARNINGS,
    SUCCESS,
    CASH_DEPOSIT,
    FUNDING,
    FUND,
    DEFAULT_TYPE_TO_CATEGORY_MAP,
)
from apps.sales.models import TransactionRecord, Invoice, LineItem
from django.core.management import BaseCommand


class Command(BaseCommand):
    """
    Goes through existing payment transactions and reformats them to go through the fund
    intermediary account rather than immediately split so that reconsiliation is easier.
    """

    @transaction.atomic
    def handle(self, *args, **options):
        # This should handle converting all invoices which exist.
        for invoice in Invoice.objects.filter(record_only=False):
            invoice_ref = ref_for_instance(invoice)
            records = TransactionRecord.objects.filter(
                source__in=[CARD, CASH_DEPOSIT], targets=invoice_ref
            ).exclude(destination=FUND)
            successful = records.filter(status=SUCCESS)
            total = sum(
                record.amount for record in records.filter(status=SUCCESS)
            ) or Money("0.00", "USD")
            if not total:
                continue
            # We need this to be the earliest transaction in the set.
            reference = successful.order_by("created_on")[0]
            reference_finalized = successful.order_by("finalized_on")[0]
            funding_record = TransactionRecord.objects.create(
                source=reference.source,
                destination=FUND,
                amount=total,
                category=FUNDING,
                payer=reference.payer,
                payee=reference.payer,
                status=SUCCESS,
                created_on=reference.created_on - relativedelta(seconds=1),
                finalized_on=reference_finalized.finalized_on
                - relativedelta(seconds=1),
                remote_ids=reference.remote_ids,
            )
            funding_record.targets.set(reference.targets.all())
            for record in successful:
                record.source = FUND
                record.save()

        TransactionRecord.objects.filter(source=UNPROCESSED_EARNINGS).update(
            source=FUND
        )
        TransactionRecord.objects.filter(destination=UNPROCESSED_EARNINGS).update(
            destination=FUND
        )
        LineItem.objects.filter(destination_account=UNPROCESSED_EARNINGS).update(
            destination_account=FUND
        )
        for line_item in LineItem.objects.filter(category__isnull=True):
            line_item.category = DEFAULT_TYPE_TO_CATEGORY_MAP[line_item.type]
            line_item.save()
