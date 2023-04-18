from apps.lib.tests.factories import AssetFactory
from apps.profiles.tests.factories import UserFactory
from apps.sales.constants import ADD_ON, CARD, ESCROW, ESCROW_HOLD, SUCCESS
from apps.sales.models import (
    BankAccount,
    CreditCardToken,
    Deliverable,
    InventoryTracker,
    Invoice,
    LineItem,
    Order,
    Product,
    Promo,
    Rating,
    Reference,
    Revision,
    ServicePlan,
    StripeAccount,
    StripeLocation,
    StripeReader,
    TransactionRecord,
    WebhookRecord,
)
from factory import SelfAttribute, Sequence, SubFactory
from factory.django import DjangoModelFactory
from moneyed import Money


class ProductFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    expected_turnaround = 3
    revisions = 4
    task_weight = 2
    owner = SelfAttribute("user")
    base_price = Money("15.00", "USD")
    name = Sequence(lambda n: "Product {0}".format(n))
    description = "Product description"
    file = SubFactory(AssetFactory)

    class Meta:
        model = Product


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    buyer = SubFactory(UserFactory)
    seller = SubFactory(UserFactory)


class InvoiceFactory(DjangoModelFactory):
    bill_to = SubFactory(UserFactory)

    class Meta:
        model = Invoice


class StripeLocationFactory(DjangoModelFactory):
    stripe_token = Sequence(lambda x: f"{x}")

    class Meta:
        model = StripeLocation


class StripeReaderFactory(DjangoModelFactory):
    location = SubFactory(StripeLocationFactory)
    stripe_token = Sequence(lambda x: f"{x}")
    virtual = True

    class Meta:
        model = StripeReader


class DeliverableFactory(DjangoModelFactory):
    name = Sequence(lambda x: "Stage {}".format(x))
    order = SubFactory(OrderFactory)
    invoice = SubFactory(
        InvoiceFactory,
        bill_to=SelfAttribute("..order.buyer"),
        issued_by=SelfAttribute("..order.seller"),
    )
    product = SubFactory(ProductFactory, user=SelfAttribute("..order.seller"))

    class Meta:
        model = Deliverable


class ReferenceFactory(DjangoModelFactory):
    file = SubFactory(AssetFactory)
    owner = SubFactory(UserFactory)

    class Meta:
        model = Reference


class CreditCardTokenFactory(DjangoModelFactory):
    last_four = Sequence(lambda x: "{}".format(x).zfill(4))
    token = Sequence(lambda x: "{}|0000".format(x).zfill(9))
    user = SubFactory(UserFactory)

    class Meta:
        model = CreditCardToken


class RevisionFactory(DjangoModelFactory):
    file = SubFactory(AssetFactory)
    deliverable = SubFactory(DeliverableFactory)
    owner = SelfAttribute("deliverable.order.seller")

    class Meta:
        model = Revision


class TransactionRecordFactory(DjangoModelFactory):
    status = SUCCESS
    remote_ids = Sequence(lambda _: [])
    source = CARD
    destination = ESCROW
    payer = SubFactory(UserFactory)
    payee = SubFactory(UserFactory)
    category = ESCROW_HOLD
    amount = Money("10.00", "USD")

    class Meta:
        model = TransactionRecord


class BankAccountFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    type = BankAccount.CHECKING
    last_four = Sequence(lambda x: "{}".format(x).zfill(4))
    url = Sequence(lambda x: "https://example.com/funding-sources/{}".format(x))

    class Meta:
        model = BankAccount


class PromoFactory(DjangoModelFactory):
    code = Sequence(lambda x: f"CODE{x}")

    class Meta:
        model = Promo


class RatingFactory(DjangoModelFactory):
    target = SubFactory(UserFactory)
    rater = SubFactory(UserFactory)
    stars = 3

    class Meta:
        model = Rating


class LineItemFactory(DjangoModelFactory):
    type = ADD_ON
    invoice = SubFactory(InvoiceFactory)
    priority = 1
    amount = Money("15.00", "USD")
    destination_user = None
    destination_account = ESCROW

    class Meta:
        model = LineItem


class StripeAccountFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    country = "US"

    class Meta:
        model = StripeAccount


class WebhookRecordFactory(DjangoModelFactory):
    secret = "whsec_DvZSxlgF4ujHsFxNAfVJNC5ucgnxZBBF"

    class Meta:
        model = WebhookRecord


class ServicePlanFactory(DjangoModelFactory):
    name = Sequence(lambda x: f"Plan{x}")

    class Meta:
        model = ServicePlan


def add_adjustment(deliverable, amount: Money):
    return LineItem.objects.create(
        invoice=deliverable.invoice,
        destination_user=deliverable.order.seller,
        destination_account=ESCROW,
        amount=amount,
        type=ADD_ON,
    )
