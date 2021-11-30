import uuid
from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Sum
from django.test import TestCase
from freezegun import freeze_time
from moneyed import Money

from apps.lib.models import Notification, ORDER_UPDATE, Subscription, COMMISSIONS_OPEN
from apps.lib.test_resources import SignalsDisabledMixin
from apps.profiles.models import User
from apps.profiles.tests.factories import UserFactory
from apps.sales.models import TransactionRecord, LineItemSim, CANCELLED, IN_PROGRESS
from apps.sales.tests.factories import TransactionRecordFactory, OrderFactory, ProductFactory, DeliverableFactory, \
    RevisionFactory, ReferenceFactory
from apps.sales.utils import claim_order_by_token, \
    check_charge_required, available_products, set_premium, account_balance, POSTED_ONLY, PENDING, lines_by_priority, \
    get_totals, reckon_lines, destroy_deliverable, divide_amount


class BalanceTestCase(SignalsDisabledMixin, TestCase):
    def setUp(self):
        user1 = UserFactory.create(username='Fox')
        user2 = UserFactory.create(username='Cat')
        transaction = TransactionRecordFactory.create(
            card=None,
            payer=user1,
            payee=user2,
            source=TransactionRecord.CARD,
            destination=TransactionRecord.ESCROW,
            amount=Money('10.00', 'USD')
        )
        user1, user2 = transaction.payer, transaction.payee
        TransactionRecordFactory.create(
            card=None,
            payer=user1,
            payee=user2,
            amount=Money('5.00', 'USD'),
            source=TransactionRecord.RESERVE,
            destination=TransactionRecord.ESCROW,
        )
        TransactionRecordFactory.create(
            card=None,
            payer=user2,
            payee=user1,
            source=TransactionRecord.ESCROW,
            destination=TransactionRecord.ACH_MISC_FEES,
            amount=Money('3.00', 'USD'),
            status=TransactionRecord.PENDING,
        )
        TransactionRecordFactory.create(
            card=None,
            payer=user2,
            payee=user1,
            source=TransactionRecord.ESCROW,
            destination=TransactionRecord.ACH_MISC_FEES,
            amount=Money('3.00', 'USD'),
            status=TransactionRecord.FAILURE,
        )
        TransactionRecordFactory.create(
            card=None,
            payer=user2,
            payee=None,
            source=TransactionRecord.ESCROW,
            destination=TransactionRecord.ACH_MISC_FEES,
            amount=Money('0.50', 'USD'),
            status=TransactionRecord.SUCCESS,
        )
        self.user1 = User.objects.get(username='Fox')
        self.user2 = User.objects.get(username='Cat')
        super().setUp()

    def test_account_balance_available(self):
        self.assertEqual(account_balance(self.user2, TransactionRecord.ESCROW), Decimal('11.50'))
        self.assertEqual(account_balance(self.user1, TransactionRecord.RESERVE), Decimal('-5.00'))
        self.assertEqual(account_balance(None, TransactionRecord.ACH_MISC_FEES), Decimal('0.50'))

    def test_account_balance_posted(self):
        self.assertEqual(account_balance(self.user2, TransactionRecord.ESCROW, POSTED_ONLY), Decimal('14.50'))
        self.assertEqual(account_balance(self.user1, TransactionRecord.RESERVE, POSTED_ONLY), Decimal('-5.00'))
        self.assertEqual(account_balance(None, TransactionRecord.ACH_MISC_FEES, POSTED_ONLY), Decimal('0.50'))

    def test_account_balance_pending(self):
        self.assertEqual(account_balance(self.user2, TransactionRecord.ESCROW, PENDING), Decimal('-3.00'))
        self.assertEqual(account_balance(self.user1, TransactionRecord.RESERVE, PENDING), Decimal('0.00'))
        self.assertEqual(account_balance(None, TransactionRecord.ACH_MISC_FEES, PENDING), Decimal('0.00'))
        self.assertEqual(account_balance(self.user1, TransactionRecord.ACH_MISC_FEES, PENDING), Decimal('3.00'))


class TestClaim(TestCase):
    def test_order_claim(self):
        user = UserFactory.create()
        order = DeliverableFactory.create(order__buyer=None).order
        claim_order_by_token(str(order.claim_token), user)
        order.refresh_from_db()
        self.assertEqual(order.buyer, user)
        self.assertIsNone(order.claim_token)

    def test_order_claim_fail_self(self):
        user = UserFactory.create()
        order = DeliverableFactory.create(order__buyer=None, order__seller=user, product__user=user).order
        original_token = order.claim_token
        claim_order_by_token(str(order.claim_token), user)
        order.refresh_from_db()
        self.assertTrue(order.claim_token)
        self.assertEqual(order.claim_token, original_token)
        self.assertIsNone(order.buyer)

    @patch('apps.sales.utils.transfer_order')
    def test_order_claim_none(self, mock_transfer):
        user = UserFactory.create()
        order = DeliverableFactory.create(order__buyer=None).order
        claim_order_by_token(None, user)
        mock_transfer.assert_not_called()
        order.refresh_from_db()
        self.assertIsNone(order.buyer)

    def test_order_claim_string(self):
        user = UserFactory.create()
        order = DeliverableFactory.create(order__buyer=None).order
        claim_order_by_token(str(order.claim_token), user)
        order.refresh_from_db()
        self.assertEqual(order.buyer, user)
        self.assertIsNone(order.claim_token)

    @patch('apps.sales.utils.logger.warning')
    def test_order_claim_fail(self, mock_warning):
        user = UserFactory.create()
        uid = uuid.uuid4()
        claim_order_by_token(uid, user)
        self.assertTrue(mock_warning.called)

    def test_order_claim_subscription(self):
        user = UserFactory.create()
        deliverable = DeliverableFactory.create(order__buyer=None)
        claim_order_by_token(str(deliverable.order.claim_token), user)
        notification = Notification.objects.get(event__type=ORDER_UPDATE)
        self.assertEqual(notification.user, user)
        self.assertEqual(notification.event.target, deliverable)


class TestCheckChargeRequired(TestCase):
    @freeze_time('2018-02-10 12:00:00')
    def test_check_charge_not_required_landscape(self):
        user = UserFactory.create(landscape_paid_through=date(2018, 2, 12))
        self.assertEqual(check_charge_required(user), (False, date(2018, 2, 12)))


class TestAvailableProducts(TestCase):
    # Basic smoke tests. Can be expanded if stuff breaks, but most of this functionality is tested elsewhere.
    def test_available_products(self):
        user = UserFactory.create()
        product = ProductFactory.create()
        self.assertEqual(list(available_products(user)), [product])

    def test_available_products_ordered(self):
        user = UserFactory.create()
        ProductFactory.create()
        self.assertIn('ORDER BY', str(available_products(user).query))


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
                    LineItemSim(amount=Money('100', 'USD'), priority=0, id=1): Money('82.58', 'USD'),
                    LineItemSim(amount=Money('5.00', 'USD'), priority=100, id=2): Money('4.13', 'USD'),
                    LineItemSim(
                        amount=Money('5.00', 'USD'), percentage=Decimal(10), cascade_percentage=True, priority=300,
                        id=3,
                    ): Money('14.22', 'USD'),
                    LineItemSim(
                        percentage=Decimal('8.25'), cascade_percentage=True, priority=600, id=4,
                    ): Money('9.07', 'USD'),
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
                    LineItemSim(amount=Money('10.00', 'USD'), priority=100, id=2): Money('8.26', 'USD'),
                    LineItemSim(
                        amount=Money('5.00', 'USD'), percentage=Decimal(10), cascade_percentage=True, priority=300, id=3,
                    ): Money('7.34', 'USD'),
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
                    LineItemSim(amount=Money('20', 'USD'), priority=0, id=1): Money('16.52', 'USD'),
                    LineItemSim(amount=Money('5.00', 'USD'), priority=100, id=2): Money('4.13', 'USD'),
                    LineItemSim(
                        amount=Money('5.00', 'USD'), percentage=Decimal(10), cascade_percentage=True, priority=300, id=3,
                    ): Money('6.88', 'USD'),
                    LineItemSim(
                        percentage=Decimal('8.25'), cascade_percentage=True, priority=600, id=4,
                    ): Money('2.47', 'USD'),
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
                    (LineItemSim(amount=Money('0.01', 'USD'), priority=0, id=1), Money('0.01', 'USD')),
                    (LineItemSim(amount=Money('0.01', 'USD'), priority=100, id=2), Money('0.01', 'USD')),
                    (LineItemSim(amount=Money('0.01', 'USD'), priority=100, id=3), Money('0.01', 'USD')),
                    (LineItemSim(amount=Money('-5.00', 'USD'), priority=100, id=4), Money('-5.00', 'USD')),
                    (LineItemSim(amount=Money('10.00', 'USD'), priority=100, id=5), Money('8.85', 'USD')),
                    (LineItemSim(
                        amount=Money('.75', 'USD'),
                        percentage=Decimal('8'),
                        priority=300,
                        cascade_amount=True,
                        cascade_percentage=True,
                        id=6,
                    ), Money('1.15', 'USD')),
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
                    LineItemSim(amount=Money('0', 'USD'), priority=0, id=1): Money('0', 'USD'),
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


class TransactionCheckMixin:
    def check_transactions(
            self, deliverable, user, remote_id='36985214745', auth_code='ABC123', source=TransactionRecord.CARD,
            landscape=False,
    ):
        escrow_transactions = TransactionRecord.objects.filter(
            auth_code=auth_code, source=source, destination=TransactionRecord.ESCROW,
        )
        if remote_id:
            escrow_transactions = escrow_transactions.filter(remote_ids__contains=remote_id)
        else:
            escrow_transactions = escrow_transactions.filter(remote_ids=[])
        if landscape:
            bonus, escrow = escrow_transactions.order_by('amount')
            self.assertEqual(bonus.status, TransactionRecord.SUCCESS)
            self.assertEqual(bonus.amount, Money('.73', 'USD'))
            self.assertEqual(bonus.payee, deliverable.order.seller)
            self.assertEqual(bonus.payer, user)
        else:
            escrow = escrow_transactions.get()
        self.assertEqual(escrow.targets.filter(content_type__model='deliverable').get().target, deliverable)
        self.assertEqual(escrow.targets.filter(content_type__model='invoice').get().target, deliverable.invoice)
        self.assertEqual(escrow.amount, Money('10.29', 'USD'))
        self.assertEqual(escrow.payer, user)
        self.assertEqual(escrow.payee, deliverable.order.seller)

        fee_candidates = TransactionRecord.objects.filter(
            source=source, auth_code=auth_code,
            destination=TransactionRecord.UNPROCESSED_EARNINGS,
        )
        if remote_id:
            fee_candidates = fee_candidates.filter(remote_ids__contains=remote_id)
        else:
            fee_candidates = fee_candidates.filter(remote_ids=[])
        fee = fee_candidates.get()
        self.assertEqual(fee.status, TransactionRecord.SUCCESS)
        self.assertEqual(fee.targets.filter(content_type__model='deliverable').get().target, deliverable)
        self.assertEqual(fee.targets.filter(content_type__model='invoice').get().target, deliverable.invoice)
        if landscape:
            self.assertEqual(fee.amount, Money('0.98', 'USD'))
        else:
            self.assertEqual(fee.amount, Money('1.71', 'USD'))
        self.assertEqual(fee.payer, user)
        self.assertIsNone(fee.payee)
        self.assertEqual(TransactionRecord.objects.all().aggregate(total=Sum('amount'))['total'], Decimal('12.00'))


class TestDestroyDeliverable(TestCase):
    def test_destroy_deliverable_fail_not_cancelled(self):
        deliverable = DeliverableFactory(status=IN_PROGRESS)
        self.assertRaises(IntegrityError, destroy_deliverable, deliverable)

    @patch('apps.lib.utils.clear_events_subscriptions_and_comments')
    def test_destroy_deliverable(self, mock_clear):
        deliverable = DeliverableFactory(status=CANCELLED)
        seller = deliverable.order.seller
        buyer = deliverable.order.buyer
        revision = RevisionFactory(deliverable=deliverable)
        unrelated_revision = RevisionFactory()
        reused_reference = ReferenceFactory()
        reference = ReferenceFactory()
        deliverable.reference_set.add(reference)
        other_deliverable = DeliverableFactory()
        other_deliverable.reference_set.add(reused_reference)
        other_deliverable.refresh_from_db()

        to_preserve = {
            'other_deliverable': other_deliverable,
            'reused_reference': reused_reference,
            'unrelated_revision': unrelated_revision,
            'buyer': buyer,
            'seller': seller,
        }
        to_destroy = {
            'deliverable': deliverable,
            'reference': reference,
            'revision': revision,
        }
        destroy_deliverable(deliverable)
        for name, target in to_preserve.items():
            try:
                target.refresh_from_db()
            except ObjectDoesNotExist:
                raise AssertionError(f'{name} was destroyed when it should not have been!')
        for name, target in to_destroy.items():
            try:
                target.refresh_from_db()
                raise AssertionError(f'{name} was preserved when it should not have been!')
            except ObjectDoesNotExist:
                continue
