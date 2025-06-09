"""
Tests for admin utility functions.
"""

from unittest.mock import Mock, patch

from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time
from moneyed import Money

from apps.lib.models import ref_for_instance
from apps.lib.test_resources import EnsurePlansMixin, DeliverableChargeMixin
from apps.lib.utils import FakeRequest
from apps.profiles.tests.factories import UserFactory
from apps.sales.admin import kill_fraudulent
from apps.sales.constants import (
    DELIVERABLE_STATUSES,
    CANCELLED,
    CARD,
    FUND,
    SUCCESS,
    ESCROW_REFUND,
    PAYOUT_ACCOUNT,
    HOLDINGS,
    ESCROW,
)
from apps.sales.models import Deliverable, TransactionRecord
from apps.sales.tests.factories import DeliverableFactory, StripeAccountFactory
from apps.sales.utils import finalize_deliverable


class TestKillFraudulent(EnsurePlansMixin, TestCase, DeliverableChargeMixin):
    def test_cancels_non_escrow(self):
        deliverables = [
            DeliverableFactory.create(status=deliverable_status, escrow_enabled=False)
            for deliverable_status, _ in DELIVERABLE_STATUSES
        ]
        staffer = UserFactory.create(is_staff=True, is_superuser=True)
        kill_fraudulent(Mock(), FakeRequest(user=staffer), Deliverable.objects.all())
        for deliverable in deliverables:
            deliverable.refresh_from_db()
            self.assertEqual(deliverable.status, CANCELLED)

    def test_kills_users(self):
        deliverable = DeliverableFactory.create()
        staffer = UserFactory.create(
            is_staff=True,
            is_superuser=True,
        )
        kill_fraudulent(Mock(), FakeRequest(user=staffer), Deliverable.objects.all())
        deliverable.refresh_from_db()
        self.assertFalse(deliverable.order.buyer.is_active)
        self.assertFalse(deliverable.order.seller.is_active)
        self.assertFalse(deliverable.order.seller.artist_profile.auto_withdraw)

    def verify_forced_refund_transactions(self, *, deliverable, mock_stripe):
        targets = [
            ref_for_instance(deliverable),
            ref_for_instance(deliverable.invoice),
        ]
        fund_transaction = TransactionRecord.objects.get(
            status=SUCCESS,
            payee=deliverable.order.buyer,
            payer=deliverable.order.buyer,
            source=CARD,
            destination=FUND,
        )
        refund_transaction = TransactionRecord.objects.get(
            status=SUCCESS,
            payee=deliverable.order.buyer,
            payer=deliverable.order.buyer,
            source=FUND,
            destination=CARD,
        )
        self.assertEqual(refund_transaction.amount, fund_transaction.amount)
        self.assertEqual(deliverable.refunded_on, timezone.now())
        self.assertEqual(refund_transaction.amount, Money("15.00", "USD"))
        self.assertEqual(refund_transaction.category, ESCROW_REFUND)
        self.assertCountEqual(
            refund_transaction.remote_ids,
            [
                "pi_12345",
                "refund123",
                "txn_test_balance",
            ],
        )
        self.assertCountEqual(list(refund_transaction.targets.all()), targets)
        mock_stripe.__enter__.return_value.Refund.create.assert_called_with(
            amount=1500, payment_intent="pi_12345"
        )

    @freeze_time("2023-01-01")
    @patch("apps.sales.utils.stripe")
    def test_reverses_transactions_for_queued(self, mock_stripe):
        mock_stripe.__enter__.return_value.Refund.create.return_value = {
            "id": "refund123"
        }
        deliverable = DeliverableFactory.create(escrow_enabled=True)
        self.charge_transaction(deliverable, source=CARD)
        staffer = UserFactory.create(
            is_staff=True,
            is_superuser=True,
        )
        kill_fraudulent(Mock(), FakeRequest(user=staffer), Deliverable.objects.all())
        deliverable.refresh_from_db()
        self.verify_forced_refund_transactions(
            deliverable=deliverable,
            mock_stripe=mock_stripe,
        )

    @freeze_time("2023-01-01")
    @patch("apps.sales.utils.stripe")
    def test_reverses_transactions_for_completed(self, mock_stripe):
        mock_stripe.__enter__.return_value.Refund.create.return_value = {
            "id": "refund123"
        }
        deliverable = DeliverableFactory.create(escrow_enabled=True)
        StripeAccountFactory.create(user=deliverable.order.seller, active=True)
        self.charge_transaction(deliverable, source=CARD)
        with patch("apps.sales.tasks.stripe") as task_mock_stripe:
            task_mock_stripe.__enter__.return_value.Transfer.create.return_value = {
                "id": "tr_12345",
                "destination_payment": "py_12345",
                "balance_transaction": "txn_12345",
            }
            finalize_deliverable(deliverable, deliverable.order.buyer)
        staffer = UserFactory.create(
            is_staff=True,
            is_superuser=True,
        )
        with patch("apps.sales.admin.stripe") as other_mock_stripe:
            other_mock_stripe.__enter__.return_value.Transfer.create_reversal.return_value = {
                "id": "trr_12345"
            }
            kill_fraudulent(
                Mock(), FakeRequest(user=staffer), Deliverable.objects.all()
            )
        deliverable.refresh_from_db()
        self.verify_forced_refund_transactions(
            deliverable=deliverable,
            mock_stripe=mock_stripe,
        )
        record = TransactionRecord.objects.get(
            source=PAYOUT_ACCOUNT,
            destination=HOLDINGS,
        )
        self.assertEqual(record.status, SUCCESS)
        self.assertEqual(record.payer, deliverable.order.seller)
        self.assertEqual(record.payee, deliverable.order.seller)
        self.assertIn("trr_12345", record.remote_ids)
        self.assertEqual(record.amount, Money("13.05", "USD"))
        record = TransactionRecord.objects.get(
            source=HOLDINGS,
            destination=ESCROW,
        )
        self.assertEqual(record.status, SUCCESS)
        self.assertEqual(record.payer, deliverable.order.seller)
        self.assertEqual(record.payee, deliverable.order.seller)
        self.assertIn("pi_12345", record.remote_ids)
        self.assertEqual(record.amount, Money("13.05", "USD"))
