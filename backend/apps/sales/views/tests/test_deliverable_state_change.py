from decimal import Decimal
from unittest.mock import call, patch

from apps.lib.abstract_models import ADULT
from apps.lib.models import (
    COMMENT,
    DISPUTE,
    ORDER_UPDATE,
    REVISION_APPROVED,
    REVISION_UPLOADED,
    Subscription,
    ref_for_instance,
)
from apps.lib.test_resources import APITestCase
from apps.profiles.tests.factories import (
    CharacterFactory,
    SubmissionFactory,
    UserFactory,
)
from apps.sales.constants import (
    AUTHORIZE,
    CARD,
    CASH_DEPOSIT,
    COMPLETED,
    DISPUTED,
    ESCROW,
    ESCROW_HOLD,
    ESCROW_REFUND,
    FAILURE,
    HOLDINGS,
    IN_PROGRESS,
    LIMBO,
    MONEY_HOLE_STAGE,
    NEW,
    PAID,
    PAYMENT_PENDING,
    QUEUED,
    REFUNDED,
    RESERVE,
    REVIEW,
    STRIPE,
    SUCCESS,
    TABLE_HANDLING,
    UNPROCESSED_EARNINGS,
    WAITING,
)
from apps.sales.models import Deliverable, TransactionRecord, idempotent_lines
from apps.sales.tests.factories import (
    CreditCardTokenFactory,
    DeliverableFactory,
    LineItemFactory,
    ReferenceFactory,
    RevisionFactory,
    ServicePlanFactory,
    TransactionRecordFactory,
)
from apps.sales.utils import get_term_invoice
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import override_settings
from django.utils import timezone
from django.utils.datetime_safe import date
from freezegun import freeze_time
from moneyed import Money
from rest_framework import status
from stripe.error import InvalidRequestError


@patch("apps.sales.views.main.notify")
class TestDeliverableStatusChange(APITestCase):
    fixture_list = ["deliverable-state-change"]

    def setUp(self):
        super().setUp()
        self.outsider = UserFactory.create(
            username="Outsider", email="outsider@example.com"
        )
        self.seller = UserFactory.create(username="Seller", email="seller@example.com")
        self.buyer = UserFactory.create(username="Buyer", email="buyer@example.com")
        self.staffer = UserFactory.create(
            is_staff=True, username="Staffer", email="staff@example.com"
        )
        characters = [
            CharacterFactory.create(
                user=self.buyer,
                name="Pictured",
                primary_submission=SubmissionFactory.create(),
            ),
            CharacterFactory.create(
                user=self.buyer,
                private=True,
                name="Unpictured1",
                primary_submission=None,
            ),
            CharacterFactory.create(
                user=UserFactory.create(),
                open_requests=True,
                name="Unpictured2",
                primary_submission=None,
            ),
        ]
        self.deliverable = DeliverableFactory.create(
            order__seller=self.seller,
            order__buyer=self.buyer,
            product__base_price=Money("5.00", "USD"),
            adjustment_task_weight=1,
            adjustment_expected_turnaround=2,
            product__task_weight=3,
            product__expected_turnaround=4,
            processor=AUTHORIZE,
        )
        self.deliverable.characters.add(*characters)
        self.final = RevisionFactory.create(
            deliverable=self.deliverable, rating=ADULT, owner=self.seller
        )
        self.url = "/api/sales/v1/order/{}/deliverables/{}/".format(
            self.deliverable.order.id, self.deliverable.id
        )

    def state_assertion(
        self,
        user_attr,
        url_ext="",
        target_response_code=status.HTTP_200_OK,
        initial_status=None,
        method="post",
        target_status=None,
    ):
        if initial_status is not None:
            self.deliverable.status = initial_status
            self.deliverable.save()
        self.login(getattr(self, user_attr))
        response = getattr(self.client, method)(self.url + url_ext)
        try:
            self.assertEqual(response.status_code, target_response_code)
        except AssertionError:
            raise AssertionError(
                f"Expected response code {target_response_code} but got "
                f"{response.status_code}. Data: {response.data}",
            )
        if target_status is not None:
            self.deliverable.refresh_from_db()
            self.assertEqual(self.deliverable.status, target_status)

    def test_accept_deliverable(self, _mock_notify):
        self.state_assertion("seller", "accept/")

    def test_waitlist_deliverable_deliverable(self, _mock_notify):
        self.state_assertion(
            "seller", "waitlist/", initial_status=NEW, target_status=WAITING
        )

    def test_accept_deliverable_waitlist(self, _mock_notify):
        idempotent_lines(self.deliverable)
        self.state_assertion(
            "seller", "accept/", initial_status=WAITING, target_status=PAYMENT_PENDING
        )

    def test_accept_deliverable_send_email(self, _mock_notify):
        self.deliverable.order.buyer = None
        self.deliverable.order.customer_email = "test_customer@example.com"
        self.deliverable.order.save()
        Subscription.objects.all().delete()
        self.state_assertion("seller", "accept/")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            f"You have a new invoice from {self.deliverable.order.seller.username}!",
        )

    def test_accept_deliverable_buyer_fail(self, _mock_notify):
        self.state_assertion("buyer", "accept/", status.HTTP_403_FORBIDDEN)

    def test_accept_deliverable_outsider(self, _mock_notify):
        self.state_assertion("outsider", "accept/", status.HTTP_403_FORBIDDEN)

    def test_accept_deliverable_staffer(self, _mock_notify):
        self.state_assertion("staffer", "accept/")

    def test_accept_deliverable_free(self, _mock_notify):
        LineItemFactory.create(
            invoice=self.deliverable.invoice,
            amount=-self.deliverable.product.base_price,
        )
        idempotent_lines(self.deliverable)
        self.state_assertion("seller", "accept/")
        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.status, QUEUED)
        self.assertFalse(self.deliverable.revisions_hidden)
        self.assertFalse(self.deliverable.escrow_enabled)

    def test_in_progress(self, _mock_notify):
        self.deliverable.stream_link = "https://google.com/"
        self.state_assertion("seller", "start/", initial_status=QUEUED)

    def test_cancel_deliverable(self, _mock_notify):
        self.state_assertion("seller", "cancel/", initial_status=NEW)

    def test_cancel_deliverable_buyer(self, _mock_notify):
        self.state_assertion("buyer", "cancel/", initial_status=PAYMENT_PENDING)

    def test_cancel_deliverable_outsider_fail(self, _mock_notify):
        self.state_assertion(
            "outsider",
            "cancel/",
            status.HTTP_403_FORBIDDEN,
            initial_status=PAYMENT_PENDING,
        )

    def test_cancel_deliverable_staffer(self, _mock_notify):
        self.state_assertion("staffer", "cancel/", initial_status=PAYMENT_PENDING)

    def test_mark_paid_deliverable_buyer_fail(self, _mock_notify):
        self.deliverable.escrow_enabled = False
        self.deliverable.save()
        self.state_assertion(
            "buyer",
            "mark-paid/",
            status.HTTP_403_FORBIDDEN,
            initial_status=PAYMENT_PENDING,
        )

    def test_mark_paid_deliverable_seller(self, _mock_notify):
        self.deliverable.escrow_enabled = False
        self.assertTrue(self.deliverable.revisions_hidden)
        self.deliverable.save()
        self.final.delete()
        self.state_assertion(
            "seller", "mark-paid/", initial_status=PAYMENT_PENDING, target_status=QUEUED
        )
        self.deliverable.refresh_from_db()
        self.assertFalse(self.deliverable.revisions_hidden)
        self.assertTrue(self.deliverable.invoice.record_only)
        self.assertEqual(self.deliverable.invoice.status, PAID)
        # By default we're on the free plan, which has no per-deliverable charge, and
        # no monthly charge.
        self.assertEqual(
            get_term_invoice(self.deliverable.order.seller).total(), Money("0", "USD")
        )

    def test_mark_paid_adds_line_for_term(self, _mock_notify):
        self.deliverable.escrow_enabled = False
        basic_plan = ServicePlanFactory.create(
            monthly_charge=Money("0", "USD"),
            per_deliverable_price=Money("1.10", "USD"),
        )
        self.seller.service_plan = basic_plan
        self.seller.save()
        self.assertTrue(self.deliverable.revisions_hidden)
        self.deliverable.save()
        self.final.delete()
        self.state_assertion(
            "seller", "mark-paid/", initial_status=PAYMENT_PENDING, target_status=QUEUED
        )
        self.assertEqual(
            get_term_invoice(self.deliverable.order.seller).total(),
            Money("1.10", "USD"),
        )

    def test_mark_paid_disables_escrow(self, _mock_notify):
        self.assertFalse(self.deliverable.invoice.record_only)
        self.assertTrue(self.deliverable.escrow_enabled)
        self.assertTrue(self.deliverable.revisions_hidden)
        self.deliverable.save()
        self.final.delete()
        self.state_assertion(
            "seller", "mark-paid/", initial_status=PAYMENT_PENDING, target_status=QUEUED
        )
        self.deliverable.refresh_from_db()
        self.assertFalse(self.deliverable.revisions_hidden)
        self.assertFalse(self.deliverable.escrow_enabled)
        self.assertTrue(self.deliverable.invoice.record_only)
        self.assertEqual(self.deliverable.invoice.status, PAID)

    def test_mark_paid_deliverable_final_uploaded(self, _mock_notify):
        self.deliverable.escrow_enabled = False
        self.deliverable.final_uploaded = True
        self.deliverable.save()
        self.state_assertion(
            "seller",
            "mark-paid/",
            initial_status=PAYMENT_PENDING,
            target_status=COMPLETED,
        )

    def test_mark_paid_revisions_exist(self, _mock_notify):
        self.deliverable.escrow_enabled = False
        self.deliverable.save()
        RevisionFactory.create(deliverable=self.deliverable)
        self.state_assertion(
            "seller",
            "mark-paid/",
            initial_status=PAYMENT_PENDING,
            target_status=IN_PROGRESS,
        )

    def test_mark_paid_task_weights(self, _mock_notify):
        self.deliverable.escrow_enabled = False
        self.deliverable.save()
        self.assertEqual(self.deliverable.adjustment_task_weight, 1)
        self.assertEqual(self.deliverable.adjustment_expected_turnaround, 2)
        self.assertEqual(self.deliverable.task_weight, 0)
        self.assertEqual(self.deliverable.expected_turnaround, 0)
        self.state_assertion("seller", "mark-paid/", initial_status=PAYMENT_PENDING)
        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.adjustment_task_weight, 1)
        self.assertEqual(self.deliverable.adjustment_expected_turnaround, 2)
        self.assertEqual(self.deliverable.task_weight, 3)
        self.assertEqual(self.deliverable.expected_turnaround, 4)

    def test_mark_paid_deliverable_staffer(self, _mock_notify):
        self.deliverable.escrow_enabled = False
        self.deliverable.save()
        self.state_assertion("staffer", "mark-paid/", initial_status=PAYMENT_PENDING)

    def test_mark_paid_paypal_never_generated(self, _mock_notify):
        self.deliverable.escrow_enabled = False
        self.deliverable.paypal = True
        self.deliverable.save()
        self.state_assertion("seller", "mark-paid/", initial_status=PAYMENT_PENDING)
        self.deliverable.refresh_from_db()
        self.assertFalse(self.deliverable.paypal)

    @patch("apps.sales.tasks.withdraw_all.delay")
    def test_approve_deliverable_buyer(self, mock_withdraw, _mock_notify):
        record = TransactionRecordFactory.create(
            payee=self.deliverable.order.seller,
            payer=self.deliverable.order.buyer,
            source=CARD,
            destination=ESCROW,
            amount=Money("15.00", "USD"),
        )
        record.targets.add(ref_for_instance(self.deliverable))
        self.state_assertion("buyer", "approve/", initial_status=REVIEW)
        record.refresh_from_db()
        records = TransactionRecord.objects.all()
        self.assertEqual(records.count(), 2)
        payment = records.get(payee=self.deliverable.order.seller, source=ESCROW)
        self.assertEqual(payment.amount, Money("15.00", "USD"))
        self.assertEqual(payment.payer, self.deliverable.order.seller)
        self.assertEqual(payment.status, SUCCESS)
        self.assertEqual(payment.destination, HOLDINGS)
        mock_withdraw.assert_called_with(self.deliverable.order.seller.id)

    @patch("apps.sales.utils.recall_notification")
    def test_approve_deliverable_recall_notification(self, mock_recall, _mock_notify):
        target_time = timezone.now()
        self.deliverable.disputed_on = target_time
        self.deliverable.save()
        record = TransactionRecordFactory.create(
            payee=self.deliverable.order.seller,
            payer=self.deliverable.order.buyer,
            destination=ESCROW,
            source=CARD,
            category=ESCROW_HOLD,
            amount=Money("15.00", "USD"),
        )
        record.targets.add(ref_for_instance(self.deliverable))
        self.state_assertion("buyer", "approve/", initial_status=DISPUTED)
        mock_recall.assert_has_calls([call(DISPUTE, self.deliverable)])
        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.disputed_on, None)

    @patch("apps.sales.utils.recall_notification")
    def test_approve_deliverable_staffer_no_recall_notification(
        self, mock_recall, _mock_notify
    ):
        record = TransactionRecordFactory.create(
            payee=self.deliverable.order.seller,
            payer=self.deliverable.order.buyer,
            destination=ESCROW,
            source=CARD,
            category=ESCROW_HOLD,
            amount=Money("15.00", "USD"),
        )
        record.targets.add(ref_for_instance(self.deliverable))
        target_time = timezone.now()
        self.deliverable.disputed_on = target_time
        self.deliverable.save()
        self.state_assertion("staffer", "approve/", initial_status=DISPUTED)
        for mock_call in mock_recall.call_args_list:
            self.assertNotEqual(mock_call[0], DISPUTE)
        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.disputed_on, target_time)

    @override_settings(
        TABLE_PERCENTAGE_FEE=Decimal("15"),
        TABLE_STATIC_FEE=Money("2.00", "USD"),
    )
    @patch("apps.sales.tasks.withdraw_all.delay")
    def test_approve_table_deliverable(self, mock_withdraw, _mock_notify):
        self.deliverable.product.base_price = Money("15.00", "USD")
        self.deliverable.product.save()
        self.deliverable.table_order = True
        self.deliverable.status = NEW
        self.deliverable.save()
        idempotent_lines(self.deliverable)
        record = TransactionRecordFactory.create(
            payee=self.deliverable.order.seller,
            payer=self.deliverable.order.buyer,
            source=CARD,
            destination=ESCROW,
            amount=Money("15.00", "USD"),
        )
        record.targets.add(
            ref_for_instance(self.deliverable),
            ref_for_instance(self.deliverable.invoice),
        )
        record2 = TransactionRecordFactory.create(
            payee=None,
            payer=self.deliverable.order.buyer,
            source=CARD,
            destination=RESERVE,
            amount=Money("2.00", "USD"),
        )
        record2.targets.add(
            ref_for_instance(self.deliverable),
            ref_for_instance(self.deliverable.invoice),
        )
        record3 = TransactionRecordFactory.create(
            payee=None,
            payer=self.deliverable.order.buyer,
            source=CARD,
            destination=MONEY_HOLE_STAGE,
            amount=Money("3.00", "USD"),
        )
        record3.targets.add(
            ref_for_instance(self.deliverable),
            ref_for_instance(self.deliverable.invoice),
        )
        self.state_assertion("buyer", "approve/", initial_status=REVIEW)
        record.refresh_from_db()
        records = TransactionRecord.objects.all()
        self.assertEqual(records.count(), 6)
        payment = records.get(payee=self.deliverable.order.seller, source=ESCROW)
        self.assertEqual(payment.amount, Money("15.00", "USD"))
        self.assertEqual(payment.payer, self.deliverable.order.seller)
        self.assertEqual(payment.status, SUCCESS)
        self.assertEqual(payment.destination, HOLDINGS)
        service_fee = records.get(
            payee__isnull=True,
            payer__isnull=True,
            source=RESERVE,
            destination=UNPROCESSED_EARNINGS,
        )
        self.assertEqual(service_fee.amount, Money("2.00", "USD"))
        self.assertEqual(service_fee.category, TABLE_HANDLING)
        self.assertEqual(
            sorted([str(target.target) for target in service_fee.targets.all()]),
            sorted([str(self.deliverable), str(self.deliverable.invoice)]),
        )
        mock_withdraw.assert_called_with(self.deliverable.order.seller.id)

    def test_refund_escrow_disabled(self, _mock_notify):
        self.deliverable.escrow_enabled = False
        self.deliverable.save()
        self.state_assertion("seller", "refund/", initial_status=REVIEW)
        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.status, REFUNDED)
        self.assertEqual(TransactionRecord.objects.all().count(), 0)

    def test_refund_cash_staffer(self, _mock_stripe):
        record = TransactionRecordFactory.create(
            payee=self.deliverable.order.seller,
            payer=self.deliverable.order.buyer,
            amount=Money("15.00", "USD"),
            source=CASH_DEPOSIT,
            destination=ESCROW,
            remote_ids=[],
        )
        targets = [
            ref_for_instance(self.deliverable),
            ref_for_instance(self.deliverable.invoice),
        ]
        record.targets.set(targets)
        self.state_assertion("staffer", "refund/", initial_status=DISPUTED)
        refund_transaction = TransactionRecord.objects.get(
            status=SUCCESS,
            payee=self.deliverable.order.buyer,
            payer=self.deliverable.order.seller,
            source=ESCROW,
            destination=CASH_DEPOSIT,
        )
        self.assertEqual(refund_transaction.amount, Money("15.00", "USD"))
        self.assertEqual(refund_transaction.category, ESCROW_REFUND)
        self.assertEqual(refund_transaction.remote_ids, [])
        self.assertCountEqual(list(refund_transaction.targets.all()), targets)

    @freeze_time("2023-01-01")
    @patch("apps.sales.utils.stripe")
    @override_settings(
        PREMIUM_PERCENTAGE_FEE=Decimal("5"), PREMIUM_STATIC_FEE=Decimal("0.10")
    )
    def test_refund_card_seller(self, mock_stripe, _mock_notify):
        mock_stripe.__enter__.return_value.Refund.create.return_value = {
            "id": "refund123"
        }
        card = CreditCardTokenFactory.create()
        record = TransactionRecordFactory.create(
            card=card,
            payee=self.deliverable.order.seller,
            payer=self.deliverable.order.buyer,
            amount=Money("15.00", "USD"),
            source=CARD,
            destination=ESCROW,
            remote_ids=["pi_1234"],
        )
        targets = [
            ref_for_instance(self.deliverable),
            ref_for_instance(self.deliverable.invoice),
        ]
        record.targets.set(targets)
        self.state_assertion(
            "seller", "refund/", initial_status=DISPUTED, target_status=REFUNDED
        )
        refund_transaction = TransactionRecord.objects.get(
            status=SUCCESS,
            payee=self.deliverable.order.buyer,
            payer=self.deliverable.order.seller,
            source=ESCROW,
            destination=CARD,
        )
        self.assertEqual(self.deliverable.refunded_on, timezone.now())
        self.assertEqual(refund_transaction.amount, Money("15.00", "USD"))
        self.assertEqual(refund_transaction.category, ESCROW_REFUND)
        self.assertCountEqual(refund_transaction.remote_ids, ["pi_1234", "refund123"])
        self.assertCountEqual(list(refund_transaction.targets.all()), targets)
        mock_stripe.__enter__.return_value.Refund.create.assert_called_with(
            amount=1500, payment_intent="pi_1234"
        )

    @patch("apps.sales.utils.stripe")
    @override_settings(
        PREMIUM_PERCENTAGE_FEE=Decimal("5"), PREMIUM_STATIC_FEE=Decimal("0.10")
    )
    def test_refund_card_seller_exception(self, mock_stripe, _mock_notify):
        mock_stripe.__enter__.return_value.Refund.create.side_effect = (
            InvalidRequestError("Failed!", param=["test"])
        )
        card = CreditCardTokenFactory.create()
        record = TransactionRecordFactory.create(
            card=card,
            payee=self.deliverable.order.seller,
            payer=self.deliverable.order.buyer,
            amount=Money("15.00", "USD"),
            source=CARD,
            destination=ESCROW,
            remote_ids=["pi_1234"],
        )
        targets = [
            ref_for_instance(self.deliverable),
            ref_for_instance(self.deliverable.invoice),
        ]
        record.targets.set(targets)
        self.state_assertion(
            "seller",
            "refund/",
            initial_status=DISPUTED,
            target_response_code=status.HTTP_400_BAD_REQUEST,
        )
        refund_transaction = TransactionRecord.objects.get(
            status=FAILURE,
            payee=self.deliverable.order.buyer,
            payer=self.deliverable.order.seller,
            source=ESCROW,
            destination=CARD,
        )
        self.assertEqual(refund_transaction.amount, Money("15.00", "USD"))
        self.assertEqual(refund_transaction.category, ESCROW_REFUND)
        self.assertEqual(refund_transaction.remote_ids, ["pi_1234"])
        self.assertCountEqual(list(refund_transaction.targets.all()), targets)
        self.assertEqual(refund_transaction.response_message, "Failed!")
        mock_stripe.__enter__.return_value.Refund.create.assert_called_with(
            amount=1500, payment_intent="pi_1234"
        )

    def test_refund_card_buyer(self, _mock_notify):
        self.state_assertion(
            "buyer", "refund/", status.HTTP_403_FORBIDDEN, initial_status=DISPUTED
        )

    def test_refund_card_outsider(self, _mock_notify):
        self.state_assertion(
            "outsider", "refund/", status.HTTP_403_FORBIDDEN, initial_status=DISPUTED
        )

    @patch("apps.sales.utils.refund_payment_intent")
    def test_refund_card_staffer_stripe(self, mock_refund_transaction, _mock_notify):
        card = CreditCardTokenFactory.create()
        self.deliverable.processor = STRIPE
        self.deliverable.save()
        record = TransactionRecordFactory.create(
            payee=self.deliverable.order.seller,
            payer=self.deliverable.order.buyer,
            card=card,
            remote_ids=["pi_123546"],
        )
        record.targets.add(ref_for_instance(self.deliverable))
        mock_refund_transaction.return_value = {"id": "123456"}
        self.state_assertion("staffer", "refund/", initial_status=DISPUTED)
        record.refresh_from_db()

    def test_approve_deliverable_seller_fail(self, _mock_notify):
        self.state_assertion(
            "seller", "approve/", status.HTTP_403_FORBIDDEN, initial_status=REVIEW
        )

    def test_approve_deliverable_outsider_fail(self, _mock_notify):
        self.state_assertion(
            "outsider", "approve/", status.HTTP_403_FORBIDDEN, initial_status=REVIEW
        )

    def test_approve_deliverable_seller(self, _mock_notify):
        self.state_assertion(
            "seller", "approve/", status.HTTP_403_FORBIDDEN, initial_status=REVIEW
        )

    def test_approve_deliverable_staffer(self, _mock_notify):
        record = TransactionRecordFactory.create(
            payee=self.deliverable.order.seller,
            payer=self.deliverable.order.buyer,
            amount=Money("15.00", "USD"),
        )
        record.targets.add(ref_for_instance(self.deliverable))
        self.state_assertion("staffer", "approve/", initial_status=REVIEW)
        record.refresh_from_db()

    def test_claim_deliverable_staffer(self, _mock_notify):
        revision = RevisionFactory.create(deliverable=self.deliverable)
        reference = ReferenceFactory.create()
        reference.deliverables.add(self.deliverable)
        self.state_assertion("staffer", "claim/", initial_status=DISPUTED)
        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.arbitrator, self.staffer)
        self.assertEqual(
            Subscription.objects.filter(
                subscriber=self.staffer,
                object_id=self.deliverable.id,
                content_type=ContentType.objects.get_for_model(Deliverable),
                type__in=[COMMENT, REVISION_UPLOADED, ORDER_UPDATE],
                email=True,
            ).count(),
            3,
        )
        self.assertEqual(
            Subscription.objects.filter(
                subscriber=self.staffer,
                object_id=revision.id,
                content_type=ContentType.objects.get_for_model(revision),
                type__in=[COMMENT, REVISION_APPROVED],
                email=True,
            ).count(),
            2,
        )
        self.assertTrue(
            Subscription.objects.filter(
                subscriber=self.staffer,
                object_id=reference.id,
                content_type=ContentType.objects.get_for_model(reference),
                type=COMMENT,
                email=True,
            ).exists()
        )

    def test_claim_deliverable_staffer_claimed_already(self, _mock_notify):
        arbitrator = UserFactory.create(is_staff=True)
        self.deliverable.arbitrator = arbitrator
        self.deliverable.save()
        self.state_assertion(
            "staffer", "claim/", status.HTTP_403_FORBIDDEN, initial_status=DISPUTED
        )
        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.arbitrator, arbitrator)

    def test_claim_deliverable_buyer(self, _mock_notify):
        self.state_assertion(
            "buyer", "claim/", status.HTTP_403_FORBIDDEN, initial_status=DISPUTED
        )

    def test_claim_deliverable_seller(self, _mock_notify):
        self.state_assertion(
            "seller", "claim/", status.HTTP_403_FORBIDDEN, initial_status=DISPUTED
        )

    @freeze_time("2019-02-01 12:00:00")
    def test_file_dispute_buyer_enough_time(self, _mock_notify):
        self.deliverable.dispute_available_on = date(year=2019, month=1, day=1)
        self.deliverable.save()
        self.state_assertion(
            "buyer", "dispute/", status.HTTP_200_OK, initial_status=IN_PROGRESS
        )

    @freeze_time("2019-02-01 12:00:00")
    def test_file_dispute_buyer_no_escrow(self, _mock_notify):
        self.deliverable.dispute_available_on = date(year=2019, month=1, day=1)
        self.deliverable.escrow_enabled = False
        self.deliverable.save()
        self.state_assertion(
            "buyer", "dispute/", status.HTTP_403_FORBIDDEN, initial_status=IN_PROGRESS
        )

    @freeze_time("2019-01-01 12:00:00")
    def test_file_dispute_buyer_too_early(self, _mock_notify):
        self.deliverable.dispute_available_on = date(year=2019, month=5, day=3)
        self.deliverable.save()
        self.state_assertion(
            "buyer", "dispute/", status.HTTP_403_FORBIDDEN, initial_status=IN_PROGRESS
        )

    def test_file_dispute_seller(self, _mock_notify):
        self.state_assertion(
            "seller", "dispute/", status.HTTP_403_FORBIDDEN, initial_status=REVIEW
        )

    def test_file_dispute_outsider_fail(self, _mock_notify):
        self.state_assertion(
            "outsider", "dispute/", status.HTTP_403_FORBIDDEN, initial_status=REVIEW
        )


class TestDeliverableAdjustments(APITestCase):
    def test_adjust_turnaround(self):
        deliverable = DeliverableFactory.create(
            product__expected_turnaround=1,
            adjustment_expected_turnaround=0,
        )
        self.login(deliverable.order.seller)
        response = self.client.patch(
            f"/api/sales/v1/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/",
            {"adjustment_expected_turnaround": 1},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.adjustment_expected_turnaround, 1)

    @override_settings(MINIMUM_TURNAROUND=Decimal("1"))
    def test_adjust_turnaround_violates_minimum(self):
        deliverable = DeliverableFactory.create(
            product__expected_turnaround=1,
            adjustment_expected_turnaround=0,
        )
        self.login(deliverable.order.seller)
        response = self.client.patch(
            f"/api/sales/v1/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/",
            {"adjustment_expected_turnaround": -1},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["adjustment_expected_turnaround"],
            ["Expected turnaround may not be less than 1"],
        )

    def test_adjust_revisions(self):
        deliverable = DeliverableFactory.create(
            product__revisions=1,
            adjustment_revisions=0,
        )
        self.login(deliverable.order.seller)
        response = self.client.patch(
            f"/api/sales/v1/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/",
            {"adjustment_revisions": 1},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.adjustment_revisions, 1)

    def test_adjust_revisions_violates_minimum(self):
        deliverable = DeliverableFactory.create(
            product__revisions=1,
            adjustment_revisions=0,
        )
        self.login(deliverable.order.seller)
        response = self.client.patch(
            f"/api/sales/v1/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/",
            {"adjustment_revisions": -2},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["adjustment_revisions"],
            ["Total revisions may not be less than 0."],
        )

    def test_adjust_task_weight(self):
        deliverable = DeliverableFactory.create(
            product__task_weight=1,
            adjustment_task_weight=0,
        )
        self.login(deliverable.order.seller)
        response = self.client.patch(
            f"/api/sales/v1/order/{deliverable.order.id}/deliverables/"
            f"{deliverable.id}/",
            {"adjustment_task_weight": 1},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.adjustment_task_weight, 1)

    def test_adjust_task_weight_violates_minimum(self):
        deliverable = DeliverableFactory.create(
            product__task_weight=1,
            adjustment_task_weight=0,
        )
        self.login(deliverable.order.seller)
        response = self.client.patch(
            f"/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/",
            {"adjustment_task_weight": -1},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["adjustment_task_weight"],
            ["Task weight may not be less than 1."],
        )

    def test_deliverable_not_visible(self):
        deliverable = DeliverableFactory.create(status=LIMBO)
        self.login(deliverable.order.seller)
        response = self.client.get(
            f"/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_deliverable_visible_to_buyer(self):
        deliverable = DeliverableFactory.create(status=LIMBO)
        self.login(deliverable.order.buyer)
        response = self.client.get(
            f"/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
