import logging

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.datetime_safe import date
from moneyed import Money
from urllib3.exceptions import HTTPError

from apps.lib.models import RENEWAL_FAILURE, SUBSCRIPTION_DEACTIVATED, RENEWAL_FIXED, TRANSFER_FAILED, ref_for_instance
from apps.lib.utils import notify, send_transaction_email
from apps.profiles.models import User
from apps.sales.apis import dwolla
from apps.sales.authorize import AuthorizeException, charge_saved_card
from apps.sales.dwolla import initiate_withdraw, perform_transfer, TRANSACTION_STATUS_MAP
from apps.sales.models import CreditCardToken, TransactionRecord, REVIEW, NEW, Deliverable, CANCELLED
from apps.sales.utils import service_price, set_service, finalize_deliverable, account_balance, destroy_deliverable
from conf.celery_config import celery_app


logger = logging.getLogger(__name__)


@celery_app.task
def renew(user_id, service, card_id=None):
    user = User.objects.get(id=user_id)
    enabled = getattr(user, service + '_enabled')
    paid_through = getattr(user, service + '_paid_through')
    old = paid_through and paid_through <= date.today()
    if old is None:
        # This should never happen.
        logger.error(
            "!!! {}({}) has NONE for {}_paid_through with {} enabled!".format(user.username, user.id, service, service)
        )
        return
    if not (enabled and old):
        # Fixed between when this task was added and it was executed.
        return
    if card_id:
        card = CreditCardToken.objects.get(id=card_id, user=user, active=True)
    else:
        card = user.primary_card
    if card is None:
        # noinspection PyUnresolvedReferences
        cards = user.credit_cards.filter(active=True).order_by('-created_on')
        if not cards.exists():
            logger.info("{}({}) can't renew due to no card on file.".format(user.username, user.id))
            notify(RENEWAL_FAILURE, user, data={'error': 'No card on file!'}, unique=True)
            return
        card = cards[0]
    price = service_price(user, service)
    record = TransactionRecord.objects.create(
        card=card,
        payer=user,
        payee=None,
        status=TransactionRecord.FAILURE,
        source=TransactionRecord.CARD,
        destination=TransactionRecord.UNPROCESSED_EARNINGS,
        category=TransactionRecord.SUBSCRIPTION_DUES,
        amount=price,
        response_message="Failed when contacting payment processor.",
    )
    record.targets.add(ref_for_instance(user))
    try:
        remote_id, auth_code = charge_saved_card(
            profile_id=card.profile_id, payment_id=card.payment_id, amount=price.amount,
        )
    except AuthorizeException as err:
        record.response_message = str(err)
        record.save()
        notify(
            RENEWAL_FAILURE, user, data={
                'error': "Card ending in {} -- {}".format(card.last_four, record.response_message)}, unique=True
        )
    else:
        record.status = TransactionRecord.SUCCESS
        record.remote_id = remote_id
        record.auth_code = auth_code
        record.finalized = True
        record.response_message = 'Upgraded to {}'.format(service)
        card.cvv_verified = True
        card.save()
        set_service(user, service, target_date=date.today() + relativedelta(months=1))
        record.save()
        if card_id or (paid_through < date.today()):
            # This was called manually or a previous attempt should have been made and there may have been a gap
            # in coverage. In this case, let's inform the user the renewal was successful instead of silently
            # succeeding.
            notify(RENEWAL_FIXED, user, unique=True)


@celery_app.task
def run_billing():
    # Anyone we've not been able to renew for five days, assume won't be renewing automatically.
    users = User.objects.filter(
        Q(portrait_enabled=True, portrait_paid_through__lte=date.today() - relativedelta(days=5)) |
        Q(landscape_enabled=True, landscape_paid_through__lte=date.today() - relativedelta(days=5))
    )
    for user in users:
        logger.info('Deactivated {}({})'.format(user.username, user.id))
        notify(SUBSCRIPTION_DEACTIVATED, user, unique=True)
        user.portrait_enabled = False
        user.landscape_enabled = False
        user.save()
    users = User.objects.filter(portrait_enabled=True, portrait_paid_through__lte=date.today())
    for user in users:
        renew.delay(user.id, 'portrait')
    users = User.objects.filter(landscape_enabled=True, landscape_paid_through__lte=date.today())
    for user in users:
        renew.delay(user.id, 'landscape')


@celery_app.task
def check_transactions():
    """
    Task to be run periodically to update the status of transfers on Dwolla.
    """
    records = TransactionRecord.objects.filter(
        status=TransactionRecord.PENDING, destination=TransactionRecord.BANK,
        source=TransactionRecord.HOLDINGS,
    )
    for record in records:
        update_transfer_status.delay(record.id)


@celery_app.task
def update_transfer_status(record_id):
    record = TransactionRecord.objects.get(id=record_id)
    with dwolla as api:
        status = api.get('https://api.dwolla.com/transfers/{}'.format(record.remote_id))
        if status.body['status'] == 'processed':
            record.status = TransactionRecord.SUCCESS
            record.save()
            TransactionRecord.objects.filter(
                targets=ref_for_instance(record), category=TransactionRecord.THIRD_PARTY_FEE,
            ).update(status=TransactionRecord.SUCCESS)
        if status.body['status'] in ['cancelled', 'failed']:
            record.status = TransactionRecord.FAILURE
            record.save()
            notify(
                TRANSFER_FAILED,
                record.payer,
                data={
                    'error': 'The bank rejected the transfer. Please try again, update your account information, '
                             'or contact support.'
                }
            )
            TransactionRecord.objects.filter(
                targets=ref_for_instance(record), category=TransactionRecord.THIRD_PARTY_FEE,
            ).update(status=TransactionRecord.FAILURE)
            deliverable = record.targets.filter(
                content_type=ContentType.objects.get_for_model(Deliverable),
            ).values_list('object_id', flat=True)
            Deliverable.objects.filter(id__in=[int(order_id) for order_id in deliverable]).update(payout_sent=False)


@celery_app.task
def auto_finalize(order_id):
    deliverable = Deliverable.objects.get(id=order_id)
    if not deliverable.status == REVIEW:
        # Was disputed in the interim.
        return
    if not deliverable.auto_finalize_on:
        # Order had final revision removed in the interim.
        return
    if deliverable.auto_finalize_on > timezone.now().date():
        # Order finalize date has been moved up.
        return
    finalize_deliverable(deliverable)


@celery_app.task
def auto_finalize_run():
    for deliverable in Deliverable.objects.filter(status=REVIEW, auto_finalize_on__lte=timezone.now().date()):
        auto_finalize.delay(deliverable.id)


@celery_app.task
def withdraw_all(user_id):
    user = User.objects.get(id=user_id)
    if not user.artist_profile.auto_withdraw:
        return
    banks = user.banks.filter(deleted=False)
    if not banks:
        return
    balance = account_balance(user, TransactionRecord.HOLDINGS)
    if balance <= 0:
        return
    with transaction.atomic():
        record, deliverables = initiate_withdraw(user, banks[0], Money(balance, 'USD'), test_only=False)
        try:
            perform_transfer(record, deliverables, note='Disbursement')
        except Exception as err:
            notify(TRANSFER_FAILED, user, data={'error': str(err)})


@celery_app.task
def remind_sale(order_id):
    deliverable = Deliverable.objects.get(id=order_id)
    if not deliverable.status == NEW:
        return
    send_transaction_email(
        'Your commissioner is awaiting your response!', 'sale_reminder.html', deliverable.order.seller, {
            'deliverable': deliverable,
        }
    )


@celery_app.task
def remind_sales():
    to_remind = []
    deliverables = Deliverable.objects.filter(
        status=NEW, created_on__lte=timezone.now() - relativedelta(days=1),
    )
    for deliverable in deliverables:
        delta = (timezone.now() - deliverable.created_on).days
        if delta <= 5:
            to_remind.append(deliverable)
            continue
        elif delta <= 20 and not (delta % 3):
            to_remind.append(deliverable)
            continue
        elif delta > 20 and not delta % 5:
            to_remind.append(deliverable)
    for deliverable in to_remind:
        remind_sale.delay(deliverable.id)


@celery_app.task(
    bind=True, autoretry_for=(HTTPError,), retry_kwargs={'max_retries': 30}, exponential_backoff=2, retry_jitter=True,
)
def get_transaction_fees(self, transaction_id: str):
    record = TransactionRecord.objects.get(id=transaction_id)
    if TransactionRecord.objects.filter(targets=ref_for_instance(record)).exists():
        # We've already grabbed the fees. Bail.
        return
    with dwolla as api:
        response = api.get(f'transfers/{record.remote_id}/fees')
    for transaction in response.body['transactions']:
        fee = TransactionRecord.objects.create(
            status=TRANSACTION_STATUS_MAP[transaction['status']],
            created_on=parse(transaction['created']),
            payee=None,
            payer=None,
            source=TransactionRecord.UNPROCESSED_EARNINGS,
            destination=TransactionRecord.ACH_TRANSACTION_FEES,
            category=TransactionRecord.THIRD_PARTY_FEE,
            remote_id=transaction['id'],
            amount=Money(transaction['amount']['value'], transaction['amount']['currency'])
        )
        fee.targets.add(ref_for_instance(record))


@celery_app.task
def clear_deliverable(deliverable_id):
    try:
        deliverable = Deliverable.objects.get(id=deliverable_id, status=CANCELLED)
    except Deliverable.DoesNotExist:
        return
    destroy_deliverable(deliverable)


@celery_app.task
def clear_cancelled_deliverables():
    to_destroy = Deliverable.objects.filter(status=CANCELLED, cancelled_on__lte=timezone.now() - relativedelta(weeks=2))
    for deliverable in to_destroy:
        clear_deliverable(deliverable.id)


@celery_app.task
def recover_returned_balance():
    if not (settings.DWOLLA_MASTER_BALANCE_KEY and settings.DWOLLA_FUNDING_SOURCE_KEY):
        return
    with dwolla as api:
        response = api.get(settings.DWOLLA_MASTER_BALANCE_KEY)
        balance = Money(response.body['balance']['value'], response.body['balance']['currency'])
        if balance <= Money('0', 'USD'):
            return

    transfer_request = {
        '_links': {
            'source': {
                'href': settings.DWOLLA_MASTER_BALANCE_KEY
            },
            'destination': {
                'href': settings.DWOLLA_FUNDING_SOURCE_KEY
            }
        },
        'amount': {
            'currency': str(balance.currency),
            'value': str(balance.amount),
        },
    }
    with dwolla as api:
        api.post('transfers', transfer_request)
