from datetime import date
from decimal import Decimal
from multiprocessing.pool import ThreadPool
from time import sleep
from unittest.mock import patch, call, PropertyMock, Mock

from dateutil.relativedelta import relativedelta
from django.core import mail
from django.db import connection
from django.test import TestCase, TransactionTestCase, override_settings
from django.utils import timezone
from djmoney.money import Money
from freezegun import freeze_time

from apps.lib.models import SUBSCRIPTION_DEACTIVATED, Notification, RENEWAL_FAILURE, RENEWAL_FIXED, TRANSFER_FAILED, \
    ref_for_instance
from apps.profiles.tests.factories import UserFactory
from apps.sales.models import TransactionRecord, REVIEW, PAYMENT_PENDING, NEW, CANCELLED, IN_PROGRESS, Deliverable
from apps.sales.tasks import run_billing, update_transfer_status, remind_sales, remind_sale, \
    withdraw_all, auto_finalize_run, auto_finalize, clear_cancelled_deliverables, \
    clear_deliverable, annotate_connect_fees_for_year_month, annotate_connect_fees
from apps.sales.tests.factories import TransactionRecordFactory, DeliverableFactory, \
    StripeAccountFactory, ServicePlanFactory


class TestAutoRenewal(TestCase):

    def setUp(self):
        super().setUp()
        ServicePlanFactory(monthly_charge=Money('0.00', 'USD'), name='Free')
        self.service_plan = ServicePlanFactory(monthly_charge=Money('6.00', 'USD'))

    @patch('apps.sales.tasks.renew')
    @freeze_time('2018-02-10 12:00:00')
    def test_tasks_made(self, mock_renew):
        disable = UserFactory.create(service_plan=self.service_plan, service_plan_paid_through=date(2018, 2, 5))
        renew_landscape = UserFactory.create(service_plan=self.service_plan, service_plan_paid_through=date(2018, 2, 9))
        run_billing()
        disable.refresh_from_db()
        self.assertFalse(disable.landscape_enabled)
        mock_renew.delay.assert_has_calls([call(renew_landscape.id)])
        self.assertEqual(Notification.objects.filter(event__type=SUBSCRIPTION_DEACTIVATED).count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        for letter in mail.outbox:
            self.assertEqual(letter.subject, 'Your subscription has been deactivated.')


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
            remote_ids=['1234'],
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
            remote_ids__contains=self.record.remote_ids, source=TransactionRecord.PAYOUT_MIRROR_SOURCE,
        )
        self.assertEqual(additional_record.amount, self.record.amount)
        self.assertEqual(additional_record.destination, TransactionRecord.PAYOUT_MIRROR_DESTINATION)
        self.assertEqual(additional_record.payee, self.record.payee)
        self.assertEqual(additional_record.payer, self.record.payer)


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


def wrapped_withdraw(user_id):
    try:
        withdraw_all(user_id)
    finally:
        connection.close()


class TestWithdrawAll(TransactionTestCase):
    @patch('apps.sales.tasks.account_balance')
    @patch('apps.sales.tasks.stripe_transfer.delay')
    def test_withdraw_all(self, stripe_transfer, mock_balance):
        user = UserFactory.create()
        # Avoid initial call in post-creation hook.
        mock_balance.return_value = Decimal('0.00')
        bank = StripeAccountFactory.create(user=user)
        stripe_transfer.assert_not_called()
        mock_balance.return_value = Decimal('25.00')
        stripe_transfer.return_value = None, Deliverable.objects.none()
        withdraw_all(user.id)
        # Normally, three dollars would be removed here for the connection fee,
        # but we're always returning a balance of $25.
        record = TransactionRecord.objects.get(category=TransactionRecord.CASH_WITHDRAW)
        stripe_transfer.assert_called_with(record.id, bank.id, None)

    @patch('apps.sales.tasks.account_balance')
    @patch('apps.sales.tasks.stripe_transfer.delay')
    def test_withdraw_all_no_auto(self, stripe_transfer, mock_balance):
        user = UserFactory.create()
        user.artist_profile.auto_withdraw = False
        user.artist_profile.save()
        mock_balance.return_value = Decimal('0.00')
        StripeAccountFactory.create(user=user)
        stripe_transfer.assert_not_called()
        mock_balance.return_value = Decimal('25.00')
        withdraw_all(user.id)
        stripe_transfer.assert_not_called()

    @patch('apps.sales.tasks.stripe_transfer.delay')
    def test_withdraw_mutex(self, stripe_transfer):
        user = UserFactory.create()
        StripeAccountFactory(user=user)
        TransactionRecordFactory(payee=user, destination=TransactionRecord.HOLDINGS, amount=Money('10.00', 'USD'))
        def side_effect(x, y, z):
            sleep(.25)
            return None, Deliverable.objects.none()
        stripe_transfer.side_effect = side_effect
        pool = ThreadPool(processes=4)
        pool.map(wrapped_withdraw, [user.id] * 4)
        pool.close()
        pool.join()
        records = TransactionRecord.objects.filter(destination=TransactionRecord.BANK)
        self.assertEqual(records.count(), 1)


    # TODO: Add in tests for deliverable annotations.


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
        build_calls(to_remind, [1, 2, 3, 4, 5, 6, 9, 12, 15, 18])
        all_orders = [*to_remind]
        # To be ignored.
        build_calls(all_orders, [7, 8, 10, 11, 13, 14, 16, 17, 19, 21, 22, 23, 24, 25, 26, 27, 28, 30])
        mock_deliverable.objects.filter.return_value = all_orders
        remind_sales()
        self.assertEqual(mock_remind_sale.delay.call_count, 10)
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

@override_settings(
    STRIPE_PAYOUT_STATIC=Money('0.25', 'USD'),
    STRIPE_PAYOUT_PERCENTAGE=Decimal('0.25'),
    STRIPE_PAYOUT_CROSS_BORDER_PERCENTAGE=Decimal('0.25'),
    STRIPE_ACTIVE_ACCOUNT_MONTHLY_FEE=Money('2.00', 'USD'),
)
class TestAnnotatePayouts(TestCase):
    @freeze_time('2021-08-01')
    def test_allocate_connect_fees_one_record(self):
        account = StripeAccountFactory.create()
        record = TransactionRecordFactory.create(
            payer=account.user, payee=account.user, source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK, amount=Money('100', 'USD'), category=TransactionRecord.CASH_WITHDRAW,
            finalized_on=timezone.now(),
        )
        record.targets.add(ref_for_instance(account))
        annotate_connect_fees_for_year_month(month=8, year=2021)
        fee_record = TransactionRecord.objects.get(
            source=TransactionRecord.UNPROCESSED_EARNINGS, destination=TransactionRecord.ACH_TRANSACTION_FEES,
        )
        self.assertEqual(fee_record.amount, Money('2.50', 'USD'))

    @freeze_time('2021-08-01')
    def test_allocate_connect_fees_multiple_records_one_user(self):
        account = StripeAccountFactory.create()
        record1 = TransactionRecordFactory.create(
            payer=account.user, payee=account.user, source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK, amount=Money('50', 'USD'), category=TransactionRecord.CASH_WITHDRAW,
            finalized_on=timezone.now(),
        )
        record2 = TransactionRecordFactory.create(
            payer=account.user, payee=account.user, source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK, amount=Money('50', 'USD'), category=TransactionRecord.CASH_WITHDRAW,
            finalized_on=timezone.now(),
        )
        record1.targets.add(ref_for_instance(account))
        record2.targets.add(ref_for_instance(account))
        annotate_connect_fees_for_year_month(month=8, year=2021)
        fee_records = TransactionRecord.objects.filter(
            source=TransactionRecord.UNPROCESSED_EARNINGS, destination=TransactionRecord.ACH_TRANSACTION_FEES,
        )
        fee_total = sum([fee_record.amount for fee_record in fee_records])
        self.assertEqual(fee_total, Money('2.75', 'USD'))

    @freeze_time('2021-08-10')
    def test_multiple_connect_fees_multiple_records(self):
        account1 = StripeAccountFactory.create()
        account2 = StripeAccountFactory.create()
        record1 = TransactionRecordFactory.create(
            payer=account1.user, payee=account1.user, source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK, amount=Money('50', 'USD'), category=TransactionRecord.CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=2),
        )
        record2 = TransactionRecordFactory.create(
            payer=account1.user, payee=account1.user, source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK, amount=Money('50', 'USD'), category=TransactionRecord.CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=1),
        )
        record3 = TransactionRecordFactory.create(
            payer=account2.user, payee=account2.user, source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK, amount=Money('50', 'USD'), category=TransactionRecord.CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=4),
        )
        record4 = TransactionRecordFactory.create(
            payer=account2.user, payee=account2.user, source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK, amount=Money('50', 'USD'), category=TransactionRecord.CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=3),
        )
        record1.targets.add(ref_for_instance(account1))
        record2.targets.add(ref_for_instance(account1))
        record3.targets.add(ref_for_instance(account2))
        record4.targets.add(ref_for_instance(account2))
        annotate_connect_fees_for_year_month(month=8, year=2021)
        fee_records = TransactionRecord.objects.filter(
            source=TransactionRecord.UNPROCESSED_EARNINGS, destination=TransactionRecord.ACH_TRANSACTION_FEES,
        )
        fee_total = sum([fee_record.amount for fee_record in fee_records])
        self.assertEqual(fee_total, Money('5.50', 'USD'))
        fee_total = sum([fee_record.amount for fee_record in fee_records.filter(targets__in=[
            ref_for_instance(record3), ref_for_instance(record4)]
        )])
        self.assertEqual(fee_total, Money('2.76', 'USD'))
        fee_total = sum([fee_record.amount for fee_record in fee_records.filter(targets__in=[
            ref_for_instance(record1), ref_for_instance(record2)]
        )])
        self.assertEqual(fee_total, Money('2.74', 'USD'))

    @freeze_time('2021-08-10')
    def test_overseas_records(self):
        account = StripeAccountFactory.create()
        record1 = TransactionRecordFactory.create(
            payer=account.user, payee=account.user, source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK, amount=Money('50', 'USD'), category=TransactionRecord.CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=2),
        )
        record2 = TransactionRecordFactory.create(
            payer=account.user, payee=account.user, source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK, amount=Money('50', 'USD'), category=TransactionRecord.CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=1),
        )
        record1.targets.add(ref_for_instance(account))
        record2.targets.add(ref_for_instance(account))
        overseas_record1 = TransactionRecordFactory.create(
            payer=account.user, payee=account.user, source=TransactionRecord.PAYOUT_MIRROR_SOURCE,
            destination=TransactionRecord.PAYOUT_MIRROR_DESTINATION, amount=Money('20', 'CAD'),
            finalized_on=record1.finalized_on,
        )
        overseas_record2 = TransactionRecordFactory.create(
            payer=account.user, payee=account.user, source=TransactionRecord.PAYOUT_MIRROR_SOURCE,
            destination=TransactionRecord.PAYOUT_MIRROR_DESTINATION, finalized_on=record2.finalized_on,
            amount=Money('22', 'CAD'),
        )
        overseas_record1.targets.add(ref_for_instance(record1))
        overseas_record2.targets.add(ref_for_instance(record2))
        annotate_connect_fees_for_year_month(month=8, year=2021)
        fee_records = TransactionRecord.objects.filter(
            source=TransactionRecord.UNPROCESSED_EARNINGS, destination=TransactionRecord.ACH_TRANSACTION_FEES,
        )
        fee_total = sum([fee_record.amount for fee_record in fee_records])
        self.assertEqual(fee_total, Money('3.00', 'USD'))

    @freeze_time('2021-08-10')
    def test_overseas_and_domestic_records(self):
        account = StripeAccountFactory.create()
        record1 = TransactionRecordFactory.create(
            payer=account.user, payee=account.user, source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK, amount=Money('50', 'USD'), category=TransactionRecord.CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=2),
        )
        record2 = TransactionRecordFactory.create(
            payer=account.user, payee=account.user, source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK, amount=Money('50', 'USD'), category=TransactionRecord.CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=1),
        )
        record1.targets.add(ref_for_instance(account))
        record2.targets.add(ref_for_instance(account))
        overseas_record1 = TransactionRecordFactory.create(
            payer=account.user, payee=account.user, source=TransactionRecord.PAYOUT_MIRROR_SOURCE,
            destination=TransactionRecord.PAYOUT_MIRROR_DESTINATION, amount=Money('20', 'CAD'),
            finalized_on=record1.finalized_on,
        )
        overseas_record1.targets.add(ref_for_instance(record1))
        annotate_connect_fees_for_year_month(month=8, year=2021)
        fee_records = TransactionRecord.objects.filter(
            source=TransactionRecord.UNPROCESSED_EARNINGS, destination=TransactionRecord.ACH_TRANSACTION_FEES,
        )
        fee_total = sum([fee_record.amount for fee_record in fee_records])
        self.assertEqual(fee_total, Money('2.88', 'USD'))
        fee_record = fee_records.get(targets=ref_for_instance(record1))
        self.assertEqual(fee_record.amount, Money('1.51', 'USD'))
        fee_record = fee_records.get(targets=ref_for_instance(record2))
        self.assertEqual(fee_record.amount, Money('1.37', 'USD'))

    @freeze_time('2021-08-10')
    def test_idempotency(self):
        account = StripeAccountFactory.create()
        record1 = TransactionRecordFactory.create(
            payer=account.user, payee=account.user, source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK, amount=Money('50', 'USD'), category=TransactionRecord.CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=2),
        )
        record2 = TransactionRecordFactory.create(
            payer=account.user, payee=account.user, source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK, amount=Money('50', 'USD'), category=TransactionRecord.CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=1),
        )
        record1.targets.add(ref_for_instance(account))
        record2.targets.add(ref_for_instance(account))
        overseas_record1 = TransactionRecordFactory.create(
            payer=account.user, payee=account.user, source=TransactionRecord.PAYOUT_MIRROR_SOURCE,
            destination=TransactionRecord.PAYOUT_MIRROR_DESTINATION, amount=Money('20', 'CAD'),
            finalized_on=record1.finalized_on,
        )
        overseas_record1.targets.add(ref_for_instance(record1))
        annotate_connect_fees_for_year_month(month=8, year=2021)
        annotate_connect_fees_for_year_month(month=8, year=2021)
        fee_records = TransactionRecord.objects.filter(
            source=TransactionRecord.UNPROCESSED_EARNINGS, destination=TransactionRecord.ACH_TRANSACTION_FEES,
        )
        fee_total = sum([fee_record.amount for fee_record in fee_records])
        self.assertEqual(fee_total, Money('2.88', 'USD'))
        fee_record = fee_records.get(targets=ref_for_instance(record1))
        self.assertEqual(fee_record.amount, Money('1.51', 'USD'))
        fee_record = fee_records.get(targets=ref_for_instance(record2))
        self.assertEqual(fee_record.amount, Money('1.37', 'USD'))

    @freeze_time('2021-08-10')
    def test_celery_task(self):
        account = StripeAccountFactory.create()
        record1 = TransactionRecordFactory.create(
            payer=account.user, payee=account.user, source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK, amount=Money('50', 'USD'), category=TransactionRecord.CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=2),
        )
        record2 = TransactionRecordFactory.create(
            payer=account.user, payee=account.user, source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK, amount=Money('50', 'USD'), category=TransactionRecord.CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=1),
        )
        record1.targets.add(ref_for_instance(account))
        record2.targets.add(ref_for_instance(account))
        overseas_record1 = TransactionRecordFactory.create(
            payer=account.user, payee=account.user, source=TransactionRecord.PAYOUT_MIRROR_SOURCE,
            destination=TransactionRecord.PAYOUT_MIRROR_DESTINATION, amount=Money('20', 'CAD'),
            finalized_on=record1.finalized_on,
        )
        overseas_record1.targets.add(ref_for_instance(record1))
        annotate_connect_fees()
        fee_records = TransactionRecord.objects.filter(
            source=TransactionRecord.UNPROCESSED_EARNINGS, destination=TransactionRecord.ACH_TRANSACTION_FEES,
        )
        fee_total = sum([fee_record.amount for fee_record in fee_records])
        self.assertEqual(fee_total, Money('2.88', 'USD'))
        fee_record = fee_records.get(targets=ref_for_instance(record1))
        self.assertEqual(fee_record.amount, Money('1.51', 'USD'))
        fee_record = fee_records.get(targets=ref_for_instance(record2))
        self.assertEqual(fee_record.amount, Money('1.37', 'USD'))
