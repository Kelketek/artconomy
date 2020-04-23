from collections import defaultdict
from csv import DictReader, DictWriter
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
from typing import TypedDict,  List, TextIO, Dict

from dateutil.relativedelta import relativedelta
from django.core.management import BaseCommand, CommandParser
from django.core.management.base import OutputWrapper
from moneyed import Money

from apps.lib.permissions import Any
from apps.sales.models import LineItemSim
from apps.sales.utils import get_totals, decimal_context


def file_to_date(file_date: str) -> date:
    day_string = file_date.split()[0]
    sections = list(map(int, day_string.split('/')))
    return date(month=sections[0], day=sections[1], year=sections[2])


class SettlementSpec(TypedDict):
    amount: Decimal
    fees: Decimal


DateMap = Dict[date, SettlementSpec]


class DateParams(TypedDict):
    settlement_dates: List[date]
    earliest_settlement: date
    latest_settlement: date


@dataclass(eq=True, frozen=True)
class CaptureSpec:
    amount: Decimal
    auth_date: date
    auth_code: str


TransactionSets = Dict[date, List[CaptureSpec]]


def get_date_map(settlements: TextIO) -> DateMap:
    """
    Given default output parameters from EVO's 'Billing & Deposits -> Funds settled'
    report, output a by-date spec of the amount of money deposited and
    """
    settlements = DictReader(settlements)
    date_map = defaultdict(lambda: {'amount': Decimal('0.00'), 'fees': Decimal('0.00')})
    for settlement in settlements:
        current = date_map[file_to_date(settlement['FileDate'])]
        current['amount'] += Decimal(settlement['Deposit'])
        current['fees'] += -Decimal(settlement['Discount'])
    return date_map


def get_transaction_sets(*, dates: DateParams, transactions: TextIO, output: OutputWrapper) -> TransactionSets:
    """
    Given default output parameters from EVO's 'Transactions -> Settlements'
    report, output a by-date spec of charges that were rolled into a date_map
    as created by get_date_map
    """
    transactions = DictReader(transactions)
    transaction_sets = defaultdict(list)
    for transaction in transactions:
        target_date = file_to_date(transaction['FileDate'])
        while target_date not in dates['settlement_dates']:
            target_date += relativedelta(days=1)
            if target_date > dates['latest_settlement']:
                print(f'Settlement not yet reached for {transaction["FileDate"]}', file=output)
                break
        if target_date > dates['latest_settlement']:
            break
        current_set: List[CaptureSpec] = transaction_sets[target_date]
        current_set.append(
            CaptureSpec(
                amount=Decimal(
                    transaction['SettleAmount']),
                auth_date=file_to_date(transaction['AuthDate']),
                auth_code=transaction['ApprovalCode'],
            ),
        )
    return transaction_sets


def normalize_earliest(
        *, transaction_sets: TransactionSets, date_map: DateMap, dates: DateParams, output: OutputWrapper,
) -> TransactionSets:
    """
    Verifies we have all the data we need for the first settlement date.
    Since we're running two different reports, we could end up with partial
    information for the first settlement.
    """
    if dates['earliest_settlement'] not in transaction_sets:
        return transaction_sets
    new_set = {**transaction_sets}
    new_transactions = []
    target_amount = date_map[dates['earliest_settlement']]['amount']
    for amount in reversed(transaction_sets[dates['earliest_settlement']]):
        new_transactions.append(amount)
        running_total = sum(item.amount for item in new_transactions)
        if running_total == target_amount:
            # Everything adds up. The rest of these transactions are old and can be discarded.
            new_set[dates['earliest_settlement']] = list(reversed(new_transactions))
            break
    else:
        print(f'Need to go further back to account for settlement on date {dates["earliest_settlement"]}', file=output)
        del new_set[dates['earliest_settlement']]
    return new_set


def normalize_latest(
        *, transaction_sets: TransactionSets, date_map: DateMap, dates: DateParams, output: OutputWrapper,
) -> TransactionSets:
    """
    Verifies we have all the data we need for the last settlement date.
    Since we're running two different reports, we could end up with partial
    information for the last settlement.
    """
    if dates['latest_settlement'] not in transaction_sets:
        return transaction_sets
    new_set = {**transaction_sets}
    target_total = sum(item.amount for item in new_set[dates['latest_settlement']])
    if date_map[dates['latest_settlement']]['amount'] != target_total:
        print(f'Entries for settlement on date {dates["latest_settlement"]} are incomplete. Dropping.', file=output)
        del new_set[dates['latest_settlement']]
    return new_set


def settlement_sanity_check(transaction_sets: TransactionSets, date_map: DateMap):
    for key, value in sorted(transaction_sets.items()):
        total = sum(item.amount for item in value)
        settlement_total = date_map[key]['amount']
        if total != settlement_total:
            raise RuntimeError(
                f'Insane value for date {key}. Transactions totaled to {total} but settlement was {settlement_total}',
            )


def divvy_fees(transactions: List[CaptureSpec], fees: Decimal):
    counter = 0

    def inc():
        nonlocal counter
        counter += 1
        return counter

    line_item_set = tuple(
        (
            LineItemSim(priority=0, amount=Money(capture_spec.amount, 'USD'), id=inc()),
            capture_spec,
        )
        for capture_spec in transactions
    )
    lines = (list((item for item, _ in line_item_set)) +
             [LineItemSim(priority=1, amount=Money(fees, 'USD'), cascade_amount=True, id=inc())])
    total, line_totals = get_totals(lines)
    return (
        (spec, spec.amount - line_totals[line].amount) for line, spec in line_item_set
    )


def output_csv(*, transaction_sets: TransactionSets, date_map: DateMap, output: OutputWrapper):
    writer = DictWriter(
        output,
        fieldnames=[
            'auth_date',
            'auth_code',
            'settlement_date',
            'amount',
            'fee',
            'fee_as_percentage',
            'batch_gross',
            'batch_fees',
            'batch_net_deposit',
        ],
    )
    writer.writeheader()
    for key, value in sorted(transaction_sets.items()):
        writer.writerows({
            'auth_date': transaction.auth_date,
            'auth_code': transaction.auth_code,
            'settlement_date': key,
            'amount': transaction.amount,
            'fee': fee,
            'fee_as_percentage': ((fee / transaction.amount) * Decimal('100')).quantize(Decimal('0.00')),
            'batch_gross': date_map[key]['amount'],
            'batch_fees': date_map[key]['fees'],
            'batch_net_deposit': date_map[key]['amount'] - date_map[key]['fees'],
        } for transaction, fee in divvy_fees(value, date_map[key]['fees']))


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--transactions',
            required=True,
            help="Path to transaction CSV export from the 'Transactions -> Settlements' "
                 "section of EVO's reporting tools.",
        )
        parser.add_argument(
            '--settlements',
            required=True,
            help="Path to transaction CSV export from the 'Billing & Deposits -> Funds settled' "
                 "section of EVO's reporting tools.",
        )

    @decimal_context
    def handle(self, *args: Any, **options: Any):
        with open(options['settlements'], 'r') as settlements:
            date_map = get_date_map(settlements)
        settlement_dates = sorted(date_map.keys())
        earliest_settlement, latest_settlement = settlement_dates[0], settlement_dates[-1]
        dates: DateParams = {
            'earliest_settlement': earliest_settlement,
            'latest_settlement': latest_settlement,
            'settlement_dates': settlement_dates,
        }
        with open(options['transactions'], 'r') as transactions:
            transaction_sets = get_transaction_sets(dates=dates, transactions=transactions, output=self.stderr)
        transaction_sets = normalize_earliest(
            transaction_sets=transaction_sets, dates=dates, date_map=date_map, output=self.stderr,
        )
        transaction_sets = normalize_latest(
            transaction_sets=transaction_sets, dates=dates, date_map=date_map, output=self.stderr,
        )
        settlement_sanity_check(transaction_sets, date_map)
        output_csv(transaction_sets=transaction_sets, date_map=date_map, output=self.stdout)
