from datetime import timedelta

from django.db.models import F
from django.utils import timezone

from django.conf import settings
from django.core.management import BaseCommand

from apps.sales.constants import CANCELLED, COMPLETED, REFUNDED
from apps.sales.models import Deliverable


class Command(BaseCommand):
    def handle(self, *args, **options):
        base_qs = Deliverable.objects.filter(redacted_on=None).exclude(
            redact_available_on__isnull=True,
        )
        base_qs.filter(status=CANCELLED).update(redact_available_on=timezone.now())
        base_qs.filter(status__in=[COMPLETED, REFUNDED], escrow_enabled=False).update(
            redact_available_on=timezone.now(),
        )
        base_qs.filter(
            status=COMPLETED,
            escrow_enabled=True,
        ).update(
            redact_available_on=F("finalized_on")
            + timedelta(days=settings.REDACTION_ALLOWED_WINDOW)
        )
        base_qs.filter(
            status=REFUNDED,
            escrow_enabled=True,
        ).update(
            redact_available_on=F("refunded_on")
            + timedelta(days=settings.REDACTION_ALLOWED_WINDOW)
        )
