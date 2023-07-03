import logging
from collections import defaultdict
from decimal import ROUND_CEILING, localcontext
from typing import Dict, Union

from apps.lib.models import (
    AUTO_CLOSED,
    RENEWAL_FAILURE,
    RENEWAL_FIXED,
    SUBSCRIPTION_DEACTIVATED,
    ref_for_instance,
)
from apps.lib.utils import notify, require_lock, send_transaction_email
from apps.profiles.models import User
from apps.sales.constants import (
    ACH_TRANSACTION_FEES,
    BANK,
    CARD,
    CASH_WITHDRAW,
    DRAFT,
    FAILURE,
    HOLDINGS,
    LIMBO,
    MISSED,
    NEW,
    OPEN,
    PAID,
    PAYOUT_MIRROR_DESTINATION,
    PAYOUT_MIRROR_SOURCE,
    PENDING,
    REVIEW,
    SUCCESS,
    THIRD_PARTY_FEE,
    UNPROCESSED_EARNINGS,
    VOID,
)
from apps.sales.line_item_funcs import divide_amount
from apps.sales.models import (
    CreditCardToken,
    Deliverable,
    Invoice,
    ServicePlan,
    StripeAccount,
    TransactionRecord,
)
from apps.sales.stripe import money_to_stripe, stripe
from apps.sales.utils import (
    account_balance,
    add_service_plan_line,
    cancel_deliverable,
    destroy_deliverable,
    fetch_prefixed,
    finalize_deliverable,
    get_term_invoice,
    invoice_post_payment,
    update_downstream_pricing,
)
from conf.celery_config import celery_app
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.datetime_safe import datetime
from moneyed import Money
from pytz import UTC
from stripe.error import CardError

logger = logging.getLogger(__name__)


def zero_invoice_check(invoice: Invoice):
    """
    Checks if an invoice is a zero invoice. If it is, marks it paid and returns True.
    Otherwise, returns False
    """
    total = invoice.total()
    if not total:
        # This invoice is a zero invoice. This might happen for a plan with no monthly
        # subscription fee where no orders are processed.
        invoice_post_payment(
            invoice,
            {
                "amount": total,
                "successful": True,
                "attempt": {
                    "cash": True,
                    "amount": total,
                    "card_id": None,
                },
            },
        )
        return True
    return False


def renew_stripe_card(*, invoice, price, user, card):
    from apps.sales.models import Invoice

    if zero_invoice_check(invoice):
        return
    with stripe as stripe_api:
        amount, currency = money_to_stripe(price)
        kwargs = {
            "amount": amount,
            "currency": currency,
            "payment_method": card.stripe_token,
            "customer": user.stripe_token,
            "confirm": True,
            "off_session": True,
            # TODO: Needs to change per service name, or else be omitted since we'll be
            # swapping methods for tracking
            # subscriptions anyway.
            "metadata": {"service": "landscape", "invoice_id": invoice.id},
        }
        try:
            # This... might cause a race condition? Seems unlikely, but if we have a bug
            # later, it would be because the webhook was contacted before we set the
            # current_intent on the invoice.
            #
            # Using the update method here to be absolutely certain we don't change
            # anything else about the invoice that might clobber what the webhook is
            # doing.
            Invoice.objects.filter(id=invoice.id).update(
                current_intent=stripe_api.PaymentIntent.create(**kwargs)["id"]
            )
            return True
        except CardError as err:
            notify(
                RENEWAL_FAILURE,
                user,
                data={
                    "error": "Card ending in {} -- {}".format(card.last_four, err),
                    "invoice_id": invoice.id,
                },
                unique=True,
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
            f"!!! {user.username}({user.id}) has NONE for service_plan_paid_through "
            f"with subscription enabled!"
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
    if zero_invoice_check(invoice):
        return
    if card is None:
        # noinspection PyUnresolvedReferences
        cards = user.credit_cards.filter(active=True).order_by("-created_on")
        if not cards.exists():
            logger.info(
                "{}({}) can't renew due to no card on file.".format(
                    user.username, user.id
                )
            )
            notify(
                RENEWAL_FAILURE, user, data={"error": "No card on file!"}, unique=True
            )
            return
        card = cards[0]
    success = renew_stripe_card(
        invoice=invoice, user=user, card=card, price=invoice.total()
    )
    if not success:
        return
    if card_id or (paid_through < timezone.now().date()):
        # This was called manually or a previous attempt should have been made and there
        # may have been a gap in coverage. In this case, let's inform the user the
        # renewal was successful instead of silently succeeding.
        notify(RENEWAL_FIXED, user, unique=True)


@celery_app.task
def deactivate(user_id: int):
    user = User.objects.get(id=user_id)
    logger.info("Deactivated {}({})".format(user.username, user.id))
    notify(SUBSCRIPTION_DEACTIVATED, user, unique=True)
    default_plan = ServicePlan.objects.get(name=settings.DEFAULT_SERVICE_PLAN_NAME)
    user.service_plan = default_plan
    user.next_service_plan = default_plan
    # We only have delinquency for term invoices, but we may some day need to make this
    # work more generally.
    user.delinquent = True
    user.save()
    # Update the user's current term invoice to use the default service plan. This might
    # make it a zero invoice, which would clear it below.
    invoice = get_term_invoice(user)
    add_service_plan_line(invoice, user.next_service_plan)
    zero_invoice_check(invoice)
    update_downstream_pricing(user)


@celery_app.task
def run_billing():
    # Anyone we've not been able to renew for five days, assume won't be renewing
    # automatically.
    users = User.objects.filter(
        Q(
            service_plan__isnull=False,
            service_plan_paid_through__lte=timezone.now().date()
            - relativedelta(days=settings.TERM_GRACE_DAYS),
        )
    ).exclude(
        # We assume that the default plan is a free plan.
        Q(service_plan__name=settings.DEFAULT_SERVICE_PLAN_NAME)
    )
    for user in users:
        deactivate.delay(user.id)
    users = User.objects.filter(
        service_plan__isnull=False,
        service_plan_paid_through__lte=timezone.now().date(),
        service_plan_paid_through__gt=timezone.now().date()
        - relativedelta(days=settings.TERM_GRACE_DAYS + 1),
    ).exclude(
        Q(service_plan__name=settings.DEFAULT_SERVICE_PLAN_NAME)
        & Q(service_plan__hidden=False)
    )
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
    for deliverable in Deliverable.objects.filter(
        status=REVIEW, auto_finalize_on__lte=timezone.now().date()
    ):
        auto_finalize.delay(deliverable.id)


RecordMap = Dict[Union[Deliverable, None], TransactionRecord]


@require_lock(TransactionRecord, "ACCESS EXCLUSIVE")
def record_to_invoice_map(user, bank: StripeAccount, amount: Money) -> RecordMap:
    invoices = Invoice.objects.select_for_update(skip_locked=True).filter(
        issued_by=user,
        payout_sent=False,
        payout_available=True,
        record_only=False,
        status=PAID,
    )
    record_map: RecordMap = {}
    bank_ref = ref_for_instance(bank)
    for invoice in invoices:
        target = ref_for_instance(invoice)
        records = TransactionRecord.objects.filter(
            targets=target,
            payee=user,
            destination=HOLDINGS,
            status=SUCCESS,
        )
        sub_amount = sum(sub_record.amount for sub_record in records)
        amount -= sub_amount
        assert amount >= Money("0", amount.currency.code)
        record = TransactionRecord.objects.create(
            amount=sub_amount,
            source=HOLDINGS,
            payee=user,
            payer=user,
            category=CASH_WITHDRAW,
            destination=BANK,
            status=PENDING,
            response_message="Failed to connect to server",
        )
        for sub_record in records:
            record.targets.add(*sub_record.targets.all())
        record.targets.add(bank_ref)
        record_map[invoice] = record
    if not amount:
        return record_map
    # TODO: Add tools for invoicing out at the company level. All payouts should be tied
    # to an invoice.
    record = TransactionRecord.objects.create(
        amount=amount,
        source=HOLDINGS,
        payee=user,
        payer=user,
        category=CASH_WITHDRAW,
        destination=BANK,
        status=PENDING,
        note="Remaining amount, not connected to any invoice. May need annotations "
        "later.",
    )
    record.targets.add(bank_ref)
    record_map[None] = record
    return record_map


@celery_app.task
def stripe_transfer(record_id, stripe_id, invoice_id=None):
    base_settings = {"metadata": {}}
    stripe_account = StripeAccount.objects.get(id=stripe_id)
    invoice = None
    if invoice_id:
        invoice = Invoice.objects.get(id=invoice_id)
        base_settings["metadata"] = {"invoice_id": invoice.id}
        base_settings["transfer_group"] = f"ACInvoice#{invoice.id}"
        source_record = TransactionRecord.objects.filter(
            source=CARD,
            targets=ref_for_instance(invoice),
            status=SUCCESS,
        ).first()
        if source_record:
            try:
                base_settings["source_transaction"] = fetch_prefixed(
                    "ch_", source_record.remote_ids
                )
            except ValueError:
                pass
        assert invoice.issued_by == stripe_account.user
    record = TransactionRecord.objects.get(id=record_id)
    base_settings["amount"], base_settings["currency"] = money_to_stripe(record.amount)
    base_settings["destination"] = stripe_account.token
    base_settings["metadata"] = {"reference_transaction": record.id}
    assert record.payee == stripe_account.user
    with stripe as stripe_api:
        try:
            transfer = stripe_api.Transfer.create(
                **base_settings,
            )
            record.status = PENDING
            record.remote_ids = [
                transfer["destination_payment"],
                transfer["id"],
                transfer["balance_transaction"],
            ]
            record.remote_ids = [
                remote_id for remote_id in record.remote_ids if remote_id
            ]
            record.response_message = ""
            record.save()
        except Exception as err:
            record.response_message = str(err)
            record.status = FAILURE
            record.save()
            if invoice:
                invoice.payout_sent = False
                invoice.save()


@celery_app.task
def withdraw_all(user_id):
    user = User.objects.get(id=user_id)
    if not user.artist_profile.auto_withdraw:
        return
    if not hasattr(user, "stripe_account"):
        return
    banks = [user.stripe_account]
    with cache.lock(f"account_user__{user.id}"):
        balance = account_balance(user, HOLDINGS)
        if balance <= 0:
            return
        with transaction.atomic():
            record_map = record_to_invoice_map(user, banks[0], Money(balance, "USD"))
            for invoice, record in record_map.items():
                if invoice:
                    invoice.payout_sent = True
                    invoice.save()
                stripe_transfer.delay(record.id, banks[0].id, invoice and invoice.id)


@celery_app.task
def remind_sale(order_id):
    deliverable = Deliverable.objects.get(id=order_id)
    if not deliverable.status == NEW:
        return
    send_transaction_email(
        "Your commissioner is awaiting your response!",
        "sale_reminder.html",
        deliverable.order.seller,
        {
            "deliverable": deliverable,
        },
    )


@celery_app.task
def remind_sales():
    to_remind = []
    deliverables = Deliverable.objects.filter(
        status=NEW,
        auto_cancel_on__gte=timezone.now(),
        auto_cancel_on__isnull=False,
    )
    for deliverable in deliverables:
        delta = (timezone.now() - deliverable.auto_cancel_on).days
        if not (delta % 3):
            to_remind.append(deliverable)
            continue
    for deliverable in to_remind:
        remind_sale.delay(deliverable.id)


@transaction.atomic
def annotate_connect_fees_for_year_month(*, year: int, month: int) -> None:
    """
    Stripe levies fees on the full transaction volume. This means calculating them by
    individual transfers could lead to subtle differences between the amount we figure
    and they amount they actually charge us. So, we have to run these calculations for
    the volume over a whole month and then divvy them up.

    We create these entries in an idempotent manner so we can run them as we go along if
    we wish. By the end of the month, the amount of fees we calculate should match the
    amount they took.

    Note that this is done in two segments. All transfers out are subject to the general
    volume pricing, but those which go internationally are subject to an additional fee
    atop the main one. Stripe levies this as a separate fee so we calculate it
    separately and consolidate afterward.

    This function may need to be optimized depending on how many transactions we end up
    dealing with. However I'm optimizing for clarity of writing for now.

    Stripe calculates its timezones on UTC.
    """
    start_datetime = datetime(
        year=year,
        month=month,
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=UTC,
    )
    end_datetime = min(datetime.now(tz=UTC), start_datetime + relativedelta(months=1))
    target_transactions = list(
        TransactionRecord.objects.filter(
            finalized_on__gte=start_datetime,
            finalized_on__lt=end_datetime,
            status=SUCCESS,
            source=HOLDINGS,
            destination=BANK,
            targets__content_type=ContentType.objects.get_for_model(StripeAccount),
        )
        .distinct()
        .order_by("finalized_on")
    )
    if not len(target_transactions):
        return
    total_volume = sum(
        [target_transaction.amount for target_transaction in target_transactions]
    )
    # Need to track all fees for each user since we'll add to them multiple times.
    user_fees_map = defaultdict(list)
    # Need to know which transactions were cross-border since they incur additional
    # fees.
    cross_border_fees_list = []
    # And we'll need to tally the total from those transactions to derive the fee.
    cross_border_transactions = []
    with localcontext() as ctx:
        ctx.rounding = ROUND_CEILING
        base_fees = (total_volume * (settings.STRIPE_PAYOUT_PERCENTAGE / 100)).round(2)
    fee_list = divide_amount(base_fees, len(target_transactions))
    for record in target_transactions:
        # Can't use update_or_create here since we are looking around the 'targets'
        # many-to-many table.
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
        cross_border = (
            TransactionRecord.objects.filter(
                targets=ref_for_instance(record),
                source=PAYOUT_MIRROR_SOURCE,
                destination=PAYOUT_MIRROR_DESTINATION,
            )
            .exclude(amount_currency="USD")
            .exists()
        )
        if cross_border:
            cross_border_fees_list.append(fee_record)
            cross_border_transactions.append(record)
    # Each user has a $2 fee per month if they have a payout. This is part of the
    # 'connect' fee.
    for key, values in user_fees_map.items():
        fee_list = divide_amount(
            settings.STRIPE_ACTIVE_ACCOUNT_MONTHLY_FEE, len(values)
        )
        for value in values:
            value.amount += fee_list.pop(0) + settings.STRIPE_PAYOUT_STATIC
            value.save()
    if not cross_border_transactions:
        return
    cross_border_total = sum(
        [
            cross_border_transaction.amount
            for cross_border_transaction in cross_border_transactions
        ],
    )
    with localcontext() as ctx:
        ctx.rounding = ROUND_CEILING
        cross_border_fee = (
            cross_border_total * (settings.STRIPE_PAYOUT_CROSS_BORDER_PERCENTAGE / 100)
        ).round(2)
    fee_list = divide_amount(cross_border_fee, len(cross_border_transactions))
    for fee_record in cross_border_fees_list:
        fee_record.amount += fee_list.pop(0)
        fee_record.save()


@celery_app.task
def annotate_connect_fees():
    """
    Runs through all payouts and tallies expected fees, creating entries for all of
    them.
    """
    target_date = timezone.now()
    annotate_connect_fees_for_year_month(month=target_date.month, year=target_date.year)
    if target_date.day == 1:
        # Also do last month's to finish it off.
        target_date -= relativedelta(months=1)
        annotate_connect_fees_for_year_month(
            month=target_date.month, year=target_date.year
        )


@celery_app.task
def clear_deliverable(deliverable_id):
    try:
        deliverable = Deliverable.objects.get(id=deliverable_id, status=MISSED)
    except Deliverable.DoesNotExist:
        return
    destroy_deliverable(deliverable)


@celery_app.task
def clear_cancelled_deliverables():
    to_destroy = Deliverable.objects.filter(
        status__in=[MISSED],
        cancelled_on__lte=timezone.now() - relativedelta(weeks=2),
        term_billed=False,
    )
    for deliverable in to_destroy:
        clear_deliverable(deliverable.id)


@celery_app.task
def cancel_abandoned_orders():
    """
    Cancels all orders that have been abandoned-- either in Limbo or from
    non-interaction.
    """
    abandoned = Deliverable.objects.filter(
        status=LIMBO,
        created_on__lte=timezone.now() - relativedelta(days=settings.LIMBO_DAYS),
    )
    for deliverable in abandoned:
        cancel_deliverable(deliverable, None)
    auto_cancelled = Deliverable.objects.filter(
        status=NEW,
        auto_cancel_on__lte=timezone.now(),
        auto_cancel_on__isnull=False,
    )
    users = set()
    for deliverable in auto_cancelled:
        cancel_deliverable(deliverable, None)
        user = deliverable.order.seller
        if user not in users:
            users |= {user}
            previously_available = not user.artist_profile.commissions_closed
            user.artist_profile.commissions_closed = True
            user.artist_profile.save()
            if previously_available:
                notify(
                    AUTO_CLOSED,
                    user,
                    data={"abandoned": True},
                    unique=True,
                    mark_unread=True,
                )


@celery_app.task
def destroy_expired_invoices():
    Invoice.objects.filter(
        status__in=[VOID, DRAFT, OPEN], expires_on__lte=timezone.now()
    ).delete()
