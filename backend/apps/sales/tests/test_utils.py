import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import ddt
from apps.lib.models import ORDER_UPDATE, Notification, Subscription, ref_for_instance
from apps.lib.test_resources import EnsurePlansMixin, SignalsDisabledMixin
from apps.profiles.models import User
from apps.profiles.tests.factories import UserFactory
from apps.sales.constants import (
    ACH_MISC_FEES,
    CANCELLED,
    CARD,
    COMPLETED,
    DELIVERABLE_TRACKING,
    ESCROW,
    FAILURE,
    HOLDINGS,
    IN_PROGRESS,
    LIMBO,
    NEW,
    PROCESSING,
    RESERVE,
    SHIELD,
    SUCCESS,
    UNPROCESSED_EARNINGS,
    VOID,
    MISSED,
)
from apps.sales.models import LineItem, TransactionRecord, Deliverable
from apps.sales.tests.factories import (
    DeliverableFactory,
    InvoiceFactory,
    LineItemFactory,
    OrderFactory,
    ProductFactory,
    ReferenceFactory,
    RevisionFactory,
    ServicePlanFactory,
    StripeAccountFactory,
    TransactionRecordFactory,
)
from apps.sales.utils import (
    PENDING,
    POSTED_ONLY,
    account_balance,
    available_products,
    claim_order_by_token,
    credit_referral,
    default_deliverable,
    destroy_deliverable,
    fetch_prefixed,
    freeze_line_items,
    from_remote_id,
    get_claim_token,
    initialize_tip_invoice,
    invoice_post_payment,
    reverse_record,
    set_service_plan,
    term_charge,
    update_downstream_pricing,
    verify_total,
    mark_adult,
)
from apps.sales.views.tests.fixtures.stripe_fixtures import base_charge_succeeded_event
from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Q, Sum
from django.test import TestCase, override_settings
from django.utils import timezone
from freezegun import freeze_time
from moneyed import Money
from rest_framework.exceptions import ValidationError
from short_stuff import gen_shortcode


class BalanceTestCase(EnsurePlansMixin, SignalsDisabledMixin, TestCase):
    def setUp(self):
        super().setUp()
        user1 = UserFactory.create(username="Fox")
        user2 = UserFactory.create(username="Cat")
        transaction = TransactionRecordFactory.create(
            card=None,
            payer=user1,
            payee=user2,
            source=CARD,
            destination=ESCROW,
            amount=Money("10.00", "USD"),
        )
        user1, user2 = transaction.payer, transaction.payee
        TransactionRecordFactory.create(
            card=None,
            payer=user1,
            payee=user2,
            amount=Money("5.00", "USD"),
            source=RESERVE,
            destination=ESCROW,
        )
        TransactionRecordFactory.create(
            card=None,
            payer=user2,
            payee=user1,
            source=ESCROW,
            destination=ACH_MISC_FEES,
            amount=Money("3.00", "USD"),
            status=PENDING,
        )
        TransactionRecordFactory.create(
            card=None,
            payer=user2,
            payee=user1,
            source=ESCROW,
            destination=ACH_MISC_FEES,
            amount=Money("3.00", "USD"),
            status=FAILURE,
        )
        TransactionRecordFactory.create(
            card=None,
            payer=user2,
            payee=None,
            source=ESCROW,
            destination=ACH_MISC_FEES,
            amount=Money("0.50", "USD"),
            status=SUCCESS,
        )
        self.user1 = User.objects.get(username="Fox")
        self.user2 = User.objects.get(username="Cat")

    def test_account_balance_available(self):
        self.assertEqual(account_balance(self.user2, ESCROW), Decimal("11.50"))
        self.assertEqual(account_balance(self.user1, RESERVE), Decimal("-5.00"))
        self.assertEqual(account_balance(None, ACH_MISC_FEES), Decimal("0.50"))

    def test_account_balance_posted(self):
        self.assertEqual(
            account_balance(self.user2, ESCROW, POSTED_ONLY), Decimal("14.50")
        )
        self.assertEqual(
            account_balance(self.user1, RESERVE, POSTED_ONLY), Decimal("-5.00")
        )
        self.assertEqual(
            account_balance(None, ACH_MISC_FEES, POSTED_ONLY), Decimal("0.50")
        )

    def test_account_balance_pending(self):
        self.assertEqual(account_balance(self.user2, ESCROW, PENDING), Decimal("-3.00"))
        self.assertEqual(account_balance(self.user1, RESERVE, PENDING), Decimal("0.00"))
        self.assertEqual(account_balance(None, ACH_MISC_FEES, PENDING), Decimal("0.00"))
        self.assertEqual(
            account_balance(self.user1, ACH_MISC_FEES, PENDING), Decimal("3.00")
        )

    def test_nonsense_balance(self):
        with self.assertRaises(TypeError):
            account_balance(self.user2, ESCROW, 50)


class TestClaim(EnsurePlansMixin, TestCase):
    def test_order_claim_no_token(self):
        user = UserFactory.create()
        order = DeliverableFactory.create(order__buyer=None).order
        claim_order_by_token(str(order.claim_token), user)
        order.refresh_from_db()
        self.assertEqual(order.buyer, user)
        self.assertIsNone(order.claim_token)

    def test_order_claim_already_claimed_and_registered(self):
        user = UserFactory.create()
        order = DeliverableFactory.create(order__buyer=user).order
        order.claim_token = gen_shortcode()
        order.save()
        with self.assertRaises(AssertionError):
            claim_order_by_token(str(order.claim_token), user)
        order.refresh_from_db()
        self.assertEqual(order.buyer, user)
        self.assertIsNone(order.claim_token)

    def test_order_claim_from_guest(self):
        guest = UserFactory.create(guest=True)
        user = UserFactory.create()
        order = DeliverableFactory.create(order__buyer=guest).order
        claim_order_by_token(str(order.claim_token), user)
        order.refresh_from_db()
        self.assertEqual(order.buyer, user)
        self.assertIsNone(order.claim_token)

    def test_force_claim(self):
        user = UserFactory.create()
        order = DeliverableFactory.create(
            order__buyer=user, order__claim_token=gen_shortcode()
        ).order
        Subscription.objects.filter(
            content_type=ContentType.objects.get_for_model(order), object_id=order.id
        ).delete()
        claim_order_by_token(str(order.claim_token), user, force=True)
        order.refresh_from_db()
        self.assertEqual(order.buyer, user)
        self.assertIsNone(order.claim_token)
        Subscription.objects.filter(
            content_type=ContentType.objects.get_for_model(order), object_id=order.id
        ).exists()

    def test_order_claim_fail_self(self):
        user = UserFactory.create()
        order = DeliverableFactory.create(
            order__buyer=None, order__seller=user, product__user=user
        ).order
        original_token = order.claim_token
        claim_order_by_token(str(order.claim_token), user)
        order.refresh_from_db()
        self.assertTrue(order.claim_token)
        self.assertEqual(order.claim_token, original_token)
        self.assertIsNone(order.buyer)

    @patch("apps.sales.utils.transfer_order")
    def test_order_claim_none(self, mock_transfer):
        user = UserFactory.create()
        order = DeliverableFactory.create(order__buyer=None).order
        claim_order_by_token(None, user)
        mock_transfer.assert_not_called()
        order.refresh_from_db()
        self.assertIsNone(order.buyer)

    def test_order_claim_string(self):
        user = UserFactory.create()
        order = DeliverableFactory.create(order__buyer=None).order
        claim_order_by_token(str(order.claim_token), user)
        order.refresh_from_db()
        self.assertEqual(order.buyer, user)
        self.assertIsNone(order.claim_token)

    @patch("apps.sales.utils.logger.warning")
    def test_order_claim_fail(self, mock_warning):
        user = UserFactory.create()
        uid = uuid.uuid4()
        claim_order_by_token(uid, user)
        self.assertTrue(mock_warning.called)

    def test_order_claim_subscription(self):
        user = UserFactory.create()
        deliverable = DeliverableFactory.create(order__buyer=None)
        claim_order_by_token(str(deliverable.order.claim_token), user)
        notification = Notification.objects.get(event__type=ORDER_UPDATE)
        self.assertEqual(notification.user, user)
        self.assertEqual(notification.event.target, deliverable)


class TestAvailableProducts(EnsurePlansMixin, TestCase):
    # Basic smoke tests. Can be expanded if stuff breaks, but most of this functionality
    # is tested elsewhere.
    def test_available_products(self):
        user = UserFactory.create()
        product = ProductFactory.create()
        self.assertEqual(list(available_products(user)), [product])

    def test_available_products_ordered(self):
        user = UserFactory.create()
        ProductFactory.create()
        self.assertIn("ORDER BY", str(available_products(user).query))


class TestFreezeLineItems(EnsurePlansMixin, TestCase):
    def test_freezes_values(self):
        invoice = InvoiceFactory.create()
        source = [
            LineItemFactory.create(
                amount=Money("0.01", "USD"), priority=0, invoice=invoice
            ),
            LineItemFactory.create(
                amount=Money("0.01", "USD"), priority=100, invoice=invoice
            ),
            LineItemFactory.create(
                amount=Money("0.01", "USD"), priority=100, invoice=invoice
            ),
            LineItemFactory.create(
                amount=Money("-5.00", "USD"), priority=100, invoice=invoice
            ),
            LineItemFactory.create(
                amount=Money("10.00", "USD"), priority=100, invoice=invoice
            ),
            LineItemFactory.create(
                amount=Money(".75", "USD"),
                percentage=Decimal("8"),
                cascade_percentage=True,
                cascade_amount=True,
                priority=300,
                invoice=invoice,
                # Priority will be overwritten by post-save action if not explicitly
                # set.
                type=SHIELD,
            ),
        ]
        freeze_line_items(invoice)
        for line_item in source:
            line_item.refresh_from_db()
        self.assertEqual(source[0].frozen_value, Money("0.00", "USD"))
        self.assertEqual(source[1].frozen_value, Money("0.00", "USD"))
        self.assertEqual(source[2].frozen_value, Money("0.00", "USD"))
        self.assertEqual(source[3].frozen_value, Money("-5.00", "USD"))
        self.assertEqual(source[4].frozen_value, Money("8.86", "USD"))
        self.assertEqual(source[5].frozen_value, Money("1.17", "USD"))


class TransactionCheckMixin:
    def check_transactions(
        self,
        deliverable,
        user,
        remote_id="36985214745",
        source=CARD,
        landscape=False,
    ):
        escrow_transactions = TransactionRecord.objects.filter(
            source=source,
            destination=ESCROW,
        )
        if remote_id:
            escrow_transactions = escrow_transactions.filter(
                remote_ids__contains=remote_id
            )
        else:
            escrow_transactions = escrow_transactions.filter(remote_ids=[])
        escrow = escrow_transactions.get()
        self.assertEqual(
            escrow.targets.filter(content_type__model="deliverable").get().target,
            deliverable,
        )
        self.assertEqual(
            escrow.targets.filter(content_type__model="invoice").get().target,
            deliverable.invoice,
        )
        if landscape:
            self.assertEqual(escrow.amount, Money("11.01", "USD"))
        else:
            self.assertEqual(escrow.amount, Money("10.28", "USD"))
        self.assertEqual(escrow.payer, user)
        self.assertEqual(escrow.payee, deliverable.order.seller)

        shield_fee_candidates = TransactionRecord.objects.filter(
            source=source,
            destination=UNPROCESSED_EARNINGS,
        )
        if remote_id:
            shield_fee_candidates = shield_fee_candidates.filter(
                remote_ids__contains=remote_id
            )
        else:
            shield_fee_candidates = shield_fee_candidates.filter(remote_ids=[])
        shield_fee = shield_fee_candidates.get()
        self.assertEqual(shield_fee.status, SUCCESS)
        self.assertEqual(
            shield_fee.targets.filter(content_type__model="deliverable").get().target,
            deliverable,
        )
        self.assertEqual(
            shield_fee.targets.filter(content_type__model="invoice").get().target,
            deliverable.invoice,
        )
        if landscape:
            self.assertEqual(shield_fee.amount, Money("0.99", "USD"))
        else:
            self.assertEqual(shield_fee.amount, Money("1.72", "USD"))
        if source == CARD:
            card_fee = TransactionRecord.objects.get(payer=None, payee=None)
            self.assertEqual(card_fee.amount, Money(".65", "USD"))
        self.assertEqual(shield_fee.payer, user)
        self.assertIsNone(shield_fee.payee)
        self.assertEqual(
            TransactionRecord.objects.all()
            .exclude(Q(payer=None) & Q(payee=None))
            .aggregate(total=Sum("amount"))["total"],
            Decimal("12.00"),
        )


class TestDestroyDeliverable(EnsurePlansMixin, TestCase):
    def test_destroy_deliverable_fail_not_cancelled(self):
        deliverable = DeliverableFactory(status=IN_PROGRESS)
        self.assertRaises(IntegrityError, destroy_deliverable, deliverable)

    def test_destroy_deliverable_accepts_missed(self):
        deliverable = DeliverableFactory.create(status=MISSED)
        destroy_deliverable(deliverable)
        self.assertRaises(Deliverable.DoesNotExist, deliverable.refresh_from_db)

    @patch("apps.lib.utils.clear_events_subscriptions_and_comments")
    def test_destroy_deliverable(self, mock_clear):
        deliverable = DeliverableFactory(status=CANCELLED)
        seller = deliverable.order.seller
        buyer = deliverable.order.buyer
        revision = RevisionFactory(deliverable=deliverable)
        unrelated_revision = RevisionFactory()
        reused_reference = ReferenceFactory()
        reference = ReferenceFactory()
        deliverable.reference_set.add(reference)
        other_deliverable = DeliverableFactory()
        other_deliverable.reference_set.add(reused_reference)
        other_deliverable.refresh_from_db()

        to_preserve = {
            "other_deliverable": other_deliverable,
            "reused_reference": reused_reference,
            "unrelated_revision": unrelated_revision,
            "buyer": buyer,
            "seller": seller,
        }
        to_destroy = {
            "deliverable": deliverable,
            "reference": reference,
            "revision": revision,
        }
        destroy_deliverable(deliverable)
        for name, target in to_preserve.items():
            try:
                target.refresh_from_db()
            except ObjectDoesNotExist:
                raise AssertionError(
                    f"{name} was destroyed when it should not have been!"
                )
        for name, target in to_destroy.items():
            try:
                target.refresh_from_db()
                raise AssertionError(
                    f"{name} was preserved when it should not have been!"
                )
            except ObjectDoesNotExist:
                continue


class TestGetClaimToken(EnsurePlansMixin, TestCase):
    def test_retrieve_existing(self):
        uid = gen_shortcode()
        order = OrderFactory.create(claim_token=uid)
        get_claim_token(order)
        self.assertEqual(uid, order.claim_token)

    def test_no_generate_irrelevant_token(self):
        order = OrderFactory.create()
        self.assertIsNone(order.claim_token)
        self.assertIsNone(get_claim_token(order))
        order.refresh_from_db()
        self.assertIsNone(order.claim_token)

    def test_generate_token(self):
        order = OrderFactory.create(buyer__guest=True)
        self.assertIsNone(order.claim_token)
        uid = get_claim_token(order)
        self.assertIsNotNone(uid)
        order.refresh_from_db()
        self.assertEqual(order.claim_token, uid)


FETCH_SCENARIOS = (
    ("test_item", "stuff_things", "wat_do"),
    ("test_item", "test_things", "wat_do"),
    ("wat_do", "test_item", "test_things"),
)


@ddt.ddt
class TestFetchPrefix(TestCase):
    @ddt.data(*FETCH_SCENARIOS)
    def test_prefix_fetched(self, id_list):
        self.assertEqual(fetch_prefixed("test_", id_list), "test_item")

    def test_prefix_not_found(self):
        with self.assertRaises(ValueError):
            fetch_prefixed("wat", ["test_thing", "wot"])


class TestVerifyTotal(EnsurePlansMixin, TestCase):
    def test_negative(self):
        deliverable = DeliverableFactory.create(
            product__base_price=Money("5.00", "USD")
        )
        LineItemFactory.create(
            invoice=deliverable.invoice, amount=Money("-6.00", "USD")
        )
        with self.assertRaises(ValidationError):
            verify_total(deliverable)

    @override_settings(MINIMUM_PRICE=Money("100.00", "USD"))
    def test_below_minimum(self):
        deliverable = DeliverableFactory.create(
            product__base_price=Money("5.00", "USD")
        )
        with self.assertRaises(ValidationError):
            verify_total(deliverable)

    @override_settings(MINIMUM_PRICE=Money("1.00", "USD"))
    def test_above_minimum(self):
        deliverable = DeliverableFactory.create(
            product__base_price=Money("5.00", "USD")
        )
        verify_total(deliverable)

    def test_zero(self):
        deliverable = DeliverableFactory.create(
            product__base_price=Money("0.00", "USD")
        )
        self.assertEqual(deliverable.invoice.total(), Money("0.00", "USD"))
        verify_total(deliverable)


class TestDefaultDeliverable(EnsurePlansMixin, TestCase):
    def test_get_default_deliverable(self):
        deliverable = DeliverableFactory.create()
        self.assertEqual(default_deliverable(deliverable.order), deliverable)

    def test_get_default_deliverable_multiple(self):
        deliverable = DeliverableFactory.create()
        DeliverableFactory.create(order=deliverable.order)
        self.assertIsNone(default_deliverable(deliverable.order))


class TestFromRemoteID(EnsurePlansMixin, TestCase):
    # Most cases are covered in other tests, so we'll just check this one here:
    def test_unsupported_status(self):
        event = base_charge_succeeded_event()["data"]["object"]
        event["status"] = "pending"
        post_success = MagicMock()
        post_save = MagicMock()
        initiate_transactions = MagicMock()
        attempt = {"stripe_event": event, "amount": Money("10.00", "USD")}
        success, transactions, message = from_remote_id(
            amount=Money("10.00", "USD"),
            attempt=attempt,
            context={},
            remote_ids=["1234"],
            user=UserFactory.create(),
            post_success=post_success,
            post_save=post_save,
            initiate_transactions=initiate_transactions,
        )
        self.assertFalse(success)
        self.assertEqual(transactions, [])
        self.assertEqual(
            message,
            "Unhandled charge status, pending for remote_ids "
            "['1234', 'txn_1Icyh5AhlvPza3BKKv8oUs3e']",
        )
        post_success.assert_not_called()
        initiate_transactions.assert_not_called()


class TestMarkAdult(EnsurePlansMixin, TestCase):
    def test_mark_adult_escrow_enabled(self):
        deliverable = DeliverableFactory.create(escrow_enabled=True)
        self.assertFalse(deliverable.order.buyer.verified_adult)
        mark_adult(deliverable)
        deliverable.order.buyer.refresh_from_db()
        self.assertTrue(deliverable.order.buyer.verified_adult)

    def test_mark_adult_paypal_invoice(self):
        deliverable = DeliverableFactory.create(
            escrow_enabled=False, invoice__paypal_token="beep"
        )
        self.assertFalse(deliverable.order.buyer.verified_adult)
        mark_adult(deliverable)
        deliverable.order.buyer.refresh_from_db()
        self.assertTrue(deliverable.order.buyer.verified_adult)

    def test_no_mark(self):
        deliverable = DeliverableFactory.create(escrow_enabled=False)
        self.assertFalse(deliverable.order.buyer.verified_adult)
        mark_adult(deliverable)
        deliverable.order.buyer.refresh_from_db()
        self.assertFalse(deliverable.order.buyer.verified_adult)


class TestCreditReferral(EnsurePlansMixin, TestCase):
    def test_credit_referral_from_free(self):
        user = UserFactory.create()
        self.assertEqual(user.service_plan, self.free)
        self.assertIsNone(user.service_plan_paid_through)
        user2 = UserFactory.create(referred_by=user)
        deliverable = DeliverableFactory.create(order__seller=user2)
        deliverable.escrow_enabled = True
        deliverable.save()
        self.assertTrue(deliverable.escrow_enabled)
        credit_referral(deliverable)
        user.refresh_from_db()
        self.assertEqual(user.service_plan, self.landscape)
        self.assertTrue(user.service_plan_paid_through)
        self.assertEqual(user.next_service_plan, self.free)

    @freeze_time("2023-01-01")
    def test_credit_referral_extends_landscape(self):
        user = UserFactory.create(
            service_plan=self.landscape,
            service_plan_paid_through=timezone.now().date(),
            next_service_plan=self.free,
        )
        # Quick sanity check.
        self.assertEqual(user.service_plan, self.landscape)
        self.assertEqual(user.next_service_plan, self.free)
        user2 = UserFactory.create(referred_by=user)
        deliverable = DeliverableFactory.create(order__seller=user2)
        deliverable.escrow_enabled = True
        deliverable.save()
        credit_referral(deliverable)
        user.refresh_from_db()
        self.assertEqual(user.service_plan, self.landscape)
        self.assertEqual(
            user.service_plan_paid_through,
            timezone.now().date() + relativedelta(months=1),
        )
        # Shouldn't affect next service plan.
        self.assertEqual(user.next_service_plan, self.free)


class TestInitializeTipInvoice(EnsurePlansMixin, TestCase):
    @override_settings(
        PROCESSING_PERCENTAGE=Decimal("5"),
        INTERNATIONAL_CONVERSION_PERCENTAGE=Decimal("2"),
    )
    def test_issue_invoice_idempotent(self):
        deliverable = DeliverableFactory.create(
            status=COMPLETED, finalized_on=timezone.now()
        )
        deliverable.order.seller.service_plan = self.landscape
        deliverable.order.seller.save()
        invoice = initialize_tip_invoice(deliverable)
        self.assertTrue(invoice.id)
        self.assertEqual(initialize_tip_invoice(deliverable), invoice)
        line = invoice.line_items.filter(type=PROCESSING).get()
        self.assertEqual(line.percentage, Decimal("5"))

    def test_reissue_voice(self):
        deliverable = DeliverableFactory.create(
            status=COMPLETED, finalized_on=timezone.now()
        )
        deliverable.order.seller.service_plan = self.landscape
        deliverable.order.seller.save()
        invoice = initialize_tip_invoice(deliverable)
        invoice.status = VOID
        invoice.save()
        self.assertNotEqual(invoice, initialize_tip_invoice(deliverable))

    @override_settings(
        PROCESSING_PERCENTAGE=Decimal("5"),
        INTERNATIONAL_CONVERSION_PERCENTAGE=Decimal("2"),
    )
    def test_international(self):
        deliverable = DeliverableFactory.create(
            status=COMPLETED, finalized_on=timezone.now(), international=True
        )
        deliverable.order.seller.service_plan = self.landscape
        deliverable.order.seller.save()
        invoice = initialize_tip_invoice(deliverable)
        line = invoice.line_items.filter(type=PROCESSING).get()
        self.assertEqual(line.percentage, Decimal("7"))


class TestInvoicePostPayment(EnsurePlansMixin, TestCase):
    def test_invoice_post_pay_wrong_amount(self):
        deliverable = DeliverableFactory.create()
        with self.assertRaises(AssertionError):
            invoice_post_payment(
                deliverable.invoice, {"successful": True, "amount": Money("100", "USD")}
            )


class TestUpdateDownstreamPricing(EnsurePlansMixin, TestCase):
    def test_product_and_deliverable_order(self):
        product = ProductFactory.create(cascade_fees=False, escrow_enabled=True)
        deliverable = DeliverableFactory.create(
            product=product, order__seller=product.user, cascade_fees=False
        )
        original_product_price = product.starting_price
        original_deliverable_price = deliverable.invoice.total()
        service_plan = ServicePlanFactory(per_deliverable_price=Money("1.00", "USD"))
        product.user.service_plan = service_plan
        product.user.save()
        update_downstream_pricing(product.user)
        product.refresh_from_db()
        deliverable.refresh_from_db()
        product_difference = product.starting_price - original_product_price
        deliverable_difference = (
            deliverable.invoice.total() - original_deliverable_price
        )
        self.assertTrue(product_difference)
        self.assertTrue(deliverable_difference)


class TestSetServicePlan(EnsurePlansMixin, TestCase):
    def test_upgrade_makes_limbo_visible(self):
        deliverable = DeliverableFactory.create(status=LIMBO)
        visible_deliverable = DeliverableFactory.create(
            status=NEW, order__seller=deliverable.order.seller
        )
        # Should make no change.
        set_service_plan(deliverable.order.seller, self.free)
        deliverable.refresh_from_db()
        visible_deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, LIMBO)
        self.assertEqual(visible_deliverable.status, NEW)
        # Landscape has no order limit.
        set_service_plan(deliverable.order.seller, self.landscape)
        deliverable.refresh_from_db()
        visible_deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, NEW)
        self.assertEqual(visible_deliverable.status, NEW)

    def test_upgrade_makes_limited_limbo_visible(self):
        deliverable = DeliverableFactory.create(status=NEW)
        second_deliverable = DeliverableFactory.create(
            status=LIMBO, order__seller=deliverable.order.seller
        )
        third_deliverable = DeliverableFactory.create(
            status=LIMBO, order__seller=deliverable.order.seller
        )
        set_service_plan(
            deliverable.order.seller,
            ServicePlanFactory.create(max_simultaneous_orders=2),
        )
        deliverable.refresh_from_db()
        second_deliverable.refresh_from_db()
        third_deliverable.refresh_from_db()
        visible = [
            item
            for item in [deliverable, second_deliverable, third_deliverable]
            if item.status == NEW
        ]
        self.assertEqual(len(visible), 2)


class TestReverseRecord(EnsurePlansMixin, TestCase):
    def test_reverse_record(self):
        initial_record = TransactionRecordFactory.create(
            source=ESCROW,
            destination=HOLDINGS,
            amount=Money("10", "USD"),
            remote_ids=["beep", "boop"],
        )
        user = UserFactory.create()
        initial_record.targets.add(ref_for_instance(user))
        created, new_record = reverse_record(initial_record)
        # Sanity check
        self.assertTrue(initial_record.payer)
        self.assertTrue(initial_record.payee)
        self.assertTrue(created)
        self.assertEqual(initial_record.amount, new_record.amount)
        self.assertEqual(initial_record.source, new_record.destination)
        self.assertEqual(initial_record.destination, new_record.source)
        self.assertEqual(initial_record.payer, new_record.payee)
        self.assertEqual(initial_record.payee, new_record.payer)
        self.assertEqual(initial_record.remote_ids, new_record.remote_ids)
        targets = [target.target for target in new_record.targets.all()]
        self.assertIn(user, targets)
        self.assertIn(initial_record, targets)
        created, again_record = reverse_record(initial_record)
        self.assertEqual(again_record, new_record)
        self.assertFalse(created)

    def test_success_only(self):
        initial_record = TransactionRecordFactory.create(
            status=FAILURE,
            source=ESCROW,
            destination=HOLDINGS,
            amount=Money("10", "USD"),
            remote_ids=["beep", "boop"],
        )
        with self.assertRaises(ValueError):
            reverse_record(initial_record)


class TestTermCharge(EnsurePlansMixin, TestCase):
    def test_term_charge(self):
        user = UserFactory.create()
        plan = ServicePlanFactory.create(per_deliverable_price=Money("1.00", "USD"))
        StripeAccountFactory.create(user=user, active=True)
        user.service_plan = plan
        user.save()
        deliverable = DeliverableFactory.create(
            order__seller=user, escrow_enabled=False
        )
        term_charge(deliverable)
        line = LineItem.objects.get(
            invoice=deliverable.invoice, type=DELIVERABLE_TRACKING
        )
        self.assertEqual(line.amount, Money("1.00", "USD"))
        self.assertEqual(line.targets.first(), ref_for_instance(deliverable))

    def test_term_charge_skips_escrow(self):
        user = UserFactory.create()
        plan = ServicePlanFactory.create(per_deliverable_price=Money("1.00", "USD"))
        StripeAccountFactory.create(user=user, active=True)
        user.service_plan = plan
        user.save()
        deliverable = DeliverableFactory.create(order__seller=user, escrow_enabled=True)
        term_charge(deliverable)
        self.assertFalse(
            LineItem.objects.filter(
                invoice=deliverable.invoice, type=DELIVERABLE_TRACKING
            ).exists()
        )
