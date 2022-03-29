from django.core.management import BaseCommand

from apps.sales.constants import HOLDINGS, SUCCESS, PAYOUT_MIRROR_SOURCE, PAYOUT_MIRROR_DESTINATION, BANK
from apps.sales.models import TransactionRecord


class Command(BaseCommand):
    """
    One-time command to create backdated mirror transactions to make exporting tax reports easier for users.
    """
    def handle(self, *args, **options):
        source_transactions = TransactionRecord.objects.filter(
            source=HOLDINGS, destination=BANK,
            status=SUCCESS,
        ).exclude(payer=None).exclude(payee=None).exclude(remote_id='')
        for transaction in source_transactions:
            destination_transaction = TransactionRecord.objects.filter(
                source=PAYOUT_MIRROR_SOURCE, destination=PAYOUT_MIRROR_DESTINATION,
                payer=transaction.payer, payee=transaction.payee, remote_ids=transaction.remote_ids,
            ).first()
            if destination_transaction:
                return
            destination_transaction = TransactionRecord.objects.create(
                source=PAYOUT_MIRROR_SOURCE, destination=PAYOUT_MIRROR_DESTINATION,
                payer=transaction.payer, payee=transaction.payee, remote_ids=transaction.remote_ids,
                created_on=transaction.created_on, finalized_on=transaction.finalized_on,
                category=transaction.category, status=SUCCESS,
                amount=transaction.amount,
            )
            destination_transaction.targets.set(transaction.targets.all())
