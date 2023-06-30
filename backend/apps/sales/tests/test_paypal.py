from decimal import Decimal
from datetime import datetime
from unittest import TestCase as UnitTest
from unittest.mock import MagicMock, patch, call

from authlib.integrations.base_client import MissingTokenError
from ddt import ddt, data, unpack
from django.test import TestCase, override_settings
from freezegun import freeze_time
from moneyed import Money

from apps.lib.test_resources import EnsurePlansMixin
from apps.profiles.tests.factories import UserFactory
from apps.sales.constants import (
    BASE_PRICE,
    ADD_ON,
    DELIVERABLE_TRACKING,
    RECONCILIATION,
    TAX,
)
from apps.sales.models import PaypalConfig, LineItem
from apps.sales.paypal import (
    PayPal,
    paypal_api,
    get_paypal_recipients,
    paypal_date,
    serialize_line_item,
    delete_webhooks,
    paypal_items,
    clear_existing_invoice,
    paypal_invoice_url,
    transferable_lines,
    reconcile_invoices,
    generate_paypal_invoice,
    validate_paypal_request,
    SignatureValidationError,
)
from apps.sales.tests.factories import (
    PaypalConfigFactory,
    InvoiceFactory,
    DeliverableFactory,
    LineItemFactory,
)
from apps.sales.views.tests.fixtures.paypal_fixtures import (
    invoice_paid_event,
    invoice_updated_event,
)


@ddt
class TestPayPalClass(UnitTest):
    @data(
        (True, "https://api-m.sandbox.paypal.com/"),
        (False, "https://api-m.paypal.com/"),
    )
    @unpack
    def test_instantiation(self, setting, result):
        with override_settings(CARD_TEST=setting):
            paypal = PayPal(key="Dude", secret="wat", template_id="sweet")
            self.assertEqual(paypal.base_url, result)
            self.assertEqual(paypal.template_id, "sweet")
            self.assertTrue(paypal.client)

    @data(
        ("get", True, False),
        ("get", False, False),
        ("post", True, True),
        ("post", False, True),
        ("patch", True, True),
        ("patch", False, True),
        ("put", False, True),
        ("put", True, True),
        ("delete", True, False),
        ("delete", False, False),
    )
    @unpack
    def test_methods(self, method, raise_error, auto_json):
        paypal = PayPal(key="beep", secret="boop", template_id="wat")
        paypal.client = MagicMock()
        response = MagicMock()
        verb = getattr(paypal.client, method)
        verb.return_value = response
        getattr(paypal, method)(
            "test/thing/",
            {"Beep": "Boop"},
            "test",
            thing="Wat",
            raise_error=raise_error,
        )
        if auto_json:
            verb.assert_called_with(
                "https://api-m.sandbox.paypal.com/test/thing/",
                "test",
                json={"Beep": "Boop"},
                thing="Wat",
            )
        else:
            verb.assert_called_with(
                "https://api-m.sandbox.paypal.com/test/thing/",
                {"Beep": "Boop"},
                "test",
                thing="Wat",
            )
        if raise_error:
            response.raise_for_status.assert_called()
        else:
            response.raise_for_status.assert_not_called()

    def test_context_management(self):
        paypal = PayPal(key="beep", secret="boop", template_id="wat")
        paypal.client = MagicMock()
        with paypal as context_manager:
            self.assertEqual(paypal, context_manager)
        paypal.client.fetch_token.assert_called_with(
            "https://api-m.sandbox.paypal.com/v1/oauth2/token"
        )

    def test_context_management_ignores_failed_token(self):
        paypal = PayPal(key="beep", secret="boop", template_id="wat")
        paypal.client = MagicMock()
        paypal.client.fetch_token.side_effect = MissingTokenError(
            "That's my purse! I don't know you!"
        )
        with paypal as context_manager:
            self.assertEqual(paypal, context_manager)
        paypal.client.fetch_token.assert_called_with(
            "https://api-m.sandbox.paypal.com/v1/oauth2/token"
        )


class TestPaypalApi(EnsurePlansMixin, TestCase):
    def test_user_without_config(self):
        user = UserFactory.create()
        with self.assertRaises(PaypalConfig.DoesNotExist) as exc:
            paypal_api(user)
        self.assertEqual(
            str(exc.exception), "This user has not set up their PayPal credentials."
        )

    def test_user_with_inactive_config(self):
        config = PaypalConfigFactory.create(template_id="", active=False)
        with self.assertRaises(PaypalConfig.DoesNotExist) as exc:
            paypal_api(config.user)
        self.assertEqual(
            str(exc.exception), "This user has not set up their PayPal credentials."
        )

    @patch("apps.sales.paypal.PayPal", autospec=True)
    def test_use_config(self, mock_paypal):
        config = PaypalConfigFactory.create()
        paypal_api(config=config)
        mock_paypal.assert_called_with(
            key=config.key, secret=config.secret, template_id=config.template_id
        )

    @patch("apps.sales.paypal.PayPal", autospec=True)
    def test_user_with_active_config(self, mock_paypal):
        config = PaypalConfigFactory.create()
        paypal_api(config.user)
        mock_paypal.assert_called_with(
            key=config.key, secret=config.secret, template_id=config.template_id
        )

    def test_empty_parameters(self):
        with self.assertRaises(TypeError) as exc:
            paypal_api()
        self.assertEqual(str(exc.exception), "Neither user nor config specified.")


@ddt
class TestGetPaypalRecipients(EnsurePlansMixin, TestCase):
    def test_bill_guest(self):
        invoice = InvoiceFactory.create(
            bill_to__guest=True, bill_to__guest_email="test@boop.com"
        )
        self.assertEqual(
            get_paypal_recipients(invoice),
            [{"billing_info": {"email_address": "test@boop.com"}}],
        )

    def test_bill_none(self):
        invoice = InvoiceFactory.create(bill_to=None)
        self.assertEqual(
            get_paypal_recipients(invoice),
            [],
        )

    def test_bill_registered(self):
        invoice = InvoiceFactory.create()
        self.assertEqual(
            get_paypal_recipients(invoice),
            [{"billing_info": {"email_address": invoice.bill_to.email}}],
        )


@ddt
class TestPaypalDate(UnitTest):
    @data(
        (datetime(year=2023, month=1, day=5), "2023-01-05"),
        (datetime(year=2023, month=11, day=20), "2023-11-20"),
        (datetime(year=2023, month=1, day=20), "2023-01-20"),
        (datetime(year=2023, month=11, day=2), "2023-11-02"),
    )
    @unpack
    def test_date_format(self, test, result):
        self.assertEqual(paypal_date(test), result)


class TestSerializeLineItem(EnsurePlansMixin, TestCase):
    def test_base_line_item(self):
        deliverable = DeliverableFactory.create(
            product__name="Boop sketch",
            product__base_price=Money("15.00", "USD"),
        )
        self.assertEqual(
            serialize_line_item(
                deliverable.invoice.line_items.get(type=BASE_PRICE),
                deliverable.invoice.total(),
                deliverable,
            ),
            {
                "name": f"Order #{deliverable.order.id} "
                f"[{deliverable.name}] - Boop sketch",
                "quantity": 1,
                "unit_amount": {"currency_code": "USD", "value": "15.00"},
                "unit_of_measure": "AMOUNT",
            },
        )

    def test_add_on(self):
        deliverable = DeliverableFactory.create(
            product__name="Boop sketch",
        )
        line = LineItemFactory.create(
            invoice=deliverable.invoice, amount=Money("5.00", "USD"), type=ADD_ON
        )
        self.assertEqual(
            serialize_line_item(
                line,
                Money("5.00", "USD"),
                deliverable,
            ),
            {
                "name": "Additional requirements",
                "quantity": 1,
                "unit_amount": {"currency_code": "USD", "value": "5.00"},
                "unit_of_measure": "AMOUNT",
            },
        )

    def test_discount(self):
        deliverable = DeliverableFactory.create()
        line = LineItemFactory.create(invoice=deliverable.invoice, type=ADD_ON)
        self.assertEqual(
            serialize_line_item(
                line,
                Money("-5.00", "USD"),
                deliverable,
            ),
            {
                "name": "Discount",
                "quantity": 1,
                "unit_amount": {"currency_code": "USD", "value": "-5.00"},
                "unit_of_measure": "AMOUNT",
            },
        )

    def test_has_description(self):
        deliverable = DeliverableFactory.create()
        line = LineItemFactory.create(
            invoice=deliverable.invoice, type=ADD_ON, description="Extra Character"
        )
        self.assertEqual(
            serialize_line_item(
                line,
                Money("5.00", "USD"),
                deliverable,
            ),
            {
                "name": "Extra Character",
                "quantity": 1,
                "unit_amount": {"currency_code": "USD", "value": "5.00"},
                "unit_of_measure": "AMOUNT",
            },
        )


@patch("apps.sales.paypal.PayPal")
class TestDeleteWebhooks(EnsurePlansMixin, TestCase):
    def test_delete_webhooks(self, mock_paypal):
        config = PaypalConfigFactory(webhook_id="Bork")
        delete_webhooks(config)
        delete = mock_paypal.return_value.__enter__.return_value.delete
        delete.assert_called_with(
            "v1/notifications/webhooks/Bork",
            raise_error=False,
        )
        delete.return_value.raise_for_status.assert_called()

    def test_ignores_404(self, mock_paypal):
        config = PaypalConfigFactory(webhook_id="Bork")
        delete = mock_paypal.return_value.__enter__.return_value.delete
        delete.return_value.status_code = 404
        delete_webhooks(config)
        delete.assert_called_with(
            "v1/notifications/webhooks/Bork",
            raise_error=False,
        )
        delete.return_value.raise_for_status.assert_not_called()

    def test_bails_if_no_webhook(self, mock_paypal):
        config = PaypalConfigFactory(webhook_id="")
        delete = mock_paypal.return_value.__enter__.return_value.delete
        delete_webhooks(config)
        delete.assert_not_called()


class TestPaypalItems(EnsurePlansMixin, TestCase):
    def test_line_handling(self):
        deliverable = DeliverableFactory.create(
            product__base_price=Money("10.00", "USD"),
            escrow_enabled=False,
        )
        LineItemFactory.create(
            invoice=deliverable.invoice, type=ADD_ON, amount=Money("5.00", "USD")
        )
        LineItemFactory.create(
            invoice=deliverable.invoice, type=ADD_ON, amount=Money("-1.00", "USD")
        )
        resulting_lines = paypal_items(
            deliverable,
            deliverable.invoice.line_items.all(),
            [
                # This line item is invalid, but should be added unchanged.
                {
                    "name": "Tax",
                    "quantity": 1,
                    "unit_amount": {"currency_code": "USD", "value": "6.00"},
                    "beep": "boop",
                    "unit_of_measure": "PERCENTAGE",
                },
            ],
        )

        self.assertCountEqual(
            resulting_lines,
            [
                {
                    "name": f"Order #{deliverable.order.id} [{deliverable.name}] - "
                    f"{deliverable.product.name}",
                    "quantity": 1,
                    "unit_amount": {"currency_code": "USD", "value": "10.00"},
                    "unit_of_measure": "AMOUNT",
                },
                {
                    "name": "Additional requirements",
                    "quantity": 1,
                    "unit_amount": {"currency_code": "USD", "value": "5.00"},
                    "unit_of_measure": "AMOUNT",
                },
                {
                    "name": "Discount",
                    "quantity": 1,
                    "unit_amount": {"currency_code": "USD", "value": "-1.00"},
                    "unit_of_measure": "AMOUNT",
                },
                {
                    "name": "Tax",
                    "quantity": 1,
                    "unit_amount": {"currency_code": "USD", "value": "6.00"},
                    "beep": "boop",
                    "unit_of_measure": "PERCENTAGE",
                },
            ],
        )


class TestClearExistingInvoice(EnsurePlansMixin, TestCase):
    def test_ignores_non_existent(self):
        deliverable = DeliverableFactory.create()
        mock_paypal = MagicMock()
        mock_paypal.post.return_value.json.return_value = {"items": []}
        self.assertTrue(clear_existing_invoice(mock_paypal, deliverable.invoice))
        mock_paypal.post.assert_called_with(
            "v2/invoicing/search-invoices",
            {"invoice_number": deliverable.invoice.id},
        )
        mock_paypal.delete.assert_not_called()

    def test_deletes_existing(self):
        deliverable = DeliverableFactory.create()
        mock_paypal = MagicMock()
        mock_paypal.post.return_value.json.return_value = {
            "items": [
                {
                    "status": "DRAFT",
                    "id": "beep",
                }
            ]
        }
        self.assertTrue(clear_existing_invoice(mock_paypal, deliverable.invoice))
        mock_paypal.delete.assert_called_with(
            "v2/invoicing/invoices/beep",
        )

    def test_skip_bad_status(self):
        deliverable = DeliverableFactory.create()
        mock_paypal = MagicMock()
        mock_paypal.post.return_value.json.return_value = {
            "items": [
                {
                    "status": "PAID",
                    "id": "beep",
                }
            ]
        }
        self.assertFalse(clear_existing_invoice(mock_paypal, deliverable.invoice))
        mock_paypal.delete.assert_not_called()


@ddt
class TestPaypalInvoiceUrl(UnitTest):
    @data(
        (True, False, "https://www.sandbox.paypal.com/invoice/p/#BEEPBOOP"),
        (True, True, "https://www.sandbox.paypal.com/invoice/details/INV2-BEEP-BOOP"),
        (False, True, "https://www.paypal.com/invoice/details/INV2-BEEP-BOOP"),
        (False, False, "https://www.paypal.com/invoice/p/#BEEPBOOP"),
    )
    @unpack
    def test_sender_url(self, test_mode, sender, result):
        with override_settings(CARD_TEST=test_mode):
            self.assertEqual(
                paypal_invoice_url("INV2-BEEP-BOOP", sender=sender),
                result,
            )


class TestTransferableLines(EnsurePlansMixin, TestCase):
    def test_lines_filtered(self):
        invoice = DeliverableFactory.create().invoice
        item = LineItemFactory.create(invoice=invoice, type=DELIVERABLE_TRACKING)
        # Sanity check before real test.
        self.assertIn(item, list(invoice.line_items.all()))
        resulting_lines = transferable_lines(invoice)
        self.assertNotIn(item, resulting_lines)
        self.assertTrue(resulting_lines)


class TestReconcileInvoices(EnsurePlansMixin, TestCase):
    def test_reconcile_invoices_initial_population(self):
        deliverable = DeliverableFactory.create()
        paypal_invoice = invoice_paid_event()["resource"]["invoice"]
        paypal_invoice["amount"]["value"] = str(
            Decimal(deliverable.invoice.total().amount) + Decimal("5.00")
        )
        reconcile_invoices(
            deliverable,
            paypal_invoice,
        )
        item = deliverable.invoice.line_items.get(type=RECONCILIATION)
        self.assertEqual(item.amount, Money("5.00", "USD"))

    def test_reconcile_invoices_replace_items(self):
        paypal_invoice = invoice_updated_event()["resource"]["invoice"]
        deliverable = DeliverableFactory.create(
            invoice__paypal_token=paypal_invoice["id"],
            escrow_enabled=False,
            paypal=True,
        )
        item = deliverable.invoice.line_items.all().get(type=BASE_PRICE)
        # Should not exist.
        item.paypal_token = "derp"
        item.save()
        reconcile_invoices(
            deliverable,
            paypal_invoice,
        )
        item = deliverable.invoice.line_items.get(type=TAX)
        self.assertEqual(item.amount, Money("5.00", "USD"))
        deliverable.invoice.refresh_from_db()
        self.assertEqual(deliverable.invoice.total(), Money("108.00", "USD"))
        item = deliverable.invoice.line_items.get(type=RECONCILIATION)
        self.assertEqual(item.frozen_value, Money("103.00", "USD"))
        self.assertFalse(
            deliverable.invoice.line_items.all().filter(type=BASE_PRICE).exists()
        )

    def test_reconcile_invoices_updates_items(self):
        paypal_invoice = invoice_updated_event()["resource"]["invoice"]
        deliverable = DeliverableFactory.create(
            invoice__paypal_token=paypal_invoice["id"],
            escrow_enabled=False,
            paypal=True,
        )
        item = deliverable.invoice.line_items.all().get(type=BASE_PRICE)
        item.paypal_token = paypal_invoice["items"][0]["id"]
        item.save()
        reconcile_invoices(
            deliverable,
            paypal_invoice,
        )
        deliverable.invoice.refresh_from_db()
        self.assertEqual(deliverable.invoice.total(), Money("108.00", "USD"))
        item.refresh_from_db()
        self.assertEqual(item.frozen_value, Money("100", "USD"))

    def test_handles_currency_change(self):
        paypal_invoice = invoice_updated_event()["resource"]["invoice"]
        paypal_invoice["amount"]["value"] = "10800"
        paypal_invoice["amount"]["currency_code"] = "JPY"
        paypal_invoice["detail"]["currency_code"] = "JPY"
        paypal_invoice["amount"]["breakdown"]["tax_total"]["value"] = "500"
        paypal_invoice["amount"]["breakdown"]["tax_total"]["currency_code"] = "JPY"
        for item in paypal_invoice["items"]:
            item["unit_amount"]["value"] = item["unit_amount"]["value"].replace(".", "")
            item["unit_amount"]["currency_code"] = "JPY"
        deliverable = DeliverableFactory.create(
            invoice__paypal_token=paypal_invoice["id"],
            escrow_enabled=False,
            paypal=True,
        )
        item = deliverable.invoice.line_items.all().get(type=BASE_PRICE)
        item.paypal_token = paypal_invoice["items"][0]["id"]
        item.save()
        reconcile_invoices(
            deliverable,
            paypal_invoice,
        )
        deliverable.invoice.refresh_from_db()
        self.assertEqual(deliverable.invoice.total(), Money("10800", "JPY"))
        item.refresh_from_db()
        self.assertEqual(item.frozen_value, Money("10000", "JPY"))
        item = deliverable.invoice.line_items.get(type=TAX)
        self.assertEqual(item.amount, Money("500", "JPY"))
        item = deliverable.invoice.line_items.get(type=RECONCILIATION)
        self.assertEqual(item.amount, Money("300", "JPY"))


@patch("apps.sales.paypal.paypal_api")
class TestGeneratePaypalInvoice(EnsurePlansMixin, TestCase):
    def test_skips_non_paypal(self, mock_paypal):
        config = PaypalConfigFactory.create(user__service_plan=self.landscape)
        deliverable = DeliverableFactory.create(
            paypal=False,
            escrow_enabled=True,
            order__seller=config.user,
        )
        self.assertFalse(generate_paypal_invoice(deliverable))
        mock_paypal.assert_not_called()

    def test_skips_no_config(self, mock_paypal):
        deliverable = DeliverableFactory.create(
            paypal=True,
            order__seller__service_plan=self.landscape,
            escrow_enabled=False,
            product__paypal=True,
        )
        self.assertFalse(generate_paypal_invoice(deliverable))
        mock_paypal.assert_not_called()

    def test_skips_inactive_config(self, mock_paypal):
        config = PaypalConfigFactory.create(
            user__service_plan=self.landscape,
            template_id="",
            active=False,
        )
        deliverable = DeliverableFactory.create(
            paypal=True,
            order__seller=config.user,
            escrow_enabled=False,
            product__paypal=True,
        )
        self.assertFalse(generate_paypal_invoice(deliverable))
        mock_paypal.assert_not_called()

    def test_skips_unsupported_plan(self, mock_paypal):
        config = PaypalConfigFactory.create(user__service_plan=self.free)
        deliverable = DeliverableFactory.create(
            paypal=True,
            order__seller=config.user,
            escrow_enabled=False,
            product__paypal=True,
        )
        self.assertFalse(generate_paypal_invoice(deliverable))
        mock_paypal.assert_not_called()

    @patch("apps.sales.paypal.clear_existing_invoice")
    def test_generates_invoice(self, _mock_clear_existing, mock_paypal):
        mock_paypal.return_value.__enter__.return_value.template_id = "Bork"
        config = PaypalConfigFactory.create(
            user__service_plan=self.landscape,
            template_id="Bork",
        )
        deliverable = DeliverableFactory.create(
            paypal=True,
            order__seller=config.user,
            order__buyer__email="test@example.com",
            escrow_enabled=False,
            product__paypal=True,
        )
        post = mock_paypal.return_value.__enter__.return_value.post
        get = mock_paypal.return_value.__enter__.return_value.get
        post.return_value.json.return_value = {
            "href": "https://paypal.com/invoicing/invoices/INV2-BEEP-BOOP"
        }
        get.return_value.json.side_effect = [
            {
                "id": "INV2-BEEP-BOOP",
                "amount": {"value": "20.00", "currency_code": "USD", "breakdown": {}},
                "items": [
                    {
                        "id": "ITEM-2HC901790X7563634",
                        "name": "Tax",
                        "quantity": 1,
                        "unit_amount": {"currency_code": "USD", "value": "6.00"},
                        "beep": "boop",
                        "unit_of_measure": "PERCENTAGE",
                    }
                ],
            },
            {
                "id": "INV2-BEEP-BOOP",
                "amount": {
                    "value": "20.00",
                    "currency_code": "USD",
                    "breakdown": {
                        "tax_total": {"value": "0.00", "currency_code": "USD"}
                    },
                },
                "items": [
                    {
                        "id": "ITEM-2HC901790X7563635",
                        "name": f"Order #{deliverable.order.id} [{deliverable.name}] - "
                        f"{deliverable.product.name}",
                        "quantity": 1,
                        "unit_amount": {"currency_code": "USD", "value": "10.00"},
                        "unit_of_measure": "AMOUNT",
                    },
                    {
                        "id": "ITEM-2HC901790X7563636",
                        "name": "Additional requirements",
                        "quantity": 1,
                        "unit_amount": {"currency_code": "USD", "value": "5.00"},
                        "unit_of_measure": "AMOUNT",
                    },
                    {
                        "id": "ITEM-2HC901790X7563637",
                        "name": "Discount",
                        "quantity": 1,
                        "unit_amount": {"currency_code": "USD", "value": "-1.00"},
                        "unit_of_measure": "AMOUNT",
                    },
                    {
                        "id": "ITEM-2HC901790X7563638",
                        "name": "Tax",
                        "quantity": 1,
                        "unit_amount": {"currency_code": "USD", "value": "6.00"},
                        "beep": "boop",
                        "unit_of_measure": "PERCENTAGE",
                    },
                ],
            },
        ]
        self.assertTrue(generate_paypal_invoice(deliverable))
        deliverable.invoice.refresh_from_db()
        self.assertEqual(deliverable.invoice.paypal_token, "INV2-BEEP-BOOP")
        post.assert_has_calls(
            [
                call(
                    "v2/invoicing/invoices",
                    {
                        "detail": {
                            "currency_code": "USD",
                            "invoice_number": deliverable.invoice.id,
                            "payment_term": {
                                "term_type": "DUE_ON_RECEIPT",
                            },
                        },
                        "configuration": {
                            "allow_tip": True,
                            "template_id": "Bork",
                        },
                        "primary_recipients": [
                            {"billing_info": {"email_address": "test@example.com"}}
                        ],
                    },
                ),
                # Not sure why this is counted as a call, but it is.
                call().json(),
                call("v2/invoicing/invoices/INV2-BEEP-BOOP/send", {}),
            ]
        )


@patch("apps.sales.paypal.paypal_api")
class TestValidatePaypalRequest(EnsurePlansMixin, TestCase):
    def test_validated(self, mock_paypal):
        post = mock_paypal.return_value.__enter__.return_value.post
        post.return_value.json.return_value = {"verification_status": "SUCCESS"}
        request = MagicMock()
        request.headers = {
            "Paypal-Transmission-Id": "Beep",
            "Paypal-Transmission-Time": "10 O'clock",
            "Paypal-Transmission-Sig": "I did it",
            "Paypal-Auth-Algo": "Super sneakret algorithm",
            "Paypal-Cert-Url": "https://example.com/cert.pem",
        }
        request.body = b'{"test": "thing"}'
        config = PaypalConfigFactory.create()
        validate_paypal_request(request, config)

    def test_invalid(self, mock_paypal):
        post = mock_paypal.return_value.__enter__.return_value.post
        post.return_value.json.return_value = {"verification_status": "FAILED"}
        request = MagicMock()
        request.headers = {
            "Paypal-Transmission-Id": "Beep",
            "Paypal-Transmission-Time": "10 O'clock",
            "Paypal-Transmission-Sig": "I did it",
            "Paypal-Auth-Algo": "Super sneakret algorithm",
            "Paypal-Cert-Url": "https://example.com/cert.pem",
        }
        request.body = b'{"test": "thing"}'
        config = PaypalConfigFactory.create()
        with self.assertRaises(SignatureValidationError):
            validate_paypal_request(request, config)

    def test_missing_headers(self, mock_paypal):
        post = mock_paypal.return_value.__enter__.return_value.post
        post.return_value.json.return_value = {"verification_status": "SUCCESS"}
        request = MagicMock()
        request.headers = {
            "Paypal-Transmission-Id": "Beep",
        }
        request.body = b'{"test": "thing"}'
        config = PaypalConfigFactory.create()
        with self.assertRaises(SignatureValidationError):
            validate_paypal_request(request, config)
        post.assert_not_called()
