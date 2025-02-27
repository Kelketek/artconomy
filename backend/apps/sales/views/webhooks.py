import csv
import json
import logging
from decimal import Decimal
from io import StringIO
from pprint import pformat
from typing import Callable

import dateutil
import requests
from rest_framework.generics import get_object_or_404

from apps.lib.models import ref_for_instance
from apps.lib.constants import TRANSFER_FAILED
from apps.lib.utils import notify
from apps.profiles.models import IN_SUPPORTED_COUNTRY, User
from apps.sales.constants import (
    BANK,
    CASH_WITHDRAW,
    FAILURE,
    HOLDINGS,
    NEW,
    PAYMENT_PENDING,
    PAYOUT_MIRROR_DESTINATION,
    PAYOUT_MIRROR_SOURCE,
    PAYOUT_REVERSAL,
    STRIPE,
    SUCCESS,
    TYPE_TRANSLATION,
    TIP,
)
from apps.sales.models import (
    CreditCardToken,
    Deliverable,
    Invoice,
    StripeAccount,
    TransactionRecord,
    WebhookRecord,
    PaypalConfig,
    LineItem,
    WebhookEventRecord,
)
from apps.sales.paypal import (
    validate_paypal_request,
    reconcile_invoices,
)
from apps.sales.stripe import stripe
from apps.sales.tasks import withdraw_all
from apps.sales.utils import (
    UserPaymentException,
    invoice_post_payment,
    mark_deliverable_paid,
    cancel_deliverable,
    refund_deliverable,
)
from django.conf import settings
from django.db import transaction
from django.db.transaction import atomic
from django.utils import timezone
from moneyed import Money, get_currency
from requests.auth import HTTPBasicAuth
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from stripe.error import SignatureVerificationError


logger = logging.getLogger(__name__)


def handle_charge_event(event, successful=True):
    charge_event = event["data"]["object"]
    metadata = charge_event["metadata"]
    amount = Money(
        (Decimal(charge_event["amount"]) / Decimal("100")).quantize(Decimal("0.00")),
        charge_event["currency"].upper(),
    )
    if "invoice_id" in metadata:
        invoice = Invoice.objects.get(id=metadata["invoice_id"])
        if successful:
            if invoice.current_intent != charge_event["payment_intent"]:
                raise UserPaymentException(
                    f"Mismatched intent ID! What happened? Received ID was "
                    f'{charge_event["payment_intent"]} while current intent is '
                    f"{invoice.current_intent}"
                )

        if successful and (amount != invoice.total()):
            raise UserPaymentException(
                f"Mismatched amount! Customer paid {amount} while total was "
                f"{invoice.total()}",
            )
        records = invoice_post_payment(
            invoice,
            {
                "amount": amount,
                "successful": successful,
                "stripe_event": event,
            },
        )
    else:
        logger.warning("Charge for unknown item:")
        logger.warning(pformat(event))
        return
    if successful and metadata.get("save_card") == "True":
        user = User.objects.get(stripe_token=charge_event["customer"])
        details = charge_event["payment_method_details"]["card"]
        card, _created = CreditCardToken.objects.update_or_create(
            stripe_token=charge_event["payment_method"],
            defaults={
                "cvv_verified": True,
                "type": TYPE_TRANSLATION[details["brand"]],
                "last_four": details["last4"],
            },
            create_defaults={"user": user},
        )
        if not user.primary_card or (metadata.get("make_primary") == "True"):
            user.primary_card_id = card.id
            user.save(update_fields=["primary_card"])
        TransactionRecord.objects.filter(
            id__in=[record.id for record in records]
        ).update(card=card)


def charge_succeeded(event):
    if not event["data"]["object"]["captured"]:
        # In-person cards have a separate authorization and capture flow.
        with stripe as stripe_api:
            stripe_api.PaymentIntent.capture(event["data"]["object"]["payment_intent"])
            return
    handle_charge_event(event, successful=True)


def charge_failed(event):
    handle_charge_event(event, successful=False)


@transaction.atomic
def account_updated(event):
    account_data = event["data"]["object"]
    account = StripeAccount.objects.get(token=account_data["id"])
    account.active = account_data["payouts_enabled"]
    account.save()
    if account.active:
        Deliverable.objects.filter(
            order__seller=account.user,
            status__in=[NEW, PAYMENT_PENDING],
        ).update(processor=STRIPE)
        account.user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        account.user.artist_profile.save()
        account.user.verified_adult = True
        account.user.save()
        withdraw_all.delay(account.user.id)


def pull_and_reconcile_payout_report(event, report):
    """
    Given a Stripe ReportRun object as specified by payout_paid,
    fetch the report file and then update our database with the transfer information.
    """
    result = requests.get(
        report["result"]["url"], auth=HTTPBasicAuth(settings.STRIPE_KEY, "")
    )
    result.raise_for_status()
    reader = csv.DictReader(StringIO(result.content.decode("utf-8")))
    # In reality, this should only ever be one row.
    for row in reader:
        parameters = event["data"]["object"]["parameters"]
        currency = get_currency(row["currency"].upper())
        amount = Money(Decimal(row["gross"]), currency)
        old_source = HOLDINGS
        old_destination = BANK
        new_source = PAYOUT_MIRROR_SOURCE
        new_destination = PAYOUT_MIRROR_DESTINATION
        category = CASH_WITHDRAW
        if amount < Money("0", currency):
            new_source, new_destination = new_destination, new_source
            old_source, old_destination = old_destination, old_source
            amount = abs(amount)
            category = PAYOUT_REVERSAL
        try:
            record = TransactionRecord.objects.get(
                remote_ids__contains=row["source_id"] + "",
                source=old_source,
                destination=old_destination,
            )
        except TransactionRecord.DoesNotExist:
            raise TransactionRecord.DoesNotExist(
                f'Could not find corresponding record for {row["source_id"]}.'
                f" It may need to be added manually or may be malformed. Please check "
                f'https://dashboard.stripe.com/{parameters["connected_account"]}/'
                f'payouts/{parameters["payout"]}'
            )
        if row["automatic_payout_effective_at_utc"]:
            timestamp = dateutil.parser.isoparse(
                row["automatic_payout_effective_at_utc"]
            )
            timestamp = timestamp.replace(tzinfo=dateutil.tz.UTC)
        else:
            timestamp = timezone.now()
        record.finalized_on = timestamp
        record.status = SUCCESS
        record.remote_ids.append(parameters["payout"])
        record.remote_ids = list(set(record.remote_ids))
        record.save()
        new_record = TransactionRecord.objects.get_or_create(
            remote_ids=record.remote_ids,
            amount=amount,
            payer=record.payer,
            payee=record.payee,
            source=new_source,
            destination=new_destination,
            status=SUCCESS,
            category=category,
            created_on=record.created_on,
            finalized_on=timestamp,
        )[0]
        new_record.targets.add(*record.targets.all())
        new_record.targets.add(ref_for_instance(record))


def reconcile_payout_report(event):
    """
    This event handles a webhook for the specific report type we run to reconcile
    payouts with our own reporting.

    This function might seem redundant, but it's possible for a report not attached to
    an event to call it. An example of this is found in payout_paid.
    """
    pull_and_reconcile_payout_report(event, event["data"]["object"])


def payout_paid(event):
    """
    Stripe webhook for the payout.paid event. Unfortunately the payout information does
    not give us a full enough picture for what we want. So we force a report generation,
    and then fetch the result of this information to get the remaining info.
    """
    payout_data = event["data"]["object"]
    with stripe as stripe_api:
        stripe_api.reporting.ReportRun.create(
            report_type="connected_account_payout_reconciliation.by_id.itemized.4",
            parameters={
                "payout": payout_data["id"],
                "connected_account": event["account"],
                "columns": [
                    "source_id",
                    "gross",
                    "net",
                    "fee",
                    "currency",
                    "automatic_payout_effective_at_utc",
                ],
            },
        )


def transfer_failed(event):
    """
    Webhook for the transfer failed event from Stripe.
    """
    transfer = event["data"]["object"]["id"]
    records = TransactionRecord.objects.filter(
        remote_ids__contains=transfer,
    )
    records.update(status=FAILURE)
    record = records.order_by("created_on")[0]
    notify(
        TRANSFER_FAILED,
        record.payer,
        data={
            "error": "The bank rejected the transfer. Please try again, update your"
            "account information, or contact support."
        },
    )


def payment_method_attached(event):
    card_info = event["data"]["object"]
    if not card_info["type"] == "card":
        logger.warning("Attached unknown payment type:", card_info["type"])
        logger.warning(pformat(event))
        raise NotImplementedError
    user = User.objects.get(stripe_token=card_info["customer"])
    card, _created = CreditCardToken.objects.get_or_create(
        user=user,
        stripe_token=card_info["id"],
        last_four=card_info["card"]["last4"],
        type=TYPE_TRANSLATION[card_info["card"]["brand"]],
        defaults={"cvv_verified": True},
    )
    updated_fields = ["verified_adult"]
    user.verified_adult = True
    if not user.primary_card:
        user.primary_card = card
        updated_fields.append("primary_card")
    user.save(update_fields=updated_fields)


REPORT_ROUTES = {
    "connected_account_payout_reconciliation.by_id.itemized.4": reconcile_payout_report,
}


def reporting_report_run_succeeded(event):
    report_type = event["data"]["object"]["report_type"]
    if report_type in REPORT_ROUTES:
        REPORT_ROUTES[report_type](event)
        return


def mockable_dummy_event(event):
    """
    Mockable function for automated tests.
    """


def dummy_event(event):
    """
    Fake Stripe event type used in automated tests. We don't mock this directly since
    it's root level and a dict value at once.
    """
    mockable_dummy_event(event)


def mockable_dummy_connect_event(event):
    """
    Mockable function for automated tests.
    """


def dummy_connect_event(event):
    """
    Fake Stripe event used in automated tests. We don't mock this directly since it's
    root level and a dict value
    at once.
    """
    mockable_dummy_connect_event(event)


def mockable_dummy_report_processor(event):
    """
    Mockable function for automated tests.
    """


def dummy_report_processor(event):
    """
    Fake report processor function used in automated tests. We don't mock this directly
    since it's root level and a dict value at once.
    """
    mockable_dummy_report_processor(event)


def invoice_centric(
    wrapped: Callable[[dict, Invoice], None]
) -> Callable[[dict, PaypalConfig], None]:
    def wrapper(event_data: dict, config: PaypalConfig):
        invoice = Invoice.objects.filter(
            paypal_token=event_data["resource"]["invoice"]["id"],
            issued_by=config.user,
        ).first()
        if invoice is None:
            # This is an invoice we're not tracking. Ignore.
            return
        wrapped(event_data, invoice)

    return wrapper


@invoice_centric
def paypal_invoice_paid(event_data: dict, invoice: Invoice):
    """
    Once a PayPal invoice is paid, mark it internally.
    """
    due_amount = Decimal(event_data["resource"]["invoice"]["due_amount"]["value"])
    if due_amount > Decimal(0):
        # Not fully paid yet. Accept event but don't do anything.
        return
    raw_tip = event_data["resource"]["invoice"].get("gratuity", None)
    tip = (raw_tip or Money("0", "USD")) and Money(
        raw_tip["value"],
        raw_tip["currency_code"],
    )
    if tip:
        # Add this to the invoice now that we have it.
        LineItem.objects.update_or_create(
            type=TIP,
            invoice=invoice,
            defaults={
                "amount": tip,
                "frozen_value": tip,
                # Not used, but required by DB schema.
                "destination_account": HOLDINGS,
                "destination_user": invoice.issued_by,
            },
        )
    deliverable = invoice.deliverables.get()
    mark_deliverable_paid(deliverable)


@invoice_centric
def paypal_invoice_cancelled(_event_data: dict, invoice: Invoice):
    cancel_deliverable(invoice.deliverables.get(), requested_by=None, skip_remote=True)


@invoice_centric
def paypal_invoice_refunded(event_data: dict, invoice: Invoice):
    deliverable = invoice.deliverables.get()
    # This should never happen, but just to be sure:
    if deliverable.escrow_enabled:
        raise RuntimeError(
            "PayPal is refunding an escrow invoice! This should not be possible!",
        )
    # See if this is a partial or total refund
    total = event_data["resource"]["invoice"]["amount"]
    refunded = event_data["resource"]["invoice"]["refunds"]["refund_amount"]
    if Money(total["value"], total["currency_code"]) <= Money(
        refunded["value"], refunded["currency_code"]
    ):
        refund_deliverable(deliverable, requesting_user=invoice.issued_by)


@invoice_centric
def paypal_invoice_updated(event_data: dict, invoice: Invoice):
    reconcile_invoices(
        invoice.deliverables.get(),
        event_data["resource"]["invoice"],
    )


STRIPE_DIRECT_WEBHOOK_ROUTES = {
    "charge.captured": charge_succeeded,
    "charge.succeeded": charge_succeeded,
    "charge.failed": charge_failed,
    "transfer.failed": transfer_failed,
    "reporting.report_run.succeeded": reporting_report_run_succeeded,
    "payment_method.attached": payment_method_attached,
}
STRIPE_CONNECT_WEBHOOK_ROUTES = {
    "account.updated": account_updated,
    "payout.paid": payout_paid,
}
PAYPAL_WEBHOOK_ROUTES = {
    "INVOICING.INVOICE.CANCELLED": paypal_invoice_cancelled,
    "INVOICING.INVOICE.PAID": paypal_invoice_paid,
    "INVOICING.INVOICE.REFUNDED": paypal_invoice_refunded,
    "INVOICING.INVOICE.UPDATED": paypal_invoice_updated,
}


if settings.TESTING:
    STRIPE_DIRECT_WEBHOOK_ROUTES["dummy_event"] = dummy_event
    STRIPE_CONNECT_WEBHOOK_ROUTES["dummy_connect_event"] = dummy_connect_event
    REPORT_ROUTES["dummy_report"] = dummy_report_processor


@atomic
def handle_stripe_event(*, body: str = None, connect: bool, event: dict = None):
    """
    Stripe event handler. This does not validate the request is brought from stripe--
    that's handled by the StripeWebhooks view. This function allows an event to be
    run as blessed even without verification, which is useful for testing.
    """
    routes = STRIPE_CONNECT_WEBHOOK_ROUTES if connect else STRIPE_DIRECT_WEBHOOK_ROUTES
    if event is None:
        if body is None:
            raise TypeError("Neither event nor body provided. Both are None.")
        event = json.loads(body)
    key, created = WebhookEventRecord.objects.get_or_create(
        defaults={"data": event},
        event_id=event["id"],
    )
    if not created:
        return Response(status=status.HTTP_204_NO_CONTENT)
    handler = routes.get(event["type"], None)
    if not handler:
        logger.warning(
            'Unsupported event "%s" received from Stripe. Connect is %s',
            event["type"],
            connect,
        )
        key.delete()
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"detail": f'Unsupported command "{event["type"]}"'},
        )
    handler(event)

    return Response(status=status.HTTP_204_NO_CONTENT)


class StripeWebhooks(APIView):
    """
    Function for processing stripe webhook events.
    """

    permission_classes = []

    def post(self, request, connect):
        with stripe as stripe_api:
            try:
                sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
                secret = WebhookRecord.objects.get(connect=connect).secret
                # If the secret is missing, we cannot verify the signature. Die
                # dramatically until an admin fixes.
                assert secret
                event = stripe_api.Webhook.construct_event(
                    request.body, sig_header, secret
                )
            except SignatureVerificationError as err:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST, data={"detail": str(err)}
                )
            return handle_stripe_event(connect=connect, event=event)


class PaypalWebhooks(APIView):
    """
    View for callbacks from PayPal.
    """

    def post(self, request, *, config_id: str):
        config = get_object_or_404(PaypalConfig, id=config_id)
        validate_paypal_request(request, config)
        route = PAYPAL_WEBHOOK_ROUTES.get(request.data["event_type"])
        if not route:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"detail": "Event type not supported."},
            )
        route(request.data, config)
        return Response(status=status.HTTP_204_NO_CONTENT)
