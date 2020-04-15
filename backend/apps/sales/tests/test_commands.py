from io import TextIOWrapper, BytesIO
from pathlib import Path
from unittest import TestCase

from django.core.management.base import OutputWrapper

from apps.sales.management.commands.settlement import DateParams, get_date_map, get_transaction_sets, \
    normalize_earliest, normalize_latest, settlement_sanity_check, output_csv
from django.conf import settings

csv_path = Path(settings.BASE_DIR) / 'backend' / 'apps' / 'sales' / 'tests' / 'csvs'

transactions_path = csv_path / 'transactions.csv'
settlements_path = csv_path / 'settlements.csv'
with open(str(csv_path / 'output.csv')) as ref_file:
    reference_output = ref_file.read()


class TestFunctionalHelpers(TestCase):
    maxDiff = None
    def test_basic_e2e(self):
        error_out = OutputWrapper(TextIOWrapper(buffer=BytesIO()))
        output = OutputWrapper(TextIOWrapper(buffer=BytesIO()))
        with open(str(settlements_path), 'r') as settlements:
            date_map = get_date_map(settlements)
        settlement_dates = sorted(date_map.keys())
        earliest_settlement, latest_settlement = settlement_dates[0], settlement_dates[-1]
        dates: DateParams = {
            'earliest_settlement': earliest_settlement,
            'latest_settlement': latest_settlement,
            'settlement_dates': settlement_dates,
        }
        with open(str(transactions_path), 'r') as transactions:
            transaction_sets = get_transaction_sets(dates=dates, transactions=transactions, output=error_out)
        transaction_sets = normalize_earliest(
            transaction_sets=transaction_sets, dates=dates, date_map=date_map, output=error_out,
        )
        transaction_sets = normalize_latest(
            transaction_sets=transaction_sets, dates=dates, date_map=date_map, output=error_out,
        )
        settlement_sanity_check(transaction_sets, date_map)
        output_csv(transaction_sets=transaction_sets, date_map=date_map, output=output)
        output._out.seek(0)
        self.assertEqual(reference_output, output._out.read())

