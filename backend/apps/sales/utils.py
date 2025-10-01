"""
The functions in this file are meant to mirror the functions in
frontend/lib/lineItemFunctions. There's not a good way to ensure that they're both
updated at the same time, but they should, hopefully, be easy enough to keep in sync.

If enough code has to be repeated between the two bases it may be worth looking into a
transpiler.
"""

import json
import logging
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    TypedDict,
    Union,
)
from urllib.parse import quote

from pytz import UTC

from apps.lib.models import (
    Comment,
    Event,
    Notification,
    Subscription,
    ref_for_instance,
)
from apps.lib.constants import (
    COMMENT,
    COMMISSIONS_OPEN,
    DISPUTE,
    REFUND,
    ORDER_UPDATE,
    SALE_UPDATE,
    REVISION_UPLOADED,
    REFERRAL_LANDSCAPE_CREDIT,
    REVISION_APPROVED,
)
from apps.lib.signals import broadcast_update
from apps.lib.tasks import check_asset_associations
from apps.lib.utils import (
    multi_filter,
    notify,
    recall_notification,
    clear_comments_by_content_obj_ref,
    clear_comments,
)
from apps.profiles.models import User
from apps.profiles.permissions import staff_power
from apps.profiles.tasks import create_or_update_stripe_user
from apps.sales.constants import (
    ADD_ON,
    CANCELLED,
    CARD,
    CARD_TRANSACTION_FEES,
    CASH_DEPOSIT,
    COMPLETED,
    CONCURRENCY_STATUSES,
    DELIVERABLE_TRACKING,
    DISPUTED,
    DRAFT,
    ESCROW,
    ESCROW_REFUND,
    ESCROW_RELEASE,
    FAILURE,
    HOLDINGS,
    IN_PROGRESS,
    LIMBO,
    MISSED,
    MONEY_HOLE,
    MONEY_HOLE_STAGE,
    NEW,
    OPEN,
    PAID,
    PAYMENT_PENDING,
    PREMIUM_SUBSCRIPTION,
    QUEUED,
    REFUNDED,
    RESERVE,
    REVIEW,
    SHIELD_FEE,
    STRIPE,
    SUBSCRIPTION,
    SUBSCRIPTION_DUES,
    SUCCESS,
    TABLE_HANDLING,
    TAX,
    TERM,
    THIRD_PARTY_FEE,
    TIP,
    TIP_SEND,
    TIPPING,
    VOID,
    WAITING,
    LINE_ITEM_TYPES_TABLE,
    FUND,
    PAYMENT,
    VENDOR,
    WORK_IN_PROGRESS_STATUSES,
    PRIORITY_MAP,
    CASCADE_UNDER_MAP,
)
from apps.sales.line_item_funcs import (
    down_context,
    get_totals,
    half_up_context,
    deliverable_lines,
    tip_lines,
)
from apps.sales.paypal import clear_existing_invoice, paypal_api
from apps.sales.stripe import (
    refund_payment_intent,
    remote_ids_from_charge,
    stripe,
    cancel_payment_intent,
)
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError, transaction
from django.db.models import Case, F, IntegerField, Model, Q, Sum, When
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import date, datetime
from django.utils.module_loading import import_string
from moneyed import Money
from rest_framework.exceptions import ValidationError
from short_stuff import gen_shortcode
from stripe.error import InvalidRequestError

if TYPE_CHECKING:  # pragma: no cover
    from apps.sales.models import (
        Product,
        Deliverable,
        Invoice,
        LineItem,
        LineItemSim,
        Order,
        ServicePlan,
        TransactionRecord,
    )

    TransactionSpecKey = (Union[User, None], int, int)
    TransactionSpecMap = Dict[TransactionSpecKey, Money]


logger = logging.getLogger(__name__)


class ALL:
    """
    Uniquely defined symbol for use as a constant to indicate 'All users'.
    This is to allow for account queries intended to give summary information,
    like 'what is the total amount in Escrow right now?'
    """

    def __init__(self):  # pragma: no cover
        raise RuntimeError("This class used as unique enum, not to be instantiated.")


AVAILABLE = 0
POSTED_ONLY = 1
PENDING = 2


def account_balance(
    user: Union[User, None, Type[ALL]],
    account_type: int,
    balance_type: int = AVAILABLE,
    additional_filters: Optional[list[Q]] = None,
) -> Decimal:
    additional_filters = additional_filters or []
    from apps.sales.models import TransactionRecord

    if balance_type == PENDING:
        statuses = [PENDING]
    elif balance_type == POSTED_ONLY:
        statuses = [SUCCESS]
    elif balance_type == AVAILABLE:
        statuses = [SUCCESS, PENDING]
    else:
        raise TypeError(f"Invalid balance type: {balance_type}")
    kwargs = {
        "status__in": statuses,
        "source": account_type,
    }
    if user is not ALL:
        kwargs["payer"] = user
    try:
        debit = Decimal(
            str(
                multi_filter(
                    TransactionRecord.objects.filter(
                        **kwargs,
                    ),
                    additional_filters,
                ).aggregate(Sum("amount"))["amount__sum"]
            )
        )
    except InvalidOperation:
        debit = Decimal("0.00")
    kwargs = {
        "status__in": statuses,
        "destination": account_type,
    }
    if user is not ALL:
        kwargs["payee"] = user
    try:
        credit = Decimal(
            str(
                multi_filter(
                    TransactionRecord.objects.filter(
                        **kwargs,
                    ),
                    additional_filters,
                ).aggregate(Sum("amount"))["amount__sum"]
            )
        )
    except InvalidOperation:
        credit = Decimal("0.00")

    return Decimal(credit - debit)


def product_ordering(qs, query=""):
    return (
        qs.annotate(
            matches=Case(
                When(name__iexact=query, then=0), default=1, output_field=IntegerField()
            ),
            tag_matches=Case(
                When(tags__name__iexact=query, then=0),
                default=1,
                output_field=IntegerField(),
            ),
            # How can we make it distinct on id while making matches and tag_matches
            # priority ordering?
        )
        .order_by("id", "matches", "tag_matches")
        .distinct("id")
    )


def available_products(requester, query="", ordering=True):
    from apps.sales.models import Product

    if query:
        q = Q(name__istartswith=query) | Q(tags__name=query.lower())
        qs = Product.objects.filter(available=True).filter(q)
    else:
        qs = Product.objects.filter(available=True)
    qs = qs.exclude(active=False)
    qs = qs.exclude(table_product=True)
    # TODO: Recheck this for basic/free plan when we have orders that have been placed
    # but they haven't upgraded.
    qs = qs.exclude(
        (
            Q(user__service_plan_paid_through__lte=timezone.now())
            | ~Q(user__service_plan__waitlisting=True)
        ),
        wait_list=True,
    )
    if requester.is_authenticated:
        if not (
            staff_power(requester, "view_as")
            or staff_power(requester, "moderate_content")
        ):
            qs = qs.exclude(user__blocking=requester)
            qs = qs.exclude(table_product=True)
        qs = qs.exclude(user__blocked_by=requester)
    if ordering:
        return product_ordering(qs, query)
    return qs


def term_charge(deliverable: "Deliverable"):
    """
    Add a deliverable's charge to a user's term invoice if applicable.
    WARNING: Does not save the deliverable.
    """
    from apps.sales.models import LineItem

    plan = deliverable.order.seller.service_plan
    if plan.per_deliverable_price and not deliverable.escrow_enabled:
        term_invoice = get_term_invoice(deliverable.order.seller)
        if not term_invoice.lines_for(deliverable).exists():
            line = LineItem.objects.create(
                invoice=term_invoice,
                amount=plan.per_deliverable_price,
                destination_account=FUND,
                category=SUBSCRIPTION_DUES,
                type=DELIVERABLE_TRACKING,
                priority=PRIORITY_MAP[DELIVERABLE_TRACKING],
                cascade_under=CASCADE_UNDER_MAP[DELIVERABLE_TRACKING],
            )
            line.targets.add(ref_for_instance(deliverable))
    deliverable.term_billed = True


def set_service_plan(user, service_plan, next_plan=None, target_date=None):
    from apps.sales.models import Deliverable

    fields = ["service_plan", "service_plan_paid_through"]
    changed = user.service_plan != service_plan
    user.service_plan = service_plan
    if next_plan:
        user.next_service_plan = next_plan
        fields.append("next_service_plan")
    if target_date:
        user.service_plan_paid_through = target_date
    user.save(
        update_fields=fields,
    )
    if changed:
        if not service_plan.max_simultaneous_orders:
            for deliverable in Deliverable.objects.filter(
                status=LIMBO, order__seller=user
            ):
                term_charge(deliverable)
                deliverable.status = NEW
                deliverable.auto_close_on = timezone.now() + relativedelta(
                    days=settings.AUTO_CANCEL_DAYS
                )
                deliverable.save()
        else:
            maximum = service_plan.max_simultaneous_orders
            current_count = Deliverable.objects.filter(
                status__in=CONCURRENCY_STATUSES
            ).count()
            if current_count < maximum:
                to_reveal = Deliverable.objects.filter(
                    status=LIMBO, order__seller=user
                )[: maximum - current_count]
                for deliverable in to_reveal:
                    term_charge(deliverable)
                    deliverable.status = NEW
                    deliverable.auto_close_on = timezone.now() + relativedelta(
                        days=settings.AUTO_CANCEL_DAYS
                    )
                    deliverable.save()

        update_downstream_pricing(user)


def available_products_by_load(seller_profile, load=None):
    from apps.sales.models import Product

    if load is None:
        load = seller_profile.load
    if seller_profile.user.service_plan.waitlisting:
        exclude_extra = Q(wait_list=False)
    else:
        exclude_extra = Q()
    return (
        Product.objects.filter(
            user_id=seller_profile.user_id, active=True, hidden=False
        )
        .exclude(
            Q(task_weight__gt=seller_profile.max_load - load) & exclude_extra,
        )
        .exclude(Q(parallel__gte=F("max_parallel")) & ~Q(max_parallel=0))
    )


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
        failure_modes = [
            seller.delinquent,
            not seller.is_active,
            seller_profile.commissions_closed,
            not products.exists(),
        ]
        if any(failure_modes):
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
        if seller.service_plan.waitlisting:
            extra_exclude = Q(wait_list=True)
        else:
            extra_exclude = Q()
        seller.products.filter(
            Q(hidden=True)
            | Q(active=False)
            | Q(inventory__count=0)
            | Q(task_weight__gt=max_size)
        ).exclude(extra_exclude).update(
            available=False,
            edited_on=timezone.now(),
        )
        if current_closed_status and not seller_profile.commissions_disabled:
            previous = Event.objects.filter(
                type=COMMISSIONS_OPEN,
                content_type=ContentType.objects.get_for_model(User),
                object_id=seller.id,
                date__gte=timezone.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
            )
            notify(
                COMMISSIONS_OPEN,
                seller,
                unique=True,
                mark_unread=not previous.exists(),
                silent_broadcast=previous.exists(),
            )
        if seller_profile.commissions_disabled or seller_profile.commissions_closed:
            seller.products.all().update(available=False, edited_on=timezone.now())
            recall_notification(COMMISSIONS_OPEN, seller)
    finally:
        del UPDATING[seller]
        broadcast_update(seller_profile)


def finalize_table_fees(deliverable: "Deliverable"):
    from apps.sales.models import TransactionRecord, ref_for_instance

    deliverable_ref = ref_for_instance(deliverable)
    invoice_ref = ref_for_instance(deliverable.invoice)
    record = TransactionRecord.objects.get(
        payee=None,
        destination=RESERVE,
        status=SUCCESS,
        targets=invoice_ref,
    )
    service_fee = TransactionRecord.objects.create(
        source=RESERVE,
        destination=FUND,
        amount=record.amount,
        payer=None,
        payee=None,
        status=SUCCESS,
        category=TABLE_HANDLING,
        remote_ids=record.remote_ids,
        auth_code=record.auth_code,
    )
    service_fee.targets.add(invoice_ref, deliverable_ref)
    tax_record = TransactionRecord.objects.get(
        payee=None,
        destination=MONEY_HOLE_STAGE,
        status=SUCCESS,
        targets=invoice_ref,
    )
    tax_burned = TransactionRecord.objects.create(
        source=MONEY_HOLE_STAGE,
        destination=MONEY_HOLE,
        amount=tax_record.amount,
        payer=None,
        payee=None,
        status=SUCCESS,
        category=TAX,
        remote_ids=tax_record.remote_ids,
        auth_code=tax_record.auth_code,
    )
    tax_burned.targets.add(invoice_ref, deliverable_ref)


def initialize_tip_invoice(deliverable):
    from apps.sales.models import Invoice, LineItem

    if not deliverable.order.seller.service_plan.tipping:
        return
    expires_on = deliverable.finalized_on + relativedelta(days=settings.TIP_DAYS)
    if expires_on <= timezone.now():
        return None
    if deliverable.tip_invoice:
        invoice = deliverable.tip_invoice
        if invoice.status != VOID:
            # Don't make a new invoice, just return the old one.
            return invoice
        invoice.delete()

    invoice = Invoice.objects.create(
        type=TIPPING,
        bill_to=deliverable.order.buyer,
        issued_by=deliverable.order.seller,
        expires_on=expires_on,
        payout_available=True,
    )
    lines = tip_lines(international=deliverable.international)
    for line in lines:
        invoice.line_items.update_or_create(
            defaults={
                "percentage": line["percentage"],
                "amount": Money(line["amount"], settings.DEFAULT_CURRENCY),
                "priority": line["priority"],
                "description": line["description"],
                "back_into_percentage": line["back_into_percentage"],
                "cascade_amount": False,
                "cascade_percentage": False,
                "cascade_under": 201,
            },
            type=line["kind"],
            category=line["category"],
            destination_account=line["destination_account"],
            destination_user_id=line["destination_user_id"],
            invoice=invoice,
        )
    amount = max(deliverable.invoice.total() * Decimal(".10"), settings.MINIMUM_TIP)
    line = LineItem.objects.create(
        type=TIP,
        category=TIP_SEND,
        percentage=0,
        amount=amount,
        cascade_amount=False,
        cascade_percentage=False,
        invoice=invoice,
        destination_user=deliverable.order.seller,
        destination_account=HOLDINGS,
        priority=PRIORITY_MAP[TIP],
        cascade_under=CASCADE_UNDER_MAP[TIP],
    )
    line.targets.add(ref_for_instance(deliverable))
    deliverable.tip_invoice = invoice
    deliverable.save()
    return invoice


def finalize_deliverable(deliverable, user=None):
    from apps.sales.models import TransactionRecord, ref_for_instance
    from apps.sales.tasks import withdraw_all

    with atomic():
        if deliverable.status == DISPUTED and user == deliverable.order.buyer:
            # User is rescinding dispute.
            recall_notification(DISPUTE, deliverable)
            # We'll pretend this never happened.
            deliverable.disputed_on = None
        deliverable.status = COMPLETED
        deliverable.finalized_on = timezone.now()
        deliverable.redact_available_on = timezone.now().date() + relativedelta(
            days=settings.REDACTION_ALLOWED_WINDOW,
        )
        deliverable.save()
        deliverable.invoice.payout_available = True
        deliverable.invoice.save(update_fields=["payout_available"])
        records = TransactionRecord.objects.filter(
            payee=deliverable.order.seller,
            destination=ESCROW,
            status=SUCCESS,
            targets__object_id=deliverable.id,
            targets__content_type=ContentType.objects.get_for_model(deliverable),
        )
        # There will always be at least one.
        record = records[0]
        to_holdings = TransactionRecord.objects.create(
            payer=deliverable.order.seller,
            payee=deliverable.order.seller,
            amount=sum((item.amount for item in records)),
            source=ESCROW,
            destination=HOLDINGS,
            category=ESCROW_RELEASE,
            status=SUCCESS,
            remote_ids=record.remote_ids,
            auth_code=record.auth_code,
        )
        to_holdings.targets.add(
            ref_for_instance(deliverable), ref_for_instance(deliverable.invoice)
        )
        if deliverable.table_order:
            finalize_table_fees(deliverable)
        initialize_tip_invoice(deliverable)
        notify(SALE_UPDATE, deliverable, unique=True, mark_unread=True)
    # Don't worry about whether it's time to withdraw or not. This will make sure that
    # an attempt is made in case there's money to withdraw that hasn't been taken yet,
    # and another process will try again if it settles later. It will also ignore if
    # the seller has auto_withdraw disabled.
    withdraw_all.delay(deliverable.order.seller.id)


def claim_order_by_token(order_claim, user):
    from apps.sales.models import Order

    if not order_claim:
        return
    order = Order.objects.filter(claim_token=order_claim).first()
    if not order:
        logger.warning(
            "User %s attempted to claim non-existent order token, %s", user, order_claim
        )
        return
    if order.seller == user:
        logger.warning(
            "Seller %s attempted to claim their own order token, %s", user, order_claim
        )
        return
    if order.buyer == user and user.is_registered:
        # This should never happen, but just in case...
        order.claim_token = None
        order.save(update_fields=["claim_token"])
    transfer_order(order, order.buyer, user)


def transfer_order(order, old_buyer, new_buyer, skip_notification=False, force=False):
    """
    Sets the buyer from one user (or None) to a new buyer.

    The force flag exists in case this needs to be done within a script
    to fix something.
    """
    from apps.sales.models import (
        ORDER_UPDATE,
        CreditCardToken,
        Revision,
        Reference,
        buyer_subscriptions,
    )

    if (
        old_buyer and old_buyer.is_registered and new_buyer.is_registered
    ) and not force:
        raise AssertionError("Tried to claim an order, but it was already claimed!")
    order.buyer = new_buyer
    for deliverable in order.deliverables.all():
        if deliverable.invoice:
            deliverable.invoice.bill_to = new_buyer
            deliverable.invoice.save()
    order.customer_email = ""
    order.claim_token = None
    order.save(update_fields=["buyer", "customer_email", "claim_token"])
    for deliverable in order.deliverables.all():
        Subscription.objects.bulk_create(
            buyer_subscriptions(deliverable), ignore_conflicts=True
        )
        if not (skip_notification or (old_buyer == new_buyer)):
            notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        update_order_payments(deliverable)
    revision_type = ContentType.objects.get_for_model(Revision)
    reference_type = ContentType.objects.get_for_model(Reference)
    Subscription.objects.bulk_create(
        [
            Subscription(
                subscriber=new_buyer,
                object_id=revision_id,
                content_type=revision_type,
                type=COMMENT,
            )
            for revision_id in Revision.objects.filter(
                deliverable__order=order
            ).values_list("id", flat=True)
        ],
        ignore_conflicts=True,
    )
    Subscription.objects.bulk_create(
        [
            Subscription(
                subscriber=new_buyer,
                object_id=reference_id,
                content_type=reference_type,
                type=COMMENT,
            )
            for reference_id in Reference.objects.filter(
                deliverables__order=order
            ).values_list("id", flat=True)
        ],
        ignore_conflicts=True,
    )
    if not old_buyer:
        return
    if old_buyer == new_buyer:
        return
    if old_buyer.is_registered:
        # Can't delete the below safely.
        return
    Subscription.objects.filter(subscriber=old_buyer).delete()
    Notification.objects.filter(user=old_buyer).update(user=new_buyer)
    Comment.objects.filter(user=old_buyer).update(user=new_buyer)
    CreditCardToken.objects.filter(user=old_buyer).update(user=new_buyer)


def cancel_deliverable(deliverable, requested_by, skip_remote=False):
    """
    Marks a deliverable as cancelled, sending relevant notifications.
    """
    if deliverable.status == LIMBO:
        deliverable.status = MISSED
    else:
        deliverable.status = CANCELLED
    if deliverable.invoice.paypal_token and not skip_remote:
        with paypal_api(deliverable.order.seller) as paypal:
            clear_existing_invoice(paypal, deliverable.invoice)
    deliverable.cancelled_on = timezone.now()
    deliverable.redact_available_on = timezone.now().date()
    deliverable.save()
    deliverable.invoice.status = VOID
    deliverable.invoice.save()
    if requested_by != deliverable.order.seller:
        notify(SALE_UPDATE, deliverable, unique=True, mark_unread=True)
    if requested_by != deliverable.order.buyer:
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)


@down_context
def lines_to_transaction_specs(lines: Iterable["LineItem"]) -> "TransactionSpecMap":
    total, __, subtotals = get_totals(lines)
    transaction_specs = defaultdict(lambda: Money("0.00", "USD"))
    for line_item, subtotal in subtotals.items():
        transaction_specs[
            line_item.destination_user,
            line_item.destination_account,
            line_item.category,
        ] += subtotal
    return transaction_specs


def fetch_prefixed(prefix: str, values: Iterable[str]) -> str:
    """
    Stripe transaction IDs all have prefixes like 'py_', or 'ch_'.
    Given a list of transaction ID strings, find the first with
    a relevant prefix and return it. Raise ValueError if none exists.
    """
    for entry in values:
        if entry.startswith(prefix):
            return entry
    raise ValueError(f"Could not find an entry starting with {prefix} in {values}")


def verify_total(deliverable: "Deliverable", field_name="amount"):
    """
    Verifies the total amount on a deliverable is within permitted ranges.

     We can't have negative values, or a value which costs more to pay for in fees
     than would be paid out to anyone.
    """
    total = deliverable.invoice.total()
    if total < Money(0, "USD"):
        raise ValidationError({field_name: ["Total cannot end up less than $0."]})
    if total == Money(0, "USD"):
        return
    if deliverable.escrow_enabled and total < settings.MINIMUM_PRICE:
        raise ValidationError(
            {
                field_name: [
                    f"Total cannot end up less than ${settings.MINIMUM_PRICE.amount}."
                ]
            }
        )


def refund_transaction_from(
    record: "TransactionRecord", category: int, amount: Optional[Money] = None
):
    """
    Creates a reversed transaction with an optionally overwritten amount.

    TODO: Don't we already have a transaction reversing function? This may be partly
    redundant.
    """
    from apps.sales.models import TransactionRecord

    if amount is None:
        amount = record.amount
    return TransactionRecord.objects.create(
        source=record.destination,
        destination=record.source,
        status=FAILURE,
        category=category,
        payer=record.payee,
        payee=record.payer,
        card=record.card,
        amount=amount,
        remote_ids=record.remote_ids,
        response_message="Failed when contacting payment processor.",
    )


def issue_refund(
    fund_transaction: "TransactionRecord",
    transaction_set: Iterable["TransactionRecord"],
    category: int,
    processor: str,
) -> List["TransactionRecord"]:
    """
    Performs all accounting and API calls to refund a set of transactions.
    """

    assert fund_transaction.destination == FUND, (
        "fund_transaction does not have destination as FUND!"
    )
    last_four = fund_transaction.card and fund_transaction.card.last_four
    transactions = [*transaction_set]
    remote_ids = [*fund_transaction.remote_ids]
    if not fund_transaction.source == CASH_DEPOSIT:
        assert remote_ids, "Could not find a remote transaction ID to refund."
        assert (processor == STRIPE) or last_four, (
            "Could not determine the last four digits of the relevant card."
        )
    refund_transactions = []
    for record in transactions:
        new_record = refund_transaction_from(record, category)
        new_record.targets.set(record.targets.all())
        refund_transactions.append(new_record)
    amount = sum(record.amount for record in transactions) or Money("0.00", "USD")
    payment_refund = refund_transaction_from(fund_transaction, category, amount=amount)
    payment_refund.targets.set(fund_transaction.targets.all())
    refund_transactions.append(payment_refund)
    if fund_transaction.source == CARD:
        try:
            auth_code = "******"
            try:
                intent_token = fetch_prefixed("pi_", remote_ids)
            except ValueError:  # pragma: no cover
                raise ValueError("Invalid Stripe payment ID. Please contact support!")
            with stripe as stripe_api:
                # Note: We will assume success here. If there is a refund failure we'll
                # have to dive into it manually anyway and will find it during the
                # accounting rounds.
                # TODO: Fix this.
                remote_id = refund_payment_intent(
                    amount=amount, api=stripe_api, intent_token=intent_token
                )["id"]
                remote_ids.append(remote_id)
            for record in refund_transactions:
                record.status = SUCCESS
                if record.destination == CARD:
                    record.remote_ids = remote_ids
                    record.auth_code = auth_code
                record.response_message = ""
        except Exception as err:
            for record in refund_transactions:
                record.response_message = str(err)
        finally:
            for record in refund_transactions:
                record.save()
    elif fund_transaction.source == CASH_DEPOSIT:
        for record in refund_transactions:
            record.status = SUCCESS
            record.response_message = ""
            record.save()
    return refund_transactions


def ensure_buyer(order: "Order"):
    """
    Makes sure there's a buyer attached to the order. Creates one if none has been set.
    """
    from apps.profiles.utils import create_guest_user
    from apps.sales.models import buyer_subscriptions

    if order.buyer:
        return
    assert order.customer_email, "No customer, and customer email not set on order."
    # Create the buyer now as a guest.
    user = create_guest_user(order.customer_email)
    order.buyer = user
    order.save()
    for deliverable in order.deliverables.all():
        Subscription.objects.bulk_create(
            buyer_subscriptions(deliverable), ignore_conflicts=True
        )
        if deliverable.invoice:
            deliverable.invoice.bill_to = user
            deliverable.invoice.save()


def update_order_payments(deliverable: "Deliverable"):
    """
    Find existing payment actions for an order, and sets the payer to the current buyer.
    This is useful when an order was once created by a guest but later chowned over to a
    registered user.
    """
    from apps.sales.models import TransactionRecord

    TransactionRecord.objects.filter(
        source__in=[CARD, CASH_DEPOSIT],
        targets__object_id=deliverable.id,
        targets__content_type=ContentType.objects.get_for_model(deliverable),
    ).update(payer=deliverable.order.buyer)


def get_claim_token(order: "Order") -> Union[str, None]:
    """
    Determines whether this order should have a claim token, and, if so, generates one
    if it does not exist, after which it returns whatever claim token is available or
    None.
    """
    if order.buyer and order.buyer.guest:
        if not order.claim_token:
            order.claim_token = gen_shortcode()
            order.save(update_fields=["claim_token"])
    return order.claim_token


def default_deliverable(order: "Order") -> Union["Deliverable", None]:
    try:
        return order.deliverables.get()
    except MultipleObjectsReturned:
        return None


def get_view_name(deliverable: "Deliverable") -> str:
    """
    Determines the most relevant view at any given time for a deliverable. For instance,
    if the deliverable is awaiting payment, the payment view is the most relevant. Note
    that the string this returns is intended to be combined with a prefix, so if this
    returns 'DeliverablePayment', then the view on the frontend might be
    'OrderDeliverablePayment', 'SaleDeliverablePayment', or 'CaseDeliverablePayment'.
    """
    if deliverable.status in [IN_PROGRESS, QUEUED, REVIEW]:
        return "DeliverableRevisions"
    if deliverable.status == PAYMENT_PENDING:
        return "DeliverablePayment"
    return "DeliverableOverview"


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
    *,
    order: "Order",
    user: User,
    logged_in: bool,
    deliverable: Union["Deliverable", None] = None,
    view_name: Union[str, None] = None,
    extra_params: Union[dict, None] = None,
) -> OrderContext:
    context = {
        "view_name": view_name or "",
        "order_id": order.id,
        "extra_params": extra_params or {},
    }
    if order.seller == user:
        context["base_name"] = "Sale"
    elif deliverable and deliverable.arbitrator == user:
        context["base_name"] = "Case"
    else:
        context["base_name"] = "Order"
    context["username"] = user.username
    deliverable = deliverable or default_deliverable(order)
    context["claim"] = user.guest and not logged_in
    context["claim_token"] = get_claim_token(order)
    context["deliverable_id"] = deliverable and deliverable.id
    if deliverable and not view_name:
        context["view_name"] = get_view_name(deliverable)
    elif view_name:
        context["view_name"] = view_name
    return context


def order_context_to_link(context: OrderContext):
    goal_path = {
        "name": context["base_name"] + context["view_name"],
        "params": {
            "username": context["username"],
            "orderId": context["order_id"],
            "deliverableId": context["deliverable_id"],
            **context["extra_params"],
        },
    }
    if context["claim"]:
        goal_path["params"]["username"] = "_"
        return {
            "name": "ClaimOrder",
            "params": {
                "orderId": context["order_id"],
                "claimToken": context["claim_token"],
                "deliverableId": context["deliverable_id"],
                "next": quote(json.dumps(goal_path), safe=""),
            },
        }
    return goal_path


@atomic
def destroy_deliverable(deliverable: "Deliverable"):
    if deliverable.status not in [CANCELLED, MISSED]:
        raise IntegrityError("Can only destroy cancelled orders!")
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
    service: "ServicePlan"
    # Should never exist unless through a webhook.
    stripe_event: dict


TransactionInitiator = Callable[
    [PaymentAttempt, Money, User, dict], List["TransactionRecord"]
]
TransactionMutator = Callable[
    [List["TransactionRecord"], PaymentAttempt, User, dict], None
]


def dummy_mutator(
    transactions: List["TransactionRecord"],
    attempt: PaymentAttempt,
    user: User,
    context: dict,
):
    """No-op mutator function for use in perform_charge's hooks."""
    pass


def perform_charge(
    *,
    attempt: PaymentAttempt,
    amount: Money,
    user: User,
    requesting_user: User,
    post_success: TransactionMutator = dummy_mutator,
    post_save: TransactionMutator = dummy_mutator,
    context: dict,
) -> Tuple[bool, List["TransactionRecord"], str]:
    """
    Convenience function for web-facing charges. Takes a payment data dictionary and
    determines which kind of payment is being submitted from the client, then routes the
    payment according to permissions and payment type.
    """
    if attempt.get("cash", False) and (
        staff_power(requesting_user, "table_seller") or not amount
    ):
        return from_cash(
            attempt=attempt,
            amount=amount,
            user=user,
            post_save=post_save,
            post_success=post_success,
            context=context,
        )
    if attempt.get("remote_ids") and (
        staff_power(requesting_user, "table_seller") or attempt.get("stripe_event")
    ):
        return from_remote_id(
            attempt=attempt,
            amount=amount,
            user=user,
            remote_ids=attempt.get("remote_ids"),
            post_save=post_save,
            post_success=post_success,
            context=context,
        )
    else:  # pragma: no cover
        raise RuntimeError("Could not identify the right way to perform this charge.")


def from_cash(
    *,
    attempt: PaymentAttempt,
    amount: Money,
    user: User,
    post_success: TransactionMutator,
    post_save: TransactionMutator,
    context: dict,
):
    """
    Function for marking payment made via cash. This should only ever be invoked through
    permission checked staffchannels because we're essentially telling the system
    'trust me, this has been paid for' and to just move the transaction along.
    """
    transactions = invoice_initiate_transactions(attempt, amount, user, context)
    for record in transactions:
        record.status = SUCCESS
    post_success(transactions, attempt, user, context)
    for record in transactions:
        record.save()
    post_save(transactions, attempt, user, context)
    return True, transactions, ""


def from_remote_id(
    *,
    attempt: PaymentAttempt,
    amount: Money,
    user: User,
    remote_ids: List[str],
    post_success: TransactionMutator,
    post_save: TransactionMutator,
    context: dict,
) -> Tuple[bool, List["TransactionRecord"], str]:
    """
    Mark this as paid via remote transaction ID from the card processor.
    """
    # This may not work if charging via stripe terminal.
    # We'll be checking this elsewhere if the stripe event is provided.
    {"auth_amount": attempt["amount"]}
    # Bogus auth code so things don't break. Need to remove this eventually-- it's a
    # holdover from Authorize.net.
    auth_code = "******"
    stripe_event = attempt["stripe_event"]
    remote_ids = [*remote_ids]
    if stripe_event["balance_transaction"]:
        remote_ids.append(stripe_event["balance_transaction"])
    if stripe_event["status"] not in ["succeeded", "failed"]:
        error = (
            f"Unhandled charge status, {stripe_event['status']} for remote_ids "
            f"{remote_ids}"
        )
        return (
            False,
            annotate_error(
                transactions=[],
                # RuntimeError shouldn't be caught, ensuring this throws properly.
                error=error,
                attempt=attempt,
                user=user,
                post_save=post_save,
                context=context,
            ),
            error,
        )
    transactions = invoice_initiate_transactions(attempt, amount, user, context)
    if stripe_event["status"] == "failed":
        error = f"{stripe_event['failure_code']}: {stripe_event['failure_message']}"
        return (
            False,
            annotate_error(
                transactions=transactions,
                error=error,
                attempt=attempt,
                user=user,
                post_save=post_save,
                context=context,
            ),
            error,
        )
    # We don't support the 'pending' status because we don't record the transaction on
    # our side until we actually run the charge-- earlier code should filter it out.
    # Maybe we'll add it in the future, but it's not complexity we need right now.
    mark_successful(
        transactions=transactions,
        remote_ids=remote_ids,
        auth_code=auth_code,
        post_success=post_success,
        post_save=post_save,
        context=context,
        attempt=attempt,
        user=user,
    )
    return True, transactions, ""


def annotate_error(
    *,
    transactions: List["TransactionRecord"],
    error: str,
    attempt: PaymentAttempt,
    user: User,
    post_save: TransactionMutator,
    context: dict,
) -> List["TransactionRecord"]:
    """
    Annotates a set of transactions with an error and then returns the appropriate
    status code.
    """
    response_message = error
    for record in transactions:
        record.status = FAILURE
        record.response_message = response_message
        record.save()
    post_save(transactions, attempt, user, context)
    return transactions


def mark_successful(
    *,
    transactions: List["TransactionRecord"],
    remote_ids: List[str],
    auth_code: str,
    post_success: TransactionMutator,
    post_save: TransactionMutator,
    attempt: PaymentAttempt,
    user: User,
    context: dict,
):
    """
    Marks a set of transactions as successful.
    """
    for record in transactions:
        record.status = SUCCESS
        record.remote_ids.extend(remote_ids)
        record.remote_ids = list(set(record.remote_ids))
        record.auth_code = auth_code
        # We have a failure message that gets set here by default. Clear it.
        record.response_message = ""
    post_success(transactions, attempt, user, context)
    for record in transactions:
        record.save()
    post_save(transactions, attempt, user, context)


@half_up_context
def initialize_stripe_charge_fees(amount: Money, stripe_event: dict):
    """
    Return a set of initialized transactions that mark what fees we paid to stripe
    for a card charge.
    """
    from apps.sales.models import TransactionRecord

    base_percentage = Decimal("0")
    payment_details = stripe_event["payment_method_details"]
    card_details = payment_details.get("card", payment_details.get("card_present"))
    if card_details is None:
        raise ValidationError("No card information provided with transaction!")
    if card_details["country"] != settings.SOURCE_COUNTRY:
        base_percentage += settings.STRIPE_INTERNATIONAL_PERCENTAGE_ADDITION
    if "card_present" in stripe_event["payment_method_details"]:
        percentage = base_percentage + settings.STRIPE_CARD_PRESENT_PERCENTAGE
        fee = (amount * (percentage / 100)).round(2)
        fee += settings.STRIPE_CARD_PRESENT_STATIC
    else:
        percentage = base_percentage + settings.STRIPE_CHARGE_PERCENTAGE
        fee = (amount * (percentage / 100)).round(2)
        fee += settings.STRIPE_CHARGE_STATIC
    return [
        TransactionRecord(
            source=FUND,
            destination=CARD_TRANSACTION_FEES,
            category=THIRD_PARTY_FEE,
            amount=fee,
        )
    ]


def get_subscription_invoice(user: User) -> "Invoice":
    """
    This grabs an invoice for upgrading the user's service plan. This prevents us from
    having multiple such invoices for a user.
    """
    from apps.sales.models import Invoice

    return Invoice.objects.get_or_create(status=OPEN, bill_to=user, type=SUBSCRIPTION)[
        0
    ]


def get_term_invoice(user: User) -> "Invoice":
    """
    This grabs the term invoice for a user. A term invoice handles all the monthly
    billing-- things like tracking non-shielded transactions. This prevents us from
    having multiple such invoices for a user.
    """
    from apps.sales.models import Invoice

    invoice = Invoice.objects.update_or_create(
        status__in=[DRAFT, OPEN],
        bill_to=user,
        type=TERM,
        due_date=user.service_plan_paid_through,
        defaults={"status": DRAFT},
    )[0]
    return invoice


def add_service_plan_line(invoice: "Invoice", service_plan: "ServicePlan"):
    amount = service_plan.monthly_charge
    item, _created = invoice.line_items.update_or_create(
        defaults={
            "amount": amount,
            "category": SUBSCRIPTION_DUES,
            "priority": PRIORITY_MAP[PREMIUM_SUBSCRIPTION],
            "cascade_under": CASCADE_UNDER_MAP[PREMIUM_SUBSCRIPTION],
            "description": f"{service_plan.name} plan monthly dues",
        },
        destination_account=FUND,
        type=PREMIUM_SUBSCRIPTION,
        destination_user=None,
    )
    item.targets.set([ref_for_instance(service_plan)])


def subscription_invoice_for_service(user: User, service_plan: "ServicePlan"):
    invoice = get_subscription_invoice(user)
    add_service_plan_line(invoice, service_plan)
    return invoice


def get_intent_card_token(user: User, card_id: Optional[str]):
    from apps.sales.models import CreditCardToken

    if card_id:
        stripe_token = get_object_or_404(
            CreditCardToken, id=card_id, user=user
        ).stripe_token
        if not stripe_token:
            raise ValidationError({"card_id": "That card ID is not a stripe card."})
        return stripe_token
    if user.primary_card and user.primary_card.stripe_token:
        return user.primary_card.stripe_token
    return None


def default_pre_pay_callable(target: Model):
    """
    We'll determine what the default callable for this model is. For the moment, we're
    storing this value as a property on the model, but we may eventually want to create
    some sort of registry if we end up factoring this out.
    """
    return getattr(target, "pre_pay_hook", None)


def default_post_pay_callable(target: Model):
    """
    We'll determine what the default callable for this model is. For the moment, we're
    storing this value as a property on the model, but we may eventually want to create
    some sort of registry if we end up factoring this out.
    """
    return getattr(target, "post_pay_hook", None)


def pre_pay_hook(
    *, billable: Union["Invoice", "LineItem"], target: Model, context: dict
) -> dict:
    """
    Determine the appropriate preflight function call for a billable. These functions
    should always return a dictionary which will be merged into the context given to the
    post_pay hooks. Care should be taken to avoid clobbering where possible, as
    execution order is not guaranteed.
    """
    import_spec = context.get("__callable__", default_pre_pay_callable(target))
    if not import_spec:
        return {}
    to_call = import_string(import_spec)
    return to_call(billable=billable, target=target, context=context)


def post_pay_hook(
    *,
    billable: Union["Invoice", "LineItem"],
    target: Model,
    context: dict,
    records: List["TransactionRecord"],
) -> List["TransactionRecord"]:
    """
    Determine the appropriate function call for a billable. These functions should
    always return a list of TransactionRecords.
    """
    import_spec = context.get("__callable__", default_post_pay_callable(target))
    if not import_spec:
        return records
    to_call = import_string(import_spec)
    return to_call(billable=billable, target=target, context=context, records=records)


def paired_iterator(always: Any, iterable: Iterable):
    """
    Generator function that always returns a tuple with the first value as it iterates
    over the second value.
    """
    for item in iterable:
        yield always, item


def invoice_post_save(
    transactions: List["TransactionRecord"],
    attempt: PaymentAttempt,
    user: User,
    context: dict,
):
    """
    Post-save perform_charge hook for invoices.
    """
    invoice = context["invoice"]
    invoice_ref = ref_for_instance(invoice)
    for record in transactions:
        record.targets.add(invoice_ref)


def invoice_initiate_transactions(
    attempt: PaymentAttempt,
    amount: Money,
    user: User,
    context: dict,
) -> List["TransactionRecord"]:
    from apps.sales.models import TransactionRecord

    funding_record: Optional[TransactionRecord] = None

    invoice = context["invoice"]
    transaction_specs = lines_to_transaction_specs(invoice.line_items.all())
    if attempt.get("cash"):
        source = CASH_DEPOSIT
    else:
        source = CARD
    # TODO: Make pay from fund an option some day, rather than adding this special case.
    if not ((invoice.type == VENDOR) and (source == CASH_DEPOSIT)):
        # First, the funding transaction.
        funding_record = TransactionRecord(
            payer=invoice.bill_to,
            status=FAILURE,
            payee=invoice.bill_to,
            category=PAYMENT,
            source=source,
            destination=FUND,
            amount=amount,
            response_message="Failed when allocating cash transfer.",
        )
    if not context["successful"]:
        assert funding_record, "Somehow failed to pay from cash. There must be a bug!"
        return [funding_record]
    transactions = [
        TransactionRecord(
            payer=invoice.bill_to,
            status=FAILURE,
            category=category,
            source=FUND,
            payee=destination_user,
            destination=destination_account,
            amount=value,
            response_message="Failed when contacting payment processor.",
        )
        for (
            (destination_user, destination_account, category),
            value,
        ) in transaction_specs.items()
        if value
    ]
    if attempt.get("stripe_event"):
        transactions.extend(
            initialize_stripe_charge_fees(
                amount=amount, stripe_event=attempt["stripe_event"]
            )
        )
    if funding_record:
        transactions.insert(0, funding_record)
    return transactions


def post_payment_transaction_creator(invoice: "Invoice", context: dict):
    """
    After an invoice is paid, the line items on the invoice tell us where to send
    the money. We create transactions for all of these based on the data given.

    The resulting transactions are later modified by the relevant post_pay hooks.
    """
    attempt = context.get("attempt")
    if not attempt:
        charge_event = context["stripe_event"]["data"]["object"]
        amount = context["amount"]
        attempt = {
            "stripe_event": charge_event,
            "amount": amount,
            "remote_ids": remote_ids_from_charge(charge_event),
        }
    success, records, message = perform_charge(
        attempt=attempt,
        amount=attempt["amount"],
        user=invoice.bill_to,
        requesting_user=context.get("requesting_user", invoice.bill_to),
        post_save=invoice_post_save,
        context={"invoice": invoice, "successful": context["successful"]},
    )
    return records


def freeze_line_items(invoice: "Invoice"):
    """
    Freezes the calculated values of line items on an invoice so that they'll no longer
    be dynamically handled
    """
    line_items = list(invoice.line_items.all())
    _, __, results = get_totals(line_items)
    for line_item in line_items:
        line_item.frozen_value = results[line_item]
        line_item.save()


@transaction.atomic
def invoice_post_payment(
    invoice: "Invoice", context: dict
) -> List["TransactionRecord"]:
    """
    Post-pay hook. This iterates through all targets and all targets on all line items,
    and then runs hooks for each. Any asynchronous operations that should occur should
    be scheduled tasks that can verify finished state and start afterwards. Otherwise,
    they might run with a DB that failed the transaction.

    Note that a payment may be 'failed.' We still call the post-payment hooks as they
    may need to perform some task like creating failed transaction records for
    reference. Payments that have failed will have successful=False in the context
    dictionary.
    """
    from apps.sales.models import Invoice
    from apps.sales.tasks import withdraw_all

    if context["successful"] and context["amount"] != invoice.total():
        raise AssertionError("The amount paid does not match the invoice total!")
    all_targets = (
        paired_iterator(invoice, invoice.targets.all()),
        *(
            paired_iterator(line_item, line_item.targets.all())
            for line_item in invoice.line_items.all().prefetch_related("targets")
        ),
    )
    all_targets = list(chain(*all_targets))
    for billable, target in all_targets:
        if not target.target:  # pragma: no cover
            raise IntegrityError(
                f"{target.__class__.__name__} for deleted item paid: #{invoice.id}, "
                f"GenericReference {target.id}",
            )
        context.update(
            pre_pay_hook(
                billable=billable,
                target=target.target,
                context={**context, **billable.context_for(target)},
            ),
        )
    # The pre-pay hooks may modify the invoice somewhat.
    invoice.refresh_from_db()
    records = post_payment_transaction_creator(invoice, context)
    for billable, target in all_targets:
        initial_records = records
        records = post_pay_hook(
            billable=billable,
            target=target.target,
            context={**context, **billable.context_for(target)},
            records=records,
        )
        if initial_records and not records:  # pragma: no cover
            raise RuntimeError(
                "Failed to return records from post_pay hook. Aborting to avoid data "
                "loss!"
            )
    if context["successful"]:
        invoice.paid_on = datetime.now(tz=UTC)
        invoice.status = PAID
        if invoice.type == VENDOR:
            invoice.payout_available = True
        invoice.save()
        freeze_line_items(invoice)
        if invoice.issued_by:
            # Make (pretty) sure we've closed out the transaction first. This won't work
            # right in testing, of course, since celery is always eager.
            withdraw_all.apply_async((invoice.issued_by_id,), countdown=1)
    # Remove a user's delinquency status if they've paid off everything that is due.
    outstanding = Invoice.objects.filter(
        bill_to=invoice.bill_to,
        due_date__isnull=False,
        due_date__lte=datetime.now(tz=UTC),
        status=OPEN,
    ).count()
    if not outstanding:
        invoice.bill_to.delinquent = False
        invoice.bill_to.save()
    return records


def refund_deliverable(deliverable: "Deliverable", requesting_user=None) -> (bool, str):
    from apps.sales.models import TransactionRecord

    statuses = [QUEUED, IN_PROGRESS, DISPUTED, REVIEW]
    if deliverable.invoice.paypal_token:
        statuses.append(COMPLETED)
    assert deliverable.status in statuses
    if not deliverable.escrow_enabled:
        deliverable.status = REFUNDED
        deliverable.redact_available_on = timezone.now().date()
        deliverable.save()
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        return True, ""
    target = ref_for_instance(deliverable)
    fund_transaction = TransactionRecord.objects.get(
        source__in=[CARD, CASH_DEPOSIT],
        targets=target,
        payer=deliverable.order.buyer,
        payee=deliverable.order.buyer,
        destination=FUND,
        status=SUCCESS,
    )
    transaction_set = TransactionRecord.objects.filter(
        source=FUND,
        payer=deliverable.order.buyer,
        targets=target,
        status=SUCCESS,
    ).exclude(category=SHIELD_FEE)
    record = issue_refund(
        fund_transaction,
        transaction_set,
        ESCROW_REFUND,
        processor=deliverable.processor,
    )[0]
    if record.status == FAILURE:
        return False, record.response_message
    deliverable.status = REFUNDED
    deliverable.refunded_on = timezone.now()
    deliverable.redact_available_on = timezone.now().date() + relativedelta(
        days=settings.REDACTION_ALLOWED_WINDOW
    )
    deliverable.save()
    notify(REFUND, deliverable, unique=True, mark_unread=True)
    notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
    if requesting_user != deliverable.order.seller:
        notify(SALE_UPDATE, deliverable, unique=True, mark_unread=True)
    return True, ""


def reverse_record(record: "TransactionRecord") -> (bool, "TransactionRecord"):
    """
    Creates an inverse record from an existing record. Note: This does NOT perform any
    particular API requests needed to support the reversal outside the system, such as
    refunding credit cards.
    """
    from apps.sales.models import TransactionRecord

    if record.status != SUCCESS:
        raise ValueError("Transactions may not be reversed if they have not succeeded.")
    ref = ref_for_instance(record)
    old_record = TransactionRecord.objects.filter(
        targets=ref_for_instance(record),
        amount=record.amount,
        destination=record.source,
        source=record.destination,
        status__in=[SUCCESS, PENDING],
    ).first()
    if old_record:
        return False, old_record
    new_record = TransactionRecord.objects.create(
        status=SUCCESS,
        source=record.destination,
        destination=record.source,
        category=record.category,
        amount=record.amount,
        payer=record.payee,
        payee=record.payer,
        card=record.card,
        auth_code=record.auth_code,
        remote_ids=record.remote_ids,
        note=f"Reversal for {record.id}",
    )
    new_record.targets.set(record.targets.all())
    new_record.targets.add(ref)
    return True, new_record


def lines_for_product(product: "Product", force_shield=False) -> List["LineItemSim"]:
    from apps.sales.models import LineItemSim

    results = []
    for line in deliverable_lines(
        base_price=product.base_price,
        extra_lines=[],
        table_product=product.table_product,
        escrow_enabled=force_shield or product.escrow_enabled,
        plan_name=product.user.service_plan.name,
        user_id=product.user.id,
        international=product.international,
    ):
        line["type"] = int(line.pop("kind"))
        line["category"] = int(line["category"])
        line["destination_account"] = int(line["destination_account"])
        # We're not removing these just yet, but we intend to once things are stable.
        line["cascade_amount"] = False
        line["cascade_percentage"] = False
        line["cascade_under"] = 201
        results.append(LineItemSim(**line))
    return results


class PaymentIntentSettingsData(TypedDict):
    card_id: Optional[int]
    use_reader: bool
    save_card: bool
    make_primary: bool


def get_invoice_intent(invoice: "Invoice", payment_settings: PaymentIntentSettingsData):
    if invoice.bill_to and invoice.bill_to.is_registered:
        create_or_update_stripe_user(invoice.bill_to.id)
        invoice.bill_to.refresh_from_db()
    if invoice.bill_to:
        stripe_token = get_intent_card_token(
            invoice.bill_to, payment_settings.get("card_id")
        )
    else:
        raise ValidationError(
            "Cannot create a payment intent when there's no user to bill."
        )
    use_terminal = payment_settings["use_reader"]
    save_card = payment_settings["save_card"] and not invoice.bill_to.guest
    make_primary = (
        save_card and payment_settings["make_primary"]
    ) and not invoice.bill_to.guest
    total = invoice.total()
    amount = int(total.amount * total.currency.sub_unit)
    if not amount:
        raise ValidationError("Cannot create a payment intent for a zero invoice.")
    if use_terminal:
        # We set card here as well to prevent a transaction issue on Stripe's side where
        # We can't unset the payment method at the same time as changing the payment
        # method types to just card_present.
        payment_method_types = ["card_present", "card"]
        capture_method = "manual"
        save_card = False
        make_primary = False
        stripe_token = None
    else:
        payment_method_types = ["card"]
        capture_method = "automatic"
    with stripe as stripe_api:
        # Can only do string values, so won't be json true value.
        metadata = {
            "invoice_id": invoice.id,
            "make_primary": make_primary,
            "save_card": save_card,
        }
        intent_kwargs = {
            # Need to figure out how to do this per-currency.
            "amount": int(total.amount * total.currency.sub_unit),
            "currency": str(total.currency).lower(),
            "customer": (invoice.bill_to and invoice.bill_to.stripe_token) or None,
            # Note: If we expand the payment types, we may need to take into account
            # that linking the charge_id to the source_transaction field of the payout
            # transfer could cause problems. See:
            # https://stripe.com/docs/connect/charges-transfers#transfer-availability
            "payment_method_types": payment_method_types,
            "payment_method": stripe_token,
            "capture_method": capture_method,
            "transfer_group": f"ACInvoice#{invoice.id}",
            "metadata": metadata,
            "receipt_email": invoice.bill_to.guest_email or invoice.bill_to.email,
        }
        if save_card:
            intent_kwargs["setup_future_usage"] = "off_session"
        if invoice.current_intent:
            try:
                intent = stripe_api.PaymentIntent.modify(
                    invoice.current_intent, **intent_kwargs
                )
                return intent["client_secret"]
            except InvalidRequestError as err:
                if err.code == "payment_intent_unexpected_state":
                    if err.json_body and err.json_body["error"]["payment_intent"][
                        "status"
                    ] in [
                        "succeeded",
                        "processing",
                    ]:
                        raise ValidationError(
                            "This payment has already been made.",
                        )
                    # Don't catch this one-- will want to get notified if this fails
                    # somehow.
                    cancel_payment_intent(
                        api=stripe_api, intent_token=invoice.current_intent
                    )
                else:
                    raise err
        intent = stripe_api.PaymentIntent.create(**intent_kwargs)
        invoice.current_intent = intent["id"]
        invoice.save()
        return intent["client_secret"]


def update_downstream_pricing(user):
    """
    Updates the pricing on all items a user has. Especially useful when performing plan
    switches.
    """
    from apps.sales.models import Deliverable, update_user_availability

    for product in user.products.filter(active=True):
        product.save()
    for deliverable in Deliverable.objects.filter(
        order__seller=user,
        status__in=[LIMBO, NEW, WAITING, PAYMENT_PENDING],
    ):
        deliverable.save()
    update_user_availability(None, user.artist_profile)


def mark_adult(deliverable):
    if deliverable.escrow_enabled or deliverable.invoice.paypal_token:
        if deliverable.order.buyer:
            deliverable.order.buyer.verified_adult = True
            deliverable.order.buyer.save(update_fields=["verified_adult"])


def credit_referral(deliverable):
    from apps.profiles.utils import extend_landscape

    seller_credit = False
    if not deliverable.order.seller.sold_shield_on:
        seller_credit = True
        deliverable.order.seller.sold_shield_on = timezone.now()
        deliverable.order.seller.save()
    if deliverable.order.buyer and not deliverable.order.buyer.bought_shield_on:
        deliverable.order.buyer.bought_shield_on = timezone.now()
        deliverable.order.buyer.save()
    if seller_credit and deliverable.order.seller.referred_by:
        extend_landscape(deliverable.order.seller.referred_by, months=1)
        notify(
            REFERRAL_LANDSCAPE_CREDIT,
            deliverable.order.seller.referred_by,
            unique=False,
        )


def claim_deliverable(user, deliverable):
    """
    Perform all subscriptions and settings to assign an arbitrator.
    """
    deliverable.arbitrator = user
    deliverable.save()
    subscriptions = [
        Subscription(
            type=COMMENT,
            object_id=deliverable.id,
            content_type=ContentType.objects.get_for_model(deliverable),
            subscriber=user,
            email=True,
        ),
        Subscription(
            type=REVISION_UPLOADED,
            object_id=deliverable.id,
            content_type=ContentType.objects.get_for_model(deliverable),
            subscriber=user,
            email=True,
        ),
        Subscription(
            type=ORDER_UPDATE,
            object_id=deliverable.id,
            content_type=ContentType.objects.get_for_model(deliverable),
            subscriber=user,
            email=True,
        ),
    ]
    for revision in deliverable.revision_set.all():
        subscriptions.append(
            Subscription(
                type=COMMENT,
                object_id=revision.id,
                content_type=ContentType.objects.get_for_model(revision),
                subscriber=user,
                email=True,
            )
        )
        subscriptions.append(
            Subscription(
                type=REVISION_APPROVED,
                object_id=revision.id,
                content_type=ContentType.objects.get_for_model(revision),
                subscriber=user,
                email=True,
            )
        )
    for reference in deliverable.reference_set.all():
        subscriptions.append(
            Subscription(
                type=COMMENT,
                object_id=reference.id,
                content_type=ContentType.objects.get_for_model(reference),
                subscriber=user,
                email=True,
            )
        )
    Subscription.objects.bulk_create(subscriptions, ignore_conflicts=True)


def get_line_description(line_item: "LineItem", amount: Money):
    """
    Produce a description (with fallback default) by line item type.

    There is a more complex version of this function with smarter output
    in AcLineItemPreview on the frontend. This simpler one handles our
    needs here.
    """
    if line_item.description:
        return line_item.description
    if line_item.type == ADD_ON:
        if amount.amount < 0:
            return "Discount"
        return "Additional requirements"
    return LINE_ITEM_TYPES_TABLE[line_item.type]


def mark_deliverable_paid(deliverable: "Deliverable"):
    """
    For cases where we need to mark a deliverable as paid without handling
    any of the money ourselves.
    """
    if deliverable.final_uploaded:
        deliverable.status = COMPLETED
    elif deliverable.revision_set.all():
        deliverable.status = IN_PROGRESS
    else:
        deliverable.status = QUEUED
    if deliverable.product:
        deliverable.task_weight = deliverable.product.task_weight
        deliverable.expected_turnaround = deliverable.product.expected_turnaround
        deliverable.revisions = deliverable.product.revisions
    deliverable.revisions_hidden = False
    deliverable.escrow_enabled = False
    deliverable.save()
    deliverable.invoice.record_only = True
    deliverable.invoice.status = PAID
    deliverable.invoice.paid_on = timezone.now()
    freeze_line_items(deliverable.invoice)
    deliverable.invoice.save()
    term_charge(deliverable)
    notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)


def cart_for_request(request, create=False):
    """
    Grabs the shopping cart for a particular request, or creates a new one if it
    does not exist.
    """
    from apps.sales.models import ShoppingCart, Product

    cart = None
    if request.GET.get("cart_id"):
        try:
            cart = ShoppingCart.objects.filter(id=request.GET.get("cart_id")).first()
            # Whoever owned this cart before, it's ours now!
            if request.user:
                cart.user = request.user
            else:
                cart.session_key = request.session.session_key
            cart.save()
        except (TypeError, ValueError):
            pass
    elif request.user.is_registered:
        cart = ShoppingCart.objects.filter(user=request.user).first()
    else:
        cart = ShoppingCart.objects.filter(
            session_key=request.session.session_key
        ).first()
    if cart:
        return cart
    user = request.user if request.user.is_registered else None
    session_key = request.session.session_key
    if not create:
        return None
    product_id = request.data.get("product", None)
    if create and not product_id:
        raise ValidationError({"product": "This field is required."})
    with transaction.atomic():
        product = Product.objects.filter(id=product_id).select_for_update().first()
        if not product:
            raise ValidationError({"product": "This product does not exist."})
        return ShoppingCart.objects.create(
            user=user, session_key=session_key, product_id=product_id
        )


class RedactionError(Exception):
    """
    Exception type for issues when redacting a deliverable.
    """


def redact_deliverable(deliverable: "Deliverable") -> None:
    """
    Destroys all specific information about a deliverable. Useful to clear out
    old commissions without removing key financial information.
    """
    from apps.sales.models import Revision, Reference

    if deliverable.status in WORK_IN_PROGRESS_STATUSES:
        raise RedactionError(
            "Deliverable must be cancelled, finalized, or refunded first.",
        )
    for revision in deliverable.revision_set.all():
        with transaction.atomic():
            revision_id = revision.id
            file_id = revision.file.id
            revision.delete()
            check_asset_associations(file_id)
        clear_comments_by_content_obj_ref(
            content_type=ContentType.objects.get_for_model(Revision),
            target_id=revision_id,
        )
    for reference in deliverable.reference_set.all():
        reference_id = reference.id
        reference_removed = False
        with transaction.atomic():
            deliverable.reference_set.remove(reference)
            if not reference.deliverables.exists():
                file_id = reference.file.id
                reference.delete()
                reference_removed = True
                check_asset_associations(file_id)
        if reference_removed:
            clear_comments_by_content_obj_ref(
                content_type=ContentType.objects.get_for_model(Reference),
                target_id=reference_id,
            )
    deliverable.characters.clear()
    deliverable.details = ""
    deliverable.notes = ""
    deliverable.name = "Redacted"
    clear_comments(deliverable)
    if deliverable.status in [NEW, PAYMENT_PENDING]:
        deliverable.status = CANCELLED
    deliverable.redacted_on = timezone.now()
    deliverable.save()


def _pricing_spec():
    from apps.sales.models import ServicePlan
    from apps.sales.serializers import ServicePlanSerializer

    plans = ServicePlan.objects.all().order_by("sort_value")
    return {
        "plans": ServicePlanSerializer(instance=plans, many=True, context={}).data,
        "minimum_price": str(settings.MINIMUM_PRICE.amount),
        "table_percentage": str(settings.TABLE_PERCENTAGE_FEE),
        "table_static": str(settings.TABLE_STATIC_FEE.amount),
        "table_tax": str(settings.TABLE_TAX),
        "international_conversion_percentage": (
            str(settings.INTERNATIONAL_CONVERSION_PERCENTAGE)
        ),
        "preferred_plan": settings.PREFERRED_SERVICE_PLAN_NAME,
        "stripe_blended_rate_static": str(settings.STRIPE_BLENDED_RATE_STATIC.amount),
        "stripe_blended_rate_percentage": str(settings.STRIPE_BLENDED_RATE_PERCENTAGE),
        "stripe_payout_cross_border_percentage": str(
            settings.STRIPE_PAYOUT_CROSS_BORDER_PERCENTAGE
        ),
        "stripe_active_account_monthly_fee": str(
            settings.STRIPE_ACTIVE_ACCOUNT_MONTHLY_FEE.amount,
        ),
        "stripe_payout_static": str(settings.STRIPE_PAYOUT_STATIC.amount),
        "stripe_payout_percentage": str(settings.STRIPE_PAYOUT_PERCENTAGE),
        "processing_percentage": str(settings.PROCESSING_PERCENTAGE),
        "processing_static": str(settings.PROCESSING_STATIC.amount),
    }


def pricing_spec():
    """
    Get the full pricing information for services.
    """
    return cache.get_or_set("price_data", _pricing_spec)
