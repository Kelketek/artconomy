from decimal import Decimal, InvalidOperation
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum, Q, IntegerField, Case, When, F
from django.db.transaction import atomic
from django.utils import timezone
from django.utils.datetime_safe import date
from moneyed import Money

from apps.lib.models import Subscription, COMMISSIONS_OPEN, Event, DISPUTE, SALE_UPDATE
from apps.lib.utils import notify, recall_notification
from apps.profiles.models import User


def escrow_balance(user):
    from apps.sales.models import PaymentRecord
    try:
        debit = Decimal(
            str(user.credits.filter(
                status=PaymentRecord.SUCCESS,
                source=PaymentRecord.ESCROW
            ).aggregate(Sum('amount'))['amount__sum'])
        )
    except InvalidOperation:
        debit = Decimal('0.00')
    try:
        credit = Decimal(
            str(user.escrow_holdings.filter(
                status=PaymentRecord.SUCCESS).exclude(
                type__in=[
                    PaymentRecord.DISBURSEMENT_SENT,
                    PaymentRecord.DISBURSEMENT_RETURNED,
                ]
            ).aggregate(Sum('amount'))['amount__sum']))
    except InvalidOperation:
        credit = Decimal('0.00')

    return credit - debit


def available_balance(user):
    from apps.sales.models import PaymentRecord
    try:
        debit = Decimal(
            str(user.debits.filter(
                status=PaymentRecord.SUCCESS,
                source=PaymentRecord.ACCOUNT,
                # In the case of disbursement failed, we use success by default since it's a record from Dwolla, not
                # us.
                type__in=[PaymentRecord.DISBURSEMENT_SENT, PaymentRecord.TRANSFER, PaymentRecord.DISBURSEMENT_RETURNED],
            ).aggregate(Sum('amount'))['amount__sum'])
        )
    except InvalidOperation:
        debit = Decimal('0.00')
    try:
        credit = Decimal(
            str(
                user.credits.filter(
                    status=PaymentRecord.SUCCESS,
                    finalized=True
                ).aggregate(Sum('amount'))['amount__sum'])
        )
    except InvalidOperation:
        credit = Decimal('0.00')

    return credit - debit


def pending_balance(user):
    from apps.sales.models import PaymentRecord
    try:
        return Decimal(
            str(
                user.credits.filter(
                    status=PaymentRecord.SUCCESS,
                    finalized=False
                ).aggregate(Sum('amount'))['amount__sum'])
        )
    except InvalidOperation:
        return Decimal('0.00')


def translate_authnet_error(err):
    response = str(err)
    if hasattr(err, 'full_response'):
        # API is inconsistent in how it returns error info.
        if 'response_reason_text' in err.full_response:
            response = err.full_response['response_reason_text']
        if 'response_text' in err.full_response:
            response = err.full_response['response_text']
        if 'response_reason_code' in err.full_response:
            response = RESPONSE_TRANSLATORS.get(err.full_response['response_reason_code'], response)
        if 'response_code' in err.full_response:
            response = RESPONSE_TRANSLATORS.get(err.full_response['response_code'], response)
    return response


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
    exclude = Q(hidden=True)
    q = Q(name__istartswith=query) | Q(tags__name__iexact=query)
    if requester.is_authenticated:
        qs = Product.objects.filter(q).exclude(exclude & ~Q(user=requester)).exclude(active=False)
        qs = qs.exclude(Q(task_weight__gt=F('user__max_load')-F('user__load')) & ~Q(user=requester))
        qs = qs.filter(Q(max_parallel=0) | Q(parallel__lt=F('max_parallel')) | Q(user=requester))
        if not requester.is_staff:
            qs = qs.exclude(user__blocking=requester)
    else:
        qs = Product.objects.filter(q).exclude(exclude)
        qs = qs.exclude(Q(task_weight__gt=F('user__max_load')-F('user__load')))
        qs = qs.filter(Q(max_parallel=0) | Q(parallel__lt=F('max_parallel')))
    qs = qs.exclude(user__commissions_closed=True).exclude(user__commissions_disabled=True)
    if ordering:
        return product_ordering(qs, query)
    return qs


RESPONSE_TRANSLATORS = {
    '54': 'This transaction cannot be refunded. It may not yet have posted. '
          'Please try again tomorrow, and contact support if it still fails.',
    'E00027': "The zip or address we have on file for your card is either incorrect or has changed. Please remove the "
          "card and add it again with updated information.",
    'E00040': "Something is wrong in our records with the card you've added. Please remove the card and re-add it."
}


def service_price(user, service):
    price = Money(getattr(settings, service.upper() + '_PRICE'), 'USD')
    if service == 'landscape':
        if user.portrait_paid_through and user.portrait_paid_through >= date.today():
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


def available_products_by_load(seller, load=None):
    from apps.sales.models import Product
    if load is None:
        load = seller.load
    return Product.objects.filter(user=seller, active=True, hidden=False).exclude(
        task_weight__gt=seller.max_load - load
    ).exclude(Q(parallel__gte=F('max_parallel')) & ~Q(max_parallel=0))


def available_products_from_user(seller):
    from apps.sales.models import Product
    if seller.commissions_closed or seller.commissions_disabled:
        return Product.objects.none()
    return available_products_by_load(seller)


# Primitive recursion check lock.
UPDATING = {}


def update_availability(seller, load, current_closed_status):
    from apps.sales.models import Order
    global UPDATING
    if seller in UPDATING:
        return
    UPDATING[seller] = True
    try:
        products = available_products_by_load(seller, load)
        if seller.commissions_closed:
            seller.commissions_disabled = True
        elif not products.exists():
            seller.commissions_disabled = True
        elif load >= seller.max_load:
            seller.commissions_disabled = True
        elif not seller.sales.filter(status=Order.NEW).exists():
            seller.commissions_disabled = False
        seller.load = load
        seller.save()
        if current_closed_status and not seller.commissions_disabled:
            previous = Event.objects.filter(
                type=COMMISSIONS_OPEN, content_type=ContentType.objects.get_for_model(User), object_id=seller.id,
                date__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            )
            notify(
                COMMISSIONS_OPEN, seller, unique=True, mark_unread=not previous.exists(), silent_broadcast=previous.exists()
            )
        elif seller.commissions_disabled:
            recall_notification(COMMISSIONS_OPEN, seller)
    finally:
        del UPDATING[seller]


def finalize_order(order, user=None):
    from apps.sales.models import PaymentRecord
    with atomic():
        if order.status == order.DISPUTED and user == order.buyer:
            # User is rescinding dispute. d
            recall_notification(DISPUTE, order)
            # We'll pretend this never happened.
            order.disputed_on = None
        order.status = order.COMPLETED
        order.save()
        notify(SALE_UPDATE, order, unique=True, mark_unread=True)
        new_tx = PaymentRecord(
            payer=None,
            amount=order.price + order.adjustment,
            payee=order.seller,
            source=PaymentRecord.ESCROW,
            txn_id=str(uuid4()),
            target=order,
            type=PaymentRecord.TRANSFER,
            status=PaymentRecord.SUCCESS,
            response_code='OdrFnl',
            response_message='Order finalized.'
        )
        old_transaction = PaymentRecord.objects.get(
            object_id=order.id, content_type=ContentType.objects.get_for_model(order), payer=order.buyer,
            type=PaymentRecord.SALE
        )
        if old_transaction.created_on.date() > (timezone.now().date() - relativedelta(days=2)):
            new_tx.finalize_on = old_transaction.created_on.date() + relativedelta(days=2)
            new_tx.finalized = False
        new_tx.save()
        old_transaction.finalized = True
        old_transaction.save()
        PaymentRecord.objects.create(
            payer=order.seller,
            amount=(
                    ((order.price + order.adjustment) * order.seller.percentage_fee * Decimal('.01'))
                    + Money(order.seller.static_fee, 'USD')
            ),
            payee=None,
            source=PaymentRecord.ACCOUNT,
            txn_id=str(uuid4()),
            target=order,
            type=PaymentRecord.TRANSFER,
            status=PaymentRecord.SUCCESS,
            response_code='OdrFee',
            response_message='Artconomy Service Fee'
        )
