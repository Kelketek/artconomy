from apps.profiles.models import ArtistProfile, User
from apps.sales.constants import REFUNDED, COMPLETED, QUEUED, REVIEW, PAID
from apps.sales.models import StripeAccount, Order, Invoice, Deliverable
from apps.sales.utils import update_availability
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Marks all verified adults."

    def handle(self, *args, **options):
        User.objects.filter(stripe_account__active=True).update(verified_adult=True)
        for deliverable in Deliverable.objects.filter(
            escrow_enabled=True,
            status__in=[QUEUED, REVIEW, COMPLETED, REFUNDED],
            order__buyer__isnull=False,
        ):
            deliverable.order.buyer.verified_adult = True
            deliverable.order.buyer.save()
        for invoice in Invoice.objects.filter(
            status=PAID, bill_to__isnull=False
        ).exclude(paypal_token=""):
            invoice.bill_to.verified_adult = True
            invoice.bill_to.save()
