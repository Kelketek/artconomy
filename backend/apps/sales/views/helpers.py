from typing import Union, List, TypedDict, Optional

from rest_framework.exceptions import ValidationError
from stripe.error import InvalidRequestError

from apps.profiles.tasks import create_or_update_stripe_user
from apps.sales.models import LineItem, Invoice, ServicePlan, Deliverable, TransactionRecord
from apps.sales.stripe import stripe
from apps.sales.utils import perform_charge, premium_post_success, premium_post_save, \
    premium_initiate_transactions, pay_deliverable, get_intent_card_token


def remote_ids_from_charge(charge_event):
    return [charge_event["payment_intent"], charge_event["id"]]


def service_charge(*, billable: Union[LineItem, Invoice], target: ServicePlan, context: dict):
    if not hasattr(billable, 'invoice'):  # pragma: no cover
        raise RuntimeError(
            "Post payment hook for service called on the invoice level rather than on the line item level. "
            "This should not happen-- we're tracking service plans at the line item level.",
        )
    invoice = billable.invoice
    attempt = {
        'amount': context['amount'],
        'service': target,
        'cash': context.get('cash', False),
    }
    remote_ids = []
    if 'stripe_event' in context:
        charge_event = context['stripe_event']['data']['object']
        attempt['stripe_event'] = charge_event
        attempt['remote_ids'] = [charge_event["payment_intent"], charge_event["id"]]
        remote_ids = remote_ids_from_charge(charge_event)
    amount = context['amount']
    _, transactions, __ = perform_charge(
        attempt=attempt,
        amount=amount,
        user=invoice.bill_to,
        requesting_user=invoice.bill_to,
        post_success=premium_post_success(invoice, target),
        post_save=premium_post_save(invoice, remote_ids),
        context={},
        initiate_transactions=premium_initiate_transactions,
    )
    return transactions


def deliverable_charge(*, billable: Union[LineItem, Invoice], target: Deliverable, context: dict) -> List['TransactionRecord']:
    if isinstance(billable, LineItem):
        # As yet, we don't have anything special here, but we may eventually.
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


class PaymentIntentSettingsData(TypedDict):
    card_id: Optional[int]
    use_reader: bool
    save_card: bool
    make_primary: bool


def get_invoice_intent(invoice: Invoice, payment_settings: PaymentIntentSettingsData):
    if invoice.bill_to.is_registered:
        create_or_update_stripe_user(invoice.bill_to.id)
        invoice.bill_to.refresh_from_db()
    stripe_token = get_intent_card_token(invoice.bill_to, payment_settings.get('card_id'))
    use_terminal = payment_settings['use_reader']
    save_card = payment_settings['save_card'] and not invoice.bill_to.guest
    make_primary = (save_card and payment_settings['make_primary']) and not invoice.bill_to.guest
    total = invoice.total()
    amount = int(total.amount * total.currency.sub_unit)
    if not amount:
        raise ValidationError('Cannot create a payment intent for a zero invoice.')
    if use_terminal:
        # We set card here as well to prevent a transaction issue on Stripe's side where
        # We can't unset the payment method at the same time as changing the payment method
        # types to just card_present.
        payment_method_types = ['card_present', 'card']
        capture_method = 'manual'
        save_card = False
        make_primary = False
        stripe_token = None
    else:
        payment_method_types = ['card']
        capture_method = 'automatic'
    with stripe as stripe_api:
        # Can only do string values, so won't be json true value.
        metadata = {'invoice_id': invoice.id, 'make_primary': make_primary, 'save_card': save_card}
        intent_kwargs = {
            # Need to figure out how to do this per-currency.
            'amount': int(total.amount * total.currency.sub_unit),
            'currency': str(total.currency).lower(),
            'customer': invoice.bill_to.stripe_token or None,
            # Note: If we expand the payment types, we may need to take into account that linking the
            # charge_id to the source_transaction field of the payout transfer could cause problems. See:
            # https://stripe.com/docs/connect/charges-transfers#transfer-availability
            'payment_method_types': payment_method_types,
            'payment_method': stripe_token,
            'capture_method': capture_method,
            'transfer_group': f'ACInvoice#{invoice.id}',
            'metadata': metadata,
            'receipt_email': invoice.bill_to.guest_email or invoice.bill_to.email,
        }
        if save_card:
            intent_kwargs['setup_future_usage'] = 'off_session'
        if invoice.current_intent:
            try:
                intent = stripe_api.PaymentIntent.modify(invoice.current_intent, **intent_kwargs)
            except InvalidRequestError as err:
                if err.code == 'payment_intent_unexpected_state':
                    raise ValidationError(
                        'Payment intent not in expected state. '
                        'Likely, it has been paid and we are waiting on webhooks.',
                    )
            return intent['client_secret']
        intent = stripe_api.PaymentIntent.create(**intent_kwargs)
        invoice.current_intent = intent['id']
        invoice.save()
        return intent['client_secret']
