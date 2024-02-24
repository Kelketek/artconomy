from decimal import Decimal
from unittest.mock import Mock, patch

from authlib.integrations.base_client import MissingTokenError

from apps.lib.abstract_models import ADULT, EXTREME, GENERAL
from apps.lib.models import COMMENT, Comment, Subscription, ref_for_instance
from apps.lib.test_resources import (
    APITestCase,
    EnsurePlansMixin,
    MethodAccessMixin,
    PermissionsTestCase,
)
from apps.lib.tests.factories import AssetFactory, TagFactory
from apps.profiles.models import (
    IN_SUPPORTED_COUNTRY,
    NO_SUPPORTED_COUNTRY,
    UNSET,
    ArtistTag,
    User,
)
from apps.profiles.tests.factories import (
    CharacterFactory,
    SubmissionFactory,
    UserFactory,
)
from apps.sales.constants import (
    ADD_ON,
    BASE_PRICE,
    CANCELLED,
    COMPLETED,
    DELIVERABLE_STATUSES,
    DISPUTED,
    DRAFT,
    ESCROW,
    EXTRA,
    HOLDINGS,
    IN_PROGRESS,
    LIMBO,
    MISSED,
    NEW,
    OPEN,
    PAID,
    PAYMENT_PENDING,
    PENDING,
    QUEUED,
    REFUNDED,
    REVIEW,
    SUBSCRIPTION,
    TIP,
    TIPPING,
    VOID,
    WAITING,
)
from apps.sales.models import Deliverable, Order, Product, Reference, PaypalConfig
from apps.sales.tests.factories import (
    CreditCardTokenFactory,
    DeliverableFactory,
    InvoiceFactory,
    LineItemFactory,
    ProductFactory,
    RatingFactory,
    ReferenceFactory,
    RevisionFactory,
    ServicePlanFactory,
    StripeAccountFactory,
    TransactionRecordFactory,
    PaypalConfigFactory,
)
from apps.sales.utils import initialize_tip_invoice
from apps.sales.views.main import (
    ArchivedCasesList,
    ArchivedOrderList,
    ArchivedSalesList,
    CancelledCasesList,
    CancelledOrderList,
    CancelledSalesList,
    CurrentCasesList,
    CurrentOrderList,
    CurrentSalesList,
    ProductList,
)
from dateutil.relativedelta import relativedelta
from ddt import data, ddt, unpack
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from django.utils.datetime_safe import date
from freezegun import freeze_time
from moneyed import Money
from rest_framework import status
from shortcuts import make_url

order_scenarios = (
    {
        "category": "current",
        "included": (NEW, IN_PROGRESS, DISPUTED, REVIEW, PAYMENT_PENDING, QUEUED),
        "buyer_only": (LIMBO,),
    },
    {
        "category": "archived",
        "included": (COMPLETED,),
        "buyer_only": tuple(),
    },
    {
        "category": "cancelled",
        "included": (REFUNDED, CANCELLED),
        "buyer_only": (MISSED,),
    },
    {
        "category": "waiting",
        "included": (WAITING,),
        "buyer_only": tuple(),
    },
)

categories = [scenario["category"] for scenario in order_scenarios]


@ddt
class TestOrderListBase(object):
    buyer = False

    @unpack
    @data(*order_scenarios)
    def test_fetch_orders(self, category, included, buyer_only):
        user = UserFactory.create(username="Fox")
        kwargs = self.factory_kwargs(user)
        [
            DeliverableFactory.create(status=order_status, **kwargs)
            for order_status in [x for x, y in DELIVERABLE_STATUSES]
        ]
        user = User.objects.get(username="Fox")
        self.login(user)
        response = self.client.get(self.make_url(user, category))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        allowed_statuses = [*included]
        if self.buyer:
            allowed_statuses.extend(buyer_only)
        for order in response.data["results"]:
            self.assertIn(
                Deliverable.objects.filter(order_id=order["id"]).first().status,
                allowed_statuses,
            )
        self.assertEqual(len(response.data["results"]), len(allowed_statuses))


class TestOrderLists(TestOrderListBase, APITestCase):
    buyer = True

    @staticmethod
    def make_url(user, category):
        return "/api/sales/account/{}/orders/{}/".format(user.username, category)

    @staticmethod
    def factory_kwargs(user):
        return {"order__buyer": user, "order__seller": UserFactory.create()}


class TestSaleLists(TestOrderListBase, APITestCase):
    @staticmethod
    def make_url(user, category):
        return "/api/sales/account/{}/sales/{}/".format(user.username, category)

    @staticmethod
    def factory_kwargs(user):
        return {"order__seller": user, "order__buyer": UserFactory.create()}

    def test_show_email_when_appropriate(self):
        artist = UserFactory.create()
        self.login(artist)
        normal_deliverable = DeliverableFactory.create(order__seller=artist)
        guest_deliverable = DeliverableFactory.create(
            order__buyer__guest=True,
            order__buyer__guest_email="test@example.com",
            order__seller=artist,
        )
        unregistered_deliverable = DeliverableFactory.create(
            order__buyer=None,
            order__customer_email="test2@example.com",
            order__seller=artist,
        )
        response = self.client.get(self.make_url(artist, "current"))
        first, second, third = response.data["results"]
        self.assertEqual(first["id"], unregistered_deliverable.order.id)
        self.assertEqual(first["guest_email"], "test2@example.com")
        self.assertEqual(second["id"], guest_deliverable.order.id)
        self.assertEqual(second["guest_email"], "test@example.com")
        self.assertEqual(third["id"], normal_deliverable.order.id)
        self.assertEqual(third["guest_email"], "")


class TestCaseLists(TestOrderListBase, APITestCase):
    @staticmethod
    def make_url(user, category):
        return "/api/sales/account/{}/cases/{}/".format(user.username, category)

    @staticmethod
    def factory_kwargs(user):
        user.is_staff = True
        user.save()
        return {
            "arbitrator": user,
            "order__buyer": UserFactory.create(),
            "order__seller": UserFactory.create(),
        }


order_passes = {**MethodAccessMixin.passes, "get": ["user", "staff"]}


class TestCurrentOrderListPermissions(MethodAccessMixin, PermissionsTestCase):
    passes = order_passes
    kwargs = {"username": "Test"}
    view_class = CurrentOrderList


class TestCancelledOrderListPermissions(MethodAccessMixin, PermissionsTestCase):
    passes = order_passes
    kwargs = {"username": "Test"}
    view_class = CancelledOrderList


class TestArchivedOrderListPermissions(MethodAccessMixin, PermissionsTestCase):
    passes = order_passes
    kwargs = {"username": "Test"}
    view_class = ArchivedOrderList


class TestCurrentSalesListPermissions(MethodAccessMixin, PermissionsTestCase):
    passes = order_passes
    kwargs = {"username": "Test"}
    view_class = CurrentSalesList


class TestCancelledSalesListPermissions(MethodAccessMixin, PermissionsTestCase):
    passes = order_passes
    kwargs = {"username": "Test"}
    view_class = CancelledSalesList


class TestArchivedSalesListPermissions(MethodAccessMixin, PermissionsTestCase):
    passes = order_passes
    kwargs = {"username": "Test"}
    view_class = ArchivedSalesList


class StaffUserList:
    def test_self(self):
        request = self.factory.get("/")
        request.user = self.user
        self.check_perms(request, self.user)

    def test_self_staff(self):
        request = self.factory.get("/")
        request.user = self.user
        request.user.is_staff = True
        self.check_perms(request, self.user, fails=False)


staff_order_passes = {**order_passes, "get": ["staff"]}


class TestCurrentCasesListPermissions(
    PermissionsTestCase, StaffUserList, MethodAccessMixin
):
    passes = staff_order_passes
    kwargs = {"username": "Test"}
    view_class = CurrentCasesList


class TestCancelledCasesListPermissions(
    PermissionsTestCase, StaffUserList, MethodAccessMixin
):
    passes = staff_order_passes
    kwargs = {"username": "Test"}
    view_class = CancelledCasesList


class TestArchivedCasesListPermissions(
    PermissionsTestCase, StaffUserList, MethodAccessMixin
):
    passes = staff_order_passes
    kwargs = {"username": "Test"}
    view_class = ArchivedCasesList


class TestSearchWaiting(APITestCase):
    def test_search_waiting_list_product_filter(self):
        deliverable = DeliverableFactory.create(status=WAITING)
        DeliverableFactory.create(
            order__seller=deliverable.order.seller, status=WAITING
        )
        url = f"/api/sales/account/{deliverable.order.seller.username}/sales/waiting/"
        self.login(deliverable.order.seller)
        response = self.client.get(url)
        self.assertEqual(len(response.data["results"]), 2)
        response = self.client.get(f"{url}?product={deliverable.product.id}")
        self.assertIDInList(deliverable.order, response.data["results"])
        self.assertEqual(len(response.data["results"]), 1)

    def test_search_waiting_list_user_filter(self):
        deliverable = DeliverableFactory.create(
            order__buyer__email="beep@boop.com", status=WAITING
        )
        # This one shouldn't match.
        DeliverableFactory.create(
            order__seller=deliverable.order.seller, status=WAITING
        )
        url = (
            f"/api/sales/account/{deliverable.order.seller.username}"
            f"/sales/waiting/?q=beep"
        )
        self.login(deliverable.order.seller)
        response = self.client.get(url)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIDInList(deliverable.order, response.data["results"])

    def test_search_waiting_list_permissions(self):
        deliverable = DeliverableFactory.create(
            order__buyer__email="beep@boop.com", status=WAITING
        )
        url = (
            f"/api/sales/account/{deliverable.order.seller.username}"
            f"/sales/waiting/?q=beep"
        )
        self.login(deliverable.order.buyer)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestProductSamples(APITestCase):
    def test_sample_list(self):
        product = ProductFactory.create()
        submission = SubmissionFactory.create()
        product.samples.add(submission)
        response = self.client.get(
            f"/api/sales/account/{product.user.username}/products/"
            f"{product.id}/samples/",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["submission"]["id"], submission.id)

    def test_destroy_sample(self):
        product = ProductFactory.create()
        submission = SubmissionFactory.create()
        product.samples.add(submission)
        linked = Product.samples.through.objects.get(
            submission=submission, product=product
        )
        self.login(product.user)
        response = self.client.delete(
            f"/api/sales/account/{product.user.username}/products/"
            f"{product.id}/samples/{linked.id}/",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(product.samples.all().count(), 0)

    def test_destroy_sample_primary(self):
        product = ProductFactory.create()
        submission = SubmissionFactory.create()
        product.samples.add(submission)
        product.primary_submission = submission
        product.save()
        linked = Product.samples.through.objects.get(
            submission=submission, product=product
        )
        self.login(product.user)
        response = self.client.delete(
            f"/api/sales/account/{product.user.username}/products/"
            f"{product.id}/samples/{linked.id}/",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(product.samples.all().count(), 0)
        product.refresh_from_db()
        self.assertIsNone(product.primary_submission)

    def test_add_sample(self):
        product = ProductFactory.create()
        submission = SubmissionFactory.create()
        submission.artists.add(product.user)
        self.login(product.user)
        response = self.client.post(
            f"/api/sales/account/{product.user.username}/products/"
            f"{product.id}/samples/",
            {"submission_id": submission.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["submission"]["id"], submission.id)

    def test_add_untagged_sample_fails(self):
        product = ProductFactory.create()
        submission = SubmissionFactory.create()
        self.login(product.user)
        response = self.client.post(
            f"/api/sales/account/{product.user.username}/products/"
            f"{product.id}/samples/",
            {"submission_id": submission.id},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["submission_id"],
            [
                "Either this submission does not exist, or you are not tagged as the "
                "artist in it."
            ],
        )


class TestCardManagement(APITestCase):
    def test_make_primary(self):
        user = UserFactory.create()
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        self.login(user)
        user.refresh_from_db()
        response = self.client.post(
            "/api/sales/account/{}/cards/{}/primary/".format(user.username, cards[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertEqual(user.primary_card.id, cards[2].id)
        response = self.client.post(
            "/api/sales/account/{}/cards/{}/primary/".format(user.username, cards[3].id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertEqual(user.primary_card.id, cards[3].id)

    def test_make_primary_not_logged_in(self):
        user = UserFactory.create()
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        response = self.client.post(
            "/api/sales/account/{}/cards/{}/primary/".format(user.username, cards[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_make_primary_outsider(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        response = self.client.post(
            "/api/sales/account/{}/cards/{}/primary/".format(user.username, cards[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_make_primary_wrong_card(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        [CreditCardTokenFactory(user=user) for __ in range(4)]
        self.login(user)
        user.refresh_from_db()
        response = self.client.post(
            "/api/sales/account/{}/cards/{}/primary/".format(
                user.username, CreditCardTokenFactory.create(user=user2).id
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_card_listing(self):
        user = UserFactory.create()
        self.login(user)
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        response = self.client.get("/api/sales/account/{}/cards/".format(user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for card in cards:
            self.assertIDInList(card, response.data)

    def test_card_listing_stripe(self):
        user = UserFactory.create()
        self.login(user)
        _authorize_cards = [
            CreditCardTokenFactory(user=user, token="boop", stripe_token=None)
            for __ in range(3)
        ]
        stripe_cards = [
            CreditCardTokenFactory(user=user, token="", stripe_token=f"{i}")
            for i in range(2)
        ]
        response = self.client.get(
            "/api/sales/account/{}/cards/stripe/".format(user.username)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for card in stripe_cards:
            self.assertIDInList(card, response.data)
        self.assertEqual(len(response.data), len(stripe_cards))

    def test_card_listing_not_logged_in(self):
        user = UserFactory.create()
        response = self.client.get("/api/sales/account/{}/cards/".format(user.username))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_card_listing_staffer(self):
        staffer = UserFactory.create(is_staff=True)
        user = UserFactory.create()
        self.login(staffer)
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        response = self.client.get("/api/sales/account/{}/cards/".format(user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for card in cards:
            self.assertIDInList(card, response.data)

    @patch("apps.sales.models.stripe")
    def test_card_removal(self, mock_stripe):
        user = UserFactory.create()
        self.login(user)
        cards = [
            CreditCardTokenFactory(user=user, stripe_token=f"{i}") for i in range(4)
        ]
        self.assertEqual(cards[0].active, True)
        self.assertEqual(cards[2].active, True)
        response = self.client.delete(
            "/api/sales/account/{}/cards/{}/".format(user.username, cards[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, False)
        cards[0].refresh_from_db()
        self.assertEqual(cards[0].active, True)
        mock_stripe.__enter__.return_value.PaymentMethod.detach.assert_called_with(
            cards[2].stripe_token
        )

    @patch("apps.sales.models.delete_payment_method")
    def test_card_removal_new_primary(self, _mock_execute):
        old_card = CreditCardTokenFactory.create()
        new_card = CreditCardTokenFactory.create(user=old_card.user)
        user = old_card.user
        user.primary_card = new_card
        user.save()
        self.login(user)
        response = self.client.delete(
            "/api/sales/account/{}/cards/{}/".format(user.username, new_card.id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertEqual(user.primary_card, old_card)

    @patch("apps.sales.models.delete_payment_method")
    def test_card_removal_not_logged_in(self, _mock_execute):
        user = UserFactory.create()
        cards = [
            CreditCardTokenFactory(user=user, stripe_token=f"{i}") for i in range(4)
        ]
        self.assertEqual(cards[2].active, True)
        response = self.client.delete(
            "/api/sales/account/{}/cards/{}/".format(user.username, cards[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, True)

    @patch("apps.sales.models.delete_payment_method")
    def test_card_removal_outsider(self, _mock_execute):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        cards = [
            CreditCardTokenFactory(user=user, stripe_token=f"{i}") for i in range(4)
        ]
        self.assertEqual(cards[2].active, True)
        response = self.client.delete(
            "/api/sales/account/{}/cards/{}/".format(user.username, cards[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, True)

    @patch("apps.sales.models.delete_payment_method")
    def test_card_removal_staff(self, _mock_execute):
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        cards = [
            CreditCardTokenFactory(user=user, stripe_token=f"{i}") for i in range(4)
        ]
        self.assertEqual(cards[0].active, True)
        self.assertEqual(cards[2].active, True)
        response = self.client.delete(
            "/api/sales/account/{}/cards/{}/".format(user.username, cards[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, False)
        cards[0].refresh_from_db()
        self.assertEqual(cards[0].active, True)


class TestProductListPermissions(PermissionsTestCase, MethodAccessMixin):
    passes = {**MethodAccessMixin.passes}
    passes["get"] = ["user", "staff", "outsider", "anonymous"]
    passes["post"] = ["user", "staff"]
    view_class = ProductList

    def get_object(self):
        product = Mock()
        product.user = self.user
        return product


class TestProduct(APITestCase):
    def test_product_listing_managed(self):
        user = UserFactory.create()
        self.login(user)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        hidden = ProductFactory.create(user=user, hidden=True)
        ProductFactory.create(user=user, active=False)
        response = self.client.get(
            "/api/sales/account/{}/products/manage/".format(user.username)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)
        for product in products:
            self.assertIDInList(product, response.data["results"])
        self.assertIDInList(hidden, response.data["results"])

    def test_create_product(self):
        user = UserFactory.create()
        self.login(user)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            "/api/sales/account/{}/products/".format(user.username),
            {
                "description": "I will draw you a porn.",
                "file": str(asset.id),
                "name": "Pornographic refsheet",
                "revisions": 2,
                "task_weight": 2,
                "expected_turnaround": 3,
                "base_price": 2.50,
                "tags": ["a", "b", "c", "d"],
            },
            format="json",
        )
        result = response.data
        self.assertEqual(result["description"], "I will draw you a porn.")
        self.assertEqual(result["name"], "Pornographic refsheet")
        self.assertEqual(result["revisions"], 2)
        self.assertEqual(result["task_weight"], 2)
        self.assertEqual(result["expected_turnaround"], 3.00)
        self.assertCountEqual(result["tags"], ["a", "b", "c", "d"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_free(self):
        user = UserFactory.create()
        self.login(user)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            "/api/sales/account/{}/products/".format(user.username),
            {
                "description": "I will draw you a porn.",
                "file": str(asset.id),
                "name": "Pornographic refsheet",
                "revisions": 2,
                "task_weight": 2,
                "expected_turnaround": 3,
                "base_price": 0,
                "tags": ["a", "b", "c", "d"],
            },
        )
        result = response.data
        self.assertEqual(result["description"], "I will draw you a porn.")
        self.assertEqual(result["name"], "Pornographic refsheet")
        self.assertEqual(result["revisions"], 2)
        self.assertEqual(result["task_weight"], 2)
        self.assertEqual(result["expected_turnaround"], 3.00)
        self.assertEqual(result["base_price"], 0.00)
        self.assertCountEqual(result["tags"], ["a", "b", "c", "d"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @override_settings(MINIMUM_PRICE=Money("1.00", "USD"))
    @patch("apps.sales.models.stripe")
    def test_create_product_minimum_unmet(self, _mock_stripe):
        account = StripeAccountFactory.create(active=True)
        account.user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        account.user.artist_profile.escrow_enabled = True
        account.user.artist_profile.save()
        self.login(account.user)
        asset = AssetFactory.create(uploaded_by=account.user)
        response = self.client.post(
            "/api/sales/account/{}/products/".format(account.user.username),
            {
                "description": "I will draw you a porn.",
                "file": str(asset.id),
                "name": "Pornographic refsheet",
                "revisions": 2,
                "task_weight": 2,
                "expected_turnaround": 3,
                "base_price": 0.50,
                "escrow_enabled": True,
                "cascade_fees": True,
                "tags": ["a", "b", "c", "d"],
            },
        )
        result = response.data
        self.assertEqual(
            result["base_price"],
            [
                "Value too small to have shield enabled. Raise until the total is at "
                "least $\xa01.00."
            ],
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(MINIMUM_PRICE=Money("5.00", "USD"))
    @patch("apps.sales.models.stripe")
    def test_create_product_negative_fails(self, _mock_stripe):
        account = StripeAccountFactory.create(active=True)
        account.user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        account.user.artist_profile.escrow_enabled = True
        account.user.artist_profile.save()
        self.login(account.user)
        asset = AssetFactory.create(uploaded_by=account.user)
        response = self.client.post(
            "/api/sales/account/{}/products/".format(account.user.username),
            {
                "description": "I will draw you a porn.",
                "file": str(asset.id),
                "name": "Pornographic refsheet",
                "revisions": 2,
                "task_weight": 2,
                "expected_turnaround": 3,
                "base_price": -0.50,
                "escrow_enabled": True,
                "cascade_fees": True,
            },
        )
        result = response.data
        self.assertEqual(
            result["base_price"],
            ["Price cannot be negative."],
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.sales.models.stripe")
    def test_create_product_insufficient_escrow_upgrade(self, _mock_stripe):
        account = StripeAccountFactory.create(active=True)
        account.user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        account.user.artist_profile.escrow_enabled = True
        account.user.artist_profile.save()
        self.login(account.user)
        asset = AssetFactory.create(uploaded_by=account.user)
        response = self.client.post(
            "/api/sales/account/{}/products/".format(account.user.username),
            {
                "description": "I will draw you a porn.",
                "file": str(asset.id),
                "name": "Pornographic refsheet",
                "revisions": 2,
                "task_weight": 2,
                "expected_turnaround": 3,
                "base_price": 1,
                "escrow_enabled": False,
                "escrow_upgradable": True,
                "cascade_fees": True,
                "tags": ["a", "b", "c", "d"],
            },
        )
        result = response.data
        self.assertEqual(
            result["base_price"],
            [
                "Value too small to have shield upgrade available. Raise until the "
                "total is at least $\xa05.00."
            ],
        )
        self.assertEqual(
            result["escrow_enabled"],
            [
                "Cannot have shield enabled on products whose total would be less than "
                "$\xa05.00"
            ],
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(MINIMUM_PRICE=Money("1.00", "USD"))
    def test_create_product_minimum_irrelevant(self):
        user = UserFactory.create(artist_profile__escrow_enabled=False)
        self.login(user)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            "/api/sales/account/{}/products/".format(user.username),
            {
                "description": "I will draw you a porn.",
                "file": str(asset.id),
                "name": "Pornographic refsheet",
                "revisions": 2,
                "task_weight": 2,
                "expected_turnaround": 3,
                "base_price": 0.50,
                "tags": ["a", "b", "c", "d"],
            },
        )
        result = response.data
        self.assertEqual(result["base_price"], 0.50)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_not_logged_in(self):
        user = UserFactory.create()
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            "/api/sales/account/{}/products/".format(user.username),
            {
                "description": "I will draw you a porn.",
                "file": str(asset.id),
                "name": "Pornographic refsheet",
                "revisions": 2,
                "task_weight": 2,
                "expected_turnaround": 3,
                "base_price": 2.50,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_outsider(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        asset = AssetFactory.create(uploaded_by=user)
        self.login(user2)
        response = self.client.post(
            "/api/sales/account/{}/products/".format(user.username),
            {
                "description": "I will draw you a porn.",
                "file": str(asset.id),
                "name": "Pornographic refsheet",
                "revisions": 2,
                "task_weight": 2,
                "expected_turnaround": 3,
                "base_price": 2.50,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_staff(self):
        staffer = UserFactory.create(is_staff=True)
        user = UserFactory.create()
        asset = AssetFactory.create(uploaded_by=staffer)
        self.login(staffer)
        response = self.client.post(
            "/api/sales/account/{}/products/".format(user.username),
            {
                "description": "I will draw you a porn.",
                "file": str(asset.id),
                "name": "Pornographic refsheet",
                "revisions": 2,
                "task_weight": 2,
                "expected_turnaround": 3,
                "base_price": 2.50,
                "tags": ["a", "b", "c", "d"],
            },
        )
        result = response.data
        self.assertEqual(result["description"], "I will draw you a porn.")
        self.assertEqual(result["name"], "Pornographic refsheet")
        self.assertEqual(result["revisions"], 2)
        self.assertEqual(result["task_weight"], 2)
        self.assertEqual(result["expected_turnaround"], 3.00)
        self.assertEqual(result["base_price"], 2.50)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_product_listing_not_logged_in(self):
        user = UserFactory.create()
        products = [ProductFactory.create(user=user) for __ in range(3)]
        ProductFactory.create(user=user, hidden=True)
        ProductFactory.create(user=user, active=False)
        response = self.client.get(
            "/api/sales/account/{}/products/manage/".format(user.username)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)
        for product in products:
            self.assertIDInList(product, response.data["results"])

    def test_product_listing_other_user(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        ProductFactory.create(user=user, hidden=True)
        ProductFactory.create(user=user, active=False)
        response = self.client.get(
            "/api/sales/account/{}/products/manage/".format(user.username)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)
        for product in products:
            self.assertIDInList(product, response.data["results"])

    def test_product_inventory(self):
        product = ProductFactory.create(track_inventory=True)
        response = self.client.get(
            f"/api/sales/account/{product.user.username}/products/"
            f"{product.id}/inventory/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_set_product_inventory_not_logged_in(self):
        product = ProductFactory.create(track_inventory=True)
        response = self.client.patch(
            f"/api/sales/account/{product.user.username}/products/"
            f"{product.id}/inventory/",
            {"count": 3},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_set_product_inventory_wrong_user(self):
        product = ProductFactory.create(track_inventory=True)
        self.login(UserFactory.create())
        response = self.client.patch(
            f"/api/sales/account/{product.user.username}/products/"
            f"{product.id}/inventory/",
            {"count": 3},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_set_product_inventory(self):
        product = ProductFactory.create(track_inventory=True)
        self.login(product.user)
        response = self.client.patch(
            f"/api/sales/account/{product.user.username}/products/"
            f"{product.id}/inventory/",
            {"count": 3},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_product_inventory_no_tracking(self):
        product = ProductFactory.create(track_inventory=False)
        response = self.client.get(
            f"/api/sales/account/{product.user.username}/products/"
            f"{product.id}/inventory/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_product_listing_staff(self):
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        hidden = ProductFactory.create(user=user, hidden=True)
        ProductFactory.create(user=user, active=False)
        response = self.client.get(
            "/api/sales/account/{}/products/manage/".format(user.username)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)
        for product in products:
            self.assertIDInList(product, response.data["results"])
        self.assertIDInList(hidden, response.data["results"])

    def test_product_update(self):
        user = UserFactory.create()
        self.login(user)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        DeliverableFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.patch(
            "/api/sales/account/{}/products/{}/".format(user.username, products[1].id),
            {"task_weight": 100},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["available"], False)

    def test_product_delete(self):
        user = UserFactory.create()
        self.login(user)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        DeliverableFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete(
            "/api/sales/account/{}/products/{}/".format(user.username, products[1].id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.delete(
            "/api/sales/account/{}/products/{}/".format(user.username, products[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        products[1].refresh_from_db()
        self.assertFalse(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 0)

    def test_product_delete_not_logged_in(self):
        user = UserFactory.create()
        products = [ProductFactory.create(user=user) for __ in range(3)]
        DeliverableFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete(
            "/api/sales/account/{}/products/{}/".format(user.username, products[1].id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(
            "/api/sales/account/{}/products/{}/".format(user.username, products[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        products[1].refresh_from_db()
        self.assertTrue(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 1)

    def test_product_delete_outsider(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        DeliverableFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete(
            "/api/sales/account/{}/products/{}/".format(user.username, products[1].id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(
            "/api/sales/account/{}/products/{}/".format(user.username, products[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        products[1].refresh_from_db()
        self.assertTrue(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 1)

    def test_product_delete_wrong_product(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        products = [ProductFactory.create(user=user2) for __ in range(3)]
        DeliverableFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete(
            "/api/sales/account/{}/products/{}/".format(user.username, products[1].id)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete(
            "/api/sales/account/{}/products/{}/".format(user.username, products[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        products[1].refresh_from_db()
        self.assertTrue(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 1)

    def test_product_delete_staffer(self):
        staffer = UserFactory.create(is_staff=True)
        user = UserFactory.create()
        self.login(staffer)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        DeliverableFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete(
            "/api/sales/account/{}/products/{}/".format(user.username, products[1].id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.delete(
            "/api/sales/account/{}/products/{}/".format(user.username, products[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        products[1].refresh_from_db()
        self.assertFalse(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 0)

    def test_product_set_primary_submission(self):
        product = ProductFactory.create()
        submission = SubmissionFactory.create()
        submission.artists.add(product.user)
        self.login(product.user)
        response = self.client.patch(
            "/api/sales/account/{}/products/{}/".format(
                product.user.username, product.id
            ),
            {"primary_submission": submission.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["primary_submission"]["id"], submission.id)

    def test_product_set_primary_submission_fails_not_artist(self):
        product = ProductFactory.create()
        submission = SubmissionFactory.create()
        self.login(product.user)
        response = self.client.patch(
            "/api/sales/account/{}/products/{}/".format(
                product.user.username, product.id
            ),
            {"primary_submission": submission.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["primary_submission"],
            ["That submission does not exist, or you cannot use it as your sample."],
        )

    def test_product_remove_primary_submission(self):
        submission = SubmissionFactory.create()
        product = ProductFactory.create(primary_submission=submission)
        self.login(product.user)
        response = self.client.patch(
            "/api/sales/account/{}/products/{}/".format(
                product.user.username, product.id
            ),
            {"primary_submission": None},
            format="json",
        )
        self.assertIsNone(response.data["primary_submission"])
        product.refresh_from_db()
        self.assertIsNone(product.primary_submission)

    def test_product_add_tags(self):
        product = ProductFactory.create()
        self.login(product.user)
        response = self.client.patch(
            "/api/sales/account/{}/products/{}/".format(
                product.user.username, product.id
            ),
            {"tags": ["inks", "full_body", "digital", "furry"]},
            format="json",
        )
        self.assertCountEqual(
            response.data["tags"], ["inks", "full_body", "digital", "furry"]
        )
        product.refresh_from_db()
        self.assertIsNone(product.primary_submission)


class TestComment(APITestCase):
    def test_make_comment(self):
        deliverable = DeliverableFactory.create()
        self.login(deliverable.order.buyer)
        response = self.client.post(
            "/api/lib/v1/comments/sales.Deliverable/{}/".format(deliverable.id),
            {"text": "test comment"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = response.data
        self.assertEqual(comment["text"], "test comment")
        self.assertEqual(comment["user"]["username"], deliverable.order.buyer.username)
        Comment.objects.get(id=comment["id"])


class TestProductSearch(APITestCase):
    def test_query_not_logged_in(self):
        product1 = ProductFactory.create(name="Test1")
        product2 = ProductFactory.create(name="Wat product 2")
        tag = TagFactory.create(name="test")
        product2.tags.add(tag)
        product3 = ProductFactory.create(
            name="Test3",
            task_weight=5,
            user__artist_profile__load=2,
            user__artist_profile__max_load=10,
        )
        # Hidden products
        ProductFactory.create(name="TestHidden", hidden=True)
        hidden = ProductFactory.create(name="Wat2 hidden", hidden=True)
        hidden.tags.add(tag)
        ProductFactory.create(
            name="Test4 overload",
            task_weight=5,
            user__artist_profile__load=10,
            user__artist_profile__max_load=10,
        )
        maxed = ProductFactory.create(name="Test5 maxed", max_parallel=2)
        DeliverableFactory.create(product=maxed, status=IN_PROGRESS)
        DeliverableFactory.create(product=maxed, status=QUEUED)
        maxed.refresh_from_db()
        overloaded = ProductFactory.create(
            name="Test6 overloaded", task_weight=1, user__artist_profile__max_load=5
        )
        DeliverableFactory.create(
            order__seller=overloaded.user, task_weight=7, status=IN_PROGRESS
        )
        ProductFactory.create(
            name="Test commissions closed",
            user__artist_profile__commissions_closed=True,
        )
        overloaded.user.refresh_from_db()

        response = self.client.get("/api/sales/search/product/", {"q": "test"})

        self.assertIDInList(product1, response.data["results"])
        self.assertIDInList(product2, response.data["results"])
        self.assertIDInList(product3, response.data["results"])
        self.assertEqual(len(response.data["results"]), 3)

    def test_query_logged_in(self):
        user = UserFactory.create(username="Fox")
        user2 = UserFactory.create()
        product1 = ProductFactory.create(name="Test1")
        product2 = ProductFactory.create(name="Wat")
        tag = TagFactory.create(name="test")
        product2.tags.add(tag)
        product3 = ProductFactory.create(name="Test3", task_weight=5)
        # Overweighted.
        ProductFactory.create(name="Test4", task_weight=100, user=user)
        product4 = ProductFactory.create(name="Test5", max_parallel=2, user=user)
        DeliverableFactory.create(product=product4)
        DeliverableFactory.create(product=product4)
        # Product from blocked user. Shouldn't be in results.
        ProductFactory.create(name="Test Blocked", user=user2)
        user.blocking.add(user2)

        ProductFactory.create(user__artist_profile__commissions_closed=True)

        user.artist_profile.max_load = 10
        user.artist_profile.load = 2
        user.artist_profile.save()

        user = User.objects.get(username="Fox")
        self.login(user)
        response = self.client.get("/api/sales/search/product/", {"q": "test"})
        self.assertIDInList(product1, response.data["results"])
        self.assertIDInList(product2, response.data["results"])
        self.assertIDInList(product3, response.data["results"])
        self.assertIDInList(product4, response.data["results"])
        self.assertEqual(len(response.data["results"]), 4)

    def test_query_different_user(self):
        product1 = ProductFactory.create(name="Test1")
        product2 = ProductFactory.create(name="Wat")
        tag = TagFactory.create(name="test")
        product2.tags.add(tag)
        product3 = ProductFactory.create(
            name="Test3",
            task_weight=5,
            user__artist_profile__load=2,
            user__artist_profile__max_load=10,
        )
        # Hidden products
        ProductFactory.create(name="Test4", hidden=True)
        hidden = ProductFactory.create(name="Wat2", hidden=True)
        hidden.tags.add(tag)
        ProductFactory.create(
            name="Test5",
            task_weight=5,
            user__artist_profile__load=8,
            user__artist_profile__max_load=10,
        )
        overloaded = ProductFactory.create(name="Test6", max_parallel=2)
        ProductFactory.create(user__artist_profile__commissions_closed=True)
        DeliverableFactory.create(product=overloaded, status=IN_PROGRESS)
        DeliverableFactory.create(product=overloaded, status=QUEUED)

        user = UserFactory.create(username="Fox")
        self.login(user)
        response = self.client.get("/api/sales/search/product/", {"q": "test"})
        self.assertIDInList(product1, response.data["results"])
        self.assertIDInList(product2, response.data["results"])
        self.assertIDInList(product3, response.data["results"])
        self.assertEqual(len(response.data["results"]), 3)

    def test_blocked(self):
        product = ProductFactory.create(name="Test1")
        user = UserFactory.create(username="Fox")
        user.blocking.add(product.user)
        self.login(user)
        response = self.client.get("/api/sales/search/product/", {"q": "test"})
        self.assertEqual(len(response.data["results"]), 0)

    def test_personal(self):
        user = UserFactory.create(username="Fox")
        listed = ProductFactory.create(user=user, name="Test")
        listed2 = ProductFactory.create(user=user, name="Test2", hidden=True)
        listed3 = ProductFactory.create(user=user, task_weight=999, name="Test3")
        # Inactive.
        ProductFactory.create(user=user, active=False, name="Test4")
        # Wrong user.
        ProductFactory.create(name="Test5")

        self.login(user)
        response = self.client.get("/api/sales/search/product/Fox/", {"q": "test"})
        self.assertIDInList(listed, response.data["results"])
        self.assertIDInList(listed2, response.data["results"])
        self.assertIDInList(listed3, response.data["results"])
        self.assertEqual(len(response.data["results"]), 3)

    def test_price_filter(self):
        # Reduce the number of DB calls by having the same user.
        user = UserFactory.create()
        low_price = ProductFactory.create(base_price=Money("20.00", "USD"), user=user)
        mid_price = ProductFactory.create(base_price=Money("75.00", "USD"), user=user)
        high_price = ProductFactory.create(
            base_price=Money("8000.00", "USD"), user=user
        )
        response = self.client.get("/api/sales/search/product/", {"min_price": "75.00"})
        self.assertIDInList(mid_price, response.data["results"])
        self.assertIDInList(high_price, response.data["results"])
        self.assertEqual(len(response.data["results"]), 2)
        response = self.client.get("/api/sales/search/product/", {"max_price": "75.00"})
        self.assertIDInList(mid_price, response.data["results"])
        self.assertIDInList(low_price, response.data["results"])
        self.assertEqual(len(response.data["results"]), 2)
        response = self.client.get(
            "/api/sales/search/product/",
            {"max_price": "100.00", "min_price": "25.00"},
        )
        self.assertIDInList(mid_price, response.data["results"])
        self.assertEqual(len(response.data["results"]), 1)

    def test_minimum_rating(self):
        user = UserFactory.create()
        general = ProductFactory.create(max_rating=GENERAL, user=user)
        adult = ProductFactory.create(max_rating=ADULT, user=user)
        extreme = ProductFactory.create(max_rating=EXTREME, user=user)
        response = self.client.get(
            "/api/sales/search/product/", {"minimum_content_rating": GENERAL}
        )
        self.assertIDInList(general, response.data["results"])
        self.assertIDInList(adult, response.data["results"])
        self.assertIDInList(extreme, response.data["results"])
        self.assertEqual(len(response.data["results"]), 3)
        response = self.client.get(
            "/api/sales/search/product/", {"minimum_content_rating": ADULT}
        )
        self.assertIDInList(adult, response.data["results"])
        self.assertIDInList(extreme, response.data["results"])
        self.assertEqual(len(response.data["results"]), 2)
        response = self.client.get(
            "/api/sales/search/product/", {"minimum_content_rating": EXTREME}
        )
        self.assertIDInList(extreme, response.data["results"])
        self.assertEqual(len(response.data["results"]), 1)

    def test_max_turnaround(self):
        user = UserFactory.create()
        in_range = ProductFactory.create(user=user, expected_turnaround=1)
        range_bound = ProductFactory.create(user=user, expected_turnaround=2)
        # Out of range.
        ProductFactory.create(user=user, expected_turnaround=5)
        response = self.client.get("/api/sales/search/product/", {"max_turnaround": 2})
        self.assertIDInList(in_range, response.data["results"])
        self.assertIDInList(range_bound, response.data["results"])
        self.assertEqual(len(response.data["results"]), 2)

    def test_watchlist(self):
        viewer = UserFactory.create()
        staff = UserFactory.create(is_staff=True)
        watched = ProductFactory.create()
        viewer.watching.add(watched.user)
        # Unwatched
        ProductFactory.create()
        response = self.client.get("/api/sales/search/product/", {"watch_list": True})
        # No difference, not logged in.
        self.assertEqual(len(response.data["results"]), 2)
        self.login(viewer)
        response = self.client.get("/api/sales/search/product/", {"watch_list": True})
        self.assertIDInList(watched, response.data["results"])
        self.assertEqual(len(response.data["results"]), 1)
        self.login(staff)
        # Now we're the staff user, who is watching no one.
        response = self.client.get("/api/sales/search/product/", {"watch_list": True})
        self.assertEqual(len(response.data["results"]), 0)
        # Staff searching as user
        response = self.client.get(
            "/api/sales/search/product/",
            {"watch_list": True, "user": viewer.username},
        )
        self.assertIDInList(watched, response.data["results"])
        self.assertEqual(len(response.data["results"]), 1)

    def test_community(self):
        lgbt = ProductFactory.create(user__artist_profile__lgbt=True)
        artist_of_color = ProductFactory.create(
            user__artist_profile__artist_of_color=True
        )
        response = self.client.get("/api/sales/search/product/", {"lgbt": True})
        self.assertIDInList(lgbt, response.data["results"])
        self.assertEqual(len(response.data["results"]), 1)
        response = self.client.get(
            "/api/sales/search/product/", {"artists_of_color": True}
        )
        self.assertIDInList(artist_of_color, response.data["results"])
        self.assertEqual(len(response.data["results"]), 1)

    def test_ordering(self):
        null_rated_mid_edited = ProductFactory.create(user__stars=None)
        Product.objects.filter(id=null_rated_mid_edited.id).update(
            edited_on=timezone.now().replace(year=2020),
        )
        low_rated_first_edited = ProductFactory.create(user__stars=1)
        Product.objects.filter(id=low_rated_first_edited.id).update(
            edited_on=timezone.now().replace(year=2022),
        )
        high_rated_last_edited = ProductFactory.create(user__stars=5)
        Product.objects.filter(id=high_rated_last_edited.id).update(
            edited_on=timezone.now().replace(year=2018),
        )
        response = self.client.get("/api/sales/search/product/")
        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual(
            ids,
            [
                low_rated_first_edited.id,
                null_rated_mid_edited.id,
                high_rated_last_edited.id,
            ],
        )
        response = self.client.get("/api/sales/search/product/", {"rating": True})
        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual(
            ids,
            [
                high_rated_last_edited.id,
                low_rated_first_edited.id,
                null_rated_mid_edited.id,
            ],
        )

    def test_featured(self):
        featured = ProductFactory.create(featured=True)
        # Non-featured
        ProductFactory.create()
        response = self.client.get("/api/sales/search/product/", {"featured": True})
        self.assertIDInList(featured, response.data["results"])

    def test_shielded(self):
        shielded = ProductFactory.create(
            user__artist_profile__bank_account_status=IN_SUPPORTED_COUNTRY,
            escrow_enabled=True,
            cascade_fees=True,
            base_price=Money("15.00", "USD"),
        )
        upgradable = ProductFactory.create(
            user__artist_profile__bank_account_status=IN_SUPPORTED_COUNTRY,
            escrow_enabled=False,
            escrow_upgradable=True,
            base_price=Money("15.00", "USD"),
        )
        # Non-shielded
        ProductFactory.create(
            user__artist_profile__bank_account_status=NO_SUPPORTED_COUNTRY
        )
        response = self.client.get("/api/sales/search/product/", {"shield_only": True})
        self.assertIDInList(shielded, response.data["results"])
        self.assertIDInList(upgradable, response.data["results"])
        self.assertEqual(len(response.data["results"]), 2)
        # Filter by shield and min_price
        response = self.client.get(
            "/api/sales/search/product/", {"shield_only": True, "min_price": "15.01"}
        )
        self.assertIDInList(upgradable, response.data["results"])
        self.assertEqual(len(response.data["results"]), 1)
        response = self.client.get(
            "/api/sales/search/product/", {"shield_only": True, "max_price": "15.01"}
        )
        self.assertIDInList(shielded, response.data["results"])
        self.assertEqual(len(response.data["results"]), 1)


class TestCancelPremium(APITestCase):
    def test_cancel(self):
        user = UserFactory.create()
        self.login(user)
        user.service_plan = self.landscape
        user.next_service_plan = self.landscape
        user.service_plan_paid_through = date(2017, 11, 18)
        user.save()
        response = self.client.post(
            f"/api/sales/account/{user.username}/cancel-premium/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertFalse(user.landscape_enabled)
        self.assertEqual(user.landscape_paid_through, date(2017, 11, 18))


class TestCreateInvoice(APITestCase):
    def test_create_invoice_no_bank_configured(self):
        user = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = UNSET
        user.artist_profile.save()
        response = self.client.post(
            f"/api/sales/account/{user.username}/create-invoice/", {}
        )
        self.assertIn(
            "You must have your banking settings configured", response.data["detail"]
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_invoice_no_orders_left(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        # Existing deliverable
        DeliverableFactory.create(order__buyer=user2, order__seller=user)
        self.login(user)
        user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        user.artist_profile.save()
        response = self.client.post(
            f"/api/sales/account/{user.username}/create-invoice/", {}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Your current service plan does not", response.data["detail"])
        self.free.max_simultaneous_orders = 0
        self.free.save()
        response = self.client.post(
            f"/api/sales/account/{user.username}/create-invoice/", {}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        user.artist_profile.save()
        response = self.client.post(
            f"/api/sales/account/{user.username}/create-invoice/",
            {
                "buyer": user2.username,
                "details": "wat",
                "rating": ADULT,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=response.data["order"]["id"])
        self.assertEqual(order.seller, user)
        self.assertEqual(order.buyer, user2)
        self.assertEqual(response.data["status"], NEW)
        self.assertEqual(response.data["details"], "wat")
        self.assertEqual(order.private, False)
        self.assertEqual(response.data["expected_turnaround"], 5)
        self.assertEqual(response.data["adjustment_task_weight"], 0)
        self.assertEqual(response.data["adjustment_expected_turnaround"], 0)
        self.assertEqual(response.data["adjustment_revisions"], 0)
        self.assertTrue(response.data["revisions_hidden"])
        self.assertTrue(response.data["escrow_enabled"])

        deliverable = Deliverable.objects.get(id=response.data["id"])
        self.assertEqual(deliverable.created_by, user)
        self.assertEqual(deliverable.invoice.status, DRAFT)
        item = deliverable.invoice.line_items.get(type=BASE_PRICE)
        self.assertEqual(item.amount, Money("50.00", "USD"))
        self.assertEqual(item.priority, 0)
        self.assertEqual(item.destination_user, order.seller)
        self.assertEqual(item.destination_account, ESCROW)
        self.assertEqual(item.percentage, 0)
        self.assertIsNone(order.claim_token)
        self.assertFalse(deliverable.invoice.record_only)

    def test_create_invoice_email(self):
        user = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        user.artist_profile.save()
        response = self.client.post(
            f"/api/sales/account/{user.username}/create-invoice/",
            {
                "buyer": "test@example.com",
                "details": "oh",
                "rating": ADULT,
                "hide_details": True,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=response.data["order"]["id"])
        self.assertEqual(order.seller, user)
        self.assertIsNone(order.buyer)
        self.assertEqual(response.data["rating"], ADULT)
        self.assertTrue(response.data["escrow_enabled"])
        self.assertEqual(order.customer_email, "test@example.com")
        self.assertTrue(order.claim_token)

    def test_create_invoice_email_exists(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        user.artist_profile.save()
        product = ProductFactory.create(
            user=user,
            base_price=Money("3.00", "USD"),
            task_weight=5,
            expected_turnaround=2,
            revisions=1,
        )
        response = self.client.post(
            f"/api/sales/account/{user.username}/create-invoice/",
            {
                "completed": False,
                "product": product.id,
                "buyer": user2.email,
                "details": "oh",
                "rating": ADULT,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=response.data["order"]["id"])
        self.assertEqual(order.seller, user)
        self.assertEqual(order.buyer, user2)
        self.assertTrue(response.data["escrow_enabled"])
        self.assertEqual(order.customer_email, "")
        self.assertIsNone(order.claim_token)

    def test_create_invoice_no_buyer(self):
        user = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        user.artist_profile.save()
        response = self.client.post(
            f"/api/sales/account/{user.username}/create-invoice/",
            {
                "completed": False,
                "buyer": "",
                "details": "oh",
                "rating": ADULT,
                "hide_details": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=response.data["order"]["id"])
        self.assertEqual(order.seller, user)
        self.assertIsNone(order.buyer)
        self.assertEqual(response.data["adjustment_task_weight"], 0)
        self.assertEqual(response.data["adjustment_expected_turnaround"], 0)
        self.assertEqual(response.data["adjustment_revisions"], 0)
        self.assertTrue(response.data["escrow_enabled"])
        self.assertEqual(order.customer_email, "")

    def test_create_invoice_self_send_fails(self):
        user = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        user.artist_profile.save()
        response = self.client.post(
            f"/api/sales/account/{user.username}/create-invoice/",
            {
                "buyer": user.email,
                "details": "oh",
                "rating": ADULT,
                "hide_details": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["buyer"], ["You cannot send yourself an invoice."]
        )

    def test_create_invoice_blocking_by_email(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        user2.blocking.add(user)
        self.login(user)
        user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        user.artist_profile.save()
        response = self.client.post(
            f"/api/sales/account/{user.username}/create-invoice/",
            {
                "buyer": user2.email,
                "details": "oh",
                "rating": ADULT,
                "hide_details": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["buyer"],
            ["Cannot send an invoice to this user. They may be blocking you."],
        )

    def test_create_invoice_blocking_by_username(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        user2.blocking.add(user)
        self.login(user)
        user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        user.artist_profile.save()
        response = self.client.post(
            f"/api/sales/account/{user.username}/create-invoice/",
            {
                "buyer": user2.username,
                "details": "oh",
                "rating": ADULT,
                "hide_details": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["buyer"],
            ["User with that username not found, or they are blocking you."],
        )

    def test_create_invoice_escrow_disabled(self):
        user = UserFactory.create(artist_mode=True)
        user2 = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = NO_SUPPORTED_COUNTRY
        user.artist_profile.save()
        response = self.client.post(
            f"/api/sales/account/{user.username}/create-invoice/",
            {
                "buyer": user2.username,
                "details": "bla bla",
                "rating": ADULT,
                "hide_details": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=response.data["order"]["id"])
        self.assertEqual(order.seller, user)
        self.assertEqual(order.buyer, user2)
        self.assertEqual(response.data["adjustment_task_weight"], 0)
        self.assertEqual(response.data["details"], "bla bla")
        self.assertEqual(response.data["adjustment_expected_turnaround"], 0)
        self.assertEqual(response.data["adjustment_revisions"], 0)
        self.assertFalse(response.data["escrow_enabled"])
        self.assertIsNone(order.claim_token)


class TestLists(APITestCase):
    def test_new_products(self):
        user = UserFactory.create()
        product = ProductFactory.create(user=user)
        response = self.client.get("/api/sales/new-products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], product.id)

    def test_who_is_open(self):
        user = UserFactory.create()
        self.login(user)
        product = ProductFactory.create()
        response = self.client.get("/api/sales/who-is-open/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)
        user.watching.add(product.user)
        response = self.client.get("/api/sales/who-is-open/")
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], product.id)

    def test_rating_list(self):
        user = UserFactory.create()
        rating = RatingFactory.create(target=user)
        response = self.client.get(f"/api/sales/account/{user.username}/ratings/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], rating.id)

    def test_featured_products(self):
        ProductFactory.create(active=False, featured=True)
        active_product = ProductFactory.create(active=True, featured=True)
        ProductFactory.create(active=True, featured=True, hidden=True)
        response = self.client.get("/api/sales/featured-products/")
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIDInList(active_product, response.data["results"])


class TestSalesStats(APITestCase):
    def test_sales_stats(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.get(f"/api/sales/account/{user.username}/sales/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestPricingInfo(APITestCase):
    @override_settings(TABLE_PERCENTAGE_FEE=Decimal("69"))
    def test_pricing_info(self):
        response = self.client.get("/api/sales/pricing-info/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["table_percentage"], Decimal("69"))


class TestOrderAuth(APITestCase):
    def test_anon_to_existing_guest(self):
        order = DeliverableFactory.create(
            order__buyer=UserFactory.create(
                email="wat@localhost",
                guest_email="test@example.com",
                guest=True,
                username="__3",
            )
        ).order
        response = self.client.post(
            "/api/sales/order-auth/",
            {
                "claim_token": order.claim_token,
                "id": order.id,
                "chown": False,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], order.buyer.id)

    def test_anon_to_new_guest(self):
        order = DeliverableFactory.create(
            order__buyer=None, order__customer_email="test@example.com"
        ).order
        response = self.client.post(
            "/api/sales/order-auth/",
            {
                "claim_token": order.claim_token,
                "id": order.id,
                "chown": False,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["guest_email"], "test@example.com")
        self.assertEqual(response.data["email"][-9:], "localhost")
        order.refresh_from_db()
        self.assertEqual(response.data["id"], order.buyer.id)

    def test_anon_chown_attempt(self):
        order = DeliverableFactory.create(
            order__buyer=None, order__customer_email="test@example.com"
        ).order
        response = self.client.post(
            "/api/sales/order-auth/",
            {
                "claim_token": order.claim_token,
                "id": order.id,
                "chown": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_seller_chown_attempt(self):
        order = DeliverableFactory.create(
            order__buyer=None, order__customer_email="test@example.com"
        ).order
        self.login(order.seller)
        response = self.client.post(
            "/api/sales/order-auth/",
            {
                "claim_token": order.claim_token,
                "id": order.id,
                "chown": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_chown_no_guest(self):
        order = DeliverableFactory.create(
            order__buyer=None, order__customer_email="test@example.com"
        ).order
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            "/api/sales/order-auth/",
            {
                "claim_token": order.claim_token,
                "id": order.id,
                "chown": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.buyer, user)
        self.assertEqual(order.deliverables.first().invoice.bill_to, user)
        self.assertIsNone(order.claim_token)
        self.assertEqual(order.customer_email, "")

    def test_order_already_claimed(self):
        order = DeliverableFactory.create().order
        response = self.client.post(
            "/api/sales/order-auth/",
            {
                "claim_token": "97uh97",
                "id": order.id,
                "chown": False,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_guest_revisiting(self):
        order = DeliverableFactory.create(
            order__buyer=UserFactory.create(
                email="wat@localhost",
                guest_email="test@example.com",
                guest=True,
                username="__3",
            )
        ).order
        self.login(order.buyer)
        response = self.client.post(
            "/api/sales/order-auth/",
            {
                "claim_token": "97uh97",
                "id": order.id,
                "chown": False,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "__3")

    def test_invalid_token(self):
        order = DeliverableFactory.create(
            order__buyer=UserFactory.create(
                email="wat@localhost",
                guest_email="test@example.com",
                guest=True,
                username="__3",
            )
        ).order
        response = self.client.post(
            "/api/sales/order-auth/",
            {
                "claim_token": "97uh97",
                "id": order.id,
                "chown": False,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestOrderManager(APITestCase):
    def test_view_order(self):
        deliverable = DeliverableFactory.create()
        self.login(deliverable.order.seller)
        response = self.client.get(f"/api/sales/order/{deliverable.order.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], deliverable.order.id)

    def test_update_order_hide_details(self):
        deliverable = DeliverableFactory.create()
        self.login(deliverable.order.seller)
        response = self.client.get(f"/api/sales/order/{deliverable.order.id}/")
        self.assertFalse(response.data["hide_details"])
        response = self.client.patch(
            f"/api/sales/order/{deliverable.order.id}/",
            {"hide_details": True},
        )
        self.assertTrue(response.data["hide_details"])


class TestOrderOutputs(APITestCase):
    def test_order_outputs_get(self):
        deliverable = DeliverableFactory.create(status=COMPLETED)
        self.login(deliverable.order.buyer)
        revision = RevisionFactory.create()
        submission = SubmissionFactory.create(
            deliverable=deliverable, revision=revision
        )
        response = self.client.get(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/outputs/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIDInList(submission, response.data)

    def test_order_outputs_post(self):
        deliverable = DeliverableFactory.create(status=COMPLETED, final_uploaded=True)
        RevisionFactory.create(deliverable=deliverable)
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/outputs/",
            {
                "caption": "Stuff",
                "tags": ["Things", "wat", "do", "now", "stuff"],
                "title": "Hi!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(deliverable.outputs.all().count(), 1)
        output = deliverable.outputs.all()[0]
        self.assertEqual(output.deliverable, deliverable)
        self.assertIn(deliverable.order.seller, output.artists.all())
        tag = ArtistTag.objects.get(user=deliverable.order.seller, submission=output)
        self.assertFalse(tag.hidden)

    def test_order_outputs_post_specific_revision(self):
        product = ProductFactory.create()
        deliverable = DeliverableFactory.create(
            status=COMPLETED, final_uploaded=True, product=product
        )
        revision_1 = RevisionFactory.create(
            deliverable=deliverable, created_on=timezone.now() - relativedelta(days=1)
        )
        RevisionFactory.create(deliverable=deliverable)
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/outputs/",
            {
                "caption": "Stuff",
                "tags": ["Things", "wat", "do", "then", "so"],
                "revision": revision_1.id,
                "title": "Hi!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(deliverable.outputs.all().count(), 1)
        output = deliverable.outputs.all()[0]
        self.assertEqual(output.deliverable, deliverable)
        self.assertEqual(output.revision, revision_1)
        self.assertNotIn(output, product.samples.all())

    def test_order_outputs_post_specific_revision_wrong_deliverable(self):
        product = ProductFactory.create()
        deliverable = DeliverableFactory.create(
            status=COMPLETED, final_uploaded=True, product=product
        )
        revision = RevisionFactory.create()
        RevisionFactory.create(deliverable=deliverable)
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/outputs/",
            {
                "caption": "Stuff",
                "tags": ["Things", "wat", "do", "then", "so"],
                "revision": revision.id,
                "title": "Hi!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {"revision": "The provided revision does not belong to this deliverable."},
        )

    def test_order_outputs_post_hidden_details_buyer(self):
        deliverable = DeliverableFactory.create(
            status=COMPLETED, final_uploaded=True, order__hide_details=True
        )
        RevisionFactory.create(deliverable=deliverable)
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/outputs/",
            {
                "caption": "Stuff",
                "tags": ["Things", "wat", "do", "then", "so"],
                "title": "Hi!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        output = deliverable.outputs.all()[0]
        tag = ArtistTag.objects.get(user=deliverable.order.seller, submission=output)
        self.assertTrue(tag.hidden)

    def test_order_outputs_post_hidden_details_seller(self):
        deliverable = DeliverableFactory.create(
            status=COMPLETED, final_uploaded=True, order__hide_details=True
        )
        RevisionFactory.create(deliverable=deliverable)
        self.login(deliverable.order.seller)
        response = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/outputs/",
            {
                "caption": "Stuff",
                "tags": ["Things", "wat", "do", "then", "so"],
                "title": "Hi!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        output = deliverable.outputs.all()[0]
        tag = ArtistTag.objects.get(user=deliverable.order.seller, submission=output)
        self.assertFalse(tag.hidden)

    def test_order_outputs_no_revisions(self):
        deliverable = DeliverableFactory.create(
            status=COMPLETED, final_uploaded=False, order__hide_details=True
        )
        self.login(deliverable.order.seller)
        response = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/outputs/",
            {
                "caption": "Stuff",
                "tags": ["Things", "wat", "do", "then", "so"],
                "title": "Hi!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "detail": "You can not create a submission from an order with no "
                "revisions."
            },
        )

    def test_order_outputs_incomplete_non_specific(self):
        deliverable = DeliverableFactory.create(
            status=IN_PROGRESS, final_uploaded=False, order__hide_details=True
        )
        RevisionFactory.create(deliverable=deliverable)
        RevisionFactory.create(deliverable=deliverable)
        self.login(deliverable.order.seller)
        response = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/outputs/",
            {
                "caption": "Stuff",
                "tags": ["Things", "wat", "do", "then", "so"],
                "title": "Hi!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "detail": "You must specify a specific revision if the order is not "
                "completed."
            },
        )

    def test_order_outputs_post_nonspecific_revision_buyer(self):
        product = ProductFactory.create()
        deliverable = DeliverableFactory.create(
            status=COMPLETED, final_uploaded=True, product=product
        )
        character = CharacterFactory.create(
            primary_submission=None, user=deliverable.order.buyer
        )
        deliverable.characters.add(character)
        RevisionFactory.create(
            deliverable=deliverable, created_on=timezone.now() - relativedelta(days=1)
        )
        revision_2 = RevisionFactory.create(deliverable=deliverable)
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/outputs/",
            {
                "caption": "Stuff",
                "tags": ["Things", "wat", "do", "so", "then"],
                "title": "Hi!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(deliverable.outputs.all().count(), 1)
        output = deliverable.outputs.all()[0]
        self.assertEqual(output.deliverable, deliverable)
        self.assertEqual(output.revision, revision_2)
        product.refresh_from_db()
        self.assertNotIn(output, product.samples.all())
        character.refresh_from_db()
        self.assertEqual(output, character.primary_submission)

    def test_order_outputs_post_nonspecific_revision_seller(self):
        product = ProductFactory.create()
        deliverable = DeliverableFactory.create(
            status=COMPLETED, final_uploaded=True, product=product
        )
        character = CharacterFactory.create(
            primary_submission=None, user=deliverable.order.buyer
        )
        deliverable.characters.add(character)
        RevisionFactory.create(
            deliverable=deliverable, created_on=timezone.now() - relativedelta(days=1)
        )
        revision_2 = RevisionFactory.create(deliverable=deliverable)
        self.login(deliverable.order.seller)
        response = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/outputs/",
            {
                "caption": "Stuff",
                "tags": ["Things", "wat", "do", "so", "then"],
                "title": "Hi!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(deliverable.outputs.all().count(), 1)
        output = deliverable.outputs.all()[0]
        self.assertEqual(output.deliverable, deliverable)
        self.assertEqual(output.revision, revision_2)
        product.refresh_from_db()
        self.assertIn(output, product.samples.all())
        character.refresh_from_db()
        self.assertIsNone(character.primary_submission)

    def test_order_output_exists(self):
        deliverable = DeliverableFactory.create(status=COMPLETED)
        self.login(deliverable.order.buyer)
        revision = RevisionFactory.create(deliverable=deliverable)
        SubmissionFactory.create(
            deliverable=deliverable, owner=deliverable.order.buyer, revision=revision
        )
        response = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/outputs/",
            {
                "caption": "Stuff",
                "tags": ["Things", "wat", "do", "so", "then"],
                "title": "Hi!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(deliverable.outputs.all().count(), 1)


class TestOrderInvite(APITestCase):
    def test_order_invite_no_buyer(self):
        deliverable = DeliverableFactory.create(
            order__buyer=None, order__customer_email="test@example.com"
        )
        self.login(deliverable.order.seller)
        request = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/invite/"
        )
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(
            mail.outbox[0].subject,
            f"You have a new invoice from {deliverable.order.seller.username}!",
        )
        self.assertIn("This artist should", mail.outbox[0].body)

    def test_order_invite_buyer_not_guest(self):
        deliverable = DeliverableFactory.create(
            order__customer_email="test@example.com"
        )
        self.login(deliverable.order.seller)
        request = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/invite/"
        )
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)

    def test_order_invite_buyer_guest(self):
        deliverable = DeliverableFactory.create(
            order__buyer__guest=True,
            order__buyer__guest_email="test@wat.com",
        )
        self.login(deliverable.order.seller)
        deliverable.order.customer_email = "test@example.com"
        deliverable.order.save()
        request = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/invite/"
        )
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(
            mail.outbox[0].subject, f"Claim Link for order #{deliverable.order.id}."
        )
        self.assertIn("resend your claim link", mail.outbox[0].body)
        deliverable.order.refresh_from_db()
        self.assertEqual(deliverable.order.buyer.guest_email, "test@example.com")

    def test_order_invite_email_not_set(self):
        deliverable = DeliverableFactory.create(
            order__buyer=None, order__customer_email=""
        )
        self.login(deliverable.order.seller)
        request = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/invite/"
        )
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)


class TestReferences(APITestCase):
    def test_upload_reference(self):
        deliverable = DeliverableFactory.create()
        asset = AssetFactory.create(uploaded_by=deliverable.order.seller)
        self.login(deliverable.order.seller)
        response = self.client.post(
            "/api/sales/references/",
            {
                "file": asset.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_upload_reference_unauthenticated(self):
        deliverable = DeliverableFactory.create()
        asset = AssetFactory.create(uploaded_by=deliverable.order.seller)
        response = self.client.post(
            "/api/sales/references/",
            {
                "file": asset.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_attach_reference(self):
        deliverable = DeliverableFactory.create(arbitrator=UserFactory.create())
        reference = ReferenceFactory.create(owner=deliverable.order.seller)
        self.login(deliverable.order.seller)
        response = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/references/",
            {"reference_id": reference.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        Subscription.objects.get(
            type=COMMENT,
            subscriber=deliverable.order.buyer,
            content_type=ContentType.objects.get_for_model(reference),
            object_id=response.data["reference"]["id"],
        )
        Subscription.objects.get(
            type=COMMENT,
            subscriber=deliverable.order.seller,
            content_type=ContentType.objects.get_for_model(reference),
            object_id=response.data["reference"]["id"],
        )
        Subscription.objects.get(
            type=COMMENT,
            subscriber=deliverable.arbitrator,
            content_type=ContentType.objects.get_for_model(reference),
            object_id=response.data["reference"]["id"],
        )

    def test_attach_unpermitted_reference(self):
        deliverable = DeliverableFactory.create(arbitrator=UserFactory.create())
        reference = ReferenceFactory.create()
        self.login(deliverable.order.seller)
        response = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/references/",
            {"reference_id": reference.id},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["reference_id"],
            ["Either this reference does not exist, or you are not allowed to use it."],
        )

    def test_list_references(self):
        deliverable = DeliverableFactory.create()
        deliverable.reference_set.add(
            ReferenceFactory.create(),
            ReferenceFactory.create(),
            ReferenceFactory.create(),
        )
        self.login(deliverable.order.buyer)
        response = self.client.get(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/references/",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        # Should be unpaginated.
        self.assertNotIn("results", response.data)

    def test_add_comment(self):
        deliverable = DeliverableFactory.create()
        reference = ReferenceFactory.create(owner=deliverable.order.buyer)
        deliverable.reference_set.add(reference)
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/lib/v1/comments/sales.Reference/{reference.id}/",
            {"text": "This is a comment"},
        )
        self.assertEqual(response.data["text"], "This is a comment")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comment_not_permitted(self):
        deliverable = DeliverableFactory.create()
        reference = ReferenceFactory.create(owner=deliverable.order.buyer)
        deliverable.reference_set.add(reference)
        self.login(UserFactory.create(is_staff=False))
        response = self.client.post(
            f"/api/lib/v1/comments/sales.Reference/{reference.id}/",
            {"text": "This is a comment"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestOrderDeliverables(APITestCase):
    def test_list_deliverables(self):
        deliverable1 = DeliverableFactory.create()
        deliverable2 = DeliverableFactory.create(order=deliverable1.order)
        # Unrelated deliverable
        DeliverableFactory.create()
        self.login(deliverable1.order.seller)
        response = self.client.get(
            f"/api/sales/order/{deliverable1.order.id}/deliverables/"
        )
        self.assertCountEqual(
            [entry["id"] for entry in response.data["results"]],
            [deliverable1.id, deliverable2.id],
        )

    def test_create_deliverable(self):
        old_deliverable = DeliverableFactory.create(
            order__seller__artist_profile__bank_account_status=IN_SUPPORTED_COUNTRY,
            order__seller__service_plan=self.landscape,
            order__seller__service_plan_paid_through=(
                timezone.now() + relativedelta(days=5)
            ).date(),
        )
        product = ProductFactory.create(
            expected_turnaround=2,
            task_weight=5,
            revisions=1,
            base_price=Money("3.00", "USD"),
            user=old_deliverable.order.seller,
        )
        self.login(old_deliverable.order.seller)
        response = self.client.post(
            f"/api/sales/order/{old_deliverable.order.id}/deliverables/",
            {
                "name": "Boop",
                "completed": False,
                "price": "5.00",
                "details": "wat",
                "task_weight": 3,
                "revisions": 3,
                "product": product.id,
                "rating": ADULT,
                "expected_turnaround": 4,
                "hold": False,
                "paid": False,
            },
        )
        deliverable = Deliverable.objects.get(id=response.data["id"])
        order = deliverable.order
        self.assertEqual(response.data["status"], PAYMENT_PENDING)
        self.assertEqual(response.data["details"], "wat")
        self.assertEqual(order.private, False)
        self.assertEqual(response.data["adjustment_task_weight"], -2)
        self.assertEqual(response.data["adjustment_expected_turnaround"], 2.00)
        self.assertEqual(response.data["rating"], ADULT)
        self.assertEqual(response.data["adjustment_revisions"], 2)
        self.assertTrue(response.data["revisions_hidden"])
        self.assertTrue(response.data["escrow_enabled"])
        self.assertEqual(response.data["product"]["id"], product.id)

        deliverable = Deliverable.objects.get(id=response.data["id"])
        item = deliverable.invoice.line_items.get(type=ADD_ON)
        self.assertEqual(item.amount, Money("2.00", "USD"))
        self.assertEqual(item.priority, 100)
        self.assertEqual(item.destination_user, order.seller)
        self.assertEqual(item.destination_account, ESCROW)
        self.assertEqual(item.percentage, 0)
        item = deliverable.invoice.line_items.get(type=BASE_PRICE)
        self.assertEqual(item.amount, Money("3.00", "USD"))
        self.assertEqual(item.priority, 0)
        self.assertEqual(item.destination_user, order.seller)
        self.assertEqual(item.destination_account, ESCROW)
        self.assertEqual(item.percentage, 0)
        self.assertIsNone(order.claim_token)
        self.assertFalse(deliverable.invoice.record_only)

    def test_create_deliverable_with_references(self):
        old_deliverable = DeliverableFactory.create(
            order__seller__artist_profile__bank_account_status=IN_SUPPORTED_COUNTRY,
            order__seller__service_plan=self.landscape,
            order__seller__service_plan_paid_through=(
                timezone.now() + relativedelta(days=5)
            ).date(),
        )
        reference = ReferenceFactory.create()
        reference.deliverables.add(old_deliverable)
        self.login(old_deliverable.order.seller)
        response = self.client.post(
            f"/api/sales/order/{old_deliverable.order.id}/deliverables/",
            {
                "name": "Boop",
                "completed": False,
                "product": None,
                "price": "5.00",
                "details": "wat",
                "task_weight": 3,
                "revisions": 3,
                "rating": ADULT,
                "expected_turnaround": 4,
                "hold": False,
                "paid": False,
                "references": [reference.id],
            },
            format="json",
        )
        deliverable = Deliverable.objects.get(id=response.data["id"])
        # Should not throw.
        Reference.objects.get(deliverables=deliverable)

    def test_create_deliverable_non_landscape(self):
        old_deliverable = DeliverableFactory.create(
            product__expected_turnaround=2,
            product__task_weight=5,
            product__revisions=1,
            product__base_price=Money("3.00", "USD"),
            product__user__artist_profile__bank_account_status=IN_SUPPORTED_COUNTRY,
            product__user__service_plan_paid_through=timezone.now()
            - relativedelta(days=5),
            product__user__service_plan=self.landscape,
        )
        self.login(old_deliverable.order.seller)
        response = self.client.post(
            f"/api/sales/order/{old_deliverable.order.id}/deliverables/",
            {
                "name": "Boop",
                "completed": False,
                "price": "5.00",
                "details": "wat",
                "task_weight": 3,
                "rating": ADULT,
                "revisions": 3,
                "expected_turnaround": 4,
                "hold": False,
                "paid": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_deliverable_buyer_fail(self):
        old_deliverable = DeliverableFactory.create(
            product__expected_turnaround=2,
            product__task_weight=5,
            product__revisions=1,
            product__base_price=Money("3.00", "USD"),
            product__user__artist_profile__bank_account_status=IN_SUPPORTED_COUNTRY,
            product__user__landscape_paid_through=timezone.now()
            + relativedelta(days=5),
        )
        self.login(old_deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/order/{old_deliverable.order.id}/deliverables/",
            {
                "name": "Boop",
                "completed": False,
                "price": "5.00",
                "details": "wat",
                "task_weight": 3,
                "revisions": 3,
                "rating": ADULT,
                "expected_turnaround": 4,
                "hold": False,
                "paid": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestBroadcast(APITestCase):
    def test_no_orders(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            f"/api/sales/account/{user.username}/broadcast/",
            {"text": "Boop", "include_waitlist": True, "include_active": True},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["detail"], "You have no matching orders to broadcast to."
        )

    def test_no_category(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            f"/api/sales/account/{user.username}/broadcast/",
            {"text": "Boop", "include_active": False, "include_waitlist": False},
            format="json",
        )
        self.assertEqual(
            response.data["detail"],
            "You must select at least one category of orders to broadcast to.",
        )

    def test_broadcast_to_active(self):
        deliverable = DeliverableFactory.create()
        self.login(deliverable.order.seller)
        deliverable2 = DeliverableFactory.create(order=deliverable.order)
        deliverable3 = DeliverableFactory.create(order__seller=deliverable.order.seller)
        deliverable4 = DeliverableFactory.create()
        deliverable5 = DeliverableFactory(
            order__seller=deliverable.order.seller, status=WAITING
        )
        response = self.client.post(
            f"/api/sales/account/{deliverable.order.seller.username}/broadcast/",
            {"text": "Boop", "include_active": True, "include_waitlist": False},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            deliverable.comments.all().count() + deliverable2.comments.all().count(), 1
        )
        self.assertEqual(deliverable3.comments.all().count(), 1)
        comment = deliverable3.comments.all()[0]
        self.assertEqual(comment.text, "Boop")
        self.assertEqual(comment.user, deliverable3.order.seller)
        self.assertEqual(deliverable4.comments.all().count(), 0)
        self.assertEqual(deliverable5.comments.all().count(), 0)

    def test_broadcast_to_waiting(self):
        deliverable = DeliverableFactory.create()
        self.login(deliverable.order.seller)
        DeliverableFactory.create(order=deliverable.order)
        DeliverableFactory.create(order__seller=deliverable.order.seller)
        DeliverableFactory.create()
        deliverable5 = DeliverableFactory(
            order__seller=deliverable.order.seller, status=WAITING
        )
        DeliverableFactory.create(status=WAITING)
        response = self.client.post(
            f"/api/sales/account/{deliverable.order.seller.username}/broadcast/",
            {"text": "Boop", "include_active": False, "include_waitlist": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(deliverable5.comments.all().count(), 1)


class TestClearWaitlist(APITestCase):
    def test_clear_waitlist(self):
        deliverable = DeliverableFactory.create(status=WAITING)
        deliverable2 = DeliverableFactory.create(
            status=WAITING, product=deliverable.product
        )
        deliverable3 = DeliverableFactory.create(
            order__seller=deliverable.order.seller, status=WAITING
        )
        deliverable4 = DeliverableFactory.create(
            order__seller=deliverable.order.seller,
            product=deliverable.product,
            status=IN_PROGRESS,
        )
        deliverable5 = DeliverableFactory.create(status=COMPLETED)
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/account/{deliverable.order.buyer.username}/products/"
            f"{deliverable.product.id}/clear-waitlist/",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.post(
            f"/api/sales/account/{deliverable.product.user.username}/products/"
            f"{deliverable.product.id}/clear-waitlist/",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.login(deliverable.product.user)
        response = self.client.post(
            f"/api/sales/account/{deliverable.product.user.username}/products/"
            f"{deliverable.product.id}/clear-waitlist/",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        for item in [
            deliverable,
            deliverable2,
            deliverable3,
            deliverable4,
            deliverable5,
        ]:
            item.refresh_from_db()
        self.assertEqual(deliverable.status, CANCELLED)
        self.assertEqual(deliverable2.status, CANCELLED)
        self.assertEqual(deliverable3.status, WAITING)
        self.assertEqual(deliverable4.status, IN_PROGRESS)
        self.assertEqual(deliverable5.status, COMPLETED)


class TestQueue(APITestCase):
    def test_queue_anonymous(self):
        deliverable = DeliverableFactory.create(
            status=QUEUED,
            order__buyer__guest=True,
            order__buyer__guest_email="test@example.com",
        )
        deliverable_private = DeliverableFactory.create(
            status=QUEUED,
            order__private=True,
            order__seller=deliverable.order.seller,
        )
        deliverable_hidden = DeliverableFactory.create(
            status=QUEUED,
            order__hide_details=True,
            order__seller=deliverable.order.seller,
        )
        response = self.client.get(
            f"/api/sales/account/{deliverable.order.seller.username}/queue/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)
        first, second, third = response.data["results"]
        self.assertEqual(first, {"id": deliverable_hidden.order.id, "private": True})
        self.assertEqual(second, {"id": deliverable_private.order.id, "private": True})
        self.assertEqual(third["seller"]["username"], deliverable.order.seller.username)


class TestAnonymousInvoice(APITestCase):
    def test_invoice_created(self):
        UserFactory.create(username=settings.ANONYMOUS_USER_USERNAME)
        user = UserFactory.create(is_staff=True)
        self.login(user)
        response = self.client.post("/api/sales/create-anonymous-invoice/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fail_non_staff(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.post("/api/sales/create-anonymous-invoice/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestRecentInvoices(APITestCase):
    def test_show_recent(self):
        newest = InvoiceFactory.create(
            created_on=timezone.now().replace(year=2022, month=8, day=1),
            manually_created=True,
        )
        oldest = InvoiceFactory.create(
            created_on=timezone.now().replace(year=2020, month=8, day=1),
            manually_created=True,
        )
        middle = InvoiceFactory.create(
            created_on=timezone.now().replace(year=2021, month=8, day=1),
            manually_created=True,
        )
        self.login(UserFactory.create(is_staff=True))
        response = self.client.get("/api/sales/recent-invoices/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target_list = [newest.id, middle.id, oldest.id]
        self.assertEqual(
            target_list, [invoice["id"] for invoice in response.data["results"]]
        )

    def test_fail_non_staff(self):
        self.login(UserFactory.create())
        response = self.client.get("/api/sales/recent-invoices/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestServicePlans(APITestCase):
    def test_list_service_plans(self):
        ServicePlanFactory(name="wat", hidden=True)
        response = self.client.get("/api/sales/service-plans/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIDInList(self.free.id, response.data)
        self.assertIDInList(self.landscape.id, response.data)
        self.assertEqual(len(response.data), 2)


class TestInvoiceLineItems(APITestCase):
    def test_invoice_line_items(self):
        deliverable = DeliverableFactory.create(
            product__base_price=Money("10.00", "USD")
        )
        self.login(deliverable.order.seller)
        response = self.client.get(
            f"/api/sales/invoice/{deliverable.invoice.id}/line-items/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["amount"], 10.0)

    def test_create_line_item(self):
        staff = UserFactory.create(is_staff=True)
        deliverable = DeliverableFactory.create(
            product__base_price=Money("10.00", "USD")
        )
        self.login(staff)
        response = self.client.post(
            f"/api/sales/invoice/{deliverable.invoice.id}/line-items/",
            {"description": "Stuff", "amount": 5, "percentage": 0, "type": EXTRA},
        )
        self.assertEqual(response.data["amount"], 5)

    def test_modify_base_line_item(self):
        staff = UserFactory.create(is_staff=True)
        deliverable = DeliverableFactory.create(
            product__base_price=Money("10.00", "USD")
        )
        self.login(staff)
        line_item = deliverable.invoice.line_items.get(type=BASE_PRICE)
        response = self.client.patch(
            f"/api/sales/invoice/{deliverable.invoice.id}/line-items/"
            f"{line_item.id}/",
            {"amount": 5, "percentage": 5},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        line_item.refresh_from_db()
        self.assertEqual(line_item.amount, Money("5.00", "USD"))
        # Should have ignored our request to set a percentage on the base price.
        self.assertEqual(line_item.percentage, 0)

    def test_create_line_item_wrong_type(self):
        staff = UserFactory.create(is_staff=True)
        deliverable = DeliverableFactory.create(
            product__base_price=Money("10.00", "USD")
        )
        self.login(staff)
        response = self.client.post(
            f"/api/sales/invoice/{deliverable.invoice.id}/line-items/",
            {"description": "Stuff", "amount": 5, "percentage": 0, "type": ADD_ON},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)

    def test_create_line_item_wrong_user(self):
        deliverable = DeliverableFactory.create(
            product__base_price=Money("10.00", "USD")
        )
        self.login(deliverable.order.seller)
        response = self.client.post(
            f"/api/sales/invoice/{deliverable.invoice.id}/line-items/",
            {"description": "Stuff", "amount": 5, "type": ADD_ON},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_tip_buyer(self):
        deliverable = DeliverableFactory.create(
            order__seller__service_plan=self.landscape,
            order__seller__service_plan__paid_through=timezone.now()
            + relativedelta(months=1),
            finalized_on=timezone.now(),
        )
        deliverable.invoice.status = PAID
        deliverable.invoice.save()
        deliverable.status = COMPLETED
        deliverable.save()
        invoice = initialize_tip_invoice(deliverable)
        line_item = invoice.line_items.get(type=TIP)
        self.login(deliverable.order.buyer)
        response = self.client.patch(
            f"/api/sales/invoice/{invoice.id}/line-items/{line_item.id}/",
            {
                "amount": "2.03",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        line_item.refresh_from_db()
        self.assertEqual(line_item.amount, Money("2.03", "USD"))
        self.assertEqual(line_item.destination_account, HOLDINGS)
        self.assertEqual(line_item.destination_user, deliverable.order.seller)

    @override_settings(MINIMUM_TIP=Money("1.00", "USD"))
    def test_update_tip_too_low(self):
        deliverable = DeliverableFactory.create(
            order__seller__service_plan=self.landscape,
            order__seller__service_plan__paid_through=timezone.now()
            + relativedelta(months=1),
            finalized_on=timezone.now(),
        )
        deliverable.invoice.status = PAID
        deliverable.invoice.save()
        deliverable.status = COMPLETED
        deliverable.save()
        invoice = initialize_tip_invoice(deliverable)
        line_item = invoice.line_items.get(type=TIP)
        self.login(deliverable.order.buyer)
        response = self.client.patch(
            f"/api/sales/invoice/{invoice.id}/line-items/{line_item.id}/",
            {
                "amount": ".50",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["amount"], ["Tip may not be less than $\xa01.00."]
        )

    @override_settings(MAXIMUM_TIP=Money("10.00", "USD"))
    def test_update_tip_too_high(self):
        deliverable = DeliverableFactory.create(
            order__seller__service_plan=self.landscape,
            order__seller__service_plan__paid_through=timezone.now()
            + relativedelta(months=1),
            finalized_on=timezone.now(),
        )
        deliverable.invoice.status = PAID
        deliverable.invoice.save()
        deliverable.status = COMPLETED
        deliverable.save()
        invoice = initialize_tip_invoice(deliverable)
        line_item = invoice.line_items.get(type=TIP)
        self.login(deliverable.order.buyer)
        response = self.client.patch(
            f"/api/sales/invoice/{invoice.id}/line-items/{line_item.id}/",
            {
                "amount": "12.00",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["amount"], ["Tip may not be more than $\xa010.00."]
        )


class TestLineItemManager(APITestCase):
    def test_retrieve_line_item(self):
        staff = UserFactory.create(is_staff=True)
        line_item = LineItemFactory.create(amount=Money("5.00", "USD"))
        self.login(staff)
        response = self.client.get(
            f"/api/sales/invoice/{line_item.invoice.id}/line-items/{line_item.id}/",
        )
        self.assertEqual(response.data["id"], line_item.id)


class TestReferenceManager(APITestCase):
    def test_get_reference(self):
        reference = ReferenceFactory.create()
        deliverable = DeliverableFactory.create()
        deliverable.reference_set.add(reference)
        self.login(deliverable.order.seller)
        response = self.client.get(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/references/{reference.id}/",
        )
        self.assertEqual(response.data["id"], reference.id)

    def test_delete_reference(self):
        deliverable = DeliverableFactory.create()
        reference = ReferenceFactory.create(owner=deliverable.order.seller)
        deliverable2 = DeliverableFactory.create(order__seller=deliverable.order.seller)
        deliverable.reference_set.add(reference)
        deliverable2.reference_set.add(reference)
        self.login(deliverable.order.seller)
        response = self.client.delete(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/references/{reference.id}/",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Should not throw.
        reference.refresh_from_db()

    def test_delete_reference_last_deliverable(self):
        deliverable = DeliverableFactory.create()
        reference = ReferenceFactory.create(owner=deliverable.order.seller)
        deliverable.reference_set.add(reference)
        self.login(deliverable.order.seller)
        response = self.client.delete(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/references/{reference.id}/",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Reference.DoesNotExist):
            reference.refresh_from_db()

    def test_delete_reference_not_owner(self):
        deliverable = DeliverableFactory.create()
        reference = ReferenceFactory.create(owner=deliverable.order.buyer)
        deliverable.reference_set.add(reference)
        self.login(deliverable.order.seller)
        response = self.client.delete(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/references/{reference.id}/",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestInvoicePayment(APITestCase):
    def test_pay_cash(self):
        line_item = LineItemFactory.create(invoice__status=OPEN)
        staff = UserFactory.create(is_staff=True)
        self.login(staff)
        response = self.client.post(
            f"/api/sales/invoice/{line_item.invoice.id}/pay/",
            {
                "amount": line_item.invoice.total().amount,
                "cash": True,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pay_cash_wrong_amount(self):
        line_item = LineItemFactory.create(invoice__status=OPEN)
        staff = UserFactory.create(is_staff=True)
        self.login(staff)
        response = self.client.post(
            f"/api/sales/invoice/{line_item.invoice.id}/pay/",
            {
                "amount": "12345",
                "cash": True,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestSetPlan(APITestCase):
    @freeze_time("2023-01-01")
    def test_set_next_plan_free(self):
        user = UserFactory.create(
            service_plan=self.landscape,
            next_service_plan=self.landscape,
            service_plan_paid_through=timezone.now().date(),
        )
        self.login(user)
        response = self.client.post(
            f"/api/sales/account/{user.username}/set-plan/", {"service": "Free"}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertEqual(user.service_plan, self.landscape)
        self.assertEqual(user.next_service_plan, self.free)
        self.assertEqual(user.service_plan_paid_through, timezone.now().date())

    @freeze_time("2023-01-01")
    def test_set_current_plan_free(self):
        user = UserFactory.create(
            service_plan=self.landscape,
            next_service_plan=self.landscape,
            service_plan_paid_through=timezone.now() - relativedelta(days=3),
        )
        self.login(user)
        response = self.client.post(
            f"/api/sales/account/{user.username}/set-plan/", {"service": "Free"}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertEqual(user.service_plan, self.free)
        self.assertEqual(user.next_service_plan, self.free)
        self.assertEqual(
            user.service_plan_paid_through, timezone.now().date().replace(month=2)
        )

    def test_allow_paid_noop(self):
        user = UserFactory.create(
            service_plan=self.landscape,
            next_service_plan=self.landscape,
            service_plan_paid_through=timezone.now(),
        )
        self.login(user)
        response = self.client.post(
            f"/api/sales/account/{user.username}/set-plan/", {"service": "Landscape"}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertEqual(user.service_plan, self.landscape)
        self.assertEqual(user.next_service_plan, self.landscape)

    def test_disallow_paid_upgrade(self):
        user = UserFactory.create(
            service_plan=self.free,
            next_service_plan=self.free,
            service_plan_paid_through=timezone.now(),
        )
        self.login(user)
        response = self.client.post(
            f"/api/sales/account/{user.username}/set-plan/", {"service": "Landscape"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertEqual(user.service_plan, self.free)
        self.assertEqual(user.next_service_plan, self.free)


class TestAccountStatus(APITestCase):
    def test_account_status(self):
        user = UserFactory.create()
        TransactionRecordFactory.create(
            payer=None,
            payee=user,
            destination=HOLDINGS,
            amount=Money("10.0", "USD"),
        )
        TransactionRecordFactory.create(
            payer=user,
            payee=None,
            source=HOLDINGS,
            amount=Money("2.0", "USD"),
        )
        TransactionRecordFactory.create(
            payer=user,
            payee=None,
            source=HOLDINGS,
            amount=Money("1.00", "USD"),
            status=PENDING,
        )
        self.login(user)
        response = self.client.get(
            f"/api/sales/account/{user.username}/account-status/",
            {"account": HOLDINGS},
        )
        self.assertEqual(
            response.data, {"available": 7.0, "pending": -1.0, "posted": 8.0}
        )


class TestStorePreview(APITestCase):
    def test_store_preview(self):
        submission = SubmissionFactory.create()
        product = ProductFactory.create(
            primary_submission=submission, user=submission.owner
        )
        response = self.client.get(f"/store/{product.user.username}")
        self.assertIn(product.preview_link, response.content.decode("utf-8"))

    def test_store_preview_avatar_url(self):
        submission = SubmissionFactory.create()
        product = ProductFactory.create(
            primary_submission=submission, user=submission.owner
        )
        User.objects.filter(id=submission.owner.id).update(avatar_url="/test.jpg")
        response = self.client.get(f"/store/{product.user.username}")
        self.assertIn(make_url("/test.jpg"), response.content.decode("utf-8"))


class TestProductPreview(APITestCase):
    def test_product_preview(self):
        submission = SubmissionFactory.create()
        product = ProductFactory.create(
            primary_submission=submission, user=submission.owner
        )
        response = self.client.get(
            f"/store/{product.user.username}/product/{product.id}"
        )
        self.assertIn(product.preview_link, response.content.decode("utf-8"))


class TestCommissionsStatus(APITestCase):
    """
    Tests serving of the commissions status image if the user is open for commissions.

    Note that this test will fail if collectstatic hasn't been run.
    """

    def test_commissions_open(self):
        product = ProductFactory.create()
        # Should be enabled by default.
        response = self.client.get(
            f"/api/sales/account/{product.user.username}/commissions-status-image/"
        )
        self.assertIn(b"commissions-open.png", response.serialize_headers())

    def test_commissions_closed(self):
        product = ProductFactory.create(user__artist_profile__commissions_closed=True)
        # Should be enabled by default.
        response = self.client.get(
            f"/api/sales/account/{product.user.username}/commissions-status-image/"
        )
        self.assertIn(b"commissions-closed.png", response.serialize_headers())


class TestFeatureProduct(APITestCase):
    def test_feature_product(self):
        product = ProductFactory.create()
        self.assertFalse(product.featured)
        user = UserFactory.create(is_staff=True)
        self.login(user)
        self.client.post(
            f"/api/sales/account/{product.user.username}/products/"
            f"{product.id}/feature/",
            {},
        )
        product.refresh_from_db()
        self.assertTrue(product.featured)

    def test_unfeature_product(self):
        product = ProductFactory.create(featured=True)
        self.assertTrue(product.featured)
        user = UserFactory.create(is_staff=True)
        self.login(user)
        self.client.post(
            f"/api/sales/account/{product.user.username}/products/"
            f"{product.id}/feature/",
            {},
        )
        product.refresh_from_db()
        self.assertFalse(product.featured)

    def test_feature_non_staff_fails(self):
        product = ProductFactory.create()
        self.login(product.user)
        response = self.client.post(
            f"/api/sales/account/{product.user.username}/products/"
            f"{product.id}/feature/",
            {},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestPremadeSearches(APITestCase):
    def test_lgbt(self):
        lgbt = ProductFactory.create(user__artist_profile__lgbt=True)
        # Unrelated
        ProductFactory.create()
        response = self.client.get("/api/sales/lgbt/")
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIDInList(lgbt, response.data["results"])

    def test_artists_of_color(self):
        artist_of_color = ProductFactory.create(
            user__artist_profile__artist_of_color=True
        )
        # Unrelated
        ProductFactory.create()
        response = self.client.get("/api/sales/artists-of-color/")
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIDInList(artist_of_color, response.data["results"])

    def test_highly_rated(self):
        highly_rated = ProductFactory.create(user__stars=5)
        # Not high enough
        ProductFactory.create(user__stars=3)
        # Unrated
        ProductFactory.create()
        response = self.client.get("/api/sales/highly-rated/")
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIDInList(highly_rated, response.data["results"])

    def test_new_artist(self):
        veteran = ProductFactory.create()
        DeliverableFactory.create(
            product=veteran, order__seller=veteran.user, status=COMPLETED
        )
        new_product = ProductFactory.create()
        response = self.client.get("/api/sales/new-artist-products/")
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIDInList(new_product, response.data["results"])

    def test_low_price(self):
        low_price = ProductFactory.create(base_price=Money("10.00", "USD"))
        ProductFactory.create(base_price=Money("50.00", "USD"))
        response = self.client.get("/api/sales/low-price/")
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIDInList(low_price, response.data["results"])

    def test_table_products(self):
        table_product = ProductFactory.create(table_product=True)
        ProductFactory.create()
        user = UserFactory.create(is_staff=True)
        self.login(user)
        response = self.client.get("/api/sales/table/products/")
        self.assertEqual(len(response.data), 1)
        self.assertIDInList(table_product, response.data)

    def test_random(self):
        products = tuple(ProductFactory.create().id for _ in range(5))
        id_sets = [
            tuple(
                item["id"]
                for item in self.client.get("/api/sales/random/").data["results"]
            )
            for _ in range(5)
        ]
        for id_set in id_sets:
            self.assertCountEqual(products, id_set)
        # Should be incredibly improbable for this to be true, though this test might
        # fail once in a long while.
        self.assertNotEqual(len(id_sets), 1)


class TestInvoiceStatus(APITestCase):
    def test_finalize_invoice(self):
        invoice = InvoiceFactory.create(status=DRAFT)
        user = UserFactory.create(is_staff=True)
        self.login(user)
        self.client.post(f"/api/sales/invoice/{invoice.id}/finalize/")
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, OPEN)

    def test_finalize_invoice_already_open(self):
        invoice = InvoiceFactory.create(status=OPEN)
        user = UserFactory.create(is_staff=True)
        self.login(user)
        response = self.client.post(f"/api/sales/invoice/{invoice.id}/finalize/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_void_invoice(self):
        invoice = InvoiceFactory.create(status=OPEN)
        user = UserFactory.create(is_staff=True)
        self.login(user)
        self.client.post(f"/api/sales/invoice/{invoice.id}/void/")
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, VOID)

    def test_void_invoice_wrong_status(self):
        invoice = InvoiceFactory.create(status=PAID)
        user = UserFactory.create(is_staff=True)
        self.login(user)
        response = self.client.post(f"/api/sales/invoice/{invoice.id}/void/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_finalize_invoice_tipping(self):
        invoice = InvoiceFactory.create(status=DRAFT, type=TIPPING)
        self.login(invoice.bill_to)
        self.client.post(f"/api/sales/invoice/{invoice.id}/finalize/")
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, OPEN)

    def test_finalize_invoice_tipping_wrong_user(self):
        invoice = InvoiceFactory.create(
            status=DRAFT, type=TIPPING, issued_by=UserFactory.create()
        )
        self.login(invoice.issued_by)
        response = self.client.post(f"/api/sales/invoice/{invoice.id}/finalize/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, DRAFT)


class TestInvoiceDetail(APITestCase):
    def test_invoice_detail(self):
        invoice = InvoiceFactory()
        self.login(invoice.bill_to)
        response = self.client.get(f"/api/sales/invoice/{invoice.id}/")
        self.assertEqual(response.data["id"], invoice.id)


class TestTableOrders(APITestCase):
    def test_table_orders(self):
        user = UserFactory.create(is_staff=True)
        deliverable = DeliverableFactory(table_order=True)
        # Unrelated
        DeliverableFactory.create()
        self.login(user)
        response = self.client.get("/api/sales/table/orders/")
        self.assertIDInList(deliverable.order, response.data)
        self.assertEqual(len(response.data), 1)


class TestProductRecommendations(APITestCase):
    def test_product_recommendations(self):
        product = ProductFactory.create()
        for i in range(3):
            ProductFactory.create(user=product.user)
        other_user_product = ProductFactory.create()
        response = self.client.get(
            f"/api/sales/account/{product.user.username}/products/"
            f"{product.id}/recommendations/",
        )
        id_list = [result["user"]["id"] for result in response.data["results"]]
        self.assertEqual([product.user.id] * 3 + [other_user_product.user.id], id_list)


class TestUserInvoices(APITestCase):
    def test_user_invoices(self):
        invoice = InvoiceFactory.create()
        # Subscription invoice that hasn't been realized
        InvoiceFactory.create(type=SUBSCRIPTION, status=OPEN, bill_to=invoice.bill_to)
        # Unrelated to the user
        InvoiceFactory.create()
        self.login(invoice.bill_to)
        response = self.client.get(
            f"/api/sales/account/{invoice.bill_to.username}/invoices/",
        )
        self.assertIDInList(invoice, response.data["results"])
        self.assertEqual(len(response.data["results"]), 1)

    def test_wrong_user(self):
        invoice = InvoiceFactory.create()
        # Unrelated to the user
        self.login(UserFactory.create())
        response = self.client.get(
            f"/api/sales/account/{invoice.bill_to.username}/invoices/",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestInvoiceTransactions(APITestCase):
    def test_invoice_transactions_staff(self):
        invoice = InvoiceFactory.create()
        record = TransactionRecordFactory.create()
        # Unrelated record
        TransactionRecordFactory.create()
        record.targets.add(ref_for_instance(invoice))
        self.login(UserFactory.create(is_staff=True))
        response = self.client.get(
            f"/api/sales/invoice/{invoice.id}/transaction-records/",
        )
        self.assertIDInList(record, response.data["results"])

    def test_invoice_transactions_non_staff(self):
        invoice = InvoiceFactory.create()
        record = TransactionRecordFactory.create()
        record.targets.add(ref_for_instance(invoice))
        self.login(invoice.bill_to)
        response = self.client.get(
            f"/api/sales/invoice/{invoice.id}/transaction-records/",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestIssueTipInvoice(APITestCase):
    def test_issue_tip_invoice(self):
        deliverable = DeliverableFactory.create(
            status=COMPLETED, finalized_on=timezone.now()
        )
        deliverable.order.seller.service_plan = self.landscape
        deliverable.order.seller.save()
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/issue-tip-invoice/",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_issue_tip_invoice_wrong_plan(self):
        deliverable = DeliverableFactory.create(
            status=COMPLETED, finalized_on=timezone.now()
        )
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/issue-tip-invoice/",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_issue_tip_invoice_past_due(self):
        deliverable = DeliverableFactory.create(
            status=COMPLETED, finalized_on=timezone.now() - relativedelta(months=1)
        )
        deliverable.order.seller.service_plan = self.landscape
        deliverable.order.seller.save()
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f"/api/sales/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/issue-tip-invoice/",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestQueueListing(EnsurePlansMixin, TestCase):
    def test_load_listing(self):
        user = UserFactory.create()
        not_included = [
            DeliverableFactory.create(
                status=COMPLETED,
                order__seller=user,
            ),
            DeliverableFactory.create(
                status=IN_PROGRESS,
            ),
        ]
        included = [
            DeliverableFactory.create(status=IN_PROGRESS, order__seller=user),
            DeliverableFactory.create(status=QUEUED, order__seller=user),
            DeliverableFactory.create(
                status=QUEUED, order__seller=user, order__buyer__guest=True
            ),
        ]
        result = self.client.get(f"/store/{user.username}/queue-listing/")
        content = result.content.decode("utf-8")
        for item in included:
            self.assertIn(f"order__{item.order.id}", content)
        for item in not_included:
            self.assertNotIn(f"order__{item.order.id}", content)
        guest_deliverable = included[-1]
        self.assertIn(f"Guest #{guest_deliverable.order.buyer.id}", content)


@patch("apps.sales.views.main.paypal_api")
class TestPaypalSettings(APITestCase):
    def test_get_settings(self, _mock_paypal):
        config = PaypalConfigFactory.create()
        self.login(config.user)
        resp = self.client.get(f"/api/sales/account/{config.user.username}/paypal/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(config.template_id, resp.data["template_id"])
        self.assertTrue(resp.data["active"])
        self.assertNotIn("key", resp.data)
        self.assertNotIn("secret", resp.data)

    def test_patch_template(self, _mock_paypal):
        config = PaypalConfigFactory.create()
        self.login(config.user)
        resp = self.client.patch(
            f"/api/sales/account/{config.user.username}/paypal/",
            {"template_id": "blorp"},
        )
        config.refresh_from_db()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(config.template_id, "blorp")
        self.assertEqual(resp.data["template_id"], "blorp")

    def test_setup_config(self, mock_paypal):
        user = UserFactory.create()
        self.login(user)
        templates_response = (
            mock_paypal.return_value.__enter__.return_value.get.return_value
        )
        templates_response.status_code = status.HTTP_200_OK
        templates_response.json.return_value = {
            "templates": [
                {
                    "template_id": "herp",
                    "name": "Amount",
                    "currency_code": "USD",
                }
            ]
        }
        webhook_response = (
            mock_paypal.return_value.__enter__.return_value.post.return_value
        )
        webhook_response.status_code = status.HTTP_200_OK
        webhook_response.json.return_value = {"id": "boop"}
        resp = self.client.post(
            f"/api/sales/account/{user.username}/paypal/",
            {"key": "blorp", "secret": "derp"},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        config = PaypalConfig.objects.get(user=user)
        self.assertNotIn("key", resp.data)
        self.assertEqual(config.key, "blorp")
        self.assertNotIn("secret", resp.data)
        self.assertEqual(config.secret, "derp")
        self.assertEqual(resp.data["template_id"], "herp")
        self.assertEqual(config.webhook_id, "boop")
        self.assertEqual(config.template_id, "herp")
        self.assertEqual(resp.data["active"], True)

    def test_no_matching_template(self, mock_paypal):
        user = UserFactory.create()
        self.login(user)
        templates_response = (
            mock_paypal.return_value.__enter__.return_value.get.return_value
        )
        templates_response.status_code = status.HTTP_200_OK
        templates_response.json.return_value = {
            "templates": [
                {
                    "template_id": "herp",
                    "name": "Amount",
                    "currency_code": "CAD",
                }
            ]
        }
        webhook_response = (
            mock_paypal.return_value.__enter__.return_value.post.return_value
        )
        webhook_response.status_code = status.HTTP_200_OK
        webhook_response.json.return_value = {"id": "boop"}
        resp = self.client.post(
            f"/api/sales/account/{user.username}/paypal/",
            {"key": "blorp", "secret": "derp"},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        config = PaypalConfig.objects.get(user=user)
        self.assertFalse(config.active)

    def test_bad_credentials(self, mock_paypal):
        user = UserFactory.create()
        self.login(user)
        mock_paypal.return_value.__enter__.return_value.get.side_effect = (
            MissingTokenError("Nope.")
        )
        resp = self.client.post(
            f"/api/sales/account/{user.username}/paypal/",
            {"key": "blorp", "secret": "derp"},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_other_upstream_error(self, mock_paypal):
        user = UserFactory.create()
        self.login(user)
        mock_paypal.return_value.__enter__.return_value.get.side_effect = (
            MissingTokenError("Nope.")
        )
        resp = self.client.post(
            f"/api/sales/account/{user.username}/paypal/",
            {"key": "blorp", "secret": "derp"},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pre_existing(self, _mock_paypal):
        config = PaypalConfigFactory.create()
        self.login(config.user)
        resp = self.client.post(
            f"/api/sales/account/{config.user.username}/paypal/",
            {"key": "blorp", "secret": "derp"},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["detail"], "PayPal already configured.")

    @patch("apps.sales.views.main.delete_webhooks")
    def test_delete(self, _delete_webhooks, _mock_paypal):
        config = PaypalConfigFactory.create()
        self.login(config.user)
        resp = self.client.delete(
            f"/api/sales/account/{config.user.username}/paypal/",
            {"key": "blorp", "secret": "derp"},
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(PaypalConfig.DoesNotExist):
            config.refresh_from_db()

    def test_no_delete_with_deliverables(self, _mock_paypal):
        config = PaypalConfigFactory.create()
        DeliverableFactory.create(
            paypal=True,
            status=IN_PROGRESS,
            order__seller=config.user,
            invoice__paypal_token="boop",
        )
        self.login(config.user)
        resp = self.client.delete(
            f"/api/sales/account/{config.user.username}/paypal/",
            {"key": "blorp", "secret": "derp"},
        )
        self.assertEqual(
            resp.data["detail"],
            "You must close out all orders currently managed by "
            "PayPal to remove this integration.",
        )


mock_template_data = {
    "templates": [
        {
            "id": "Beep",
            "name": "Beeper",
            "template_info": {"detail": {"currency_code": "USD"}},
        },
        {
            "id": "Boop",
            "name": "Booper",
            "template_info": {"detail": {"currency_code": "CAD"}},
        },
        {
            "id": "Herp",
            "name": "Beeper",
            "template_info": {"detail": {"currency_code": "USD"}},
        },
    ]
}


@ddt
class TestPaypalTemplates(APITestCase):
    @patch("apps.sales.views.main.paypal_api")
    @data(True, False)
    def test_get_templates(self, active, mock_paypal):
        config = PaypalConfigFactory.create(active=active)
        mock_get = mock_paypal.return_value.__enter__.return_value.get
        mock_get.return_value.json.return_value = mock_template_data
        self.login(config.user)
        resp = self.client.get(
            f"/api/sales/account/{config.user.username}/paypal/templates/"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.data,
            [{"id": "Beep", "name": "Beeper"}, {"id": "Herp", "name": "Beeper"}],
        )
