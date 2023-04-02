from decimal import Decimal

from django.test import TestCase
from moneyed import Money

from apps.sales.line_item_funcs import lines_by_priority, get_totals, reckon_lines, to_distribute, divide_amount
from apps.sales.models import LineItemSim


class TestLineCalculations(TestCase):
    maxDiff = None

    def test_line_sort(self):
        lines = [
            LineItemSim(amount=Money('5', 'USD'), priority=0, id=1),
            LineItemSim(amount=Money('6', 'USD'), priority=1, id=2),
            LineItemSim(amount=Money('7', 'USD'), priority=2, id=3),
            LineItemSim(amount=Money('8', 'USD'), priority=2, id=4),
            LineItemSim(amount=Money('9', 'USD'), priority=1, id=5),
            LineItemSim(amount=Money('10', 'USD'), priority=-1, id=6),
        ]
        priority_set = lines_by_priority(lines)
        expected_result = [
            [LineItemSim(amount=Money('10', 'USD'), priority=-1, id=6)],
            [LineItemSim(amount=Money('5', 'USD'), priority=0, id=1)],
            [
                LineItemSim(amount=Money('6', 'USD'), priority=1, id=2),
                LineItemSim(amount=Money('9', 'USD'), priority=1, id=5),
            ],
            [
                LineItemSim(amount=Money('7', 'USD'), priority=2, id=3),
                LineItemSim(amount=Money('8', 'USD'), priority=2, id=4),
            ],
        ]
        self.assertEqual(
            priority_set,
            expected_result,
        )

    def test_get_totals_single_line(self):
        source = [LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1)]
        result = get_totals(source)
        self.assertEqual(
            result,
            (
                Money('10.00', 'USD'),
                Money('0.00', 'USD'),
                {LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1): Money('10.00', 'USD')},
            ),
        )
        self.assertEqual(result[0], sum(result[2].values()))

    def test_get_totals_percentage_line(self):
        source = [
            LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1),
            LineItemSim(percentage=Decimal(10), priority=1, id=2),
        ]
        result = get_totals(source)
        self.assertEqual(
            result,
            (
                Money('11.00', 'USD'),
                Money('0.00', 'USD'),
                {
                    LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1): Money('10.00', 'USD'),
                    LineItemSim(percentage=Decimal(10), priority=1, id=2): Money('1.00', 'USD'),
                },
            ),
        )
        self.assertEqual(result[0], sum(result[2].values()))

    def test_get_totals_percentage_cascade(self):
        source = [
            LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1),
            LineItemSim(percentage=Decimal(10), priority=1, cascade_percentage=True, id=2),
        ]
        result = get_totals(source)
        self.assertEqual(
            result,
            (
                Money('10.00', 'USD'),
                Money('0.00', 'USD'),
                {
                    LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1): Money('9.00', 'USD'),
                    LineItemSim(
                        percentage=Decimal(10), priority=1, cascade_percentage=True, id=2,
                    ): Money('1.00', 'USD'),
                },
            ),
        )
        self.assertEqual(result[0], sum(result[2].values()))

    def test_get_totals_percentage_backed_in_cascade(self):
        source = [
            LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1),
            LineItemSim(percentage=Decimal(10), priority=1, cascade_percentage=True, back_into_percentage=True, id=2),
        ]
        result = get_totals(source)
        self.assertEqual(
            result,
            (
                Money('10.00', 'USD'),
                Money('0.00', 'USD'),
                {
                    LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1): Money('9.09', 'USD'),
                    LineItemSim(
                        percentage=Decimal(10), priority=1, cascade_percentage=True, back_into_percentage=True, id=2,
                    ):
                        Money('0.91', 'USD'),
                },
            ),
        )
        self.assertEqual(result[0], sum(result[2].values()))

    def test_get_totals_percentage_with_static(self):
        source = [
            LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1),
            LineItemSim(percentage=Decimal(10), amount=Money('.25', 'USD'), priority=1, id=2),
        ]
        result = get_totals(source)
        self.assertEqual(
            result,
            (
                Money('11.25', 'USD'),
                Money('0.00', 'USD'),
                {
                    LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1): Money('10.00', 'USD'),
                    LineItemSim(
                        percentage=Decimal(10), amount=Money('.25', 'USD'), priority=1,
                        id=2,
                    ): Money('1.25', 'USD'),
                },
            ),
        )
        self.assertEqual(result[0], sum(result[2].values()))

    def test_get_totals_percentage_with_static_cascade(self):
        source = [
            LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1),
            LineItemSim(
                percentage=Decimal(10), amount=Money('.25', 'USD'), priority=1, cascade_percentage=True,
                cascade_amount=True, id=2,
            ),
        ]
        result = get_totals(source)
        self.assertEqual(
            result,
            (
                Money('10.00', 'USD'),
                Money('0.00', 'USD'),
                {
                    LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1): Money('8.75', 'USD'),
                    LineItemSim(
                        percentage=Decimal(10), amount=Money('.25', 'USD'), priority=1, cascade_percentage=True,
                        cascade_amount=True, id=2,
                    ): Money('1.25', 'USD'),
                },
            ),
        )
        self.assertEqual(result[0], sum(result[2].values()))

    def test_get_totals_percentage_no_cascade_amount(self):
        source = [
            LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1),
            LineItemSim(
                percentage=Decimal(10), amount=Money('.25', 'USD'), priority=1, cascade_percentage=True,
                cascade_amount=False, id=2,
            ),
        ]
        result = get_totals(source)
        self.assertEqual(
            result,
            (
                Money('10.25', 'USD'),
                Money('0.00', 'USD'),
                {
                    LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1): Money('9.00', 'USD'),
                    LineItemSim(
                        percentage=Decimal(10), amount=Money('.25', 'USD'), priority=1, cascade_percentage=True,
                        cascade_amount=False, id=2,
                    ): Money('1.25', 'USD'),
                },
            ),
        )
        self.assertEqual(result[0], sum(result[2].values()))

    def test_get_totals_concurrent_priorities(self):
        source = [
            LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1),
            LineItemSim(percentage=Decimal(10), priority=1, id=2),
            LineItemSim(percentage=Decimal(5), priority=1, id=3),
        ]
        result = get_totals(source)
        self.assertEqual(
            result,
            (
                Money('11.50', 'USD'),
                Money('0.00', 'USD'),
                {
                    LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1): Money('10.00', 'USD'),
                    LineItemSim(percentage=Decimal(10), priority=1, id=2): Money('1.00', 'USD'),
                    LineItemSim(percentage=Decimal(5), priority=1, id=3): Money('.50', 'USD'),
                },
            ),
        )
        self.assertEqual(result[0], sum(result[2].values()))

    def test_get_totals_concurrent_priorities_cascade(self):
        source = [
            LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1),
            LineItemSim(percentage=Decimal(10), priority=1, cascade_percentage=True, id=2),
            LineItemSim(percentage=Decimal(5), priority=1, cascade_percentage=True, id=3),
        ]
        result = get_totals(source)
        self.assertEqual(
            result,
            (
                Money('10.00', 'USD'),
                Money('0.00', 'USD'),
                {
                    LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1): Money('8.50', 'USD'),
                    LineItemSim(
                        percentage=Decimal(10), priority=1, cascade_percentage=True, id=2,
                    ): Money('1.00', 'USD'),
                    LineItemSim(percentage=Decimal(5), priority=1, cascade_percentage=True, id=3): Money('.50', 'USD'),
                },
            ),
        )
        self.assertEqual(result[0], sum(result[2].values()))

    def test_get_totals_multi_priority_cascade(self):
        source = [
            LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1),
            LineItemSim(percentage=Decimal(20), priority=1, cascade_percentage=True, id=2),
            LineItemSim(percentage=Decimal(10), priority=2, cascade_percentage=True, id=3),
        ]
        result = get_totals(source)
        self.assertEqual(
            result,
            (
                Money('10.00', 'USD'),
                Money('0.00', 'USD'),
                {
                    LineItemSim(amount=Money('10.00', 'USD'), priority=0, id=1): Money('7.20', 'USD'),
                    LineItemSim(
                        percentage=Decimal(20), priority=1, cascade_percentage=True, id=2,
                    ): Money('1.80', 'USD'),
                    # Level 2 pulls from both lower levels to get its total.
                    LineItemSim(
                        percentage=Decimal(10), priority=2, cascade_percentage=True, id=3,
                    ): Money('1.00', 'USD'),
                },
            ),
        )
        self.assertEqual(result[0], sum(result[2].values()))

    def test_get_totals_multi_priority_cascade_on_concurrent_priority(self):
        source = [
            LineItemSim(amount=Money('2.00', 'USD'), priority=0, id=1),
            LineItemSim(amount=Money('8.00', 'USD'), priority=0, id=2),
            LineItemSim(percentage=Decimal(20), priority=1, cascade_percentage=True, id=3),
            LineItemSim(percentage=Decimal(10), priority=2, cascade_percentage=True, id=4),
        ]
        result = get_totals(source)
        self.assertEqual(
            result,
            (
                Money('10.00', 'USD'),
                Money('0.00', 'USD'),
                {
                    LineItemSim(amount=Money('2.00', 'USD'), priority=0, id=1): Money('1.44', 'USD'),
                    LineItemSim(amount=Money('8.00', 'USD'), priority=0, id=2): Money('5.76', 'USD'),
                    LineItemSim(
                        percentage=Decimal(20), priority=1, cascade_percentage=True, id=3,
                    ): Money('1.80', 'USD'),
                    LineItemSim(
                        percentage=Decimal(10), priority=2, cascade_percentage=True, id=4,
                    ): Money('1.00', 'USD'),
                },
            ),
        )
        self.assertEqual(result[0], sum(result[2].values()))

    def test_fixed_point_decisions(self):
        source = [
            LineItemSim(amount=Money('100', 'USD'), priority=0, id=1),
            LineItemSim(amount=Money('5.00', 'USD'), priority=100, id=2),
            LineItemSim(
                amount=Money('5.00', 'USD'), percentage=Decimal(10), cascade_percentage=True, priority=300, id=3,
            ),
            LineItemSim(percentage=Decimal('8.25'), cascade_percentage=True, priority=600, id=4)
        ]
        result = get_totals(source)
        self.assertEqual(
            result,
            (
                Money('110.00', 'USD'),
                Money('0.00', 'USD'),
                {
                    LineItemSim(amount=Money('100', 'USD'), priority=0, id=1): Money('82.57', 'USD'),
                    LineItemSim(amount=Money('5.00', 'USD'), priority=100, id=2): Money('4.12', 'USD'),
                    LineItemSim(
                        amount=Money('5.00', 'USD'), percentage=Decimal(10), cascade_percentage=True, priority=300,
                        id=3,
                    ): Money('14.23', 'USD'),
                    LineItemSim(
                        percentage=Decimal('8.25'), cascade_percentage=True, priority=600, id=4,
                    ): Money('9.08', 'USD'),
                }
            )
        )
        self.assertEqual(result[0], sum(result[2].values()))

    def test_fixed_point_calculations_2(self):
        source = [
            LineItemSim(amount=Money('20', 'USD'), priority=0, id=1),
            LineItemSim(amount=Money('10.00', 'USD'), priority=100, id=2),
            LineItemSim(
                amount=Money('5.00', 'USD'), percentage=Decimal(10), cascade_percentage=True, priority=300, id=3,
            ),
            LineItemSim(percentage=Decimal('8.25'), cascade_percentage=True, priority=600, id=4)
        ]
        result = get_totals(source)
        self.assertEqual(
            result,
            (
                Money('35.00', 'USD'),
                Money('0.00', 'USD'),
                {
                    LineItemSim(amount=Money('20', 'USD'), priority=0, id=1): Money('16.51', 'USD'),
                    LineItemSim(amount=Money('10.00', 'USD'), priority=100, id=2): Money('8.25', 'USD'),
                    LineItemSim(
                        amount=Money('5.00', 'USD'), percentage=Decimal(10), cascade_percentage=True, priority=300, id=3,
                    ): Money('7.35', 'USD'),
                    LineItemSim(
                        percentage=Decimal('8.25'), cascade_percentage=True, priority=600, id=4,
                    ): Money('2.89', 'USD'),
                }
            )
        )
        self.assertEqual(result[0], sum(result[2].values()))

    def test_fixed_point_calculations_3(self):
        source = [
            LineItemSim(amount=Money('20', 'USD'), priority=0, id=1),
            LineItemSim(amount=Money('5.00', 'USD'), priority=100, id=2),
            LineItemSim(
                amount=Money('5.00', 'USD'), percentage=Decimal(10), cascade_percentage=True, priority=300, id=3,
            ),
            LineItemSim(percentage=Decimal('8.25'), cascade_percentage=True, priority=600, id=4)
        ]
        result = get_totals(source)
        self.assertEqual(
            result,
            (
                Money('30.00', 'USD'),
                Money('0.00', 'USD'),
                {
                    LineItemSim(amount=Money('20', 'USD'), priority=0, id=1): Money('16.51', 'USD'),
                    LineItemSim(amount=Money('5.00', 'USD'), priority=100, id=2): Money('4.12', 'USD'),
                    LineItemSim(
                        amount=Money('5.00', 'USD'), percentage=Decimal(10), cascade_percentage=True, priority=300, id=3,
                    ): Money('6.89', 'USD'),
                    LineItemSim(
                        percentage=Decimal('8.25'), cascade_percentage=True, priority=600, id=4,
                    ): Money('2.48', 'USD'),
                }
            )
        )
        self.assertEqual(result[0], sum(result[2].values()))

    def test_reckon_lines(self):
        source = [
            LineItemSim(amount=Money('1.00', 'USD'), priority=0, id=1),
            LineItemSim(amount=Money('5.00', 'USD'), priority=1, id=2),
            LineItemSim(amount=Money('4.00', 'USD'), priority=2, id=3),
        ]
        self.assertEqual(reckon_lines(source), Money('10.00', 'USD'))

    def test_complex_discount(self):
        source = [
            LineItemSim(amount=Money('0.01', 'USD'), priority=0, id=1),
            LineItemSim(amount=Money('0.01', 'USD'), priority=100, id=2),
            LineItemSim(amount=Money('0.01', 'USD'), priority=100, id=3),
            LineItemSim(amount=Money('-5.00', 'USD'), priority=100, id=4),
            LineItemSim(amount=Money('10.00', 'USD'), priority=100, id=5),
            LineItemSim(
                amount=Money('.75', 'USD'),
                percentage=Decimal('8'),
                cascade_percentage=True,
                cascade_amount=True,
                priority=300,
                id=6,
            ),
        ]
        result = get_totals(source)
        result = list(result)
        result[2] = list(sorted(result[2].items(), key=lambda x: x[0].id))
        self.assertEqual(
            result,
            [
                Money('5.03', 'USD'),
                Money('-5.00', 'USD'),
                [
                    (LineItemSim(amount=Money('0.01', 'USD'), priority=0, id=1), Money('0.00', 'USD')),
                    (LineItemSim(amount=Money('0.01', 'USD'), priority=100, id=2), Money('0.00', 'USD')),
                    (LineItemSim(amount=Money('0.01', 'USD'), priority=100, id=3), Money('0.01', 'USD')),
                    (LineItemSim(amount=Money('-5.00', 'USD'), priority=100, id=4), Money('-5.00', 'USD')),
                    (LineItemSim(amount=Money('10.00', 'USD'), priority=100, id=5), Money('8.86', 'USD')),
                    (LineItemSim(
                        amount=Money('.75', 'USD'),
                        percentage=Decimal('8'),
                        priority=300,
                        cascade_amount=True,
                        cascade_percentage=True,
                        id=6,
                    ), Money('1.16', 'USD')),
                ]
            ]
        )

    def test_zero_total(self):
        source = [
            LineItemSim(amount=Money('0', 'USD'), priority=0, id=1),
            LineItemSim(amount=Money('8', 'USD'), cascade_percentage=True, cascade_amount=True, priority=100, id=2),
        ]
        result = get_totals(source)
        self.assertEqual(
            result,
            (
                Money('0.00', 'USD'),
                Money('0.00', 'USD'),
                {
                    LineItemSim(amount=Money('0', 'USD'), priority=0, id=1): Money('-8.00', 'USD'),
                    LineItemSim(
                        amount=Money('8.00', 'USD'),
                        cascade_percentage=True,
                        cascade_amount=True,
                        priority=100,
                        id=2,
                    ): Money('8.00', 'USD'),
                }
            )
        )

    def test_negative_distribution(self):
        """
        In this case, there's a fee that isn't entirely absorbed by the other line items.
        """
        source = [
            LineItemSim(amount=Money('1', 'USD'), priority=0, id=1),
            LineItemSim(amount=Money('1', 'USD'), priority=1, id=2),
            LineItemSim(amount=Money('4', 'USD'), priority=1, id=3),
            LineItemSim(amount=Money('8', 'USD'), cascade_amount=True, priority=100, id=4),
        ]
        result = get_totals(source)
        self.assertEqual(
            result,
            (
                Money('6.00', 'USD'),
                Money('0.00', 'USD'),
                {
                    LineItemSim(id=1, priority=0, amount=Money('1', 'USD')): Money('-0.34', 'USD'),
                    LineItemSim(id=2, priority=1, amount=Money('1', 'USD')): Money('-0.33', 'USD'),
                    LineItemSim(id=3, priority=1, amount=Money('4', 'USD')): Money('-1.33', 'USD'),
                    LineItemSim(
                        id=4,
                        priority=100,
                        amount=Money('8', 'USD'),
                        cascade_amount=True,
                    ): Money('8.00', 'USD'),
                }
            )
        )

    def test_non_cascading_percentage(self):
        """
        Test percentage amounts that are backed into, but not cascaded.
        """
        source = [
            LineItemSim(amount=Money('5', 'USD'), priority=0, id=1),
            LineItemSim(amount=Money('1', 'USD'), priority=1, id=2),
            LineItemSim(amount=Money('4', 'USD'), priority=1, id=3),
            LineItemSim(percentage=Decimal('5'), back_into_percentage=True, priority=100, id=4),
        ]
        result = get_totals(source)
        self.assertEqual(
            result,
            (
                Money('10.52', 'USD'),
                Money('0.00', 'USD'),
                {
                    LineItemSim(id=1, priority=0, amount=Money('5', 'USD'), percentage=Decimal('0'), back_into_percentage=False): Money('5.00', 'USD'),
                    LineItemSim(id=2, priority=1, amount=Money('1', 'USD'), percentage=Decimal('0'), back_into_percentage=False): Money('1.00', 'USD'),
                    LineItemSim(id=3, priority=1, amount=Money('4', 'USD'), percentage=Decimal('0'), back_into_percentage=False): Money('4.00', 'USD'),
                    LineItemSim(id=4, priority=100, amount=Money('0', 'USD'), percentage=Decimal('5'), back_into_percentage=True): Money('0.52', 'USD'),
            })

        )

    def test_handles_many_transactions_divvied_up_for_fees(self):
        source = [
            LineItemSim(amount=Money('25.00', 'USD'), priority=0, cascade_amount=False, id=1),
            LineItemSim(amount=Money('25.00', 'USD'), priority=0, cascade_amount=False, id=2),
            LineItemSim(amount=Money('35.00', 'USD'), priority=0, cascade_amount=False, id=3),
            LineItemSim(amount=Money('55.00', 'USD'), priority=0, cascade_amount=False, id=4),
            LineItemSim(amount=Money('10.00', 'USD'), priority=0, cascade_amount=False, id=5),
            LineItemSim(amount=Money('5.00', 'USD'), priority=0, cascade_amount=False, id=6),
            LineItemSim(amount=Money('30.00', 'USD'), priority=0, cascade_amount=False, id=7),
            LineItemSim(amount=Money('55.00', 'USD'), priority=0, cascade_amount=False, id=8),
            LineItemSim(amount=Money('25.00', 'USD'), priority=0, cascade_amount=False, id=9),
            LineItemSim(amount=Money('5.00', 'USD'), priority=0, cascade_amount=False, id=10),
            LineItemSim(amount=Money('6.00', 'USD'), priority=0, cascade_amount=False, id=11),
            LineItemSim(amount=Money('25.00', 'USD'), priority=0, cascade_amount=False, id=12),
            LineItemSim(amount=Money('6.00', 'USD'), priority=0, cascade_amount=False, id=13),
            LineItemSim(amount=Money('3.00', 'USD'), priority=0, cascade_amount=False, id=14),
            LineItemSim(amount=Money('5.00', 'USD'), priority=0, cascade_amount=False, id=15),
            LineItemSim(amount=Money('10.06', 'USD'), priority=1, cascade_amount=True, id=16),
        ]
        result = get_totals(source)
        self.assertEqual(
            result,
            (
                Money('315', 'USD'),
                Money('0.00', 'USD'),
                {
                    LineItemSim(
                        amount=Money('25.00', 'USD'),
                        back_into_percentage=False,
                        cascade_amount=False,
                        cascade_percentage=False,
                        description='',
                        id=1,
                        percentage=Decimal('0.00'),
                        priority=0,
                        type=0,
                    ): Money('24.20', 'USD'),
                    LineItemSim(
                        amount=Money('25.00', 'USD'),
                        back_into_percentage=False,
                        cascade_amount=False,
                        cascade_percentage=False,
                        description='',
                        id=2,
                        percentage=Decimal('0.00'),
                        priority=0,
                        type=0,
                    ): Money('24.20', 'USD'),
                    LineItemSim(
                        amount=Money('35.00', 'USD'),
                        back_into_percentage=False,
                        cascade_amount=False,
                        cascade_percentage=False,
                        description='',
                        id=3,
                        percentage=Decimal('0.00'),
                        priority=0,
                        type=0,
                    ): Money('33.89', 'USD'),
                    LineItemSim(
                        amount=Money('55.00', 'USD'),
                        back_into_percentage=False,
                        cascade_amount=False,
                        cascade_percentage=False,
                        description='',
                        id=4,
                        percentage=Decimal('0.00'),
                        priority=0,
                        type=0,
                    ): Money('53.25', 'USD'),
                    LineItemSim(
                        amount=Money('10.00', 'USD'),
                        back_into_percentage=False,
                        cascade_amount=False,
                        cascade_percentage=False,
                        description='',
                        id=5,
                        percentage=Decimal('0.00'),
                        priority=0,
                        type=0,
                    ): Money('9.68', 'USD'),
                    LineItemSim(
                        amount=Money('5.00', 'USD'),
                        back_into_percentage=False,
                        cascade_amount=False,
                        cascade_percentage=False,
                        description='',
                        id=6,
                        percentage=Decimal('0.00'),
                        priority=0,
                        type=0,
                    ): Money('4.84', 'USD'),
                    LineItemSim(
                        amount=Money('30.00', 'USD'),
                        back_into_percentage=False,
                        cascade_amount=False,
                        cascade_percentage=False,
                        description='',
                        id=7,
                        percentage=Decimal('0.00'),
                        priority=0,
                        type=0,
                    ): Money('29.04', 'USD'),
                    LineItemSim(
                        amount=Money('55.00', 'USD'),
                        back_into_percentage=False,
                        cascade_amount=False,
                        cascade_percentage=False,
                        description='',
                        id=8,
                        percentage=Decimal('0.00'),
                        priority=0,
                        type=0,
                    ): Money('53.25', 'USD'),
                    LineItemSim(
                        amount=Money('25.00', 'USD'),
                        back_into_percentage=False,
                        cascade_amount=False,
                        cascade_percentage=False,
                        description='',
                        id=9,
                        percentage=Decimal('0.00'),
                        priority=0,
                        type=0,
                    ): Money('24.2', 'USD'),
                    LineItemSim(
                        amount=Money('5.00', 'USD'),
                        back_into_percentage=False,
                        cascade_amount=False,
                        cascade_percentage=False,
                        description='',
                        id=10,
                        percentage=Decimal('0.00'),
                        priority=0,
                        type=0,
                    ): Money('4.84', 'USD'),
                    LineItemSim(
                        amount=Money('6', 'USD'),
                        back_into_percentage=False,
                        cascade_amount=False,
                        cascade_percentage=False,
                        description='',
                        id=11,
                        percentage=Decimal('0.00'),
                        priority=0,
                        type=0,
                    ): Money('5.80', 'USD'),
                    LineItemSim(
                        amount=Money('25.00', 'USD'),
                        back_into_percentage=False,
                        cascade_amount=False,
                        cascade_percentage=False,
                        description='',
                        id=12,
                        percentage=Decimal('0.00'),
                        priority=0,
                        type=0,
                    ): Money('24.2', 'USD'),
                    LineItemSim(
                        amount=Money('6', 'USD'),
                        back_into_percentage=False,
                        cascade_amount=False,
                        cascade_percentage=False,
                        description='',
                        id=13,
                        percentage=Decimal('0.00'),
                        priority=0,
                        type=0,
                    ): Money('5.80', 'USD'),
                    LineItemSim(
                        amount=Money('3.00', 'USD'),
                        back_into_percentage=False,
                        cascade_amount=False,
                        cascade_percentage=False,
                        description='',
                        id=14,
                        percentage=Decimal('0.00'),
                        priority=0,
                        type=0,
                    ): Money('2.90', 'USD'),
                    LineItemSim(
                        amount=Money('5.00', 'USD'),
                        back_into_percentage=False,
                        cascade_amount=False,
                        cascade_percentage=False,
                        description='',
                        id=15,
                        percentage=Decimal('0.00'),
                        priority=0,
                        type=0,
                    ): Money('4.84', 'USD'),
                    LineItemSim(
                        amount=Money('10.06', 'USD'),
                        back_into_percentage=False,
                        cascade_amount=True,
                        cascade_percentage=False,
                        description='',
                        id=16,
                        percentage=Decimal('0.00'),
                        priority=1,
                        type=0,
                    ): Money('10.07', 'USD'),
                },
            )
        )


class TestMoneyHelpers(TestCase):
    def test_divide_amount(self):
        self.assertEqual(
            divide_amount(Money('10', 'USD'), 3),
            [Money('3.34', 'USD'), Money('3.33', 'USD'), Money('3.33', 'USD')],
        )
        self.assertEqual(
            divide_amount(Money('10.01', 'USD'), 3),
            [Money('3.34', 'USD'), Money('3.34', 'USD'), Money('3.33', 'USD')],
        )
        self.assertEqual(
            divide_amount(Money('10.02', 'USD'), 3),
            [Money('3.34', 'USD'), Money('3.34', 'USD'), Money('3.34', 'USD')],
        )
        self.assertEqual(
            divide_amount(Money('10.03', 'USD'), 3),
            [Money('3.35', 'USD'), Money('3.34', 'USD'), Money('3.34', 'USD')],
        )

    def test_divide_non_subunit(self):
        self.assertEqual(
            divide_amount(Money('10000', 'SUR'), 3),
            [Money('3334', 'SUR'), Money('3333', 'SUR'), Money('3333', 'SUR')],
        )
        self.assertEqual(
            divide_amount(Money('10001', 'SUR'), 3),
            [Money('3334', 'SUR'), Money('3334', 'SUR'), Money('3333', 'SUR')],
        )
        self.assertEqual(
            divide_amount(Money('10002', 'SUR'), 3),
            [Money('3334', 'SUR'), Money('3334', 'SUR'), Money('3334', 'SUR')],
        )
        self.assertEqual(
            divide_amount(Money('10003', 'SUR'), 3),
            [Money('3335', 'SUR'), Money('3334', 'SUR'), Money('3334', 'SUR')],
        )
