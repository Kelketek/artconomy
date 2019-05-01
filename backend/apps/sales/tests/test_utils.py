import uuid
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from moneyed import Money, Decimal

from apps.lib.models import Notification, ORDER_UPDATE
from apps.profiles.tests.factories import UserFactory
from apps.sales.models import PaymentRecord, Order
from apps.sales.tasks import withdraw_all
from apps.sales.tests.factories import PaymentRecordFactory, BankAccountFactory, OrderFactory
from apps.sales.utils import escrow_balance, available_balance, pending_balance, claim_order_by_token, finalize_order


class BalanceTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.user2 = UserFactory.create()
        self.user3 = UserFactory.create()

    def test_escrow_balances(self):
        PaymentRecordFactory.create(
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('10.00', 'USD')
        )
        self.assertEqual(escrow_balance(self.user), Decimal('10.00'))
        self.assertEqual(escrow_balance(self.user2), Decimal('0.00'))
        self.assertEqual(escrow_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('25.00', 'USD')
        )
        self.assertEqual(escrow_balance(self.user), Decimal('35.00'))
        self.assertEqual(escrow_balance(self.user2), Decimal('0.00'))
        self.assertEqual(escrow_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('5.00', 'USD')
        )
        self.assertEqual(escrow_balance(self.user), Decimal('40.00'))
        self.assertEqual(escrow_balance(self.user2), Decimal('0.00'))
        self.assertEqual(escrow_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            status=PaymentRecord.FAILURE,
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('6.00', 'USD')
        )
        self.assertEqual(escrow_balance(self.user), Decimal('40.00'))
        self.assertEqual(escrow_balance(self.user2), Decimal('0.00'))
        self.assertEqual(escrow_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=self.user,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ESCROW,
            amount=Money('10.00', 'USD')
        )
        self.assertEqual(escrow_balance(self.user), Decimal('30.00'))
        self.assertEqual(escrow_balance(self.user2), Decimal('0.00'))
        self.assertEqual(escrow_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=self.user,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ESCROW,
            amount=Money('25.00', 'USD')
        )
        self.assertEqual(escrow_balance(self.user), Decimal('5.00'))
        self.assertEqual(escrow_balance(self.user2), Decimal('0.00'))
        self.assertEqual(escrow_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=None,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ACCOUNT,
            type=PaymentRecord.DISBURSEMENT_SENT,
            amount=Money('15.00', 'USD')
        )
        self.assertEqual(escrow_balance(self.user), Decimal('5.00'))
        self.assertEqual(escrow_balance(self.user2), Decimal('0.00'))
        self.assertEqual(escrow_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=None,
            status=PaymentRecord.FAILURE,
            source=PaymentRecord.ACCOUNT,
            type=PaymentRecord.DISBURSEMENT_SENT,
            amount=Money('8.00', 'USD')
        )
        self.assertEqual(escrow_balance(self.user), Decimal('5.00'))
        self.assertEqual(escrow_balance(self.user2), Decimal('0.00'))
        self.assertEqual(escrow_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=None,
            payer=self.user,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ACCOUNT,
            type=PaymentRecord.DISBURSEMENT_RETURNED,
            amount=Money('8.00', 'USD')
        )
        self.assertEqual(escrow_balance(self.user), Decimal('5.00'))
        self.assertEqual(escrow_balance(self.user2), Decimal('0.00'))
        self.assertEqual(escrow_balance(self.user3), Decimal('0.00'))

    def test_account_balance(self):
        PaymentRecordFactory.create(
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('10.00', 'USD')
        )
        self.assertEqual(available_balance(self.user), Decimal('0.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('25.00', 'USD')
        )
        self.assertEqual(available_balance(self.user), Decimal('0.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('5.00', 'USD')
        )
        self.assertEqual(available_balance(self.user), Decimal('0.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            status=PaymentRecord.FAILURE,
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('6.00', 'USD')
        )
        self.assertEqual(available_balance(self.user), Decimal('0.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=self.user,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ESCROW,
            amount=Money('10.00', 'USD')
        )
        self.assertEqual(available_balance(self.user), Decimal('10.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
        record = PaymentRecordFactory.create(
            payee=self.user,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ESCROW,
            finalized=False,
            amount=Money('25.00', 'USD')
        )
        self.assertEqual(available_balance(self.user), Decimal('10.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
        record.finalized = True
        record.save()
        self.assertEqual(available_balance(self.user), Decimal('35.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payer=self.user,
            payee=None,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ACCOUNT,
            type=PaymentRecord.DISBURSEMENT_SENT,
            amount=Money('15.00', 'USD')
        )
        self.assertEqual(available_balance(self.user), Decimal('20.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payer=self.user,
            payee=None,
            status=PaymentRecord.FAILURE,
            source=PaymentRecord.ACCOUNT,
            type=PaymentRecord.DISBURSEMENT_SENT,
            amount=Money('8.00', 'USD')
        )
        self.assertEqual(available_balance(self.user), Decimal('20.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=self.user,
            payer=None,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ACCOUNT,
            type=PaymentRecord.DISBURSEMENT_RETURNED,
            amount=Money('5.00', 'USD')
        )
        self.assertEqual(available_balance(self.user), Decimal('25.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
        txn = PaymentRecordFactory.create(
            payee=None,
            payer=self.user,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ACCOUNT,
            type=PaymentRecord.TRANSFER,
            finalized=False,
            amount=Money('5.00', 'USD')
        )
        self.assertEqual(available_balance(self.user), Decimal('25.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
        txn.finalized = True
        txn.save()
        self.assertEqual(available_balance(self.user), Decimal('20.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))

    def test_pending_balance(self):
        PaymentRecordFactory.create(
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('10.00', 'USD')
        )
        self.assertEqual(pending_balance(self.user), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user2), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('25.00', 'USD')
        )
        self.assertEqual(pending_balance(self.user), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user2), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('5.00', 'USD')
        )
        self.assertEqual(pending_balance(self.user), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user2), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            status=PaymentRecord.FAILURE,
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('6.00', 'USD')
        )
        self.assertEqual(pending_balance(self.user), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user2), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=self.user,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ESCROW,
            amount=Money('10.00', 'USD')
        )
        self.assertEqual(pending_balance(self.user), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user2), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user3), Decimal('0.00'))
        record = PaymentRecordFactory.create(
            payee=self.user,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ESCROW,
            finalized=False,
            amount=Money('25.00', 'USD')
        )
        self.assertEqual(pending_balance(self.user), Decimal('25.00'))
        self.assertEqual(pending_balance(self.user2), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user3), Decimal('0.00'))
        fee = PaymentRecordFactory.create(
            payee=None,
            payer=self.user,
            source=PaymentRecord.ACCOUNT,
            type=PaymentRecord.TRANSFER,
            finalized=False,
            amount=Money('5.00', 'USD')
        )
        self.assertEqual(pending_balance(self.user), Decimal('20.00'))
        self.assertEqual(pending_balance(self.user2), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user3), Decimal('0.00'))
        record.finalized = True
        record.save()
        self.assertEqual(pending_balance(self.user), Decimal('-5.00'))
        self.assertEqual(pending_balance(self.user2), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user3), Decimal('0.00'))
        fee.finalized = True
        fee.save()
        self.assertEqual(pending_balance(self.user), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user2), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payer=self.user,
            payee=None,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ACCOUNT,
            type=PaymentRecord.DISBURSEMENT_SENT,
            amount=Money('15.00', 'USD')
        )
        self.assertEqual(pending_balance(self.user), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user2), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payer=self.user,
            payee=None,
            status=PaymentRecord.FAILURE,
            source=PaymentRecord.ACCOUNT,
            type=PaymentRecord.DISBURSEMENT_SENT,
            amount=Money('8.00', 'USD')
        )
        self.assertEqual(pending_balance(self.user), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user2), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=self.user,
            payer=None,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ACCOUNT,
            type=PaymentRecord.DISBURSEMENT_RETURNED,
            amount=Money('5.00', 'USD')
        )
        self.assertEqual(pending_balance(self.user), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user2), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=None,
            payer=self.user,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ACCOUNT,
            type=PaymentRecord.TRANSFER,
            amount=Money('5.00', 'USD')
        )
        self.assertEqual(pending_balance(self.user), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user2), Decimal('0.00'))
        self.assertEqual(pending_balance(self.user3), Decimal('0.00'))

    @patch('apps.sales.tasks.available_balance')
    @patch('apps.sales.tasks.initiate_withdraw')
    @patch('apps.sales.tasks.perform_transfer')
    def test_withdraw_all(self, mock_perform_transfer, mock_initiate, mock_balance):
        # Avoid initial call in post-creation hook.
        mock_balance.return_value = Decimal('0.00')
        bank = BankAccountFactory.create(user=self.user)
        mock_initiate.assert_not_called()
        mock_balance.return_value = Decimal('25.00')
        withdraw_all(self.user.id)
        # Normally, three dollars would be removed here for the connection fee,
        # but we're always returning a balance of $25.
        mock_initiate.assert_called_with(self.user, bank, Money('25.00', 'USD'), test_only=False)
        mock_perform_transfer.assert_called()


class TestClaim(TestCase):
    def test_order_claim(self):
        user = UserFactory.create()
        uid = uuid.uuid4()
        order = OrderFactory.create(buyer=None, claim_token=uid)
        claim_order_by_token(uid, user)
        order.refresh_from_db()
        self.assertEqual(order.buyer, user)
        self.assertIsNone(order.claim_token)

    def test_order_claim_string(self):
        user = UserFactory.create()
        uid = uuid.uuid4()
        order = OrderFactory.create(buyer=None, claim_token=uid)
        claim_order_by_token(str(uid), user)
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
        uid = uuid.uuid4()
        order = OrderFactory.create(buyer=None, claim_token=uid)
        claim_order_by_token(str(uid), user)
        notification = Notification.objects.get(event__type=ORDER_UPDATE)
        self.assertEqual(notification.user, user)
        self.assertEqual(notification.event.target, order)
