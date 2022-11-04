import re
from contextlib import contextmanager
from dataclasses import dataclass
from decimal import Decimal
from typing import Union, List

from django.core.exceptions import ValidationError
from django.db import transaction, models, IntegrityError

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import (
    Model, CharField, ForeignKey, IntegerField, BooleanField, DateTimeField, ManyToManyField,
    SET_NULL, PositiveIntegerField, URLField, CASCADE, DecimalField, Avg, DateField, EmailField, Sum,
    TextField,
    SlugField,
    PROTECT, OneToOneField, JSONField, FloatField,
)

# Create your models here.
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from djmoney.models.fields import MoneyField
from moneyed import Money
from short_stuff import gen_shortcode
from short_stuff.django.models import ShortCodeField

from apps.lib.models import Comment, Subscription, SALE_UPDATE, ORDER_UPDATE, REVISION_UPLOADED, COMMENT, NEW_PRODUCT, \
    Event, ref_for_instance, REFERENCE_UPLOADED
from apps.lib.abstract_models import ImageModel, thumbnail_hook, HitsMixin, RATINGS, GENERAL, get_next_increment
from apps.lib.permissions import Any, IsStaff
from apps.lib.utils import (
    clear_events, recall_notification,
    send_transaction_email,
    demark, mark_modified, mark_read, clear_markers, clear_events_subscriptions_and_comments)
from apps.profiles.models import User, ArtistProfile
from apps.profiles.permissions import UserControls
from apps.sales.apis import PROCESSOR_CHOICES
from apps.sales.permissions import OrderViewPermission, ReferenceViewPermission
from apps.sales.stripe import delete_payment_method, stripe
from apps.sales.utils import update_availability, reckon_lines, order_context_to_link, order_context, get_totals
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
    max_rating = IntegerField(
        choices=RATINGS, db_index=True, default=GENERAL,
        help_text="The maximum content rating you will support for this product."
    )
    samples = ManyToManyField('profiles.Submission', related_name='is_sample_for', blank=True)
    created_on = DateTimeField(default=timezone.now, db_index=True)
    edited_on = DateTimeField(db_index=True, auto_now=True)
    shippable = BooleanField(default=False)
    active = BooleanField(default=True, db_index=True)
    available = BooleanField(default=True, db_index=True)
    featured = BooleanField(default=False, db_index=True)
    wait_list = BooleanField(default=False, db_index=True)
    table_product = BooleanField(default=False, db_index=True)
    track_inventory = BooleanField(default=False, db_index=True)
    catalog_enabled = BooleanField(default=False, db_index=True)
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
            LineItemSim(amount=self.base_price, priority=0, type=BASE_PRICE, id=0),
        ]
        if self.table_product:
            lines.extend([
                LineItemSim(
                    id=300,
                    percentage=settings.TABLE_PERCENTAGE_FEE, priority=300,
                    amount=Money(settings.TABLE_STATIC_FEE, 'USD'),
                    type=TABLE_SERVICE, cascade_percentage=True,
                    cascade_amount=False,
                ),
                LineItemSim(
                    id=600,
                    percentage=settings.TABLE_TAX, priority=600, type=TAX, cascade_percentage=True, cascade_amount=True,
                    back_into_percentage=True,
                ),
            ])
        elif self.base_price and not self.escrow_disabled:
            lines.extend([
                LineItemSim(
                    id=200,
                    amount=Money(settings.SERVICE_STATIC_FEE, 'USD'),
                    percentage=settings.SERVICE_PERCENTAGE_FEE, priority=200,
                    type=SHIELD,
                    cascade_percentage=True,
                    cascade_amount=True,
                ),
                LineItemSim(
                    id=201,
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
        if self.deliverables.all().count():
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


WAITING = 0
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

DELIVERABLE_STATUSES = (
    (WAITING, 'Waiting List'),
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


class Deliverable(Model):
    preserve_comments = True
    post_pay_hook = 'apps.sales.views.helpers.deliverable_charge'
    comment_permissions = [OrderViewPermission]
    watch_permissions = {'DeliverableViewSerializer': [OrderViewPermission], None: [OrderViewPermission]}
    processor = models.CharField(choices=PROCESSOR_CHOICES, db_index=True, max_length=24)
    status = IntegerField(choices=DELIVERABLE_STATUSES, default=NEW, db_index=True)
    order = models.ForeignKey('Order', null=False, on_delete=CASCADE, related_name='deliverables')
    product = models.ForeignKey('Product', null=True, on_delete=SET_NULL, related_name='deliverables')
    # TODO: Remove this field in favor of invoice target(s)
    invoice = models.ForeignKey('Invoice', null=True, on_delete=SET_NULL, related_name='deliverables')
    revisions = IntegerField(default=0)
    revisions_hidden = BooleanField(default=True)
    final_uploaded = BooleanField(default=False)
    details = TextField(max_length=5000)
    adjustment_expected_turnaround = DecimalField(default=0, max_digits=5, decimal_places=2)
    adjustment_task_weight = IntegerField(default=0)
    adjustment_revisions = IntegerField(default=0)
    task_weight = IntegerField(default=0)
    escrow_disabled = BooleanField(default=False, db_index=True)
    trust_finalized = BooleanField(default=False, db_index=True)
    table_order = BooleanField(default=False, db_index=True)
    service_invoice_marked = BooleanField(default=False, db_index=True)
    expected_turnaround = DecimalField(
        validators=[MinValueValidator(settings.MINIMUM_TURNAROUND)],
        help_text="Number of days completion is expected to take.",
        max_digits=5, decimal_places=2,
        default=0,
    )
    created_on = DateTimeField(db_index=True, default=timezone.now)
    disputed_on = DateTimeField(blank=True, null=True, db_index=True)
    started_on = DateTimeField(blank=True, null=True)
    paid_on = DateTimeField(blank=True, null=True, db_index=True)
    dispute_available_on = DateField(blank=True, null=True)
    cancelled_on = DateTimeField(blank=True, null=True)
    auto_finalize_on = DateField(blank=True, null=True, db_index=True)
    arbitrator = ForeignKey(User, related_name='cases', null=True, blank=True, on_delete=SET_NULL)
    stream_link = URLField(blank=True, default='')
    characters = ManyToManyField('profiles.Character', blank=True)
    payout_sent = BooleanField(default=False, db_index=True)
    rating = IntegerField(
        choices=RATINGS, db_index=True, default=GENERAL,
        help_text="The desired content rating of this piece.",
    )
    commission_info = TextField(blank=True, default='')
    subscriptions = GenericRelation('lib.Subscription')
    name = CharField(default='', max_length=150)
    current_intent = CharField(max_length=30, db_index=True, default='', blank=True)
    comments = GenericRelation(
        Comment, related_query_name='deliverable', content_type_field='content_type', object_id_field='object_id'
    )

    def notification_serialize(self, context):
        from .serializers import DeliverableViewSerializer
        return DeliverableViewSerializer(instance=self, context=context).data

    def modified_kwargs(self, _data):
        return {'order': self.order, 'deliverable': self}

    # noinspection PyUnusedLocal
    def notification_display(self, context):
        from .serializers import ProductSerializer
        from .serializers import RevisionSerializer, ReferenceSerializer
        if self.revisions_hidden and not (self.order.seller == context['request'].user):
            revision = None
        else:
            revision = self.revision_set.all().last()
        if revision:
            return RevisionSerializer(instance=revision, context=context).data
        reference = self.reference_set.all().first()
        if reference:
            return ReferenceSerializer(instance=reference, context=context).data
        if not self.product:
            return None
        return ProductSerializer(instance=self.product, context=context).data['primary_submission']

    def notification_name(self, context):
        if context['request'].user == self.arbitrator:
            base_string = f'Case #{self.order.id}'
        else:
            base_string = self.order.notification_name(context)
        result = f'{base_string} [{self.name}]'
        if self.status == WAITING:
            result += ' (Waitlisted)'
        return f'{base_string} [{self.name}]'

    def notification_link(self, context):
        return order_context_to_link(
            order_context(
                order=self.order,
                deliverable=self,
                logged_in=False,
                user=context['request'].user,
                view_name=context.get('view_name', None),
            ),
        )

    @property
    def stripe_metadata(self):
        return {'order_id': self.order.id, 'deliverable_id': self.id, 'invoice_id': str(self.invoice_id)}

    def save(self, *args, **kwargs):
        if self.table_order:
            self.escrow_disabled = False
        super().save(*args, **kwargs)


def get_next_order_position():
    """
    Must be defined in root for migrations.
    """
    return get_next_increment(Order, 'order_display_position')


def get_next_sale_position():
    """
    Must be defined in root for migrations.
    """
    return get_next_increment(Order, 'sale_display_position')


def get_next_case_position():
    """
    Must be defined in root for migrations.
    """
    return get_next_increment(Order, 'case_display_position')


class Order(Model):
    """
    Record of Order
    """

    preserve_comments = True
    comment_permissions = [OrderViewPermission]

    seller = ForeignKey(User, related_name='sales', on_delete=CASCADE)
    buyer = ForeignKey(User, related_name='buys', on_delete=CASCADE, null=True, blank=True)
    claim_token = ShortCodeField(blank=True, null=True)
    customer_email = EmailField(blank=True)
    created_on = DateTimeField(db_index=True, default=timezone.now)
    private = BooleanField(default=False)
    hide_details = BooleanField(default=False)
    order_display_position = FloatField(db_index=True, default=get_next_order_position)
    sale_display_position = FloatField(db_index=True, default=get_next_sale_position)
    # Note: This will affect all arbitrators across all deliverables for this order.
    # This may result in strange behavior, but at least it won't be consumer-facing.
    case_display_position = FloatField(db_index=True, default=get_next_case_position)

    def __str__(self):
        return f"#{self.id} by {self.seller} for {self.buyer}"

    def modified_kwargs(self, _data):
        return {'order': self}

    def notification_display(self, context):
        return self.deliverables.first().notification_display(context)

    def notification_link(self, context):
        return order_context_to_link(order_context(order=self, logged_in=False, user=context['request'].user))

    def notification_name(self, context):
        request = context['request']
        if request.user == self.seller:
            return "Sale #{}".format(self.id)
        return "Order #{}".format(self.id)

    def save(
        self,
        *args, **kwargs,
    ) -> None:
        if self.private:
            self.hide_details = True
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['created_on']


@receiver(post_save, sender=Deliverable)
@disable_on_load
def auto_subscribe_deliverable(sender, instance, created=False, **_kwargs):
    if not created:
        return
    deliverable_type = ContentType.objects.get_for_model(model=sender)
    subscriptions = [
        Subscription(
            subscriber=instance.order.seller,
            content_type=deliverable_type,
            object_id=instance.id,
            email=True,
            type=SALE_UPDATE
        ),
        Subscription(
            subscriber=instance.order.seller,
            content_type=deliverable_type,
            object_id=instance.id,
            email=True,
            type=REFERENCE_UPLOADED,
        ),
        Subscription(
            subscriber=instance.order.seller,
            content_type=deliverable_type,
            object_id=instance.id,
            email=True,
            type=COMMENT
        )
    ] + buyer_subscriptions(instance, order_type=deliverable_type)
    Subscription.objects.bulk_create(subscriptions, ignore_conflicts=True)


def idempotent_lines(instance: Deliverable):
    if instance.status not in [WAITING, NEW, PAYMENT_PENDING]:
        return
    main_qs = instance.invoice.lines_for(instance)
    if instance.status == PAYMENT_PENDING and instance.invoice.status == DRAFT:
        instance.invoice.status = OPEN
    if instance.product:
        line = main_qs.update_or_create(
            defaults={'amount': instance.product.base_price},
            invoice=instance.invoice, amount=instance.product.base_price, type=BASE_PRICE,
            destination_user=instance.order.seller,
            destination_account=TransactionRecord.ESCROW,
        )[0]
        line.annotate(instance)
    total = reckon_lines(main_qs.filter(priority__lt=PRIORITY_MAP[SHIELD]))
    escrow_enabled = (not instance.escrow_disabled) and total
    if instance.table_order:
        line = main_qs.update_or_create(
            defaults={
                'percentage': settings.TABLE_PERCENTAGE_FEE,
                'cascade_percentage': True,
                'amount': Money(settings.TABLE_STATIC_FEE, 'USD'),
                'cascade_amount': False,
            },
            invoice=instance.invoice,
            destination_user=None, destination_account=TransactionRecord.RESERVE, type=TABLE_SERVICE,
        )[0]
        line.annotate(instance)
        line = main_qs.update_or_create(
            defaults={'percentage': settings.TABLE_TAX, 'cascade_percentage': True, 'cascade_amount': True,
             'back_into_percentage': True},
            invoice=instance.invoice, destination_user=None, destination_account=TransactionRecord.MONEY_HOLE_STAGE,
            type=TAX,
        )[0]
        line.annotate(instance)
        main_qs.filter(type__in=[BONUS, SHIELD]).delete()
        instance.invoice.record_only = False
    elif escrow_enabled:
        line = main_qs.update_or_create(
            defaults={
                'percentage': settings.SERVICE_PERCENTAGE_FEE,
                'amount': Money(settings.SERVICE_STATIC_FEE, 'USD'),
                'cascade_percentage': True,
                'cascade_amount': True,
            },
            invoice=instance.invoice,
            destination_user=None, destination_account=TransactionRecord.UNPROCESSED_EARNINGS, type=SHIELD,
        )[0]
        line.annotate(instance)
        if instance.order.seller.landscape:
            destination_kwargs = {
                'destination_user': instance.order.seller,
                'destination_account': TransactionRecord.ESCROW
            }
        else:
            destination_kwargs = {
                'destination_user': None,
                'destination_account': TransactionRecord.UNPROCESSED_EARNINGS,
            }
        line = main_qs.update_or_create(
            defaults={
                'percentage': settings.PREMIUM_PERCENTAGE_BONUS,
                'amount': Money(settings.PREMIUM_STATIC_BONUS, 'USD'),
                'cascade_percentage': True,
                'cascade_amount': True,
                **destination_kwargs,
            },
            invoice=instance.invoice, percentage=settings.PREMIUM_PERCENTAGE_BONUS,
            amount=settings.PREMIUM_STATIC_BONUS,
            type=BONUS,
        )[0]
        line.annotate(instance)
        main_qs.filter(
            type=EXTRA, destination_account=TransactionRecord.RESERVE, description='Table Service',
            invoice=instance.invoice,
        ).delete()
        main_qs.filter(type=TAX).delete()
        instance.invoice.record_only = False
    else:
        main_qs.filter(type__in=[BONUS, SHIELD]).delete()
        main_qs.filter(
            type=EXTRA, destination_account=TransactionRecord.RESERVE, description='Table Service',
            invoice=instance.invoice,
        ).delete()
        main_qs.filter(type=TAX).delete()
        instance.invoice.record_only = True
    instance.invoice.save()


@receiver(pre_save, sender=Deliverable)
@disable_on_load
def ensure_invoice(sender, instance, **kwargs):
    if not instance.invoice:
        instance.invoice = Invoice.objects.create(bill_to=instance.order.buyer)


@receiver(post_save, sender=Deliverable)
@disable_on_load
def ensure_line_items(sender, instance, **kwargs):
    idempotent_lines(instance)
    instance.invoice.targets.add(ref_for_instance(instance))


def buyer_subscriptions(instance, order_type=None):
    if not instance.order.buyer:
        return []
    if not order_type:
        order_type = ContentType.objects.get_for_model(model=instance)
    return [
        Subscription(
            subscriber=instance.order.buyer,
            content_type=order_type,
            object_id=instance.id,
            email=True,
            type=ORDER_UPDATE,
        ),
        Subscription(
            subscriber=instance.order.buyer,
            content_type=order_type,
            object_id=instance.id,
            email=True,
            type=REVISION_UPLOADED,
        ),
        Subscription(
            subscriber=instance.order.buyer,
            content_type=order_type,
            object_id=instance.id,
            email=True,
            type=REFERENCE_UPLOADED,
        ),
        Subscription(
            subscriber=instance.order.buyer,
            content_type=order_type,
            object_id=instance.id,
            email=True,
            type=COMMENT
        ),
    ]


# noinspection PyUnusedLocal
@receiver(post_save, sender=Deliverable)
@disable_on_load
def issue_order_claim(sender: type, instance: Deliverable, created=False, **kwargs):
    if not created:
        return
    if (not instance.order.buyer) or instance.order.buyer.guest:
        instance.order.claim_token = gen_shortcode()
        instance.order.save()
    else:
        return
    if instance.status == NEW:
        # Seller has opted to not send off this notification yet.
        return
    send_transaction_email(
        f'You have a new invoice from {instance.order.seller.username}!',
        'invoice_issued.html', instance.order.customer_email,
        {'deliverable': instance, 'claim_token': instance.order.claim_token}
    )


WEIGHTED_STATUSES = [IN_PROGRESS, PAYMENT_PENDING, QUEUED]


@receiver(post_delete, sender=Deliverable)
@disable_on_load
def auto_remove_order(sender, instance, **_kwargs):
    clear_events_subscriptions_and_comments(instance)


remove_deliverable_events = receiver(pre_delete, sender=Deliverable)(disable_on_load(clear_events))
remove_deliverable_markers = receiver(post_delete, sender=Deliverable)(disable_on_load(clear_markers))


@transaction.atomic
def update_artist_load(sender, instance, **_kwargs):
    seller = instance.order.seller
    result = Deliverable.objects.filter(
        order__seller_id=seller.id, status__in=WEIGHTED_STATUSES
    ).aggregate(base_load=Sum('task_weight'), added_load=Sum('adjustment_task_weight'))
    load = (result['base_load'] or 0) + (result['added_load'] or 0)
    if isinstance(instance, Deliverable) and instance.product:
        instance.product.parallel = Deliverable.objects.filter(
            product_id=instance.product.id, status__in=WEIGHTED_STATUSES
        ).distinct().count()
        instance.product.save()
    # Availability update could be recursive, so get the latest version of the user.
    seller = User.objects.get(id=seller.id)
    update_availability(seller, load, seller.artist_profile.commissions_disabled)


order_load_check = receiver(post_save, sender=Deliverable, dispatch_uid='load')(disable_on_load(update_artist_load))
# No need for delete check-- orders are only ever archived, not deleted.

# noinspection PyUnusedLocal
@transaction.atomic
def update_product_availability(sender, instance, **kwargs):
    update_availability(
        instance.user, instance.user.artist_profile.load, instance.user.artist_profile.commissions_disabled
    )


# noinspection PyUnusedLocal,PyUnusedLocal
@transaction.atomic
def update_user_availability(sender, instance, **kwargs):
    update_availability(instance.user, instance.load, instance.commissions_disabled)


@receiver(post_save, sender=Product)
def update_deliverable_line_items(sender, instance, **kwargs):
    invoices = Deliverable.objects.filter(product=instance, status__in=[NEW, PAYMENT_PENDING]).values_list(
        'invoice', flat=True,
    )
    LineItem.objects.filter(invoice__in=invoices, type=BASE_PRICE).update(amount=instance.base_price)


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
    instance.target.rating_count = instance.target.ratings.all().count()
    instance.target.save()


VISA = 1
MASTERCARD = 2
AMEX = 3
DISCOVER = 4
DINERS = 5
UNIONPAY = 6
JCB = 8
UNKNOWN = 9


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
        (DINERS, "Diners Club"),
        (UNIONPAY, "UnionPay"),
    )

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
        'visa': VISA,
        'mastercard': MASTERCARD,
        'unionpay': UNIONPAY
    }

    user = ForeignKey(User, related_name='credit_cards', on_delete=CASCADE)
    type = IntegerField(choices=CARD_TYPES, default=VISA)
    last_four = CharField(max_length=4)
    # Field for deprecated service, authorize.net. To be removed eventually.
    token = CharField(max_length=50, blank=True, default='')
    # Must have null available for unique to be True with blank entries.
    stripe_token = CharField(max_length=50, blank=True, default=None, null=True, db_index=True, unique=True)
    active = BooleanField(default=True, db_index=True)
    cvv_verified = BooleanField(default=False, db_index=True)
    created_on = DateTimeField(auto_now_add=True, db_index=True)
    watch_permissions = {'CardSerializer': [UserControls]}

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
        with stripe as stripe_api:
            delete_payment_method(api=stripe_api, method_token=self.stripe_token)
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

    def announce_channels(self):
        channels = [f'profiles.User.pk.{self.user.id}.all_cards']
        if self.stripe_token:
            channels.append(f'profiles.User.pk.{self.user.id}.stripe_cards')
        else:
            channels.append(f'profiles.User.pk.{self.user.id}.authorize_cards')
        return channels

    def save(self, **kwargs):
        if not (self.stripe_token or self.token):
            raise ValidationError('No token for any upstream card provider!')
        return super().save(**kwargs)


class TransactionRecord(Model):
    """
    Model for tracking the movement of money.
    """
    # Status types
    SUCCESS = 0
    FAILURE = 1
    PENDING = 2

    TRANSACTION_STATUSES = (
        (SUCCESS, 'Successful'),
        (FAILURE, 'Failed'),
        (PENDING, 'Pending'),
    )

    # Account types
    CARD = 300
    BANK = 301
    ESCROW = 302
    HOLDINGS = 303
    # DEPRECATED: This used to be true and is no longer so. We now determine at the time of payment whether the
    # amount to be taken is more or less due to landscape service.
    # OLD NOTE, NO LONGER CORRECT: All fees put the difference for premium bonus into reserve until an order is
    # complete. When complete, these amounts are deposited into either the cash account of Artconomy, or added to the
    # user's holdings.
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

    # These next accounts are used to generate reports about what money was actually deposited into the payee's currency
    # for tax purposes.

    # The balance of this account will always be negative (or zero) and potentially incalculable because the currency
    # could vary.
    PAYOUT_MIRROR_SOURCE = 500
    # The balance of this account will always be positive (or zero) and potentially incalculable because the currency
    # could vary.
    PAYOUT_MIRROR_DESTINATION = 501

    ACCOUNT_TYPES = (
        (CARD, 'Credit Card'),
        (BANK, 'Bank Account'),
        (ESCROW, 'Escrow'),
        (HOLDINGS, 'Finalized Earnings, available for withdraw'),
        (PAYOUT_MIRROR_SOURCE, '(Local Currency) Finalized Earnings, available for withdraw'),
        (PAYOUT_MIRROR_DESTINATION, '(Local Currency) Bank Account'),
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
    # something, but we need to be able to pay using Dwolla.
    MANUAL_PAYOUT = 416
    PAYOUT_REVERSAL = 417

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
        (EXTRA_ITEM, 'Extra item'),
        (CORRECTION, 'Correction'),
        (TABLE_SERVICE, 'Table Service'),
        (TAX, 'Tax'),
        (MANUAL_PAYOUT, 'Manual Payout'),
        (PAYOUT_REVERSAL, 'Payout Reversal'),
    )

    id = ShortCodeField(primary_key=True, db_index=True, default=gen_shortcode)

    status = IntegerField(choices=TRANSACTION_STATUSES, db_index=True)
    source = IntegerField(choices=ACCOUNT_TYPES, db_index=True)
    destination = IntegerField(choices=ACCOUNT_TYPES, db_index=True)
    category = IntegerField(choices=CATEGORIES, db_index=True)
    payer = ForeignKey(User, null=True, blank=True, related_name='debits', on_delete=PROTECT)
    payee = ForeignKey(User, null=True, blank=True, related_name='credits', on_delete=PROTECT)
    card = ForeignKey(CreditCardToken, null=True, blank=True, on_delete=SET_NULL)
    created_on = DateTimeField(db_index=True, default=timezone.now)
    finalized_on = DateTimeField(db_index=True, default=None, null=True, blank=True)
    amount = MoneyField(max_digits=8, decimal_places=2, default_currency='USD')
    targets = ManyToManyField(to='lib.GenericReference', related_name='referencing_transactions', blank=True)
    auth_code = CharField(max_length=6, default='', db_index=True, blank=True)
    remote_ids = JSONField(default=list)
    response_message = TextField(default='', blank=True)
    note = TextField(default='', blank=True)

    def __str__(self):
        return (
            f'{self.get_status_display()} [{self.get_category_display()}]: {self.amount} from '
            f'{self.payer or "(Artconomy)"} [{self.get_source_display()}] to '
            f'{self.payee or "(Artconomy)"} [{self.get_destination_display()}] for '
            f'{self.target_string}'
        )

    @property
    def remote_id(self):
        raise RuntimeError('Convert all references to remote_id to use remote_ids')

    @remote_id.setter
    def remote_id(self, value):
        raise RuntimeError('Convert all references to remote_id to use remote_ids')

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

    def save(self, *args, **kwargs):
        if (self.status in [TransactionRecord.SUCCESS, TransactionRecord.FAILURE]) and (self.finalized_on is None):
            self.finalized_on = timezone.now()
        return super().save(*args, **kwargs)


DRAFT = 0
OPEN = 1
PAID = 2
VOID = 5

INVOICE_STATUSES = (
    (DRAFT, 'Draft'),
    (OPEN, 'Open'),
    (PAID, 'Paid'),
    (VOID, 'Void'),
)

SALE = 0
SUBSCRIPTION = 1

INVOICE_TYPES = (
    (SALE, 'Sale'),
    (SUBSCRIPTION, 'Subscription'),
)


class Invoice(models.Model):
    id = ShortCodeField(primary_key=True, db_index=True, default=gen_shortcode)
    status = models.IntegerField(default=DRAFT, choices=INVOICE_STATUSES)
    watch_permissions = {'InvoiceSerializer': [UserControls], None: [UserControls]}
    type = models.IntegerField(default=SALE, choices=INVOICE_TYPES)
    bill_to = models.ForeignKey(User, null=True, on_delete=CASCADE, related_name='invoices_billed_to')
    created_on = models.DateTimeField(default=timezone.now, db_index=True)
    paid_on = models.DateTimeField(null=True, db_index=True, blank=True)
    # We don't currently use stripe Invoices, but we anticipate doing so.
    stripe_token = models.CharField(default='', db_index=True, max_length=50, blank=True)
    current_intent = CharField(max_length=30, db_index=True, default='', blank=True)
    record_only = models.BooleanField(default=False, db_index=True)
    # This flag is a temporary hack until we migrate over to a unified method of handling these transactions.
    creates_own_transactions = models.BooleanField(default=False, db_index=True)
    # You should also add the targets to the line item annotations if adding them here. This is used
    # to make lookups for things like 'the invoice for this deliverable' easier, though in the future
    # it's possible that we could have multiple deliverables on an invoice.
    #
    # The reason why this is useful rather than just querying line items is that it's possible that
    # someone might be billed for an action taken regarding a deliverable, rather than the invoice being
    # for the work of the deliverable itself. This makes querying just a bit easier for the deliverable's
    # work invoice.
    targets = ManyToManyField(to='lib.GenericReference', related_name='referencing_invoices', blank=True)

    def total(self) -> Money:
        return reckon_lines(self.line_items.all())

    def context_for(self, target):
        # Provided for compatibility in post_payment hook. We might eventually allow for more specific annotations
        # like we do with LineItems.
        return {}

    def lines_for(self, target):
        from apps.lib.models import ref_for_instance
        return self.line_items.filter(targets=ref_for_instance(target))

    def __str__(self):
        result = f'Invoice {self.id} for {self.bill_to} in the amount of {self.total()}'
        deliverable = self.deliverables.first()
        if deliverable:
            result += f' for deliverable: {deliverable}'
        return result

    class Meta:
        ordering = ('-created_on',)


class LineItemAnnotation(models.Model):
    """
    Annotation for a line item on an invoice. Useful to trigger post-payment effects.
    """
    target = ForeignKey('lib.GenericReference', on_delete=CASCADE)
    line_item = ForeignKey('sales.LineItem', on_delete=CASCADE)
    # Do not allow users to set custom keys here, as it could lead to arbitrary code execution.
    context = JSONField(default=dict)


BASE_PRICE = 0
ADD_ON = 1
SHIELD = 2
BONUS = 3
TIP = 4
TABLE_SERVICE = 5
TAX = 6
EXTRA = 7
PREMIUM_SUBSCRIPTION = 8
OTHER_FEE = 9

LINE_ITEM_TYPES = (
    (BASE_PRICE, 'Base Price'),
    (ADD_ON, 'Add on or Discount'),
    (OTHER_FEE, 'Other fee'),
    (SHIELD, 'Shield'),
    (BONUS, 'Bonus'),
    (TIP, 'Tip'),
    (TABLE_SERVICE, 'Table Service'),
    (EXTRA, 'Extra'),
    (TAX, 'Tax'),
    (PREMIUM_SUBSCRIPTION, 'Premium Subscription'),
)

PRIORITY_MAP = {
    BASE_PRICE: 0,
    ADD_ON: 100,
    PREMIUM_SUBSCRIPTION: 110,
    OTHER_FEE: 120,
    TIP: 200,
    SHIELD: 300,
    BONUS: 300,
    TABLE_SERVICE: 300,
    EXTRA: 400,
    TAX: 600,
}


class LineItem(Model):
    type = IntegerField(choices=LINE_ITEM_TYPES, db_index=True)
    invoice = ForeignKey(Invoice, on_delete=CASCADE, related_name='line_items', null=True)
    amount = MoneyField(
        max_digits=6, decimal_places=2, default_currency='USD',
        blank=True, default=0,
    )
    frozen_value = MoneyField(
        max_digits=6, decimal_places=2, default_currency='USD',
        blank=True, null=True, default=None,
        help_text='Snapshotted amount after calculations have been completed and the relevant '
                  'invoice is paid. This helps keep historical record in case the line item calculation '
                  'algorithms change.'
    )
    percentage = DecimalField(max_digits=5, db_index=True, decimal_places=3, default=0)
    # Line items will be run in layers to get our totals/subtotals. Higher numbers will be run after lower numbers.
    # If two items have the same priority, they will both be run as if the other had not been run.
    priority = IntegerField(db_index=True)
    cascade_percentage = BooleanField(db_index=True, default=False)
    cascade_amount = BooleanField(db_index=True, default=False)
    back_into_percentage = BooleanField(db_index=True, default=False)
    destination_user = ForeignKey(User, null=True, db_index=True, on_delete=CASCADE, blank=True)
    destination_account = IntegerField(choices=TransactionRecord.ACCOUNT_TYPES)
    description = CharField(max_length=250, blank=True, default='')
    watch_permissions = {'LineItemSerializer': [OrderViewPermission]}
    targets = ManyToManyField('lib.GenericReference', through=LineItemAnnotation, related_name='line_items')

    def __str__(self):
        return f'{self.get_type_display()} ({self.amount}, {self.percentage}) for #{self.invoice.id}, priority {self.priority}'

    @property
    def deliverable(self):
        return Deliverable.objects.filter(invoice=self.invoice).first()

    def announce_channels(self):
        deliverable = self.deliverable
        channels = []
        if deliverable:
            channels.append(f'sales.Deliverable.pk.{deliverable.id}.line_items')
        channels.append(f'sales.Invoice.pk.{self.invoice.id}.line_items')
        return channels

    def context_for(self, target):
        return LineItemAnnotation.objects.get(target=target, line_item=self).context

    def annotate(self, target):
        ref = ref_for_instance(target)
        return LineItemAnnotation.objects.get_or_create(target=ref, line_item=self)[0]

    def save(self, *args, **kwargs):
        self.priority = PRIORITY_MAP[self.type]
        super().save(*args, **kwargs)


@dataclass(frozen=True)
class LineItemSim:
    id: int
    priority: int
    amount: Money = Money('0', 'USD')
    percentage: Decimal = Decimal(0)
    cascade_percentage: bool = False
    cascade_amount: bool = False
    back_into_percentage: bool = False
    type: int = BASE_PRICE
    description: str = ''


class Revision(ImageModel):
    comment_permissions = [OrderViewPermission]
    preserve_comments = True
    deliverable = ForeignKey(Deliverable, on_delete=CASCADE)
    comments = GenericRelation(
        Comment, related_query_name='revisions', content_type_field='content_type', object_id_field='object_id'
    )

    def __str__(self):
        return f'Revision {self.id} for {self.deliverable}'

    def modified_kwargs(self, _data):
        return {'order': self.deliverable.order, 'deliverable': self.deliverable}

    def can_reference_asset(self, user):
        return (
            (user == self.owner and not self.deliverable.order.private)
            or ((user == self.deliverable.order.buyer) and self.deliverable.status == COMPLETED)
        )

    def notification_link(self, context):
        return order_context_to_link(
            order_context(
                order=self.deliverable.order,
                logged_in=False,
                user=context['request'].user,
                extra_params={'revisionId': self.id},
                view_name='DeliverableRevision',
            ),
        )

    def notification_display(self, context):
        from apps.sales.serializers import RevisionSerializer
        return RevisionSerializer(instance=self, context=context).data

    def notification_name(self, context):
        return f'Revision ID #{self.id} on {self.deliverable.notification_name(context)}'

    class Meta:
        ordering = ['created_on']


revision_thumbnailer = receiver(post_save, sender=Revision)(thumbnail_hook)
revision_clear = receiver(post_delete, sender=Revision)(clear_markers)


def deliverable_from_context(context, check_request=True):
    # This data not to be trusted. It is user provided.
    deliverable = context['extra_data'].get('deliverable', None)
    if deliverable is not None:
        try:
            deliverable = int(deliverable)
            deliverable = Deliverable.objects.get(id=deliverable)
            if check_request:
                if not OrderViewPermission().has_object_permission(context['request'], None, deliverable):
                    raise ValueError
            return deliverable
        except (ValueError, Deliverable.DoesNotExist):
            return None


class Reference(ImageModel):
    """
    NOTE: References have to have their subscriptions created at the point of creation, as signals would not indicate
    which deliverable is being dealt with.
    """
    comment_permissions = [Any(ReferenceViewPermission, IsStaff)]
    preserve_comments = True
    deliverables = ManyToManyField(Deliverable)
    comments = GenericRelation(
        Comment, related_query_name='references', content_type_field='content_type', object_id_field='object_id'
    )

    def can_reference_asset(self, user):
        # Despite this being a reference, it should never be the source for any other models/sharing.
        return False

    def modified_kwargs(self, data):
        deliverable = deliverable_from_context({'extra_data': data}, check_request=False)
        if deliverable is None:
            return {}
        if not self.deliverables.filter(id=deliverable.id).exists():
            return {}
        return {'order': deliverable.order, 'deliverable': deliverable}

    def notification_display(self, context):
        from apps.sales.serializers import ReferenceSerializer
        return ReferenceSerializer(context=context, instance=self).data

    def notification_link(self, context):
        deliverable = context.get('deliverable', deliverable_from_context(context))
        if deliverable is None:
            return None
        return order_context_to_link(
            order_context(
                order=deliverable.order,
                deliverable=deliverable,
                user=context['request'].user,
                view_name='DeliverableReference',
                extra_params={'referenceId': self.id},
                logged_in=False,
            ))

    def notification_name(self, context):
        deliverable = deliverable_from_context(context)
        return f'Reference ID #{self.id} for {deliverable and deliverable.notification_name(context)}'

    class Meta:
        ordering = ['created_on']


reference_thumbnailer = receiver(post_save, sender=Reference)(thumbnail_hook)
reference_clear = receiver(post_delete, sender=Reference)(clear_markers)


@disable_on_load
def auto_subscribe_image(sender, instance, created=False, **kwargs):
    if not created:
        return
    mark_modified(obj=instance, **instance.modified_kwargs({}))
    mark_read(obj=instance, user=instance.owner)
    content_type = ContentType.objects.get_for_model(instance)
    Subscription.objects.create(
        subscriber=instance.deliverable.order.seller,
        content_type=content_type,
        object_id=instance.id,
        email=True,
        type=COMMENT
    )
    if instance.deliverable.arbitrator:
        Subscription.objects.create(
            subscriber=instance.deliverable.arbitrator,
            content_type=content_type,
            object_id=instance.id,
            email=True,
            type=COMMENT
        )
    if not instance.deliverable.order.buyer:
        return
    Subscription.objects.create(
        subscriber=instance.deliverable.order.buyer,
        content_type=content_type,
        object_id=instance.id,
        email=True,
        type=COMMENT
    )


revision_comment_receiver = receiver(post_save, sender=Revision)(auto_subscribe_image)


@receiver(post_delete, sender=Reference)
@disable_on_load
def delete_comments_and_events(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(instance)
    Event.objects.filter(object_id=instance.id, content_type=content_type).delete()
    Subscription.objects.filter(object_id=instance.id, content_type=content_type).delete()
    Comment.objects.filter(object_id=instance.id, content_type=content_type).delete()
    Comment.objects.filter(top_object_id=instance.id, top_content_type=content_type).delete()
    Event.objects.filter(data__reference=instance.id).delete()


class BankAccount(Model):
    """
    Deprecated. This was the model used to track Dwolla bank accounts for transfers.

    It is no longer used-- payouts via Dwolla have been removed and we only retain these
    for record keeping purposes.
    """
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
    processor = 'dwolla'

    # noinspection PyUnusedLocal
    def notification_serialize(self, context):
        from .serializers import BankAccountSerializer
        return BankAccountSerializer(instance=self).data


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


class WebhookRecord(Model):
    key = CharField(max_length=50)
    connect = BooleanField(default=False)
    secret = CharField(max_length=250)

    def __str__(self):
        return f'Webhook {self.id} {"(Connect)" if self.connect else ""}'


class StripeAccount(Model):
    id = ShortCodeField(primary_key=True, db_index=True, default=gen_shortcode)
    user = OneToOneField(User, on_delete=CASCADE, related_name='stripe_account')
    country = CharField(max_length=2, db_index=True)
    active = BooleanField(default=False, db_index=True)
    token = CharField(max_length=50, db_index=True)
    processor = 'stripe'
    watch_permissions = {'StripeAccountSerializer': [UserControls]}

    def announce_channels(self):
        return [f'profiles.User.pk.{self.user_id}.stripe_accounts']

    def delete(self, using=None, keep_parents=False):
        with stripe as api:
            api.Account.delete(self.token)
        return super(StripeAccount, self).delete()


class ServicePlan(models.Model):
    """
    Service plans describe levels of service for users.
    """
    post_pay_hook = 'apps.sales.views.helpers.service_charge'
    name = models.CharField(max_length=100, db_index=True, unique=True)
    description = models.CharField(max_length=1000)
    features = JSONField(default=list)
    sort_value = models.IntegerField(default=0, db_index=True)
    monthly_charge = MoneyField(
        default=Money('0.00', 'USD'), db_index=True, help_text='Monthly subscription price.',
        max_digits=5, decimal_places=2,
    )
    per_deliverable_price = MoneyField(
        default=Money('0.00', 'USD'), db_index=True, help_text='Amount we charge for each deliverable tracked.',
        max_digits=5, decimal_places=2,
    )
    max_simultaneous_orders = models.IntegerField(
        default=0, help_text='How many simultaneous orders are permitted. 0 means infinite.',
    )
    auto_shield = models.BooleanField(
        default=False, help_text='Whether shield protection can be automatically made available on each product.',
    )
    shield_static_price = MoneyField(
        default=Money('1.50', 'USD'), help_text='Static amount charged per shield order. Replaces the per deliverable '
                                                'price on shield orders.',
        max_digits=5, decimal_places=2,
    )
    shield_percentage_price = DecimalField(
        default=Decimal('8'), help_text='Percentage amount applied to shield orders.',
        max_digits=5, decimal_places=2,
    )
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} (#{self.id})'


class StripeLocation(models.Model):
    """
    Model to represent a location in the Stripe API
    """
    id = ShortCodeField(primary_key=True, default=gen_shortcode)
    name = CharField(max_length=150)
    stripe_token = CharField(max_length=50, default='', blank=True)
    line1 = CharField(max_length=250)
    line2 = CharField(max_length=250, default='', blank=True)
    city = CharField(max_length=250, default='', blank=True)
    state = CharField(max_length=5, default='', blank=True)
    postal_code = CharField(max_length=20, default='', blank=True)
    country = CharField(max_length=2)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) -> None:
        with stripe as stripe_api:
            address = {'line1': self.line1, 'country': self.country}
            for field in ['city', 'state', 'postal_code', 'line2']:
                if value := getattr(self, field):
                    address[field] = value
            if self.stripe_token:
                stripe_api.terminal.Location.modify(
                    self.stripe_token,
                    display_name=self.name,
                    address=address,
                )
            else:
                location = stripe_api.terminal.Location.create(
                    display_name=self.name,
                    address=address,
                )
                self.stripe_token = location.id
            super().save()

    def delete(self, *args, **kwargs):
        with stripe as stripe_api:
            stripe_api.terminal.Location.delete(self.stripe_token)
        super().delete(*args, **kwargs)


class StripeReader(models.Model):
    """
    Model to represent terminals in the API.
    """
    registration_code = ''
    id = ShortCodeField(primary_key=True, default=gen_shortcode)
    name = CharField(max_length=150, db_index=True)
    stripe_token = CharField(max_length=50)
    virtual = BooleanField()
    location = ForeignKey(
        StripeLocation,
        on_delete=CASCADE,
        help_text='Primary location where reader will be used. Cannot be changed after it is initially set. '
                  'You must delete the reader and recreate it to change its location.'
    )

    def __str__(self):
        return f'{self.name} at {self.location and self.location.name} (#{self.id})'

    def save(self, *args, **kwargs) -> None:
        with stripe as stripe_api:
            if not self.stripe_token:
                reader = stripe_api.terminal.Reader.create(
                    label=self.name,
                    location=self.location.stripe_token,
                    registration_code=self.registration_code,
                )
                if self.registration_code.startswith('simulated'):
                    self.virtual = True
                self.stripe_token = reader.id
            else:
                stripe_api.terminal.Reader.modify(
                    self.stripe_token,
                    label=self.name,
                )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with stripe as stripe_api:
            stripe_api.terminal.Reader.delete(self.stripe_token)
        super().delete(*args, **kwargs)


# Force load of registrations for serializers.
import apps.sales.serializers
