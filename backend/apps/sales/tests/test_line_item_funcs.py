from apps.sales.line_item_funcs import (
    divide_amount,
)
from django.test import TestCase
from moneyed import Money


class TestMoneyHelpers(TestCase):
    def test_divide_amount(self):
        self.assertEqual(
            divide_amount(Money("10", "USD"), 3),
            [Money("3.34", "USD"), Money("3.33", "USD"), Money("3.33", "USD")],
        )
        self.assertEqual(
            divide_amount(Money("10.01", "USD"), 3),
            [Money("3.34", "USD"), Money("3.34", "USD"), Money("3.33", "USD")],
        )
        self.assertEqual(
            divide_amount(Money("10.02", "USD"), 3),
            [Money("3.34", "USD"), Money("3.34", "USD"), Money("3.34", "USD")],
        )
        self.assertEqual(
            divide_amount(Money("10.03", "USD"), 3),
            [Money("3.35", "USD"), Money("3.34", "USD"), Money("3.34", "USD")],
        )

    def test_divide_non_subunit(self):
        self.assertEqual(
            divide_amount(Money("10000", "SUR"), 3),
            [Money("3334", "SUR"), Money("3333", "SUR"), Money("3333", "SUR")],
        )
        self.assertEqual(
            divide_amount(Money("10001", "SUR"), 3),
            [Money("3334", "SUR"), Money("3334", "SUR"), Money("3333", "SUR")],
        )
        self.assertEqual(
            divide_amount(Money("10002", "SUR"), 3),
            [Money("3334", "SUR"), Money("3334", "SUR"), Money("3334", "SUR")],
        )
        self.assertEqual(
            divide_amount(Money("10003", "SUR"), 3),
            [Money("3335", "SUR"), Money("3334", "SUR"), Money("3334", "SUR")],
        )
