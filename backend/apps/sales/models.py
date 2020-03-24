import re
from contextlib import contextmanager
from dataclasses import dataclass
from decimal import Decimal
from typing import Union, List
from uuid import uuid4
from warnings import warn

from django.db import transaction, models, IntegrityError

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import (
    Model, CharField, ForeignKey, IntegerField, BooleanField, DateTimeField, ManyToManyField,
    SET_NULL, PositiveIntegerField, URLField, CASCADE, DecimalField, Avg, DateField, EmailField, Sum,
    UUIDField,
    TextField,
    SlugField,
    PROTECT)

# Create your models here.
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from djmoney.models.fields import MoneyField
from moneyed import Money
from short_stuff import gen_unique_id, slugify

from apps.lib.models import Comment, Subscription, SALE_UPDATE, ORDER_UPDATE, REVISION_UPLOADED, COMMENT, NEW_PRODUCT, \
    Event, ref_for_instance
from apps.lib.abstract_models import ImageModel, thumbnail_hook, HitsMixin, RATINGS, GENERAL
from apps.lib.utils import (
    clear_events, recall_notification, require_lock,
    send_transaction_email,
    demark)
from apps.profiles.models import User, ArtistProfile
from apps.sales.authorize import create_customer_profile, create_card, AddressInfo, CardInfo, \
    refund_transaction
from apps.sales.permissions import OrderViewPermission
from apps.sales.utils import update_availability, reckon_lines
from shortcuts import disable_on_load


class Product(ImageModel, HitsMixin):
    """
    Product on offer by an art seller.
    """
    name = CharField(max_length=250, db_index=True)
    description = CharField(max_length=5000)
    expected_turnaround = DecimalField(
        validators=[MinValueValidator(settings.MINIMUM_TURNAROUND)],
        help_text="Number of days completion is expected to take.",
        max_digits=5, decimal_places=2
    )
    base_price = MoneyField(
        max_digits=6, decimal_places=2, default_currency='USD',
        db_index=True, null=True,
    )
    # Cached value from get_starting_price, useful for searching.
    starting_price = MoneyField(
        max_digits=6, decimal_places=2, default_currency='USD',
        db_index=True, null=True, blank=True,
    )
    tags = ManyToManyField('lib.Tag', related_name='products', blank=True)
    tags__max = 200
    hidden = BooleanField(default=False, help_text="Whether this product is visible.", db_index=True)
    user = ForeignKey(User, on_delete=CASCADE, related_name='products')
    primary_submission = ForeignKey(
        'profiles.Submission', on_delete=SET_NULL, related_name='featured_sample_for', null=True,
        blank=True,
    )
    samples = ManyToManyField('profiles.Submission', related_name='is_sample_for', blank=True)
    created_on = DateTimeField(default=timezone.now, db_index=True)
    edited_on = DateTimeField(db_index=True, auto_now=True)
    shippable = BooleanField(default=False)
    active = BooleanField(default=True, db_index=True)
    available = BooleanField(default=True, db_index=True)
    featured = BooleanField(default=False, db_index=True)
    table_product = BooleanField(default=False, db_index=True)
    track_inventory = BooleanField(default=False, db_index=True)
    revisions = IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    max_parallel = IntegerField(
        validators=[MinValueValidator(0)], help_text="How many of these you are willing to have in your "
                                                     "backlog at one time.",
        blank=True,
        default=0
    )
    parallel = IntegerField(default=0, blank=True)
    hit_counter = GenericRelation(
        'hitcount.HitCount', object_id_field='object_pk',
        related_query_name='hit_counter')
    task_weight = IntegerField(
        validators=[MinValueValidator(1)]
    )

    @property
    def preview_link(self):
        if not self.primary_submission:
            return '/static/images/default-avatar.png'
        return self.primary_submission.preview_link

    def can_reference_asset(self, user):
        return user == self.user

    @property
    def line_items(self) -> List['LineItemSim']:
        lines = [
            LineItemSim(amount=self.base_price, priority=0, type=BASE_PRICE),
        ]
        if self.table_product:
            lines.extend([
                LineItemSim(
                    percentage=settings.TABLE_PERCENTAGE_FEE, priority=300,
                    amount=Money(settings.TABLE_STATIC_FEE, 'USD'),
                    type=TABLE_SERVICE, cascade_percentage=True,
                    cascade_amount=False,
                ),
                LineItemSim(
                    percentage=settings.TABLE_TAX, priority=600, type=TAX, cascade_percentage=True, cascade_amount=True,
                    back_into_percentage=True,
                ),
            ])
        elif self.base_price and not self.escrow_disabled:
            lines.extend([
                LineItemSim(
                    amount=Money(settings.SERVICE_STATIC_FEE, 'USD'),
                    percentage=settings.SERVICE_PERCENTAGE_FEE, priority=200,
                    type=SHIELD,
                    cascade_percentage=True,
                    cascade_amount=True,
                ),
                LineItemSim(
                    amount=Money(settings.PREMIUM_STATIC_BONUS, 'USD'),
                    percentage=settings.PREMIUM_PERCENTAGE_BONUS, priority=200,
                    type=BONUS,
                    cascade_percentage=True,
                    cascade_amount=True,
                ),
            ])
        return lines

    def get_starting_price(self) -> Money:
        return reckon_lines(self.line_items)

    @property
    def escrow_disabled(self):
        if not self.base_price:
            return True
        if self.table_product:
            return False
        return self.user.artist_profile.escrow_disabled

    @property
    def preview_description(self) -> str:
        price = self.starting_price
        if price:
            price = str(price).replace('US$', '$')
        price = f'[Starts at {price or "FREE"}] - '
        return price + demark(self.description)

    def proto_delete(self, *args, **kwargs):
        self.samples.clear()
        if self.order_set.all().count():
            self.active = False
            self.save()
            auto_remove_product_notifications(Product, self)
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
        self.starting_price = self.get_starting_price()
        self.owner = self.user
        result = self.wrap_operation(super().save, *args, **kwargs)
        if self.primary_submission:
            self.samples.add(self.primary_submission)
        return result

    # noinspection PyUnusedLocal
    def notification_display(self, context: dict) -> dict:
        from .serializers import ProductSerializer
        return ProductSerializer(instance=self, context=context).data['primary_submission']

    def __str__(self):
        return "{} offered by {} at {}".format(self.name, self.user.username, self.base_price)


# noinspection PyUnusedLocal
@receiver(post_delete, sender=Product)
@disable_on_load
def auto_remove_product_notifications(sender, instance, **kwargs):
    Event.objects.filter(data__product=instance.id).delete()
    Event.objects.filter(object_id=instance.id, content_type=ContentType.objects.get_for_model(instance)).delete()


product_thumbnailer = receiver(post_save, sender=Product)(thumbnail_hook)


@receiver(post_save, sender=Product)
@disable_on_load
def apply_inventory(sender, instance, **kwargs):
    if instance.track_inventory:
        InventoryTracker.objects.get_or_create(product=instance)
    else:
        InventoryTracker.objects.filter(product=instance).delete()


class InventoryTracker(Model):
    product = models.OneToOneField('Product', on_delete=CASCADE, related_name='inventory')
    count = models.IntegerField(default=0, db_index=True)


class InventoryError(IntegrityError):
    """
    Used when a product is out of stock.
    """


@contextmanager
def inventory_change(product: Union['Product', None], delta: int = -1):
    if product is None:
        # Nothing to do.
        yield
        return
    with transaction.atomic():
        tracker = InventoryTracker.objects.select_for_update().filter(product=product).first()
        if not tracker:
            # Nothing to do here, carry on.
            yield
            return
        tracker.count += delta
        if tracker.count < 0:
            raise InventoryError()
        # Should return the row, locked for editing. When the block this function is used in is exited, should
        # release the lock.
        yield tracker.count
        tracker.save()


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

    PAID_STATUSES = (QUEUED, IN_PROGRESS, REVIEW, REFUNDED, COMPLETED)

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

    preserve_comments = True
    comment_permissions = [OrderViewPermission]

    status = IntegerField(choices=STATUSES, default=NEW, db_index=True)
    product = ForeignKey('Product', null=True, blank=True, on_delete=SET_NULL)
    seller = ForeignKey(User, related_name='sales', on_delete=CASCADE)
    buyer = ForeignKey(User, related_name='buys', on_delete=CASCADE, null=True, blank=True)
    revisions = IntegerField(default=0)
    revisions_hidden = BooleanField(default=True)
    final_uploaded = BooleanField(default=False)
    claim_token = UUIDField(blank=True, null=True)
    customer_email = EmailField(blank=True)
    details = CharField(max_length=5000)
    adjustment_expected_turnaround = DecimalField(default=0, max_digits=5, decimal_places=2)
    adjustment_task_weight = IntegerField(default=0)
    adjustment_revisions = IntegerField(default=0)
    task_weight = IntegerField(default=0)
    escrow_disabled = BooleanField(default=False, db_index=True)
    trust_finalized = BooleanField(default=False, db_index=True)
    table_order = BooleanField(default=False, db_index=True)
    expected_turnaround = DecimalField(
        validators=[MinValueValidator(settings.MINIMUM_TURNAROUND)],
        help_text="Number of days completion is expected to take.",
        max_digits=5, decimal_places=2,
        default=0
    )
    created_on = DateTimeField(db_index=True, default=timezone.now)
    disputed_on = DateTimeField(blank=True, null=True, db_index=True)
    started_on = DateTimeField(blank=True, null=True)
    paid_on = DateTimeField(blank=True, null=True, db_index=True)
    dispute_available_on = DateField(blank=True, null=True)
    auto_finalize_on = DateField(blank=True, null=True, db_index=True)
    arbitrator = ForeignKey(User, related_name='cases', null=True, blank=True, on_delete=SET_NULL)
    stream_link = URLField(blank=True, default='')
    characters = ManyToManyField('profiles.Character', blank=True)
    payout_sent = BooleanField(default=False, db_index=True)
    rating = IntegerField(
        choices=RATINGS, db_index=True, default=GENERAL,
        help_text="The desired content rating of this piece.",
    )
    private = BooleanField(default=False)
    commission_info = TextField(blank=True, default='')
    comments = GenericRelation(
        Comment, related_query_name='order', content_type_field='content_type', object_id_field='object_id'
    )
    subscriptions = GenericRelation('lib.Subscription')

    def total(self):
        return reckon_lines(self.line_items.all())

    def notification_serialize(self, context):
        from .serializers import OrderViewSerializer
        return OrderViewSerializer(instance=self, context=context).data

    # noinspection PyUnusedLocal
    def notification_display(self, context):
        from .serializers import ProductSerializer
        from .serializers import RevisionSerializer
        if self.revisions_hidden and not (self.seller == context['request'].user):
            revision = None
        else:
            revision = self.revision_set.all().last()
        if revision is None:
            return ProductSerializer(instance=self.product, context=context).data['primary_submission']
        else:
            return RevisionSerializer(instance=revision, context=context).data

    def notification_name(self, context):
        request = context['request']
        if request.user == self.seller:
            return "Sale #{}".format(self.id)
        if request.user == self.arbitrator:
            return "Case #{}".format(self.id)
        return "Order #{}".format(self.id)

    def notification_link(self, context):
        request = context['request']
        data = {'params': {'orderId': self.id, 'username': context['request'].user.username}}
        # Doing early returns here so we match name, rather than overwriting.
        if request.user == self.seller:
            data['name'] = 'Sale'
            return data
        if request.user == self.arbitrator:
            data['name'] = 'Case'
            return data
        if request.user.guest:
            data['name'] = 'ClaimOrder'
            if not self.claim_token:
                self.claim_token = uuid4()
                self.save()
            data['params']['claimToken'] = str(self.claim_token)
            return data
        data['name'] = 'Order'
        return data

    def __str__(self):
        return "#{} {} for {} by {}".format(
            self.id, (self.product and self.product.name) or '<Custom>', self.buyer, self.seller,
        )

    def save(self, *args, **kwargs):
        if self.table_order:
            self.escrow_disabled = False
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['created_on']

@receiver(post_save, sender=Order)
@disable_on_load
def auto_subscribe_order(sender, instance, created=False, **_kwargs):
    if not created:
        return
    order_type = ContentType.objects.get_for_model(model=sender)
    subscriptions = [
        Subscription(
            subscriber=instance.seller,
            content_type=order_type,
            object_id=instance.id,
            email=True,
            type=SALE_UPDATE
        ),
        Subscription(
            subscriber=instance.seller,
            content_type=order_type,
            object_id=instance.id,
            email=True,
            type=COMMENT
        )
    ] + buyer_subscriptions(instance, order_type=order_type)
    Subscription.objects.bulk_create(subscriptions, ignore_conflicts=True)
    if (not instance.buyer) or instance.buyer.guest:
        instance.claim_token = uuid4()
        instance.save()


def idempotent_lines(instance: Order):
    if instance.status not in [Order.NEW, Order.PAYMENT_PENDING]:
        return
    if instance.product:
        LineItem.objects.update_or_create(
            {'amount': instance.product.base_price},
            order=instance, amount=instance.product.base_price, type=BASE_PRICE, destination_user=instance.seller,
            destination_account=TransactionRecord.ESCROW,
        )
    total = reckon_lines(instance.line_items.filter(priority__lt=PRIORITY_MAP[SHIELD]))
    escrow_enabled = (not instance.escrow_disabled) and total
    if instance.table_order:
        LineItem.objects.update_or_create(
            {
                'percentage': settings.TABLE_PERCENTAGE_FEE,
                'cascade_percentage': True,
                'amount': Money(settings.TABLE_STATIC_FEE, 'USD'),
                'cascade_amount': False,
            },
            order=instance,
            destination_user=None, destination_account=TransactionRecord.RESERVE, type=TABLE_SERVICE,
        )
        LineItem.objects.update_or_create(
            {'percentage': settings.TABLE_TAX, 'cascade_percentage': True, 'cascade_amount': True,
             'back_into_percentage': True},
            order=instance, destination_user=None, destination_account=TransactionRecord.MONEY_HOLE_STAGE, type=TAX,
        )
        instance.line_items.filter(type__in=[BONUS, SHIELD]).delete()
    elif escrow_enabled:
        LineItem.objects.update_or_create(
            {
                'percentage': settings.SERVICE_PERCENTAGE_FEE,
                'amount': Money(settings.SERVICE_STATIC_FEE, 'USD'),
                'cascade_percentage': True,
                'cascade_amount': True,
            },
            order=instance,
            destination_user=None, destination_account=TransactionRecord.RESERVE, type=SHIELD,
        )
        LineItem.objects.update_or_create(
            {
                'percentage': settings.PREMIUM_PERCENTAGE_BONUS,
                'amount': Money(settings.PREMIUM_STATIC_BONUS, 'USD'),
                'cascade_percentage': True,
                'cascade_amount': True,
            },
            order=instance, percentage=settings.PREMIUM_PERCENTAGE_BONUS, amount=settings.PREMIUM_STATIC_BONUS,
            destination_user=None, destination_account=TransactionRecord.RESERVE, type=BONUS,
        )
        LineItem.objects.filter(
            type=EXTRA, destination_account=TransactionRecord.RESERVE, description='Table Service', order=instance,
        ).delete()
        LineItem.objects.filter(type=TAX).delete()
    else:
        instance.line_items.filter(type__in=[BONUS, SHIELD]).delete()
        LineItem.objects.filter(
            type=EXTRA, destination_account=TransactionRecord.RESERVE, description='Table Service', order=instance,
        ).delete()
        LineItem.objects.filter(type=TAX).delete()


@receiver(post_save, sender=Order)
def ensure_line_items(sender, instance, **kwargs):
    idempotent_lines(instance)


def buyer_subscriptions(instance, order_type=None):
    if not instance.buyer:
        return []
    if not order_type:
        order_type = ContentType.objects.get_for_model(model=instance)
    return [
        Subscription(
            subscriber=instance.buyer,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id,
            email=True,
            type=ORDER_UPDATE,
        ),
        Subscription(
            subscriber=instance.buyer,
            content_type=order_type,
            object_id=instance.id,
            email=True,
            type=REVISION_UPLOADED
        ),
        Subscription(
            subscriber=instance.buyer,
            content_type=order_type,
            object_id=instance.id,
            email=True,
            type=COMMENT
        ),
    ]


# noinspection PyUnusedLocal
@receiver(post_save, sender=Order)
@disable_on_load
def issue_order_claim(sender: type, instance: Order, created=False, **kwargs):
    if not created:
        return
    if not instance.claim_token:
        return
    if instance.buyer:
        return
    if instance.status == Order.NEW:
        # Seller has opted to not send off this notification yet.
        return
    send_transaction_email(
        f'You have a new invoice from {instance.seller.username}!',
        'invoice_issued.html', instance.customer_email,
        {'order': instance, 'claim_token': slugify(instance.claim_token)}
    )


WEIGHTED_STATUSES = [Order.IN_PROGRESS, Order.PAYMENT_PENDING, Order.QUEUED]


@receiver(post_delete, sender=Order)
@disable_on_load
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


remove_order_events = receiver(pre_delete, sender=Order)(disable_on_load(clear_events))


@transaction.atomic
@require_lock(User, 'ACCESS EXCLUSIVE')
@require_lock(Order, 'ACCESS EXCLUSIVE')
@require_lock(Product, 'ACCESS EXCLUSIVE')
def update_artist_load(sender, instance, **_kwargs):
    seller = instance.seller
    result = Order.objects.filter(
        seller_id=seller.id, status__in=WEIGHTED_STATUSES
    ).aggregate(base_load=Sum('task_weight'), added_load=Sum('adjustment_task_weight'))
    load = (result['base_load'] or 0) + (result['added_load'] or 0)
    if isinstance(instance, Order) and instance.product:
        instance.product.parallel = Order.objects.filter(
            product_id=instance.product.id, status__in=WEIGHTED_STATUSES
        ).count()
        instance.product.save()
    # Availability update could be recursive, so get the latest version of the user.
    seller = User.objects.get(id=seller.id)
    update_availability(seller, load, seller.artist_profile.commissions_disabled)


order_load_check = receiver(post_save, sender=Order, dispatch_uid='load')(disable_on_load(update_artist_load))
# No need for delete check-- orders are only ever archived, not deleted.

# noinspection PyUnusedLocal
@transaction.atomic
@require_lock(User, 'ACCESS EXCLUSIVE')
@require_lock(Order, 'ACCESS EXCLUSIVE')
@require_lock(Product, 'ACCESS EXCLUSIVE')
def update_product_availability(sender, instance, **kwargs):
    update_availability(
        instance.user, instance.user.artist_profile.load, instance.user.artist_profile.commissions_disabled
    )


# noinspection PyUnusedLocal,PyUnusedLocal
@transaction.atomic
@require_lock(User, 'ACCESS EXCLUSIVE')
@require_lock(Order, 'ACCESS EXCLUSIVE')
@require_lock(Product, 'ACCESS EXCLUSIVE')
def update_user_availability(sender, instance, **kwargs):
    update_availability(instance.user, instance.load, instance.commissions_disabled)


@receiver(post_save, sender=Product)
def update_order_line_items(sender, instance, **kwargs):
    orders = instance.order_set.filter(status__in=[Order.NEW, Order.PAYMENT_PENDING])
    LineItem.objects.filter(order__in=orders, type=BASE_PRICE).update(amount=instance.base_price)


@receiver(post_save, sender=InventoryTracker)
@disable_on_load
def update_tracker_availability(sender, instance, **kwargs):
    update_product_availability(sender, instance.product, **kwargs)

@receiver(post_delete, sender=InventoryTracker)
@disable_on_load
def clear_tracker_availability(sender, instance, **kwargs):
    update_product_availability(sender, instance.product, **kwargs)

product_availability_check_save = receiver(
    post_save, sender=Product, dispatch_uid='load'
)(disable_on_load(update_product_availability))
product_availability_check_delete = receiver(
    post_delete, sender=Product, dispatch_uid='load'
)(disable_on_load(update_product_availability))

user_availability_check_save = receiver(
    post_save, sender=ArtistProfile, dispatch_uid='load'
)(disable_on_load(update_user_availability))


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

    def __str__(self):
        return f'{self.rater} rated {self.target} {self.stars} stars for [{self.content_object}]'


# noinspection PyUnusedLocal
@receiver(post_save, sender=Rating)
@disable_on_load
def tabulate_stars(sender, instance, **_kwargs):
    instance.target.stars = instance.target.ratings.all().aggregate(Avg('stars'))['stars__avg']
    instance.target.save()


VISA = 1
MASTERCARD = 2
AMEX = 3
DISCOVER = 4
DINERS = 5


CARD_QUALIFIERS = {
    VISA: r'4\d{12}(\d{3})?$',
    AMEX: r'37\d{13}$',
    MASTERCARD: r'5[1-5]\d{14}$',
    DISCOVER: r'6011\d{12}',
    DINERS: r'(30[0-5]\d{11}|(36|38)\d{12})$'
}


def resolve_card_type(number: str) -> int:
    for c_type, card_type_re in CARD_QUALIFIERS.items():
        if re.match(card_type_re, number):
            return c_type


class CreditCardToken(Model):
    """
    Card tokens are stored based on Authorize.net's API. We don't store full card data to avoid issues
    with PCI compliance.
    """

    CARD_TYPES = (
        (VISA, 'Visa'),
        (MASTERCARD, 'Mastercard'),
        (AMEX, 'American Express'),
        (DISCOVER, 'Discover'),
        (DINERS, "Diners Club"))

    ACTIVE_STATUS = 10

    DELETED_STATUS = 20

    CARD_STATUS = (
        (ACTIVE_STATUS, 'Active'),
        (DELETED_STATUS, 'Removed/Deleted'))

    TYPE_TRANSLATION = {
        'amex': AMEX,
        'discover': DISCOVER,
        'mc': MASTERCARD,
        'diners': DINERS,
        'visa': VISA
    }

    user = ForeignKey(User, related_name='credit_cards', on_delete=CASCADE)
    type = IntegerField(choices=CARD_TYPES, default=VISA)
    last_four = CharField(max_length=4)
    token = CharField(max_length=50)
    active = BooleanField(default=True, db_index=True)
    cvv_verified = BooleanField(default=False, db_index=True)
    created_on = DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return "%s ending in %s%s" % (
            self.get_type_display(), self.last_four,
            "" if self.active else " (Deleted)")

    def delete(self, *args, **kwargs):
        """
        Prevent this function from working to avoid accidental deletion.

        We will not allow this to be done in any way but the most deliberate manner,
        since transaction records will exist for the card. So, instead, we raise an exception.

        To mark a card as deleted properly, use the mark_deleted function.
        """
        raise RuntimeError("Credit card tokens are critical for historical billing information.")

    def mark_deleted(self):
        """
        Mark a card as deleted. Deleted cards are hidden away from the user, but kept for
        historical accounting purposes.
        """
        from apps.sales.authorize import delete_card
        delete_card(profile_id=self.profile_id, payment_id=self.payment_id)
        self.active = False
        self.save()
        if self.user.primary_card == self:
            self.user.primary_card = None
            cards = self.user.credit_cards.filter(active=True).order_by('-created_on')
            if cards:
                self.user.primary_card = cards[0]
            self.user.save()

    @property
    def profile_id(self) -> str:
        """
        We used to use the library AuthorizeSauce to handle transactions with Authorize.net. It made charging cards
        easy, but took too many shortcuts to be used for serious fraud prevention, did not handle CVVs as expected,
        and its method of communicating with Authorize.net is no longer supported by Authorize.net.

        So, customers from before our payment refactor have a different format in which we store their card tokens
        for Authorize.net's servers:

        XXXXXXXX|XXXXXXXX

        Where the first section is the user's token on Authorize.net and the latter section is the card token.

        If the card has this pattern, we break the string up and hand the caller back the first section. If not, we
        grab the token from the user model directly.
        """
        parts = self.token.split('|')
        if len(parts) > 1:
            return parts[0]
        return self.user.authorize_token

    @property
    def payment_id(self) -> str:
        """
        As a corollary to the user_token property, we also need to be able to extract just the payment id from old
        cards.
        """
        parts = self.token.split('|')
        if len(parts) > 1:
            return parts[1]
        return self.token

    @classmethod
    def create(
            cls, user: User, first_name: str, last_name: str, number: str, cvv: str, exp_year: int, exp_month: int,
            country: str, zip_code: str, make_primary: bool
    ):
        card_info = CardInfo(
            number=number,
            exp_year=exp_year,
            exp_month=exp_month,
            cvv=cvv,
        )

        address_info = AddressInfo(first_name=first_name, last_name=last_name, postal_code=zip_code, country=country)

        if not user.authorize_token:
            user.authorize_token = create_customer_profile(user.email)
            user.save()
        token = create_card(card_info, address_info, user.authorize_token)
        token = cls(
            user=user, type=resolve_card_type(number), last_four=number[-4:],
            token=token, cvv_verified=True)

        token.save()
        if (not token.user.primary_card) or make_primary:
            token.user.primary_card = token
            token.user.save()
        return token


class TransactionRecord(Model):
    """
    Model for tracking the movement of money.
    """
    # Status types
    SUCCESS = 0
    FAILURE = 1
    PENDING = 2

    STATUSES = (
        (SUCCESS, 'Successful'),
        (FAILURE, 'Failed'),
        (PENDING, 'Pending'),
    )

    # Account types
    CARD = 300
    BANK = 301
    ESCROW = 302
    HOLDINGS = 303
    # All fees put the difference for premium bonus into reserve until an order is complete. When complete, these
    # amounts are deposited into either the cash account of Artconomy, or added to the user's holdings.
    RESERVE = 304
    # Earnings for which we have not yet subtracted card/bank transfer fees.
    UNPROCESSED_EARNINGS = 305
    # These two fee types will be used to keep track of fees that have been paid out to card processors.
    CARD_TRANSACTION_FEES = 306
    CARD_MISC_FEES = 307

    # Fees from performing ACH transactions
    ACH_TRANSACTION_FEES = 308
    # Fees for other ACH-related items, like Dwolla's customer onboarding fees.
    ACH_MISC_FEES = 309

    # Tax held here until order finalized
    MONEY_HOLE_STAGE = 310

    # Where taxes go
    MONEY_HOLE = 311

    # For when a customer gives us cash, like at an event.
    CASH_DEPOSIT = 407

    ACCOUNT_TYPES = (
        (CARD, 'Credit Card'),
        (BANK, 'Bank Account'),
        (ESCROW, 'Escrow'),
        (HOLDINGS, 'Finalized Earnings, available for withdraw'),
        (RESERVE, 'Contingency reserve'),
        (UNPROCESSED_EARNINGS, 'Unannotated earnings'),
        (CARD_TRANSACTION_FEES, 'Card transaction fees'),
        (CARD_MISC_FEES, 'Other card fees'),
        (CASH_DEPOSIT, 'Cash deposit'),
        (ACH_TRANSACTION_FEES, 'ACH Transaction fees'),
        (ACH_MISC_FEES, 'Other ACH fees'),
        (MONEY_HOLE_STAGE, 'Tax staging'),
        (MONEY_HOLE, 'Tax')
    )

    # Transaction types
    SHIELD_FEE = 400
    ESCROW_HOLD = 401
    ESCROW_RELEASE = 402
    ESCROW_REFUND = 403
    SUBSCRIPTION_DUES = 404
    SUBSCRIPTION_REFUND = 405
    CASH_WITHDRAW = 406
    THIRD_PARTY_FEE = 408
    # The extra money earned for subscribing to premium services and completing a sale.
    PREMIUM_BONUS = 409
    # 'Catch all' for any transfers between accounts.
    INTERNAL_TRANSFER = 410
    THIRD_PARTY_REFUND = 411
    # For when we make a mistake and need to correct it somehow.
    CORRECTION = 412
    # For fees levied at conventions
    TABLE_SERVICE = 413
    TAX = 414
    # For things like inventory items sold at tables alongside the commission, like a pop socket.
    EXTRA_ITEM = 415
    # For times when we're manually sending money to others-- such as cases where we don't yet have code to manage
    # something but we need to be able to pay using Dwolla.
    MANUAL_PAYOUT = 416

    CATEGORIES = (
        (SHIELD_FEE, 'Artconomy Service Fee'),
        (ESCROW_HOLD, 'Escrow hold'),
        (ESCROW_RELEASE, 'Escrow release'),
        (ESCROW_REFUND, 'Escrow refund'),
        (SUBSCRIPTION_DUES, 'Subscription dues'),
        (SUBSCRIPTION_REFUND, 'Refund for subscription dues'),
        (CASH_WITHDRAW, 'Cash withdrawal'),
        (THIRD_PARTY_FEE, 'Third party fee'),
        (PREMIUM_BONUS, 'Premium service bonus'),
        (INTERNAL_TRANSFER, 'Internal Transfer'),
        (THIRD_PARTY_REFUND, 'Third party refund'),
        (CORRECTION, 'Correction'),
        (TAX, 'Tax'),
        (MANUAL_PAYOUT, 'Manual Payout')
    )

    id = UUIDField(primary_key=True, db_index=True, default=gen_unique_id)

    status = IntegerField(choices=STATUSES, db_index=True)
    source = IntegerField(choices=ACCOUNT_TYPES, db_index=True)
    destination = IntegerField(choices=ACCOUNT_TYPES, db_index=True)
    category = IntegerField(choices=CATEGORIES, db_index=True)
    payer = ForeignKey(User, null=True, blank=True, related_name='debits', on_delete=PROTECT)
    payee = ForeignKey(User, null=True, blank=True, related_name='credits', on_delete=PROTECT)
    card = ForeignKey(CreditCardToken, null=True, blank=True, on_delete=SET_NULL)
    created_on = DateTimeField(db_index=True, default=timezone.now)
    finalized_on = DateTimeField(db_index=True, default=None, null=True, blank=True)
    amount = MoneyField(max_digits=6, decimal_places=2, default_currency='USD')
    targets = ManyToManyField(to='lib.GenericReference', related_name='referencing_transactions')

    remote_id = CharField(max_length=40, blank=True, default='')
    response_message = TextField(default='', blank=True)
    note = TextField(default='', blank=True)

    def __str__(self):
        return (
            f'{self.get_status_display()}: {self.amount} from '
            f'{self.payer or "(Artconomy)"} [{self.get_source_display()}] to '
            f'{self.payee or "(Artconomy)"} [{self.get_destination_display()}] for '
            f'{self.target_string}'
        )

    @property
    def target_string(self):
        count = self.targets.all().count()
        if not count:
            return 'None'
        base_string = str(self.targets.all().first().target)
        if count == 1:
            return base_string
        count -= 1
        return base_string + f' and {count} other(s).'

    def __setattr__(self, key, value):
        if key in ['object_id', 'content_type', 'content_type_id', 'target']:
            raise AttributeError("Single target no longer supported. Add to 'targets' M2M field via GenericReference.")
        object.__setattr__(self, key, value)

    def refund_card(self) -> 'TransactionRecord':
        if self.category == TransactionRecord.SUBSCRIPTION_DUES:
            category = TransactionRecord.SUBSCRIPTION_REFUND
        elif self.category == TransactionRecord.ESCROW_HOLD:
            category = TransactionRecord.ESCROW_REFUND
        else:
            raise RuntimeError(
                f'Not sure what refund category this transaction applies to! Found {self.get_category_display()}',
            )
        record = TransactionRecord(
            source=self.destination,
            destination=self.source,
            status=TransactionRecord.FAILURE,
            category=category,
            payer=self.payee,
            payee=self.payer,
            amount=self.amount,
            response_message="Failed when contacting payment processor.",
        )
        record.targets.set(self.targets.all())
        try:
            record.remote_id = refund_transaction(self.remote_id, self.card.last_four, self.amount.amount)
            record.status = TransactionRecord.SUCCESS
            record.save()
        except Exception as err:
            record.response_message = str(err)
            record.save()
        return record

    def refund_account(self):
        raise NotImplementedError("Account refunds are not yet implemented.")

    def refund(self):
        warn('Deprecated refund function used.')
        if self.status != TransactionRecord.SUCCESS:
            raise ValueError("Cannot refund a failed transaction.")
        if self.source == TransactionRecord.CARD:
            return self.refund_card()
        elif self.source == TransactionRecord.BANK:
            raise NotImplementedError("ACH Refunds are not implemented.")
        elif self.source == TransactionRecord.ESCROW:
            raise ValueError(
                "Cannot refund an escrow sourced payment. Are you sure you grabbed the right payment object?"
            )
        else:
            return self.refund_account()

    def save(self, *args, **kwargs):
        if (self.status in [TransactionRecord.SUCCESS, TransactionRecord.FAILURE]) and (self.finalized_on is None):
            self.finalized_on = timezone.now()
        return super().save(*args, **kwargs)


BASE_PRICE = 0
ADD_ON = 1
SHIELD = 2
BONUS = 3
TIP = 4
TABLE_SERVICE = 5
TAX = 6
EXTRA = 7

LINE_ITEM_TYPES = (
    (BASE_PRICE, 'Base Price'),
    (ADD_ON, 'Add on or Discount'),
    (SHIELD, 'Shield'),
    (BONUS, 'Bonus'),
    (TIP, 'Tip'),
    (TABLE_SERVICE, 'Table Service'),
    (EXTRA, 'Extra'),
    (TAX, 'Tax'),
)

PRIORITY_MAP = {
    BASE_PRICE: 0,
    ADD_ON: 100,
    TIP: 200,
    SHIELD: 300,
    BONUS: 300,
    TABLE_SERVICE: 300,
    EXTRA: 400,
    TAX: 600,
}


class LineItem(Model):
    type = IntegerField(choices=LINE_ITEM_TYPES, db_index=True)
    order = ForeignKey(Order, on_delete=CASCADE, related_name='line_items')
    amount = MoneyField(
        max_digits=6, decimal_places=2, default_currency='USD',
        blank=True, default=0,
    )
    percentage = DecimalField(max_digits=5, db_index=True, decimal_places=3, default=0)
    # Line items will be run in layers to get our totals/subtotals. Higher numbers will be run after lower numbers.
    # If two items have the same priority, they will both be run as if the other had not been run.
    priority = IntegerField(db_index=True)
    cascade_percentage = BooleanField(db_index=True, default=False)
    cascade_amount = BooleanField(db_index=True, default=False)
    back_into_percentage = BooleanField(db_index=True, default=False)
    destination_user = ForeignKey(User, null=True, db_index=True, on_delete=CASCADE)
    destination_account = IntegerField(choices=TransactionRecord.ACCOUNT_TYPES)
    description = CharField(max_length=250, blank=True, default='')

    def __str__(self):
        return f'{self.get_type_display()} ({self.amount}, {self.percentage}) for #{self.order.id}, priority {self.priority}'

    def save(self, *args, **kwargs):
        self.priority = PRIORITY_MAP[self.type]
        super().save(*args, **kwargs)


@dataclass(frozen=True)
class LineItemSim:
    priority: int
    amount: Money = Money('0', 'USD')
    percentage: Decimal = Decimal(0)
    cascade_percentage: bool = False
    cascade_amount: bool = False
    back_into_percentage: bool = False
    type: int = BASE_PRICE
    description: str = ''


class PaymentRecord(Model):
    """
    Old Model for tracking the movement of money.
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
        (DISBURSEMENT_SENT, 'Initiated Disbursement'),
        (DISBURSEMENT_RETURNED, 'Disbursement completed'),
        (REFUND, 'Refund')
    )

    source = IntegerField(choices=PAYMENT_SOURCES, db_index=True)
    status = IntegerField(choices=STATUSES, db_index=True)
    type = IntegerField(choices=TYPES, db_index=True)
    card = ForeignKey(CreditCardToken, null=True, blank=True, on_delete=SET_NULL)
    payer = ForeignKey(User, null=True, blank=True, related_name='old_debits', on_delete=CASCADE)
    payee = ForeignKey(User, null=True, blank=True, related_name='old_credits', on_delete=CASCADE)
    escrow_for = ForeignKey(
        User, null=True, blank=True, related_name='escrow_holdings', on_delete=CASCADE
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

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        raise RuntimeError('This model is deprecated. Use the new TransactionRecord model!')


class Revision(ImageModel):
    order = ForeignKey(Order, on_delete=CASCADE)

    def can_reference_asset(self, user):
        return (
            (user == self.owner and not self.order.private)
            or ((user == self.order.buyer) and self.order.status == Order.COMPLETED)
        )

    class Meta:
        ordering = ['created_on']


revision_thumbnailer = receiver(post_save, sender=Revision)(thumbnail_hook)


class BankAccount(Model):
    CHECKING = 0
    SAVINGS = 1
    ACCOUNT_TYPES = (
        (CHECKING, 'Checking'),
        (SAVINGS, 'Savings')
    )
    user = ForeignKey(User, on_delete=CASCADE, related_name='banks')
    url = URLField()
    last_four = CharField(max_length=4)
    type = IntegerField(choices=ACCOUNT_TYPES)
    deleted = BooleanField(default=False)

    # noinspection PyUnusedLocal
    def notification_serialize(self, context):
        from .serializers import BankAccountSerializer
        return BankAccountSerializer(instance=self).data


# noinspection PyUnusedLocal
@receiver(post_save, sender=BankAccount)
@disable_on_load
def ensure_shield(sender, instance, created=False, **_kwargs):
    if not created:
        return
    instance.user.escrow_disabled = False
    instance.user.save()
    record = TransactionRecord.objects.create(
        payer=instance.user,
        amount=Money('1.00', 'USD'),
        category=TransactionRecord.THIRD_PARTY_FEE,
        payee=None,
        source=TransactionRecord.HOLDINGS,
        destination=TransactionRecord.ACH_MISC_FEES,
        status=TransactionRecord.SUCCESS,
        note='Bank Connection Fee'
    )
    record.targets.add(ref_for_instance(instance))
    from apps.sales.tasks import withdraw_all
    withdraw_all(instance.user.id)


class Promo(Model):
    """
    For now, this will just be used to handle free months of landscape.
    """
    code = SlugField(unique=True)
    starts = DateTimeField(default=timezone.now, db_index=True)
    expires = DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.code
