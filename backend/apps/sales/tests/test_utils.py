import uuid
from datetime import date
from unittest.mock import patch

from django.test import TestCase
from freezegun import freeze_time
from moneyed import Money, Decimal

from apps.lib.models import Notification, ORDER_UPDATE, Subscription, COMMISSIONS_OPEN
from apps.lib.test_resources import SignalsDisabledMixin, FixtureBase
from apps.profiles.models import User
from apps.profiles.tests.factories import UserFactory
from apps.sales.models import TransactionRecord
from apps.sales.tests.factories import TransactionRecordFactory, OrderFactory, ProductFactory
from apps.sales.utils import claim_order_by_token, \
    check_charge_required, available_products, set_service, account_balance, POSTED_ONLY, PENDING


class BalanceTestCase(SignalsDisabledMixin, FixtureBase, TestCase):
    def setUp(self):
        if self.rebuild_fixtures:
            user1 = UserFactory.create(username='Fox')
            user2 = UserFactory.create(username='Cat')
            transaction = TransactionRecordFactory.create(
                card=None,
                payer=user1,
                payee=user2,
                source=TransactionRecord.CARD,
                destination=TransactionRecord.ESCROW,
                target=None,
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
            self.save_fixture('balance-tests')
        else:
            self.load_fixture('balance-tests')

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
        order = OrderFactory.create(buyer=None)
        claim_order_by_token(str(order.claim_token), user)
        order.refresh_from_db()
        self.assertEqual(order.buyer, user)
        self.assertIsNone(order.claim_token)

    def test_order_claim_fail_self(self):
        user = UserFactory.create()
        order = OrderFactory.create(buyer=None, seller=user, product__user=user)
        original_token = order.claim_token
        claim_order_by_token(str(order.claim_token), user)
        order.refresh_from_db()
        self.assertTrue(order.claim_token)
        self.assertEqual(order.claim_token, original_token)
        self.assertIsNone(order.buyer)

    @patch('apps.sales.utils.transfer_order')
    def test_order_claim_none(self, mock_transfer):
        user = UserFactory.create()
        order = OrderFactory.create(buyer=None)
        claim_order_by_token(None, user)
        mock_transfer.assert_not_called()
        order.refresh_from_db()
        self.assertIsNone(order.buyer)

    def test_order_claim_string(self):
        user = UserFactory.create()
        order = OrderFactory.create(buyer=None)
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
        order = OrderFactory.create(buyer=None)
        claim_order_by_token(str(order.claim_token), user)
        notification = Notification.objects.get(event__type=ORDER_UPDATE)
        self.assertEqual(notification.user, user)
        self.assertEqual(notification.event.target, order)


class TestCheckChargeRequired(TestCase):
    @freeze_time('2018-02-10 12:00:00')
    def test_check_charge_not_required_landscape(self):
        user = UserFactory.create(portrait_paid_through=date(2018, 2, 12), landscape_paid_through=date(2018, 2, 12))
        self.assertEqual(check_charge_required(user, 'landscape'), (False, date(2018, 2, 12)))


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


class TestSetService(TestCase):
    @freeze_time('2018-02-10 12:00:00')
    def test_set_landscape(self):
        user = UserFactory.create()
        other_user = UserFactory.create()
        user.watching.add(other_user)
        set_service(user, 'landscape', date(2018, 3, 10))
        subscriptions = Subscription.objects.filter(type=COMMISSIONS_OPEN)
        self.assertEqual(subscriptions.count(), 1)
        subscription = subscriptions[0]
        self.assertTrue(subscription.telegram)