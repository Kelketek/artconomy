import logging
from collections import defaultdict
from decimal import ROUND_CEILING, localcontext
from typing import Dict, Union

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.datetime_safe import date, datetime
from moneyed import Money
from pytz import UTC
from urllib3.exceptions import HTTPError

from apps.lib.models import RENEWAL_FAILURE, SUBSCRIPTION_DEACTIVATED, RENEWAL_FIXED, TRANSFER_FAILED, ref_for_instance
from apps.lib.utils import notify, send_transaction_email, require_lock
from apps.profiles.models import User
from apps.sales.apis import dwolla, AUTHORIZE, STRIPE
from apps.sales.authorize import AuthorizeException, charge_saved_card
from apps.sales.dwolla import initiate_withdraw, perform_transfer, TRANSACTION_STATUS_MAP
from apps.sales.models import CreditCardToken, TransactionRecord, REVIEW, NEW, Deliverable, CANCELLED, \
    PREMIUM_SUBSCRIPTION, PAID, COMPLETED, StripeAccount
from apps.sales.stripe import stripe, money_to_stripe
from apps.sales.utils import set_premium, finalize_deliverable, account_balance, destroy_deliverable, \
    get_term_invoice, get_user_processor, fetch_prefixed, divide_amount
from conf.celery_config import celery_app


logger = logging.getLogger(__name__)


def renew_stripe_card(*, invoice, price, user, card):
    with stripe as stripe_api:
        amount, currency = money_to_stripe(price)
        kwargs = {
            'amount': amount,
            'currency': currency,
            'payment_method': card.stripe_token,
            'customer': user.stripe_token,
            'confirm': True,
            'off_session': True,
            'metadata': {'service': 'landscape'}
        }
        try:
            if user.current_intent:
                stripe_api.PaymentIntent.update(
                    user.current_intent,
                    **kwargs,
                )
            else:
                stripe_api.PaymentIntent.create(
                    **kwargs,
                )
            return True
        except stripe_api.error.CardError as err:
            notify(
                RENEWAL_FAILURE, user, data={
                    'error': "Card ending in {} -- {}".format(card.last_four, err.message)}, unique=True
            )
            return False


def renew_authorize_card(*, invoice, price, user, card):
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
    record.targets.add(ref_for_instance(user), ref_for_instance(invoice))
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
        return False
    record.status = TransactionRecord.SUCCESS
    record.remote_ids = [remote_id]
    record.auth_code = auth_code
    record.finalized = True
    record.response_message = 'Upgraded to landscape'
    card.cvv_verified = True
    card.save()
    record.save()
    set_premium(user, target_date=date.today() + relativedelta(months=1))
    invoice.paid_on = timezone.now()
    invoice.status = PAID
    invoice.save()
    return True


@celery_app.task
def renew(user_id, card_id=None):
    user = User.objects.get(id=user_id)
    enabled = user.landscape_enabled
    paid_through = user.landscape_paid_through
    old = paid_through and paid_through <= date.today()
    if old is None:
        # This should never happen.
        logger.error(
            "!!! {}({}) has NONE for landscape_paid_through with landscape enabled!".format(user.username, user.id)
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
    price = Money(settings.LANDSCAPE_PRICE, 'USD')
    invoice = get_term_invoice(user)
    invoice.line_items.update_or_create(
        defaults={'amount': price, 'description': 'Landscape'},
        destination_account=TransactionRecord.UNPROCESSED_EARNINGS,
        type=PREMIUM_SUBSCRIPTION,
        destination_user=None,
    )
    if card.token:
        success = renew_authorize_card(invoice=invoice, user=user, card=card, price=price)
    else:
        success = renew_stripe_card(invoice=invoice, user=user, card=card, price=price)
    if not success:
        return
    if card_id or (paid_through < date.today()):
        # This was called manually or a previous attempt should have been made and there may have been a gap
        # in coverage. In this case, let's inform the user the renewal was successful instead of silently
        # succeeding.
        notify(RENEWAL_FIXED, user, unique=True)


@celery_app.task
def run_billing():
    # Anyone we've not been able to renew for five days, assume won't be renewing automatically.
    users = User.objects.filter(
        Q(landscape_enabled=True, landscape_paid_through__lte=date.today() - relativedelta(days=5))
    )
    for user in users:
        logger.info('Deactivated {}({})'.format(user.username, user.id))
        notify(SUBSCRIPTION_DEACTIVATED, user, unique=True)
        user.landscape_enabled = False
        user.save()
    users = User.objects.filter(landscape_enabled=True, landscape_paid_through__lte=date.today())
    for user in users:
        renew.delay(user.id)


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
        status = api.get('https://api.dwolla.com/transfers/{}'.format(record.remote_ids[0]))
        if status.body['status'] == 'processed':
            record.status = TransactionRecord.SUCCESS
            record.save()
            new_record = TransactionRecord.objects.get_or_create(
                remote_ids=record.remote_ids, amount=record.amount,
                payer=record.payer, payee=record.payee, source=TransactionRecord.PAYOUT_MIRROR_SOURCE,
                destination=TransactionRecord.PAYOUT_MIRROR_DESTINATION, status=TransactionRecord.SUCCESS,
                category=TransactionRecord.CASH_WITHDRAW,
                created_on=record.created_on, finalized_on=timezone.now(),
            )[0]
            new_record.targets.add(*record.targets.all())
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
            deliverable_ids = record.targets.filter(
                content_type=ContentType.objects.get_for_model(Deliverable),
            ).values_list('object_id', flat=True)
            Deliverable.objects.filter(id__in=[int(order_id) for order_id in deliverable_ids]).update(payout_sent=False)


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


RecordMap = Dict[Union[Deliverable, None], TransactionRecord]


@require_lock(TransactionRecord, 'ACCESS EXCLUSIVE')
def record_to_deliverable_map(user, bank: StripeAccount, amount: Money) -> RecordMap:
    deliverables = Deliverable.objects.select_for_update(skip_locked=True).filter(
        order__seller=user,
        payout_sent=False,
        escrow_disabled=False,
        status=COMPLETED,
    )
    record_map: RecordMap = {}
    bank_ref = ref_for_instance(bank)
    for deliverable in deliverables:
        target = ref_for_instance(deliverable)
        records = TransactionRecord.objects.filter(
            targets=target,
            payee=user,
            destination=TransactionRecord.HOLDINGS,
            status=TransactionRecord.SUCCESS,
        )
        sub_amount = sum(sub_record.amount for sub_record in records)
        amount -= sub_amount
        assert amount >= Money('0', amount.currency.code)
        record = TransactionRecord.objects.create(
            amount=sub_amount,
            source=TransactionRecord.HOLDINGS,
            payee=user,
            payer=user,
            category=TransactionRecord.CASH_WITHDRAW,
            destination=TransactionRecord.BANK,
            status=TransactionRecord.FAILURE,
            response_message='Failed to connect to server',
        )
        for sub_record in records:
            record.targets.add(*sub_record.targets.all())
        record.targets.add(bank_ref)
        record_map[deliverable] = record
    if not amount:
        return record_map
    record = TransactionRecord.objects.create(
        amount=amount,
        source=TransactionRecord.HOLDINGS,
        payee=user,
        payer=user,
        destination=TransactionRecord.BANK,
        status=TransactionRecord.PENDING,
        note='Remaining amount, not connected to deliverables. May need annotations later.'
    )
    record_map[None] = record
    return record


@celery_app.task
def stripe_transfer(record_id, stripe_id, deliverable_id=None):
    base_settings = {
        'metadata': {}
    }
    stripe_account = StripeAccount.objects.get(id=stripe_id)
    deliverable = None
    if deliverable_id:
        deliverable = Deliverable.objects.get(id=deliverable_id)
        base_settings['metadata'] = deliverable.stripe_metadata
        base_settings['transfer_group'] = f'ACInvoice#{deliverable.invoice.id}'
        source_record = TransactionRecord.objects.filter(
            source=TransactionRecord.CARD, targets=ref_for_instance(deliverable),
            status=TransactionRecord.SUCCESS, destination=TransactionRecord.ESCROW,
        ).first()
        if source_record:
            try:
                base_settings['source_transaction'] = fetch_prefixed('ch_', source_record.remote_ids)
            except ValueError:
                pass
        assert deliverable.order.seller == stripe_account.user
    record = TransactionRecord.objects.get(id=record_id)
    base_settings['amount'], base_settings['currency'] = money_to_stripe(record.amount)
    base_settings['destination'] = stripe_account.token
    base_settings['metadata'] = {'reference_transaction': record.id}
    assert record.payee == stripe_account.user
    with stripe as stripe_api:
        try:
            transfer = stripe_api.Transfer.create(
                **base_settings,
            )
            record.status = TransactionRecord.PENDING
            record.remote_ids = [transfer.destination_payment, transfer.id]
            record.response_message = ''
            record.save()
        except Exception as err:
            record.response_message = str(err)
            record.status = TransactionRecord.FAILURE
            record.save()
            if deliverable:
                deliverable.payout_sent = False
                deliverable.save()


@celery_app.task
def withdraw_all(user_id):
    user = User.objects.get(id=user_id)
    if not user.artist_profile.auto_withdraw:
        return
    processor = get_user_processor(user)
    if processor == AUTHORIZE:
        banks = user.banks.filter(deleted=False)
        if not banks:
            return
    elif processor == STRIPE:
        if not hasattr(user, 'stripe_account'):
            return
        banks = [user.stripe_account]
    else:
        raise Exception(f"Unknown payment processor-- thus, unknown payout processor. Value was: {user.processor}")
    balance = account_balance(user, TransactionRecord.HOLDINGS)
    if balance <= 0:
        return
    with transaction.atomic():
        if processor == 'authorize':
            record, deliverables = initiate_withdraw(user, banks[0], Money(balance, 'USD'), test_only=False)
            try:
                perform_transfer(record, deliverables, note='Disbursement')
            except Exception as err:
                notify(TRANSFER_FAILED, user, data={'error': str(err)})
        elif processor == 'stripe':
            record_map = record_to_deliverable_map(user, banks[0], Money(balance, 'USD'))
            for deliverable, record in record_map.items():
                deliverable.payout_sent = True
                deliverable.save()
                stripe_transfer.delay(record.id, banks[0].id, deliverable and deliverable.id)
        else:
            raise RuntimeError(f'Got unknown processor: {processor}')


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
        response = api.get(f'transfers/{record.remote_ids[0]}/fees')
    for transaction in response.body['transactions']:
        fee = TransactionRecord.objects.create(
            status=TRANSACTION_STATUS_MAP[transaction['status']],
            created_on=parse(transaction['created']),
            payee=None,
            payer=None,
            source=TransactionRecord.UNPROCESSED_EARNINGS,
            destination=TransactionRecord.ACH_TRANSACTION_FEES,
            category=TransactionRecord.THIRD_PARTY_FEE,
            remote_ids=[transaction['id']],
            amount=Money(transaction['amount']['value'], transaction['amount']['currency'])
        )
        fee.targets.add(ref_for_instance(record))


@transaction.atomic
def annotate_connect_fees_for_year_month(*, year: int, month: int) -> None:
    """
    Stripe levies fees on the full transaction volume. This means calculating them by individual transfers could
    lead to subtle differences between the amount we figure and they amount they actually charge us. So, we have to
    run these calculations for the volume over a whole month and then divvy them up.

    We create these entries in an idempotent manner so we can run them as we go along if we wish. By the end of the
    month, the amount of fees we calculate should match the amount they took.

    Note that this is done in two segments. All transfers out are subject to the general volume pricing, but those
    which go internationally are subject to an additional fee atop the main one. Stripe levies this as a separate fee
    so we calculate it separately and consolidate afterward.

    This function may need to be optimized depending on how many transactions we end up dealing with. However
    I'm optimizing for clarity of writing for now.

    Stripe calculates its timezones on UTC.
    """
    start_datetime = datetime(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=UTC)
    end_datetime = min(datetime.now(tz=UTC), start_datetime + relativedelta(months=1))
    target_transactions = list(TransactionRecord.objects.filter(
        finalized_on__gte=start_datetime, finalized_on__lt=end_datetime, status=TransactionRecord.SUCCESS,
        source=TransactionRecord.HOLDINGS, destination=TransactionRecord.BANK,
        targets__content_type=ContentType.objects.get_for_model(StripeAccount)
    ).distinct().order_by('finalized_on'))
    if not len(target_transactions):
        return
    total_volume = sum([target_transaction.amount for target_transaction in target_transactions])
    # Need to track all fees for each user since we'll add to them multiple times.
    user_fees_map = defaultdict(list)
    # Need to know which transactions were cross-border since they incur additional fees.
    cross_border_fees_list = []
    # And we'll need to tally the total from those transactions to derive the fee.
    cross_border_transactions = []
    with localcontext() as ctx:
        ctx.rounding = ROUND_CEILING
        base_fees = (total_volume * (settings.STRIPE_PAYOUT_PERCENTAGE / 100)).round(2)
    fee_list = divide_amount(base_fees, len(target_transactions))
    for record in target_transactions:
        # Can't use update_or_create here since we are looking around the 'targets' many-to-many table.
        fee_record = TransactionRecord.objects.filter(
            source=TransactionRecord.UNPROCESSED_EARNINGS,
            destination=TransactionRecord.ACH_TRANSACTION_FEES,
            category=TransactionRecord.THIRD_PARTY_FEE,
            targets=ref_for_instance(record),
        ).first()
        if not fee_record:
            fee_record = TransactionRecord(
                source=TransactionRecord.UNPROCESSED_EARNINGS,
                destination=TransactionRecord.ACH_TRANSACTION_FEES,
                category=TransactionRecord.THIRD_PARTY_FEE,
            )
        fee_record.finalized_on = record.finalized_on
        fee_record.amount = fee_list.pop(0)
        fee_record.status = TransactionRecord.SUCCESS
        fee_record.remote_ids = record.remote_ids
        fee_record.save()
        fee_record.targets.add(*record.targets.all(), ref_for_instance(record))
        user_fees_map[record.payer].append(fee_record)
        fee_record.targets.add(*record.targets.all())
        cross_border = TransactionRecord.objects.filter(
            targets=ref_for_instance(record),
            source=TransactionRecord.PAYOUT_MIRROR_SOURCE,
            destination=TransactionRecord.PAYOUT_MIRROR_DESTINATION,
        ).exclude(amount_currency='USD').exists()
        if cross_border:
            cross_border_fees_list.append(fee_record)
            cross_border_transactions.append(record)
    # Each user has a $2 fee per month if they have a payout. This is part of the 'connect' fee. It's going to be
    # a challenge to find a way to mitigate the cost of this, but we can at least account for it to start.
    for key, values in user_fees_map.items():
        fee_list = divide_amount(settings.STRIPE_ACTIVE_ACCOUNT_MONTHLY_FEE, len(values))
        for value in values:
            value.amount += (fee_list.pop(0) + settings.STRIPE_PAYOUT_STATIC)
            value.save()
    if not cross_border_transactions:
        return
    cross_border_total = sum(
        [cross_border_transaction.amount for cross_border_transaction in cross_border_transactions],
    )
    with localcontext() as ctx:
        ctx.rounding = ROUND_CEILING
        cross_border_fee = (cross_border_total * (settings.STRIPE_PAYOUT_CROSS_BORDER_PERCENTAGE / 100)).round(2)
    fee_list = divide_amount(cross_border_fee, len(cross_border_transactions))
    for fee_record in cross_border_fees_list:
        fee_record.amount += fee_list.pop(0)
        fee_record.save()


@celery_app.task
def annotate_connect_fees():
    """
    Runs through all payouts and tallies expected fees, creating entries for all of them.
    """
    target_date = timezone.now()
    annotate_connect_fees_for_year_month(month=target_date.month, year=target_date.year)
    if target_date.day == 1:
        # Also do last month's to finish it off.
        target_date -= relativedelta(months=1)
        annotate_connect_fees_for_year_month(month=target_date.month, year=target_date.year)


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
