from datetime import date
from decimal import Decimal
from multiprocessing.pool import ThreadPool
from time import sleep
from unittest.mock import Mock, call, patch

from apps.lib.models import SUBSCRIPTION_DEACTIVATED, Notification, ref_for_instance
from apps.lib.test_resources import EnsurePlansMixin
from apps.profiles.tests.factories import UserFactory
from apps.sales.constants import (
    ACH_TRANSACTION_FEES,
    BANK,
    CANCELLED,
    CARD,
    CASH_WITHDRAW,
    COMPLETED,
    DRAFT,
    ESCROW,
    FAILURE,
    HOLDINGS,
    IN_PROGRESS,
    LIMBO,
    MISSED,
    NEW,
    OPEN,
    PAID,
    PAYMENT_PENDING,
    PAYOUT_MIRROR_DESTINATION,
    PAYOUT_MIRROR_SOURCE,
    PENDING,
    REVIEW,
    SUCCESS,
    UNPROCESSED_EARNINGS,
    VOID,
)
from apps.sales.models import Deliverable, Invoice, TransactionRecord
from apps.sales.tasks import (
    annotate_connect_fees,
    annotate_connect_fees_for_year_month,
    auto_finalize,
    auto_finalize_run,
    cancel_abandoned_orders,
    clear_cancelled_deliverables,
    clear_deliverable,
    destroy_expired_invoices,
    remind_sale,
    remind_sales,
    renew,
    renew_stripe_card,
    run_billing,
    stripe_transfer,
    withdraw_all,
    drip_placed_order,
)
from apps.sales.tests.factories import (
    CreditCardTokenFactory,
    DeliverableFactory,
    InvoiceFactory,
    LineItemFactory,
    ServicePlanFactory,
    StripeAccountFactory,
    TransactionRecordFactory,
)
from apps.sales.utils import add_service_plan_line, get_term_invoice
from dateutil.relativedelta import relativedelta
from django.core import mail
from django.db import connection
from django.test import TestCase, TransactionTestCase, override_settings
from django.utils import timezone
from djmoney.money import Money
from freezegun import freeze_time
from stripe.error import CardError


@patch("apps.sales.tasks.stripe")
class TestRenewStripeCard(EnsurePlansMixin, TestCase):
    def test_successful_renewal(self, mock_stripe):
        card = CreditCardTokenFactory.create(
            stripe_token="123", user__stripe_token="456"
        )
        user = card.user
        invoice = get_term_invoice(user)
        amount = Money("10.00", "USD")
        LineItemFactory.create(
            amount=amount,
            invoice=invoice,
        )
        mock_stripe.__enter__.return_value.PaymentIntent.create.return_value = {
            "id": "beep"
        }
        renew_stripe_card(card=card, invoice=invoice, user=user, price=amount)
        invoice.refresh_from_db()
        self.assertEqual(invoice.current_intent, "beep")
        mock_stripe.__enter__.return_value.PaymentIntent.create.assert_called_with(
            amount=1000,
            currency="usd",
            payment_method="123",
            customer="456",
            off_session=True,
            confirm=True,
            # TODO: Needs to change per service name, or else be omitted since we'll be
            #  swapping methods for tracking
            # subscriptions anyway.
            metadata={"service": "landscape", "invoice_id": invoice.id},
        )

    def test_zero_renewal(self, mock_stripe):
        card = CreditCardTokenFactory.create(
            stripe_token="123", user__stripe_token="456"
        )
        user = card.user
        invoice = get_term_invoice(user)
        renew_stripe_card(
            card=card, invoice=invoice, user=user, price=Money("0.00", "USD")
        )
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, PAID)
        mock_stripe.__enter__.return_value.PaymentIntent.create.assert_not_called()

    def test_failed_renewal(self, mock_stripe):
        card = CreditCardTokenFactory.create(last_four="9999")
        user = card.user
        invoice = get_term_invoice(user)
        amount = Money("10.00", "USD")
        LineItemFactory.create(
            amount=amount,
            invoice=invoice,
        )
        mock_stripe.__enter__.return_value.PaymentIntent.create.side_effect = CardError(
            "Borked!",
            code="Boink",
            param="number",
        )
        self.assertEqual(len(mail.outbox), 0)
        renew_stripe_card(card=card, invoice=invoice, user=user, price=amount)
        self.assertEqual(len(mail.outbox), 1)


@patch("apps.sales.tasks.renew_stripe_card")
class TestRenew(EnsurePlansMixin, TestCase):
    @freeze_time("2022-05-01")
    def test_no_card_specified_has_primary(self, mock_renew_stripe_card):
        card = CreditCardTokenFactory.create(
            user__service_plan_paid_through=timezone.now().date(),
            user__service_plan=self.landscape,
            user__next_service_plan=self.landscape,
        )
        card.user.primary_card = card
        card.user.save()
        invoice = get_term_invoice(card.user)
        add_service_plan_line(invoice, self.landscape)
        renew(card.user.id)
        mock_renew_stripe_card.assert_called_with(
            invoice=invoice,
            user=card.user,
            card=card,
            price=self.landscape.monthly_charge,
        )

    def test_renew_free_plan(self, mock_renew_stripe_card):
        user = UserFactory.create(
            service_plan=self.landscape,
            next_service_plan=self.free,
            service_plan_paid_through=date.today(),
        )
        renew(user.id)
        user.refresh_from_db()
        self.assertEqual(user.service_plan, self.free)
        mock_renew_stripe_card.assert_not_called()

    def test_renew_basic_plan(self, mock_renew_stripe_card):
        basic = ServicePlanFactory.create(
            monthly_charge=Money("0.00", "USD"),
            name="Basic",
            per_deliverable_price=Money("1.35", "USD"),
        )
        user = UserFactory.create(
            service_plan=basic,
            next_service_plan=basic,
            service_plan_paid_through=date.today(),
        )
        renew(user.id)
        user.refresh_from_db()
        self.assertEqual(user.service_plan, basic)
        mock_renew_stripe_card.assert_not_called()
        self.assertEqual(
            user.service_plan_paid_through,
            timezone.now().date() + relativedelta(months=1),
        )

    @freeze_time("2022-05-01")
    def test_no_card_specified(self, mock_renew_stripe_card):
        card = CreditCardTokenFactory.create(
            user__service_plan_paid_through=timezone.now().date(),
            user__service_plan=self.landscape,
            user__next_service_plan=self.landscape,
        )
        card2 = CreditCardTokenFactory.create(user=card.user)
        card.user.primary_card = card
        card.user.save()
        invoice = get_term_invoice(card.user)
        add_service_plan_line(invoice, self.landscape)
        renew(card.user.id, card_id=card2.id)
        mock_renew_stripe_card.assert_called_with(
            invoice=invoice,
            user=card.user,
            card=card2,
            price=self.landscape.monthly_charge,
        )

    @freeze_time("2022-05-01")
    def test_no_card_specified_no_primary_has_card(self, mock_renew_stripe_card):
        card = CreditCardTokenFactory.create(
            user__service_plan_paid_through=timezone.now().date(),
            user__service_plan=self.landscape,
            user__next_service_plan=self.landscape,
        )
        card.user.primary_card = None
        card.user.save()
        invoice = get_term_invoice(card.user)
        add_service_plan_line(invoice, self.landscape)
        renew(card.user.id)
        mock_renew_stripe_card.assert_called_with(
            invoice=invoice,
            user=card.user,
            card=card,
            price=self.landscape.monthly_charge,
        )

    @freeze_time("2022-05-01")
    def test_no_card_specified_no_card(self, mock_renew_stripe_card):
        user = UserFactory.create(
            primary_card=None,
            service_plan_paid_through=timezone.now().date(),
            service_plan=self.landscape,
            next_service_plan=self.landscape,
        )
        self.assertEqual(len(mail.outbox), 0)
        renew(user.id)
        mock_renew_stripe_card.assert_not_called()
        self.assertEqual(len(mail.outbox), 1)

    @freeze_time("2022-05-01")
    def test_user_already_current(self, mock_renew_stripe_card):
        user = UserFactory.create(
            primary_card=None,
            service_plan_paid_through=timezone.now().date() + relativedelta(days=5),
            service_plan=self.landscape,
            next_service_plan=self.landscape,
        )
        self.assertEqual(len(mail.outbox), 0)
        renew(user.id)
        mock_renew_stripe_card.assert_not_called()
        self.assertEqual(len(mail.outbox), 0)

    @freeze_time("2022-05-01")
    def test_renewal_card_failure(self, mock_renew_stripe_card):
        card = CreditCardTokenFactory.create(
            user__service_plan_paid_through=timezone.now().date(),
            user__service_plan=self.landscape,
            user__next_service_plan=self.landscape,
        )
        self.assertEqual(len(mail.outbox), 0)
        mock_renew_stripe_card.return_value = False
        invoice = get_term_invoice(card.user)
        add_service_plan_line(invoice, self.landscape)
        renew(card.user.id)
        mock_renew_stripe_card.assert_called_with(
            invoice=invoice,
            user=card.user,
            card=card,
            price=self.landscape.monthly_charge,
        )
        # Mail would be sent by renew_stripe_card, which is mocked.
        self.assertEqual(len(mail.outbox), 0)

    @freeze_time("2022-05-01")
    @patch("apps.sales.tasks.logger")
    def test_subscription_date_corrupt(self, mock_logger, mock_renew_stripe_card):
        card = CreditCardTokenFactory.create(
            user__service_plan_paid_through=None,
            user__service_plan=self.landscape,
            user__next_service_plan=self.landscape,
        )
        user = card.user
        self.assertEqual(len(mail.outbox), 0)
        mock_renew_stripe_card.return_value = False
        renew(user.id)
        mock_renew_stripe_card.assert_not_called()
        mock_logger.error.assert_called_with(
            f"!!! {user.username}({user.id}) has NONE for service_plan_paid_through "
            f"with subscription enabled!",
        )
        self.assertEqual(len(mail.outbox), 0)


class TestAutoRenewal(EnsurePlansMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.service_plan = ServicePlanFactory(monthly_charge=Money("6.00", "USD"))
        self.basic_plan = ServicePlanFactory(
            monthly_charge=Money("0.00", "USD"),
            per_deliverable_price=Money("1.00", "USD"),
        )

    @patch("apps.sales.tasks.renew")
    @freeze_time("2018-02-10 12:00:00")
    @override_settings(TERM_GRACE_DAYS=5)
    def test_tasks_made(self, mock_renew):
        disable = UserFactory.create(
            service_plan=self.service_plan, service_plan_paid_through=date(2018, 1, 1)
        )
        renew_landscape = UserFactory.create(
            service_plan=self.service_plan, service_plan_paid_through=date(2018, 2, 7)
        )
        renew_basic = UserFactory.create(
            service_plan=self.basic_plan, service_plan_paid_through=date(2018, 2, 7)
        )
        run_billing()
        disable.refresh_from_db()
        self.assertFalse(disable.landscape_enabled)
        mock_renew.delay.assert_has_calls(
            [call(renew_landscape.id), call(renew_basic.id)]
        )
        self.assertEqual(
            Notification.objects.filter(event__type=SUBSCRIPTION_DEACTIVATED).count(), 1
        )
        self.assertEqual(len(mail.outbox), 1)
        for letter in mail.outbox:
            self.assertEqual(letter.subject, "Your subscription has been deactivated.")


class TestFinalizers(EnsurePlansMixin, TestCase):
    @freeze_time("2018-02-10 12:00:00")
    @patch("apps.sales.tasks.auto_finalize")
    def test_auto_finalize_run(self, mock_auto_finalize):
        deliverable = DeliverableFactory.create(
            status=REVIEW, auto_finalize_on=date(2018, 2, 10)
        )
        order2 = DeliverableFactory.create(
            status=REVIEW, auto_finalize_on=date(2018, 2, 9)
        )
        DeliverableFactory.create(
            status=PAYMENT_PENDING, auto_finalize_on=date(2018, 2, 9)
        )
        DeliverableFactory.create(status=REVIEW, auto_finalize_on=date(2018, 2, 11))
        auto_finalize_run()
        mock_auto_finalize.delay.assert_has_calls(
            [call(deliverable.id), call(order2.id)], any_order=True
        )
        self.assertEqual(mock_auto_finalize.delay.call_count, 2)

    @freeze_time("2018-02-10 12:00:00")
    @patch("apps.sales.tasks.finalize_deliverable")
    def test_auto_finalize(self, mock_finalize_deliverable):
        deliverable = DeliverableFactory.create(
            status=REVIEW, auto_finalize_on=date(2018, 2, 10)
        )
        auto_finalize(deliverable.id)
        mock_finalize_deliverable.assert_called_with(deliverable)

    @freeze_time("2018-02-10 12:00:00")
    @patch("apps.sales.tasks.finalize_deliverable")
    def test_auto_finalize_old(self, mock_finalize_deliverable):
        deliverable = DeliverableFactory.create(
            status=REVIEW, auto_finalize_on=date(2018, 2, 9)
        )
        auto_finalize(deliverable.id)
        mock_finalize_deliverable.assert_called_with(deliverable)

    @freeze_time("2018-02-10 12:00:00")
    @patch("apps.sales.tasks.finalize_deliverable")
    def test_auto_finalize_wrong_status(self, mock_finalize_deliverable):
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, auto_finalize_on=date(2018, 2, 9)
        )
        auto_finalize(deliverable.id)
        mock_finalize_deliverable.assert_not_called()

    @freeze_time("2018-02-10 12:00:00")
    @patch("apps.sales.tasks.finalize_deliverable")
    def test_auto_finalize_not_yet(self, mock_finalize_deliverable):
        deliverable = DeliverableFactory.create(
            status=REVIEW, auto_finalize_on=date(2018, 2, 11)
        )
        auto_finalize(deliverable.id)
        mock_finalize_deliverable.assert_not_called()

    @freeze_time("2018-02-10 12:00:00")
    @patch("apps.sales.tasks.finalize_deliverable")
    def test_auto_finalize_null(self, mock_finalize_deliverable):
        deliverable = DeliverableFactory.create(status=REVIEW, auto_finalize_on=None)
        auto_finalize(deliverable.id)
        mock_finalize_deliverable.assert_not_called()


def wrapped_withdraw(user_id):
    try:
        withdraw_all(user_id)
    finally:
        connection.close()


class TestWithdrawAll(EnsurePlansMixin, TransactionTestCase):
    @patch("apps.sales.tasks.account_balance")
    @patch("apps.sales.tasks.stripe_transfer.delay")
    def test_withdraw_all(self, stripe_transfer, mock_balance):
        user = UserFactory.create()
        # Avoid initial call in post-creation hook.
        mock_balance.return_value = Decimal("0.00")
        bank = StripeAccountFactory.create(user=user)
        stripe_transfer.assert_not_called()
        mock_balance.return_value = Decimal("25.00")
        stripe_transfer.return_value = None, Deliverable.objects.none()
        withdraw_all(user.id)
        # Normally, three dollars would be removed here for the connection fee,
        # but we're always returning a balance of $25.
        record = TransactionRecord.objects.get(category=CASH_WITHDRAW)
        stripe_transfer.assert_called_with(record.id, bank.id, None)

    @patch("apps.sales.tasks.account_balance")
    @patch("apps.sales.tasks.stripe_transfer.delay")
    def test_withdraw_all_no_auto(self, stripe_transfer, mock_balance):
        user = UserFactory.create()
        user.artist_profile.auto_withdraw = False
        user.artist_profile.save()
        mock_balance.return_value = Decimal("0.00")
        StripeAccountFactory.create(user=user)
        stripe_transfer.assert_not_called()
        mock_balance.return_value = Decimal("25.00")
        withdraw_all(user.id)
        stripe_transfer.assert_not_called()

    @patch("apps.sales.tasks.stripe_transfer.delay")
    def test_withdraw_mutex(self, stripe_transfer):
        user = UserFactory.create()
        StripeAccountFactory(user=user)
        TransactionRecordFactory(
            payee=user, destination=HOLDINGS, amount=Money("10.00", "USD")
        )

        def side_effect(x, y, z):
            sleep(0.25)
            return None, Deliverable.objects.none()

        stripe_transfer.side_effect = side_effect
        pool = ThreadPool(processes=4)
        pool.map(wrapped_withdraw, [user.id] * 4)
        pool.close()
        pool.join()
        records = TransactionRecord.objects.filter(destination=BANK)
        self.assertEqual(records.count(), 1)

    @patch("apps.sales.tasks.record_to_invoice_map")
    def test_withdraw_all_bails_on_zero(self, mock_mapper):
        user = UserFactory.create()
        StripeAccountFactory(user=user)
        withdraw_all(user.id)
        mock_mapper.assert_not_called()

    @patch("apps.sales.tasks.stripe_transfer.delay")
    def test_withdraw_amount_matches(self, stripe_transfer):
        user = UserFactory.create()
        account = StripeAccountFactory(user=user)
        deliverable = DeliverableFactory.create(
            order__seller=user, status=COMPLETED, invoice__payout_sent=False
        )
        deliverable.invoice.payout_available = True
        deliverable.invoice.status = PAID
        deliverable.invoice.save()
        record = TransactionRecordFactory(
            payee=user, destination=HOLDINGS, amount=Money("10.00", "USD")
        )
        record.targets.add(
            ref_for_instance(deliverable), ref_for_instance(deliverable.invoice)
        )
        withdraw_all(user.id)
        transfer = TransactionRecord.objects.get(destination=BANK)
        self.assertCountEqual(
            [target.target for target in transfer.targets.all()],
            [deliverable, deliverable.invoice, account],
        )
        self.assertEqual(transfer.amount, Money("10.00", "USD"))
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.invoice.payout_sent, True)
        stripe_transfer.assert_called_with(
            transfer.id, account.id, deliverable.invoice.id
        )


@patch("apps.sales.tasks.stripe")
class TestStripeTransfer(EnsurePlansMixin, TestCase):
    def test_send_transfer_deliverable(self, mock_stripe):
        deliverable = DeliverableFactory.create()
        record = TransactionRecordFactory.create(
            payee=deliverable.order.seller,
            amount=Money("10.00", "USD"),
            status=FAILURE,
        )
        account = StripeAccountFactory.create(
            user=deliverable.order.seller, token="foo"
        )
        mock_stripe.__enter__.return_value.Transfer.create.return_value = {
            "id": "beep",
            "destination_payment": "boop",
            "balance_transaction": "1234",
        }
        stripe_transfer(record.id, account.id, invoice_id=deliverable.invoice.id)
        record.refresh_from_db()
        self.assertEqual(record.status, PENDING)
        mock_stripe.__enter__.return_value.Transfer.create.assert_called_with(
            metadata={"reference_transaction": record.id},
            transfer_group=f"ACInvoice#{deliverable.invoice.id}",
            amount=1000,
            currency="usd",
            destination="foo",
        )

    def test_send_transfer_failed_with_invoice(self, mock_stripe):
        deliverable = DeliverableFactory.create(invoice__payout_sent=True)
        record = TransactionRecordFactory.create(
            payee=deliverable.order.seller,
            amount=Money("10.00", "USD"),
            status=FAILURE,
        )
        account = StripeAccountFactory.create(
            user=deliverable.order.seller, token="foo"
        )
        mock_stripe.__enter__.return_value.Transfer.create.side_effect = ValueError(
            "Failed!"
        )
        stripe_transfer(record.id, account.id, invoice_id=deliverable.invoice.id)
        record.refresh_from_db()
        self.assertEqual(record.status, FAILURE)
        self.assertEqual(record.response_message, "Failed!")
        deliverable.refresh_from_db()
        self.assertFalse(deliverable.invoice.payout_sent)

    def test_send_transfer_deliverable_with_source(self, mock_stripe):
        deliverable = DeliverableFactory.create()
        record = TransactionRecordFactory.create(
            payee=deliverable.order.seller,
            payer=deliverable.order.seller,
            amount=Money("10.00", "USD"),
            status=FAILURE,
        )
        source_record = TransactionRecordFactory.create(
            source=CARD,
            destination=ESCROW,
            status=SUCCESS,
            remote_ids=["ch_stuff", "things"],
        )
        source_record.targets.add(ref_for_instance(deliverable.invoice))
        account = StripeAccountFactory.create(
            user=deliverable.order.seller, token="foo"
        )
        mock_stripe.__enter__.return_value.Transfer.create.return_value = {
            "id": "beep",
            "destination_payment": "boop",
            "balance_transaction": "1234",
        }
        stripe_transfer(record.id, account.id, invoice_id=deliverable.invoice.id)
        record.refresh_from_db()
        self.assertEqual(record.status, PENDING)
        mock_stripe.__enter__.return_value.Transfer.create.assert_called_with(
            metadata={"reference_transaction": record.id},
            transfer_group=f"ACInvoice#{deliverable.invoice.id}",
            amount=1000,
            currency="usd",
            destination="foo",
            source_transaction="ch_stuff",
        )

    def test_send_transfer_deliverable_with_unmarked_source(self, mock_stripe):
        deliverable = DeliverableFactory.create()
        record = TransactionRecordFactory.create(
            payee=deliverable.order.seller,
            payer=deliverable.order.seller,
            amount=Money("10.00", "USD"),
            status=FAILURE,
        )
        source_record = TransactionRecordFactory.create(
            source=CARD, destination=ESCROW, status=SUCCESS, remote_ids=["things"]
        )
        source_record.targets.add(ref_for_instance(deliverable.invoice))
        account = StripeAccountFactory.create(
            user=deliverable.order.seller, token="foo"
        )
        mock_stripe.__enter__.return_value.Transfer.create.return_value = {
            "id": "beep",
            "destination_payment": "boop",
            "balance_transaction": "1234",
        }
        stripe_transfer(record.id, account.id, invoice_id=deliverable.invoice.id)
        record.refresh_from_db()
        self.assertEqual(record.status, PENDING)
        mock_stripe.__enter__.return_value.Transfer.create.assert_called_with(
            metadata={"reference_transaction": record.id},
            transfer_group=f"ACInvoice#{deliverable.invoice.id}",
            amount=1000,
            currency="usd",
            destination="foo",
        )

    def test_send_transfer_no_invoice(self, mock_stripe):
        user = UserFactory.create()
        record = TransactionRecordFactory.create(
            payee=user,
            amount=Money("10.00", "USD"),
            status=FAILURE,
        )
        account = StripeAccountFactory.create(user=user, token="foo")
        mock_stripe.__enter__.return_value.Transfer.create.return_value = {
            "id": "beep",
            "destination_payment": "boop",
            "balance_transaction": "1234",
        }
        stripe_transfer(record.id, account.id)
        record.refresh_from_db()
        self.assertEqual(record.status, PENDING)
        mock_stripe.__enter__.return_value.Transfer.create.assert_called_with(
            metadata={"reference_transaction": record.id},
            amount=1000,
            currency="usd",
            destination="foo",
        )

    def test_send_transfer_fails_no_deliverable(self, mock_stripe):
        user = UserFactory.create()
        record = TransactionRecordFactory.create(
            payee=user,
            amount=Money("10.00", "USD"),
            status=FAILURE,
        )
        account = StripeAccountFactory.create(user=user, token="foo")
        mock_stripe.__enter__.return_value.Transfer.create.side_effect = ValueError(
            "Failed!"
        )
        stripe_transfer(record.id, account.id)
        record.refresh_from_db()
        self.assertEqual(record.status, FAILURE)
        self.assertEqual(record.response_message, "Failed!")


class TestReminders(EnsurePlansMixin, TestCase):
    @freeze_time("2018-02-10 12:00:00")
    @patch("apps.sales.tasks.Deliverable")
    @patch("apps.sales.tasks.remind_sale")
    def test_reminder_emails(self, mock_remind_sale, mock_deliverable):
        def build_calls(order_list, differences):
            for i in differences:
                mock = Mock()
                # Negative to make distinct so we know the arguments are in the right
                # order.
                mock.id = 0 - i
                mock.auto_cancel_on = timezone.now() - relativedelta(days=i)
                order_list.append(mock)

        to_remind = []
        build_calls(to_remind, [3, 6, 9, 12, 15, 18])
        all_orders = [*to_remind]
        # To be ignored.
        build_calls(all_orders, [1, 2, 4, 7, 8, 10, 11, 13, 14, 16, 17, 19])
        mock_deliverable.objects.filter.return_value = all_orders
        remind_sales()
        self.assertEqual(mock_remind_sale.delay.call_count, 6)
        to_remind = [call(order.id) for order in to_remind]
        mock_remind_sale.delay.assert_has_calls(to_remind, any_order=True)
        timestamp = timezone.now()
        timestamp = timestamp.replace(year=2018, month=2, day=10, hour=12, minute=0)
        mock_deliverable.objects.filter.assert_called_with(
            status=NEW,
            auto_cancel_on__gte=timestamp,
            auto_cancel_on__isnull=False,
        )

    @freeze_time("2020-08-01 15:21:34")
    def test_send_reminder(self):
        deliverable = DeliverableFactory.create(
            status=NEW,
            details="# This is a test\n\nDo things and stuff.",
            auto_cancel_on=timezone.now(),
        )
        remind_sale(deliverable.id)
        self.assertEqual(
            mail.outbox[0].subject, "Your commissioner is awaiting your response!"
        )
        self.assertIn("08/01/2020", mail.outbox[0].body)

    def test_status_changed(self):
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, details="# This is a test\n\nDo things and stuff."
        )
        remind_sale(deliverable.id)
        self.assertEqual(len(mail.outbox), 0)


class TestDeliverableClear(EnsurePlansMixin, TestCase):
    @patch("apps.sales.tasks.clear_deliverable")
    def test_clear_deliverables(self, mock_clear):
        chosen = DeliverableFactory(
            status=MISSED, cancelled_on=timezone.now() - relativedelta(months=2)
        )
        DeliverableFactory(
            status=CANCELLED, cancelled_on=timezone.now() - relativedelta(months=2)
        )
        DeliverableFactory(status=MISSED, cancelled_on=timezone.now())
        DeliverableFactory(status=MISSED, cancelled_on=None)
        DeliverableFactory(status=MISSED, cancelled_on=None)
        clear_cancelled_deliverables()
        mock_clear.delay.assert_called_with(chosen.id)
        mock_clear.assert_not_called()
        self.assertEqual(mock_clear.delay.call_count, 1)

    @patch("apps.sales.tasks.destroy_deliverable")
    def test_clear_deliverable(self, mock_destroy):
        not_relevant = DeliverableFactory(status=IN_PROGRESS)
        clear_deliverable(not_relevant.id)
        mock_destroy.assert_not_called()
        # Non-existent
        clear_deliverable(-1)
        mock_destroy.assert_not_called()
        relevant = DeliverableFactory(status=MISSED)
        clear_deliverable(relevant.id)
        mock_destroy.assert_called_with(relevant)


@override_settings(
    STRIPE_PAYOUT_STATIC=Money("0.25", "USD"),
    STRIPE_PAYOUT_PERCENTAGE=Decimal("0.25"),
    STRIPE_PAYOUT_CROSS_BORDER_PERCENTAGE=Decimal("0.25"),
    STRIPE_ACTIVE_ACCOUNT_MONTHLY_FEE=Money("2.00", "USD"),
)
class TestAnnotatePayouts(EnsurePlansMixin, TestCase):
    @freeze_time("2021-08-01")
    def test_allocate_connect_fees_one_record(self):
        account = StripeAccountFactory.create()
        record = TransactionRecordFactory.create(
            payer=account.user,
            payee=account.user,
            source=HOLDINGS,
            destination=BANK,
            amount=Money("100", "USD"),
            category=CASH_WITHDRAW,
            finalized_on=timezone.now(),
        )
        record.targets.add(ref_for_instance(account))
        annotate_connect_fees_for_year_month(month=8, year=2021)
        fee_record = TransactionRecord.objects.get(
            source=UNPROCESSED_EARNINGS,
            destination=ACH_TRANSACTION_FEES,
        )
        self.assertEqual(fee_record.amount, Money("2.50", "USD"))

    @freeze_time("2021-08-01")
    def test_allocate_connect_fees_multiple_records_one_user(self):
        account = StripeAccountFactory.create()
        record1 = TransactionRecordFactory.create(
            payer=account.user,
            payee=account.user,
            source=HOLDINGS,
            destination=BANK,
            amount=Money("50", "USD"),
            category=CASH_WITHDRAW,
            finalized_on=timezone.now(),
        )
        record2 = TransactionRecordFactory.create(
            payer=account.user,
            payee=account.user,
            source=HOLDINGS,
            destination=BANK,
            amount=Money("50", "USD"),
            category=CASH_WITHDRAW,
            finalized_on=timezone.now(),
        )
        record1.targets.add(ref_for_instance(account))
        record2.targets.add(ref_for_instance(account))
        annotate_connect_fees_for_year_month(month=8, year=2021)
        fee_records = TransactionRecord.objects.filter(
            source=UNPROCESSED_EARNINGS,
            destination=ACH_TRANSACTION_FEES,
        )
        fee_total = sum([fee_record.amount for fee_record in fee_records])
        self.assertEqual(fee_total, Money("2.75", "USD"))

    @freeze_time("2021-08-10")
    def test_multiple_connect_fees_multiple_records(self):
        account1 = StripeAccountFactory.create()
        account2 = StripeAccountFactory.create()
        record1 = TransactionRecordFactory.create(
            payer=account1.user,
            payee=account1.user,
            source=HOLDINGS,
            destination=BANK,
            amount=Money("50", "USD"),
            category=CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=2),
        )
        record2 = TransactionRecordFactory.create(
            payer=account1.user,
            payee=account1.user,
            source=HOLDINGS,
            destination=BANK,
            amount=Money("50", "USD"),
            category=CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=1),
        )
        record3 = TransactionRecordFactory.create(
            payer=account2.user,
            payee=account2.user,
            source=HOLDINGS,
            destination=BANK,
            amount=Money("50", "USD"),
            category=CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=4),
        )
        record4 = TransactionRecordFactory.create(
            payer=account2.user,
            payee=account2.user,
            source=HOLDINGS,
            destination=BANK,
            amount=Money("50", "USD"),
            category=CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=3),
        )
        record1.targets.add(ref_for_instance(account1))
        record2.targets.add(ref_for_instance(account1))
        record3.targets.add(ref_for_instance(account2))
        record4.targets.add(ref_for_instance(account2))
        annotate_connect_fees_for_year_month(month=8, year=2021)
        fee_records = TransactionRecord.objects.filter(
            source=UNPROCESSED_EARNINGS,
            destination=ACH_TRANSACTION_FEES,
        )
        fee_total = sum([fee_record.amount for fee_record in fee_records])
        self.assertEqual(fee_total, Money("5.50", "USD"))
        fee_total = sum(
            [
                fee_record.amount
                for fee_record in fee_records.filter(
                    targets__in=[ref_for_instance(record3), ref_for_instance(record4)]
                )
            ]
        )
        self.assertEqual(fee_total, Money("2.76", "USD"))
        fee_total = sum(
            [
                fee_record.amount
                for fee_record in fee_records.filter(
                    targets__in=[ref_for_instance(record1), ref_for_instance(record2)]
                )
            ]
        )
        self.assertEqual(fee_total, Money("2.74", "USD"))

    @freeze_time("2021-08-10")
    def test_overseas_records(self):
        account = StripeAccountFactory.create()
        record1 = TransactionRecordFactory.create(
            payer=account.user,
            payee=account.user,
            source=HOLDINGS,
            destination=BANK,
            amount=Money("50", "USD"),
            category=CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=2),
        )
        record2 = TransactionRecordFactory.create(
            payer=account.user,
            payee=account.user,
            source=HOLDINGS,
            destination=BANK,
            amount=Money("50", "USD"),
            category=CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=1),
        )
        record1.targets.add(ref_for_instance(account))
        record2.targets.add(ref_for_instance(account))
        overseas_record1 = TransactionRecordFactory.create(
            payer=account.user,
            payee=account.user,
            source=PAYOUT_MIRROR_SOURCE,
            destination=PAYOUT_MIRROR_DESTINATION,
            amount=Money("20", "CAD"),
            finalized_on=record1.finalized_on,
        )
        overseas_record2 = TransactionRecordFactory.create(
            payer=account.user,
            payee=account.user,
            source=PAYOUT_MIRROR_SOURCE,
            destination=PAYOUT_MIRROR_DESTINATION,
            finalized_on=record2.finalized_on,
            amount=Money("22", "CAD"),
        )
        overseas_record1.targets.add(ref_for_instance(record1))
        overseas_record2.targets.add(ref_for_instance(record2))
        annotate_connect_fees_for_year_month(month=8, year=2021)
        fee_records = TransactionRecord.objects.filter(
            source=UNPROCESSED_EARNINGS,
            destination=ACH_TRANSACTION_FEES,
        )
        fee_total = sum([fee_record.amount for fee_record in fee_records])
        self.assertEqual(fee_total, Money("3.00", "USD"))

    @freeze_time("2021-08-10")
    def test_overseas_and_domestic_records(self):
        account = StripeAccountFactory.create()
        record1 = TransactionRecordFactory.create(
            payer=account.user,
            payee=account.user,
            source=HOLDINGS,
            destination=BANK,
            amount=Money("50", "USD"),
            category=CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=2),
        )
        record2 = TransactionRecordFactory.create(
            payer=account.user,
            payee=account.user,
            source=HOLDINGS,
            destination=BANK,
            amount=Money("50", "USD"),
            category=CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=1),
        )
        record1.targets.add(ref_for_instance(account))
        record2.targets.add(ref_for_instance(account))
        overseas_record1 = TransactionRecordFactory.create(
            payer=account.user,
            payee=account.user,
            source=PAYOUT_MIRROR_SOURCE,
            destination=PAYOUT_MIRROR_DESTINATION,
            amount=Money("20", "CAD"),
            finalized_on=record1.finalized_on,
        )
        overseas_record1.targets.add(ref_for_instance(record1))
        annotate_connect_fees_for_year_month(month=8, year=2021)
        fee_records = TransactionRecord.objects.filter(
            source=UNPROCESSED_EARNINGS,
            destination=ACH_TRANSACTION_FEES,
        )
        fee_total = sum([fee_record.amount for fee_record in fee_records])
        self.assertEqual(fee_total, Money("2.88", "USD"))
        fee_record = fee_records.get(targets=ref_for_instance(record1))
        self.assertEqual(fee_record.amount, Money("1.51", "USD"))
        fee_record = fee_records.get(targets=ref_for_instance(record2))
        self.assertEqual(fee_record.amount, Money("1.37", "USD"))

    @freeze_time("2021-08-10")
    def test_idempotency(self):
        account = StripeAccountFactory.create()
        record1 = TransactionRecordFactory.create(
            payer=account.user,
            payee=account.user,
            source=HOLDINGS,
            destination=BANK,
            amount=Money("50", "USD"),
            category=CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=2),
        )
        record2 = TransactionRecordFactory.create(
            payer=account.user,
            payee=account.user,
            source=HOLDINGS,
            destination=BANK,
            amount=Money("50", "USD"),
            category=CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=1),
        )
        record1.targets.add(ref_for_instance(account))
        record2.targets.add(ref_for_instance(account))
        overseas_record1 = TransactionRecordFactory.create(
            payer=account.user,
            payee=account.user,
            source=PAYOUT_MIRROR_SOURCE,
            destination=PAYOUT_MIRROR_DESTINATION,
            amount=Money("20", "CAD"),
            finalized_on=record1.finalized_on,
        )
        overseas_record1.targets.add(ref_for_instance(record1))
        annotate_connect_fees_for_year_month(month=8, year=2021)
        annotate_connect_fees_for_year_month(month=8, year=2021)
        fee_records = TransactionRecord.objects.filter(
            source=UNPROCESSED_EARNINGS,
            destination=ACH_TRANSACTION_FEES,
        )
        fee_total = sum([fee_record.amount for fee_record in fee_records])
        self.assertEqual(fee_total, Money("2.88", "USD"))
        fee_record = fee_records.get(targets=ref_for_instance(record1))
        self.assertEqual(fee_record.amount, Money("1.51", "USD"))
        fee_record = fee_records.get(targets=ref_for_instance(record2))
        self.assertEqual(fee_record.amount, Money("1.37", "USD"))

    @freeze_time("2021-08-10")
    def test_celery_task(self):
        account = StripeAccountFactory.create()
        record1 = TransactionRecordFactory.create(
            payer=account.user,
            payee=account.user,
            source=HOLDINGS,
            destination=BANK,
            amount=Money("50", "USD"),
            category=CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=2),
        )
        record2 = TransactionRecordFactory.create(
            payer=account.user,
            payee=account.user,
            source=HOLDINGS,
            destination=BANK,
            amount=Money("50", "USD"),
            category=CASH_WITHDRAW,
            finalized_on=timezone.now() - relativedelta(days=1),
        )
        record1.targets.add(ref_for_instance(account))
        record2.targets.add(ref_for_instance(account))
        overseas_record1 = TransactionRecordFactory.create(
            payer=account.user,
            payee=account.user,
            source=PAYOUT_MIRROR_SOURCE,
            destination=PAYOUT_MIRROR_DESTINATION,
            amount=Money("20", "CAD"),
            finalized_on=record1.finalized_on,
        )
        overseas_record1.targets.add(ref_for_instance(record1))
        annotate_connect_fees()
        fee_records = TransactionRecord.objects.filter(
            source=UNPROCESSED_EARNINGS,
            destination=ACH_TRANSACTION_FEES,
        )
        fee_total = sum([fee_record.amount for fee_record in fee_records])
        self.assertEqual(fee_total, Money("2.88", "USD"))
        fee_record = fee_records.get(targets=ref_for_instance(record1))
        self.assertEqual(fee_record.amount, Money("1.51", "USD"))
        fee_record = fee_records.get(targets=ref_for_instance(record2))
        self.assertEqual(fee_record.amount, Money("1.37", "USD"))

    @freeze_time("2022-08-02")
    @patch("apps.sales.tasks.annotate_connect_fees_for_year_month")
    def test_runs_once_normally(self, mock_annotate):
        annotate_connect_fees()
        mock_annotate.assert_called_once_with(month=8, year=2022)

    @freeze_time("2022-01-01")
    @patch("apps.sales.tasks.annotate_connect_fees_for_year_month")
    def test_runs_twice_on_first(self, mock_annotate):
        annotate_connect_fees()
        mock_annotate.assert_any_call(month=1, year=2022)
        # Checks the last call.
        mock_annotate.assert_called_with(month=12, year=2021)

    def test_no_records(self):
        # Shouldn't raise anything.
        annotate_connect_fees()
        # Shouldn't create anything.
        self.assertEqual(TransactionRecord.objects.all().count(), 0)


class TestDestroyExpiredInvoices(EnsurePlansMixin, TestCase):
    def test_destroy_invoices(self):
        user = UserFactory.create()
        for status in [DRAFT, OPEN, VOID]:
            invoice = InvoiceFactory.create(
                status=status, bill_to=user, expires_on=timezone.now()
            )
            destroy_expired_invoices()
            with self.assertRaises(Invoice.DoesNotExist):
                invoice.refresh_from_db()

    def test_ignore_non_expired(self):
        # Should not be affected due to date.
        invoice = InvoiceFactory.create(
            status=OPEN,
            expires_on=timezone.now() + relativedelta(days=1, hours=1),
        )
        destroy_expired_invoices()
        # Should still exist.
        invoice.refresh_from_db()

    def test_ignore_no_date(self):
        # Should not be affected due to date.
        invoice = InvoiceFactory.create(
            status=OPEN,
            expires_on=None,
        )
        destroy_expired_invoices()
        # Should still exist.
        invoice.refresh_from_db()

    def test_ignore_wrong_status(self):
        # Should not be affected due to date.
        invoice = InvoiceFactory.create(
            status=PAID,
            expires_on=timezone.now(),
        )
        destroy_expired_invoices()
        # Should still exist.
        invoice.refresh_from_db()


class TestCancelAbandonedOrders(EnsurePlansMixin, TestCase):
    def test_cancel_deliverable_emails_and_closes(self):
        to_cancel = DeliverableFactory.create(auto_cancel_on=timezone.now(), status=NEW)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(Notification.objects.all().count(), 0)
        self.assertFalse(to_cancel.order.seller.artist_profile.commissions_closed)
        cancel_abandoned_orders()
        to_cancel.refresh_from_db()
        self.assertEqual(to_cancel.status, CANCELLED)
        self.assertTrue(to_cancel.order.seller.artist_profile.commissions_closed)
        self.assertEqual(len(mail.outbox), 3)
        subjects = [item.subject for item in mail.outbox]
        self.assertIn("Your commissions have been automatically closed.", subjects)

    @override_settings(LIMBO_DAYS=5)
    def test_limbo_to_missed(self):
        to_miss = DeliverableFactory.create(
            created_on=timezone.now() - relativedelta(days=10), status=LIMBO
        )
        cancel_abandoned_orders()
        to_miss.refresh_from_db()
        self.assertEqual(to_miss.status, MISSED)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(Notification.objects.all().count(), 2)
        self.assertFalse(to_miss.order.seller.artist_profile.commissions_closed)
        self.assertIn("Your sale was cancelled.", mail.outbox[0].subject)

    def test_limbo_too_early(self):
        to_miss = DeliverableFactory.create(
            auto_cancel_on=timezone.now() - relativedelta(days=2), status=LIMBO
        )
        cancel_abandoned_orders()
        to_miss.refresh_from_db()
        self.assertEqual(to_miss.status, LIMBO)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(Notification.objects.all().count(), 0)
        self.assertFalse(to_miss.order.seller.artist_profile.commissions_closed)
        self.assertEqual(len(mail.outbox), 0)

    def test_not_cancelled_yet(self):
        not_cancelled_yet = DeliverableFactory.create(
            auto_cancel_on=timezone.now() + relativedelta(days=2), status=NEW
        )
        cancel_abandoned_orders()
        not_cancelled_yet.refresh_from_db()
        self.assertEqual(not_cancelled_yet.status, NEW)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(Notification.objects.all().count(), 0)
        self.assertFalse(
            not_cancelled_yet.order.seller.artist_profile.commissions_closed
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_wrong_status(self):
        payment_pending = DeliverableFactory.create(
            auto_cancel_on=timezone.now(),
            status=PAYMENT_PENDING,
        )
        cancel_abandoned_orders()
        payment_pending.refresh_from_db()
        self.assertEqual(payment_pending.status, PAYMENT_PENDING)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(Notification.objects.all().count(), 0)
        self.assertFalse(payment_pending.order.seller.artist_profile.commissions_closed)
        self.assertEqual(len(mail.outbox), 0)


@patch("apps.sales.tasks.drip")
@override_settings(DRIP_ACCOUNT_ID="bork")
class DripTaskTestCase(EnsurePlansMixin, TestCase):
    def test_order_placed(self, mock_drip):
        mock_drip.post.assert_not_called()
        deliverable = DeliverableFactory.create(
            order__buyer__email="beep@example.com", order__buyer__username="Dude"
        )
        drip_placed_order(deliverable.order.id)
        mock_drip.post.assert_called_with(
            f"/v3/bork/shopper_activity/order",
            json={
                "provider": "artconomy",
                "email": "beep@example.com",
                "order_public_id": str(deliverable.order.id),
                "order_url": "https://artconomy.vulpinity.com/orders/Dude/order/"
                f"{deliverable.order.id}/deliverables/{deliverable.id}/",
                "action": "placed",
                "grand_total": float(deliverable.invoice.total().amount),
                "currency": "USD",
                "product": str(deliverable.product.id),
            },
        )
        self.assertEqual(mock_drip.post.call_count, 1)
