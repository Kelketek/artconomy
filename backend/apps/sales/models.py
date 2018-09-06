import socket
import uuid
from pathlib import Path

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AnonymousUser
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.utils import IntegrityError
from urllib.error import URLError

from authorize import AuthorizeError, Address
from authorize.data import CreditCard
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator, BaseValidator
from django.db.models import Model, CharField, ForeignKey, IntegerField, BooleanField, DateTimeField, ManyToManyField, \
    TextField, SET_NULL, PositiveIntegerField, URLField, CASCADE, DecimalField, Sum, Avg, DateField, EmailField

# Create your models here.
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from django.template import Context, Template
from django.template.loader import get_template
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from moneyed import Money

from apps.lib.models import Comment, Subscription, SALE_UPDATE, ORDER_UPDATE, REVISION_UPLOADED, COMMENT, NEW_PRODUCT, \
    Event, ORDER_TOKEN_ISSUED, EMAIL_SUBJECTS
from apps.lib.abstract_models import ImageModel
from apps.lib.utils import clear_events, MinimumOrZero, recall_notification, require_lock, notify, FakeRequest
from apps.profiles.models import User
from apps.sales.permissions import OrderViewPermission
from apps.sales.apis import sauce
from apps.sales.utils import update_availability


@deconstructible
class MinimumOrZeroValidator(BaseValidator):
    message = _('Ensure this value is greater than or equal to %(limit_value)s, or is zero.')
    code = 'min_or_zero'

    def compare(self, a, b):
        if not a:
            return False
        return a < b


class Product(ImageModel):
    """
    Product on offer by an art seller.
    """

    name = CharField(max_length=250)
    description = CharField(max_length=5000)
    expected_turnaround = DecimalField(
        validators=[MinValueValidator(settings.MINIMUM_TURNAROUND)],
        help_text="Number of days completion is expected to take.",
        max_digits=5, decimal_places=2
    )
    price = MoneyField(
        max_digits=6, decimal_places=2, default_currency='USD',
        db_index=True, validators=[MinimumOrZeroValidator(settings.MINIMUM_PRICE)]
    )
    tags = ManyToManyField('lib.Tag', related_name='products', blank=True)
    tags__max = 200
    hidden = BooleanField(default=False, help_text="Whether this product is visible.", db_index=True)
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='products')
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
    parallel = IntegerField(default=0, blank=True)
    task_weight = IntegerField(
        validators=[MinValueValidator(1)]
    )

    def proto_delete(self, *args, **kwargs):
        if self.order_set.all().count():
            self.active = False
            self.save()
            auto_remove_product_notifiations(Product, self)
        else:
            super().delete(*args, **kwargs)

    def wrap_operation(self, function, always=False, *args, **kwargs):
        do_recall = False
        pk = self.pk
        if self.pk and not always:
            old = Product.objects.get(pk=self.pk)
            if self.hidden and not old.hidden:
                do_recall = True
        result = function(*args, **kwargs)
        if do_recall or always:
            recall_notification(NEW_PRODUCT, self.user, {'product': pk}, unique_data=True)
        return result

    def delete(self, *args, **kwargs):
        return self.wrap_operation(self.proto_delete, always=True, *args, **kwargs)

    def save(self, *args, **kwargs):
        return self.wrap_operation(super().save, *args, **kwargs)

    def notification_display(self, context):
        from .serializers import ProductSerializer
        return ProductSerializer(instance=self).data

    def __str__(self):
        return "{} offered by {} at {}".format(self.name, self.user.username, self.price)


@receiver(post_delete, sender=Product)
def auto_remove_product_notifiations(sender, instance, **kwargs):
    Event.objects.filter(data__product=instance.id).delete()


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
    seller = ForeignKey(settings.AUTH_USER_MODEL, related_name='sales', on_delete=CASCADE)
    buyer = ForeignKey(settings.AUTH_USER_MODEL, related_name='buys', on_delete=CASCADE)
    price = MoneyField(
        max_digits=4, decimal_places=2, default_currency='USD',
        blank=True, null=True, validators=[MinValueValidator(settings.MINIMUM_PRICE)]
    )
    revisions = IntegerField(default=0)
    details = CharField(max_length=5000)
    adjustment = MoneyField(max_digits=4, decimal_places=2, default_currency='USD', blank=True, default=0)
    adjustment_expected_turnaround = DecimalField(default=0, max_digits=5, decimal_places=2)
    adjustment_task_weight = IntegerField(default=0)
    task_weight = IntegerField(default=0)
    escrow_disabled = BooleanField(default=False, db_index=True)
    expected_turnaround = DecimalField(
        validators=[MinValueValidator(settings.MINIMUM_TURNAROUND)],
        help_text="Number of days completion is expected to take.",
        max_digits=5, decimal_places=2,
        default=0
    )
    created_on = DateTimeField(auto_now_add=True, db_index=True)
    disputed_on = DateTimeField(blank=True, null=True, db_index=True)
    started_on = DateTimeField(blank=True, null=True)
    paid_on = DateTimeField(blank=True, null=True, db_index=True)
    dispute_available_on = DateField(blank=True, null=True)
    auto_finalize_on = DateField(blank=True, null=True, db_index=True)
    arbitrator = ForeignKey(settings.AUTH_USER_MODEL, related_name='cases', null=True, blank=True, on_delete=SET_NULL)
    stream_link = URLField(blank=True, default='')
    characters = ManyToManyField('profiles.Character', blank=True)
    private = BooleanField(default=False)
    comments = GenericRelation(
        Comment, related_query_name='order', content_type_field='content_type', object_id_field='object_id'
    )
    subscriptions = GenericRelation('lib.Subscription')

    def total(self):
        price = self.price
        if price is None:
            price = self.product.price
        return price + (self.adjustment or Money(0, 'USD'))

    def notification_serialize(self, context):
        from .serializers import OrderViewSerializer
        return OrderViewSerializer(instance=self, context=context).data

    def notification_display(self, context):
        from .serializers import ProductSerializer
        return ProductSerializer(instance=self.product).data

    def notification_name(self, context):
        request = context['request']
        if request.user == self.seller:
            return "Sale #{}".format(self.id)
        if request.user == self.arbitrator:
            return "Case #{}".format(self.id)
        return "Order #{}".format(self.id)

    def notification_link(self, context):
        request = context['request']
        data = {'params': {'orderID': self.id, 'username': context['request'].user.username}}
        # Doing early returns here so we match name, rather than overwriting.
        if request.user == self.seller:
            data['name'] = 'Sale'
            return data
        if request.user == self.arbitrator:
            data['name'] = 'Case'
            return data
        data['name'] = 'Order'
        return data

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
            email=True,
            type=SALE_UPDATE
        )
        Subscription.objects.create(
            subscriber=instance.buyer,
            content_type=ContentType.objects.get_for_model(model=sender),
            object_id=instance.id,
            email=True,
            type=ORDER_UPDATE,
        )
        Subscription.objects.create(
            subscriber=instance.buyer,
            content_type=ContentType.objects.get_for_model(model=sender),
            object_id=instance.id,
            email=True,
            type=REVISION_UPLOADED
        )
        Subscription.objects.create(
            subscriber=instance.buyer,
            content_type=ContentType.objects.get_for_model(model=sender),
            object_id=instance.id,
            email=True,
            type=COMMENT
        )
        # In the off chance the seller and buyer are the same.
        Subscription.objects.get_or_create(
            subscriber=instance.seller,
            content_type=ContentType.objects.get_for_model(model=sender),
            object_id=instance.id,
            type=COMMENT
        )


WEIGHTED_STATUSES = [Order.IN_PROGRESS, Order.PAYMENT_PENDING, Order.QUEUED]


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


remove_order_events = receiver(pre_delete, sender=Order)(clear_events)


class PlaceholderSale(Model):

    STATUSES = (
        (Order.IN_PROGRESS, 'In Progress'),
        (Order.COMPLETED, 'Completed'),
    )

    title = CharField(max_length=150)
    status = IntegerField(choices=Order.STATUSES, default=Order.IN_PROGRESS, db_index=True)
    seller = ForeignKey(settings.AUTH_USER_MODEL, related_name='placeholder_sales', on_delete=CASCADE)
    task_weight = IntegerField(default=0)
    expected_turnaround = DecimalField(
        validators=[MinValueValidator(settings.MINIMUM_TURNAROUND)],
        help_text="Number of days completion is expected to take.",
        max_digits=5, decimal_places=2
    )
    created_on = DateTimeField(auto_now_add=True, db_index=True)
    description = CharField(max_length=5000)


@transaction.atomic
@require_lock(User, 'ACCESS EXCLUSIVE')
@require_lock(Order, 'ACCESS EXCLUSIVE')
@require_lock(PlaceholderSale, 'ACCESS EXCLUSIVE')
@require_lock(Product, 'ACCESS EXCLUSIVE')
def update_artist_load(sender, instance, **_kwargs):
    result = Order.objects.filter(
        seller=instance.seller, status__in=WEIGHTED_STATUSES
    ).aggregate(base_load=Sum('task_weight'), added_load=Sum('adjustment_task_weight'))
    load = (result['base_load'] or 0) + (result['added_load'] or 0)
    result = PlaceholderSale.objects.filter(
        seller=instance.seller, status__in=WEIGHTED_STATUSES
    ).aggregate(load=Sum('task_weight'))
    load += (result['load'] or 0)
    if isinstance(instance, Order):
        instance.product.parallel = Order.objects.filter(product=instance.product, status__in=WEIGHTED_STATUSES).count()
        instance.product.save()
    # Availability update could be recursive, so get the latest version of the user.
    seller = User.objects.get(id=instance.seller.id)
    update_availability(seller, load, seller.commissions_disabled)


order_load_check = receiver(post_save, sender=Order, dispatch_uid='load')(update_artist_load)
# No need for delete check-- orders are only ever archived, not deleted.
placeholder_load_check = receiver(post_save, sender=PlaceholderSale, dispatch_uid='load')(update_artist_load)
placeholder_load_check_delete = receiver(
    post_delete, sender=PlaceholderSale, dispatch_uid='load'
)(update_artist_load)


@transaction.atomic
@require_lock(User, 'ACCESS EXCLUSIVE')
@require_lock(Order, 'ACCESS EXCLUSIVE')
@require_lock(PlaceholderSale, 'ACCESS EXCLUSIVE')
@require_lock(Product, 'ACCESS EXCLUSIVE')
def update_product_availability(sender, instance, **kwargs):
    update_availability(instance.user, instance.user.load, instance.user.commissions_disabled)


@transaction.atomic
@require_lock(User, 'ACCESS EXCLUSIVE')
@require_lock(Order, 'ACCESS EXCLUSIVE')
@require_lock(PlaceholderSale, 'ACCESS EXCLUSIVE')
@require_lock(Product, 'ACCESS EXCLUSIVE')
def update_user_availability(sender, instance, **kwargs):
    update_availability(instance, instance.load, instance.commissions_disabled)


product_availability_check_save = receiver(
    post_save, sender=Product, dispatch_uid='load'
)(update_product_availability)
product_availability_check_delete = receiver(
    post_delete, sender=Product, dispatch_uid='load'
)(update_product_availability)

user_availability_check_save = receiver(
    post_save, sender=User, dispatch_uid='load'
)(update_user_availability)


class Rating(Model):
    """
    An individual star rating for a category.
    """
    stars = IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comments = CharField(max_length=1000, blank=True, default='')
    object_id = PositiveIntegerField(null=True, blank=True, db_index=True)
    content_type = ForeignKey(ContentType, on_delete=SET_NULL, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    target = ForeignKey('profiles.User', related_name='ratings', on_delete=CASCADE)
    rater = ForeignKey('profiles.User', related_name='ratings_received', on_delete=CASCADE)
    created_on = DateTimeField(auto_now_add=True, db_index=True)


@receiver(post_save, sender=Rating)
def tabulate_stars(sender, instance, **_kwargs):
    instance.target.stars = instance.target.ratings.all().aggregate(Avg('stars'))['stars__avg']
    instance.target.save()


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
    created_on = DateTimeField(auto_now_add=True, db_index=True)

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
        except (AuthorizeError, URLError, socket.timeout):
            # There may be older cards which aren't truly in place anyway.
            # Better to not crash when they're removed.
            pass
        if self.user.primary_card == self:
            self.user.primary_card = None
            cards = self.user.credit_cards.filter(active=True).order_by('-created_on')
            if cards:
                self.user.primary_card = cards[0]
            self.user.save()
        self.active = False
        self.save()

    @classmethod
    def authorize_card(cls, first_name, last_name, number, cvv, exp_year, exp_month, country, zip_code):
        card = CreditCard(
            card_number=number,
            exp_year=exp_year,
            exp_month=exp_month,
            cvv=cvv,
            first_name=first_name,
            last_name=last_name
        )

        card_type = CreditCardToken.TYPE_TRANSLATION[card.card_type]

        address = Address(street='', city='', state='', zip_code=zip_code, country=country)
        compiled_card = sauce.card(card, address)
        # Send along an authorization containing the CVV to verify the card.
        compiled_card.auth(1)
        saved_card = compiled_card.save()

        return saved_card, card_type, number[:4]

    @classmethod
    def create(
            cls, user, first_name, last_name, card_number, cvv, exp_year, exp_month, country, zip_code, make_primary
    ):

        saved_card, card_type, last_four = cls.authorize_card(
            first_name, last_name, card_number, cvv, exp_year, exp_month, country, zip_code
        )

        token = cls(
            user=user, card_type=card_type, last_four=card_number[:4],
            payment_id=saved_card.uid, cvv_verified=True)

        token.save()
        if (not token.user.primary_card) or make_primary:
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
    DISBURSEMENT_SENT = 201
    DISBURSEMENT_RETURNED = 202
    REFUND = 204
    TRANSFER = 205

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
        (DISBURSEMENT_SENT, 'Initiated Disbersement'),
        (DISBURSEMENT_RETURNED, 'Disbursement completed'),
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
    amount = MoneyField(max_digits=6, decimal_places=2, default_currency='USD')
    txn_id = CharField(max_length=40)
    created_on = DateTimeField(auto_now_add=True, db_index=True)
    response_code = CharField(max_length=10)
    response_message = TextField()
    # Needed for async checks against ACH transfers. Set false when we need to query periodically about the status
    # of this transfer.
    # Also used for checking if an escrow payment has been released.
    finalized = BooleanField(default=True, db_index=True)
    # Used to manage things like delays on the bank side so our account does not overdraw.
    finalize_on = DateField(default=None, db_index=True, null=True)
    object_id = PositiveIntegerField(null=True, blank=True, db_index=True)
    content_type = ForeignKey(ContentType, on_delete=SET_NULL, null=True, blank=True)
    target = GenericForeignKey('content_type', 'object_id')
    note = TextField(default='', blank=True)

    def __str__(self):
        return "{}{} from {} to {}".format(
            '' if self.status == self.SUCCESS else 'FAILED: ',
            self.amount,
            self.payer or '(Artconomy)',
            self.payee or '(Artconomy)',
        )

    def refund_card(self, amount=None):
        if amount:
            note = 'Refund, minus fees.'
        else:
            note = ''
        amount = amount or self.amount
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
            amount=amount,
            response_message="Failed when contacting payment processor.",
            note=note
        )
        transaction = sauce.transaction(self.txn_id)
        try:
            response = transaction.credit(self.card.last_four, amount.amount)
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

    def refund(self, amount=None):
        if self.status != PaymentRecord.SUCCESS:
            raise ValueError("Cannot refund a failed transaction.")
        if self.source == PaymentRecord.CARD:
            return self.refund_card(amount)
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


class BankAccount(Model):
    CHECKING = 0
    SAVINGS = 1
    ACCOUNT_TYPES = (
        (CHECKING, 'Checking'),
        (SAVINGS, 'Savings')
    )
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='banks')
    url = URLField()
    last_four = CharField(max_length=4)
    type = IntegerField(choices=ACCOUNT_TYPES)
    deleted = BooleanField(default=False)

    def notification_serialize(self, context):
        from .serializers import BankAccountSerializer
        return BankAccountSerializer(instance=self).data


@receiver(post_save, sender=BankAccount)
def ensure_shield(sender, instance, created=False, **_kwargs):
    if not created:
        return
    instance.user.escrow_disabled = False
    instance.user.save()


class CharacterTransfer(Model):
    NEW = 0
    COMPLETED = 1
    CANCELLED = 2
    REJECTED = 3
    STATUSES = (
        (NEW, 'New'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
        (REJECTED, 'Rejected'),
    )
    status = IntegerField(choices=STATUSES, db_index=True, default=NEW)
    created_on = DateTimeField(auto_now_add=True)
    seller = ForeignKey('profiles.User', on_delete=CASCADE, related_name='character_transfers_outbound')
    buyer = ForeignKey('profiles.User', on_delete=CASCADE, related_name='character_transfers_inbound')
    character = ForeignKey('profiles.Character', on_delete=SET_NULL, null=True, blank=True)
    saved_name = CharField(blank=True, default='', max_length=150)
    include_assets = BooleanField(default=False)
    price = MoneyField(
        max_digits=6, decimal_places=2, default_currency='USD',
        db_index=True, validators=[MinimumOrZero(settings.MINIMUM_PRICE)]
    )

    def save(self, *args, **kwargs):
        if self.character.transfer and self.character.transfer != self:
            raise IntegrityError("There is already a transfer for this character.")
        super().save()

    def notification_serialize(self, context):
        from apps.sales.serializers import CharacterTransferSerializer
        return CharacterTransferSerializer(instance=self, context=context).data


@receiver(post_save, sender=CharacterTransfer)
def auto_set_transfer(sender, instance, **_kwargs):
    if instance.status == CharacterTransfer.NEW:
        instance.character.transfer = instance
        instance.character.save()
    else:
        instance.character.transfer = None
        instance.character.save()


def mini_key():
    return str(uuid.uuid4())[:8]


def tomorrow():
    return timezone.now() + relativedelta(days=1)


class OrderToken(Model):
    product = ForeignKey(Product, on_delete=CASCADE, related_name='tokens')
    activation_code = CharField(max_length=8, default=mini_key)
    expires_on = DateTimeField(db_index=True, default=tomorrow)
    email = EmailField()

    def notification_serialize(self, context):
        from .serializers import OrderTokenSerializer
        return OrderTokenSerializer(instance=self, context=context).data


@receiver(post_save, sender=OrderToken)
def send_token_info(sender, instance, created=False, **kwargs):
    if not created:
        return
    try:
        user = User.objects.get(email__iexact=instance.email)
        notify(ORDER_TOKEN_ISSUED, user, data={'order_token': instance.id, 'product': instance.product.id})
    except User.DoesNotExist:
        from apps.sales.serializers import OrderTokenSerializer
        template_path = Path(settings.BACKEND_ROOT) / 'templates' / 'notifications' / '31_order_token_issued.html'
        subject = EMAIL_SUBJECTS[ORDER_TOKEN_ISSUED]
        req_context = {'request': FakeRequest(AnonymousUser())}
        ctx = {
            'data': {
                'token': OrderTokenSerializer(instance=instance, context=req_context).data
            }
        }
        subject = Template(subject).render(Context(ctx))
        to = [instance.email]
        from_email = settings.DEFAULT_FROM_EMAIL
        message = get_template(template_path).render(ctx)
        msg = EmailMessage(subject, message, to=to, from_email=from_email)
        msg.content_subtype = 'html'
        msg.send()


@receiver(post_delete, sender=OrderToken)
def revoke_token_info(sender, instance, **kwargs):
    Event.objects.filter(data__order_token=instance.id).delete()
