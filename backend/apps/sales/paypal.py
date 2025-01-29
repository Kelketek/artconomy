import logging
import sys
from decimal import Decimal
from datetime import datetime

from typing import Optional, TYPE_CHECKING

from authlib.integrations.requests_client import OAuth2Session
from django.conf import settings
from django.db import transaction
from moneyed import Money
from authlib.integrations.base_client.errors import OAuthError

from apps.lib.utils import FakeRequest
from apps.profiles.models import User
from apps.sales.constants import (
    DELIVERABLE_TRACKING,
    RECONCILIATION,
    BASE_PRICE,
    HOLDINGS,
    TAX,
    MONEY_HOLE,
    TAXES,
    CORRECTION,
)
from apps.sales.line_item_funcs import get_totals, digits, down_context

log = logging.getLogger("authlib")
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

if TYPE_CHECKING:  # pragma: no cover
    from apps.sales.models import PaypalConfig, Invoice, LineItem, Deliverable


class PayPal:
    """
    Manager class for acting as a PayPal app for a given user.
    """

    def __init__(self, *, key: str, secret: str, template_id: str):
        if settings.SANDBOX_APIS:
            self.base_url = "https://api-m.sandbox.paypal.com/"
        else:
            self.base_url = "https://api-m.paypal.com/"
        self.template_id = template_id
        self.client = OAuth2Session(key, secret)
        # We're not using PayPal's marketplace functionality. We're using direct
        # API keys for each user so that they're responsible for the content they
        # handle.

    def get(self, url, *args, raise_error=True, **kwargs):
        response = self.client.get(f"{self.base_url}{url}", *args, **kwargs)
        if raise_error:
            response.raise_for_status()
        return response

    def post(self, url, json, *args, raise_error=True, **kwargs):
        response = self.client.post(f"{self.base_url}{url}", *args, json=json, **kwargs)
        if raise_error:
            response.raise_for_status()
        return response

    def put(self, url, json, *args, raise_error=True, **kwargs):
        response = self.client.put(f"{self.base_url}{url}", *args, json=json, **kwargs)
        if raise_error:
            response.raise_for_status()
        return response

    def patch(self, url, json, *args, raise_error=True, **kwargs):
        response = self.client.patch(
            f"{self.base_url}{url}",
            *args,
            json=json,
            **kwargs,
        )
        if raise_error:
            response.raise_for_status()
        return response

    def delete(self, url, *args, raise_error=True, **kwargs):
        response = self.client.delete(f"{self.base_url}{url}", *args, **kwargs)
        if raise_error:
            response.raise_for_status()
        return response

    def __enter__(self):
        try:
            self.client.fetch_token(f"{self.base_url}v1/oauth2/token")
        except OAuthError:
            # Subsequent calls will fail, which we'll prefer for flow control.
            pass
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # No cleanup needed.
        pass


def paypal_api(user: Optional[User] = None, config: Optional["PaypalConfig"] = None):
    """
    Scaffolds up the PayPal class based on a particular user or config.

    Validates that the user has a sane config. If a config is passed,
    does not validate that the config is active before use.
    """
    from apps.sales.models import PaypalConfig

    if config is None:
        try:
            config = user.paypal_config
            if not config.active:
                raise PaypalConfig.DoesNotExist("No active PayPal Configuration.")
        except PaypalConfig.DoesNotExist as err:
            raise PaypalConfig.DoesNotExist(
                "This user has not set up their PayPal credentials."
            ) from err
        except AttributeError:
            raise TypeError("Neither user nor config specified.")
    return PayPal(key=config.key, secret=config.secret, template_id=config.template_id)


def get_paypal_recipients(invoice: "Invoice"):
    if invoice.bill_to is None:
        return []
    if invoice.bill_to.guest:
        return [{"billing_info": {"email_address": invoice.bill_to.guest_email}}]
    return [{"billing_info": {"email_address": invoice.bill_to.email}}]


def paypal_date(timestamp: datetime) -> str:
    return timestamp.strftime("%Y-%m-%d")


def serialize_line_item(
    line: "LineItem", line_subtotal: Money, deliverable: "Deliverable"
):
    from apps.sales.utils import get_line_description

    description = line.description
    if not line.description and line.type == BASE_PRICE:
        description = deliverable.notification_name(
            {
                "request": FakeRequest(
                    deliverable.order.buyer or deliverable.order.seller
                ),
            }
        )
        if deliverable.product:
            description = f"{description} - {deliverable.product.name}"
    if not description:
        description = get_line_description(line, line_subtotal)
    return {
        "name": description,
        "quantity": 1,
        "unit_of_measure": "AMOUNT",
        "unit_amount": {
            "currency_code": str(line_subtotal.currency),
            "value": str(line_subtotal.amount),
        },
    }


def delete_webhooks(config: "PaypalConfig"):
    if not config.webhook_id:
        return
    with paypal_api(config=config) as paypal:
        resp = paypal.delete(
            f"v1/notifications/webhooks/{config.webhook_id}",
            raise_error=False,
        )
        if resp.status_code == 404:
            # Webhook already deleted.
            return
        resp.raise_for_status()


def paypal_items(
    deliverable: "Deliverable",
    line_items: list["LineItem"],
    existing: list[dict],
):
    total, discount, line_map = get_totals(line_items)
    lines = [
        serialize_line_item(line, line_subtotal, deliverable)
        for line, line_subtotal in line_map.items()
    ]
    lines.extend(existing)
    return lines


def clear_existing_invoice(paypal: PayPal, invoice: "Invoice") -> bool:
    """
    Looks up an existing invoice and deletes it from PayPal if it exists.

    Make sure you've already entered the PayPal contest before calling this. Returns
    True if the invoice was deleted or else there was not one. Returns False if the
    invoice exists and is in a state we cannot edit.
    """
    response = paypal.post(
        "v2/invoicing/search-invoices",
        {"invoice_number": invoice.id},
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("items", []):
        # Does not exist.
        return True
    if data["items"][0]["status"] not in ["DRAFT", "CANCELLED"]:
        return False
    paypal.delete(f'v2/invoicing/invoices/{data["items"][0]["id"]}')
    return True


def paypal_invoice_url(invoice_token: str, sender=False):
    if sender:
        extension = f"/invoice/details/{invoice_token}"
    else:
        token = invoice_token.split("INV2-", maxsplit=1)[-1].replace("-", "")
        extension = f"/invoice/p/#{token}"
    if settings.SANDBOX_APIS:
        base_url = "https://www.sandbox.paypal.com"
    else:
        base_url = "https://www.paypal.com"
    return f"{base_url}{extension}"


def transferable_lines(invoice: "Invoice"):
    # Deliverable tracking is a helper line item type for the seller, but isn't to be
    # carried over to the invoice. Also orders the lines in a consistent manner.
    return [
        line_item
        for line_item in invoice.line_items.exclude(type=DELIVERABLE_TRACKING).order_by(
            "priority", "id"
        )
    ]


def sync_from_local_invoice(deliverable: "Deliverable", paypal_invoice: dict):
    """
    Builds a set of line items for initial synchronization from the PayPal invoice from
    our line items.
    """
    # Used for initial synchronization to the PayPal invoice from our line items.
    for source_item, dest_item in zip(
        transferable_lines(deliverable.invoice), paypal_invoice["items"]
    ):
        # Note: zip stops when the shortest iterator is exhausted, which should
        # always be line_items, if they aren't the same length.
        # This means any additional line items which we aren't accounting for
        # won't have a matching database entry, but we roll up a composite of the
        # difference below.
        source_item.paypal_token = dest_item["id"]
        price = Money(
            dest_item["unit_amount"]["value"],
            dest_item["unit_amount"]["currency_code"],
        )
        source_item.frozen_value = price
        source_item.save()


@down_context
def sync_from_upstream_invoice_edits(deliverable: "Deliverable", paypal_invoice: dict):
    """
    Finds existing line items we have record of from the
    :param deliverable:
    :param line_items:
    :param paypal_invoice:
    :return:
    """
    deliverable.invoice.currency = paypal_invoice["detail"]["currency_code"]
    deliverable.invoice.save()
    mapped_lines = {item["id"]: item for item in paypal_invoice["items"]}
    for line_item in deliverable.invoice.line_items.exclude(paypal_token="").all():
        if not mapped_lines.get(line_item.paypal_token):
            line_item.delete()
            continue
        paypal_line = mapped_lines[line_item.paypal_token]
        amount = Money(
            paypal_line["unit_amount"]["value"],
            paypal_line["unit_amount"]["currency_code"],
        ) * Decimal(paypal_line["quantity"])
        amount = amount.round(digits(amount.currency))
        line_item.amount = amount
        line_item.frozen_value = amount
        line_item.save()


def reconcile_invoices(
    deliverable: "Deliverable",
    paypal_invoice: dict,
):
    from apps.sales.models import LineItem

    deliverable.invoice.record_only = True
    # Only used for helping the artist determine their costs, but now would cause
    # a calculation problem.
    deliverable.invoice.line_items.filter(type=DELIVERABLE_TRACKING).delete()
    if deliverable.invoice.paypal_token:
        sync_from_upstream_invoice_edits(deliverable, paypal_invoice)
    else:
        deliverable.invoice.paypal_token = paypal_invoice["id"]
        deliverable.invoice.save()
        sync_from_local_invoice(
            deliverable,
            paypal_invoice,
        )
    for line in deliverable.invoice.line_items.filter(type__in=[TAX, RECONCILIATION]):
        # Make sure the websocket calls happen.
        line.delete()
    deliverable.invoice.line_items.filter(type__in=[TAX, RECONCILIATION]).delete()
    tax_total = Money(
        paypal_invoice["amount"]["breakdown"]["tax_total"]["value"],
        paypal_invoice["amount"]["breakdown"]["tax_total"]["currency_code"],
    )
    if tax_total:
        LineItem.objects.create(
            invoice=deliverable.invoice,
            type=TAX,
            category=TAXES,
            description="Tax",
            amount=tax_total,
            frozen_value=tax_total,
            # Required by database, but not used.
            destination_account=MONEY_HOLE,
            destination_user=deliverable.invoice.issued_by,
        )
    difference = (
        Money(
            paypal_invoice["amount"]["value"],
            paypal_invoice["amount"]["currency_code"],
        )
        - deliverable.invoice.total()
    )
    if difference:
        if difference.amount > 0:
            description = "Other costs (see PayPal)"
        else:
            description = "Other discounts (see PayPal invoice for details)"
        LineItem.objects.update_or_create(
            invoice=deliverable.invoice,
            type=RECONCILIATION,
            category=CORRECTION,
            description=description,
            amount=difference,
            frozen_value=difference,
            # Required by database, but not used.
            destination_account=HOLDINGS,
            destination_user=deliverable.invoice.issued_by,
        )


@transaction.atomic
def generate_paypal_invoice(deliverable: "Deliverable"):
    """
    Generate a PayPal invoice for a particular deliverable.

    If the deliverable is not eligible for PayPal invoicing (such as if the user
    doesn't have an active PayPal config, or PayPal invoicing is disabled for this
    deliverable), return False.

    Returns True if invoice was created successfully, and throws if there was a
    communication/API error with PayPal.
    """
    from apps.sales.models import PaypalConfig

    invoice = deliverable.invoice
    if not deliverable.order.seller.service_plan.paypal_invoicing:
        return False
    if not deliverable.paypal:
        return False
    try:
        config = invoice.issued_by.paypal_config
        if not config.active:
            return False
    except PaypalConfig.DoesNotExist:
        return False

    with paypal_api(config=config) as paypal:
        # First thing to do is to attempt deleting the invoice if it exists already,
        # which might happen if things fail.
        clear_existing_invoice(paypal, invoice)
        # Create initial invoice. Makes sure that any pre-added items, such as tax, are
        # created so that we can loop them in.
        data = {
            "detail": {
                "currency_code": "USD",
                "invoice_number": invoice.id,
                "payment_term": {
                    "term_type": "DUE_ON_RECEIPT",
                },
            },
            "configuration": {
                "allow_tip": True,
                "template_id": paypal.template_id,
            },
            "primary_recipients": get_paypal_recipients(invoice),
        }
        resp = paypal.post(
            "v2/invoicing/invoices",
            data,
        )
        # Now that we have the invoice created, we need to pull the existing line items
        # from it and consolidate them with our own.
        url = resp.json()["href"]
        remote_id = url.split("invoicing/invoices/")[-1]
        resp = paypal.get(f"v2/invoicing/invoices/{remote_id}")
        full_invoice = resp.json()
        source_items = transferable_lines(invoice)
        items = paypal_items(deliverable, source_items, full_invoice.get("items", []))
        full_invoice["items"] = items
        # This is dynamically calculated. Don't contradict upstream.
        del full_invoice["amount"]
        paypal.put(f"v2/invoicing/invoices/{remote_id}", full_invoice)
        resp = paypal.get(f"v2/invoicing/invoices/{remote_id}")
        full_invoice = resp.json()
        reconcile_invoices(deliverable, full_invoice)
        paypal.post(
            f"v2/invoicing/invoices/{remote_id}/send",
            {},
        )
        return True


class SignatureValidationError(ValueError):
    """
    Raised when a signature on a request is invalid.
    """


CERTIFICATE_CACHE = {}

REQUIRED_HEADERS = (
    "Paypal-Auth-Algo",
    "Paypal-Cert-Url",
)

VALID_PAYPAL_DOMAINS = (
    "https://api.sandbox.paypal.com/",
    "https://api.paypal.com/",
)


def validate_paypal_request(request, config: "PaypalConfig"):
    """
    Used to verify that webhook events actually came from PayPal.

    There is some way to DIY this so that we don't have to call PayPal every time
    they call us, but I've not been able to make it work according to their
    documentation.
    """
    if settings.BYPASS_PAYPAL_WEBHOOK_VALIDATION:
        return
    try:
        transmission_id = request.headers["Paypal-Transmission-Id"]
        transmission_time = request.headers["Paypal-Transmission-Time"]
        transmission_sig = request.headers["Paypal-Transmission-Sig"]
        auth_algo = request.headers["Paypal-Auth-Algo"]
        cert_url = request.headers["Paypal-Cert-Url"]
    except KeyError as err:
        raise SignatureValidationError("Missing critical header.") from err
    with paypal_api(config=config) as paypal:
        # Python's JSON serializer output is different from the json we receive.
        # Since it's a signature validation, we have to template this in a really weird
        # way that no one in their right mind would want to do.
        #
        # This could have an injection attack on our side easily. But this endpoint
        # doesn't do anything of consequence other than validate a call, and it will
        # reject anything that doesn't fit strictly to its schema anyway.
        data = (
            "{"
            f"""
            "auth_algo": "{auth_algo}",
            "cert_url": "{cert_url}",
            "transmission_id": "{transmission_id}",
            "transmission_sig": "{transmission_sig}",
            "transmission_time": "{transmission_time}",
            "webhook_id": "{config.webhook_id}",
            "webhook_event": {request.body.decode('utf-8')}
            """
            "}"
        )
        # If someone tries to make bogus requests, this will throw, and we'll know about
        # it.
        resp = paypal.post(
            "v1/notifications/verify-webhook-signature",
            json=None,
            data=data,
            headers={"content-type": "application/json"},
        )
        if not resp.json()["verification_status"] == "SUCCESS":
            raise SignatureValidationError("Signature validation failed!")
    return
