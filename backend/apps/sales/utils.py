import logging
from collections import defaultdict
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
from functools import reduce
from typing import Union, Type, TYPE_CHECKING, List, Dict, Iterator, Callable

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum, Q, IntegerField, Case, When, F
from django.db.transaction import atomic
from django.utils import timezone
from django.utils.datetime_safe import date
from moneyed import Money
from rest_framework.exceptions import ValidationError

from apps.lib.models import Subscription, COMMISSIONS_OPEN, Event, DISPUTE, SALE_UPDATE, Notification, \
    Comment, ORDER_UPDATE
from apps.lib.utils import notify, recall_notification
from apps.profiles.models import User, VERIFIED
from apps.sales.authorize import refund_transaction

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

    return credit - debit


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
    if service == 'landscape':
        if user.portrait_paid_through and user.portrait_paid_through > date.today():
            price -= Money(settings.PORTRAIT_PRICE, 'USD')
    return price


def set_service(user, service, target_date=None):
    if service == 'portrait':
        user.portrait_enabled = True
        user.landscape_enabled = False
    else:
        user.landscape_enabled = True
        user.portrait_enabled = False
    if target_date:
        setattr(user, service + '_paid_through', target_date)
        # Landscape includes portrait, so this is always set regardless.
        user.portrait_paid_through = target_date
        for watched in user.watching.all():
            content_type = ContentType.objects.get_for_model(watched)
            sub, _ = Subscription.objects.get_or_create(
                subscriber=user,
                content_type=content_type,
                object_id=watched.id,
                type=COMMISSIONS_OPEN
            )
            sub.until = target_date
            sub.telegram = True
            sub.email = True
            sub.save()
    user.save()


def check_charge_required(user, service):
    if service == 'portrait':
        if user.landscape_paid_through:
            if user.landscape_paid_through >= date.today():
                return False, user.landscape_paid_through
        if user.portrait_paid_through:
            if user.portrait_paid_through >= date.today():
                return False, user.portrait_paid_through
    else:
        if user.landscape_paid_through:
            if user.landscape_paid_through >= date.today():
                return False, user.landscape_paid_through
    return True, None


def available_products_by_load(seller_profile, load=None):
    from apps.sales.models import Product
    if load is None:
        load = seller_profile.load
    return Product.objects.filter(user_id=seller_profile.user_id, active=True, hidden=False).exclude(
        task_weight__gt=seller_profile.max_load - load
    ).exclude(Q(parallel__gte=F('max_parallel')) & ~Q(max_parallel=0))


def available_products_from_user(seller_profile):
    from apps.sales.models import Product
    if seller_profile.commissions_closed or seller_profile.commissions_disabled:
        return Product.objects.none()
    return available_products_by_load(seller_profile)


# Primitive recursion check lock.
UPDATING = {}


def update_availability(seller, load, current_closed_status):
    from apps.sales.models import Order
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
        elif not seller.sales.filter(status=Order.NEW).exists():
            seller_profile.commissions_disabled = False
        seller_profile.load = load
        if products.exists() and not seller_profile.commissions_disabled:
            seller_profile.has_products = True
        seller_profile.save()
        products.update(available=True, edited_on=timezone.now())
        # Sanity setting.
        seller.products.filter(Q(hidden=True) | Q(active=False) | Q(inventory__count=0)).update(
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


def early_finalize(order, user: User):
    if (
            order.final_uploaded
            and order.seller.landscape
            and order.seller.trust_level == VERIFIED
            and not order.escrow_disabled
    ):
        order.trust_finalized = True
        finalize_order(order, user)


def allocate_bonus(order: 'Order', source_record: 'TransactionRecord'):
    from apps.sales.models import TransactionRecord, ref_for_instance
    amount = get_bonus_amount(order)
    bonus = TransactionRecord(
        payer=None,
        source=TransactionRecord.RESERVE,
        amount=amount,
        status=TransactionRecord.SUCCESS,
        remote_id=source_record.remote_id,
        auth_code=source_record.auth_code,
    )
    if order.seller.landscape:
        bonus.payee = order.seller
        bonus.destination = TransactionRecord.HOLDINGS
        bonus.category = TransactionRecord.PREMIUM_BONUS
    else:
        bonus.payee = None
        bonus.destination = TransactionRecord.UNPROCESSED_EARNINGS
        bonus.category = TransactionRecord.SHIELD_FEE
    bonus.save()
    bonus.targets.add(ref_for_instance(order))


def finalize_table_fees(order: 'Order'):
    from apps.sales.models import TransactionRecord, ref_for_instance
    ref = ref_for_instance(order)
    record = TransactionRecord.objects.get(
        payee=None, destination=TransactionRecord.RESERVE,
        status=TransactionRecord.SUCCESS,
    )
    record.targets.add(ref)
    TransactionRecord.objects.create(
        source=TransactionRecord.RESERVE,
        destination=TransactionRecord.UNPROCESSED_EARNINGS,
        amount=record.amount,
        payer=None, payee=None,
        status=TransactionRecord.SUCCESS,
        category=TransactionRecord.TABLE_SERVICE,
        remote_id=record.remote_id,
        auth_code=record.auth_code,
    )
    tax_record = TransactionRecord.objects.get(
        payee=None, destination=TransactionRecord.MONEY_HOLE_STAGE,
        status=TransactionRecord.SUCCESS,
    )
    tax_record.targets.add(ref)
    tax_burned = TransactionRecord.objects.create(
        source=TransactionRecord.MONEY_HOLE_STAGE,
        destination=TransactionRecord.MONEY_HOLE,
        amount=tax_record.amount,
        payer=None, payee=None,
        status=TransactionRecord.SUCCESS,
        category=TransactionRecord.TABLE_SERVICE,
        remote_id=tax_record.remote_id,
        auth_code=tax_record.auth_code,
    )
    tax_burned.targets.add(ref)


def finalize_order(order, user=None):
    from apps.sales.models import TransactionRecord, ref_for_instance
    from apps.sales.tasks import withdraw_all
    with atomic():
        if order.status == order.DISPUTED and user == order.buyer:
            # User is rescinding dispute.
            recall_notification(DISPUTE, order)
            # We'll pretend this never happened.
            order.disputed_on = None
        order.status = order.COMPLETED
        order.save()
        notify(SALE_UPDATE, order, unique=True, mark_unread=True)
        record = TransactionRecord.objects.get(
            payee=order.seller, destination=TransactionRecord.ESCROW,
            status=TransactionRecord.SUCCESS,
            targets__object_id=order.id, targets__content_type=ContentType.objects.get_for_model(order),
        )
        to_holdings = TransactionRecord.objects.create(
            payer=order.seller,
            payee=order.seller,
            amount=record.amount,
            source=TransactionRecord.ESCROW,
            destination=TransactionRecord.HOLDINGS,
            category=TransactionRecord.ESCROW_RELEASE,
            status=TransactionRecord.SUCCESS,
            remote_id=record.remote_id,
            auth_code=record.auth_code,
        )
        to_holdings.targets.add(ref_for_instance(order))
        if not order.table_order:
            allocate_bonus(order, record)
        else:
            finalize_table_fees(order)
    # Don't worry about whether it's time to withdraw or not. This will make sure that an attempt is made in case
    # there's money to withdraw that hasn't been taken yet, and another process will try again if it settles later.
    # It will also ignore if the seller has auto_withdraw disabled.
    withdraw_all.delay(order.seller.id)


def claim_order_by_token(order_claim, user):
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
    transfer_order(order, order.buyer, user)


def split_fee(transaction: 'TransactionRecord') -> 'TransactionRecord':
    from apps.sales.models import TransactionRecord
    base_amount = transaction.amount.amount - settings.SERVICE_STATIC_FEE
    withheld_amount = settings.PREMIUM_STATIC_BONUS
    withheld_amount += settings.PREMIUM_PERCENTAGE_BONUS * Decimal('.01') * base_amount
    withheld_amount = Money(withheld_amount, 'USD')
    return TransactionRecord.objects.create(
        payer=None,
        payee=None,
        amount=transaction.amount - withheld_amount,
        source=TransactionRecord.RESERVE,
        destination=TransactionRecord.UNPROCESSED_EARNINGS,
        remote_id=transaction.remote_id,
        auth_code=transaction.auth_code,
        status=TransactionRecord.SUCCESS,
        target=transaction.target,
        category=TransactionRecord.SHIELD_FEE,
    )


def get_bonus_amount(order: 'Order') -> Money:
    from apps.sales.models import BONUS
    bonus = order.line_items.filter(type=BONUS).first()
    if not bonus:
        return Money(0, 'USD')
    return get_totals(order.line_items.all())[2][bonus]


def recuperate_fee(record: 'TransactionRecord') -> 'TransactionRecord':
    from apps.sales.models import TransactionRecord, Order
    amount = get_bonus_amount(record.targets.filter(content_type=ContentType.objects.get_for_model(Order)).get().target)
    record = TransactionRecord.objects.create(
        status=TransactionRecord.SUCCESS,
        payer=None,
        payee=None,
        source=TransactionRecord.RESERVE,
        destination=TransactionRecord.UNPROCESSED_EARNINGS,
        amount=amount,
        category=TransactionRecord.SHIELD_FEE,
    )
    record.targets.set(record.targets.all())


def transfer_order(order, old_buyer, new_buyer):
    from apps.sales.models import buyer_subscriptions, CreditCardToken, ORDER_UPDATE
    assert old_buyer != new_buyer
    order.buyer = new_buyer
    order.customer_email = ''
    order.claim_token = None
    order.save()
    Subscription.objects.bulk_create(buyer_subscriptions(order), ignore_conflicts=True)
    notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
    update_order_payments(order)
    if not old_buyer:
        return
    assert old_buyer.guest
    Subscription.objects.filter(subscriber=old_buyer).delete()
    Notification.objects.filter(user=old_buyer).update(user=new_buyer)
    Comment.objects.filter(user=old_buyer).update(user=new_buyer)
    CreditCardToken.objects.filter(user=old_buyer).update(user=new_buyer)


def cancel_order(order, requested_by):
    from apps.sales.models import Order
    order.status = Order.CANCELLED
    order.save()
    if requested_by != order.seller:
        notify(SALE_UPDATE, order, unique=True, mark_unread=True)
    if requested_by != order.buyer:
        notify(ORDER_UPDATE, order, unique=True, mark_unread=True)


if TYPE_CHECKING:
    from apps.sales.models import LineItemSim, LineItem, TransactionRecord

    Line = Union[LineItem, LineItemSim]
    LineMoneyMap = Dict[Line, Money]
    TransactionSpecKey = (Union[User, None], int, int)
    TransactionSpecMap = Dict[TransactionSpecKey, Money]


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
        multiplier = (original_value / total).quantize(Decimal('.01'))
        reductions[line] = Money(distributed_amount.amount * multiplier, 'USD')
    return reductions


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
        cascaded_amount = Money(0, 'USD')
        added_amount = Money(0, 'USD')
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
                total=current_total, distributed_amount=cascaded_amount, line_values={
                    key: value for key, value in subtotals.items() if key.priority < line.priority
            }))
        if added_amount:
            summable_totals[line] = added_amount
        working_subtotals[line] = working_amount
    new_subtotals = {**subtotals}
    for reduction_set in reductions:
        for line, reduction in reduction_set.items():
            new_subtotals[line] -= reduction
    return current_total + sum(summable_totals.values()), discount, {**new_subtotals, **working_subtotals}


def get_totals(
        lines: Iterator['Line']) -> (Money, 'LineMoneyMap'):
    priority_sets = lines_by_priority(lines)
    with localcontext() as ctx:
        ctx.rounding = ROUND_HALF_EVEN
        value, discount, subtotals = reduce(
            priority_total, priority_sets, (Money('0.00', 'USD'), Money('0.00', 'USD'), {}),
        )
        for key, amount in subtotals.items():
            subtotals[key] = amount.round(2)
    return value.round(2), discount, subtotals


def reckon_lines(lines) -> Money:
    """
    Reckons all line items to produce a total value.
    """
    value, discount, _subtotals = get_totals(lines)
    return value.round(2)


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
    _, __, subtotals = reduce(priority_total, priority_sets, (Money('0.00', 'USD'), Money('0.00', 'USD'), {}))
    transaction_specs = defaultdict(lambda: Money('0.00', 'USD'))
    for line_item, subtotal in subtotals.items():
        transaction_specs[
            line_item.destination_user, line_item.destination_account, type_map[line_item.type]
        ] += subtotal
    return transaction_specs


if TYPE_CHECKING:
    from apps.sales.models import Order


def verify_total(order: 'Order'):
    total = order.total()
    if total < Money(0, 'USD'):
        raise ValidationError({'amount': ['Total cannot end up less than $0.']})
    if total == Money(0, 'USD'):
        return
    if (not order.escrow_disabled) and total < Money(settings.MINIMUM_PRICE, 'USD'):
        raise ValidationError({'amount': [f'Total cannot end up less than ${settings.MINIMUM_PRICE}.']})


def issue_refund(transaction_set: Iterator['TransactionRecord'], category: int) -> List['TransactionRecord']:
    from apps.sales.models import TransactionRecord
    remote_id = ''
    last_four = None
    transactions = [*transaction_set]
    cash_transactions = [
        transaction for transaction in transaction_set if transaction.source == TransactionRecord.CASH_DEPOSIT
    ]
    card_transactions = [transaction for transaction in transaction_set if transaction.source == TransactionRecord.CARD]
    for transaction in card_transactions:
        remote_id = transaction.remote_id
        last_four = transaction.card.last_four
    if not len(cash_transactions) == len(transactions):
        assert remote_id, 'Could not find a remote transaction ID to refund.'
        assert last_four, 'Could not determine the last four digits of the relevant card.'
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
            response_message="Failed when contacting payment processor.",
        )
        record.targets.set(transaction.targets.all())
        refund_transactions.append(record)
    amount = sum(transaction.amount for transaction in card_transactions)
    if card_transactions:
        try:
            remote_id, auth_code = refund_transaction(remote_id, last_four, amount)
            for transaction in refund_transactions:
                transaction.status = TransactionRecord.SUCCESS
                if transaction.destination == TransactionRecord.CARD:
                    transaction.remote_id = remote_id
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
    Subscription.objects.bulk_create(buyer_subscriptions(order), ignore_conflicts=True)


def update_order_payments(order: 'Order'):
    """
    Find existing payment actions for an order, and sets the payer to the current buyer.
    This is useful when a order was once created by a guest but later chowned over to a registered user.
    """
    from apps.sales.models import TransactionRecord
    TransactionRecord.objects.filter(
        source__in=[TransactionRecord.CARD, TransactionRecord.CASH_DEPOSIT],
        targets__object_id=order.id, targets__content_type=ContentType.objects.get_for_model(order),
    ).update(payer=order.buyer)


def decimal_context(wrapped: Callable):
    def wrapper(*args, **kwargs):
        with localcontext() as ctx:
            ctx.rounding = ROUND_HALF_EVEN
            return wrapped(*args, **kwargs)
    return wrapper
