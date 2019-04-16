import logging
from decimal import Decimal, InvalidOperation
from typing import Union, Type

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum, Q, IntegerField, Case, When, F
from django.db.transaction import atomic
from django.utils import timezone
from django.utils.datetime_safe import date
from moneyed import Money

from apps.lib.models import Subscription, COMMISSIONS_OPEN, Event, DISPUTE, SALE_UPDATE, Notification, \
    Comment
from apps.lib.utils import notify, recall_notification
from apps.profiles.models import User

logger = logging.getLogger(__name__)


class ALL:
    def __init__(self):
        raise RuntimeError('This class used as unique enum, not to be instantiated.')
    pass


AVAILABLE = 0
POSTED_ONLY= 1
PENDING = 2

def account_balance(user: Union[User, None, Type[ALL]], account_type: int, balance_type: int=AVAILABLE) -> Decimal:
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
    if requester.is_authenticated:
        if not requester.is_staff:
            qs = qs.exclude(user__blocking=requester)
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
        products.update(available=True)
        # Sanity setting.
        seller.products.filter(Q(hidden=True) | Q(active=False)).update(available=False)
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
            seller.products.all().update(available=False)
            recall_notification(COMMISSIONS_OPEN, seller)
    finally:
        del UPDATING[seller]


def finalize_order(order, user=None):
    from apps.sales.models import TransactionRecord
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
            payer=order.buyer, payee=order.seller, destination=TransactionRecord.ESCROW,
            status=TransactionRecord.SUCCESS, object_id=order.id, content_type=ContentType.objects.get_for_model(order),
        )
        TransactionRecord.objects.create(
            payer=order.seller,
            payee=order.seller,
            amount=record.amount,
            source=TransactionRecord.ESCROW,
            destination=TransactionRecord.HOLDINGS,
            target=order,
            category=TransactionRecord.ESCROW_RELEASE,
            status=TransactionRecord.SUCCESS,
            remote_id=record.remote_id,
        )
        amount = get_bonus_amount(record)
        bonus = TransactionRecord(
            payer=None,
            source=TransactionRecord.RESERVE,
            target=order,
            amount=amount,
            status=TransactionRecord.SUCCESS,
            remote_id=record.remote_id,
        )
        if order.seller.landscape:
            bonus.payee = order.seller
            bonus.destination=TransactionRecord.HOLDINGS
            bonus.category=TransactionRecord.PREMIUM_BONUS
        else:
            bonus.payee = None
            bonus.destination = TransactionRecord.UNPROCESSED_EARNINGS
            bonus.category = TransactionRecord.SERVICE_FEE
        bonus.save()
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
        status=TransactionRecord.SUCCESS,
        target=transaction.target,
        category=TransactionRecord.SERVICE_FEE,
    )


def get_bonus_amount(record) -> Money:
    from apps.sales.models import TransactionRecord
    fee_payment = TransactionRecord.objects.get(
        object_id=record.object_id,
        content_type_id=record.content_type_id,
        status=TransactionRecord.SUCCESS,
        payer=record.payer,
        payee=None,
        destination=TransactionRecord.RESERVE,
    )
    initial_split = TransactionRecord.objects.get(
        object_id=record.object_id,
        content_type_id=record.content_type_id,
        status=TransactionRecord.SUCCESS,
        payer=None,
        payee=None,
        source=TransactionRecord.RESERVE,
        destination=TransactionRecord.UNPROCESSED_EARNINGS,
    )
    return fee_payment.amount - initial_split.amount


def recuperate_fee(record: 'TransactionRecord') -> 'TransactionRecord':
    from apps.sales.models import TransactionRecord
    amount = get_bonus_amount(record)
    return TransactionRecord.objects.create(
        object_id=record.object_id,
        content_type_id=record.content_type_id,
        status=TransactionRecord.SUCCESS,
        payer=None,
        payee=None,
        source=TransactionRecord.RESERVE,
        destination=TransactionRecord.UNPROCESSED_EARNINGS,
        amount=amount,
        category=TransactionRecord.SERVICE_FEE,
    )


def transfer_order(order, old_buyer, new_buyer):
    from apps.sales.models import buyer_subscriptions, CreditCardToken, ORDER_UPDATE
    assert old_buyer != new_buyer
    order.buyer = new_buyer
    order.customer_email = ''
    order.claim_token = None
    order.save()
    Subscription.objects.bulk_create(buyer_subscriptions(order), ignore_conflicts=True)
    notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
    if not old_buyer:
        return
    assert old_buyer.guest
    Subscription.objects.filter(subscriber=old_buyer).delete()
    Notification.objects.filter(user=old_buyer).update(user=new_buyer)
    Comment.objects.filter(user=old_buyer).update(user=new_buyer)
    CreditCardToken.objects.filter(user=old_buyer).update(user=new_buyer)
