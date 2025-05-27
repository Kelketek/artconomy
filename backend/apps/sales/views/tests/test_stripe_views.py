from unittest.mock import Mock, patch

from apps.lib.test_resources import APITestCase
from apps.lib.tests.test_utils import create_staffer
from apps.profiles.tests.factories import UserFactory
from apps.sales import stripe as stripe_module
from apps.sales.constants import OPEN, PAYMENT_PENDING, STRIPE
from apps.sales.models import StripeAccount, Deliverable
from apps.sales.tests.factories import (
    CreditCardTokenFactory,
    DeliverableFactory,
    InvoiceFactory,
    StripeAccountFactory,
    StripeReaderFactory,
)
from apps.sales.views.tests.fixtures.stripe_fixtures import (
    COUNTRIES_ARTCONOMY_OUTPUT,
    gen_stripe_countries_output,
)
from django.test import override_settings
from rest_framework import status
from stripe.error import InvalidRequestError


class TestStripeCountries(APITestCase):
    @patch("apps.sales.views.stripe_views.stripe")
    def test_list_countries(self, mock_stripe):
        stripe_module.COUNTRY_CACHE["cache"] = None
        mock_stripe.__enter__.return_value.CountrySpec.retrieve.return_value = (
            gen_stripe_countries_output()
        )
        result = self.client.get("/api/sales/v1/stripe-countries/")
        self.assertEqual(result.data, COUNTRIES_ARTCONOMY_OUTPUT)
        # Should be cached for the second go-around.
        result = self.client.get("/api/sales/v1/stripe-countries/")
        self.assertEqual(result.data, COUNTRIES_ARTCONOMY_OUTPUT)
        self.assertEqual(
            mock_stripe.__enter__.return_value.CountrySpec.retrieve.call_count, 1
        )


@patch("apps.sales.views.stripe_views.stripe")
class TestStripeAccountLink(APITestCase):
    def test_stripe_link_creates_account(self, mock_stripe):
        mock_stripe.__enter__.return_value.CountrySpec.retrieve.return_value = (
            gen_stripe_countries_output()
        )
        mock_stripe.__enter__.return_value.Account.create.return_value = {"id": "12345"}
        mock_stripe.__enter__.return_value.AccountLink.create.return_value = {
            "url": "https://stripe.com/strope/"
        }
        user = UserFactory.create()
        self.login(user)
        result = self.client.post(
            f"/api/sales/v1/account/{user.username}/stripe-accounts/link/",
            {"url": "https://example.com/", "country": "US"},
        )
        self.assertEqual(result.data["link"], "https://stripe.com/strope/")
        account = StripeAccount.objects.get()
        self.assertEqual(account.token, "12345")

    @patch("apps.sales.models.stripe")
    def test_stripe_link_change_country(self, mock_model_stripe, mock_stripe):
        account = StripeAccountFactory.create(token="12345", country="US")
        user = account.user
        mock_stripe.__enter__.return_value.CountrySpec.retrieve.return_value = (
            gen_stripe_countries_output()
        )
        mock_stripe.__enter__.return_value.Account.create.return_value = {"id": "6789"}
        mock_stripe.__enter__.return_value.AccountLink.create.return_value = {
            "url": "https://stripe.com/strope/"
        }
        self.login(user)
        result = self.client.post(
            f"/api/sales/v1/account/{user.username}/stripe-accounts/link/",
            {"url": "https://example.com/", "country": "DE"},
        )
        self.assertEqual(result.data["link"], "https://stripe.com/strope/")
        # Old one should be, or else the ID should be updated.
        account = StripeAccount.objects.get()
        self.assertEqual(account.token, "6789")

    @patch("apps.sales.models.stripe")
    def test_stripe_link_change_country_deliverable_exists(
        self,
        mock_model_stripe,
        mock_stripe,
    ):
        account = StripeAccountFactory.create(token="12345", country="US")
        user = account.user
        mock_stripe.__enter__.return_value.CountrySpec.retrieve.return_value = (
            gen_stripe_countries_output()
        )
        mock_stripe.__enter__.return_value.Account.create.return_value = {"id": "6789"}
        mock_stripe.__enter__.return_value.AccountLink.create.return_value = {
            "url": "https://stripe.com/strope/"
        }
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user)
        # Sidestep side effects when setting this field.
        Deliverable.objects.filter(id=deliverable.id).update(escrow_enabled=True)
        result = self.client.post(
            f"/api/sales/v1/account/{user.username}/stripe-accounts/link/",
            {"url": "https://example.com/", "country": "DE"},
        )
        self.assertEqual(
            result.data["detail"],
            "User already started escrow sales! Cannot redo Stripe account.",
        )
        # No change should have happened.
        current_account = StripeAccount.objects.get()
        self.assertEqual(account, current_account)
        self.assertEqual(account.token, current_account.token)

    # Note: testserver is the server name of Django's test system.
    @override_settings(ALLOWED_HOSTS=("testserver",))
    @patch("apps.sales.models.stripe")
    def test_stripe_link_bad_url(self, mock_model_stripe, mock_stripe):
        mock_stripe.__enter__.return_value.CountrySpec.retrieve.return_value = (
            gen_stripe_countries_output()
        )
        user = UserFactory.create()
        self.login(user)
        result = self.client.post(
            f"/api/sales/v1/account/{user.username}/stripe-accounts/link/",
            {"url": "https://example.com/", "country": "DE"},
        )
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.data["url"], ["Unrecognized domain."])

    @patch("apps.sales.models.stripe")
    def test_stripe_link_same_country(self, mock_model_stripe, mock_stripe):
        account = StripeAccountFactory.create(token="12345", country="US")
        user = account.user
        mock_stripe.__enter__.return_value.CountrySpec.retrieve.return_value = (
            gen_stripe_countries_output()
        )
        mock_stripe.__enter__.return_value.AccountLink.create.return_value = {
            "url": "https://stripe.com/strope/"
        }
        self.login(user)
        result = self.client.post(
            f"/api/sales/v1/account/{user.username}/stripe-accounts/link/",
            {"url": "https://example.com/", "country": "US"},
        )
        self.assertEqual(result.data["link"], "https://stripe.com/strope/")
        # Old one should be, or else the ID should be updated.
        account = StripeAccount.objects.get()
        self.assertEqual(account.token, "12345")


class TestStripeAccounts(APITestCase):
    def test_stripe_account_list_none(self):
        user = UserFactory.create()
        self.login(user)
        result = self.client.get(
            f"/api/sales/v1/account/{user.username}/stripe-accounts/",
        )
        self.assertEqual(result.data, [])

    def test_stripe_account_list_one(self):
        account = StripeAccountFactory.create(country="GB", active=True)
        user = account.user
        self.login(user)
        result = self.client.get(
            f"/api/sales/v1/account/{user.username}/stripe-accounts/",
        )
        self.assertEqual(
            result.data, [{"id": account.id, "active": True, "country": "GB"}]
        )

    def test_stripe_accounts_wrong_account(self):
        account = StripeAccountFactory.create(country="GB", active=True)
        self.login(UserFactory.create())
        result = self.client.get(
            f"/api/sales/v1/account/{account.user.username}/stripe-accounts/",
        )
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)


@patch("apps.sales.models.stripe")
@patch("apps.sales.views.stripe_views.stripe")
class TestStripePresentCard(APITestCase):
    def test_no_invoice_intent(self, _mock_stripe, _mock_model_stripe):
        invoice = InvoiceFactory.create(status=OPEN)
        invoice.current_intent = ""
        invoice.save()
        self.login(invoice.bill_to)
        response = self.client.post(
            f"/api/sales/v1/invoice/{invoice.id}/stripe-process-present-card/"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "This invoice does not have a generated payment intent.",
        )

    def test_processed_intent(self, mock_stripe, _mock_model_stripe):
        invoice = InvoiceFactory.create(status=OPEN, current_intent="beep")
        reader = StripeReaderFactory.create(stripe_token="abc")
        self.login(invoice.bill_to)
        response = self.client.post(
            f"/api/sales/v1/invoice/{invoice.id}/stripe-process-present-card/",
            {"reader": reader.id},
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # noqa: E501
        mock_stripe.__enter__.return_value.terminal.Reader.process_payment_intent.assert_called_with(
            "abc",
            payment_intent="beep",
        )

    def test_no_connection(self, mock_stripe, _mock_model_stripe):
        mock_api = Mock()
        # noqa: E501
        mock_api.terminal.Reader.process_payment_intent.side_effect = (
            InvalidRequestError(
                "Reader is currently unreachable, please ensure the reader is "
                "powered on and connected to the internet before retrying your "
                "request.",
                "Request",
            )
        )
        mock_stripe.__enter__.return_value = mock_api
        reader = StripeReaderFactory.create()
        invoice = InvoiceFactory.create(status=OPEN)
        invoice.current_intent = "beep"
        invoice.save()
        self.login(invoice.bill_to)
        response = self.client.post(
            f"/api/sales/v1/invoice/{invoice.id}/stripe-process-present-card/",
            {"reader": reader.id},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Could not reach the card reader. Make sure it is on and connected to the "
            "Internet.",
        )

    def test_other_exception(self, mock_stripe, _mock_model_stripe):
        mock_api = Mock()
        mock_api.terminal.Reader.process_payment_intent.side_effect = (
            InvalidRequestError(
                "It borked!",
                param="things",
            )
        )
        mock_stripe.__enter__.return_value = mock_api
        reader = StripeReaderFactory.create()
        invoice = InvoiceFactory.create(status=OPEN)
        invoice.current_intent = "beep"
        invoice.save()
        self.login(invoice.bill_to)
        with self.assertRaises(InvalidRequestError, msg="It borked!"):
            self.client.post(
                f"/api/sales/v1/invoice/{invoice.id}/stripe-process-present-card/",
                {"reader": reader.id},
            )


@patch("apps.sales.models.stripe")
class TestStripeReaders(APITestCase):
    def test_list_readers(self, _mock_stripe):
        reader = StripeReaderFactory.create(name="Money Maker")
        user = create_staffer("table_seller")
        self.login(user)
        result = self.client.get("/api/sales/v1/stripe-readers/")
        self.assertEqual(
            result.data["results"], [{"id": reader.id, "name": reader.name}]
        )

    def test_list_readers_non_staff(self, _mock_stripe):
        user = UserFactory.create()
        self.login(user)
        result = self.client.get("/api/sales/v1/stripe-readers/")
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)


@patch("apps.sales.views.stripe_views.stripe")
class TestSetupIntent(APITestCase):
    def test_setup_intent(self, mock_stripe):
        mock_stripe.__enter__.return_value.SetupIntent.create.return_value = {
            "client_secret": "1234"
        }
        user = UserFactory.create(stripe_token="beep")
        self.login(user)
        result = self.client.post(
            f"/api/sales/v1/account/{user.username}/cards/setup-intent/"
        )
        self.assertEqual(result.data, {"secret": "1234"})


class TestInvoicePaymentIntent(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.patcher = patch("apps.sales.utils.create_or_update_stripe_user")
        self.patcher.start()

    def tearDown(self) -> None:
        self.patcher.stop()

    @patch("apps.sales.utils.stripe")
    def test_create_payment_intent(self, mock_stripe):
        mock_api = Mock()
        mock_stripe.__enter__.return_value = mock_api
        mock_api.PaymentIntent.create.return_value = {
            "id": "raw_id",
            "client_secret": "sneak",
        }
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, invoice__status=OPEN
        )
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/v1/invoice/{deliverable.invoice.id}/payment-intent/",
        )
        self.assertEqual(response.data, {"secret": "sneak"})
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.invoice.current_intent, "raw_id")
        params = mock_api.PaymentIntent.create.call_args_list[0][1]
        self.assertEqual(params["amount"], deliverable.invoice.total().amount * 100)
        self.assertEqual(params["currency"], "usd")
        self.assertIsNone(params["payment_method"])
        self.assertEqual(
            params["metadata"],
            {
                "invoice_id": deliverable.invoice.id,
                "make_primary": False,
                "save_card": False,
            },
        )
        self.assertEqual(params["payment_method_types"], ["card"])
        self.assertEqual(
            params["transfer_group"], f"ACInvoice#{deliverable.invoice.id}"
        )
        mock_api.PaymentIntent.modify.assert_not_called()

    @patch("apps.sales.utils.stripe")
    def test_modify_payment_intent(self, mock_stripe):
        mock_api = Mock()
        mock_stripe.__enter__.return_value = mock_api
        mock_api.PaymentIntent.modify.return_value = {
            "id": "raw_id",
            "client_secret": "sneak",
        }
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING,
            invoice__current_intent="old_id",
            processor=STRIPE,
            invoice__status=OPEN,
        )
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/v1/invoice/{deliverable.invoice.id}/payment-intent/",
            {"save_card": True},
        )
        self.assertEqual(response.data, {"secret": "sneak"})
        deliverable.refresh_from_db()
        # Should not have changed.
        self.assertEqual(deliverable.invoice.current_intent, "old_id")
        mock_api.PaymentIntent.create.assert_not_called()
        self.assertEqual(
            mock_api.PaymentIntent.modify.call_args_list[0][0][0], "old_id"
        )
        params = mock_api.PaymentIntent.modify.call_args_list[0][1]
        self.assertEqual(params["amount"], deliverable.invoice.total().amount * 100)
        self.assertEqual(params["currency"], "usd")
        self.assertEqual(
            params["metadata"],
            {
                "invoice_id": deliverable.invoice.id,
                "make_primary": False,
                "save_card": True,
            },
        )
        self.assertEqual(params["capture_method"], "automatic")
        self.assertEqual(params["setup_future_usage"], "off_session")
        self.assertEqual(params["payment_method_types"], ["card"])
        self.assertEqual(
            params["transfer_group"], f"ACInvoice#{deliverable.invoice.id}"
        )

    @patch("apps.sales.utils.stripe")
    def test_use_specific_card(self, mock_stripe):
        mock_api = Mock()
        mock_stripe.__enter__.return_value = mock_api
        mock_api.PaymentIntent.create.return_value = {
            "id": "raw_id",
            "client_secret": "sneak",
        }
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, processor=STRIPE, invoice__status=OPEN
        )
        card = CreditCardTokenFactory(
            user=deliverable.order.buyer, stripe_token="butts", token=""
        )
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/v1/invoice/{deliverable.invoice.id}/payment-intent/",
            {"card_id": card.id},
        )
        self.assertEqual(response.data, {"secret": "sneak"})
        deliverable.refresh_from_db()
        params = mock_api.PaymentIntent.create.call_args_list[0][1]
        self.assertEqual(params["payment_method"], "butts")

    @patch("apps.sales.utils.stripe")
    def test_fail_wrong_card_user(self, mock_stripe):
        mock_api = Mock()
        mock_stripe.__enter__.return_value = mock_api
        mock_api.PaymentIntent.create.return_value = {
            "id": "raw_id",
            "client_secret": "sneak",
        }
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, processor=STRIPE, invoice__status=OPEN
        )
        card = CreditCardTokenFactory(stripe_token="butts", token="")
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/v1/invoice/{deliverable.invoice.id}/payment-intent/",
            {"card_id": card.id},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.sales.utils.stripe")
    def test_use_default_card(self, mock_stripe):
        mock_api = Mock()
        mock_stripe.__enter__.return_value = mock_api
        mock_api.PaymentIntent.create.return_value = {
            "id": "raw_id",
            "client_secret": "sneak",
        }
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, processor=STRIPE, invoice__status=OPEN
        )
        card = CreditCardTokenFactory(
            stripe_token="butts", token="", user=deliverable.order.buyer
        )
        deliverable.order.buyer.primary_card = card
        deliverable.order.buyer.save()
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/v1/invoice/{deliverable.invoice.id}/payment-intent/",
        )
        self.assertEqual(response.data, {"secret": "sneak"})
        deliverable.refresh_from_db()
        params = mock_api.PaymentIntent.create.call_args_list[0][1]
        self.assertEqual(params["payment_method"], "butts")

    @patch("apps.sales.utils.stripe")
    def test_fail_no_bill_to(self, mock_stripe):
        mock_api = Mock()
        mock_stripe.__enter__.return_value = mock_api
        mock_api.PaymentIntent.create.return_value = {
            "id": "raw_id",
            "client_secret": "sneak",
        }
        invoice = InvoiceFactory.create(bill_to=None, status=OPEN)
        self.login(UserFactory.create(is_superuser=True, is_staff=True))
        response = self.client.post(
            f"/api/sales/v1/invoice/{invoice.id}/payment-intent/",
        )
        print(response.data)
        self.assertEqual(
            response.data,
            ["Cannot create a payment intent when there's no user to bill."],
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_incompatible_card(self):
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, processor=STRIPE, invoice__status=OPEN
        )
        card = CreditCardTokenFactory(
            token="butts", stripe_token="", user=deliverable.order.buyer
        )
        deliverable.order.buyer.primary_card = card
        deliverable.order.buyer.save()
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/v1/invoice/{deliverable.invoice.id}/payment-intent/",
            {"card_id": card.id},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {"card_id": "That card ID is not a stripe card."}
        )

    @patch("apps.sales.utils.stripe")
    def test_succeeded_already(self, mock_stripe):
        mock_api = Mock()
        mock_stripe.__enter__.return_value = mock_api
        mock_api.PaymentIntent.modify.side_effect = InvalidRequestError(
            "Oops.",
            param="",
            code="payment_intent_unexpected_state",
            json_body={"error": {"payment_intent": {"status": "succeeded"}}},
        )
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING,
            invoice__current_intent="old_id",
            processor=STRIPE,
            invoice__status=OPEN,
        )
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/v1/invoice/{deliverable.invoice.id}/payment-intent/",
            {"save_card": True},
        )
        self.assertIn("This payment has already been made.", response.data[0])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.sales.utils.stripe")
    def test_start_over(self, mock_stripe):
        mock_api = Mock()
        mock_stripe.__enter__.return_value = mock_api
        mock_api.PaymentIntent.modify.side_effect = InvalidRequestError(
            "Oops.",
            param="",
            code="payment_intent_unexpected_state",
            json_body={"error": {"payment_intent": {"status": "beeping"}}},
        )
        mock_api.PaymentIntent.create.return_value = {
            "id": "raw_id",
            "client_secret": "sneak",
        }
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING,
            invoice__current_intent="old_id",
            processor=STRIPE,
            invoice__status=OPEN,
        )
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/v1/invoice/{deliverable.invoice.id}/payment-intent/",
        )
        self.assertEqual(response.data, {"secret": "sneak"})
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.invoice.current_intent, "raw_id")

    @patch("apps.sales.utils.stripe")
    def test_zero_invoice(self, mock_stripe):
        card = CreditCardTokenFactory(stripe_token="butts", token="")
        invoice = InvoiceFactory.create(bill_to=card.user, status=OPEN)
        self.login(invoice.bill_to)
        response = self.client.post(
            f"/api/sales/v1/invoice/{invoice.id}/payment-intent/",
        )
        self.assertIn("zero invoice", response.data[0])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.sales.utils.stripe")
    def test_use_terminal(self, mock_stripe):
        mock_api = Mock()
        mock_stripe.__enter__.return_value = mock_api
        mock_api.PaymentIntent.create.return_value = {
            "id": "raw_id",
            "client_secret": "sneak",
        }
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, invoice__status=OPEN
        )
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/v1/invoice/{deliverable.invoice.id}/payment-intent/",
            {"use_reader": True, "save_card": True},
        )
        self.assertEqual(response.data, {"secret": "sneak"})
        params = mock_api.PaymentIntent.create.call_args_list[0][1]
        self.assertEqual(params["payment_method_types"], ["card_present", "card"])
        self.assertEqual(params["capture_method"], "manual")
        self.assertEqual(
            params["metadata"],
            {
                "invoice_id": deliverable.invoice.id,
                "make_primary": False,
                # We're not saving the card if we use a terminal.
                "save_card": False,
            },
        )


class TestPremiumPaymentIntent(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.patcher = patch("apps.sales.utils.create_or_update_stripe_user")
        self.patcher.start()

    def tearDown(self) -> None:
        self.patcher.stop()

    @patch("apps.sales.utils.stripe")
    def test_premium_payment_intent(self, mock_stripe):
        mock_api = Mock()
        mock_stripe.__enter__.return_value = mock_api
        mock_api.PaymentIntent.create.return_value = {
            "id": "raw_id",
            "client_secret": "sneak",
        }
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            f"/api/sales/v1/account/{user.username}/premium/intent/",
            {"use_reader": True, "save_card": True, "service": "Landscape"},
        )
        self.assertEqual(response.data, {"secret": "sneak"})
