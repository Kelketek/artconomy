from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand
from django.db import transaction

from apps.lib.models import ref_for_instance
from apps.sales.constants import (
    VENDOR_PAYMENT,
    FUND,
    SUCCESS,
    VENDOR,
    PAID,
    BASE_PRICE,
    HOLDINGS,
)
from apps.sales.models import TransactionRecord, Invoice


class Command(BaseCommand):
    """
    Goes through existing manual payouts and marks them as vendor invoices.
    """

    @transaction.atomic
    def handle(self, *args, **options):
        content_type = ContentType.objects.get_for_model(Invoice)
        records = TransactionRecord.objects.filter(
            status=SUCCESS, category=VENDOR_PAYMENT, source=FUND, payer=None
        ).exclude(targets__content_type=content_type)
        for transaction_record in records:
            invoice = Invoice.objects.create(
                bill_to=None,
                issued_by=transaction_record.payee,
                type=VENDOR,
                status=PAID,
                created_on=transaction_record.created_on,
                paid_on=transaction_record.created_on,
            )
            invoice.line_items.create(
                amount=transaction_record.amount,
                frozen_value=transaction_record.amount,
                destination_user=transaction_record.payee,
                destination_account=HOLDINGS,
                category=VENDOR_PAYMENT,
                type=BASE_PRICE,
                priority=0,
            )
            transaction_record.targets.add(ref_for_instance(invoice))
