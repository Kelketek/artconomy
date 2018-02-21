from urllib.error import URLError

from authorize import AuthorizeError, Address
from authorize.data import CreditCard
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, CharField, ForeignKey, IntegerField, BooleanField, DateTimeField, ManyToManyField, \
    TextField, SET_NULL, PositiveIntegerField, URLField, CASCADE

# Create your models here.
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from djmoney.models.fields import MoneyField
from moneyed import Money

from apps.lib.models import Comment, Subscription, SALE_UPDATE, ORDER_UPDATE, REVISION_UPLOADED, COMMENT
from apps.lib.abstract_models import ImageModel
from apps.sales.permissions import OrderViewPermission
from apps.sales.sauce import sauce


class Product(ImageModel):
    """
    Product on offer by an art seller.
    """
    SKETCH = 0
    FULLBODY = 1
    REFERENCE = 2
    BADGE = 3
    ICON = 4
    ICON_SET = 5
    HEADSHOT = 6
    CHIBI = 7
    GAME_ASSET = 8
    THREE_D = 9
    ANIMATION_2D = 10
    ANIMATION_3D = 11
    STORY_SHORT = 12
    STORY_LONG = 13
    MUSIC = 14
    OTHER = 15

    name = CharField(max_length=250)
    description = CharField(max_length=5000)
    expected_turnaround = IntegerField(
        validators=[MinValueValidator(1)], help_text="Number of days completion is expected to take."
    )
    price = MoneyField(
        max_digits=6, decimal_places=2, default_currency='USD',
        db_index=True, validators=[MinValueValidator(settings.MINIMUM_PRICE)]
    )
    tags = ManyToManyField('lib.Tag', related_name='products', blank=True)
    tags__max = 200
    hidden = BooleanField(default=False, help_text="Whether this product is visible.", db_index=True)
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    created_on = DateTimeField(auto_now_add=True)
    shippable = BooleanField(default=False)
    active = BooleanField(default=True, db_index=True)
    revisions = IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    max_parallel = IntegerField(
        validators=[MinValueValidator(0)], help_text="How many of these you are willing to have in your "
                                                     "backlog at one time.",
        blank=True,
        default=0
    )
    task_weight = IntegerField(
        validators=[MinValueValidator(1)]
    )

    def delete(self, using=None, keep_parents=False):
        if self.order_set.all().count():
            self.active = False
            self.save()
        else:
            super().delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        return "{} offered by {} at {}".format(self.name, self.user.username, self.price)


class Auction(Model):
    """
    YCH or other Auction. One-off, not a repeatable product
    """

    OPEN = 1
    CLOSED = 2
    CANCELLED = 3

    status = IntegerField(
        choices=(
            (OPEN, 'Open'),
            (CLOSED, 'Closed'),
            (CANCELLED, 'Cancelled'),
        )
    )
    created_on = DateTimeField(auto_now_add=True)
    ends_on = DateTimeField()


class Placeholder(Model):
    """
    Multiple placeholders per auction can be bid on.
    """
    OPEN = 1
    CLOSED = 2

    STATUSES = (
        (OPEN, 'Open'),
        (CLOSED, 'Closed')
    )

    status = IntegerField(choices=STATUSES, db_index=True)
    auction = ForeignKey('Auction', on_delete=CASCADE)
    description = CharField(max_length=2000)
    buy_now_price = MoneyField(
        max_digits=4, decimal_places=2, default_currency='USD', blank=True, null=True, db_index=True
    )
    start_price = MoneyField(
        max_digits=4, decimal_places=2, default_currency='USD', default=5, validators=[MinValueValidator(5)]
    )
    reserve_price = MoneyField(
        max_digits=4, decimal_places=2, default_currency='USD', default=5, validators=[MinValueValidator(5)]
    )


class Bid(Model):
    """
    A bid placed by a user on an Auction.
    """
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    placeholder = ForeignKey('Placeholder', on_delete=CASCADE)
    bid = MoneyField(max_digits=4, decimal_places=2, default_currency='USD', db_index=True)
    max_bid = MoneyField(max_digits=4, decimal_places=2, default_currency='USD', db_index=True)
    created_on = DateTimeField(auto_now_add=True)


class Order(Model):
    """
    Record of Order
    """
    NEW = 1
    PAYMENT_PENDING = 2
    QUEUED = 3
    IN_PROGRESS = 4
    REVIEW = 5
    CANCELLED = 6
    DISPUTED = 7
    COMPLETED = 8
    REFUNDED = 9

    STATUSES = (
        (NEW, 'New'),
        (PAYMENT_PENDING, 'Payment Pending'),
        (QUEUED, 'Queued'),
        (IN_PROGRESS, 'In Progress'),
        (REVIEW, 'Review'),
        (CANCELLED, 'Cancelled'),
        (DISPUTED, 'Disputed'),
        (COMPLETED, 'Completed'),
        (REFUNDED, 'Refunded'),
    )

    comment_permissions = [OrderViewPermission]

    status = IntegerField(choices=STATUSES, default=NEW, db_index=True)
    product = ForeignKey('Product', null=True, blank=True, on_delete=CASCADE)
    auction = ForeignKey('Auction', null=True, blank=True, on_delete=CASCADE)
    seller = ForeignKey(settings.AUTH_USER_MODEL, related_name='sales', on_delete=CASCADE)
    buyer = ForeignKey(settings.AUTH_USER_MODEL, related_name='buys', on_delete=CASCADE)
    price = MoneyField(
        max_digits=4, decimal_places=2, default_currency='USD',
        blank=True, null=True, validators=[MinValueValidator(settings.MINIMUM_PRICE)]
    )
    revisions = IntegerField(default=0)
    details = CharField(max_length=5000)
    adjustment = MoneyField(max_digits=4, decimal_places=2, default_currency='USD', blank=True, default=0)
    created_on = DateTimeField(auto_now_add=True, db_index=True)
    disputed_on = DateTimeField(blank=True, null=True, db_index=True)
    arbitrator = ForeignKey(settings.AUTH_USER_MODEL, related_name='cases', null=True, blank=True, on_delete=SET_NULL)
    stream_link = URLField(blank=True, default='')
    characters = ManyToManyField('profiles.Character')
    private = BooleanField(default=False)
    comments = GenericRelation(
        Comment, related_query_name='order', content_type_field='content_type', object_id_field='object_id'
    )

    def total(self):
        price = self.price
        if price is None:
            price = self.product.price
        return price + (self.adjustment or Money(0, 'USD'))

    def notification_serialize(self):
        from .serializers import OrderViewSerializer
        return OrderViewSerializer(instance=self).data

    def __str__(self):
        return "#{} {} for {} by {}".format(self.id, self.product.name, self.buyer, self.seller)

    class Meta:
        ordering = ['created_on']


@receiver(post_save, sender=Order)
def auto_subscribe_order(sender, instance, created=False, **_kwargs):
    if created:
        Subscription.objects.create(
            subscriber=instance.seller,
            content_type=ContentType.objects.get_for_model(model=sender),
            object_id=instance.id,
            type=SALE_UPDATE
        )
        Subscription.objects.create(
            subscriber=instance.buyer,
            content_type=ContentType.objects.get_for_model(model=sender),
            object_id=instance.id,
            type=ORDER_UPDATE
        )
        Subscription.objects.create(
            subscriber=instance.buyer,
            content_type=ContentType.objects.get_for_model(model=sender),
            object_id=instance.id,
            type=REVISION_UPLOADED
        )
        Subscription.objects.create(
            subscriber=instance.buyer,
            content_type=ContentType.objects.get_for_model(model=sender),
            object_id=instance.id,
            type=COMMENT
        )
        Subscription.objects.create(
            subscriber=instance.seller,
            content_type=ContentType.objects.get_for_model(model=sender),
            object_id=instance.id,
            type=COMMENT
        )


@receiver(post_delete, sender=Order)
def auto_remove_order(sender, instance, **_kwargs):
    Subscription.objects.filter(
        subscriber=instance.seller,
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type=SALE_UPDATE
    ).delete()
    Subscription.objects.filter(
        subscriber=instance.buyer,
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type=ORDER_UPDATE
    ).delete()
    Subscription.objects.filter(
        subscriber=instance.buyer,
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type=REVISION_UPLOADED
    ).delete()
    Subscription.objects.filter(
        subscriber=instance.buyer,
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type=COMMENT
    ).delete()
    Subscription.objects.filter(
        subscriber=instance.seller,
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type=COMMENT
    ).delete()


class RatingSet(Model):
    BUYER = 1
    SELLER = 2

    TYPES = (
        (BUYER, 'Buyer'),
        (SELLER, 'Seller')
    )

    RATE_MAPPING = {
        BUYER: [
            ''
        ]
    }

    rater = ForeignKey(settings.AUTH_USER_MODEL, related_name='submitted_ratings', on_delete=CASCADE)
    target = ForeignKey(settings.AUTH_USER_MODEL, related_name='received_ratings', on_delete=CASCADE)
    transaction_type = IntegerField(choices=TYPES)


class Rating(Model):
    """
    An individual star rating for a category.
    """
    stars = IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    category = CharField(max_length=100, db_index=True)
    rating_set = ForeignKey('RatingSet', on_delete=CASCADE)
    comments = CharField(max_length=1000, blank=True, default='')


class CreditCardToken(Model):
    """
    Card tokens are stored based on Authorize.net's API. We don't store full card data to avoid issues
    with PCI compliance.
    """
    VISA_TYPE = 1
    MASTERCARD_TYPE = 2
    AMEX_TYPE = 3
    DISCOVER_TYPE = 4
    DINERS_TYPE = 5

    CARD_TYPES = (
        (VISA_TYPE, 'Visa'),
        (MASTERCARD_TYPE, 'Mastercard'),
        (AMEX_TYPE, 'American Express'),
        (DISCOVER_TYPE, 'Discover'),
        (DINERS_TYPE, "Diners Club"))

    ACTIVE_STATUS = 10

    DELETED_STATUS = 20

    CARD_STATUS = (
        (ACTIVE_STATUS, 'Active'),
        (DELETED_STATUS, 'Removed/Deleted'))

    # Authorizesauce uses these constants to refer to the card types.
    TYPE_TRANSLATION = {
        'amex': AMEX_TYPE,
        'discover': DISCOVER_TYPE,
        'mc': MASTERCARD_TYPE,
        'diners': DINERS_TYPE,
        'visa': VISA_TYPE
    }

    user = ForeignKey(settings.AUTH_USER_MODEL, related_name='credit_cards', on_delete=CASCADE)
    card_type = IntegerField(choices=CARD_TYPES, default=VISA_TYPE)
    last_four = CharField(max_length=4)
    payment_id = CharField(max_length=50)
    active = BooleanField(default=True, db_index=True)
    cvv_verified = BooleanField(default=False, db_index=True)

    def __init__(self, *args, **kwargs):
        super(CreditCardToken, self).__init__(*args, **kwargs)
        self.api = None
        self._get_sauce()

    def __unicode__(self):
        return "%s ending in %s (%s)" % (
            self.get_card_type_display(), self.last_four,
            "" if self.active else " (Deleted)")

    def _get_sauce(self):
        if self.payment_id:
            self.api = sauce.saved_card(self.payment_id)

    def save(self, *args, **kwargs):
        super(CreditCardToken, self).save(*args, **kwargs)
        self._get_sauce()

    def delete(self, *args, **kwargs):
        """
        Remove a card and its existence from Authorize.net.

        We will not allow this to be done in any way but the most deliberate manner,
        since transaction records will exist for the card. So, instead, we raise an exception.

        To mark a card as deleted properly, use the mark_delete function.
        """
        raise RuntimeError("Credit card tokens are critical for historical billing information.")

    def mark_deleted(self):
        """
        Mark a card as deleted. Deleted cards are hidden away from the user, but kept for
        historical accounting purposes.
        """
        try:
            self.api.delete()
        except (AuthorizeError, URLError):
            # There may be older cards which aren't truly in place anyway.
            # Better to not crash when they're removed.
            pass
        if self.user.primary_card == self:
            self.user.primary_card = None
            self.user.save()
        self.active = False
        self.save()

    @classmethod
    def authorize_card(cls, first_name, last_name, number, exp_year, exp_month, country, zip_code):
        card = CreditCard(
            card_number=number,
            exp_year=exp_year,
            exp_month=exp_month,
            cvv='000',  # We won't be validating a CVV until at least the first transaction.
            first_name=first_name,
            last_name=last_name
        )

        card_type = CreditCardToken.TYPE_TRANSLATION[card.card_type]

        address = Address(street='', city='', state='', zip_code=zip_code, country=country)
        saved_card = sauce.card(card, address).save()

        return saved_card, card_type, number[:4]

    @classmethod
    def create(cls, user, first_name, last_name, card_number, exp_year, exp_month, country, zip_code):

        saved_card, card_type, last_four = cls.authorize_card(
            first_name, last_name, card_number, exp_year, exp_month, country, zip_code
        )

        token = cls(
            user=user, card_type=card_type, last_four=card_number[:4],
            payment_id=saved_card.uid)

        token.save()
        if not token.user.primary_card:
            token.user.primary_card = token
            token.user.save()
        return token


class PaymentRecord(Model):
    """
    Model for tracking the movement of money.
    """
    SUCCESS = 0
    FAILURE = 1

    CARD = 100
    ACH = 101
    ESCROW = 102
    ACCOUNT = 103

    SALE = 200
    DISBURSEMENT = 201
    REFUND = 202
    TRANSFER = 203

    STATUSES = (
        (SUCCESS, 'SUCCESS'),
        (FAILURE, 'FAILURE'),
    )

    PAYMENT_SOURCES = (
        (CARD, 'Credit Card'),
        (ACH, 'Bank Transfer'),
        (ESCROW, 'Escrow Holdings'),
        (ACCOUNT, 'Cash Holdings'),
    )

    TYPES = (
        (SALE, 'Sale of good or service'),
        (TRANSFER, 'Internal Transfer'),
        (DISBURSEMENT, 'Disbursement to account'),
        (REFUND, 'Refund')
    )

    source = IntegerField(choices=PAYMENT_SOURCES, db_index=True)
    status = IntegerField(choices=STATUSES, db_index=True)
    type = IntegerField(choices=TYPES, db_index=True)
    card = ForeignKey(CreditCardToken, null=True, blank=True, on_delete=SET_NULL)
    payer = ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='debits', on_delete=CASCADE)
    payee = ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='credits', on_delete=CASCADE)
    escrow_for = ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, related_name='escrow_holdings', on_delete=CASCADE
    )
    amount = MoneyField(max_digits=4, decimal_places=2, default_currency='USD')
    txn_id = CharField(max_length=40)
    created_on = DateTimeField(auto_now_add=True, db_index=True)
    response_code = CharField(max_length=10)
    response_message = TextField()
    object_id = PositiveIntegerField(null=True, blank=True, db_index=True)
    content_type = ForeignKey(ContentType, on_delete=SET_NULL, null=True, blank=True)
    target = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return "{}{} from {} to {}".format(
            '' if self.status == self.SUCCESS else 'FAILED: ',
            self.amount,
            self.payer or '(Artconomy)',
            self.payee or '(Artconomy)',
        )

    def refund_card(self):
        if self.escrow_for:
            source = PaymentRecord.ESCROW
        else:
            source = PaymentRecord.ACCOUNT
        record = PaymentRecord(
            source=source,
            status=PaymentRecord.FAILURE,
            type=PaymentRecord.REFUND,
            payer=self.payee,
            payee=self.payer,
            content_type=self.content_type,
            object_id=self.object_id,
            amount=self.amount,
            response_message="Failed when contacting Authorize.net."
        )
        transaction = sauce.transaction(self.txn_id)
        try:
            response = transaction.credit(self.card.last_four, self.amount.amount)
            record.txn_id = response.uid
            record.status = PaymentRecord.SUCCESS
            record.save()
        except Exception as err:
            from apps.sales.utils import translate_authnet_error
            record.response_message = translate_authnet_error(err)
            record.save()
        return record

    def refund_account(self):
        raise NotImplementedError("Account refunds are not yet implemented.")

    def refund(self):
        if self.status != PaymentRecord.SUCCESS:
            raise ValueError("Cannot refund a failed transaction.")
        if self.source == PaymentRecord.CARD:
            return self.refund_card()
        elif self.source == PaymentRecord.ACH:
            raise NotImplementedError("ACH Refunds are not implemented.")
        elif self.source == PaymentRecord.ESCROW:
            raise ValueError(
                "Cannot refund an escrow sourced payment. Are you sure you grabbed the right payment object?"
            )
        else:
            return self.refund_account()


class Revision(ImageModel):
    order = ForeignKey(Order, on_delete=CASCADE)

    class Meta:
        ordering = ['created_on']
