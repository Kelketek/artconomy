from datetime import date
from decimal import Decimal
from unittest.mock import patch, call, PropertyMock, Mock
from uuid import uuid4

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from djmoney.money import Money
from freezegun import freeze_time

from apps.lib.models import SUBSCRIPTION_DEACTIVATED, Notification, RENEWAL_FAILURE, RENEWAL_FIXED, TRANSFER_FAILED, \
    ref_for_instance
from apps.profiles.tests.factories import UserFactory
from apps.sales.authorize import AuthorizeException
from apps.sales.models import TransactionRecord, REVIEW, PAYMENT_PENDING, NEW, CANCELLED, IN_PROGRESS, Deliverable
from apps.sales.tasks import run_billing, renew, update_transfer_status, remind_sales, remind_sale, check_transactions, \
    withdraw_all, auto_finalize_run, auto_finalize, get_transaction_fees, clear_cancelled_deliverables, \
    clear_deliverable, recover_returned_balance
from apps.sales.tests.factories import CreditCardTokenFactory, TransactionRecordFactory, DeliverableFactory, \
    BankAccountFactory


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
        mock_charge_card.return_value = ('Trans123', 'ABC123')
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
        mock_charge_card.return_value = 'Trans123', 'ABC123'
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
        mock_charge_card.return_value = ('Trans123', 'ABC123')
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
        mock_charge_card.assert_called_with(profile_id=card.profile_id, payment_id=card.payment_id,
                                            amount=Decimal('6.00'))

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
        mock_charge_card.assert_called_with(profile_id=card.profile_id, payment_id=card.payment_id,
                                            amount=Decimal('2.00'))

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
        mock_charge_card.return_value = ('Trans123', 'ABC123')
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
        mock_charge_card.return_value = ('Trans123', 'ABC123')
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
        self.deliverable = DeliverableFactory.create(payout_sent=True)
        self.record.targets.add(ref_for_instance(self.deliverable))

    def test_check_transaction_status_no_change(self, mock_api):
        mock_api.return_value.get.return_value.body = {'status': 'pending'}
        update_transfer_status(self.record.id)
        self.assertEqual(TransactionRecord.objects.all().count(), 1)
        self.record.refresh_from_db()
        self.assertEqual(self.record.status, TransactionRecord.PENDING)
        self.assertIsNone(self.record.finalized_on)
        self.deliverable.refresh_from_db()
        self.assertTrue(self.deliverable.payout_sent)

    def test_check_transaction_status_cancelled(self, mock_api):
        mock_api.return_value.get.return_value.body = {'status': 'cancelled'}
        update_transfer_status(self.record.id)
        self.assertEqual(TransactionRecord.objects.all().count(), 1)
        self.record.refresh_from_db()
        self.assertEqual(self.record.status, TransactionRecord.FAILURE)
        self.assertTrue(self.record.finalized_on)
        self.deliverable.refresh_from_db()
        self.assertFalse(self.deliverable.payout_sent)

    def test_check_transaction_status_failed(self, mock_api):
        mock_api.return_value.get.return_value.body = {'status': 'cancelled'}
        update_transfer_status(self.record.id)
        self.assertEqual(TransactionRecord.objects.all().count(), 1)
        self.record.refresh_from_db()
        self.assertEqual(self.record.status, TransactionRecord.FAILURE)
        self.assertTrue(self.record.finalized_on)
        self.deliverable.refresh_from_db()
        self.assertFalse(self.deliverable.payout_sent)

    def test_check_transaction_status_processed(self, mock_api):
        mock_api.return_value.get.return_value.body = {'status': 'processed'}
        update_transfer_status(self.record.id)
        self.assertEqual(TransactionRecord.objects.all().count(), 2)
        self.record.refresh_from_db()
        self.assertTrue(self.record.finalized_on)
        self.deliverable.refresh_from_db()
        self.assertTrue(self.deliverable.payout_sent)
        additional_record = TransactionRecord.objects.get(
            remote_id=self.record.remote_id, source=TransactionRecord.PAYOUT_MIRROR_SOURCE,
        )
        self.assertEqual(additional_record.amount, self.record.amount)
        self.assertEqual(additional_record.destination, TransactionRecord.PAYOUT_MIRROR_DESTINATION)
        self.assertEqual(additional_record.payee, self.record.payee)
        self.assertEqual(additional_record.payer, self.record.payer)

    @patch('apps.sales.tasks.update_transfer_status')
    def test_update_transactions(self, mock_update_transfer_status, _mock_api):
        check_transactions()
        mock_update_transfer_status.delay.assert_called_with(self.record.id)


class TestFinalizers(TestCase):
    @freeze_time('2018-02-10 12:00:00')
    @patch('apps.sales.tasks.auto_finalize')
    def test_auto_finalize_run(self, mock_auto_finalize):
        deliverable = DeliverableFactory.create(status=REVIEW, auto_finalize_on=date(2018, 2, 10))
        order2 = DeliverableFactory.create(status=REVIEW, auto_finalize_on=date(2018, 2, 9))
        DeliverableFactory.create(status=PAYMENT_PENDING, auto_finalize_on=date(2018, 2, 9))
        DeliverableFactory.create(status=REVIEW, auto_finalize_on=date(2018, 2, 11))
        auto_finalize_run()
        mock_auto_finalize.delay.assert_has_calls([call(deliverable.id), call(order2.id)], any_order=True)
        self.assertEqual(mock_auto_finalize.delay.call_count, 2)

    @freeze_time('2018-02-10 12:00:00')
    @patch('apps.sales.tasks.finalize_deliverable')
    def test_auto_finalize(self, mock_finalize_deliverable):
        deliverable = DeliverableFactory.create(status=REVIEW, auto_finalize_on=date(2018, 2, 10))
        auto_finalize(deliverable.id)
        mock_finalize_deliverable.assert_called_with(deliverable)

    @freeze_time('2018-02-10 12:00:00')
    @patch('apps.sales.tasks.finalize_deliverable')
    def test_auto_finalize_old(self, mock_finalize_deliverable):
        deliverable = DeliverableFactory.create(status=REVIEW, auto_finalize_on=date(2018, 2, 9))
        auto_finalize(deliverable.id)
        mock_finalize_deliverable.assert_called_with(deliverable)

    @freeze_time('2018-02-10 12:00:00')
    @patch('apps.sales.tasks.finalize_deliverable')
    def test_auto_finalize_wrong_status(self, mock_finalize_deliverable):
        deliverable = DeliverableFactory.create(status=PAYMENT_PENDING, auto_finalize_on=date(2018, 2, 9))
        auto_finalize(deliverable.id)
        mock_finalize_deliverable.assert_not_called()

    @freeze_time('2018-02-10 12:00:00')
    @patch('apps.sales.tasks.finalize_deliverable')
    def test_auto_finalize_not_yet(self, mock_finalize_deliverable):
        deliverable = DeliverableFactory.create(status=REVIEW, auto_finalize_on=date(2018, 2, 11))
        auto_finalize(deliverable.id)
        mock_finalize_deliverable.assert_not_called()

    @freeze_time('2018-02-10 12:00:00')
    @patch('apps.sales.tasks.finalize_deliverable')
    def test_auto_finalize_null(self, mock_finalize_deliverable):
        deliverable = DeliverableFactory.create(status=REVIEW, auto_finalize_on=None)
        auto_finalize(deliverable.id)
        mock_finalize_deliverable.assert_not_called()


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
        mock_initiate.return_value = None, Deliverable.objects.none()
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
        mock_initiate.return_value = None, Deliverable.objects.none()
        withdraw_all(user.id)
        mock_initiate.assert_called_with(user, bank, Money('25.00', 'USD'), test_only=False)
        notifications = Notification.objects.filter(event__type=TRANSFER_FAILED)
        self.assertEqual(notifications.count(), 1)
        notification = notifications[0]
        self.assertEqual(notification.event.data, {'error': 'Wat'})


class TestReminders(TestCase):
    @freeze_time('2018-02-10 12:00:00')
    @patch('apps.sales.tasks.Deliverable')
    @patch('apps.sales.tasks.remind_sale')
    def test_reminder_emails(self, mock_remind_sale, mock_deliverable):
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
        mock_deliverable.objects.filter.return_value = all_orders
        remind_sales()
        self.assertEqual(mock_remind_sale.delay.call_count, 12)
        to_remind = [
            call(order.id) for order in to_remind
        ]
        mock_remind_sale.delay.assert_has_calls(to_remind, any_order=True)
        timestamp = timezone.now()
        timestamp = timestamp.replace(year=2018, month=2, day=9, hour=12, minute=0)
        mock_deliverable.objects.filter.assert_called_with(
            status=NEW, created_on__lte=timestamp,
        )

    def test_send_reminder(self):
        deliverable = DeliverableFactory.create(status=NEW, details='# This is a test\n\nDo things and stuff.')
        remind_sale(deliverable.id)
        self.assertEqual(mail.outbox[0].subject, 'Your commissioner is awaiting your response!')

    def test_status_changed(self):
        deliverable = DeliverableFactory.create(status=PAYMENT_PENDING, details='# This is a test\n\nDo things and stuff.')
        remind_sale(deliverable.id)
        self.assertEqual(len(mail.outbox), 0)


def gen_dwolla_response():
    return {
            'transactions': [
                {
                 'id': 'c4ded785-d753-45e8-b225-1ec88c321a46',
                 'status': 'processed',
                 'amount': {'value': '0.12', 'currency': 'USD'},
                 'created': '2018-09-26T06:59:25.597Z'}],
    }


def gen_dwolla_balance(amount: Money):
    return {
        'balance': {'value': str(amount.amount), 'currency': str(amount.currency)},
    }


@patch('apps.sales.apis.DwollaContext.dwolla_api', new_callable=PropertyMock)
class TestGetTransactionFees(TestCase):
    def test_get_transaction_fee(self, mock_api):
        mock_api.return_value.get.return_value.body = gen_dwolla_response()
        record = TransactionRecordFactory.create(remote_id=str(uuid4()))
        get_transaction_fees(str(record.id))
        mock_api.return_value.get.assert_called_with(f'transfers/{record.remote_id}/fees')
        results = TransactionRecord.objects.filter(targets=ref_for_instance(record))
        self.assertEqual(results.count(), 1)
        fee_record = results[0]
        self.assertEqual(fee_record.amount, Money('.12', 'USD'))
        self.assertEqual(fee_record.status, TransactionRecord.SUCCESS)
        self.assertIsNone(fee_record.payer)
        self.assertIsNone(fee_record.payee)
        self.assertEqual(fee_record.category, TransactionRecord.THIRD_PARTY_FEE)
        self.assertTrue(fee_record.created_on)
        self.assertEqual(fee_record.destination, TransactionRecord.ACH_TRANSACTION_FEES)
        self.assertEqual(fee_record.remote_id, 'c4ded785-d753-45e8-b225-1ec88c321a46')
        self.assertEqual(fee_record.created_on, parse('2018-09-26T06:59:25.597Z'))

    def test_get_transaction_fee_multiple(self, mock_api):
        response = gen_dwolla_response()
        response['transactions'].append({
            'id': 'sdvibnwer98',
            'status': 'pending',
            'amount': {'value': '5.00', 'currency': 'USD'},
            'created': '2019-09-26T06:59:25.597Z'
        })
        mock_api.return_value.get.return_value.body = response
        record = TransactionRecordFactory.create(remote_id=str(uuid4()))
        get_transaction_fees(str(record.id))
        mock_api.return_value.get.assert_called_with(f'transfers/{record.remote_id}/fees')
        results = TransactionRecord.objects.filter(targets=ref_for_instance(record))
        self.assertEqual(results.count(), 2)
        fee_record = results.get(status=TransactionRecord.SUCCESS)
        self.assertEqual(fee_record.amount, Money('.12', 'USD'))
        self.assertEqual(fee_record.status, TransactionRecord.SUCCESS)
        self.assertIsNone(fee_record.payer)
        self.assertIsNone(fee_record.payee)
        self.assertEqual(fee_record.category, TransactionRecord.THIRD_PARTY_FEE)
        self.assertEqual(fee_record.destination, TransactionRecord.ACH_TRANSACTION_FEES)
        self.assertEqual(fee_record.remote_id, 'c4ded785-d753-45e8-b225-1ec88c321a46')
        self.assertEqual(fee_record.created_on, parse('2018-09-26T06:59:25.597Z'))
        pending_fee_record = results.get(status=TransactionRecord.PENDING)
        self.assertEqual(pending_fee_record.amount, Money('5', 'USD'))
        self.assertEqual(pending_fee_record.status, TransactionRecord.PENDING)
        self.assertIsNone(pending_fee_record.payer)
        self.assertIsNone(pending_fee_record.payee)
        self.assertEqual(pending_fee_record.category, TransactionRecord.THIRD_PARTY_FEE)
        self.assertEqual(pending_fee_record.destination, TransactionRecord.ACH_TRANSACTION_FEES)
        self.assertEqual(pending_fee_record.remote_id, 'sdvibnwer98')
        self.assertEqual(pending_fee_record.created_on, parse('2019-09-26T06:59:25.597Z'))


class TestDeliverableClear(TestCase):
    @patch('apps.sales.tasks.clear_deliverable')
    def test_clear_deliverables(self, mock_clear):
        chosen = DeliverableFactory(status=CANCELLED, cancelled_on=timezone.now() - relativedelta(months=2))
        DeliverableFactory(status=CANCELLED, cancelled_on=timezone.now())
        DeliverableFactory(status=CANCELLED, cancelled_on=None)
        DeliverableFactory(status=CANCELLED, cancelled_on=None)
        clear_cancelled_deliverables()
        mock_clear.assert_called_with(chosen.id)
        self.assertEqual(mock_clear.call_count, 1)

    @patch('apps.sales.tasks.destroy_deliverable')
    def test_clear_deliverable(self, mock_destroy):
        not_relevant = DeliverableFactory(status=IN_PROGRESS)
        clear_deliverable(not_relevant.id)
        mock_destroy.assert_not_called()
        # Non-existent
        clear_deliverable(-1)
        mock_destroy.assert_not_called()
        relevent = DeliverableFactory(status=CANCELLED)
        clear_deliverable(relevent.id)
        mock_destroy.assert_called_with(relevent)


@patch('apps.sales.apis.DwollaContext.dwolla_api', new_callable=PropertyMock)
class TestRecoverReturnedBalance(TestCase):
    @override_settings(DWOLLA_MASTER_BALANCE_KEY='', DWOLLA_FUNDING_SOURCE_KEY='')
    def test_bail_no_keys_set(self, mock_dwolla):
        recover_returned_balance()
        mock_dwolla.return_value.get.assert_not_called()
        mock_dwolla.return_value.post.assert_not_called()

    @override_settings(DWOLLA_MASTER_BALANCE_KEY='', DWOLLA_FUNDING_SOURCE_KEY='https://example.com/')
    def test_bail_no_funding_key(self, mock_dwolla):
        recover_returned_balance()
        mock_dwolla.return_value.get.assert_not_called()
        mock_dwolla.return_value.post.assert_not_called()

    @override_settings(DWOLLA_MASTER_BALANCE_KEY='https://example.com/', DWOLLA_FUNDING_SOURCE_KEY='')
    def test_bail_no_balance_key(self, mock_dwolla):
        recover_returned_balance()
        mock_dwolla.return_value.get.assert_not_called()
        mock_dwolla.return_value.post.assert_not_called()

    @override_settings(
        DWOLLA_MASTER_BALANCE_KEY='https://example.com/master-balance/',
        DWOLLA_FUNDING_SOURCE_KEY='https://example.com/funding-source/',
    )
    def test_retrieve_negative_balance(self, mock_dwolla):
        mock_dwolla.return_value.get.return_value.body = gen_dwolla_balance(Money('-5', 'USD'))
        recover_returned_balance()
        mock_dwolla.return_value.get.assert_called_with('https://example.com/master-balance/')
        mock_dwolla.return_value.post.assert_not_called()

    @override_settings(
        DWOLLA_MASTER_BALANCE_KEY='https://example.com/master-balance/',
        DWOLLA_FUNDING_SOURCE_KEY='https://example.com/funding-source/',
    )
    def test_retrieve_zero_balance(self, mock_dwolla):
        mock_dwolla.return_value.get.return_value.body = gen_dwolla_balance(Money('0', 'USD'))
        recover_returned_balance()
        mock_dwolla.return_value.get.assert_called_with('https://example.com/master-balance/')
        mock_dwolla.return_value.post.assert_not_called()

    @override_settings(
        DWOLLA_MASTER_BALANCE_KEY='https://example.com/master-balance/',
        DWOLLA_FUNDING_SOURCE_KEY='https://example.com/funding-source/',
    )
    def test_retrieve_positive_balance(self, mock_dwolla):
        mock_dwolla.return_value.get.return_value.body = gen_dwolla_balance(Money('5', 'USD'))
        recover_returned_balance()
        mock_dwolla.return_value.get.assert_called_with('https://example.com/master-balance/')
        mock_dwolla.return_value.post.assert_called_with('transfers', {
            '_links': {
                'source': {
                    'href': 'https://example.com/master-balance/',
                },
                'destination': {
                    'href': 'https://example.com/funding-source/',
                }
            },
            'amount': {
                'currency': 'USD',
                'value': '5',
            },
        })
