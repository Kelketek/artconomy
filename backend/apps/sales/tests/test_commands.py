from dateutil.relativedelta import relativedelta
from django.core.management import call_command
from django.utils import timezone

from apps.lib.test_resources import EnsurePlansMixin
from django.test import TestCase, override_settings

from apps.profiles.tests.factories import UserFactory
from apps.sales.constants import REFUNDED, COMPLETED, IN_PROGRESS, NEW
from apps.sales.tests.factories import DeliverableFactory


class TestMarkRedactionAvailability(EnsurePlansMixin, TestCase):
    @override_settings(REDACTION_ALLOWED_WINDOW=1)
    def test_mark_sales(self):
        buyer = UserFactory.create()
        seller = UserFactory.create()
        finalized_on = timezone.now() - relativedelta(days=5)
        should_set = [
            DeliverableFactory.create(
                status=REFUNDED,
                refunded_on=finalized_on,
                escrow_enabled=True,
                order__buyer=buyer,
                order__seller=seller,
            ),
            DeliverableFactory.create(
                status=COMPLETED,
                finalized_on=finalized_on,
                escrow_enabled=True,
                order__buyer=buyer,
                order__seller=seller,
            ),
            DeliverableFactory.create(
                status=COMPLETED,
                finalized_on=None,
                escrow_enabled=False,
                order__buyer=buyer,
                order__seller=seller,
            ),
        ]
        should_not_set = [
            DeliverableFactory.create(
                status=IN_PROGRESS,
                finalized_on=timezone.now(),
                escrow_enabled=True,
                order__buyer=buyer,
                order__seller=seller,
            ),
            DeliverableFactory.create(
                status=NEW,
                finalized_on=None,
                escrow_enabled=True,
                order__buyer=buyer,
                order__seller=seller,
            ),
        ]
        call_command("mark_redaction_availability")
        for item in should_set:
            item.refresh_from_db()
            if item.redact_available_on is None:
                raise AssertionError(
                    f"Failed with status {item.get_status_display()} "
                    f"and finalization on {item.finalized_on} with "
                    f"escrow_enabled status {item.escrow_enabled}"
                )
        for item in should_not_set:
            item.refresh_from_db()
            if item.redact_available_on is not None:
                raise AssertionError(
                    f"Found inappropriate redaction with "
                    f"status {item.get_status_display()} "
                    f"and finalization on {item.finalized_on} with "
                    f"escrow_enabled status {item.escrow_enabled}"
                )
