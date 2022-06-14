"""
The functions in this file are meant to mirror the functions in frontend/lib/lineItemFunctions. There's not a good way
to ensure that they're both updated at the same time, but they should, hopefully, be easy enough to keep in sync.
If enough code has to be repeated between the two bases it may be worth looking into a transpiler.
"""
import json
import logging
from collections import defaultdict
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext, ROUND_FLOOR, ROUND_CEILING
from functools import reduce
from itertools import chain
from urllib.parse import quote

from django.utils.module_loading import import_string
from math import ceil
from typing import Union, Type, TYPE_CHECKING, List, Dict, Iterator, Callable, Tuple, TypedDict, Optional, Any

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError, transaction
from django.db.models import Sum, Q, IntegerField, Case, When, F, Model
from django.db.transaction import atomic
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.datetime_safe import date
from moneyed import Money, Currency
from pandas.tseries.offsets import BDay
from rest_framework.exceptions import ValidationError
from short_stuff import gen_shortcode

from apps.lib.models import Subscription, COMMISSIONS_OPEN, Event, DISPUTE, SALE_UPDATE, Notification, \
    Comment, ORDER_UPDATE, COMMENT, ref_for_instance
from apps.lib.utils import notify, recall_notification
from apps.profiles.models import User, VERIFIED
from apps.sales.apis import STRIPE
from apps.sales.stripe import refund_payment_intent, stripe

if TYPE_CHECKING:
    from apps.sales.models import LineItemSim, LineItem, TransactionRecord, Deliverable, Revision, CreditCardToken, \
    Invoice, ServicePlan, VOID

    Line = Union[LineItem, LineItemSim]
    LineMoneyMap = Dict[Line, Money]
    TransactionSpecKey = (Union[User, None], int, int)
    TransactionSpecMap = Dict[TransactionSpecKey, Money]


logger = logging.getLogger(__name__)


class ALL:
    def __init__(self):
        raise RuntimeError('This class used as unique enum, not to be instantiated.')
    pass


AVAILABLE = 0
POSTED_ONLY = 1
PENDING = 2


def account_balance(
        user: Union[User, None, Type[ALL]], account_type: int, balance_type: int = AVAILABLE, qs_kwargs: dict = None,
) -> Decimal:
    qs_kwargs = qs_kwargs or {}
    from apps.sales.models import TransactionRecord
    if balance_type == PENDING:
        statuses = [TransactionRecord.PENDING]
    elif balance_type == POSTED_ONLY:
        statuses = [TransactionRecord.SUCCESS]
    elif balance_type == AVAILABLE:
        statuses = [TransactionRecord.SUCCESS, TransactionRecord.PENDING]
    else:
        raise TypeError(f'Invalid balance type: {balance_type}')
    kwargs = {
        'status__in': statuses,
        'source': account_type,
        **qs_kwargs,
    }
    if user is not ALL:
        kwargs['payer'] = user
    try:
        debit = Decimal(
            str(TransactionRecord.objects.filter(
                **kwargs,
            ).aggregate(Sum('amount'))['amount__sum'])
        )
    except InvalidOperation:
        debit = Decimal('0.00')
    kwargs = {
        'status__in': statuses,
        'destination': account_type,
        **qs_kwargs,
    }
    if user is not ALL:
        kwargs['payee'] = user
    try:
        credit = Decimal(
            str(TransactionRecord.objects.filter(
                **kwargs,
            ).aggregate(Sum('amount'))['amount__sum'])
        )
    except InvalidOperation:
        credit = Decimal('0.00')

    return Decimal(credit - debit)


def product_ordering(qs, query=''):
    return qs.annotate(
        matches=Case(
            When(name__iexact=query, then=0),
            default=1,
            output_field=IntegerField()
        ),
        tag_matches=Case(
            When(tags__name__iexact=query, then=0),
            default=1,
            output_field=IntegerField()
        )
        # How can we make it distinct on id while making matches and tag_matches priority ordering?
    ).order_by('id', 'matches', 'tag_matches').distinct('id')


def available_products(requester, query='', ordering=True):
    from apps.sales.models import Product
    if query:
        q = Q(name__istartswith=query) | Q(tags__name=query.lower())
        qs = Product.objects.filter(available=True).filter(q)
    else:
        qs = Product.objects.filter(available=True)
    qs = qs.exclude(active=False)
    qs = qs.exclude(table_product=True)
    # TODO: Recheck this for basic/free plan when we have orders that have been placed but they haven't upgraded.
    qs = qs.exclude((Q(user__service_plan_paid_through__lte=timezone.now()) | ~Q(user__service_plan__name='Landscape')), wait_list=True)
    if requester.is_authenticated:
        if not requester.is_staff:
            qs = qs.exclude(user__blocking=requester)
            qs = qs.exclude(table_product=True)
        qs = qs.exclude(user__blocked_by=requester)
    if ordering:
        return product_ordering(qs, query)
    return qs


def service_price(user, service):
    price = Money(getattr(settings, service.upper() + '_PRICE'), 'USD')
    return price


def set_premium(user, service_plan, target_date=None):
    user.service_plan = service_plan
    user.next_service_plan = service_plan
    if target_date:
        user.service_plan_paid_through = target_date
    user.save(
        update_fields=['service_plan', 'service_plan_paid_through', 'next_service_plan'],
    )


def check_charge_required(user):
    if user.landscape_paid_through:
        if user.landscape_paid_through >= date.today():
            return False, user.landscape_paid_through
    return True, None


def available_products_by_load(seller_profile, load=None):
    from apps.sales.models import Product
    if load is None:
        load = seller_profile.load
    return Product.objects.filter(user_id=seller_profile.user_id, active=True, hidden=False).exclude(
        task_weight__gt=seller_profile.max_load - load, wait_list=False,
    ).exclude(Q(parallel__gte=F('max_parallel')) & ~Q(max_parallel=0))


def available_products_from_user(seller_profile):
    from apps.sales.models import Product
    if seller_profile.commissions_closed or seller_profile.commissions_disabled:
        return Product.objects.none()
    return available_products_by_load(seller_profile)


# Primitive recursion check lock.
UPDATING = {}


def update_availability(seller, load, current_closed_status):
    global UPDATING
    if seller in UPDATING:
        return
    UPDATING[seller] = True
    seller_profile = seller.artist_profile
    try:
        products = available_products_by_load(seller_profile, load)
        if seller_profile.commissions_closed:
            seller_profile.commissions_disabled = True
        elif not products.exists():
            seller_profile.commissions_disabled = True
        else:
            seller_profile.commissions_disabled = False
        seller_profile.load = load
        if products.exists() and not seller_profile.commissions_disabled:
            seller_profile.has_products = True
        seller_profile.save()
        products.update(available=True, edited_on=timezone.now())
        # Sanity setting.
        max_size = seller_profile.max_load - load
        seller.products.filter(
            Q(hidden=True) | Q(active=False) | Q(inventory__count=0) | Q(task_weight__gt=max_size)
        ).exclude(wait_list=True).update(
            available=False, edited_on=timezone.now(),
        )
        if current_closed_status and not seller_profile.commissions_disabled:
            previous = Event.objects.filter(
                type=COMMISSIONS_OPEN, content_type=ContentType.objects.get_for_model(User), object_id=seller.id,
                date__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            )
            notify(
                COMMISSIONS_OPEN, seller, unique=True, mark_unread=not previous.exists(),
                silent_broadcast=previous.exists()
            )
        if seller_profile.commissions_disabled or seller_profile.commissions_closed:
            seller.products.all().update(available=False, edited_on=timezone.now())
            recall_notification(COMMISSIONS_OPEN, seller)
    finally:
        del UPDATING[seller]


def early_finalize(deliverable: 'Deliverable', user: User):
    if (
            deliverable.final_uploaded
            and deliverable.order.seller.landscape
            and deliverable.order.seller.trust_level == VERIFIED
            and not deliverable.escrow_disabled
    ):
        deliverable.trust_finalized = True
        finalize_deliverable(deliverable, user)


def floor_context(wrapped: Callable):
    def wrapper(*args, **kwargs):
        with localcontext() as ctx:
            ctx.rounding = ROUND_FLOOR
            return wrapped(*args, **kwargs)
    return wrapper


def ceiling_context(wrapped: Callable):
    def wrapper(*args, **kwargs):
        with localcontext() as ctx:
            ctx.rounding = ROUND_CEILING
            return wrapped(*args, **kwargs)
    return wrapper


def half_even_context(wrapped: Callable):
    def wrapper(*args, **kwargs):
        with localcontext() as ctx:
            ctx.rounding = ROUND_HALF_EVEN
            return wrapped(*args, **kwargs)
    return wrapper


def finalize_table_fees(deliverable: 'Deliverable'):
    from apps.sales.models import TransactionRecord, ref_for_instance
    ref = ref_for_instance(deliverable)
    record = TransactionRecord.objects.get(
        payee=None, destination=TransactionRecord.RESERVE,
        status=TransactionRecord.SUCCESS,
        targets=ref,
    )
    service_fee = TransactionRecord.objects.create(
        source=TransactionRecord.RESERVE,
        destination=TransactionRecord.UNPROCESSED_EARNINGS,
        amount=record.amount,
        payer=None, payee=None,
        status=TransactionRecord.SUCCESS,
        category=TransactionRecord.TABLE_SERVICE,
        remote_ids=record.remote_ids,
        auth_code=record.auth_code,
    )
    service_fee.targets.add(ref)
    tax_record = TransactionRecord.objects.get(
        payee=None, destination=TransactionRecord.MONEY_HOLE_STAGE,
        status=TransactionRecord.SUCCESS,
        targets=ref,
    )
    tax_burned = TransactionRecord.objects.create(
        source=TransactionRecord.MONEY_HOLE_STAGE,
        destination=TransactionRecord.MONEY_HOLE,
        amount=tax_record.amount,
        payer=None, payee=None,
        status=TransactionRecord.SUCCESS,
        category=TransactionRecord.TAX,
        remote_ids=tax_record.remote_ids,
        auth_code=tax_record.auth_code,
    )
    tax_burned.targets.add(ref)


def finalize_deliverable(deliverable, user=None):
    from apps.sales.models import TransactionRecord, COMPLETED, DISPUTED, ref_for_instance
    from apps.sales.tasks import withdraw_all
    with atomic():
        if deliverable.status == DISPUTED and user == deliverable.order.buyer:
            # User is rescinding dispute.
            recall_notification(DISPUTE, deliverable)
            # We'll pretend this never happened.
            deliverable.disputed_on = None
        deliverable.status = COMPLETED
        deliverable.save()
        notify(SALE_UPDATE, deliverable, unique=True, mark_unread=True)
        records = TransactionRecord.objects.filter(
            payee=deliverable.order.seller, destination=TransactionRecord.ESCROW,
            status=TransactionRecord.SUCCESS,
            targets__object_id=deliverable.id, targets__content_type=ContentType.objects.get_for_model(deliverable),
        )
        # There will always be at least one.
        record = records[0]
        to_holdings = TransactionRecord.objects.create(
            payer=deliverable.order.seller,
            payee=deliverable.order.seller,
            amount=sum((item.amount for item in records)),
            source=TransactionRecord.ESCROW,
            destination=TransactionRecord.HOLDINGS,
            category=TransactionRecord.ESCROW_RELEASE,
            status=TransactionRecord.SUCCESS,
            remote_ids=record.remote_ids,
            auth_code=record.auth_code,
        )
        to_holdings.targets.add(ref_for_instance(deliverable))
        if deliverable.table_order:
            finalize_table_fees(deliverable)
    # Don't worry about whether it's time to withdraw or not. This will make sure that an attempt is made in case
    # there's money to withdraw that hasn't been taken yet, and another process will try again if it settles later.
    # It will also ignore if the seller has auto_withdraw disabled.
    withdraw_all.delay(deliverable.order.seller.id)


def claim_order_by_token(order_claim, user, force=False):
    from apps.sales.models import Order
    if not order_claim:
        return
    order = Order.objects.filter(claim_token=order_claim).first()
    if not order:
        logger.warning("User %s attempted to claim non-existent order token, %s", user, order_claim)
        return
    if order.seller == user:
        logger.warning("Seller %s attempted to claim their own order token, %s", user, order_claim)
        return
    if order.buyer == user and user.is_registered:
        order.claim_token = None
        order.save()
    transfer_order(order, order.buyer, user, force=force)


def transfer_order(order, old_buyer, new_buyer, force=False):
    from apps.sales.models import buyer_subscriptions, CreditCardToken, Revision, ORDER_UPDATE
    if (old_buyer == new_buyer) and not force:
        raise AssertionError("Tried to claim an order, but it was already claimed!")
    order.buyer = new_buyer
    for deliverable in order.deliverables.all():
        if deliverable.invoice:
            deliverable.invoice.bill_to = new_buyer
            deliverable.invoice.save()
    order.customer_email = ''
    order.claim_token = None
    order.save()
    for deliverable in order.deliverables.all():
        Subscription.objects.bulk_create(buyer_subscriptions(deliverable), ignore_conflicts=True)
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        update_order_payments(deliverable)
    revision_type = ContentType.objects.get_for_model(Revision)
    Subscription.objects.bulk_create([
        Subscription(
            subscriber=new_buyer,
            object_id=revision_id,
            content_type=revision_type,
            type=COMMENT,
        )
        for revision_id in Revision.objects.filter(deliverable__order=order).values_list('id', flat=True)
    ], ignore_conflicts=True)
    if not old_buyer:
        return
    if old_buyer == new_buyer:
        return
    Subscription.objects.filter(subscriber=old_buyer).delete()
    Notification.objects.filter(user=old_buyer).update(user=new_buyer)
    Comment.objects.filter(user=old_buyer).update(user=new_buyer)
    CreditCardToken.objects.filter(user=old_buyer).update(user=new_buyer)


def cancel_deliverable(deliverable, requested_by):
    from apps.sales.models import CANCELLED, VOID
    deliverable.status = CANCELLED
    deliverable.cancelled_on = timezone.now()
    deliverable.save()
    deliverable.invoice.status = VOID
    if requested_by != deliverable.order.seller:
        notify(SALE_UPDATE, deliverable, unique=True, mark_unread=True)
    if requested_by != deliverable.order.buyer:
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)


def lines_by_priority(
        lines: Iterator[Union['LineItem', 'LineItemSim']]) -> List[List[Union['LineItem', 'LineItemSim']]]:
    """
    Groups line items by priority.
    """
    priority_sets = defaultdict(list)
    for line in lines:
        priority_sets[line.priority].append(line)
    return [priority_set for _, priority_set in sorted(priority_sets.items())]


def distribute_reduction(
        *, total: Money, distributed_amount: Money, line_values: 'LineMoneyMap'
) -> 'LineMoneyMap':
    reductions = {}
    if total.amount == 0:
        return reductions
    for line, original_value in line_values.items():
        if original_value < Money(0, total.currency):
            continue
        multiplier = original_value / total
        reductions[line] = Money(distributed_amount.amount * multiplier, total.currency)
    return reductions


@half_even_context
def priority_total(
        current: (Money, Money, 'LineMoneyMap'), priority_set: List['Line']
) -> (Money, 'LineMoneyMap'):
    """
    Get the effect on the total of a priority set. First runs any percentage increase, then
    adds in the static amount. Calculates the difference of each separately to make sure they're not affecting each
    other.
    """
    current_total, discount, subtotals = current
    working_subtotals = {}
    summable_totals = {}
    reductions: List['LineMoneyMap'] = []
    for line in priority_set:
        cascaded_amount = Money(0, current_total.currency)
        added_amount = Money(0, current_total.currency)
        # Percentages with equal priorities should not stack.
        multiplier = (Decimal('.01') * line.percentage)
        if line.back_into_percentage:
            working_amount = (current_total / (multiplier + Decimal('1.00'))) * multiplier
        else:
            working_amount = current_total * (Decimal('.01') * line.percentage)
        if line.cascade_percentage:
            cascaded_amount += working_amount
        else:
            added_amount += working_amount
        if line.cascade_amount:
            cascaded_amount += line.amount
        else:
            added_amount += line.amount
        working_amount += line.amount
        if cascaded_amount:
            reductions.append(distribute_reduction(
                total=current_total - discount, distributed_amount=cascaded_amount, line_values={
                    key: value for key, value in subtotals.items() if key.priority < line.priority
                }))
        if added_amount:
            summable_totals[line] = added_amount
        working_subtotals[line] = working_amount
        if working_amount < Money(0, working_amount.currency):
            discount += working_amount
    new_subtotals = {**subtotals}
    for reduction_set in reductions:
        for line, reduction in reduction_set.items():
            new_subtotals[line] -= reduction
    return current_total + sum(summable_totals.values()), discount, {**new_subtotals, **working_subtotals}


@floor_context
def to_distribute(total: Money, money_map: 'LineMoneyMap') -> Money:
    combined_sum = sum([value.round(2) for value in money_map.values()])
    difference = total - combined_sum
    upper_bound = Money(Decimal(len(money_map)) * Decimal('0.01'), total.currency)
    if difference > upper_bound:
        raise ValueError(f'Too many fractions! {difference} > {upper_bound}')
    return difference


def biggest_first(item: Tuple['LineItem', Decimal]) -> Tuple[Decimal, int]:
    return -item[1], item[0].id


@floor_context
def distribute_difference(difference: Money, money_map: 'LineMoneyMap') -> 'LineMoneyMap':
    """
    So. We have a few leftover pennies. To figure out where we should allocate them,
    we need to zero out everything but the remainder (that is, everything but what's beyond
    the cents place), and then compare what remains. The largest numbers are the numbers that
    were closest to rolling over into another penny, so we put them there first.

    We also floor all of the amounts to make sure that the discrete total of all values will be
    the correct target, and each value will be representable as a real monetary value-- that is,
    something no more fractionalized than cents.
    """
    updated_map = {key: value.round(2) for key, value in money_map.items()}
    test_map = {key: value - value.round(2) for key, value in money_map.items()}
    sorted_values = [(key, value) for key, value in test_map.items()]
    sorted_values.sort(key=biggest_first)
    remaining = difference
    amount = Money('0.01', remaining.currency)
    while remaining > Money('0.00', remaining.currency):
        key = sorted_values.pop(0)[0]
        updated_map[key] += amount
        remaining -= amount
    return updated_map


def normalized_lines(priority_sets: List[List[Union['LineItem', 'LineItemSim']]]):
    total, discount, subtotals = reduce(
        priority_total, priority_sets, (Money('0.00', 'USD'), Money('0.00', 'USD'), {}),
    )
    total = total.round(2)
    difference = to_distribute(total, subtotals)
    if difference > Money('0', difference.currency):
        subtotals = distribute_difference(difference, subtotals)
    else:
        subtotals = {key: value.round(2) for key, value in subtotals.items()}
    return total, discount, subtotals


@floor_context
def get_totals(lines: Iterator['Line']) -> (Money, Money, 'LineMoneyMap'):
    priority_sets = lines_by_priority(lines)
    return normalized_lines(priority_sets)


def reckon_lines(lines) -> Money:
    """
    Reckons all line items to produce a total value.
    """
    value, discount, _subtotals = get_totals(lines)
    return value.round(2)


def digits(currency: Currency) -> int:
    return len(str(currency.sub_unit)) - 1


@floor_context
def divide_amount(amount: Money, divisor: int) -> List[Money]:
    """
    Takes an amount of money, and divides it as evenly as possible according to divisor.
    Then, allocate remaining 'pennies' of the currency to the entries until the total number of discrete values
    is accounted for.

    TODO: Replicate in JS version
    """
    assert amount == amount.round(digits(amount.currency))
    target_amount = amount / divisor
    target_amount = target_amount.round(digits(amount.currency))
    difference = amount - (target_amount * divisor).round(digits(amount.currency))
    difference *= target_amount.currency.sub_unit
    difference = int(difference.amount)
    result = [target_amount] * divisor
    if digits(target_amount.currency):
        penny_amount = Money(Decimal('0.' + ('0' * (digits(target_amount.currency) - 1)) + '1'), target_amount.currency)
    else:
        penny_amount = Money('1', target_amount.currency)
    assert difference >= 0
    # It's probably not possible for it to loop around again, but I'm not a confident
    # enough mathematician to disprove it, especially since I'm unsure how having discrete values factors in for edge
    # cases. If someone else can be more assured, I'm good with simplifying this loop.
    while difference:
        for index, item in enumerate(result):
            result[index] += penny_amount
            difference -= 1
            if not difference:
                break
    return result


@floor_context
def lines_to_transaction_specs(lines: Iterator['LineItem']) -> 'TransactionSpecMap':
    from apps.sales.models import BONUS, SHIELD, ADD_ON, BASE_PRICE, TABLE_SERVICE, TAX, EXTRA, TIP, TransactionRecord
    type_map = {
        BONUS: TransactionRecord.SHIELD_FEE,
        SHIELD: TransactionRecord.SHIELD_FEE,
        TABLE_SERVICE: TransactionRecord.TABLE_SERVICE,
        TAX: TransactionRecord.TAX,
        ADD_ON: TransactionRecord.ESCROW_HOLD,
        BASE_PRICE: TransactionRecord.ESCROW_HOLD,
        TIP: TransactionRecord.ESCROW_HOLD,
        EXTRA: TransactionRecord.EXTRA_ITEM,
    }
    priority_sets = lines_by_priority(lines)
    total, __, subtotals = normalized_lines(priority_sets)
    transaction_specs = defaultdict(lambda: Money('0.00', 'USD'))
    for line_item, subtotal in subtotals.items():
        transaction_specs[
            line_item.destination_user, line_item.destination_account, type_map[line_item.type]
        ] += subtotal
    return transaction_specs


if TYPE_CHECKING:
    from apps.sales.models import Order, Deliverable


def fetch_prefixed(prefix: str, values: List[str]) -> str:
    for entry in values:
        if entry.startswith(prefix):
            return entry
    raise ValueError(f'Could not find an entry starting with {prefix} in {values}')


def verify_total(deliverable: 'Deliverable'):
    total = deliverable.invoice.total()
    if total < Money(0, 'USD'):
        raise ValidationError({'amount': ['Total cannot end up less than $0.']})
    if total == Money(0, 'USD'):
        return
    if (not deliverable.escrow_disabled) and total < Money(settings.MINIMUM_PRICE, 'USD'):
        raise ValidationError({'amount': [f'Total cannot end up less than ${settings.MINIMUM_PRICE}.']})


def issue_refund(transaction_set: Iterator['TransactionRecord'], category: int, processor: str) -> List['TransactionRecord']:
    from apps.sales.models import TransactionRecord
    last_four = None
    transactions = [*transaction_set]
    cash_transactions = [
        transaction for transaction in transaction_set if transaction.source == TransactionRecord.CASH_DEPOSIT
    ]
    card_transactions = [transaction for transaction in transaction_set if transaction.source == TransactionRecord.CARD]
    for transaction in card_transactions:
        remote_ids = transaction.remote_ids
        last_four = transaction.card and transaction.card.last_four
        break
    if not len(cash_transactions) == len(transactions):
        assert remote_ids, 'Could not find a remote transaction ID to refund.'
        assert (processor == STRIPE) or last_four, 'Could not determine the last four digits of the relevant card.'
    refund_transactions = []
    for transaction in transactions:
        record = TransactionRecord.objects.create(
            source=transaction.destination,
            destination=transaction.source,
            status=TransactionRecord.FAILURE,
            category=category,
            payer=transaction.payee,
            payee=transaction.payer,
            card=transaction.card,
            amount=transaction.amount,
            remote_ids=transaction.remote_ids,
            response_message="Failed when contacting payment processor.",
        )
        record.targets.set(transaction.targets.all())
        refund_transactions.append(record)
    amount = sum(transaction.amount for transaction in card_transactions)
    if card_transactions:
        try:
            auth_code = '******'
            try:
                intent_token = fetch_prefixed('pi_', remote_ids)
            except ValueError:
                raise ValueError('Invalid Stripe payment ID. Please contact support!')
            with stripe as stripe_api:
                # Note: We will assume success here. If there is a refund failure we'll have to dive into it
                # manually anyway and will find it during the accounting rounds.
                # TODO: Fix this.
                refund_payment_intent(amount=amount, api=stripe_api, intent_token=intent_token)['id']
            for transaction in refund_transactions:
                transaction.status = TransactionRecord.SUCCESS
                if transaction.destination == TransactionRecord.CARD:
                    transaction.remote_ids = remote_ids
                    transaction.auth_code = auth_code
                transaction.response_message = ''
        except Exception as err:
            for transaction in refund_transactions:
                transaction.response_message = str(err)
        finally:
            for transaction in refund_transactions:
                transaction.save()
    else:
        for transaction in refund_transactions:
            transaction.status = TransactionRecord.SUCCESS
            transaction.response_message = ''
            transaction.save()
    return refund_transactions


def ensure_buyer(order: 'Order'):
    """
    Makes sure there's a buyer attached to the order. Creates one if none has been set.
    """
    from apps.sales.models import buyer_subscriptions
    from apps.profiles.utils import create_guest_user
    if order.buyer:
        return
    assert order.customer_email, "No customer, and customer email not set on order."
    # Create the buyer now as a guest.
    user = create_guest_user(order.customer_email)
    order.buyer = user
    order.save()
    for deliverable in order.deliverables.all():
        Subscription.objects.bulk_create(buyer_subscriptions(deliverable), ignore_conflicts=True)


def update_order_payments(deliverable: 'Deliverable'):
    """
    Find existing payment actions for an order, and sets the payer to the current buyer.
    This is useful when a order was once created by a guest but later chowned over to a registered user.
    """
    from apps.sales.models import TransactionRecord
    TransactionRecord.objects.filter(
        source__in=[TransactionRecord.CARD, TransactionRecord.CASH_DEPOSIT],
        targets__object_id=deliverable.id, targets__content_type=ContentType.objects.get_for_model(deliverable),
    ).update(payer=deliverable.order.buyer)


def get_claim_token(order: 'Order') -> Union[str, None]:
    """Determines whether this order should have a claim token, and, if so, generates one if it does not exist,
    after which it returns whatever claim token is available or None.
    """
    if order.buyer and order.buyer.guest:
        if not order.claim_token:
            order.claim_token = gen_shortcode()
            order.save()
    return order.claim_token


def default_deliverable(order: 'Order') -> Union['Deliverable', None]:
    try:
        return order.deliverables.get()
    except MultipleObjectsReturned:
        return None


def get_view_name(deliverable: 'Deliverable') -> str:
    """
    Determines the most relevant view at any given time for a deliverable. For instance, if the deliverable is awaiting
    payment, the payment view is the most relevant. Note that the string this returns is intended to be combined with
    a prefix, so if this returns 'DeliverablePayment', then the view on the frontend might be 'OrderDeliverablePayment',
    'SaleDeliverablePayment', or 'CaseDeliverablePayment'.
    """
    from apps.sales.models import IN_PROGRESS, QUEUED, PAYMENT_PENDING, REVIEW
    if deliverable.status in [IN_PROGRESS, QUEUED, REVIEW]:
        return 'DeliverableRevisions'
    if deliverable.status == PAYMENT_PENDING:
        return 'DeliverablePayment'
    return 'DeliverableOverview'


class OrderContext(TypedDict):
    view_name: str
    base_name: str
    username: str
    latest_settlement: date
    claim: bool
    deliverable_id: int
    order_id: int
    claim_token: Union[str, None]
    extra_params: dict


def order_context(
        *, order: 'Order', user: User, logged_in: bool,
        deliverable: Union['Deliverable', None] = None,
        view_name: Union[str, None] = None,
        extra_params: Union[dict, None] = None,
) -> OrderContext:
    context = {'view_name': view_name or '', 'order_id': order.id, 'extra_params': extra_params or {}}
    if order.seller == user:
        context['base_name'] = 'Sale'
    elif deliverable and deliverable.arbitrator == user:
        context['base_name'] = 'Case'
    else:
        context['base_name'] = 'Order'
    context['username'] = user.username
    deliverable = deliverable or default_deliverable(order)
    context['claim'] = user.guest and not logged_in
    context['claim_token'] = get_claim_token(order)
    context['deliverable_id'] = deliverable and deliverable.id
    if deliverable and not view_name:
        context['view_name'] = get_view_name(deliverable)
    elif view_name:
        context['view_name'] = view_name
    return context


def order_context_to_link(context: OrderContext):
    goal_path = {
        'name': context['base_name'] + context['view_name'],
        'params': {
            'username': context['username'],
            'orderId': context['order_id'],
            'deliverableId': context['deliverable_id'],
            **context['extra_params'],
        },
    }
    if context['claim']:
        goal_path['params']['username'] = '_'
        return {
            'name': 'ClaimOrder',
            'params': {
                'orderId': context['order_id'],
                'claimToken': context['claim_token'],
                'deliverableId': context['deliverable_id'],
                'next': quote(json.dumps(goal_path), safe=''),
            },
        }
    return goal_path


@atomic
def destroy_deliverable(deliverable: 'Deliverable'):
    from apps.sales.models import CANCELLED
    if deliverable.status != CANCELLED:
        raise IntegrityError('Can only destroy cancelled orders!')
    references = list(deliverable.reference_set.all())
    deliverable.reference_set.clear()
    for reference in references:
        if not reference.deliverables.exists():
            reference.delete()
    for revision in deliverable.revision_set.all():
        revision.delete()
    order = deliverable.order
    deliverable.delete()
    if not order.deliverables.exists():
        order.delete()


class UserPaymentException(Exception):
    pass


class PaymentAttempt(TypedDict, total=False):
    cash: bool
    remote_ids: List[str]
    card_id: int
    amount: Money
    number: str
    exp_date: date
    cvv: str
    first_name: str
    last_name: str
    country: str
    zip: str
    save_card: bool
    make_primary: bool
    # Used only in premium upgrade transactions
    service: 'ServicePlan'
    # Should never exist unless through a webhook.
    stripe_event: dict


TransactionInitiator = Callable[[PaymentAttempt, Money, User, dict], List['TransactionRecord']]
TransactionMutator = Callable[[List['TransactionRecord'], PaymentAttempt, User, dict], None]


def dummy_mutator(transactions: List['TransactionRecord'], attempt: PaymentAttempt, user: User, context: dict):
    """No-op mutator function for use in perform_charge's hooks."""
    pass


def perform_charge(
        *, attempt: PaymentAttempt, amount: Money, user: User, requesting_user: User,
        initiate_transactions: TransactionInitiator, post_success: TransactionMutator = dummy_mutator,
        post_save: TransactionMutator = dummy_mutator, context: dict,
) -> Tuple[bool, List['TransactionRecord'], str]:
    """
    Convenience function for web-facing charges. Takes a payment data dictionary and determines which kind of payment
    is being submitted from the client, then routes the payment according to permissions and payment type.
    """
    if attempt.get('cash', False) and requesting_user.is_staff:
        return from_cash(
            attempt=attempt, amount=amount, user=user, initiate_transactions=initiate_transactions,
            post_save=post_save, post_success=post_success, context=context,
        )
    if attempt.get('remote_ids') and (requesting_user.is_staff or attempt.get('stripe_event')):
        return from_remote_id(
            attempt=attempt, amount=amount, user=user, remote_ids=attempt.get('remote_ids'),
            initiate_transactions=initiate_transactions, post_save=post_save, post_success=post_success,
            context=context,
        )
    else:
        raise RuntimeError('Could not identify the right way to perform this charge.')


def from_cash(
        *, attempt: PaymentAttempt, amount: Money, user: User, initiate_transactions: TransactionInitiator,
        post_success: TransactionMutator, post_save: TransactionMutator, context: dict,
):
    """
    Function for marking payment made via cash. This should only ever be invoked through permission checked staff
    channels because we're essentially telling the system 'trust me, this has been paid for' and to just move the
    transaction along.
    """
    from apps.sales.models import TransactionRecord
    transactions = initiate_transactions(attempt, amount, user, context)
    for transaction in transactions:
        transaction.status = TransactionRecord.SUCCESS
        transaction.source = TransactionRecord.CASH_DEPOSIT
    post_success(transactions, attempt, user, context)
    for transaction in transactions:
        transaction.save()
    post_save(transactions, attempt, user, context)
    return True, transactions, ''


def from_remote_id(
        *, attempt: PaymentAttempt, amount: Money, user: User, remote_ids: List[str],
        initiate_transactions: TransactionInitiator, post_success: TransactionMutator,
        post_save: TransactionMutator, context: dict,
) -> Tuple[bool, List['TransactionRecord'], str]:
    """
    Mark this as paid via remote transaction ID from the card processor.
    """
    # This may not work if charging via stripe terminal.
    # We'll be checking this elsewhere if the stripe event is provided.
    details = {'auth_amount': attempt['amount']}
    # Bogus auth code so things don't break. Need to remove this eventually-- it's a holdover from Authorize.net.
    auth_code = '******'
    stripe_event = attempt['stripe_event']
    if stripe_event['status'] not in ['succeeded', 'failed']:
        error = f'Unhandled charge status, {stripe_event["status"]} for remote_ids {remote_ids}'
        return False, annotate_error(
            transactions=[],
            # RuntimeError shouldn't be caught, ensuring this throws properly.
            error=error,
            attempt=attempt,
            user=user,
            post_save=post_save,
            context=context,
        ), error
    transactions = initiate_transactions(attempt, amount, user, context)
    if stripe_event['status'] == 'failed':
        error = f'{stripe_event["failure_code"]}: {stripe_event["failure_message"]}'
        return False, annotate_error(
            transactions=transactions,
            error=error,
            attempt=attempt,
            user=user,
            post_save=post_save,
            context=context,
        ), error
    # We're assuming we'll not be encountering 'pending' here. We have no card transactions which should require it.
    mark_successful(
        transactions=transactions, remote_ids=remote_ids, auth_code=auth_code, post_success=post_success,
        post_save=post_save, context=context, attempt=attempt, user=user,
    )
    return True, transactions, ''


def annotate_error(
        *, transactions: List['TransactionRecord'], error: str, attempt: PaymentAttempt, user: User,
        post_save: TransactionMutator, context: dict,
) -> List['TransactionRecord']:
    """
    Annotates a set of transactions with an error and then returns the appropriate status code.
    """
    from apps.sales.models import TransactionRecord
    response_message = error
    for transaction in transactions:
        transaction.status = TransactionRecord.FAILURE
        transaction.response_message = response_message
        transaction.save()
    post_save(transactions, attempt, user, context)
    return transactions


def mark_successful(
        *, transactions: List['TransactionRecord'], remote_ids: List[str], auth_code: str,
        post_success: TransactionMutator,
        post_save: TransactionMutator, attempt: PaymentAttempt, user: User, context: dict,
):
    """
    Marks a set of transactions as successful.
    """
    from apps.sales.models import TransactionRecord
    for transaction in transactions:
        transaction.status = TransactionRecord.SUCCESS
        transaction.remote_ids.extend(remote_ids)
        transaction.remote_ids = list(set(transaction.remote_ids))
        transaction.auth_code = auth_code
        # We have a failure message that gets set here by default. Clear it.
        transaction.response_message = ''
    post_success(transactions, attempt, user, context)
    for transaction in transactions:
        transaction.save()
    post_save(transactions, attempt, user, context)


@ceiling_context
def initialize_stripe_charge_fees(amount: Money, stripe_event: dict):
    """Return a set of initialized transactions that mark what fees we paid to stripe for a card charge."""
    from apps.sales.models import TransactionRecord
    if 'card_present' in stripe_event['payment_method_details']:
        fee = (amount * (settings.STRIPE_CARD_PRESENT_PERCENTAGE / 100)).round(2)
        fee += settings.STRIPE_CARD_PRESENT_STATIC
    else:
        fee = (amount * (settings.STRIPE_CHARGE_PERCENTAGE / 100)).round(2)
        fee += settings.STRIPE_CHARGE_STATIC
    return [
        TransactionRecord(
            source=TransactionRecord.UNPROCESSED_EARNINGS,
            destination=TransactionRecord.CARD_TRANSACTION_FEES,
            category=TransactionRecord.THIRD_PARTY_FEE,
            amount=fee,
        )
    ]


def deliverable_initialize_transactions(
        attempt: PaymentAttempt, amount: Money, user: User, context: dict,
) -> List['TransactionRecord']:
    from apps.sales.models import TransactionRecord
    deliverable = context['deliverable']
    transaction_specs = lines_to_transaction_specs(deliverable.invoice.line_items.all())
    # TODO: This should probably be decided some other way/earlier in the process.
    if attempt.get('cash'):
        source = TransactionRecord.CASH_DEPOSIT
    else:
        source = TransactionRecord.CARD
    transactions = [
        TransactionRecord(
            payer=deliverable.order.buyer,
            status=TransactionRecord.FAILURE,
            category=category,
            source=source,
            payee=destination_user,
            destination=destination_account,
            amount=value,
            response_message="Failed when contacting payment processor.",
        ) for ((destination_user, destination_account, category), value) in transaction_specs.items()
    ]
    if deliverable.processor == STRIPE and source == TransactionRecord.CARD:
        transactions.extend(initialize_stripe_charge_fees(amount=amount, stripe_event=attempt['stripe_event']))
    return transactions


def deliverable_post_save(transactions: List['TransactionRecord'], attempt: PaymentAttempt, user: User, context: dict):
    """
    Post-save perform_charge hook for deliverable.
    """
    deliverable = context['deliverable']
    deliverable_ref = ref_for_instance(deliverable)
    invoice_ref = ref_for_instance(deliverable.invoice)
    for transaction in transactions:
        transaction.targets.add(invoice_ref, deliverable_ref)


def premium_initiate_transactions(
        data: PaymentAttempt, amount: Money, user: User, context: dict,
) -> List['TransactionRecord']:
    from apps.sales.models import TransactionRecord
    return [TransactionRecord.objects.create(
        payer=user,
        payee=None,
        source=TransactionRecord.CARD,
        destination=TransactionRecord.UNPROCESSED_EARNINGS,
        category=TransactionRecord.SUBSCRIPTION_DUES,
        status=TransactionRecord.FAILURE,
        amount=amount,
        response_message='Failed when contacting payment processor.',
    )]


def premium_post_success(invoice, service_plan):
    from apps.sales.models import PAID

    def wrapped(transactions: List['TransactionRecord'], data: PaymentAttempt, user: User, context: dict):
        for transaction in transactions:
            transaction.response_message = 'Upgraded to landscape'
        set_premium(user, service_plan, target_date=date.today() + relativedelta(months=1))
        invoice.paid_on = timezone.now()
        invoice.status = PAID
        invoice.save()
        user.current_intent = ''
        user.save(update_fields=['current_intent'])
    return wrapped


def premium_post_save(invoice, remote_ids=None):
    def wrapped(transactions: List['TransactionRecord'], data: PaymentAttempt, user: User, context: dict):
        invoice_ref = ref_for_instance(invoice)
        for transaction in transactions:
            transaction.targets.add(invoice_ref)
            if remote_ids:
                transaction.remote_ids = list(set(transaction.remote_ids + remote_ids))
    return wrapped


def pay_deliverable(*, attempt: PaymentAttempt, deliverable: 'Deliverable', requesting_user: User) -> Tuple[bool, List['TransactionRecord'], str]:
    from apps.sales.models import IN_PROGRESS, QUEUED, REVIEW
    from apps.profiles.utils import credit_referral
    if attempt['amount'] != deliverable.invoice.total():
        return False, [], 'The price has changed. Please refresh.'
    try:
        ensure_buyer(deliverable.order)
    except AssertionError:
        return False, [], 'No buyer is set for this order, nor is there a customer email set.'
    success, records, message = perform_charge(
        attempt=attempt, amount=attempt['amount'], user=deliverable.order.buyer,
        requesting_user=requesting_user, post_save=deliverable_post_save,
        context={'deliverable': deliverable}, initiate_transactions=deliverable_initialize_transactions,
    )
    if not success:
        return success, records, message
    if deliverable.final_uploaded:
        deliverable.status = REVIEW
        deliverable.auto_finalize_on = (timezone.now() + relativedelta(days=2)).date()
        early_finalize(deliverable, requesting_user)
    elif deliverable.revision_set.all().exists():
        deliverable.status = IN_PROGRESS
    else:
        deliverable.status = QUEUED
    deliverable.revisions_hidden = False
    # Save the original turnaround/weight.
    deliverable.task_weight = (
            (deliverable.product and deliverable.product.task_weight)
            or deliverable.task_weight
    )
    deliverable.expected_turnaround = (
            (deliverable.product and deliverable.product.expected_turnaround)
            or deliverable.expected_turnaround
    )
    deliverable.dispute_available_on = (
        timezone.now() + BDay(
            ceil(
                ceil(deliverable.expected_turnaround + deliverable.adjustment_expected_turnaround) * 1.25))
    ).date()
    deliverable.paid_on = timezone.now()
    # Preserve this so it can't be changed during disputes.
    deliverable.commission_info = deliverable.order.seller.artist_profile.commission_info
    deliverable.save()
    notify(SALE_UPDATE, deliverable, unique=True, mark_unread=True)
    credit_referral(deliverable)
    return success, records, message


def get_term_invoice(user: User) -> 'Invoice':
    from apps.sales.models import Invoice, OPEN, SUBSCRIPTION
    return Invoice.objects.get_or_create(status=OPEN, bill_to=user, type=SUBSCRIPTION)[0]


def get_intent_card_token(user: User, card_id: Optional[str]):
    from apps.sales.models import CreditCardToken
    if card_id:
        stripe_token = get_object_or_404(CreditCardToken, id=card_id, user=user).stripe_token
        if not stripe_token:
            raise Http404('That card ID is not a stripe card.')
        return stripe_token
    if user.primary_card and user.primary_card.stripe_token:
        return user.primary_card.stripe_token
    return None


def default_callable(target: Model):
    """
    We'll determine what the default callable for this model is. For the moment, we're storing this value
    as a property on the model, but we may eventually want to create some sort of registry if we end up factoring
    this out.
    """
    return getattr(target, 'post_pay_hook', None)


def post_pay_hook(*, billable: Union['Invoice', 'LineItem'], target: Model, context: dict) -> List['TransactionRecord']:
    """
    Determine the appropriate function call for a billable. These functions should always return a list of
    TransactionRecords.
    """
    to_call = import_string(context.get('__callable__', default_callable(target)))
    if not to_call:
        return []
    return to_call(billable=billable, target=target, context=context)


def paired_iterator(always: Any, iterator: Iterator):
    """
    Generator function that always returns a tuple with the first value as it iterates over the second value.
    """
    for item in iterator:
        yield always, item


def hacky_invoice_post_save(transactions: List['TransactionRecord'], attempt: PaymentAttempt, user: User, context: dict):
    """
    Post-save perform_charge hook for deliverable.
    """
    invoice = context['invoice']
    invoice_ref = ref_for_instance(invoice)
    for transaction in transactions:
        transaction.targets.add(invoice_ref)


def hacky_invoice_initiate_transactions(
        attempt: PaymentAttempt, amount: Money, user: User, context: dict,
) -> List['TransactionRecord']:
    from apps.sales.models import TransactionRecord
    invoice = context['invoice']
    transaction_specs = lines_to_transaction_specs(invoice.line_items.all())
    transactions = [
        TransactionRecord(
            payer=invoice.bill_to,
            status=TransactionRecord.FAILURE,
            category=category,
            source=TransactionRecord.CARD,
            payee=destination_user,
            destination=destination_account,
            amount=value,
            response_message="Failed when contacting payment processor.",
        ) for ((destination_user, destination_account, category), value) in transaction_specs.items()
    ]
    if attempt.get('stripe_event'):
        transactions.extend(initialize_stripe_charge_fees(amount=amount))
    return transactions


def hacky_transaction_creation(invoice: 'Invoice', context: dict):
    from apps.sales.views.helpers import remote_ids_from_charge
    attempt = context.get('attempt')
    if not attempt:
        charge_event = context['stripe_event']['data']['object']
        amount = context['amount']
        attempt = {
            'stripe_event': charge_event,
            'amount': amount,
            'remote_ids': remote_ids_from_charge(charge_event),
        }
    success, records, message = perform_charge(
        attempt=attempt, amount=attempt['amount'], user=invoice.bill_to,
        requesting_user=context.get('requesting_user', invoice.bill_to), post_save=hacky_invoice_post_save,
        context={'invoice': invoice}, initiate_transactions=hacky_invoice_initiate_transactions,
    )
    return records


@transaction.atomic
def invoice_post_payment(invoice: 'Invoice', context: dict) -> List['TransactionRecord']:
    """
    Post-pay hook. This iterates through all targets and all targets on all line items, and then runs hooks for
    each. Any asynchronous operations that should occur should be scheduled tasks that can verify finished state
    and start afterwards. Otherwise they might run with a DB that failed the transaction.

    Note that a payment may be 'failed.' We still call the post-payment hooks as they may need to perform some task
    like creating failed transaction records for reference. Payments that have failed will have successful=False in
    the context dictionary.
    """
    from apps.sales.models import PAID
    all_targets = (
        paired_iterator(invoice, invoice.targets.all()),
        *(
            paired_iterator(line_item, line_item.targets.all())
            for line_item in invoice.line_items.all().prefetch_related('targets')
        ),
    )
    records = []
    for billable, target in chain(*all_targets):
        if not target.target:
            raise IntegrityError(
                f'{target.__class__.__name__} for deleted item paid: #{invoice.id}, GenericReference {target.id}',
            )
        records.extend(post_pay_hook(billable=billable, target=target.target, context={**context, **billable.context_for(target)}))
    if invoice.creates_own_transactions:
        records.extend(hacky_transaction_creation(invoice, context))
    if context['successful']:
        invoice.paid_on = timezone.now()
        invoice.status = PAID
        invoice.save()
    return records


class AccountMutex:
    def __init__(self, users: List[User]):
        # Not 100% sure on this, but I think we can avoid deadlocks if we always lock users in the same order, even if
        # there are multiple, since one thread will always be ahead of the other.
        self.users = sorted(list(set(users)))
        self.mutexes = []
        self.acquired = []

    def __enter__(self):
        for user in self.users:
            lock_name = f'account_mutex__{user.id}'
            self.mutexes.append(cache.lock(lock_name))
        for lock in self.mutexes:
            lock.__enter__()
            self.acquired.append(lock)

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        result = []
        for lock in self.acquired:
            result.append(lock.__exit__(exc_type, exc_val, exc_tb))
        return all(result)
