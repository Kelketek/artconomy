from datetime import date
from decimal import Decimal
from unittest.mock import patch, call, PropertyMock, Mock

from dateutil.relativedelta import relativedelta
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from djmoney.money import Money
from freezegun import freeze_time

from apps.lib.models import SUBSCRIPTION_DEACTIVATED, Notification, RENEWAL_FAILURE, RENEWAL_FIXED, TRANSFER_FAILED
from apps.profiles.tests.factories import UserFactory
from apps.sales.authorize import AuthorizeException
from apps.sales.models import TransactionRecord, Order
from apps.sales.tasks import run_billing, renew, update_transfer_status, remind_sales, remind_sale, check_transactions, \
    withdraw_all, auto_finalize_run, auto_finalize
from apps.sales.tests.factories import CreditCardTokenFactory, TransactionRecordFactory, OrderFactory, BankAccountFactory


class TestAutoRenewal(TestCase):
    @patch('apps.sales.tasks.renew')
    @freeze_time('2018-02-10 12:00:00')
    def test_tasks_made(self, mock_renew):
        disable1 = UserFactory.create(landscape_enabled=True, landscape_paid_through=date(2018, 2, 5))
        disable2 = UserFactory.create(portrait_enabled=True, portrait_paid_through=date(2018, 2, 4))
        renew_portrait = UserFactory.create(portrait_enabled=True, portrait_paid_through=date(2018, 2, 10))
        renew_landscape = UserFactory.create(landscape_enabled=True, landscape_paid_through=date(2018, 2, 9))
        run_billing()
        disable1.refresh_from_db()
        disable2.refresh_from_db()
        self.assertFalse(disable1.landscape_enabled)
        self.assertFalse(disable2.portrait_enabled)
        mock_renew.delay.assert_has_calls([call(renew_portrait.id, 'portrait'), call(renew_landscape.id, 'landscape')])
        self.assertEqual(Notification.objects.filter(event__type=SUBSCRIPTION_DEACTIVATED).count(), 2)
        self.assertEqual(len(mail.outbox), 2)
        for letter in mail.outbox:
            self.assertEqual(letter.subject, 'Your subscription has been deactivated.')

    @override_settings(PORTRAIT_PRICE=Decimal('2.00'))
    @patch('apps.sales.tasks.charge_saved_card')
    @freeze_time('2018-02-10 12:00:00')
    def test_renew_portrait(self, mock_charge_card):
        mock_charge_card.return_value = 'Trans123'
        card = CreditCardTokenFactory.create(
            user__portrait_enabled=True, user__portrait_paid_through=date(2018, 2, 10),
            token='1234', user__authorize_token='5678'
        )
        card.user.primary_card = card
        card.user.save()
        renew(card.user.id, 'portrait')
        card.user.refresh_from_db()
        self.assertEqual(card.user.portrait_paid_through, date(2018, 3, 10))
        self.assertTrue(card.user.portrait_enabled)
        self.assertFalse(card.user.landscape_enabled)
        self.assertIsNone(card.user.landscape_paid_through)
        records = TransactionRecord.objects.filter(payer=card.user)
        self.assertEqual(records.count(), 1)
        record = records[0]
        self.assertIsNone(record.payee)
        self.assertTrue(record.finalized_on)
        self.assertEqual(record.status, TransactionRecord.SUCCESS)
        self.assertEqual(record.remote_id, 'Trans123')
        self.assertEqual(record.category, TransactionRecord.SUBSCRIPTION_DUES)
        self.assertEqual(record.amount, Money('2.00', 'USD'))
        mock_charge_card.assert_called_with(payment_id='1234', profile_id='5678', amount=Decimal('2.00'))

    @override_settings(PORTRAIT_PRICE=Decimal('2.00'))
    @patch('apps.sales.tasks.charge_saved_card')
    @freeze_time('2018-02-10 12:00:00')
    def test_renew_no_primary(self, mock_charge_card):
        mock_charge_card.return_value = 'Trans123'
        card = CreditCardTokenFactory.create(
            user__portrait_enabled=True, user__portrait_paid_through=date(2018, 2, 10),
            token='1234', user__authorize_token='5678'
        )
        renew(card.user.id, 'portrait')
        card.user.refresh_from_db()
        self.assertEqual(card.user.portrait_paid_through, date(2018, 3, 10))
        self.assertTrue(card.user.portrait_enabled)
        self.assertFalse(card.user.landscape_enabled)
        self.assertIsNone(card.user.landscape_paid_through)
        records = TransactionRecord.objects.filter(payer=card.user)
        self.assertEqual(records.count(), 1)
        record = records[0]
        self.assertIsNone(record.payee)
        self.assertTrue(record.finalized_on)
        self.assertEqual(record.status, TransactionRecord.SUCCESS)
        self.assertEqual(record.remote_id, 'Trans123')
        self.assertEqual(record.category, TransactionRecord.SUBSCRIPTION_DUES)
        self.assertEqual(record.amount, Money('2.00', 'USD'))
        mock_charge_card.assert_called_with(payment_id='1234', profile_id='5678', amount=Decimal('2.00'))

    @override_settings(PORTRAIT_PRICE=Decimal('2.00'))
    @patch('apps.sales.tasks.charge_saved_card')
    @freeze_time('2018-02-10 12:00:00')
    def test_renew_invalid(self, mock_charge_card):
        card = CreditCardTokenFactory.create(
            token='1234', user__authorize_token='5678'
        )
        renew(card.user.id, 'portrait')
        card.user.refresh_from_db()
        self.assertEqual(card.user.portrait_paid_through, None)
        self.assertFalse(card.user.portrait_enabled)
        self.assertFalse(card.user.landscape_enabled)
        mock_charge_card.assert_not_called()

    @override_settings(LANDSCAPE_PRICE=Decimal('6.00'))
    @patch('apps.sales.tasks.charge_saved_card')
    @freeze_time('2018-02-10 12:00:00')
    def test_renew_landscape(self, mock_charge_card):
        mock_charge_card.return_value = 'Trans123'
        card = CreditCardTokenFactory.create(
            user__landscape_enabled=True, user__landscape_paid_through=date(2018, 2, 10)
        )
        card.user.primary_card = card
        card.user.save()
        renew(card.user.id, 'landscape')
        card.user.refresh_from_db()
        self.assertEqual(card.user.landscape_paid_through, date(2018, 3, 10))
        self.assertTrue(card.user.landscape_enabled)
        self.assertFalse(card.user.portrait_enabled)
        self.assertEqual(card.user.portrait_paid_through, date(2018, 3, 10))
        records = TransactionRecord.objects.filter(payer=card.user)
        self.assertEqual(records.count(), 1)
        record = records[0]
        self.assertIsNone(record.payee)
        self.assertTrue(record.finalized_on)
        self.assertEqual(record.status, TransactionRecord.SUCCESS)
        self.assertEqual(record.remote_id, 'Trans123')
        self.assertEqual(record.category, TransactionRecord.SUBSCRIPTION_DUES)
        self.assertEqual(record.amount, Money('6.00', 'USD'))
        self.assertEqual(record.card, card)
        mock_charge_card.assert_called_with(profile_id=card.profile_id, payment_id=card.payment_id, amount=Decimal('6.00'))

    @override_settings(PORTRAIT_PRICE=Decimal('2.00'))
    @patch('apps.sales.tasks.charge_saved_card')
    @freeze_time('2018-02-10 12:00:00')
    def test_failed_renewal(self, mock_charge_card):
        mock_charge_card.side_effect = AuthorizeException('Crap.')
        card = CreditCardTokenFactory.create(
            user__portrait_enabled=True, user__portrait_paid_through=date(2018, 2, 10)
        )
        card.user.primary_card = card
        card.user.save()
        renew(card.user.id, 'portrait')
        card.user.refresh_from_db()
        self.assertTrue(card.user.portrait_enabled)
        self.assertEqual(card.user.portrait_paid_through, date(2018, 2, 10))
        records = TransactionRecord.objects.filter(payer=card.user)
        self.assertEqual(records.count(), 1)
        record = records[0]
        self.assertIsNone(record.payee)
        self.assertTrue(record.finalized_on)
        self.assertEqual(record.status, TransactionRecord.FAILURE)
        self.assertEqual(record.remote_id, '')
        self.assertEqual(record.category, TransactionRecord.SUBSCRIPTION_DUES)
        self.assertEqual(record.amount, Money('2.00', 'USD'))
        self.assertEqual(record.card, card)
        self.assertEqual(record.response_message, 'Crap.')
        self.assertEqual(Notification.objects.filter(event__type=RENEWAL_FAILURE).count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Issue with your subscription')
        mock_charge_card.assert_called_with(profile_id=card.profile_id, payment_id=card.payment_id, amount=Decimal('2.00'))

    @override_settings(PORTRAIT_PRICE=Decimal('2.00'))
    @patch('apps.sales.tasks.charge_saved_card')
    @freeze_time('2018-02-10 12:00:00')
    def test_failed_renewal_no_card(self, mock_charge_card):
        mock_charge_card.side_effect = AuthorizeException('Crap.')
        user = UserFactory.create(portrait_enabled=True, portrait_paid_through=date(2018, 2, 10))
        renew(user.id, 'portrait')
        user.refresh_from_db()
        self.assertTrue(user.portrait_enabled)
        self.assertEqual(user.portrait_paid_through, date(2018, 2, 10))
        records = TransactionRecord.objects.filter(payer=user)
        self.assertEqual(records.count(), 0)
        self.assertEqual(Notification.objects.filter(event__type=RENEWAL_FAILURE).count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Issue with your subscription')
        mock_charge_card.assert_not_called()

    @patch('apps.sales.tasks.charge_saved_card')
    @freeze_time('2018-02-10 12:00:00')
    def test_already_renewed(self, mock_charge_card):
        # Still mock out capture here to avoid chance of contacting outside server.
        mock_charge_card.return_value = 'Trans123'
        card = CreditCardTokenFactory.create(
            user__portrait_enabled=True, user__portrait_paid_through=date(2018, 2, 11)
        )
        card.user.primary_card = card
        card.user.save()
        renew(card.user.id, 'portrait')
        card.user.refresh_from_db()
        self.assertEqual(card.user.portrait_enabled, True)
        self.assertEqual(card.user.portrait_paid_through, date(2018, 2, 11))
        self.assertFalse(TransactionRecord.objects.all().exists())
        mock_charge_card.assert_not_called()

    @override_settings(PORTRAIT_PRICE=Decimal('2.00'))
    @patch('apps.sales.tasks.charge_saved_card')
    @freeze_time('2018-02-10 12:00:00')
    def test_card_override(self, mock_charge_card):
        mock_charge_card.return_value = 'Trans123'
        primary_card = CreditCardTokenFactory.create(
            user__portrait_enabled=True, user__portrait_paid_through=date(2018, 2, 10),
        )
        primary_card.user.primary_card = primary_card
        primary_card.user.save()
        card = CreditCardTokenFactory.create(user=primary_card.user)
        renew(card.user.id, 'portrait', card_id=card.id)
        card.user.refresh_from_db()
        self.assertEqual(card.user.portrait_paid_through, date(2018, 3, 10))
        self.assertTrue(card.user.portrait_enabled)
        self.assertFalse(card.user.landscape_enabled)
        self.assertIsNone(card.user.landscape_paid_through)
        records = TransactionRecord.objects.filter(payer=card.user)
        self.assertEqual(records.count(), 1)
        record = records[0]
        self.assertIsNone(record.payee)
        self.assertTrue(record.finalized_on)
        self.assertEqual(record.status, TransactionRecord.SUCCESS)
        self.assertEqual(record.remote_id, 'Trans123')
        self.assertEqual(record.category, TransactionRecord.SUBSCRIPTION_DUES)
        self.assertEqual(record.amount, Money('2.00', 'USD'))
        self.assertEqual(card.user.primary_card, primary_card)
        self.assertEqual(Notification.objects.filter(event__type=RENEWAL_FIXED).count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Subscription renewed successfully')


@patch('apps.sales.apis.DwollaContext.dwolla_api', new_callable=PropertyMock)
class TestUpdateTransaction(TestCase):
    def setUp(self):
        super().setUp()
        user = UserFactory.create()
        self.record = TransactionRecordFactory.create(
            payee=user,
            payer=user,
            status=TransactionRecord.PENDING,
            category=TransactionRecord.CASH_WITHDRAW,
            source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK,
            remote_id='1234',
        )

    def test_check_transaction_status_no_change(self, _mock_api):
        _mock_api.return_value.get.return_value.body = {'status': 'pending'}
        update_transfer_status(self.record.id)
        self.assertEqual(TransactionRecord.objects.all().count(), 1)
        self.record.refresh_from_db()
        self.assertEqual(self.record.status, TransactionRecord.PENDING)
        self.assertIsNone(self.record.finalized_on)

    def test_check_transaction_status_cancelled(self, _mock_api):
        _mock_api.return_value.get.return_value.body = {'status': 'cancelled'}
        update_transfer_status(self.record.id)
        self.assertEqual(TransactionRecord.objects.all().count(), 1)
        self.record.refresh_from_db()
        self.assertEqual(self.record.status, TransactionRecord.FAILURE)
        self.assertTrue(self.record.finalized_on)

    def test_check_transaction_status_processed(self, _mock_api):
        _mock_api.return_value.get.return_value.body = {'status': 'processed'}
        update_transfer_status(self.record.id)
        self.assertEqual(TransactionRecord.objects.all().count(), 1)
        self.record.refresh_from_db()
        self.assertTrue(self.record.finalized_on)

    @patch('apps.sales.tasks.update_transfer_status')
    def test_update_transactions(self, mock_update_transfer_status, _mock_api):
        check_transactions()
        mock_update_transfer_status.delay.assert_called_with(self.record.id)


class TestFinalizers(TestCase):
    @freeze_time('2018-02-10 12:00:00')
    @patch('apps.sales.tasks.auto_finalize')
    def test_auto_finalize_run(self, mock_auto_finalize):
        order = OrderFactory.create(status=Order.REVIEW, auto_finalize_on=date(2018, 2, 10))
        order2 = OrderFactory.create(status=Order.REVIEW, auto_finalize_on=date(2018, 2, 9))
        OrderFactory.create(status=Order.PAYMENT_PENDING, auto_finalize_on=date(2018, 2, 9))
        OrderFactory.create(status=Order.REVIEW, auto_finalize_on=date(2018, 2, 11))
        auto_finalize_run()
        mock_auto_finalize.delay.assert_has_calls([call(order.id), call(order2.id)], any_order=True)
        self.assertEqual(mock_auto_finalize.delay.call_count, 2)

    @freeze_time('2018-02-10 12:00:00')
    @patch('apps.sales.tasks.finalize_order')
    def test_auto_finalize(self, mock_finalize_order):
        order = OrderFactory.create(status=Order.REVIEW, auto_finalize_on=date(2018, 2, 10))
        auto_finalize(order.id)
        mock_finalize_order.assert_called_with(order)

    @freeze_time('2018-02-10 12:00:00')
    @patch('apps.sales.tasks.finalize_order')
    def test_auto_finalize_old(self, mock_finalize_order):
        order = OrderFactory.create(status=Order.REVIEW, auto_finalize_on=date(2018, 2, 9))
        auto_finalize(order.id)
        mock_finalize_order.assert_called_with(order)

    @freeze_time('2018-02-10 12:00:00')
    @patch('apps.sales.tasks.finalize_order')
    def test_auto_finalize_wrong_status(self, mock_finalize_order):
        order = OrderFactory.create(status=Order.PAYMENT_PENDING, auto_finalize_on=date(2018, 2, 9))
        auto_finalize(order.id)
        mock_finalize_order.assert_not_called()

    @freeze_time('2018-02-10 12:00:00')
    @patch('apps.sales.tasks.finalize_order')
    def test_auto_finalize_not_yet(self, mock_finalize_order):
        order = OrderFactory.create(status=Order.REVIEW, auto_finalize_on=date(2018, 2, 11))
        auto_finalize(order.id)
        mock_finalize_order.assert_not_called()

    @freeze_time('2018-02-10 12:00:00')
    @patch('apps.sales.tasks.finalize_order')
    def test_auto_finalize_null(self, mock_finalize_order):
        order = OrderFactory.create(status=Order.REVIEW, auto_finalize_on=None)
        auto_finalize(order.id)
        mock_finalize_order.assert_not_called()

class TestWithdrawAll(TestCase):
    @patch('apps.sales.tasks.account_balance')
    @patch('apps.sales.tasks.initiate_withdraw')
    @patch('apps.sales.tasks.perform_transfer')
    def test_withdraw_all(self, mock_perform_transfer, mock_initiate, mock_balance):
        user = UserFactory.create()
        # Avoid initial call in post-creation hook.
        mock_balance.return_value = Decimal('0.00')
        bank = BankAccountFactory.create(user=user)
        mock_initiate.assert_not_called()
        mock_balance.return_value = Decimal('25.00')
        withdraw_all(user.id)
        # Normally, three dollars would be removed here for the connection fee,
        # but we're always returning a balance of $25.
        mock_initiate.assert_called_with(user, bank, Money('25.00', 'USD'), test_only=False)
        mock_perform_transfer.assert_called()

    @patch('apps.sales.tasks.account_balance')
    @patch('apps.sales.tasks.initiate_withdraw')
    @patch('apps.sales.tasks.perform_transfer')
    def test_withdraw_all_no_auto(self, mock_perform_transfer, mock_initiate, mock_balance):
        user = UserFactory.create()
        user.artist_profile.auto_withdraw = False
        user.artist_profile.save()
        mock_balance.return_value = Decimal('0.00')
        BankAccountFactory.create(user=user)
        mock_initiate.assert_not_called()
        mock_balance.return_value = Decimal('25.00')
        withdraw_all(user.id)
        mock_initiate.assert_not_called()
        mock_perform_transfer.assert_not_called()

    @patch('apps.sales.tasks.account_balance')
    @patch('apps.sales.tasks.initiate_withdraw')
    @patch('apps.sales.tasks.perform_transfer')
    def test_withdraw_exception(self, mock_perform_transfer, mock_initiate, mock_balance):
        user = UserFactory.create()
        user.artist_profile.auto_withdraw = True
        user.artist_profile.save()
        mock_balance.return_value = Decimal('0.00')
        bank = BankAccountFactory.create(user=user)
        mock_initiate.assert_not_called()
        mock_balance.return_value = Decimal('25.00')
        mock_perform_transfer.side_effect = RuntimeError('Wat')
        withdraw_all(user.id)
        mock_initiate.assert_called_with(user, bank, Money('25.00', 'USD'), test_only=False)
        notifications = Notification.objects.filter(event__type=TRANSFER_FAILED)
        self.assertEqual(notifications.count(), 1)
        notification = notifications[0]
        self.assertEqual(notification.event.data, {'error': 'Wat'})


class TestReminders(TestCase):
    @freeze_time('2018-02-10 12:00:00')
    @patch('apps.sales.tasks.Order')
    @patch('apps.sales.tasks.remind_sale')
    def test_reminder_emails(self, mock_remind_sale, mock_order):
        def build_calls(order_list, differences):
            for i in differences:
                mock = Mock()
                # Negative to make distinct so we know the arguments are in the right order.
                mock.id = 0 - i
                mock.created_on = timezone.now() - relativedelta(days=i)
                order_list.append(mock)

        to_remind = []
        build_calls(to_remind, [1, 2, 3, 4, 5, 6, 9, 12, 15, 18, 25, 30])
        all_orders = [*to_remind]
        # To be ignored.
        build_calls(all_orders, [7, 8, 10, 11, 13, 14, 16, 17, 19, 21, 22, 23, 24, 26, 27, 28])
        mock_order.objects.filter.return_value = all_orders
        remind_sales()
        self.assertEqual(mock_remind_sale.delay.call_count, 12)
        to_remind = [
            call(order.id) for order in to_remind
        ]
        mock_remind_sale.delay.assert_has_calls(to_remind, any_order=True)
        timestamp = timezone.now()
        timestamp = timestamp.replace(year=2018, month=2, day=9, hour=12, minute=0)
        mock_order.objects.filter.assert_called_with(
            status=mock_order.NEW, created_on__lte=timestamp,
        )

    def test_send_reminder(self):
        order = OrderFactory.create(status=Order.NEW, details='# This is a test\n\nDo things and stuff.')
        remind_sale(order.id)
        self.assertEqual(mail.outbox[0].subject, 'Your commissioner is awaiting your response!')

    def test_status_changed(self):
        order = OrderFactory.create(status=Order.PAYMENT_PENDING, details='# This is a test\n\nDo things and stuff.')
        remind_sale(order.id)
        self.assertEqual(len(mail.outbox), 0)
