from csv import DictReader, DictWriter
from datetime import datetime
from typing import Any, TypedDict, List, Dict

import pendulum
from django.core.management.base import OutputWrapper
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
            'batch_gross': line['batch_gross'],
            'batch_fees': line['batch_fees'],
            'batch_net_deposit': line['batch_net_deposit'],
        }
        for line in DictReader(handle)
    ]


def new_output_row(transaction: TransactionSpec, for_note: str, writer: DictWriter):
    row = {
        **transaction,
        'for': for_note,
    }
    row['auth_date'] = row['auth_date'].to_formatted_date_string()
    row['settlement_date'] = row['settlement_date'].to_formatted_date_string()
    row['amount'] = str(row['amount'].amount)
    row['fee'] = str(row['fee'].amount)
    writer.writerow(row)


def create_fee_transaction(
        source_transactions: List[TransactionRecord], transaction: TransactionSpec, date: datetime,
        writer: DictWriter,
):
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
            auth_code=transaction['auth_code'],
            targets__in=refs,
        ).distinct().get()
    except TransactionRecord.DoesNotExist:
        fee_transaction = TransactionRecord.objects.create(
            status=TransactionRecord.SUCCESS,
            source=TransactionRecord.UNPROCESSED_EARNINGS,
            destination=TransactionRecord.CARD_TRANSACTION_FEES,
            category=TransactionRecord.THIRD_PARTY_FEE,
            amount=transaction['fee'],
        )
    fee_transaction.amount = transaction['fee']
    fee_transaction.auth_code = transaction['auth_code']
    fee_transaction.payer = None
    fee_transaction.payee = None
    fee_transaction.created_on = date
    fee_transaction.save()
    all_refs = {*refs, *sub_refs}
    fee_transaction.targets.set(all_refs)
    fee_note = ', '.join(str(ref.target) for ref in all_refs)
    new_output_row(transaction, for_note=fee_note, writer=writer)


def distribute_fees(transaction: TransactionSpec, writer: DictWriter, err: OutputWrapper):
    candidates = list(TransactionRecord.objects.filter(
        created_on__gte=(transaction['auth_date'] - relativedelta(weeks=1)),
        created_on__lte=(transaction['auth_date'] + relativedelta(weeks=1)),
        auth_code=transaction['auth_code'],
        source=TransactionRecord.CARD,
        status=TransactionRecord.SUCCESS,
    ))
    if not candidates:
        new_output_row(transaction, for_note='<UNKNOWN: Transaction made off-site?>', writer=writer)
        print('WARNING: No matching transactions found for', transaction, file=err)
        return
    total = sum((record.amount for record in candidates))
    if total != transaction['amount']:
        print(f'WARNING: Inexact match found. Transactions total to {total} but card was charged {transaction["amount"]}', transaction, file=err)
    create_fee_transaction(candidates, transaction, candidates[0].created_on, writer)


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
        writer = DictWriter(self.stdout, fieldnames=[
            'auth_code',
            'for',
            'amount',
            'fee',
            'batch_gross',
            'batch_fees',
            'batch_net_deposit',
            'auth_date',
            'settlement_date',
        ])
        writer.writeheader()
        with atomic():
            for transaction in transactions:
                distribute_fees(transaction, writer, self.stderr)
