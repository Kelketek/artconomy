from collections import defaultdict
from csv import DictReader
from datetime import timedelta
from decimal import Decimal
from typing import Any, TypedDict, List, Dict

import pendulum
from pendulum import DateTime
from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand, CommandParser
from django.db.models import QuerySet
from django.db.transaction import atomic
from moneyed import Money
from mypy.api import TextIO

from apps.lib.models import ref_for_instance
from apps.sales.models import TransactionRecord, Order


class TransactionSpec(TypedDict):
    auth_date: DateTime
    settlement_date: DateTime
    amount: Money
    fee: Money


TransactionDateSet = Dict[Money, List[TransactionSpec]]

TransactionDateMap = Dict[pendulum.DateTime, TransactionDateSet]


def get_transactions_list(handle: TextIO) -> List[TransactionSpec]:
    return [
        {
            'auth_date': pendulum.parse(line['auth_date'], tzinfo='UTC'),
            'settlement_date': pendulum.parse(line['settlement_date'], tzinfo='UTC'),
            'amount': Money(line['amount'], 'USD'),
            'fee': Money(line['fee'], 'USD'),
        }
        for line in DictReader(handle)
    ]


def transaction_date_map(transactions: List[TransactionSpec]) -> TransactionDateMap:
    date_map: defaultdict[DateTime, List[TransactionSpec]] = defaultdict(list)
    for transaction in transactions:
        date_map[transaction['auth_date']].append(transaction)
    deep_map = {}
    for auth_date in date_map.keys():
        amount_sets = defaultdict(list)
        for transaction in date_map[auth_date]:
            amount_sets[transaction['amount']].append(transaction)
        deep_map[auth_date] = dict(amount_sets)
    return deep_map


def match_exact(
        *,
        candidates: QuerySet,
        transactions: List[TransactionSpec],
        amount: Money,
        auth_date: DateTime,
        exclude: List[str],
):
    assigned = []
    transactions = [*transactions]
    order_type = ContentType.objects.get_for_model(Order)
    # Orders are not expected to ever be one-to-one since we split those transactions up.
    exact_candidates = candidates.filter(amount=amount).exclude(
        targets__content_type=order_type,
    ).exclude(id__in=exclude)
    for candidate in exact_candidates:
        if candidate.id in assigned:
            continue
        try:
            transaction = transactions.pop()
        except IndexError:
            print("Leftover exact match candidates on ", auth_date, exact_candidates.exclude(id__in=assigned))
            break
        create_fee_transaction([candidate], transaction['fee'], auth_date)
        assigned.append(candidate.id)
    return assigned, transactions


def create_fee_transaction(source_transactions: List[TransactionRecord], fee: Money, date: DateTime):
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
            targets__in=refs,
        ).get()
    except TransactionRecord.DoesNotExist:
        fee_transaction = TransactionRecord.objects.create(
            status=TransactionRecord.SUCCESS,
            source=TransactionRecord.UNPROCESSED_EARNINGS,
            destination=TransactionRecord.CARD_TRANSACTION_FEES,
            category=TransactionRecord.THIRD_PARTY_FEE,
            amount=fee,
        )
    fee_transaction.amount = fee
    fee_transaction.payer = None
    fee_transaction.payee = None
    fee_transaction.created_on = date.in_timezone('UTC')
    fee_transaction.save()
    fee_transaction.targets.set([*refs] + [*sub_refs])


def match_remaining(
        *,
        candidates: QuerySet,
        transactions: List[TransactionSpec],
        amount: Money,
        auth_date: DateTime,
        exclude: List[str],
):
    assigned = []
    transactions = [*transactions]
    order_type = ContentType.objects.get_for_model(Order)
    # Group by methodology doesn't seem to work as expected across m2m fields. Could diagnose, but faster to just
    # do it in the Python for now.
    summed_candidates = list(candidates.filter(
        targets__content_type=order_type,
    ).exclude(id__in=exclude).values('targets__object_id', 'amount'))
    ids_to_amounts = defaultdict(lambda: Decimal('0.00'))
    for summed in summed_candidates:
        ids_to_amounts[summed['targets__object_id']] += summed['amount']
    ids_to_amounts = {key: value for key, value in ids_to_amounts.items() if value == amount.amount}
    for object_id in ids_to_amounts.keys():
        try:
            transaction = transactions.pop()
        except IndexError:
            print("Leftover non-exact match candidates on ", auth_date, candidates.exclude(id__in=assigned))
            break
        relevant_transactions = list(candidates.filter(targets__object_id=object_id))
        create_fee_transaction(relevant_transactions, transaction['fee'], auth_date)
        assigned.extend([relevant_transaction.id for relevant_transaction in relevant_transactions])
    return assigned, transactions


def distribute_fees(initial_auth_date: DateTime, auth_date: DateTime, transaction_date_set: TransactionDateSet, assigned: List[TransactionRecord]):
    assigned = [*assigned]
    candidates = TransactionRecord.objects.filter(
        created_on__gte=auth_date.to_iso8601_string(),
        created_on__lte=(auth_date + relativedelta(days=1)).to_iso8601_string(),
        source=TransactionRecord.CARD,
        status=TransactionRecord.SUCCESS,
    ).order_by('created_on')
    for amount in transaction_date_set.keys():
        transactions = transaction_date_set[amount]
        new_assigned, transactions = match_exact(
            candidates=candidates, transactions=transactions, amount=amount, auth_date=auth_date,
            exclude=assigned,
        )
        assigned.extend(new_assigned)
        new_assigned, transactions = match_remaining(
            candidates=candidates, transactions=transactions, amount=amount, auth_date=auth_date,
            exclude=assigned,
        )
        assigned.extend(new_assigned)
        if transactions:
            if (initial_auth_date - auth_date) > timedelta(days=2):
                print("Left over transactions on", auth_date, transactions)
            else:
                fake_date = auth_date - relativedelta(days=1)
                fake_set = {amount: transactions}
                distribute_fees(initial_auth_date, fake_date, fake_set, assigned)
            # print(candidates)
    return assigned


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--processed',
            required=True,
            help="Path to output CSV from the settlement command."
        )

    def handle(self, *args: Any, **options: Any):
        with open(options['processed'], 'r') as processed:
            transactions = get_transactions_list(processed)
        date_map = transaction_date_map(transactions)
        with atomic():
            assigned = []
            for auth_date, transaction_set in date_map.items():
                assigned = distribute_fees(auth_date, auth_date, transaction_set, assigned)
            raise RuntimeError
