import logging
from datetime import datetime
from typing import Dict, Optional, Any

from dateutil.parser import parse
from django.urls import reverse

from apps.lib.models import (
    ref_for_instance,
)
from apps.lib.constants import (
    RENEWAL_FAILURE,
    SUBSCRIPTION_DEACTIVATED,
    RENEWAL_FIXED,
    AUTO_CLOSED,
)
from apps.lib.utils import notify, require_lock, send_transaction_email, utc_now
from apps.profiles.models import User
from apps.sales.constants import (
    PAYOUT_ACCOUNT,
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
    PENDING,
    REVIEW,
    SUCCESS,
    VOID,
    WEIGHTED_STATUSES,
    COMPLETED,
)
from apps.sales.mail_campaign import drip
from apps.sales.models import (
    CreditCardToken,
    Deliverable,
    Invoice,
    ServicePlan,
    StripeAccount,
    TransactionRecord,
    Order,
    ShoppingCart,
    WebhookEventRecord,
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
from django.core.cache import cache
from django.db import transaction, IntegrityError
from django.db.models import Q, Count
from django.utils import timezone
from moneyed import Money
from stripe import CardError

from shortcuts import make_url

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
    users = (
        User.objects.filter(
            service_plan__isnull=False,
            service_plan_paid_through__lte=timezone.now().date(),
            service_plan_paid_through__gt=timezone.now().date()
            - relativedelta(days=settings.TERM_GRACE_DAYS + 1),
        )
        .exclude(
            Q(service_plan__name=settings.DEFAULT_SERVICE_PLAN_NAME)
            & Q(service_plan__hidden=False)
        )
        .exclude(
            is_active=False,
        )
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


RecordMap = Dict[Invoice, TransactionRecord]


# TODO: Reimplement this lock as an application lock.
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
            destination=PAYOUT_ACCOUNT,
            status=PENDING,
            response_message="Failed to connect to server",
        )
        for sub_record in records:
            record.targets.add(*sub_record.targets.all())
        record.targets.add(bank_ref)
        record_map[invoice] = record
    if not amount:
        return record_map
    raise IntegrityError(
        f"Amount of {amount} found unconnected to any invoice for {user}!",
    )


@celery_app.task
def stripe_transfer(record_id: str, stripe_id: str, invoice_id: str) -> None:
    base_settings: dict[str, Any] = {"metadata": {}}
    stripe_account = StripeAccount.objects.get(id=stripe_id)
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
            record.status = SUCCESS
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
                invoice.payout_sent = True
                invoice.save()
                stripe_transfer.delay(record.id, banks[0].id, invoice.id)


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
        clear_deliverable.delay(deliverable.id)


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


@celery_app.task(
    bind=True,
    rate_limit="10/h",
    max_retries=30,
    retry_jitter=True,
)
def drip_placed_order(self, order_id):
    if not settings.DRIP_ACCOUNT_ID:
        return
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist as err:
        # Could be mid-transaction
        self.retry(exc=err)
    buyer = order.buyer
    if not buyer:
        return
    deliverable = order.deliverables.last()
    total = deliverable.invoice.total()
    data = {
        "provider": "artconomy",
        "email": buyer.guest_email or buyer.email,
        "order_id": str(order.id),
        "order_url": make_url(
            f"/orders/{buyer.username}/order/{order.id}/deliverables/{deliverable.id}/",
        ),
        "action": "placed",
        "grand_total": float(total.amount),
        "currency": str(total.currency),
    }
    deliverable = order.deliverables.all().last()
    if deliverable.product:
        data["product"] = str(deliverable.product.id)
    if buyer.drip_id:
        data["person_id"] = buyer.drip_id
    try:
        response = drip.post(
            f"/v3/{settings.DRIP_ACCOUNT_ID}/shopper_activity/order",
            json=data,
        )
        response.raise_for_status()
    except Exception as err:
        self.retry(exc=err)


@celery_app.task(
    bind=True,
    max_retries=30,
    retry_jitter=True,
)
def drip_sync_cart(self, cart_id: str, timestamp: str):
    if not settings.DRIP_ACCOUNT_ID:
        return
    timestamp = parse(timestamp)
    cart = (
        ShoppingCart.objects.exclude(Q(user=None) & Q(email=""))
        .filter(id=cart_id, edited_on=timestamp)
        .first()
    )
    if not cart:
        return
    data = {
        "provider": "artconomy",
        "email": cart.email or cart.user.guest_email or cart.user.email,
        "action": "updated" if cart.last_synced else "created",
        "cart_id": cart_id,
        "cart_url": make_url(
            reverse(
                "store:continue_cart",
                kwargs={
                    "username": cart.product.user.username,
                    "product_id": cart.product.id,
                },
            )
        )
        + f"?cart_id={cart_id}",
        "items": [
            {
                "product_id": str(cart.product.id),
                "name": cart.product.name,
                "brand": cart.product.user.username,
                "product_url": make_url(
                    reverse(
                        "store:product_preview",
                        kwargs={
                            "username": cart.product.user.username,
                            "product_id": cart.product.id,
                        },
                    )
                ),
            }
        ],
    }
    try:
        response = drip.post(
            f"/v3/{settings.DRIP_ACCOUNT_ID}/shopper_activity/cart",
            json=data,
        )
        response.raise_for_status()
        cart.last_synced = timezone.now()
        cart.save()
    except Exception as err:
        self.retry(exc=err)


@celery_app.task()
def clear_old_carts():
    ShoppingCart.objects.filter(
        edited_on__lte=timezone.now() - relativedelta(months=1)
    ).delete()


@celery_app.task()
def promote_top_sellers(reference_date: Optional[str] = None):
    end_date = parse(reference_date or utc_now().isoformat())
    end_date = end_date.replace(day=1, second=0, minute=0, hour=0, microsecond=0)
    start_date = end_date - relativedelta(months=1)
    users = (
        User.objects.filter(stars__gte=4.5)
        .exclude(stars=None)
        .exclude(is_active=False)
        .annotate(
            month_sales=Count(
                "sales",
                filter=Q(
                    sales__deliverables__created_on__gte=start_date,
                    sales__deliverables__created_on__lte=end_date,
                    sales__deliverables__status__in=[COMPLETED, *WEIGHTED_STATUSES],
                ),
            )
        )
        .order_by("-month_sales")
        .distinct()
    )[:2]
    User.objects.filter(featured=True).update(featured=False)
    for user in users:
        user.featured = True
        user.save(update_fields=["featured"])


@celery_app.task()
def clear_old_webhook_logs():
    WebhookEventRecord.objects.filter(
        created_on__lte=timezone.now() - relativedelta(months=2),
    ).delete()


@celery_app.task()
def run_balance_report(
    *, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
):
    """
    Ask Stripe to generate a balance report, which will then be sent to us via
    webhook for reconciliation.
    """
    with stripe as stripe_api:
        start_time_stamp: int = int(
            (start_time and start_time.timestamp())
            or (utc_now() - relativedelta(days=2)).timestamp()
        )
        end_time_stamp: int = int(
            (end_time and end_time.timestamp())
            or stripe_api.reporting.ReportType.retrieve("balance.summary.1")[
                "data_available_end"
            ]
        )
        stripe_api.reporting.ReportRun.create(
            report_type="balance_change_from_activity.itemized.3",
            parameters={
                "interval_start": start_time_stamp,
                "interval_end": end_time_stamp,
                "columns": [
                    "balance_transaction_id",
                    "created_utc",
                    "available_on_utc",
                    "reporting_category",
                    "gross",
                    "currency",
                    "description",
                ],
            },
        )


@celery_app.task()
def perform_redaction(deliverable_id: Deliverable) -> None:
    from apps.sales.utils import redact_deliverable

    deliverable = Deliverable.objects.get(id=deliverable_id)
    redact_deliverable(deliverable)


@celery_app.task()
def redact_scheduled_deliverables() -> None:
    for deliverable_id in (
        Deliverable.objects.exclude(auto_redact_on=None)
        .filter(auto_redact_on__lte=timezone.now().date())
        .values_list("id", flat=True)
    ):
        perform_redaction.delay(deliverable_id)
