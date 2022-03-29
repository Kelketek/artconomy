import logging
from collections import defaultdict
from decimal import ROUND_CEILING, localcontext
from typing import Dict, Union

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.datetime_safe import date, datetime
from moneyed import Money
from pytz import UTC
from stripe.error import CardError

from apps.lib.models import RENEWAL_FAILURE, SUBSCRIPTION_DEACTIVATED, RENEWAL_FIXED, TRANSFER_FAILED, ref_for_instance
from apps.lib.utils import notify, send_transaction_email, require_lock
from apps.profiles.models import User
from apps.sales.models import CreditCardToken, TransactionRecord, Deliverable, StripeAccount, ServicePlan
from apps.sales.constants import PREMIUM_SUBSCRIPTION, COMPLETED, NEW, REVIEW, CANCELLED, UNPROCESSED_EARNINGS, \
    HOLDINGS, SUCCESS, CASH_WITHDRAW, BANK, PENDING, ACH_TRANSACTION_FEES, THIRD_PARTY_FEE, CARD, ESCROW, FAILURE, \
    PAYOUT_MIRROR_SOURCE, PAYOUT_MIRROR_DESTINATION, PAID
from apps.sales.stripe import stripe, money_to_stripe
from apps.sales.utils import finalize_deliverable, account_balance, destroy_deliverable, \
    fetch_prefixed, subscription_invoice_for_service, get_term_invoice, invoice_post_payment, add_service_plan_line
from apps.sales.line_item_funcs import divide_amount
from conf.celery_config import celery_app


logger = logging.getLogger(__name__)


def renew_stripe_card(*, invoice, price, user, card):
    from apps.sales.models import Invoice
    if not invoice.total():
        # This invoice is a zero invoice. This might happen for a plan with no monthly subscription fee where
        # No orders are processed.
        invoice_post_payment(
            invoice, {
                'amount': invoice.total(),
                'successful': True,
                'cash': True,
            },
        )
        return
    with stripe as stripe_api:
        amount, currency = money_to_stripe(price)
        kwargs = {
            'amount': amount,
            'currency': currency,
            'payment_method': card.stripe_token,
            'customer': user.stripe_token,
            'confirm': True,
            'off_session': True,
            # TODO: Needs to change per service name, or else be omitted since we'll be swapping methods for tracking
            # subscriptions anyway.
            'metadata': {'service': 'landscape', 'invoice_id': invoice.id}
        }
        try:
            # This... might cause a race condition? Seems unlikely, but if we have a bug later, it would be because
            # the webhook was contacted before we set the current_intent on the invoice.
            #
            # Using the update method here to be absolutely certain we don't change anything else about the invoice
            # that might clobber what the webhook is doing.
            Invoice.objects.filter(id=invoice.id).update(current_intent=stripe_api.PaymentIntent.create(**kwargs)['id'])
            return True
        except CardError as err:
            notify(
                RENEWAL_FAILURE, user, data={
                    'error': "Card ending in {} -- {}".format(card.last_four, err)}, unique=True
            )
            return False


@celery_app.task
def renew(user_id, card_id=None):
    user = User.objects.get(id=user_id)
    enabled = user.service_plan
    paid_through = user.service_plan_paid_through
    old = paid_through and paid_through <= timezone.now().date()
    if old is None:
        # This should never happen.
        logger.error(
            "!!! {}({}) has NONE for service_plan_paid_through with subscription enabled!".format(
                user.username, user.id,
            )
        )
        return
    if not (enabled and old):
        # Fixed between when this task was added and when it was executed.
        return
    if card_id:
        card = CreditCardToken.objects.get(id=card_id, user=user, active=True)
    else:
        card = user.primary_card
    invoice = get_term_invoice(user)
    add_service_plan_line(invoice, user.next_service_plan)
    if not invoice.total():
        # This invoice is a zero invoice. This might happen for a plan with no monthly subscription fee where
        # No orders are processed.
        invoice_post_payment(
            invoice, {
                'amount': invoice.total(),
                'successful': True,
                'cash': True,
            },
        )
        if paid_through < timezone.now().date():
            notify(RENEWAL_FIXED, user, unique=True)
        return
    if card is None:
        # noinspection PyUnresolvedReferences
        cards = user.credit_cards.filter(active=True).order_by('-created_on')
        if not cards.exists():
            logger.info("{}({}) can't renew due to no card on file.".format(user.username, user.id))
            notify(RENEWAL_FAILURE, user, data={'error': 'No card on file!'}, unique=True)
            return
        card = cards[0]
    success = renew_stripe_card(invoice=invoice, user=user, card=card, price=invoice.total())
    if not success:
        return
    if card_id or (paid_through < timezone.now().date()):
        # This was called manually or a previous attempt should have been made and there may have been a gap
        # in coverage. In this case, let's inform the user the renewal was successful instead of silently
        # succeeding.
        notify(RENEWAL_FIXED, user, unique=True)


@celery_app.task
def run_billing():
    # Anyone we've not been able to renew for five days, assume won't be renewing automatically.
    users = User.objects.filter(
        Q(service_plan__isnull=False, service_plan_paid_through__lte=timezone.now().date() - relativedelta(days=5))
    ).exclude(
        # We assume that the default plan is a free plan.
        Q(service_plan__name=settings.DEFAULT_SERVICE_PLAN_NAME)
    )
    for user in users:
        logger.info('Deactivated {}({})'.format(user.username, user.id))
        notify(SUBSCRIPTION_DEACTIVATED, user, unique=True)
        default_plan = ServicePlan.objects.get(name=settings.DEFAULT_SERVICE_PLAN_NAME)
        user.service_plan = default_plan
        user.next_service_plan = default_plan
        user.save()
        # TODO: What other effects should happen if the user hasn't paid their dues?
    users = User.objects.filter(
        service_plan__isnull=False, service_plan_paid_through__lte=timezone.now().date(),
    ).exclude(Q(service_plan__name=settings.DEFAULT_SERVICE_PLAN_NAME) & Q(service_plan__hidden=False))
    for user in users:
        renew.delay(user.id)


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
            destination=HOLDINGS,
            status=SUCCESS,
        )
        sub_amount = sum(sub_record.amount for sub_record in records)
        amount -= sub_amount
        assert amount >= Money('0', amount.currency.code)
        record = TransactionRecord.objects.create(
            amount=sub_amount,
            source=HOLDINGS,
            payee=user,
            payer=user,
            category=CASH_WITHDRAW,
            destination=BANK,
            status=PENDING,
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
        source=HOLDINGS,
        payee=user,
        payer=user,
        category=CASH_WITHDRAW,
        destination=BANK,
        status=PENDING,
        note='Remaining amount, not connected to deliverables. May need annotations later.'
    )
    record_map[None] = record
    return record_map


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
            source=CARD, targets=ref_for_instance(deliverable),
            status=SUCCESS, destination=ESCROW,
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
            record.status = PENDING
            record.remote_ids = [transfer['destination_payment'], transfer['id']]
            record.response_message = ''
            record.save()
        except Exception as err:
            record.response_message = str(err)
            record.status = FAILURE
            record.save()
            if deliverable:
                deliverable.payout_sent = False
                deliverable.save()


@celery_app.task
def withdraw_all(user_id):
    user = User.objects.get(id=user_id)
    if not user.artist_profile.auto_withdraw:
        return
    if not hasattr(user, 'stripe_account'):
        return
    banks = [user.stripe_account]
    with cache.lock(f'account_user__{user.id}'):
        balance = account_balance(user, HOLDINGS)
        if balance <= 0:
            return
        with transaction.atomic():
            record_map = record_to_deliverable_map(user, banks[0], Money(balance, 'USD'))
            for deliverable, record in record_map.items():
                if deliverable:
                    deliverable.payout_sent = True
                    deliverable.save()
                stripe_transfer.delay(record.id, banks[0].id, deliverable and deliverable.id)


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
        finalized_on__gte=start_datetime, finalized_on__lt=end_datetime, status=SUCCESS,
        source=HOLDINGS, destination=BANK,
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
            source=UNPROCESSED_EARNINGS,
            destination=ACH_TRANSACTION_FEES,
            category=THIRD_PARTY_FEE,
            targets=ref_for_instance(record),
        ).first()
        if not fee_record:
            fee_record = TransactionRecord(
                source=UNPROCESSED_EARNINGS,
                destination=ACH_TRANSACTION_FEES,
                category=THIRD_PARTY_FEE,
            )
        fee_record.finalized_on = record.finalized_on
        fee_record.amount = fee_list.pop(0)
        fee_record.status = SUCCESS
        fee_record.remote_ids = record.remote_ids
        fee_record.save()
        fee_record.targets.add(*record.targets.all(), ref_for_instance(record))
        user_fees_map[record.payer].append(fee_record)
        fee_record.targets.add(*record.targets.all())
        cross_border = TransactionRecord.objects.filter(
            targets=ref_for_instance(record),
            source=PAYOUT_MIRROR_SOURCE,
            destination=PAYOUT_MIRROR_DESTINATION,
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
