import json
import time
from datetime import date
from decimal import Decimal
from unittest.mock import patch, Mock

from dateutil.relativedelta import relativedelta
from django.http import HttpRequest
from django.test import RequestFactory, override_settings
from django.utils import timezone
from freezegun import freeze_time
from moneyed import Money
from rest_framework import status
import stripe as stripe_api

from apps.lib.models import ref_for_instance, Subscription, SALE_UPDATE
from apps.lib.test_resources import APITestCase
from apps.profiles.tests.factories import UserFactory
from apps.sales.apis import STRIPE
from apps.sales.models import PAYMENT_PENDING, QUEUED, CreditCardToken, TransactionRecord, REVIEW, IN_PROGRESS, \
    ServicePlan, OPEN
from apps.sales.stripe import money_to_stripe
from apps.sales.tests.factories import DeliverableFactory, CreditCardTokenFactory, WebhookRecordFactory, InvoiceFactory, \
    LineItemFactory, ServicePlanFactory, add_adjustment, RevisionFactory
from apps.sales.tests.test_utils import TransactionCheckMixin
from apps.sales.utils import UserPaymentException
from apps.sales.views import StripeWebhooks


class TestInvoicePaymentIntent(APITestCase):
    def setUp(self) -> None:
        self.patcher = patch('apps.sales.views.create_or_update_stripe_user')
        self.patcher.start()

    def tearDown(self) -> None:
        self.patcher.stop()

    @patch('apps.sales.views.stripe')
    def test_create_payment_intent(self, mock_stripe):
        mock_api = Mock()
        mock_stripe.__enter__.return_value = mock_api
        mock_api.PaymentIntent.create.return_value = {'id': 'raw_id', 'client_secret': 'sneak'}
        deliverable = DeliverableFactory.create(status=PAYMENT_PENDING, invoice__status=OPEN)
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f'/api/sales/v1/invoices/{deliverable.invoice.id}/payment-intent/',
        )
        self.assertEqual(response.data, {'secret': 'sneak'})
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.invoice.current_intent, 'raw_id')
        params = mock_api.PaymentIntent.create.call_args_list[0][1]
        self.assertEqual(params['amount'], deliverable.invoice.total().amount * 100)
        self.assertEqual(params['currency'], 'usd')
        self.assertIsNone(params['payment_method'])
        self.assertEqual(params['metadata'], {
            'invoice_id': deliverable.invoice.id,
            'make_primary': False,
            'save_card': False,
        })
        self.assertEqual(params['payment_method_types'], ['card'])
        self.assertEqual(params['transfer_group'], f'ACInvoice#{deliverable.invoice.id}')
        mock_api.PaymentIntent.modify.assert_not_called()

    @patch('apps.sales.views.stripe')
    def test_modify_payment_intent(self, mock_stripe):
        mock_api = Mock()
        mock_stripe.__enter__.return_value = mock_api
        mock_api.PaymentIntent.modify.return_value = {'id': 'raw_id', 'client_secret': 'sneak'}
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, invoice__current_intent='old_id', processor=STRIPE,
            invoice__status=OPEN,
        )
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f'/api/sales/v1/invoices/{deliverable.invoice.id}/payment-intent/',
        )
        self.assertEqual(response.data, {'secret': 'sneak'})
        deliverable.refresh_from_db()
        # Should not have changed.
        self.assertEqual(deliverable.invoice.current_intent, 'old_id')
        mock_api.PaymentIntent.create.assert_not_called()
        self.assertEqual(mock_api.PaymentIntent.modify.call_args_list[0][0][0], 'old_id')
        params = mock_api.PaymentIntent.modify.call_args_list[0][1]
        self.assertEqual(params['amount'], deliverable.invoice.total().amount * 100)
        self.assertEqual(params['currency'], 'usd')
        self.assertEqual(
            params['metadata'],
            {
                'invoice_id': deliverable.invoice.id,
                'make_primary': False,
                'save_card': False
            }
        )
        self.assertEqual(params['payment_method_types'], ['card'])
        self.assertEqual(params['transfer_group'], f'ACInvoice#{deliverable.invoice.id}')

    @patch('apps.sales.views.stripe')
    def test_use_specific_card(self, mock_stripe):
        mock_api = Mock()
        mock_stripe.__enter__.return_value = mock_api
        mock_api.PaymentIntent.create.return_value = {'id': 'raw_id', 'client_secret': 'sneak'}
        deliverable = DeliverableFactory.create(status=PAYMENT_PENDING, processor=STRIPE, invoice__status=OPEN)
        card = CreditCardTokenFactory(user=deliverable.order.buyer, stripe_token='butts', token='')
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f'/api/sales/v1/invoices/{deliverable.invoice.id}/payment-intent/',
            {'card_id': card.id}
        )
        self.assertEqual(response.data, {'secret': 'sneak'})
        deliverable.refresh_from_db()
        params = mock_api.PaymentIntent.create.call_args_list[0][1]
        self.assertEqual(params['payment_method'], 'butts')

    @patch('apps.sales.views.stripe')
    def test_fail_wrong_card_user(self, mock_stripe):
        mock_api = Mock()
        mock_stripe.__enter__.return_value = mock_api
        mock_api.PaymentIntent.create.return_value = {'id': 'raw_id', 'client_secret': 'sneak'}
        deliverable = DeliverableFactory.create(status=PAYMENT_PENDING, processor=STRIPE, invoice__status=OPEN)
        card = CreditCardTokenFactory(stripe_token='butts', token='')
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f'/api/sales/v1/invoices/{deliverable.invoice.id}/payment-intent/',
            {'card_id': card.id}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('apps.sales.views.stripe')
    def test_use_default_card(self, mock_stripe):
        mock_api = Mock()
        mock_stripe.__enter__.return_value = mock_api
        mock_api.PaymentIntent.create.return_value = {'id': 'raw_id', 'client_secret': 'sneak'}
        deliverable = DeliverableFactory.create(status=PAYMENT_PENDING, processor=STRIPE, invoice__status=OPEN)
        card = CreditCardTokenFactory(stripe_token='butts', token='', user=deliverable.order.buyer)
        deliverable.order.buyer.primary_card = card
        deliverable.order.buyer.save()
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f'/api/sales/v1/invoices/{deliverable.invoice.id}/payment-intent/',
        )
        self.assertEqual(response.data, {'secret': 'sneak'})
        deliverable.refresh_from_db()
        params = mock_api.PaymentIntent.create.call_args_list[0][1]
        self.assertEqual(params['payment_method'], 'butts')


def base_charge_succeeded_event():
    return {
        "id": "evt_1Icyh5AhlvPza3BKV9A13pSj",
        "object": "event",
        "api_version": "2019-12-03",
        "created": 1617653203,
        "data": {
            "object": {
                "id": "ch_1Icyh4AhlvPza3BK7ZkPN95S",
                "object": "charge",
                "amount": 1500,
                "amount_captured": 1500,
                "amount_refunded": 0,
                "application": None,
                "application_fee": None,
                "application_fee_amount": None,
                "balance_transaction": "txn_1Icyh5AhlvPza3BKKv8oUs3e",
                "billing_details": {
                    "address": {
                        "city": None,
                        "country": None,
                        "line1": None,
                        "line2": None,
                        "postal_code": None,
                        "state": None
                    },
                    "email": None,
                    "name": None,
                    "phone": None
                },
                "calculated_statement_descriptor": "ARTCONOMY.COM",
                "captured": True,
                "created": 1617653202,
                "currency": "usd",
                "customer": None,
                "description": "(created by Stripe CLI)",
                "destination": None,
                "dispute": None,
                "disputed": False,
                "failure_code": None,
                "failure_message": None,
                "fraud_details": {},
                "invoice": None,
                "livemode": False,
                "metadata": {},
                "on_behalf_of": None,
                "order": None,
                "outcome": {
                    "network_status": "approved_by_network",
                    "reason": None,
                    "risk_level": "normal",
                    "risk_score": 51,
                    "seller_message": "Payment complete.",
                    "type": "authorized"
                },
                "paid": True,
                "payment_intent": 'pi_asrdfo8uyv7234',
                "payment_method": "card_1Icyh4AhlvPza3BKKfHLWtEW",
                "payment_method_details": {
                    "card": {
                        "brand": "visa",
                        "checks": {
                            "address_line1_check": None,
                            "address_postal_code_check": None,
                            "cvc_check": None
                        },
                        "country": "US",
                        "exp_month": 4,
                        "exp_year": 2022,
                        "fingerprint": "UpCjmErZWs5fGhh7",
                        "funding": "credit",
                        "installments": None,
                        "last4": "4242",
                        "network": "visa",
                        "three_d_secure": None,
                        "wallet": None
                    },
                    "type": "card"
                },
                "receipt_email": None,
                "receipt_number": None,
                "receipt_url": "https://pay.stripe.com/receipts/acct_1Fu0KSAhlvPza3BK/ch_1Icyh4AhlvPza3BK7ZkPN95S/rcpt_JFTe7703FypdF9BO3C6kfZcrouVJ2Wm",
                "refunded": False,
                "refunds": {
                    "object": "list",
                    "data": [],
                    "has_more": False,
                    "total_count": 0,
                    "url": "/v1/charges/ch_1Icyh4AhlvPza3BK7ZkPN95S/refunds"
                },
                "review": None,
                "shipping": None,
                "source": {
                    "id": "card_1Icyh4AhlvPza3BKKfHLWtEW",
                    "object": "card",
                    "address_city": None,
                    "address_country": None,
                    "address_line1": None,
                    "address_line1_check": None,
                    "address_line2": None,
                    "address_state": None,
                    "address_zip": None,
                    "address_zip_check": None,
                    "brand": "Visa",
                    "country": "US",
                    "customer": None,
                    "cvc_check": None,
                    "dynamic_last4": None,
                    "exp_month": 4,
                    "exp_year": 2022,
                    "fingerprint": "UpCjmErZWs5fGhh7",
                    "funding": "credit",
                    "last4": "4242",
                    "metadata": {},
                    "name": None,
                    "tokenization_method": None
                },
                "source_transfer": None,
                "statement_descriptor": None,
                "statement_descriptor_suffix": None,
                "status": "succeeded",
                "transfer_data": None,
                "transfer_group": None
            }
        },
        "livemode": False,
        "pending_webhooks": 1,
        "request": {
            "id": "req_jcqQXmSfMGTwR2",
            "idempotency_key": None
        },
        "type": "charge.succeeded"
    }


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


@override_settings(
    SERVICE_STATIC_FEE=Decimal('0.50'), SERVICE_PERCENTAGE_FEE=Decimal('4'),
    PREMIUM_STATIC_BONUS=Decimal('0.25'), PREMIUM_PERCENTAGE_BONUS=Decimal('4'),
)
class TestStripeWebhook(TransactionCheckMixin, APITestCase):
    def setUp(self):
        super(TestStripeWebhook, self).setUp()
        self.webhook = WebhookRecordFactory.create()
        self.factory = RequestFactory()
        self.view = StripeWebhooks.as_view()
        self.landscape = ServicePlanFactory(name='Landscape')

    def gen_request(self, event):
        event = json.dumps(event)
        request = Mock(spec=HttpRequest)
        request.GET = {}
        request.body = event.encode()
        request.META = {'HTTP_STRIPE_SIGNATURE': generate_header(secret=self.webhook.secret, payload=event)}
        request.method = 'post'
        return request

    def test_deliverable_paid(self):
        event = base_charge_succeeded_event()
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, invoice__current_intent=event['data']['object']['payment_intent'],
            order__buyer__stripe_token='beep',
        )
        event = base_charge_succeeded_event()
        event['data']['object']['metadata'] = {'invoice_id': deliverable.invoice.id}
        event['data']['object']['customer'] = 'beep'
        request = self.gen_request(event)
        response = self.view(request, False)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, QUEUED)
        transaction = TransactionRecord.objects.get(
            source=TransactionRecord.CARD, destination=TransactionRecord.ESCROW, payer=deliverable.order.buyer,
            payee=deliverable.order.seller,
        )
        targets = list(transaction.targets.all())
        self.assertIn(ref_for_instance(deliverable), targets)
        self.assertIn(ref_for_instance(deliverable.invoice), targets)
        self.assertEqual(transaction.targets.count(), 2)

    def test_deliverable_wrong_amount_throws(self):
        event = base_charge_succeeded_event()
        event['data']['object']['amount'] = 100
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, invoice__current_intent=event['data']['object']['payment_intent'],
            order__buyer__stripe_token='beep',
        )
        event['data']['object']['metadata'] = {'invoice_id': deliverable.invoice.id}
        event['data']['object']['customer'] = 'beep'
        self.assertRaises(
            UserPaymentException,
            self.view,
            self.gen_request(event),
            False,
        )
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, PAYMENT_PENDING)
        self.assertEqual(CreditCardToken.objects.all().count(), 0)

    def test_deliverable_add_card_primary(self):
        event = base_charge_succeeded_event()
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, invoice__current_intent=event['data']['object']['payment_intent'],
            order__buyer__stripe_token='beep',
        )
        CreditCardToken.objects.all().delete()
        event['data']['object']['metadata'] = {
            'deliverable_id': deliverable.id,
            'order_id': deliverable.order.id,
            'invoice_id': deliverable.invoice.id,
            'save_card': 'True',
            'make_primary': 'True',
        }
        event['data']['object']['payment_method'] = 'weo8r7gfb348g'
        event['data']['object']['customer'] = 'beep'
        response = self.view(self.gen_request(event), False)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cards = CreditCardToken.objects.all()
        self.assertEqual(cards.count(), 1)
        card = cards[0]
        self.assertEqual(card.stripe_token, 'weo8r7gfb348g')
        self.assertEqual(card.user.primary_card, card)

    def test_service_extension(self):
        event = base_charge_succeeded_event()
        user = UserFactory.create(stripe_token='burp')
        self.assertIsNone(user.service_plan)
        CreditCardToken.objects.all().delete()
        invoice = InvoiceFactory(bill_to=user, current_intent=event['data']['object']['payment_intent'])
        line = LineItemFactory(invoice=invoice)
        service_plan = ServicePlanFactory()
        line.targets.add(ref_for_instance(service_plan))
        event['data']['object']['metadata'] = {
            'invoice_id': invoice.id,
        }
        event['data']['object']['customer'] = 'burp'
        response = self.view(self.gen_request(event), False)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertEqual(user.service_plan, service_plan)

    # These tests have been migrated over from the code that checked authorize transactions.
    # Eventually, they need to be made independent of the code checking stripe transactions and only
    # check whether proper post-payment events happen, independent of what processor did them.
    # That will likely require some refactoring, so for now, they go here.
    def test_pay_order_landscape(self):
        event = base_charge_succeeded_event()
        user = UserFactory.create()
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            invoice__current_intent=event['data']['object']['payment_intent'],
            order__seller__service_plan=self.landscape,
            order__seller__service_plan_paid_through=(timezone.now() + relativedelta(days=5)).date(),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        subscription = Subscription.objects.get(subscriber=deliverable.order.seller, type=SALE_UPDATE)
        self.assertTrue(subscription.email)
        event['data']['object']['amount'] = money_to_stripe(Money('12.00', 'USD'))[0]
        event['data']['object']['metadata'] = {'invoice_id': deliverable.invoice.id}
        event['data']['object']['customer'] = 'beep'
        response = self.view(self.gen_request(event), False)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.check_transactions(deliverable, user, remote_id=event['data']['object']['id'], landscape=True)

    @freeze_time('2020-08-02')
    def test_pay_order_weights_set(self):
        event = base_charge_succeeded_event()
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            invoice__current_intent=event['data']['object']['payment_intent'],
            product__task_weight=1, product__expected_turnaround=1,
            adjustment_task_weight=3, adjustment_expected_turnaround=2
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        subscription = Subscription.objects.get(subscriber=deliverable.order.seller, type=SALE_UPDATE)
        self.assertTrue(subscription.email)
        event['data']['object']['amount'] = money_to_stripe(Money('12.00', 'USD'))[0]
        event['data']['object']['metadata'] = {'invoice_id': deliverable.invoice.id}
        event['data']['object']['customer'] = 'beep'
        response = self.view(self.gen_request(event), False)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.task_weight, 1)
        self.assertEqual(deliverable.expected_turnaround, 1)
        self.assertEqual(deliverable.adjustment_task_weight, 3)
        self.assertEqual(deliverable.adjustment_expected_turnaround, 2)
        self.assertEqual(deliverable.dispute_available_on, date(year=2020, month=8, day=6))

    def test_pay_order_revisions_exist(self):
        event = base_charge_succeeded_event()
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            invoice__current_intent=event['data']['object']['payment_intent'],
            revisions_hidden=True,
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        RevisionFactory.create(deliverable=deliverable)
        event['data']['object']['amount'] = money_to_stripe(Money('12.00', 'USD'))[0]
        event['data']['object']['metadata'] = {'invoice_id': deliverable.invoice.id}
        event['data']['object']['customer'] = 'beep'
        self.view(self.gen_request(event), False)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, IN_PROGRESS)
        self.assertFalse(deliverable.revisions_hidden)
        self.assertFalse(deliverable.final_uploaded)

    @freeze_time('2018-08-01 12:00:00')
    def test_pay_order_final_uploaded(self):
        event = base_charge_succeeded_event()
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            invoice__current_intent=event['data']['object']['payment_intent'],
            revisions_hidden=True, final_uploaded=True,
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        RevisionFactory.create(deliverable=deliverable)
        event['data']['object']['amount'] = money_to_stripe(Money('12.00', 'USD'))[0]
        event['data']['object']['metadata'] = {'invoice_id': deliverable.invoice.id}
        event['data']['object']['customer'] = 'beep'
        self.view(self.gen_request(event), False)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, REVIEW)
        self.assertFalse(deliverable.revisions_hidden)
        self.assertTrue(deliverable.final_uploaded)
        self.assertEqual(deliverable.auto_finalize_on, date(2018, 8, 3))

    ### End ported tests that need to be redone.
