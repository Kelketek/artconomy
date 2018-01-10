from django.contrib.contenttypes.models import ContentType
from factory import Sequence, PostGenerationMethodCall, SubFactory, SelfAttribute, LazyAttribute
from factory.django import DjangoModelFactory, ImageField
from moneyed import Money

from apps.profiles.tests.factories import UserFactory
from apps.sales.models import Order, Product, CreditCardToken, Revision, PaymentRecord


class ProductFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    category = Product.REFERENCE
    expected_turnaround = 3
    revisions = 4
    task_weight = 2
    uploaded_by = SelfAttribute('user')
    price = Money('15.00', 'USD')
    name = Sequence(lambda n: 'Product id {0}'.format(n))
    description = 'Product description'
    file = ImageField(color='blue')

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
    payment_id = Sequence(lambda x: '{}|0000'.format(x).zfill(9))
    user = SubFactory(UserFactory)

    class Meta:
        model = CreditCardToken


class RevisionFactory(DjangoModelFactory):
    file = ImageField(color='blue')
    order = SubFactory(OrderFactory)
    uploaded_by = SelfAttribute('order.seller')

    class Meta:
        model = Revision


class PaymentRecordFactory(DjangoModelFactory):
    card = SubFactory(CreditCardTokenFactory)
    status = PaymentRecord.SUCCESS
    txn_id = Sequence(lambda x: '{}'.format(x))
    response_message = 'Payment happened.'
    response_code = 'PMT'
    source = PaymentRecord.CARD
    payer = SubFactory(UserFactory)
    payee = SubFactory(UserFactory)
    target = SubFactory(OrderFactory)
    type = PaymentRecord.SALE
    amount = Money('10.00', 'USD')

    class Meta:
        model = PaymentRecord