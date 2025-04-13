import json
import time
from csv import DictReader
from datetime import date
from decimal import Decimal
from io import StringIO
from unittest.mock import Mock, patch

import stripe as stripe_api
from apps.lib.models import (
    Notification,
    Subscription,
    ref_for_instance,
)
from apps.lib.constants import SALE_UPDATE, TIP_RECEIVED
from apps.lib.test_resources import APITestCase, EnsurePlansMixin
from apps.profiles.tests.factories import SubmissionFactory, UserFactory
from apps.sales.constants import (
    AUTHORIZE,
    BASE_PRICE,
    CARD,
    CARD_TRANSACTION_FEES,
    COMPLETED,
    ESCROW,
    FAILURE,
    IN_PROGRESS,
    NEW,
    OPEN,
    PAID,
    PAYMENT_PENDING,
    PENDING,
    QUEUED,
    REVIEW,
    STRIPE,
    SUBSCRIPTION,
    SUCCESS,
    TERM,
    TIP,
    TIPPING,
    CANCELLED,
    REFUNDED,
    FUND,
    THIRD_PARTY_FEE,
    BANK_TRANSFER_FEES,
    CASH_DEPOSIT,
    TOP_UP,
)
from apps.sales.models import CreditCardToken, TransactionRecord, WebhookEventRecord
from apps.sales.stripe import money_to_stripe
from apps.sales.tests.factories import (
    CreditCardTokenFactory,
    DeliverableFactory,
    InvoiceFactory,
    LineItemFactory,
    RevisionFactory,
    ServicePlanFactory,
    StripeAccountFactory,
    TransactionRecordFactory,
    WebhookRecordFactory,
    add_adjustment,
    PaypalConfigFactory,
)
from apps.sales.tests.test_utils import TransactionCheckMixin
from apps.sales.utils import UserPaymentException
from apps.sales.views.tests.fixtures.paypal_fixtures import (
    invoice_paid_event,
    invoice_cancelled_event,
    invoice_refunded_event,
    invoice_updated_event,
)
from apps.sales.views.tests.fixtures.stripe_fixtures import (
    base_account_updated_event,
    base_charge_succeeded_event,
    base_payment_method_attached_event,
    DUMMY_BALANCE_REPORT,
    base_report_event,
)
from apps.sales.views.webhooks import StripeWebhooks, handle_stripe_event
from dateutil.relativedelta import relativedelta
from django.core import mail
from django.db.models import Sum
from django.http import HttpRequest
from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone
from freezegun import freeze_time
from moneyed import Money
from rest_framework import status

DUMMY_WEBHOOK_PAYLOAD = """{
  "id": "evt_test_webhook",
  "object": "event"
}"""

DUMMY_WEBHOOK_SECRET = "whsec_test_secret"


def generate_header(**kwargs):
    # Yanked from https://raw.githubusercontent.com/stripe/stripe-python/master/tests/test_webhook.py
    timestamp = kwargs.get("timestamp", int(time.time()))
    payload = kwargs.get("payload", DUMMY_WEBHOOK_PAYLOAD)
    secret = kwargs.get("secret", DUMMY_WEBHOOK_SECRET)
    scheme = kwargs.get("scheme", stripe_api.WebhookSignature.EXPECTED_SCHEME)
    signature = kwargs.get("signature", None)
    if signature is None:
        payload_to_sign = "%d.%s" % (timestamp, payload)
        signature = stripe_api.WebhookSignature._compute_signature(
            payload_to_sign, secret
        )
    header = "t=%d,%s=%s" % (timestamp, scheme, signature)
    return header


class TestStripeWebhook(APITestCase):
    def setUp(self):
        super().setUp()
        self.webhook = WebhookRecordFactory.create()
        self.webhook_connect = WebhookRecordFactory.create(connect=True)
        self.factory = RequestFactory()
        self.view = StripeWebhooks.as_view()

    def gen_request(self, event):
        event = json.dumps(event)
        request = Mock(spec=HttpRequest)
        request.GET = {}
        request.body = event.encode()
        request.META = {
            "HTTP_STRIPE_SIGNATURE": generate_header(
                secret=self.webhook.secret, payload=event
            )
        }
        request.method = "post"
        return request

    @patch("apps.sales.views.webhooks.pull_report")
    def test_import_balance_transactions_and_fees(self, mock_pull):
        self.assertEqual(TransactionRecord.objects.count(), 0)
        mock_pull.return_value = DictReader(StringIO(DUMMY_BALANCE_REPORT))
        event = base_report_event()
        self.view(self.gen_request(event), False)
        self.assertEqual(TransactionRecord.objects.count(), 3)
        record = TransactionRecord.objects.get(remote_ids__contains="txn_beep")
        self.assertEqual(record.source, FUND)
        self.assertEqual(record.destination, CARD_TRANSACTION_FEES)
        self.assertIsNone(record.payer)
        self.assertIsNone(record.payee)
        self.assertEqual(record.category, THIRD_PARTY_FEE)
        self.assertEqual(record.amount, Money("0.08", "USD"))
        self.assertIn("Radar for Fraud Teams", record.remote_ids)
        record = TransactionRecord.objects.get(remote_ids__contains="txn_stuff")
        self.assertEqual(record.source, FUND)
        self.assertEqual(record.destination, BANK_TRANSFER_FEES)
        self.assertIsNone(record.payer)
        self.assertIsNone(record.payee)
        self.assertEqual(record.category, THIRD_PARTY_FEE)
        self.assertEqual(record.amount, Money("5.50", "USD"))
        record = TransactionRecord.objects.get(remote_ids__contains="txn_topup")
        self.assertEqual(record.source, CASH_DEPOSIT)
        self.assertEqual(record.destination, FUND)
        self.assertIsNone(record.payer)
        self.assertIsNone(record.payee)
        self.assertEqual(record.amount, Money('100.00', 'USD'))
        self.assertEqual(record.category, TOP_UP)
        self.assertEqual(record.status, SUCCESS)

    @patch("apps.sales.views.webhooks.mockable_dummy_event")
    def test_validates_event(self, mockable_dummy_event):
        event = base_charge_succeeded_event()
        event["type"] = "dummy_event"
        response = self.view(self.gen_request(event), False)
        mockable_dummy_event.assert_called()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @patch("apps.sales.views.webhooks.mockable_dummy_connect_event")
    def test_validates_connect_event(self, mockable_dummy_event):
        event = base_charge_succeeded_event()
        event["type"] = "dummy_connect_event"
        response = self.view(self.gen_request(event), True)
        mockable_dummy_event.assert_called()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_bad_signature(self):
        event = {}
        request = self.gen_request(event)
        original = request.META["HTTP_STRIPE_SIGNATURE"]
        timestamp = original.split(",")
        request.META["HTTP_STRIPE_SIGNATURE"] = f"{timestamp},v1=abcd34238"
        response = self.view(request, True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestHandleEvent(EnsurePlansMixin, TestCase):
    def test_empty_event_raises(self):
        with self.assertRaises(TypeError):
            handle_stripe_event(connect=False)

    @patch("apps.sales.views.webhooks.mockable_dummy_event")
    def test_handle_raw_body(self, mock_dummy_event):
        event = base_charge_succeeded_event()
        event["type"] = "dummy_event"
        handle_stripe_event(body=json.dumps(event), connect=False)
        mock_dummy_event.assert_called()

    @patch("apps.sales.views.webhooks.logger")
    def test_unknown_command(self, mock_logger):
        event = base_charge_succeeded_event()
        event["type"] = "foo"
        response = handle_stripe_event(event=event, connect=False)
        mock_logger.warning.assert_any_call(
            'Unsupported event "%s" received from Stripe. Connect is %s', "foo", False
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_idempotent_command(self):
        event = base_charge_succeeded_event()
        WebhookEventRecord.objects.create(event_id=event["id"], data={})
        response = handle_stripe_event(event=event, connect=False)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


@override_settings(
    STRIPE_CHARGE_PERCENTAGE=Decimal("2.90"),
    STRIPE_CHARGE_STATIC=Money("0.30", "USD"),
    STRIPE_CARD_PRESENT_PERCENTAGE=Decimal("2.70"),
    STRIPE_CARD_PRESENT_STATIC=Money("0.05", "USD"),
    STRIPE_INTERNATIONAL_PERCENTAGE_ADDITION=Decimal("1.5"),
)
class TestHandleChargeEvent(EnsurePlansMixin, TransactionCheckMixin, TestCase):
    def test_deliverable_paid(self):
        event = base_charge_succeeded_event()
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING,
            invoice__current_intent=event["data"]["object"]["payment_intent"],
            order__buyer__stripe_token="beep",
        )
        event["data"]["object"]["metadata"] = {"invoice_id": deliverable.invoice.id}
        event["data"]["object"]["customer"] = "beep"
        # Throw in a random target to a line item to cover one more branch
        deliverable.invoice.line_items.first().targets.add(
            ref_for_instance(SubmissionFactory.create())
        )
        handle_stripe_event(connect=False, event=event)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, QUEUED)
        fund_transaction = TransactionRecord.objects.get(
            source=CARD,
            destination=FUND,
            payer=deliverable.order.buyer,
            payee=deliverable.order.buyer,
            status=SUCCESS,
        )
        escrow_transaction = TransactionRecord.objects.get(
            source=FUND,
            destination=ESCROW,
            payer=deliverable.order.buyer,
            payee=deliverable.order.seller,
            status=SUCCESS,
        )
        fee = TransactionRecord.objects.get(
            source=FUND,
            destination=CARD_TRANSACTION_FEES,
        )
        self.assertEqual(fee.amount, Money("0.74", "USD"))
        for transaction in [fund_transaction, escrow_transaction, fee]:
            targets = list(transaction.targets.all())
            self.assertIn(ref_for_instance(deliverable), targets)
            self.assertIn(ref_for_instance(deliverable.invoice), targets)
            self.assertEqual(transaction.targets.count(), 2)

    def test_manual_invoice(self):
        event = base_charge_succeeded_event()
        line = LineItemFactory.create(
            type=BASE_PRICE,
            amount=Money("15.00", "USD"),
            invoice__bill_to__stripe_token="beep",
            invoice__manually_created=True,
        )
        invoice = line.invoice
        invoice.current_intent = event["data"]["object"]["payment_intent"]
        invoice.save()
        event["data"]["object"]["metadata"] = {"invoice_id": invoice.id}
        event["data"]["object"]["customer"] = "beep"
        handle_stripe_event(connect=False, event=event)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, PAID)
        total = TransactionRecord.objects.filter(source=CARD).aggregate(
            total=Sum("amount")
        )["total"]
        self.assertEqual(total, Decimal("15.00"))

    def test_deliverable_paid_card_present(self):
        event = base_charge_succeeded_event()
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING,
            invoice__current_intent=event["data"]["object"]["payment_intent"],
            order__buyer__stripe_token="beep",
        )
        event["data"]["object"]["metadata"] = {"invoice_id": deliverable.invoice.id}
        event["data"]["object"]["customer"] = "beep"
        event["data"]["object"]["payment_method_details"]["card_present"] = event[
            "data"
        ]["object"]["payment_method_details"]["card"]
        del event["data"]["object"]["payment_method_details"]["card"]
        handle_stripe_event(connect=False, event=event)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, QUEUED)
        fee = TransactionRecord.objects.get(
            source=FUND,
            destination=CARD_TRANSACTION_FEES,
        )
        self.assertEqual(fee.amount, Money("0.46", "USD"))

    def test_deliverable_payment_failed(self):
        event = base_charge_succeeded_event()
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING,
            invoice__current_intent=event["data"]["object"]["payment_intent"],
            order__buyer__stripe_token="beep",
        )
        event["data"]["object"]["metadata"] = {"invoice_id": deliverable.invoice.id}
        event["data"]["object"]["customer"] = "beep"
        event["type"] = "charge.failed"
        event["data"]["object"]["status"] = "failed"
        handle_stripe_event(connect=False, event=event)
        transaction = TransactionRecord.objects.get(
            source=CARD,
            destination=FUND,
            payer=deliverable.order.buyer,
            payee=deliverable.order.buyer,
            status=FAILURE,
        )
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, PAYMENT_PENDING)
        targets = list(transaction.targets.all())
        self.assertIn(ref_for_instance(deliverable), targets)
        self.assertIn(ref_for_instance(deliverable.invoice), targets)
        self.assertEqual(transaction.targets.count(), 2)

    def test_deliverable_paid_international_card(self):
        event = base_charge_succeeded_event()
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING,
            invoice__current_intent=event["data"]["object"]["payment_intent"],
            order__buyer__stripe_token="beep",
        )
        event["data"]["object"]["metadata"] = {"invoice_id": deliverable.invoice.id}
        event["data"]["object"]["customer"] = "beep"
        event["data"]["object"]["payment_method_details"]["card"]["country"] = "BR"
        handle_stripe_event(connect=False, event=event)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, QUEUED)
        fee = TransactionRecord.objects.get(
            source=FUND,
            destination=CARD_TRANSACTION_FEES,
        )
        self.assertEqual(fee.amount, Money("0.96", "USD"))

    def test_deliverable_wrong_amount_throws(self):
        event = base_charge_succeeded_event()
        event["data"]["object"]["amount"] = 100
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING,
            invoice__current_intent=event["data"]["object"]["payment_intent"],
            order__buyer__stripe_token="beep",
        )
        event["data"]["object"]["metadata"] = {"invoice_id": deliverable.invoice.id}
        event["data"]["object"]["customer"] = "beep"
        with self.assertRaises(UserPaymentException):
            handle_stripe_event(connect=False, event=event)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, PAYMENT_PENDING)
        self.assertEqual(CreditCardToken.objects.all().count(), 0)

    def test_deliverable_add_card_primary(self):
        event = base_charge_succeeded_event()
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING,
            invoice__current_intent=event["data"]["object"]["payment_intent"],
            order__buyer__stripe_token="beep",
        )
        CreditCardToken.objects.all().delete()
        event["data"]["object"]["metadata"] = {
            "deliverable_id": deliverable.id,
            "order_id": deliverable.order.id,
            "invoice_id": deliverable.invoice.id,
            "save_card": "True",
            "make_primary": "True",
        }
        event["data"]["object"]["payment_method"] = "weo8r7gfb348g"
        event["data"]["object"]["customer"] = "beep"
        handle_stripe_event(connect=False, event=event)
        cards = CreditCardToken.objects.all()
        self.assertEqual(cards.count(), 1)
        card = cards[0]
        self.assertEqual(card.stripe_token, "weo8r7gfb348g")
        self.assertEqual(card.user.primary_card, card)

    def test_deliverable_add_card_numbers_changed(self):
        event = base_charge_succeeded_event()
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING,
            invoice__current_intent=event["data"]["object"]["payment_intent"],
            order__buyer__stripe_token="beep",
        )
        CreditCardToken.objects.all().delete()
        CreditCardTokenFactory(
            user=deliverable.invoice.bill_to,
            last_four=9999,
            stripe_token="weo8r7gfb348g",
        )
        event["data"]["object"]["metadata"] = {
            "deliverable_id": deliverable.id,
            "order_id": deliverable.order.id,
            "invoice_id": deliverable.invoice.id,
            "save_card": "True",
            "make_primary": "True",
        }
        event["data"]["object"]["payment_method"] = "weo8r7gfb348g"
        event["data"]["object"]["payment_method_details"]["card"]["last4"] = "7483"
        event["data"]["object"]["customer"] = "beep"
        handle_stripe_event(connect=False, event=event)
        cards = CreditCardToken.objects.all()
        self.assertEqual(cards.count(), 1)
        card = cards[0]
        self.assertEqual(card.stripe_token, "weo8r7gfb348g")
        self.assertEqual(card.last_four, "7483")

    def test_pay_order_landscape(self):
        event = base_charge_succeeded_event()
        user = UserFactory.create()
        deliverable = DeliverableFactory.create(
            order__buyer=user,
            status=PAYMENT_PENDING,
            product__base_price=Money("10.00", "USD"),
            invoice__current_intent=event["data"]["object"]["payment_intent"],
            order__seller__service_plan=self.landscape,
            order__seller__service_plan_paid_through=(
                timezone.now() + relativedelta(days=5)
            ).date(),
        )
        add_adjustment(deliverable, Money("2.00", "USD"))
        subscription = Subscription.objects.get(
            subscriber=deliverable.order.seller, type=SALE_UPDATE
        )
        self.assertTrue(subscription.email)
        event["data"]["object"]["amount"] = money_to_stripe(Money("12.00", "USD"))[0]
        event["data"]["object"]["metadata"] = {"invoice_id": deliverable.invoice.id}
        event["data"]["object"]["customer"] = "beep"
        handle_stripe_event(connect=False, event=event)
        self.check_transactions(
            deliverable, user, remote_id=event["data"]["object"]["id"], landscape=True
        )

    @freeze_time("2020-08-02")
    def test_pay_order_weights_set(self):
        event = base_charge_succeeded_event()
        user = UserFactory.create()
        deliverable = DeliverableFactory.create(
            order__buyer=user,
            status=PAYMENT_PENDING,
            product__base_price=Money("10.00", "USD"),
            invoice__current_intent=event["data"]["object"]["payment_intent"],
            product__task_weight=1,
            product__expected_turnaround=1,
            adjustment_task_weight=3,
            adjustment_expected_turnaround=2,
        )
        add_adjustment(deliverable, Money("2.00", "USD"))
        subscription = Subscription.objects.get(
            subscriber=deliverable.order.seller, type=SALE_UPDATE
        )
        self.assertTrue(subscription.email)
        event["data"]["object"]["amount"] = money_to_stripe(Money("12.00", "USD"))[0]
        event["data"]["object"]["metadata"] = {"invoice_id": deliverable.invoice.id}
        event["data"]["object"]["customer"] = "beep"
        handle_stripe_event(connect=False, event=event)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.task_weight, 1)
        self.assertEqual(deliverable.expected_turnaround, 1)
        self.assertEqual(deliverable.adjustment_task_weight, 3)
        self.assertEqual(deliverable.adjustment_expected_turnaround, 2)
        self.assertEqual(
            deliverable.dispute_available_on, date(year=2020, month=8, day=6)
        )

    def test_pay_order_revisions_exist(self):
        event = base_charge_succeeded_event()
        user = UserFactory.create()
        deliverable = DeliverableFactory.create(
            order__buyer=user,
            status=PAYMENT_PENDING,
            product__base_price=Money("10.00", "USD"),
            invoice__current_intent=event["data"]["object"]["payment_intent"],
            revisions_hidden=True,
        )
        add_adjustment(deliverable, Money("2.00", "USD"))
        RevisionFactory.create(deliverable=deliverable)
        event["data"]["object"]["amount"] = money_to_stripe(Money("12.00", "USD"))[0]
        event["data"]["object"]["metadata"] = {"invoice_id": deliverable.invoice.id}
        event["data"]["object"]["customer"] = "beep"
        handle_stripe_event(connect=False, event=event)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, IN_PROGRESS)
        self.assertFalse(deliverable.revisions_hidden)
        self.assertFalse(deliverable.final_uploaded)

    @freeze_time("2018-08-01 12:00:00")
    def test_pay_order_final_uploaded(self):
        event = base_charge_succeeded_event()
        user = UserFactory.create()
        deliverable = DeliverableFactory.create(
            order__buyer=user,
            status=PAYMENT_PENDING,
            product__base_price=Money("10.00", "USD"),
            invoice__current_intent=event["data"]["object"]["payment_intent"],
            revisions_hidden=True,
            final_uploaded=True,
        )
        add_adjustment(deliverable, Money("2.00", "USD"))
        RevisionFactory.create(deliverable=deliverable)
        event["data"]["object"]["amount"] = money_to_stripe(Money("12.00", "USD"))[0]
        event["data"]["object"]["metadata"] = {"invoice_id": deliverable.invoice.id}
        event["data"]["object"]["customer"] = "beep"
        handle_stripe_event(connect=False, event=event)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, REVIEW)
        self.assertFalse(deliverable.revisions_hidden)
        self.assertTrue(deliverable.final_uploaded)
        self.assertEqual(deliverable.auto_finalize_on, date(2018, 8, 3))

    def test_pay_tip(self):
        event = base_charge_succeeded_event()
        user = UserFactory.create()
        deliverable = DeliverableFactory.create(
            order__buyer=user,
            status=COMPLETED,
        )
        self.assertEqual(Subscription.objects.filter(type=TIP_RECEIVED).count(), 1)
        line = LineItemFactory.create(
            invoice__type=TIPPING,
            amount=Money("10.00", "USD"),
            type=TIP,
            invoice__current_intent=event["data"]["object"]["payment_intent"],
            invoice__bill_to=user,
            invoice__issued_by=deliverable.order.seller,
        )
        line.targets.add(ref_for_instance(deliverable))
        event["data"]["object"]["amount"] = money_to_stripe(Money("10.00", "USD"))[0]
        event["data"]["object"]["metadata"] = {"invoice_id": line.invoice.id}
        event["data"]["object"]["customer"] = "beep"
        Notification.objects.all().delete()
        handle_stripe_event(connect=False, event=event)
        line.invoice.refresh_from_db()
        self.assertEqual(line.invoice.status, PAID)
        self.assertEqual(
            Notification.objects.filter(event__type=TIP_RECEIVED).count(), 1
        )

    def test_throws_on_mismatched_intent(self):
        event = base_charge_succeeded_event()
        user = UserFactory.create()
        deliverable = DeliverableFactory.create(
            order__buyer=user,
            status=PAYMENT_PENDING,
            product__base_price=Money("10.00", "USD"),
            invoice__current_intent="pi_beep",
            revisions_hidden=True,
            final_uploaded=True,
        )
        add_adjustment(deliverable, Money("2.00", "USD"))
        RevisionFactory.create(deliverable=deliverable)
        event["data"]["object"]["amount"] = money_to_stripe(Money("12.00", "USD"))[0]
        event["data"]["object"]["metadata"] = {"invoice_id": deliverable.invoice.id}
        event["data"]["object"]["customer"] = "beep"
        with self.assertRaises(UserPaymentException):
            handle_stripe_event(connect=False, event=event)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, PAYMENT_PENDING)

    def test_throws_on_mismatched_amount(self):
        event = base_charge_succeeded_event()
        user = UserFactory.create()
        deliverable = DeliverableFactory.create(
            order__buyer=user,
            status=PAYMENT_PENDING,
            product__base_price=Money("10.00", "USD"),
            invoice__current_intent=event["data"]["object"]["payment_intent"],
            revisions_hidden=True,
            final_uploaded=True,
        )
        add_adjustment(deliverable, Money("2.00", "USD"))
        RevisionFactory.create(deliverable=deliverable)
        event["data"]["object"]["amount"] = money_to_stripe(Money("24.00", "USD"))[0]
        event["data"]["object"]["metadata"] = {"invoice_id": deliverable.invoice.id}
        event["data"]["object"]["customer"] = "beep"
        with self.assertRaises(UserPaymentException):
            handle_stripe_event(connect=False, event=event)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, PAYMENT_PENDING)

    def test_ignores_mismatched_amount_on_failure(self):
        event = base_charge_succeeded_event()
        event["type"] = "charge.failed"
        user = UserFactory.create()
        deliverable = DeliverableFactory.create(
            order__buyer=user,
            status=PAYMENT_PENDING,
            product__base_price=Money("10.00", "USD"),
            invoice__current_intent="pi_beep",
            revisions_hidden=True,
            final_uploaded=True,
        )
        add_adjustment(deliverable, Money("2.00", "USD"))
        RevisionFactory.create(deliverable=deliverable)
        event["data"]["object"]["amount"] = money_to_stripe(Money("34.00", "USD"))[0]
        event["data"]["object"]["metadata"] = {"invoice_id": deliverable.invoice.id}
        event["data"]["object"]["customer"] = "beep"
        response = handle_stripe_event(connect=False, event=event)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, PAYMENT_PENDING)

    @patch("apps.sales.views.webhooks.logger")
    def test_logs_unknown_charge(self, mock_logger):
        event = base_charge_succeeded_event()
        event["data"]["object"]["amount"] = money_to_stripe(Money("12.00", "USD"))[0]
        event["data"]["object"]["metadata"] = {}
        event["data"]["object"]["customer"] = "beep"
        handle_stripe_event(connect=False, event=event)
        mock_logger.warning.assert_any_call("Charge for unknown item:")

    def test_service_extension_failed(self):
        event = base_charge_succeeded_event()
        event["type"] = "charge.failed"
        event["data"]["object"]["status"] = "failed"
        current_date = timezone.now().date()
        user = UserFactory.create(
            stripe_token="burp", service_plan_paid_through=current_date
        )
        self.assertEqual(user.service_plan_paid_through, current_date)
        CreditCardToken.objects.all().delete()
        invoice = InvoiceFactory(
            bill_to=user,
            current_intent=event["data"]["object"]["payment_intent"],
            type=TERM,
            status=OPEN,
        )
        line = LineItemFactory(invoice=invoice)
        service_plan = ServicePlanFactory()
        line.targets.add(ref_for_instance(service_plan))
        event["data"]["object"]["metadata"] = {
            "invoice_id": invoice.id,
        }
        event["data"]["object"]["customer"] = "burp"
        handle_stripe_event(connect=False, event=event)
        user.refresh_from_db()
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, OPEN)
        self.assertEqual(user.service_plan, self.free)
        self.assertEqual(user.service_plan_paid_through, current_date)
        self.assertEqual(TransactionRecord.objects.filter(status=FAILURE).count(), 1)
        self.assertEqual(TransactionRecord.objects.filter(status=SUCCESS).count(), 0)

    def test_service_extension(self):
        event = base_charge_succeeded_event()
        current_date = timezone.now().date()
        user = UserFactory.create(
            stripe_token="burp", service_plan_paid_through=current_date
        )
        self.assertEqual(user.service_plan_paid_through, current_date)
        CreditCardToken.objects.all().delete()
        invoice = InvoiceFactory(
            bill_to=user,
            current_intent=event["data"]["object"]["payment_intent"],
            type=TERM,
        )
        line = LineItemFactory(invoice=invoice)
        service_plan = ServicePlanFactory()
        line.targets.add(ref_for_instance(service_plan))
        event["data"]["object"]["metadata"] = {
            "invoice_id": invoice.id,
        }
        event["data"]["object"]["customer"] = "burp"
        handle_stripe_event(connect=False, event=event)
        user.refresh_from_db()
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, PAID)
        self.assertEqual(user.service_plan, service_plan)
        self.assertEqual(
            user.service_plan_paid_through, current_date + relativedelta(months=1)
        )
        # Term invoices don't set the target plan.
        self.assertEqual(user.next_service_plan, self.free)

    def test_service_subscription(self):
        event = base_charge_succeeded_event()
        current_date = timezone.now().date()
        user = UserFactory.create(
            stripe_token="burp", service_plan_paid_through=current_date
        )
        self.assertEqual(user.service_plan_paid_through, current_date)
        CreditCardToken.objects.all().delete()
        invoice = InvoiceFactory(
            bill_to=user,
            current_intent=event["data"]["object"]["payment_intent"],
            type=SUBSCRIPTION,
        )
        line = LineItemFactory(invoice=invoice)
        service_plan = ServicePlanFactory()
        line.targets.add(ref_for_instance(service_plan))
        event["data"]["object"]["metadata"] = {
            "invoice_id": invoice.id,
        }
        event["data"]["object"]["customer"] = "burp"
        handle_stripe_event(connect=False, event=event)
        user.refresh_from_db()
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, PAID)
        self.assertEqual(user.service_plan, service_plan)
        self.assertEqual(
            user.service_plan_paid_through, current_date + relativedelta(months=1)
        )
        self.assertEqual(user.next_service_plan, service_plan)


class TestPaymentAttached(EnsurePlansMixin, TestCase):
    def test_payment_attached_no_existing(self):
        event = base_payment_method_attached_event()
        event["data"]["object"]["customer"] = "cus_1234"
        event["data"]["object"]["card"]["last4"] = "1234"
        user = UserFactory.create(stripe_token="cus_1234")
        user.credit_cards.all().delete()
        response = handle_stripe_event(connect=False, event=event)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(user.credit_cards.all().count(), 1)
        user.refresh_from_db()
        card = user.credit_cards.get()
        self.assertEqual(card.last_four, "1234")
        self.assertEqual(user.primary_card, card)
        self.assertTrue(user.verified_adult)

    def test_payment_attached_has_existing_primary(self):
        event = base_payment_method_attached_event()
        old_card = CreditCardTokenFactory(
            user__stripe_token="cus_1234", last_four="1111"
        )
        user = old_card.user
        user.primary_card = old_card
        user.save()
        self.assertEqual(user.primary_card, old_card)
        event["data"]["object"]["customer"] = "cus_1234"
        event["data"]["object"]["card"]["last4"] = "1234"
        response = handle_stripe_event(connect=False, event=event)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(user.credit_cards.all().count(), 2)
        user.refresh_from_db()
        card = user.credit_cards.get(last_four="1234")
        self.assertNotEqual(user.primary_card, card)
        self.assertEqual(user.primary_card, old_card)

    def test_payment_type_unsupported(self):
        event = base_payment_method_attached_event()
        event["data"]["object"]["type"] = "gold"
        with self.assertRaises(NotImplementedError):
            handle_stripe_event(event=event, connect=False)


class TestChargeCreated(TestCase):
    @patch("apps.sales.views.webhooks.handle_charge_event")
    @patch("apps.sales.views.webhooks.stripe")
    def test_capture_authorized(self, mock_stripe, mock_handle_charge_event):
        event = base_charge_succeeded_event()
        event["data"]["object"]["payment_intent"] = "beep_beep"
        event["data"]["object"]["captured"] = False
        handle_stripe_event(connect=False, event=event)
        mock_stripe.__enter__.return_value.PaymentIntent.capture.assert_called_with(
            "beep_beep"
        )
        mock_handle_charge_event.assert_not_called()

    @patch("apps.sales.views.webhooks.handle_charge_event")
    @patch("apps.sales.views.webhooks.stripe")
    def test_already_captured(self, mock_stripe, mock_handle_charge_event):
        event = base_charge_succeeded_event()
        event["data"]["object"]["payment_intent"] = "beep_beep"
        event["data"]["object"]["captured"] = True
        handle_stripe_event(connect=False, event=event)
        mock_stripe.__enter__.return_value.PaymentIntent.capture.assert_not_called()
        mock_handle_charge_event.assert_called()


class TestChargeCaptured(TestCase):
    @patch("apps.sales.views.webhooks.handle_charge_event")
    @patch("apps.sales.views.webhooks.stripe")
    def test_redirect_to_handle_charge_event(
        self, mock_stripe, mock_handle_charge_event
    ):
        event = base_charge_succeeded_event()
        event["data"]["object"]["payment_intent"] = "beep_beep"
        event["data"]["object"]["captured"] = True
        handle_stripe_event(connect=False, event=event)
        mock_stripe.__enter__.return_value.PaymentIntent.capture.assert_not_called()
        mock_handle_charge_event.assert_called()


class TestTransferFailed(EnsurePlansMixin, TestCase):
    def test_transfer_failed(self):
        event = base_charge_succeeded_event()
        event["type"] = "transfer.failed"
        event["data"]["object"]["id"] = "beep"
        record = TransactionRecordFactory.create(remote_ids=["beep"], status=PENDING)
        self.assertEqual(len(mail.outbox), 0)
        response = handle_stripe_event(connect=False, event=event)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(mail.outbox), 1)
        record.refresh_from_db()
        self.assertEqual(record.status, FAILURE)


class TestAccountUpdated(EnsurePlansMixin, TestCase):
    @patch("apps.sales.views.webhooks.withdraw_all")
    def test_account_updated_can_transfer(self, mock_withdraw_all):
        event = base_account_updated_event()
        account = StripeAccountFactory(
            active=False, token=event["data"]["object"]["id"]
        )
        affected_deliverable = DeliverableFactory.create(
            order__seller=account.user, processor=AUTHORIZE, status=NEW
        )
        unaffected_deliverable = DeliverableFactory.create(
            order__seller=account.user,
            status=QUEUED,
            processor=AUTHORIZE,
        )
        unrelated_deliverable = DeliverableFactory.create(
            status=NEW, processor=AUTHORIZE
        )
        handle_stripe_event(connect=True, event=event)
        account.refresh_from_db()
        self.assertTrue(account.active)
        affected_deliverable.refresh_from_db()
        unaffected_deliverable.refresh_from_db()
        unrelated_deliverable.refresh_from_db()
        self.assertEqual(affected_deliverable.processor, STRIPE)
        self.assertEqual(unaffected_deliverable.processor, AUTHORIZE)
        self.assertEqual(unrelated_deliverable.processor, AUTHORIZE)
        mock_withdraw_all.delay.assert_called_with(account.user.id)

    @patch("apps.sales.views.webhooks.withdraw_all")
    def test_account_updated_no_transfer(self, mock_withdraw_all):
        event = base_account_updated_event()
        event["data"]["object"]["payouts_enabled"] = False
        account = StripeAccountFactory(
            active=False, token=event["data"]["object"]["id"]
        )
        affected_deliverable = DeliverableFactory.create(
            order__seller=account.user, processor=AUTHORIZE, status=NEW
        )
        handle_stripe_event(connect=True, event=event)
        account.refresh_from_db()
        self.assertFalse(account.active)
        affected_deliverable.refresh_from_db()
        self.assertEqual(affected_deliverable.processor, AUTHORIZE)
        mock_withdraw_all.delay.assert_not_called()


def prep_for_invoice(event, invoice):
    event["resource"]["invoice"]["id"] = invoice.paypal_token
    event["resource"]["invoice"]["number"] = invoice.id
    total = invoice.total()
    event["resource"]["invoice"]["amount"]["value"] = total.amount
    event["resource"]["invoice"]["amount"]["currency_code"] = str(total.currency)


@override_settings(BYPASS_PAYPAL_WEBHOOK_VALIDATION=True)
class TestPaypalWebhooks(APITestCase):
    def test_invoice_paid_fully(self):
        deliverable = DeliverableFactory.create(
            invoice__paypal_token="boop",
            status=PAYMENT_PENDING,
        )
        config = PaypalConfigFactory.create(user=deliverable.order.seller)
        paid_event = invoice_paid_event()
        prep_for_invoice(paid_event, deliverable.invoice)
        resp = self.client.post(
            f"/api/sales/paypal-webhooks/{config.id}/", paid_event, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, QUEUED)

    def test_invoice_paid_partially(self):
        deliverable = DeliverableFactory.create(
            invoice__paypal_token="boop",
            status=PAYMENT_PENDING,
        )
        config = PaypalConfigFactory.create(user=deliverable.order.seller)
        paid_event = invoice_paid_event()
        prep_for_invoice(paid_event, deliverable.invoice)
        paid_event["resource"]["invoice"]["due_amount"]["value"] = "5.00"
        paid_event["resource"]["invoice"]["due_amount"]["currency_code"] = "USD"
        resp = self.client.post(
            f"/api/sales/paypal-webhooks/{config.id}/", paid_event, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, PAYMENT_PENDING)

    def test_invoice_paid_with_gratuity(self):
        deliverable = DeliverableFactory.create(
            invoice__paypal_token="boop",
            status=NEW,
        )
        deliverable.status = PAYMENT_PENDING
        deliverable.save()
        config = PaypalConfigFactory.create(user=deliverable.order.seller)
        paid_event = invoice_paid_event()
        prep_for_invoice(paid_event, deliverable.invoice)
        original_total = deliverable.invoice.total()
        paid_event["resource"]["invoice"]["gratuity"] = {
            "value": "5.00",
            "currency_code": "USD",
        }
        resp = self.client.post(
            f"/api/sales/paypal-webhooks/{config.id}/", paid_event, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, QUEUED)
        self.assertEqual(
            deliverable.invoice.total(), original_total + Money("5.00", "USD")
        )
        self.assertEqual(
            deliverable.invoice.line_items.filter(type=TIP).get().amount,
            Money("5.00", "USD"),
        )

    def test_invoice_cancelled(self):
        deliverable = DeliverableFactory.create(
            invoice__paypal_token="boop",
            status=NEW,
        )
        deliverable.status = PAYMENT_PENDING
        deliverable.save()
        config = PaypalConfigFactory.create(user=deliverable.order.seller)
        cancelled_event = invoice_cancelled_event()
        prep_for_invoice(cancelled_event, deliverable.invoice)
        resp = self.client.post(
            f"/api/sales/paypal-webhooks/{config.id}/", cancelled_event, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, CANCELLED)

    def test_non_existent_invoice_cancel(self):
        config = PaypalConfigFactory.create()
        cancelled_event = invoice_cancelled_event()
        resp = self.client.post(
            f"/api/sales/paypal-webhooks/{config.id}/", cancelled_event, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_paypal_refunded_full_amount(self):
        deliverable = DeliverableFactory.create(
            invoice__paypal_token="Boop",
            escrow_enabled=False,
            status=NEW,
        )
        deliverable.status = COMPLETED
        deliverable.save()
        config = PaypalConfigFactory.create(user=deliverable.order.seller)
        refunded = invoice_refunded_event()
        prep_for_invoice(refunded, deliverable.invoice)
        resp = self.client.post(
            f"/api/sales/paypal-webhooks/{config.id}/", refunded, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, REFUNDED)

    def test_paypal_refunded_partial_does_nothing(self):
        deliverable = DeliverableFactory.create(
            invoice__paypal_token="Boop",
            escrow_enabled=False,
            status=NEW,
        )
        deliverable.status = COMPLETED
        deliverable.save()
        config = PaypalConfigFactory.create(user=deliverable.order.seller)
        refunded = invoice_refunded_event()
        prep_for_invoice(refunded, deliverable.invoice)
        amount_dict = refunded["resource"]["invoice"]["refunds"]["refund_amount"]
        amount_dict["value"] = "1"
        resp = self.client.post(
            f"/api/sales/paypal-webhooks/{config.id}/", refunded, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, COMPLETED)

    def test_paypal_refunded_throws_for_escrow(self):
        deliverable = DeliverableFactory.create(
            invoice__paypal_token="Boop",
            escrow_enabled=True,
            status=NEW,
        )
        deliverable.status = COMPLETED
        deliverable.save()
        config = PaypalConfigFactory.create(user=deliverable.order.seller)
        cancelled_event = invoice_refunded_event()
        prep_for_invoice(cancelled_event, deliverable.invoice)
        with self.assertRaises(RuntimeError):
            self.client.post(
                f"/api/sales/paypal-webhooks/{config.id}/",
                cancelled_event,
                format="json",
            )

    def test_unsupported_event(self):
        unsupported_event = invoice_refunded_event()
        config = PaypalConfigFactory.create()
        unsupported_event["event_type"] = "PANIC"
        resp = self.client.post(
            f"/api/sales/paypal-webhooks/{config.id}/", unsupported_event, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["detail"], "Event type not supported.")

    def test_invoice_updated(self):
        deliverable = DeliverableFactory.create(invoice__paypal_token="Beep")
        updated_event = invoice_updated_event()
        updated_event["resource"]["invoice"]["id"] = deliverable.invoice.paypal_token
        updated_event["resource"]["invoice"]["number"] = deliverable.invoice.id
        config = PaypalConfigFactory.create(user=deliverable.order.seller)
        resp = self.client.post(
            f"/api/sales/paypal-webhooks/{config.id}/", updated_event, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        deliverable.invoice.refresh_from_db()
        self.assertEqual(deliverable.invoice.total(), Money("108.00", "USD"))
