from csv import DictReader
from datetime import datetime
from decimal import localcontext, ROUND_HALF_EVEN
from typing import Any, TypedDict, List, Dict

import pendulum
from pendulum import DateTime
from dateutil.relativedelta import relativedelta
from django.core.management import BaseCommand, CommandParser
from django.db.transaction import atomic
from moneyed import Money
from mypy.api import TextIO

from apps.lib.models import ref_for_instance
from apps.sales.models import TransactionRecord
from apps.sales.utils import half_even_context


class TransactionSpec(TypedDict):
    auth_date: DateTime
    settlement_date: DateTime
    auth_code: str
    amount: Money
    fee: Money


TransactionDateSet = Dict[Money, List[TransactionSpec]]

TransactionDateMap = Dict[pendulum.DateTime, TransactionDateSet]


def get_transactions_list(handle: TextIO) -> List[TransactionSpec]:
    return [
        {
            'auth_date': pendulum.parse(line['auth_date'], tzinfo='UTC'),
            'settlement_date': pendulum.parse(line['settlement_date'], tzinfo='UTC'),
            'auth_code': line['auth_code'],
            'amount': Money(line['amount'], 'USD'),
            'fee': Money(line['fee'], 'USD'),
        }
        for line in DictReader(handle)
    ]


def create_fee_transaction(source_transactions: List[TransactionRecord], auth_code: str, fee: Money, date: datetime):
    refs = [ref_for_instance(source_transaction) for source_transaction in source_transactions]
    sub_refs = []
    for relevant_transaction in source_transactions:
        sub_refs.extend(list(relevant_transaction.targets.all()))
    try:
        fee_transaction = TransactionRecord.objects.filter(
            status=TransactionRecord.SUCCESS,
            source=TransactionRecord.UNPROCESSED_EARNINGS,
            destination=TransactionRecord.CARD_TRANSACTION_FEES,
            category=TransactionRecord.THIRD_PARTY_FEE,
            auth_code=auth_code,
            targets__in=refs,
        ).distinct().get()
    except TransactionRecord.DoesNotExist:
        fee_transaction = TransactionRecord.objects.create(
            status=TransactionRecord.SUCCESS,
            source=TransactionRecord.UNPROCESSED_EARNINGS,
            destination=TransactionRecord.CARD_TRANSACTION_FEES,
            category=TransactionRecord.THIRD_PARTY_FEE,
            amount=fee,
        )
    fee_transaction.amount = fee
    fee_transaction.auth_code = auth_code
    fee_transaction.payer = None
    fee_transaction.payee = None
    fee_transaction.created_on = date
    fee_transaction.save()
    fee_transaction.targets.set([*refs] + [*sub_refs])


def distribute_fees(transaction: TransactionSpec):
    candidates = list(TransactionRecord.objects.filter(
        created_on__gte=(transaction['auth_date'] - relativedelta(weeks=1)),
        created_on__lte=(transaction['auth_date'] + relativedelta(weeks=1)),
        auth_code=transaction['auth_code'],
        source=TransactionRecord.CARD,
        status=TransactionRecord.SUCCESS,
    ))
    if not candidates:
        print('No matching transactions found for', transaction)
        return
    total = sum((record.amount for record in candidates))
    if total != transaction['amount']:
        print(f'WARNING: Inexact match found. {total} != {transaction["amount"]}', transaction)
    create_fee_transaction(candidates, transaction['auth_code'], transaction['fee'], candidates[0].created_on)


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--processed',
            required=True,
            help="Path to output CSV from the settlement command."
        )

    @half_even_context
    def handle(self, *args: Any, **options: Any):
        with open(options['processed'], 'r') as processed:
            transactions = get_transactions_list(processed)
        with atomic():
            for transaction in transactions:
                distribute_fees(transaction)
            raise RuntimeError()
