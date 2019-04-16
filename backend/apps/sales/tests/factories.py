from factory import Sequence, SubFactory, SelfAttribute
from factory.django import DjangoModelFactory
from moneyed import Money

from apps.lib.tests.factories import AssetFactory
from apps.profiles.tests.factories import UserFactory
from apps.sales.models import (
    Order, Product, CreditCardToken, Revision, BankAccount,
    Promo, Rating,
    TransactionRecord)


class ProductFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    expected_turnaround = 3
    revisions = 4
    task_weight = 2
    owner = SelfAttribute('user')
    price = Money('15.00', 'USD')
    name = Sequence(lambda n: 'Product {0}'.format(n))
    description = 'Product description'
    file = SubFactory(AssetFactory)

    class Meta:
        model = Product


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    buyer = SubFactory(UserFactory)
    seller = SelfAttribute('product.user')
    product = SubFactory(ProductFactory)


class CreditCardTokenFactory(DjangoModelFactory):
    last_four = Sequence(lambda x: '{}'.format(x).zfill(4))
    token = Sequence(lambda x: '{}|0000'.format(x).zfill(9))
    user = SubFactory(UserFactory)

    class Meta:
        model = CreditCardToken


class RevisionFactory(DjangoModelFactory):
    file = SubFactory(AssetFactory)
    order = SubFactory(OrderFactory)
    owner = SelfAttribute('order.seller')

    class Meta:
        model = Revision


class TransactionRecordFactory(DjangoModelFactory):
    status = TransactionRecord.SUCCESS
    remote_id = Sequence(lambda x: '{}'.format(x))
    source = TransactionRecord.CARD
    destination = TransactionRecord.ESCROW
    payer = SubFactory(UserFactory)
    payee = SubFactory(UserFactory)
    category = TransactionRecord.ESCROW_HOLD
    amount = Money('10.00', 'USD')

    class Meta:
        model = TransactionRecord


class BankAccountFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    type = BankAccount.CHECKING
    last_four = Sequence(lambda x: '{}'.format(x).zfill(4))
    url = Sequence(lambda x: 'https://example.com/funding-sources/{}'.format(x))

    class Meta:
        model = BankAccount


class PromoFactory(DjangoModelFactory):
    code = Sequence(lambda x: f'CODE{x}')

    class Meta:
        model = Promo


class RatingFactory(DjangoModelFactory):
    target = SubFactory(UserFactory)
    rater = SubFactory(UserFactory)
    stars = 3

    class Meta:
        model = Rating