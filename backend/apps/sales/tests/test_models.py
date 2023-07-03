from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch

from apps.lib.models import (
    COMMENT,
    NEW_PRODUCT,
    REVISION_APPROVED,
    ModifiedMarker,
    Subscription,
    ref_for_instance,
)
from apps.lib.test_resources import EnsurePlansMixin
from apps.lib.tests.factories_interdepend import CommentFactory
from apps.lib.utils import FakeRequest
from apps.profiles.models import IN_SUPPORTED_COUNTRY, NO_SUPPORTED_COUNTRY
from apps.profiles.tests.factories import SubmissionFactory, UserFactory
from apps.sales.constants import (
    BASE_PRICE,
    CANCELLED,
    COMPLETED,
    DELIVERABLE_TRACKING,
    NEW,
    PAYMENT_PENDING,
    PENDING,
    PRIORITY_MAP,
    QUEUED,
    SHIELD,
    SUCCESS,
    TABLE_SERVICE,
    TAX,
    WAITING,
)
from apps.sales.models import (
    InventoryTracker,
    Product,
    StripeLocation,
    StripeReader,
    deliverable_from_context,
)
from apps.sales.tests.factories import (
    CreditCardTokenFactory,
    DeliverableFactory,
    InvoiceFactory,
    LineItemFactory,
    OrderFactory,
    ProductFactory,
    PromoFactory,
    RatingFactory,
    ReferenceFactory,
    RevisionFactory,
    ServicePlanFactory,
    StripeAccountFactory,
    StripeLocationFactory,
    StripeReaderFactory,
    TransactionRecordFactory,
    WebhookRecordFactory,
)
from ddt import data, ddt, unpack
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone
from freezegun import freeze_time
from moneyed import Money


class TestRating(EnsurePlansMixin, TestCase):
    def test_set_stars(self):
        user = UserFactory.create()
        rater = UserFactory.create()
        RatingFactory.create(target=user, stars=2, rater=rater)
        RatingFactory.create(target=user, stars=5, rater=rater)
        RatingFactory.create(target=user, stars=4, rater=rater)
        user.refresh_from_db()
        self.assertEqual(user.stars, Decimal("3.67"))
        self.assertEqual(user.rating_count, 3)

    def test_string(self):
        user = UserFactory.create(username="Beep")
        rater = UserFactory.create(username="Boop")
        deliverable = DeliverableFactory.create(
            product=None, order__seller=user, order__buyer=rater
        )
        rating = RatingFactory.create(target=user, stars=2, rater=rater)
        rating.content_object = deliverable
        rating.save()
        self.assertEqual(str(rating), f"Boop rated Beep 2 stars for [{deliverable}]")


class TestPromo(TestCase):
    def test_promo_string(self):
        promo = PromoFactory.create(code="Wat")
        self.assertEqual(str(promo), "WAT")


DESCRIPTION_VALUES = (
    {
        "price": Decimal("5.00"),
        "prefix": "[Starts at $5.00] - ",
        "escrow_enabled": True,
    },
    {"price": Decimal("0"), "prefix": "[Starts at FREE] - ", "escrow_enabled": True},
    {"price": Decimal("0"), "prefix": "[Starts at FREE] - ", "escrow_enabled": False},
    {
        "price": Decimal("1.1"),
        "prefix": "[Starts at $1.10] - ",
        "escrow_enabled": False,
    },
)


@ddt
class TestProduct(EnsurePlansMixin, TestCase):
    def test_can_reference(self):
        user = UserFactory.create()
        product = ProductFactory.create(user=user)
        other = UserFactory.create()
        self.assertTrue(product.can_reference_asset(user))
        self.assertFalse(product.can_reference_asset(other))

    @patch("apps.sales.models.recall_notification")
    def test_recall(self, mock_recall_notification):
        user = UserFactory.create()
        product = ProductFactory.create(hidden=False, user=user)
        mock_recall_notification.assert_not_called()
        product.hidden = True
        product.save()
        mock_recall_notification.assert_called_with(
            NEW_PRODUCT, user, {"product": product.id}, unique_data=True
        )

    def test_notification_display(self):
        request = Mock()
        request.user = UserFactory.create()
        context = {"request": request}
        product = ProductFactory.create(
            user=request.user, primary_submission=SubmissionFactory.create()
        )
        data = product.notification_display(context)
        self.assertEqual(data["id"], product.primary_submission.id)

    def test_escrow_disabled(self):
        product = ProductFactory.create(user__artist_profile__escrow_enabled=False)
        self.assertFalse(product.escrow_enabled)
        product.table_product = True
        product.save()
        self.assertTrue(product.escrow_enabled)
        product.escrow_enabled = True
        product.table_product = False
        product.save()
        # Should be overwritten by lack of bank support.
        self.assertFalse(product.escrow_enabled)

    @unpack
    @data(*DESCRIPTION_VALUES)
    def test_preview_description(
        self, price: Decimal, prefix: str, escrow_enabled: bool
    ):
        account_status = (
            IN_SUPPORTED_COUNTRY if escrow_enabled else NO_SUPPORTED_COUNTRY
        )
        product = ProductFactory.create(
            base_price=price,
            description="Test **Test** *Test*",
        )
        product.user.artist_profile.bank_status = account_status
        product.user.artist_profile.escrow_enabled = escrow_enabled
        product.user.artist_profile.save()
        self.assertTrue(
            product.preview_description.startswith(prefix),
            msg=f"{repr(product.preview_description)} does not start with "
            f"{repr(prefix)}.",
        )
        self.assertTrue(
            product.preview_description.endswith("Test Test Test"),
            msg=f"{repr(product.preview_description)} does not end with 'Test Test "
            f"Test'.",
        )

    def test_preview_link(self):
        product = ProductFactory.create(primary_submission=None)
        self.assertEqual(product.preview_link, "/static/images/default-avatar.png")
        submission = SubmissionFactory.create()
        product.primary_submission = submission
        self.assertEqual(product.preview_link, submission.preview_link)

    def test_string(self):
        product = ProductFactory.create(
            name="Beep", user__username="Boop", base_price=Money("30.00", "USD")
        )
        self.assertEqual(str(product), "Beep offered by Boop at $30.00")


class TestTransactionRecord(EnsurePlansMixin, TestCase):
    def test_string(self):
        record = TransactionRecordFactory.create(
            payer__username="Dude", payee__username="Chick"
        )
        self.assertEqual(
            str(record),
            "Successful [Escrow hold]: $10.00 from Dude [Credit Card] to Chick "
            "[Escrow] for None",
        )
        submission = SubmissionFactory.create()
        record.targets.add(ref_for_instance(submission))
        self.assertEqual(
            str(record),
            f"Successful [Escrow hold]: $10.00 from Dude [Credit Card] to Chick "
            f"[Escrow] for {submission}",
        )
        record.targets.add(ref_for_instance(SubmissionFactory.create()))
        self.assertEqual(
            str(record),
            f"Successful [Escrow hold]: $10.00 from Dude [Credit Card] to "
            f"Chick [Escrow] for {submission} and 1 other(s).",
        )

    def test_auto_finalize(self):
        record = TransactionRecordFactory.create(status=PENDING)
        self.assertIsNone(record.finalized_on)
        record.status = SUCCESS
        record.save()
        self.assertTrue(record.finalized_on)


@ddt
@override_settings(
    TABLE_PERCENTAGE_FEE=Decimal("20"),
    TABLE_STATIC_FEE=Money("2.00", "USD"),
    TABLE_TAX=Decimal("8"),
)
class TestDeliverable(EnsurePlansMixin, TestCase):
    def test_total(self):
        deliverable = DeliverableFactory.create(product__base_price=Money(5, "USD"))
        self.assertEqual(deliverable.invoice.total(), Money("5.00", "USD"))
        LineItemFactory.create(invoice=deliverable.invoice, amount=Money("2.00", "USD"))
        self.assertEqual(deliverable.invoice.total(), Money("7.00", "USD"))

    def deliverable_and_context(self):
        deliverable = DeliverableFactory.create()
        deliverable.arbitrator = UserFactory.create()
        deliverable.save()
        request = Mock()
        request.user = deliverable.arbitrator
        context = {"request": request}
        return deliverable, context

    def test_notification_name(self):
        deliverable, context = self.deliverable_and_context()
        self.assertEqual(
            f"Case #{deliverable.order.id} [{deliverable.name}]",
            deliverable.notification_name(context),
        )
        deliverable.buyer = deliverable.arbitrator
        deliverable.arbitrator = None
        self.assertEqual(
            f"Order #{deliverable.order.id} [{deliverable.name}]",
            deliverable.notification_name(context),
        )

    def test_notification_name_waitlisted(self):
        deliverable, context = self.deliverable_and_context()
        deliverable.status = WAITING
        deliverable.save()
        self.assertEqual(
            f"Case #{deliverable.order.id} [{deliverable.name}] (Waitlisted)",
            deliverable.notification_name(context),
        )

    def test_notification_link(self):
        deliverable, context = self.deliverable_and_context()
        self.assertEqual(
            {
                "name": "CaseDeliverableOverview",
                "params": {
                    "orderId": deliverable.order.id,
                    "deliverableId": deliverable.id,
                    "username": context["request"].user.username,
                },
            },
            deliverable.notification_link(context),
        )
        deliverable.buyer = deliverable.arbitrator
        deliverable.arbitrator = None
        deliverable.save()
        self.assertEqual(
            {
                "name": "OrderDeliverableOverview",
                "params": {
                    "orderId": deliverable.order.id,
                    "deliverableId": deliverable.id,
                    "username": context["request"].user.username,
                },
            },
            deliverable.notification_link(context),
        )

    def test_notification_link_guest(self):
        deliverable, context = self.deliverable_and_context()
        deliverable.order.buyer = UserFactory.create(guest=True, username="__1")
        deliverable.order.claim_token = "y1zGvlKfTnmA"
        deliverable.order.save()
        context["request"].user = deliverable.order.buyer
        self.assertEqual(
            {
                "name": "ClaimOrder",
                "params": {
                    "claimToken": "y1zGvlKfTnmA",
                    "orderId": deliverable.order.id,
                    "deliverableId": deliverable.id,
                    "next": f"%7B%22name%22%3A%20%22OrderDeliverableOverview%22%2C%20%2"
                    f"2params%22%3A%20"
                    f"%7B%22username%22%3A%20%22_%22%2C%20%22orderId%22%3A%20"
                    f"{deliverable.order.id}"
                    f"%2C%20%22deliverableId%22%3A%20{deliverable.id}%7D%7D",
                },
            },
            deliverable.notification_link(context),
        )

    def test_notification_link_deliverable(self):
        deliverable, context = self.deliverable_and_context()
        DeliverableFactory.create(order=deliverable.order)
        self.assertEqual(
            {
                "name": "CaseDeliverableOverview",
                "params": {
                    "orderId": deliverable.order.id,
                    "deliverableId": deliverable.id,
                    "username": context["request"].user.username,
                },
            },
            deliverable.notification_link(context),
        )
        deliverable.buyer = deliverable.arbitrator
        deliverable.arbitrator = None
        deliverable.save()
        self.assertEqual(
            {
                "name": "OrderDeliverableOverview",
                "params": {
                    "orderId": deliverable.order.id,
                    "deliverableId": deliverable.id,
                    "username": context["request"].user.username,
                },
            },
            deliverable.notification_link(context),
        )

    def test_notification_display(self):
        deliverable, context = self.deliverable_and_context()
        deliverable.product.primary_submission = SubmissionFactory.create()
        output = deliverable.notification_display(context)
        self.assertEqual(output["id"], deliverable.product.primary_submission.id)
        self.assertEqual(output["title"], deliverable.product.primary_submission.title)

    def test_notification_display_revision(self):
        deliverable, context = self.deliverable_and_context()
        deliverable.product.primary_submission = SubmissionFactory.create()
        deliverable.revisions_hidden = False
        revision = RevisionFactory.create(deliverable=deliverable)
        output = deliverable.notification_display(context)
        self.assertEqual(output["id"], revision.id)
        self.assertIn(revision.file.file.name, output["file"]["full"])

    @data(True, False)
    @patch("apps.sales.stripe.stripe")
    def test_create_line_items_escrow(self, cascade_fees, mock_stripe):
        plan = ServicePlanFactory.create(
            name="Test Plan",
            shield_percentage_price=Decimal("9"),
            shield_static_price=Money(".35", "USD"),
        )
        deliverable = DeliverableFactory.create(
            product__base_price=Money("15.00", "USD"),
            order__seller__service_plan=plan,
            cascade_fees=cascade_fees,
        )
        base_price = deliverable.invoice.line_items.get(type=BASE_PRICE)
        self.assertEqual(base_price.amount, Money("15.00", "USD"))
        self.assertEqual(base_price.percentage, 0)
        self.assertEqual(base_price.priority, 0)
        shield = deliverable.invoice.line_items.get(type=SHIELD)
        self.assertEqual(shield.percentage, Decimal("9"))
        self.assertEqual(shield.amount, Money(".35", "USD"))
        self.assertEqual(shield.cascade_percentage, cascade_fees)
        self.assertEqual(shield.cascade_amount, cascade_fees)
        self.assertEqual(shield.priority, PRIORITY_MAP[SHIELD])
        self.assertEqual(deliverable.invoice.line_items.all().count(), 2)

    @data(True, False)
    def test_create_line_items_escrow_international(self, cascade_fees):
        plan = ServicePlanFactory.create(
            name="Test Plan",
            shield_percentage_price=Decimal("9"),
            shield_static_price=Money(".35", "USD"),
        )
        account = StripeAccountFactory.create(country="AU", user__service_plan=plan)
        deliverable = DeliverableFactory.create(
            product__base_price=Money("15.00", "USD"),
            cascade_fees=cascade_fees,
            order__seller=account.user,
        )
        base_price = deliverable.invoice.line_items.get(type=BASE_PRICE)
        self.assertEqual(base_price.amount, Money("15.00", "USD"))
        self.assertEqual(base_price.percentage, 0)
        self.assertEqual(base_price.priority, 0)
        shield = deliverable.invoice.line_items.get(type=SHIELD)
        self.assertEqual(shield.percentage, Decimal("10"))
        self.assertEqual(shield.amount, Money(".35", "USD"))
        self.assertEqual(shield.cascade_percentage, cascade_fees)
        self.assertEqual(shield.cascade_amount, cascade_fees)
        self.assertEqual(shield.priority, PRIORITY_MAP[SHIELD])
        self.assertEqual(deliverable.invoice.line_items.all().count(), 2)

    def test_create_line_items_non_escrow_free(self):
        deliverable = DeliverableFactory.create(
            product__base_price=Money("15.00", "USD"), escrow_enabled=False
        )
        base_price = deliverable.invoice.line_items.get(type=BASE_PRICE)
        self.assertEqual(base_price.amount, Money("15.00", "USD"))
        self.assertEqual(base_price.percentage, 0)
        self.assertEqual(base_price.priority, 0)
        self.assertEqual(deliverable.invoice.line_items.all().count(), 1)

    @data(True, False)
    def test_create_line_items_non_escrow_metered(self, cascade_fees):
        plan = ServicePlanFactory.create(per_deliverable_price=Money("2.00", "USD"))
        deliverable = DeliverableFactory.create(
            product__base_price=Money("15.00", "USD"),
            escrow_enabled=False,
            order__seller__service_plan=plan,
            cascade_fees=cascade_fees,
        )
        base_price = deliverable.invoice.line_items.get(type=BASE_PRICE)
        self.assertEqual(base_price.amount, Money("15.00", "USD"))
        self.assertEqual(base_price.percentage, 0)
        self.assertEqual(base_price.priority, 0)
        meter_price = deliverable.invoice.line_items.get(type=DELIVERABLE_TRACKING)
        self.assertEqual(meter_price.amount, Money("2.00", "USD"))
        self.assertEqual(meter_price.cascade_amount, cascade_fees)
        self.assertEqual(deliverable.invoice.line_items.all().count(), 2)

    @data(True, False)
    def test_create_line_items_table_service(self, cascade_fees):
        deliverable = DeliverableFactory.create(
            product__base_price=Money("15.00", "USD"),
            table_order=True,
            cascade_fees=cascade_fees,
        )
        base_price = deliverable.invoice.line_items.get(type=BASE_PRICE)
        self.assertEqual(base_price.amount, Money("15.00", "USD"))
        self.assertEqual(base_price.percentage, 0)
        self.assertEqual(base_price.priority, 0)
        table_service = deliverable.invoice.line_items.get(type=TABLE_SERVICE)
        self.assertEqual(table_service.percentage, Decimal("20"))
        self.assertEqual(table_service.amount, Money("2.00", "USD"))
        self.assertEqual(table_service.cascade_percentage, cascade_fees)
        self.assertFalse(table_service.cascade_amount)
        set_on_fire = deliverable.invoice.line_items.get(type=TAX)
        self.assertEqual(set_on_fire.percentage, Decimal("8"))
        self.assertEqual(set_on_fire.amount, Money("0.00", "USD"))
        self.assertEqual(deliverable.invoice.line_items.all().count(), 3)

    @override_settings(AUTO_CANCEL_DAYS=5)
    @freeze_time("2023-01-01")
    def test_set_auto_cancel(self):
        deliverable = DeliverableFactory.create(status=NEW)
        self.assertEqual(deliverable.auto_cancel_on, timezone.now().replace(day=6))
        with freeze_time(date(2023, 1, 3)):
            CommentFactory.create(
                top=deliverable,
                content_object=deliverable,
                user=deliverable.order.buyer,
            )
            deliverable.refresh_from_db()
            self.assertEqual(deliverable.auto_cancel_on, timezone.now().replace(day=8))

    @override_settings(AUTO_CANCEL_DAYS=5)
    @freeze_time("2023-01-01")
    def test_no_set_auto_cancel_on_secondary_deliverables(self):
        initial_deliverable = DeliverableFactory.create(status=NEW)
        second_deliverable = DeliverableFactory.create(
            status=NEW, order=initial_deliverable.order
        )
        # Re-saving shouldn't break the first, though.
        initial_deliverable.save()
        self.assertEqual(
            initial_deliverable.auto_cancel_on, timezone.now().replace(day=6)
        )
        self.assertIsNone(second_deliverable.auto_cancel_on)

    @override_settings(AUTO_CANCEL_DAYS=5)
    @freeze_time("2023-01-01")
    def test_auto_cancel_cleared_on_response(self):
        deliverable = DeliverableFactory.create(status=NEW)
        self.assertEqual(deliverable.auto_cancel_on, timezone.now().replace(day=6))
        CommentFactory.create(
            top=deliverable, content_object=deliverable, user=deliverable.order.seller
        )
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.auto_cancel_on, None)

    @override_settings(AUTO_CANCEL_DAYS=5)
    @freeze_time("2023-01-01")
    def test_auto_cancel_stays_none_if_not_new(self):
        deliverable = DeliverableFactory.create(status=PAYMENT_PENDING)
        self.assertEqual(deliverable.auto_cancel_on, None)
        CommentFactory.create(
            top=deliverable, content_object=deliverable, user=deliverable.order.buyer
        )
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.auto_cancel_on, None)


class TestCreditCardToken(EnsurePlansMixin, TestCase):
    def test_string(self):
        card = CreditCardTokenFactory.create(last_four="1234")
        self.assertEqual(str(card), "Visa ending in 1234")
        card.active = False
        self.assertEqual(str(card), "Visa ending in 1234 (Deleted)")

    def test_no_delete(self):
        card = CreditCardTokenFactory.create()
        self.assertRaises(RuntimeError, card.delete)

    def test_channels(self):
        card = CreditCardTokenFactory.create()
        self.assertEqual(
            card.announce_channels(),
            [
                f"profiles.User.pk.{card.user.id}.all_cards",
                f"profiles.User.pk.{card.user.id}.stripe_cards",
            ],
        )

    def test_check_token(self):
        with self.assertRaises(ValidationError):
            CreditCardTokenFactory.create(stripe_token="", token="")


class TestRevision(EnsurePlansMixin, TestCase):
    def test_can_reference(self):
        user = UserFactory.create()
        buyer = UserFactory.create()
        revision = RevisionFactory.create(
            owner=user,
            deliverable__order__seller=user,
            deliverable__product__user=user,
            deliverable__order__buyer=buyer,
        )
        other = UserFactory.create()
        self.assertTrue(revision.can_reference_asset(revision.owner))
        self.assertFalse(revision.can_reference_asset(other))
        self.assertFalse(revision.can_reference_asset(buyer))
        revision.deliverable.status = COMPLETED
        self.assertTrue(revision.can_reference_asset(buyer))

    def test_string(self):
        revision = RevisionFactory.create()
        self.assertEqual(
            str(revision),
            f"Revision {revision.id} for Deliverable object "
            f"({revision.deliverable.id})",
        )

    def test_notification_name(self):
        revision = RevisionFactory.create()
        context = {"request": FakeRequest(user=revision.deliverable.order.buyer)}
        self.assertEqual(
            revision.notification_name(context),
            f"Revision ID #{revision.id} on Order #{revision.deliverable.order.id} "
            f"[{revision.deliverable.name}]",
        )

    def test_notification_display(self):
        revision = RevisionFactory.create()
        context = {"request": FakeRequest(user=revision.deliverable.order.buyer)}
        self.assertIn(
            "file",
            revision.notification_display(context),
        )

    def test_notification_link(self):
        revision = RevisionFactory.create()
        context = {"request": FakeRequest(user=revision.deliverable.order.buyer)}
        self.assertEqual(
            revision.notification_link(context),
            {
                "name": "OrderDeliverableRevision",
                "params": {
                    "deliverableId": revision.deliverable.id,
                    "orderId": revision.deliverable.order.id,
                    "revisionId": revision.id,
                    "username": revision.deliverable.order.buyer.username,
                },
            },
        )

    def test_subscriptions_created(self):
        deliverable = DeliverableFactory.create()
        Subscription.objects.all().delete()
        revision = RevisionFactory.create(
            owner=deliverable.order.seller, deliverable=deliverable
        )
        seller_comment_subscription = Subscription.objects.get(
            subscriber=revision.owner, type=COMMENT
        )
        self.assertEqual(seller_comment_subscription.target, revision)
        seller_approval_subscription = Subscription.objects.get(
            subscriber=revision.owner, type=REVISION_APPROVED
        )
        self.assertEqual(seller_approval_subscription.target, revision)
        buyer_subscription = Subscription.objects.get(
            subscriber=deliverable.order.buyer
        )
        self.assertEqual(buyer_subscription.type, COMMENT)
        self.assertEqual(buyer_subscription.target, revision)

    def test_subscription_created_no_buyer(self):
        deliverable = DeliverableFactory.create(order__buyer=None)
        Subscription.objects.all().delete()
        revision = RevisionFactory.create(
            owner=deliverable.order.seller, deliverable=deliverable
        )
        seller_comment_subscription = Subscription.objects.get(
            subscriber=revision.owner, type=COMMENT
        )
        self.assertEqual(seller_comment_subscription.target, revision)
        seller_approval_subscription = Subscription.objects.get(
            subscriber=revision.owner, type=REVISION_APPROVED
        )
        self.assertEqual(seller_approval_subscription.target, revision)

    def test_subscription_created_once(self):
        deliverable = DeliverableFactory.create(order__buyer=None)
        Subscription.objects.all().delete()
        revision = RevisionFactory.create(
            owner=deliverable.order.seller, deliverable=deliverable
        )
        self.assertEqual(Subscription.objects.all().count(), 2)
        revision.save()
        self.assertEqual(Subscription.objects.all().count(), 2)


class TestLoadAdjustment(EnsurePlansMixin, TestCase):
    def test_load_changes(self):
        user = UserFactory.create()
        user.artist_profile.max_load = 10
        user.artist_profile.save()
        DeliverableFactory.create(task_weight=5, status=QUEUED, order__seller=user)
        user.refresh_from_db()
        self.assertEqual(user.artist_profile.load, 5)
        self.assertFalse(user.artist_profile.commissions_disabled)
        self.assertFalse(user.artist_profile.commissions_closed)
        order = DeliverableFactory.create(task_weight=5, status=NEW, order__seller=user)
        user.refresh_from_db()
        self.assertEqual(user.artist_profile.load, 5)
        self.assertFalse(user.artist_profile.commissions_disabled)
        self.assertFalse(user.artist_profile.commissions_closed)
        order.status = QUEUED
        order.save()
        user.refresh_from_db()
        # Max load reached.
        self.assertEqual(user.artist_profile.load, 10)
        self.assertTrue(user.artist_profile.commissions_disabled)
        self.assertFalse(user.artist_profile.commissions_closed)
        DeliverableFactory.create(task_weight=5, status=NEW, order__seller=user)
        user.refresh_from_db()
        # Now we have an order in a new state. This shouldn't undo the disability.
        self.assertEqual(user.artist_profile.load, 10)
        self.assertTrue(user.artist_profile.commissions_disabled)
        self.assertFalse(user.artist_profile.commissions_closed)
        order.status = COMPLETED
        order.save()
        user.refresh_from_db()
        # We have reduced the load, but never took care of the new order. This used to
        # result in commissions being disabled, but we've removed that functionality
        # and they should be open now.
        self.assertEqual(user.artist_profile.load, 5)
        self.assertFalse(user.artist_profile.commissions_disabled)
        self.assertFalse(user.artist_profile.commissions_closed)
        # Closing commissions should disable them as well.
        user.artist_profile.commissions_closed = True
        user.save()
        self.assertTrue(user.artist_profile.commissions_closed)
        self.assertTrue(user.artist_profile.commissions_disabled)
        user.artist_profile.commissions_closed = False
        order.status = CANCELLED
        order.save()
        # We should be clear again.
        user.refresh_from_db()
        self.assertFalse(user.artist_profile.commissions_closed)
        self.assertFalse(user.artist_profile.commissions_disabled)
        Product.objects.all().delete()
        # Make a product too big for the user to complete. Should close the user.
        product = ProductFactory.create(user=user, task_weight=20)
        user.refresh_from_db()
        self.assertFalse(user.artist_profile.commissions_closed)
        self.assertTrue(user.artist_profile.commissions_disabled)
        # And dropping it should open them back up.
        product.task_weight = 1
        product.save()
        user.refresh_from_db()
        self.assertFalse(user.artist_profile.commissions_closed)
        self.assertFalse(user.artist_profile.commissions_disabled)
        # Waitlisting won't open commissions...
        product.task_weight = 20
        product.wait_list = True
        product.save()
        user.refresh_from_db()
        self.assertFalse(user.artist_profile.commissions_closed)
        self.assertTrue(user.artist_profile.commissions_disabled)
        # ...Unless you are on a plan that allows it.
        user.service_plan.waitlisting = True
        user.service_plan.save()
        product.save()
        user.refresh_from_db()
        self.assertFalse(user.artist_profile.commissions_closed)
        self.assertFalse(user.artist_profile.commissions_disabled)
        # But a specific product that is too large will be considered unavailable.
        other_product = ProductFactory.create(user=user, task_weight=20)
        other_product.refresh_from_db()
        self.assertFalse(other_product.available)
        # It will be considered available if the weight is under the available slots.
        other_product.task_weight = 5
        other_product.save()
        other_product.refresh_from_db()
        self.assertTrue(other_product.available)


class TestOrder(EnsurePlansMixin, TestCase):
    def test_order_string(self):
        order = OrderFactory.create(seller__username="Jim", buyer__username="Bob")
        self.assertEqual(str(order), f"#{order.id} by Jim for Bob")

    def test_mark_modified(self):
        order = OrderFactory.create()
        with self.assertRaises(ModifiedMarker.DoesNotExist):
            ModifiedMarker.objects.get(
                content_type=ContentType.objects.get_for_model(order),
                object_id=order.id,
            )
        CommentFactory.create(top=order)
        # Should exist now.
        marker = ModifiedMarker.objects.get(
            content_type=ContentType.objects.get_for_model(order), object_id=order.id
        )
        self.assertEqual(marker.order, order)

    def test_notification_display(self):
        deliverable = DeliverableFactory.create()
        self.assertEqual(
            deliverable.order.notification_link(
                {"request": FakeRequest(user=deliverable.order.seller)}
            ),
            {
                "name": "SaleDeliverableOverview",
                "params": {
                    "deliverableId": deliverable.id,
                    "orderId": deliverable.order.id,
                    "username": deliverable.order.seller.username,
                },
            },
        )


class TestInventoryTracker(EnsurePlansMixin, TestCase):
    def test_inventory(self):
        product = ProductFactory.create(track_inventory=False)
        self.assertTrue(product.available)
        with self.assertRaises(InventoryTracker.DoesNotExist):
            InventoryTracker.objects.get(product=product)
        product.track_inventory = True
        product.save()
        product.refresh_from_db()
        inventory = InventoryTracker.objects.get(product=product)
        self.assertEqual(inventory.count, 0)
        self.assertFalse(product.available)
        product.track_inventory = False
        product.save()
        with self.assertRaises(InventoryTracker.DoesNotExist):
            inventory.refresh_from_db()
        product.refresh_from_db()
        self.assertTrue(product.available)


class TestInvoice(EnsurePlansMixin, TestCase):
    def test_string_no_deliverable(self):
        invoice = InvoiceFactory.create()
        self.assertEqual(
            str(invoice),
            # Not sure why the money library adds this weird padding, but it's their
            # bug, not mine.
            f"Invoice {invoice.id} [Sale] for {invoice.bill_to.username} in the amount "
            f"of $\xa00.00",
        )

    def test_string_deliverable(self):
        deliverable = DeliverableFactory.create(
            product__base_price=Money("15.00", "USD")
        )
        self.assertEqual(
            str(deliverable.invoice),
            f"Invoice {deliverable.invoice.id} [Sale] for "
            f"{deliverable.invoice.bill_to.username} in the amount of "
            f"$15.00 for deliverable: Deliverable object ({deliverable.id})",
        )


class TestReference(EnsurePlansMixin, TestCase):
    def test_never_reference(self):
        reference = ReferenceFactory.create()
        self.assertFalse(reference.can_reference_asset(reference.file.uploaded_by))

    def test_mark_modified(self):
        deliverable = DeliverableFactory.create()
        reference = ReferenceFactory.create()
        deliverable.reference_set.add(reference)
        with self.assertRaises(ModifiedMarker.DoesNotExist):
            ModifiedMarker.objects.get(
                content_type=ContentType.objects.get_for_model(reference),
                object_id=reference.id,
            )
        CommentFactory.create(top=reference, extra_data={"deliverable": deliverable.id})
        # Should exist now.
        marker = ModifiedMarker.objects.get(
            content_type=ContentType.objects.get_for_model(reference),
            object_id=reference.id,
        )
        self.assertEqual(marker.deliverable, reference.deliverables.first())

    def test_mark_modified_deliverable_gone(self):
        deliverable = DeliverableFactory.create()
        reference = ReferenceFactory.create()
        with self.assertRaises(ModifiedMarker.DoesNotExist):
            ModifiedMarker.objects.get(
                content_type=ContentType.objects.get_for_model(reference),
                object_id=reference.id,
            )
        CommentFactory.create(top=reference, extra_data={"deliverable": deliverable.id})
        # Should exist now.
        marker = ModifiedMarker.objects.get(
            content_type=ContentType.objects.get_for_model(reference),
            object_id=reference.id,
        )
        self.assertIsNone(marker.deliverable)

    def test_notification_name(self):
        deliverable = DeliverableFactory.create()
        reference = ReferenceFactory.create()
        deliverable.reference_set.add(reference)
        context = {
            "extra_data": {"deliverable": deliverable.id},
            "request": FakeRequest(user=deliverable.order.seller),
        }
        self.assertEqual(
            reference.notification_name(context),
            f"Reference ID #{reference.id} for Sale #{deliverable.order.id} "
            f"[{deliverable.name}]",
        )

    def test_notification_link(self):
        deliverable = DeliverableFactory.create()
        reference = ReferenceFactory.create()
        deliverable.reference_set.add(reference)
        context = {
            "extra_data": {"deliverable": deliverable.id},
            "request": FakeRequest(user=deliverable.order.seller),
        }
        self.assertEqual(
            reference.notification_link(context),
            {
                "name": "SaleDeliverableReference",
                "params": {
                    "deliverableId": deliverable.id,
                    "orderId": deliverable.order.id,
                    "referenceId": reference.id,
                    "username": deliverable.order.seller.username,
                },
            },
        )

    def test_notification_link_no_context(self):
        reference = ReferenceFactory.create()
        context = {"extra_data": {"deliverable": "1234"}}
        self.assertEqual(
            reference.notification_link(context),
            None,
        )

    def test_notification_display(self):
        deliverable = DeliverableFactory.create()
        reference = ReferenceFactory.create()
        deliverable.reference_set.add(reference)
        context = {
            "extra_data": {"deliverable": deliverable.id},
            "request": FakeRequest(user=deliverable.order.seller),
        }
        self.assertIn(
            "file",
            reference.notification_display(context),
        )


class TestLineItem(EnsurePlansMixin, TestCase):
    def test_string(self):
        line_item = LineItemFactory.create(
            amount=Money("15", "USD"), percentage=5, priority=100
        )
        self.assertEqual(
            str(line_item),
            f"Add on or Discount ($15.00, 5) for #{line_item.invoice.id}, priority 100",
        )


class TestWebhook(TestCase):
    def test_string(self):
        webhook = WebhookRecordFactory.create()
        connect_webhook = WebhookRecordFactory.create(connect=True)
        self.assertEqual(str(webhook), f"Webhook {webhook.id}")
        self.assertEqual(
            str(connect_webhook), f"Webhook {connect_webhook.id} (Connect)"
        )


class TestDeliverableFromRequest(EnsurePlansMixin, TestCase):
    def test_deliverable_from_context(self):
        deliverable = DeliverableFactory.create()
        context = {
            "extra_data": {"deliverable": deliverable.id},
            "request": FakeRequest(user=deliverable.order.seller),
        }
        self.assertEqual(deliverable_from_context(context), deliverable)

    def test_deliverable_from_context_bad_permission(self):
        deliverable = DeliverableFactory.create()
        context = {
            "extra_data": {"deliverable": deliverable.id},
            "request": FakeRequest(user=UserFactory.create()),
        }
        self.assertIsNone(deliverable_from_context(context))

    def test_deliverable_from_context_no_check(self):
        deliverable = DeliverableFactory.create()
        context = {
            "extra_data": {"deliverable": deliverable.id},
            "request": FakeRequest(user=UserFactory.create()),
        }
        self.assertEqual(
            deliverable_from_context(context, check_request=False), deliverable
        )

    def test_nonexistent(self):
        context = {
            "extra_data": {"deliverable": 1234},
            "request": FakeRequest(user=UserFactory.create()),
        }
        self.assertIsNone(deliverable_from_context(context))

    def test_nonsense(self):
        context = {
            "extra_data": {"deliverable": "beep"},
            "request": FakeRequest(user=UserFactory.create()),
        }
        self.assertIsNone(deliverable_from_context(context))


class TestServicePlan(TestCase):
    def test_string(self):
        plan = ServicePlanFactory.create(name="Boop")
        self.assertEqual(str(plan), f"Boop (#{plan.id})")


@patch("apps.sales.models.stripe")
class TestStripeLocation(TestCase):
    def test_string(self, _mock_stripe):
        location = StripeLocationFactory.create()
        self.assertEqual(str(location), location.name)

    def test_create_location(self, mock_stripe):
        location = StripeLocation(
            name="Beep",
            line1="1234 Someplace lane",
            city="Houston",
            postal_code="77339",
        )
        mock_stripe.__enter__.return_value.terminal.Location.create.return_value = {
            "id": "1234"
        }
        location.save()
        mock_stripe.__enter__.return_value.terminal.Location.create.assert_called_with(
            display_name="Beep",
            address={
                "line1": "1234 Someplace lane",
                "country": "",
                "city": "Houston",
                "postal_code": "77339",
            },
        )
        self.assertEqual(location.stripe_token, "1234")

    def test_modify_location(self, mock_stripe):
        location = StripeLocation(
            name="Beep",
            line1="1234 Someplace lane",
            city="Houston",
            postal_code="77339",
        )
        mock_stripe.__enter__.return_value.terminal.Location.create.return_value = {
            "id": "1234"
        }
        location.save()
        mock_stripe.__enter__.return_value.terminal.Location.modify.assert_not_called()
        location.save()
        mock_stripe.__enter__.return_value.terminal.Location.modify.assert_called_with(
            "1234",
            display_name="Beep",
            address={
                "line1": "1234 Someplace lane",
                "country": "",
                "city": "Houston",
                "postal_code": "77339",
            },
        )

    def test_delete(self, mock_stripe):
        location = StripeLocationFactory.create(stripe_token="1234")
        location.delete()
        mock_stripe.__enter__.return_value.terminal.Location.delete.assert_called_with(
            "1234"
        )


@patch("apps.sales.models.stripe")
class TestStripeReader(TestCase):
    def test_string(self, _mock_stripe):
        reader = StripeReaderFactory.create(name="Beep", location__name="Boop")
        self.assertEqual(str(reader), f"Beep at Boop (#{reader.id})")

    def test_create_reader_normal(self, mock_stripe):
        location = StripeLocationFactory.create(stripe_token="1234")
        reader = StripeReader(
            name="Swiper",
            location=location,
        )
        reader.registration_code = "Beep Boop"
        mock_stripe.__enter__.return_value.terminal.Reader.create.return_value = {
            "id": "5678"
        }
        reader.save()
        mock_stripe.__enter__.return_value.terminal.Reader.create.assert_called_with(
            label="Swiper",
            location="1234",
            registration_code="Beep Boop",
        )
        self.assertEqual(reader.stripe_token, "5678")
        self.assertFalse(reader.virtual)

    def test_create_reader_virtual(self, mock_stripe):
        location = StripeLocationFactory.create(stripe_token="1234")
        reader = StripeReader(
            name="Swiper",
            location=location,
        )
        reader.registration_code = "simulated"
        mock_stripe.__enter__.return_value.terminal.Reader.create.return_value = {
            "id": "5678"
        }
        reader.save()
        mock_stripe.__enter__.return_value.terminal.Reader.create.assert_called_with(
            label="Swiper",
            location="1234",
            registration_code="simulated",
        )
        self.assertEqual(reader.stripe_token, "5678")
        self.assertTrue(reader.virtual)

    def test_delete(self, mock_stripe):
        reader = StripeReaderFactory.create(stripe_token="Boop")
        reader.delete()
        mock_stripe.__enter__.return_value.terminal.Reader.delete.assert_called_with(
            "Boop"
        )
