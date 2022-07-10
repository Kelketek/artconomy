import csv
from decimal import Decimal
from io import StringIO
from pprint import pformat

import dateutil
import requests
from django.conf import settings

from django.db import transaction
from django.db.transaction import atomic
from django.utils import timezone
from moneyed import Money, get_currency
from requests.auth import HTTPBasicAuth
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.lib.models import ref_for_instance, TRANSFER_FAILED
from apps.lib.utils import notify
from apps.profiles.models import User, IN_SUPPORTED_COUNTRY
from apps.sales.apis import STRIPE
from apps.sales.models import Invoice, Deliverable, TransactionRecord, CreditCardToken, \
    StripeAccount, NEW, PAYMENT_PENDING, WebhookRecord
from apps.sales.stripe import stripe
from apps.sales.tasks import withdraw_all
from apps.sales.utils import UserPaymentException, invoice_post_payment
from apps.sales.views.views import logger


@transaction.atomic
def handle_charge_event(event, successful=True):
    charge_event = event['data']['object']
    metadata = charge_event['metadata']
    amount = Money(
        (Decimal(charge_event['amount']) / Decimal('100')).quantize(Decimal('0.00')),
        charge_event['currency'].upper(),
    )
    if 'invoice_id' in metadata:
        invoice = Invoice.objects.get(id=metadata['invoice_id'])
        if successful:
            if invoice.current_intent != charge_event['payment_intent']:
                raise UserPaymentException(
                    f'Mismatched intent ID! What happened? Received ID was '
                    f'{charge_event["payment_intent"]} while current intent is {invoice.current_intent}'
                )

        if successful and (amount != invoice.total()):
            raise UserPaymentException(
                f'Mismatched amount! Customer paid {amount} while total was {invoice.total()}',
            )
        records = invoice_post_payment(
            invoice, {
                'amount': amount,
                'successful': successful,
                'stripe_event': event,
            },
        )
    else:
        logger.warning('Charge for unknown item:')
        logger.warning(pformat(event))
        return
    if successful and metadata.get('save_card') == 'True':
        user = User.objects.get(stripe_token=charge_event['customer'])
        details = charge_event['payment_method_details']['card']
        card, _created = CreditCardToken.objects.get_or_create(
            user=user, last_four=details['last4'],
            stripe_token=charge_event['payment_method'],
            type=CreditCardToken.TYPE_TRANSLATION[details['brand']],
            defaults={'cvv_verified': True},
        )
        if not user.primary_card or (metadata.get('make_primary') == 'True'):
            user.primary_card_id = card.id
            user.save(update_fields=['primary_card'])
        TransactionRecord.objects.filter(id__in=[record.id for record in records]).update(card=card)


def charge_succeeded(event):
    if not event['data']['object']['captured']:
        # In-person cards have a separate authorization and capture flow.
        with stripe as stripe_api:
            stripe_api.PaymentIntent.capture(
                event['data']['object']['payment_intent']
            )
            return
    handle_charge_event(event, successful=True)


def charge_failed(event):
    try:
        handle_charge_event(event, successful=False)
    except UserPaymentException:
        pass


def charge_captured(event):
    charge_succeeded(event)


@transaction.atomic
def account_updated(event):
    account_data = event['data']['object']
    account = StripeAccount.objects.get(token=account_data['id'])
    account.active = account_data['payouts_enabled']
    account.save()
    if account.active:
        Deliverable.objects.filter(
            order__seller=account.user, status__in=[NEW, PAYMENT_PENDING],
        ).update(processor=STRIPE)
        account.user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        account.user.artist_profile.save()
        withdraw_all.delay(account.user.id)


@atomic
def pull_and_reconcile_report(report):
    """
    Given a Stripe ReportRun object as specified by payout_paid,
    fetch the report file and then update our database with the transfer information.
    """
    result = requests.get(report.result['url'], auth=HTTPBasicAuth(settings.STRIPE_KEY, ''))
    result.raise_for_status()
    reader = csv.DictReader(StringIO(result.content.decode('utf-8')))
    for row in reader:
        # In reality, this should only ever be one row.
        if not row['source_id']:
            raise RuntimeError('No source ID!')
        record = TransactionRecord.objects.get(
            remote_ids__contains=row['source_id'] + '', source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK,
        )
        if row['automatic_payout_effective_at_utc']:
            timestamp = dateutil.parser.isoparse(row['automatic_payout_effective_at_utc'])
            timestamp = timestamp.replace(tzinfo=dateutil.tz.UTC)
        else:
            timestamp = timezone.now()
        record.finalized_on = timestamp
        record.status = TransactionRecord.SUCCESS
        record.save()
        currency = get_currency(row['currency'].upper())
        amount = Money(Decimal(row['gross']), currency)
        new_record = TransactionRecord.objects.get_or_create(
            remote_ids=record.remote_ids, amount=amount,
            payer=record.payer, payee=record.payee, source=TransactionRecord.PAYOUT_MIRROR_SOURCE,
            destination=TransactionRecord.PAYOUT_MIRROR_DESTINATION, status=TransactionRecord.SUCCESS,
            category=TransactionRecord.CASH_WITHDRAW,
            created_on=record.created_on, finalized_on=timestamp,
        )[0]
        new_record.targets.add(*record.targets.all())
        new_record.targets.add(ref_for_instance(record))


@atomic
def payout_paid(event):
    """
    Stripe webhook for the payout.paid event. Unfortunately the payout information does not give us a full enough
    picture for what we want. So we force a report generation, and then fetch the result of this information to get
    the remaining info.
    """
    payout_data = event['data']['object']
    with stripe as stripe_api:
        report = stripe_api.reporting.ReportRun.create(
            report_type='connected_account_payout_reconciliation.by_id.itemized.4',
            parameters={
                'payout': payout_data['id'],
                'connected_account': event['account'],
                'columns': [
                    'source_id',
                    'gross',
                    'net',
                    'fee',
                    'currency',
                    'automatic_payout_effective_at_utc',
                ]
            }
        )
        if report.result:
            # This might happen if the request appeared to fail but actually succeeded silently.
            pull_and_reconcile_report(report)


def transfer_failed(event):
    """
    Webhook for the transfer failed event from Stripe.
    """
    transfer = event['data']['object']['id']
    records = TransactionRecord.objects.filter(
        remote_ids=transfer,
    )
    records.update(status=TransactionRecord.FAILURE)
    record = records.order_by('created_on')[0]
    notify(
        TRANSFER_FAILED,
        record.payer,
        data={
            'error': 'The bank rejected the transfer. Please try again, update your account information, '
                     'or contact support.'
        }
    )


def reconcile_payout_report(event):
    """
    This event handles a webhook for the specific report type we run to reconcile payouts with our own reporting.
    """
    pull_and_reconcile_report(event['data']['object'])


@transaction.atomic
def payment_method_attached(event):
    card_info = event['data']['object']
    if not card_info['type'] == 'card':
        logger.warning('Attached unknown payment type:', card_info['type'])
        logger.warning(pformat(event))
        raise NotImplementedError
    user = User.objects.get(stripe_token=card_info['customer'])
    card, _created = CreditCardToken.objects.get_or_create(
        user=user,
        stripe_token=card_info['id'],
        last_four=card_info['card']['last4'],
        type=CreditCardToken.TYPE_TRANSLATION[card_info['card']['brand']],
        defaults={'cvv_verified': True},
    )
    if not user.primary_card:
        user.primary_card = card
        user.save(update_fields=['primary_card'])


REPORT_ROUTES = {
    'connected_account_payout_reconciliation.by_id.itemized.4': reconcile_payout_report,
}


def reporting_report_run_succeeded(event):
    report_type = event['data']['object']['report_type']
    if report_type in REPORT_ROUTES:
        REPORT_ROUTES[report_type](event)
        return


def spy_failure(event):
    raise NotImplementedError('Bogus failure to trap real-world webhook.')


STRIPE_DIRECT_WEBHOOK_ROUTES = {
    'charge.captured': charge_captured,
    'charge.succeeded': charge_succeeded,
    'charge.failed': charge_failed,
    'transfer.failed': transfer_failed,
    'reporting.report_run.succeeded': reporting_report_run_succeeded,
    'payment_method.attached': payment_method_attached,
}
STRIPE_CONNECT_WEBHOOK_ROUTES = {
    'account.updated': account_updated,
    'payout.paid': payout_paid,
    'payout.failed': spy_failure,
}


class StripeWebhooks(APIView):
    """
    Function for processing stripe webhook events.
    """
    permission_classes = []

    def post(self, request, connect):
        with stripe as stripe_api:
            try:
                sig_header = request.META['HTTP_STRIPE_SIGNATURE']
                secret = WebhookRecord.objects.get(connect=connect).secret
                # If the secret is missing, we cannot verify the signature. Die dramatically until an admin fixes.
                assert secret
                event = stripe_api.Webhook.construct_event(request.body, sig_header, secret)
            except ValueError as err:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': str(err)})
            routes = STRIPE_CONNECT_WEBHOOK_ROUTES if connect else STRIPE_DIRECT_WEBHOOK_ROUTES
            handler = routes.get(event['type'], None)
            if not handler:
                logger.warning('Unsupported event "%s" received from Stripe. Connect is %s', event['type'], connect)
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={'detail': f'Unsupported command "{event["type"]}"'}
                )
            handler(event)
        return Response(status=status.HTTP_204_NO_CONTENT)
