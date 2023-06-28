from unittest.mock import patch
from uuid import UUID

from apps.lib.abstract_models import ADULT, GENERAL
from apps.lib.test_resources import APITestCase, EnsurePlansMixin
from apps.lib.tests.factories_interdepend import CommentFactory
from apps.profiles.models import ArtconomyAnonymousUser
from apps.profiles.tests.factories import (
    AvatarFactory,
    CharacterFactory,
    SubmissionFactory,
    UserFactory,
)
from apps.profiles.utils import (
    UserClearException,
    clear_user,
    empty_user,
    extend_landscape,
)
from apps.sales.constants import (
    CANCELLED,
    HOLDINGS,
    IN_PROGRESS,
    LIMBO,
    MISSED,
    NEW,
    PAYMENT_PENDING,
    PENDING,
    SUCCESS,
    WAITING,
)
from apps.sales.tests.factories import (
    BankAccountFactory,
    DeliverableFactory,
    ProductFactory,
    TransactionRecordFactory,
)
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.utils.datetime_safe import date
from freezegun import freeze_time
from moneyed import Money


class ExtendPremiumTest(EnsurePlansMixin, TestCase):
    @freeze_time("2018-08-01")
    def test_extend_landscape_from_none(self):
        user = UserFactory.create()
        self.assertIsNone(user.landscape_paid_through)
        extend_landscape(user, months=1)
        self.assertEqual(user.landscape_paid_through, date(2018, 9, 1))
        self.assertEqual(user.service_plan, self.landscape)

    @freeze_time("2018-08-01")
    def test_extend_landscape_from_past(self):
        user = UserFactory.create(
            service_plan=self.landscape, service_plan_paid_through=date(2018, 7, 5)
        )
        extend_landscape(user, months=1)
        self.assertEqual(user.landscape_paid_through, date(2018, 9, 1))

    @freeze_time("2018-08-01")
    def test_extend_landscape_from_future(self):
        user = UserFactory.create(
            service_plan=self.landscape, service_plan_paid_through=date(2018, 9, 5)
        )
        extend_landscape(user, months=1)
        self.assertEqual(user.landscape_paid_through, date(2018, 10, 5))


class TestEmptyUser(APITestCase):
    def test_empty_user(self):
        session = {
            "sfw_mode": True,
            "rating": ADULT,
            "max_rating": GENERAL,
            "birthday": "1988-08-01",
        }
        self.assertEqual(
            empty_user(user=ArtconomyAnonymousUser(), session=session),
            {
                "blacklist": [],
                "nsfw_blacklist": [],
                "rating": ADULT,
                "sfw_mode": True,
                "username": "_",
                "birthday": "1988-08-01",
            },
        )


class TestClearUser(EnsurePlansMixin, TestCase):
    def test_fail_on_outstanding_order(self):
        user = UserFactory.create()
        DeliverableFactory.create(order__buyer=user, status=IN_PROGRESS)
        with self.assertRaises(UserClearException) as err:
            clear_user(user)
        self.assertEqual(
            str(err.exception),
            f"{user.username} has outstanding orders which are unfinished. Cannot remove!",
        )

    def test_fail_on_outstanding_sale(self):
        user = UserFactory.create()
        DeliverableFactory.create(order__seller=user, status=IN_PROGRESS)
        with self.assertRaises(UserClearException) as err:
            clear_user(user)
        self.assertEqual(
            str(err.exception),
            f"{user.username} has outstanding sales to complete or refund. Cannot remove!",
        )

    def test_fail_balance(self):
        user = UserFactory()
        TransactionRecordFactory.create(
            payee=user,
            amount=Money("1.00", "USD"),
            destination=HOLDINGS,
            status=SUCCESS,
        )
        with self.assertRaises(UserClearException) as err:
            clear_user(user)
        self.assertEqual(
            str(err.exception),
            f"{user.username} has pending transactions! Cannot remove!",
        )

    def test_fail_pending(self):
        user = UserFactory()
        TransactionRecordFactory.create(
            payee=user,
            amount=Money("1.00", "USD"),
            destination=HOLDINGS,
            status=SUCCESS,
        )
        TransactionRecordFactory.create(
            payer=user,
            amount=Money("1.00", "USD"),
            source=HOLDINGS,
            status=PENDING,
        )
        with self.assertRaises(UserClearException) as err:
            clear_user(user)
        self.assertEqual(
            str(err.exception),
            f"{user.username} has pending transactions! Cannot remove!",
        )

    def test_zero_balance(self):
        user = UserFactory()
        TransactionRecordFactory.create(
            payee=user,
            amount=Money("1.00", "USD"),
            destination=HOLDINGS,
            status=SUCCESS,
        )
        TransactionRecordFactory.create(
            payer=user,
            amount=Money("1.00", "USD"),
            source=HOLDINGS,
            status=SUCCESS,
        )
        clear_user(user)

    def test_clear_relevant_deliverables(self):
        user = UserFactory()
        not_relevant = DeliverableFactory.create(status=IN_PROGRESS)
        not_relevant_2 = DeliverableFactory.create(status=NEW)
        relevant_1 = DeliverableFactory.create(status=NEW, order__buyer=user)
        relevant_2 = DeliverableFactory.create(
            status=PAYMENT_PENDING, order__seller=user
        )
        relevant_3 = DeliverableFactory.create(status=WAITING, order__buyer=user)
        relevant_4 = DeliverableFactory.create(status=LIMBO, order__buyer=user)
        clear_user(user)
        to_refresh = [
            not_relevant,
            not_relevant_2,
            relevant_1,
            relevant_2,
            relevant_3,
            relevant_4,
        ]
        for order in to_refresh:
            order.refresh_from_db()
        self.assertEqual(not_relevant.status, IN_PROGRESS)
        self.assertEqual(not_relevant_2.status, NEW)
        self.assertEqual(relevant_1.status, CANCELLED)
        self.assertEqual(relevant_2.status, CANCELLED)
        self.assertEqual(relevant_3.status, CANCELLED)
        self.assertEqual(relevant_4.status, MISSED)

    @patch("apps.profiles.utils.avatar_url")
    @patch("apps.profiles.utils.uuid4")
    def test_user_attributes_changed(self, mock_uuid4, mock_avatar):
        mock_uuid4.return_value = UUID("bde2aa86-b622-4811-97ff-efccf2001047")
        mock_avatar.return_value = "https://example.com/test-reset.png"
        user = UserFactory(
            username="TestUser",
            is_active=True,
            email="test@example.com",
            landscape_enabled=True,
        )
        clear_user(user)
        user.refresh_from_db()
        self.assertEqual(user.username, f"__deleted{user.id}")
        self.assertEqual(user.email, f"bde2aa86-b622-4811-97ff-efccf2001047@local")
        self.assertFalse(user.is_active)
        self.assertFalse(user.landscape_enabled)
        self.assertEqual(user.avatar_url, "https://example.com/test-reset.png")

    def test_delete_related(self):
        user = UserFactory.create()
        to_destroy = [
            CommentFactory(user=user),
            SubmissionFactory(owner=user),
            ProductFactory(user=user),
            CharacterFactory(user=user),
            AvatarFactory.create(user=user),
        ]
        # Product should prevent this from being deleted, since the product has a deliverable.
        deliverable = DeliverableFactory.create(order__seller=user)
        favorite = SubmissionFactory(title="Favorite")
        bank_account = BankAccountFactory(user=user)
        user.favorites.add(favorite)
        user.watching.add(UserFactory.create())
        user.watched_by.add(UserFactory.create())
        to_preserve = [
            CommentFactory(),
            SubmissionFactory(),
            ProductFactory(),
            CharacterFactory(),
            deliverable.product,
            favorite,
            BankAccountFactory(),
            bank_account,
            AvatarFactory.create(),
        ]
        clear_user(user)
        for item in to_destroy:
            with self.assertRaises(ObjectDoesNotExist):
                item.refresh_from_db()
                raise AssertionError(
                    f"{item} survived culling when it should not have!"
                )
        for item in to_preserve:
            try:
                item.refresh_from_db()
            except ObjectDoesNotExist:
                raise AssertionError(
                    f"{item} was culled when it should have been preserved!"
                )
        self.assertEqual(user.favorites.count(), 0)
        self.assertEqual(user.watching.count(), 0)
        self.assertEqual(user.watched_by.count(), 0)
        self.assertEqual(user.subscription_set.count(), 0)
