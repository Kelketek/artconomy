from typing import Union, List

from apps.profiles.models import User
from apps.sales.models import LineItem, Invoice, ServicePlan, Deliverable, TransactionRecord
from apps.sales.utils import get_term_invoice, perform_charge, premium_post_success, premium_post_save, \
    premium_initiate_transactions, pay_deliverable


def remote_ids_from_charge(charge_event):
    return [charge_event["payment_intent"], charge_event["id"]]


def service_charge(*, billable: Union[LineItem, Invoice], target: ServicePlan, context: dict):
    charge_event = context['stripe_event']['data']['object']
    user = User.objects.get(stripe_token=charge_event['customer'])
    invoice = get_term_invoice(user)
    amount = context['amount']
    _, transactions, __ = perform_charge(
        attempt={
            'stripe_event': charge_event,
            'amount': amount,
            'service': target,
            'remote_ids': [charge_event["payment_intent"], charge_event["id"]],
        },
        amount=amount,
        user=user,
        requesting_user=user,
        post_success=premium_post_success(invoice, target),
        post_save=premium_post_save(invoice, remote_ids_from_charge(charge_event)),
        context={},
        initiate_transactions=premium_initiate_transactions,
    )
    return transactions


def deliverable_charge(*, billable: Union[LineItem, Invoice], target: Deliverable, context: dict) -> List['TransactionRecord']:
    if isinstance(billable, LineItem):
        # As of yet, we don't have anything special here, but we may eventually.
        return []
    amount = context['amount']
    charge_event = context['stripe_event']['data']['object']
    deliverable = target
    # TODO: Unify handling of success flag to make this more consistent.
    _, records, message = pay_deliverable(
        attempt={
            'stripe_event': charge_event,
            'amount': amount,
            'remote_ids': remote_ids_from_charge(charge_event),
        },
        requesting_user=deliverable.order.buyer,
        deliverable=deliverable,
    )
    return records
