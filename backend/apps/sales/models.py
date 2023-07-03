from contextlib import contextmanager
from dataclasses import dataclass
from decimal import Decimal
from math import ceil
from typing import List, Union

from apps.lib.abstract_models import (
    GENERAL,
    RATINGS,
    HitsMixin,
    ImageModel,
    get_next_increment,
    thumbnail_hook,
)
from apps.lib.models import (
    COMMENT,
    NEW_PRODUCT,
    ORDER_UPDATE,
    REFERENCE_UPLOADED,
    REVISION_APPROVED,
    REVISION_UPLOADED,
    SALE_UPDATE,
    TIP_RECEIVED,
    Comment,
    Event,
    Subscription,
    note_for_text,
    ref_for_instance,
)
from apps.lib.permissions import Any, IsStaff
from apps.lib.utils import (
    clear_events,
    clear_events_subscriptions_and_comments,
    clear_markers,
    demark,
    mark_modified,
    mark_read,
    notify,
    recall_notification,
    send_transaction_email,
)
from apps.profiles.models import ArtistProfile, User
from apps.profiles.permissions import BillTo, IssuedBy, UserControls
from apps.sales.constants import (
    ACCOUNT_TYPES,
    BASE_PRICE,
    BONUS,
    CARD_TYPES,
    CATEGORIES,
    COMPLETED,
    DELIVERABLE_STATUSES,
    DELIVERABLE_TRACKING,
    DRAFT,
    ESCROW,
    EXTRA,
    FAILURE,
    IN_PROGRESS,
    INVOICE_STATUSES,
    INVOICE_TYPES,
    LIMBO,
    LINE_ITEM_TYPES,
    MISSED,
    MONEY_HOLE_STAGE,
    NEW,
    OPEN,
    PAYMENT_PENDING,
    PRIORITY_MAP,
    PROCESSOR_CHOICES,
    QUEUED,
    RESERVE,
    REVIEW,
    SALE,
    SHIELD,
    SUBSCRIPTION,
    SUCCESS,
    TABLE_SERVICE,
    TAX,
    TIP,
    TRANSACTION_STATUSES,
    UNPROCESSED_EARNINGS,
    VISA,
    WAITING,
    WEIGHTED_STATUSES,
)
from apps.sales.line_item_funcs import reckon_lines
from apps.sales.permissions import (
    DeliverableStatusPermission,
    OrderViewPermission,
    ReferenceViewPermission,
)
from apps.sales.stripe import delete_payment_method, stripe
from apps.sales.utils import (
    credit_referral,
    ensure_buyer,
    get_claim_token,
    lines_for_product,
    order_context,
    order_context_to_link,
    set_service_plan,
    update_availability,
)
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import IntegrityError, models, transaction
from django.db.models import (
    CASCADE,
    PROTECT,
    SET_NULL,
    Avg,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    EmailField,
    FloatField,
    ForeignKey,
    IntegerField,
    JSONField,
    ManyToManyField,
    Model,
    OneToOneField,
    PositiveIntegerField,
    SlugField,
    Sum,
    TextField,
    URLField,
)

# Create your models here.
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from djmoney.models.fields import MoneyField
from moneyed import Money
from pandas._libs.tslibs.offsets import BDay
from short_stuff import gen_shortcode
from short_stuff.django.models import ShortCodeField
from shortcuts import disable_on_load


def get_next_product_position():
    """
    Must be defined in root for migrations.
    """
    return get_next_increment(Product, "display_position")


class Product(ImageModel, HitsMixin):
    """
    Product on offer by an art seller.
    """

    name = CharField(max_length=250, db_index=True)
    description = CharField(max_length=5000)
    expected_turnaround = DecimalField(
        validators=[MinValueValidator(settings.MINIMUM_TURNAROUND)],
        help_text="Number of days completion is expected to take.",
        max_digits=5,
        decimal_places=2,
    )
    base_price = MoneyField(
        max_digits=6,
        decimal_places=2,
        default_currency="USD",
        db_index=True,
        null=True,
    )
    cascade_fees = BooleanField(default=True)
    escrow_enabled = BooleanField(default=False, db_index=True)
    escrow_upgradable = BooleanField(default=False, db_index=True)
    # Cached value from get_starting_price, useful for searching.
    starting_price = MoneyField(
        max_digits=6,
        decimal_places=2,
        default_currency="USD",
        db_index=True,
        null=True,
        blank=True,
    )
    shield_price = MoneyField(
        max_digits=6,
        decimal_places=2,
        default_currency="USD",
        db_index=True,
        null=True,
        blank=True,
    )
    tags = ManyToManyField("lib.Tag", related_name="products", blank=True)
    tags__max = 200
    hidden = BooleanField(
        default=False, help_text="Whether this product is visible.", db_index=True
    )
    user = ForeignKey(User, on_delete=CASCADE, related_name="products")
    primary_submission = ForeignKey(
        "profiles.Submission",
        on_delete=SET_NULL,
        related_name="featured_sample_for",
        null=True,
        blank=True,
    )
    max_rating = IntegerField(
        choices=RATINGS,
        db_index=True,
        default=GENERAL,
        help_text="The maximum content rating you will support for this product.",
    )
    samples = ManyToManyField(
        "profiles.Submission", related_name="is_sample_for", blank=True
    )
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
    international = BooleanField(default=False, db_index=True)
    max_parallel = IntegerField(
        validators=[MinValueValidator(0)],
        help_text="How many of these you are willing to have in your "
        "backlog at one time.",
        blank=True,
        default=0,
    )
    parallel = IntegerField(default=0, blank=True)
    hit_counter = GenericRelation(
        "hitcount.HitCount",
        object_id_field="object_pk",
        related_query_name="hit_counter",
    )
    task_weight = IntegerField(validators=[MinValueValidator(1)])
    display_position = FloatField(db_index=True, default=get_next_product_position)

    @property
    def preview_link(self):
        if not self.primary_submission:
            return "/static/images/default-avatar.png"
        return self.primary_submission.preview_link

    def can_reference_asset(self, user):
        return user == self.user

    def get_starting_price(self, force_shield=False) -> Money:
        return reckon_lines(lines_for_product(self, force_shield=force_shield))

    @property
    def preview_description(self) -> str:
        price = self.starting_price
        if price:
            price = str(price).replace("US$", "$")
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
            recall_notification(
                NEW_PRODUCT, self.user, {"product": pk}, unique_data=True
            )
        return result

    def delete(self, *args, **kwargs):
        return self.wrap_operation(self.proto_delete, always=True, *args, **kwargs)

    def save(self, *args, **kwargs):
        self.starting_price = self.get_starting_price()
        self.shield_price = self.get_starting_price(force_shield=True)
        self.owner = self.user
        self.international = (
            StripeAccount.objects.filter(
                user=self.user,
            )
            .exclude(country=settings.SOURCE_COUNTRY)
            .exists()
        )
        if not self.base_price or self.base_price < settings.MINIMUM_PRICE:
            self.escrow_enabled = False
        if not self.user.artist_profile.escrow_enabled:
            self.escrow_enabled = False
        if self.table_product:
            self.escrow_enabled = True
        result = self.wrap_operation(super().save, *args, **kwargs)
        if self.primary_submission:
            self.samples.add(self.primary_submission)
        return result

    # noinspection PyUnusedLocal
    def notification_display(self, context: dict) -> dict:
        from .serializers import ProductSerializer

        return ProductSerializer(instance=self, context=context).data[
            "primary_submission"
        ]

    def __str__(self):
        return "{} offered by {} at {}".format(
            self.name, self.user.username, self.base_price
        )


# noinspection PyUnusedLocal
@receiver(post_delete, sender=Product)
@disable_on_load
def auto_remove_product_notifications(sender, instance, **kwargs):
    Event.objects.filter(data__product=instance.id).delete()
    Event.objects.filter(
        object_id=instance.id, content_type=ContentType.objects.get_for_model(instance)
    ).delete()


product_thumbnailer = receiver(post_save, sender=Product)(thumbnail_hook)


@receiver(post_save, sender=Product)
@disable_on_load
def apply_inventory(sender, instance, **kwargs):
    if instance.track_inventory:
        InventoryTracker.objects.get_or_create(product=instance)
    else:
        InventoryTracker.objects.filter(product=instance).delete()


class InventoryTracker(Model):
    product = models.OneToOneField(
        "Product", on_delete=CASCADE, related_name="inventory"
    )
    count = models.IntegerField(default=0, db_index=True)


class InventoryError(IntegrityError):
    """
    Used when a product is out of stock.
    """


@contextmanager
def inventory_change(product: Union["Product", None], delta: int = -1):
    if product is None:
        # Nothing to do.
        yield
        return
    with transaction.atomic():
        tracker = (
            InventoryTracker.objects.select_for_update().filter(product=product).first()
        )
        if not tracker:
            # Nothing to do here, carry on.
            yield
            return
        tracker.count += delta
        if tracker.count < 0:
            raise InventoryError()
        # Should return the row, locked for editing. When the block this function is
        # used in is exited, should release the lock.
        yield tracker.count
        tracker.save()


def get_default_processor():
    return settings.DEFAULT_CARD_PROCESSOR


class Deliverable(Model):
    preserve_comments = True
    pre_pay_hook = "apps.sales.models.deliverable_pre_pay"
    post_pay_hook = "apps.sales.models.deliverable_post_pay"
    comment_permissions = [
        OrderViewPermission,
        DeliverableStatusPermission(
            *(
                status
                for (status, _) in DELIVERABLE_STATUSES
                if status not in (LIMBO, MISSED)
            )
        ),
    ]
    watch_permissions = {
        "DeliverableSerializer": [OrderViewPermission],
        None: [OrderViewPermission],
    }
    processor = models.CharField(
        choices=PROCESSOR_CHOICES,
        db_index=True,
        max_length=24,
        default=get_default_processor,
    )
    status = IntegerField(choices=DELIVERABLE_STATUSES, default=NEW, db_index=True)
    order = models.ForeignKey(
        "Order", null=False, on_delete=CASCADE, related_name="deliverables"
    )
    product = models.ForeignKey(
        "Product", null=True, on_delete=SET_NULL, related_name="deliverables"
    )
    invoice = models.ForeignKey(
        "Invoice", null=True, on_delete=SET_NULL, related_name="deliverables"
    )
    revisions = IntegerField(default=0)
    revisions_hidden = BooleanField(default=True)
    final_uploaded = BooleanField(default=False)
    details = TextField(max_length=5000)
    adjustment_expected_turnaround = DecimalField(
        default=0, max_digits=5, decimal_places=2
    )
    adjustment_task_weight = IntegerField(default=0)
    adjustment_revisions = IntegerField(default=0)
    task_weight = IntegerField(default=0)
    escrow_enabled = BooleanField(default=True, db_index=True)
    trust_finalized = BooleanField(default=False, db_index=True)
    cascade_fees = BooleanField(default=True)
    table_order = BooleanField(default=False, db_index=True)
    term_billed = BooleanField(
        default=False,
        db_index=True,
        help_text="Marked true when this deliverable has been credited on a monthly "
        "invoice (or otherwise would have been if such credits do not apply)",
    )
    international = BooleanField(default=False)
    service_invoice_marked = BooleanField(default=False, db_index=True)
    expected_turnaround = DecimalField(
        validators=[MinValueValidator(settings.MINIMUM_TURNAROUND)],
        help_text="Number of days completion is expected to take.",
        max_digits=5,
        decimal_places=2,
        default=0,
        db_index=True,
    )
    created_on = DateTimeField(db_index=True, default=timezone.now)
    disputed_on = DateTimeField(blank=True, null=True, db_index=True)
    started_on = DateTimeField(blank=True, null=True)
    paid_on = DateTimeField(blank=True, null=True, db_index=True)
    dispute_available_on = DateField(blank=True, null=True)
    cancelled_on = DateTimeField(blank=True, null=True)
    auto_finalize_on = DateField(blank=True, null=True, db_index=True)
    finalized_on = DateTimeField(blank=True, null=True, db_index=True)
    auto_cancel_on = DateTimeField(blank=True, null=True, db_index=True)
    refunded_on = DateTimeField(blank=True, null=True, db_index=True)
    tip_invoice = models.ForeignKey(
        "Invoice",
        null=True,
        on_delete=SET_NULL,
        blank=True,
        related_name="tipped_deliverables",
    )
    arbitrator = ForeignKey(
        User, related_name="cases", null=True, blank=True, on_delete=SET_NULL
    )
    stream_link = URLField(blank=True, default="")
    characters = ManyToManyField("profiles.Character", blank=True)
    rating = IntegerField(
        choices=RATINGS,
        db_index=True,
        default=GENERAL,
        help_text="The desired content rating of this piece.",
    )
    commission_info = ForeignKey("lib.Note", null=True, blank=True, on_delete=SET_NULL)
    subscriptions = GenericRelation("lib.Subscription")
    name = CharField(default="", max_length=150)
    current_intent = CharField(max_length=30, db_index=True, default="", blank=True)
    comments = GenericRelation(
        Comment,
        related_query_name="deliverable",
        content_type_field="content_type",
        object_id_field="object_id",
    )

    def notification_serialize(self, context):
        from .serializers import DeliverableSerializer

        if self.status == LIMBO and context["request"].user == self.order.seller:
            return {"id": self.id, "status": LIMBO, "order": {"id": self.order_id}}
        return DeliverableSerializer(instance=self, context=context).data

    def modified_kwargs(self, _data):
        return {"order": self.order, "deliverable": self}

    # noinspection PyUnusedLocal
    def notification_display(self, context):
        from .serializers import (
            ProductSerializer,
            ReferenceSerializer,
            RevisionSerializer,
        )

        if self.revisions_hidden and not (self.order.seller == context["request"].user):
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
        return ProductSerializer(instance=self.product, context=context).data[
            "primary_submission"
        ]

    def notification_name(self, context):
        if context["request"].user == self.arbitrator:
            base_string = f"Case #{self.order.id}"
        else:
            base_string = self.order.notification_name(context)
        result = f"{base_string} [{self.name}]"
        if self.status == WAITING:
            result += " (Waitlisted)"
        return result

    def notification_link(self, context):
        return order_context_to_link(
            order_context(
                order=self.order,
                deliverable=self,
                logged_in=False,
                user=context["request"].user,
                view_name=context.get("view_name", None),
            ),
        )

    def new_comment(self, comment):
        if self.status != NEW:
            return
        if comment.user == self.order.seller:
            self.auto_cancel_on = None
        else:
            self.auto_cancel_on = timezone.now() + relativedelta(
                days=settings.AUTO_CANCEL_DAYS
            )
        self.save()

    def save(self, *args, **kwargs):
        if self.status == NEW and not self.id and not self.auto_cancel_on:
            if self.order.deliverables.all().count() == 0:
                # This is the first deliverable. Set the auto-cancel date.
                self.auto_cancel_on = timezone.now() + relativedelta(
                    days=settings.AUTO_CANCEL_DAYS
                )
            else:
                self.auto_cancel_on = None
        elif self.status is not NEW:
            self.auto_cancel_on = None
        if self.table_order:
            self.escrow_enabled = True
        if self.status in [NEW, PAYMENT_PENDING, WAITING]:
            self.international = (
                StripeAccount.objects.filter(
                    user=self.order.seller,
                )
                .exclude(country=settings.SOURCE_COUNTRY)
                .exists()
            )
        if not self.commission_info:
            self.commission_info = note_for_text(
                self.order.seller.artist_profile.commission_info
            )
        super().save(*args, **kwargs)


def deliverable_pre_pay(
    *, billable: Union["LineItem", "Invoice"], target: Deliverable, context: dict
) -> dict:
    if isinstance(billable, LineItem):
        # As yet, we don't have anything special here, but we may eventually.
        return {}
    deliverable = target
    try:
        ensure_buyer(deliverable.order)
    except AssertionError:
        raise AssertionError(
            "No buyer is set for this order, nor is there a customer email set."
        )
    return {}


def deliverable_post_pay(
    *,
    billable: Union["LineItem", "Invoice"],
    target: Deliverable,
    context: dict,
    records: List["TransactionRecord"],
) -> List["TransactionRecord"]:
    deliverable = target
    deliverable_ref = ref_for_instance(deliverable)
    for record in records:
        record.targets.add(deliverable_ref)
    if isinstance(billable, LineItem):
        # Let sellers know when they've gotten a tip.
        if billable.type == TIP:
            notify(TIP_RECEIVED, deliverable, unique=True, mark_unread=True)
        return records
    if not context.get("successful"):
        # Nothing to do here, the payment wasn't successful.
        return records
    if deliverable.final_uploaded:
        deliverable.status = REVIEW
        deliverable.auto_finalize_on = (timezone.now() + relativedelta(days=2)).date()
    elif deliverable.revision_set.all().exists():
        deliverable.status = IN_PROGRESS
    else:
        deliverable.status = QUEUED
    deliverable.revisions_hidden = False
    # Save the original turnaround/weight.
    deliverable.task_weight = (
        deliverable.product and deliverable.product.task_weight
    ) or deliverable.task_weight
    deliverable.expected_turnaround = (
        deliverable.product and deliverable.product.expected_turnaround
    ) or deliverable.expected_turnaround
    deliverable.dispute_available_on = (
        timezone.now()
        + BDay(
            ceil(
                ceil(
                    deliverable.expected_turnaround
                    + deliverable.adjustment_expected_turnaround
                )
                * 1.25
            )
        )
    ).date()
    deliverable.paid_on = timezone.now()
    deliverable.save()
    credit_referral(deliverable)
    notify(SALE_UPDATE, deliverable, unique=True, mark_unread=True)
    return records


def get_next_order_position():
    """
    Must be defined in root for migrations.
    """
    return get_next_increment(Order, "order_display_position")


def get_next_sale_position():
    """
    Must be defined in root for migrations.
    """
    return get_next_increment(Order, "sale_display_position")


def get_next_case_position():
    """
    Must be defined in root for migrations.
    """
    return get_next_increment(Order, "case_display_position")


class Order(Model):
    """
    Record of Order
    """

    preserve_comments = True
    comment_permissions = [OrderViewPermission]

    seller = ForeignKey(User, related_name="sales", on_delete=CASCADE)
    buyer = ForeignKey(
        User, related_name="buys", on_delete=CASCADE, null=True, blank=True
    )
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
        return {"order": self}

    def notification_display(self, context):
        return self.deliverables.first().notification_display(context)

    def notification_link(self, context):
        return order_context_to_link(
            order_context(order=self, logged_in=False, user=context["request"].user)
        )

    def notification_name(self, context):
        request = context["request"]
        if request.user == self.seller:
            return "Sale #{}".format(self.id)
        return "Order #{}".format(self.id)

    def save(
        self,
        *args,
        **kwargs,
    ) -> None:
        if self.private:
            self.hide_details = True
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["created_on"]


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
            type=SALE_UPDATE,
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
            type=COMMENT,
        ),
        Subscription(
            subscriber=instance.order.seller,
            content_type=deliverable_type,
            object_id=instance.id,
            email=False,
            type=TIP_RECEIVED,
        ),
    ] + buyer_subscriptions(instance, order_type=deliverable_type)
    Subscription.objects.bulk_create(subscriptions, ignore_conflicts=True)


def delete(queryset):
    for item in queryset:
        item.delete()


def idempotent_lines(instance: Deliverable):
    if instance.status not in [WAITING, NEW, PAYMENT_PENDING]:
        return
    main_qs = instance.invoice.lines_for(instance)
    if instance.status == PAYMENT_PENDING and instance.invoice.status == DRAFT:
        instance.invoice.status = OPEN
    if instance.product:
        line = main_qs.update_or_create(
            defaults={"amount": instance.product.base_price},
            invoice=instance.invoice,
            amount=instance.product.base_price,
            type=BASE_PRICE,
            destination_user=instance.order.seller,
            destination_account=ESCROW,
        )[0]
        line.annotate(instance)
    total = reckon_lines(main_qs.filter(priority__lt=PRIORITY_MAP[SHIELD]))
    escrow_enabled = instance.escrow_enabled and total
    plan = instance.order.seller.service_plan
    # Once this is in production long enough and all lines for existing deliverables
    # have been recalculated, this line can be removed.
    delete(main_qs.filter(type=BONUS))
    if instance.table_order:
        line = main_qs.update_or_create(
            defaults={
                "percentage": settings.TABLE_PERCENTAGE_FEE,
                "cascade_percentage": instance.cascade_fees,
                "amount": settings.TABLE_STATIC_FEE,
                # We don't cascade this flat amount for table products. Might revisit
                # this later.
                "cascade_amount": False,
            },
            invoice=instance.invoice,
            destination_user=None,
            destination_account=RESERVE,
            type=TABLE_SERVICE,
        )[0]
        line.annotate(instance)
        line = main_qs.update_or_create(
            defaults={
                "percentage": settings.TABLE_TAX,
                "cascade_percentage": instance.cascade_fees,
                "cascade_amount": instance.cascade_fees,
                "back_into_percentage": instance.cascade_fees,
            },
            invoice=instance.invoice,
            destination_user=None,
            destination_account=MONEY_HOLE_STAGE,
            type=TAX,
        )[0]
        line.annotate(instance)
        delete(main_qs.filter(type__in=[BONUS, SHIELD]))
        instance.invoice.record_only = False
    elif escrow_enabled:
        percentage = plan.shield_percentage_price
        if instance.international:
            percentage += settings.INTERNATIONAL_CONVERSION_PERCENTAGE
        line = main_qs.update_or_create(
            defaults={
                "percentage": percentage,
                "amount": plan.shield_static_price,
                "cascade_percentage": instance.cascade_fees,
                "cascade_amount": instance.cascade_fees,
                "back_into_percentage": not instance.cascade_fees,
            },
            invoice=instance.invoice,
            destination_user=None,
            destination_account=UNPROCESSED_EARNINGS,
            type=SHIELD,
        )[0]
        line.annotate(instance)
        delete(
            main_qs.filter(
                type=EXTRA,
                destination_account=RESERVE,
                description="Table Service",
                invoice=instance.invoice,
            )
        )
        delete(main_qs.filter(type__in=[TAX, DELIVERABLE_TRACKING]))
        instance.invoice.record_only = False
    else:
        delete(main_qs.filter(type__in=[BONUS, SHIELD]))
        delete(
            main_qs.filter(
                type=EXTRA,
                destination_account=RESERVE,
                description="Table Service",
                invoice=instance.invoice,
            )
        )
        delete(main_qs.filter(type=TAX))
        if plan.per_deliverable_price:
            line = main_qs.update_or_create(
                defaults={
                    "amount": plan.per_deliverable_price,
                    "cascade_amount": instance.cascade_fees,
                },
                invoice=instance.invoice,
                destination_user=None,
                type=DELIVERABLE_TRACKING,
                destination_account=UNPROCESSED_EARNINGS,
            )[0]
            line.annotate(instance)
        instance.invoice.record_only = True
    instance.invoice.save()


@receiver(pre_save, sender=Deliverable)
@disable_on_load
def ensure_invoice(sender, instance, **kwargs):
    if not instance.invoice:
        instance.invoice = Invoice.objects.create(
            bill_to=instance.order.buyer, issued_by=instance.order.seller
        )


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
            type=COMMENT,
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
        f"You have a new invoice from {instance.order.seller.username}!",
        "invoice_issued.html",
        instance.order.customer_email,
        {
            "deliverable": instance,
            "claim_token": get_claim_token(instance.order),
            "order": instance.order,
        },
    )


@receiver(post_delete, sender=Deliverable)
@disable_on_load
def auto_remove_order(sender, instance, **_kwargs):
    clear_events_subscriptions_and_comments(instance)


remove_deliverable_events = receiver(pre_delete, sender=Deliverable)(
    disable_on_load(clear_events)
)
remove_deliverable_markers = receiver(post_delete, sender=Deliverable)(
    disable_on_load(clear_markers)
)


@transaction.atomic
def update_artist_load(sender, instance, **_kwargs):
    seller = instance.order.seller
    result = Deliverable.objects.filter(
        order__seller_id=seller.id, status__in=WEIGHTED_STATUSES
    ).aggregate(base_load=Sum("task_weight"), added_load=Sum("adjustment_task_weight"))
    load = (result["base_load"] or 0) + (result["added_load"] or 0)
    if isinstance(instance, Deliverable) and instance.product:
        instance.product.parallel = (
            Deliverable.objects.filter(
                product_id=instance.product.id, status__in=WEIGHTED_STATUSES
            )
            .distinct()
            .count()
        )
        instance.product.save()
    # Availability update could be recursive, so get the latest version of the user.
    seller = User.objects.get(id=seller.id)
    update_availability(seller, load, seller.artist_profile.commissions_disabled)


order_load_check = receiver(post_save, sender=Deliverable, dispatch_uid="load")(
    disable_on_load(update_artist_load)
)
# No need for delete check-- orders are only ever archived, not deleted.


# noinspection PyUnusedLocal
@transaction.atomic
def update_product_availability(sender, instance, **kwargs):
    update_availability(
        instance.user,
        instance.user.artist_profile.load,
        instance.user.artist_profile.commissions_disabled,
    )


# noinspection PyUnusedLocal,PyUnusedLocal
@transaction.atomic
def update_user_availability(sender, instance, **kwargs):
    update_availability(instance.user, instance.load, instance.commissions_disabled)


@receiver(post_save, sender=Product)
def update_deliverable_line_items(sender, instance, **kwargs):
    invoices = Deliverable.objects.filter(
        product=instance, status__in=[NEW, PAYMENT_PENDING]
    ).values_list(
        "invoice",
        flat=True,
    )
    LineItem.objects.filter(invoice__in=invoices, type=BASE_PRICE).update(
        amount=instance.base_price
    )


@receiver(post_save, sender=InventoryTracker)
@disable_on_load
def update_tracker_availability(sender, instance, **kwargs):
    update_product_availability(sender, instance.product, **kwargs)


@receiver(post_delete, sender=InventoryTracker)
@disable_on_load
def clear_tracker_availability(sender, instance, **kwargs):
    update_product_availability(sender, instance.product, **kwargs)


product_availability_check_save = receiver(
    post_save, sender=Product, dispatch_uid="load"
)(disable_on_load(update_product_availability))
product_availability_check_delete = receiver(
    post_delete, sender=Product, dispatch_uid="load"
)(disable_on_load(update_product_availability))

user_availability_check_save = receiver(
    post_save, sender=ArtistProfile, dispatch_uid="load"
)(disable_on_load(update_user_availability))


class Rating(Model):
    """
    An individual star rating for a category.
    """

    stars = IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comments = CharField(max_length=1000, blank=True, default="")
    object_id = PositiveIntegerField(null=True, blank=True, db_index=True)
    content_type = ForeignKey(ContentType, on_delete=SET_NULL, null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
    target = ForeignKey("profiles.User", related_name="ratings", on_delete=CASCADE)
    rater = ForeignKey(
        "profiles.User", related_name="ratings_received", on_delete=CASCADE
    )
    created_on = DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return (
            f"{self.rater} rated {self.target} {self.stars} stars for "
            f"[{self.content_object}]"
        )


# noinspection PyUnusedLocal
@receiver(post_save, sender=Rating)
@disable_on_load
def tabulate_stars(sender, instance, **_kwargs):
    instance.target.stars = instance.target.ratings.all().aggregate(Avg("stars"))[
        "stars__avg"
    ]
    instance.target.rating_count = instance.target.ratings.all().count()
    instance.target.save()


class CreditCardToken(Model):
    """
    Card tokens are stored based on our processor's APIs. We don't store full card data
    to avoid issues with PCI compliance.
    """

    user = ForeignKey(User, related_name="credit_cards", on_delete=CASCADE)
    type = IntegerField(choices=CARD_TYPES, default=VISA)
    last_four = CharField(max_length=4)
    # Field for deprecated service, authorize.net. To be removed eventually.
    token = CharField(max_length=50, blank=True, default="")
    # Must have null available for unique to be True with blank entries.
    stripe_token = CharField(
        max_length=50, blank=True, default=None, null=True, db_index=True, unique=True
    )
    active = BooleanField(default=True, db_index=True)
    cvv_verified = BooleanField(default=False, db_index=True)
    created_on = DateTimeField(auto_now_add=True, db_index=True)
    watch_permissions = {"CardSerializer": [UserControls]}

    def __str__(self):
        return "%s ending in %s%s" % (
            self.get_type_display(),
            self.last_four,
            "" if self.active else " (Deleted)",
        )

    def delete(self, *args, **kwargs):
        """
        Prevent this function from working to avoid accidental deletion.

        We will not allow this to be done in any way but the most deliberate manner,
        since transaction records will exist for the card. So, instead, we raise an
        exception.

        To mark a card as deleted properly, use the mark_deleted function.
        """
        raise RuntimeError(
            "Credit card tokens are critical for historical billing information."
        )

    def mark_deleted(self):
        """
        Mark a card as deleted. Deleted cards are hidden away from the user, but kept
        for historical accounting purposes.
        """
        with stripe as stripe_api:
            delete_payment_method(api=stripe_api, method_token=self.stripe_token)
        self.active = False
        self.save()
        if self.user.primary_card == self:
            self.user.primary_card = None
            cards = self.user.credit_cards.filter(active=True).order_by("-created_on")
            if cards:
                self.user.primary_card = cards[0]
            self.user.save()

    def announce_channels(self):
        return [
            f"profiles.User.pk.{self.user.id}.all_cards",
            f"profiles.User.pk.{self.user.id}.stripe_cards",
        ]

    def save(self, **kwargs):
        if not (self.stripe_token or self.token):
            raise ValidationError("No token for any upstream card provider!")
        return super().save(**kwargs)


class TransactionRecord(Model):
    """
    Model for tracking the movement of money.
    """

    id = ShortCodeField(primary_key=True, db_index=True, default=gen_shortcode)

    status = IntegerField(choices=TRANSACTION_STATUSES, db_index=True)
    source = IntegerField(choices=ACCOUNT_TYPES, db_index=True)
    destination = IntegerField(choices=ACCOUNT_TYPES, db_index=True)
    category = IntegerField(choices=CATEGORIES, db_index=True)
    payer = ForeignKey(
        User, null=True, blank=True, related_name="debits", on_delete=PROTECT
    )
    payee = ForeignKey(
        User, null=True, blank=True, related_name="credits", on_delete=PROTECT
    )
    card = ForeignKey(CreditCardToken, null=True, blank=True, on_delete=SET_NULL)
    created_on = DateTimeField(db_index=True, default=timezone.now)
    finalized_on = DateTimeField(db_index=True, default=None, null=True, blank=True)
    amount = MoneyField(max_digits=8, decimal_places=2, default_currency="USD")
    targets = ManyToManyField(
        to="lib.GenericReference", related_name="referencing_transactions", blank=True
    )
    auth_code = CharField(max_length=6, default="", db_index=True, blank=True)
    remote_ids = JSONField(default=list)
    response_message = TextField(default="", blank=True)
    note = TextField(default="", blank=True)

    class Meta:
        ordering = ("-finalized_on", "-created_on", "id")

    def __str__(self):
        return (
            f"{self.get_status_display()} [{self.get_category_display()}]: "
            f"{self.amount} from "
            f'{self.payer or "(Artconomy)"} [{self.get_source_display()}] to '
            f'{self.payee or "(Artconomy)"} [{self.get_destination_display()}] for '
            f"{self.target_string}"
        )

    @property
    def target_string(self):
        count = self.targets.all().count()
        if not count:
            return "None"
        base_string = str(self.targets.all().first().target)
        if count == 1:
            return base_string
        count -= 1
        return base_string + f" and {count} other(s)."

    def save(self, *args, **kwargs):
        if (self.status in [SUCCESS, FAILURE]) and (self.finalized_on is None):
            self.finalized_on = timezone.now()
        return super().save(*args, **kwargs)


class Invoice(models.Model):
    id = ShortCodeField(primary_key=True, db_index=True, default=gen_shortcode)
    status = models.IntegerField(default=DRAFT, choices=INVOICE_STATUSES)
    watch_permissions = {
        "InvoiceSerializer": [Any(UserControls, BillTo, IssuedBy)],
        None: [Any(UserControls, BillTo, IssuedBy)],
    }
    type = models.IntegerField(default=SALE, choices=INVOICE_TYPES)
    bill_to = models.ForeignKey(
        User, null=True, on_delete=CASCADE, related_name="invoices_billed_to"
    )
    issued_by = models.ForeignKey(
        User,
        null=True,
        on_delete=SET_NULL,
        blank=True,
        related_name="invoices_issued_by",
    )
    created_on = models.DateTimeField(default=timezone.now, db_index=True)
    due_date = models.DateField(
        default=timezone.now, db_index=True, null=True, blank=True
    )
    paid_on = models.DateTimeField(null=True, db_index=True, blank=True)
    expires_on = models.DateTimeField(
        null=True, blank=True, db_index=True, default=None
    )
    # We don't currently use stripe Invoices, but we anticipate doing so.
    stripe_token = models.CharField(
        default="", db_index=True, max_length=50, blank=True
    )
    current_intent = CharField(max_length=30, db_index=True, default="", blank=True)
    record_only = models.BooleanField(default=False, db_index=True)
    # Used to look up invoices made manually at a table event.
    manually_created = models.BooleanField(default=False, db_index=True)
    payout_sent = models.BooleanField(default=False, db_index=True)
    # Used to flag whether this invoice can send a payout when paid. This will be false
    # for deliverables, since they have to finish escrow. In that case, this flag will
    # be set True upon completion of the deliverable. For tip invoices, this is
    # immediately True.
    payout_available = models.BooleanField(default=False, db_index=True)
    # You should also add the targets to the line item annotations if adding them here.
    # This is used to make lookups for things like 'the invoice for this deliverable'
    # easier, though in the future it's possible that we could have multiple
    # deliverables on an invoice.
    #
    # The reason why this is useful rather than just querying line items is that it's
    # possible that someone might be billed for an action taken regarding a deliverable,
    # rather than the invoice being for the work of the deliverable itself. This makes
    # querying just a bit easier for the deliverable's
    # work invoice.
    targets = ManyToManyField(
        to="lib.GenericReference", related_name="referencing_invoices", blank=True
    )

    def total(self) -> Money:
        return reckon_lines(self.line_items.all())

    def context_for(self, target):
        # Provided for compatibility in post_payment hook. We might eventually allow for
        # more specific annotations like we do with LineItems.
        return {}

    def lines_for(self, target):
        from apps.lib.models import ref_for_instance

        return self.line_items.filter(targets=ref_for_instance(target))

    def __str__(self):
        result = (
            f"Invoice {self.id} [{self.get_type_display()}] for {self.bill_to} in the "
            f"amount of {self.total()}"
        )
        deliverable = self.deliverables.first()
        if deliverable:
            result += f" for deliverable: {deliverable}"
        return result

    class Meta:
        ordering = ("-created_on",)


class LineItemAnnotation(models.Model):
    """
    Annotation for a line item on an invoice. Useful to trigger post-payment effects.
    """

    target = ForeignKey("lib.GenericReference", on_delete=CASCADE)
    line_item = ForeignKey("sales.LineItem", on_delete=CASCADE)
    # Do not allow users to set custom keys here, as it could lead to arbitrary code
    # execution.
    context = JSONField(default=dict)


class LineItem(Model):
    type = IntegerField(choices=LINE_ITEM_TYPES, db_index=True)
    invoice = ForeignKey(
        Invoice, on_delete=CASCADE, related_name="line_items", null=True
    )
    amount = MoneyField(
        max_digits=6,
        decimal_places=2,
        default_currency="USD",
        blank=True,
        default=0,
    )
    frozen_value = MoneyField(
        max_digits=6,
        decimal_places=2,
        default_currency="USD",
        blank=True,
        null=True,
        default=None,
        help_text="Snapshotted amount after calculations have been completed and the "
        "relevant invoice is paid. This helps keep historical record in case "
        "the line item calculation algorithms change.",
    )
    percentage = DecimalField(max_digits=5, db_index=True, decimal_places=3, default=0)
    # Line items will be run in layers to get our totals/subtotals. Higher numbers will
    # be run after lower numbers. If two items have the same priority, they will both be
    # run as if the other had not been run.
    priority = IntegerField(db_index=True)
    cascade_percentage = BooleanField(db_index=True, default=False)
    cascade_amount = BooleanField(db_index=True, default=False)
    back_into_percentage = BooleanField(db_index=True, default=False)
    destination_user = ForeignKey(
        User, null=True, db_index=True, on_delete=CASCADE, blank=True
    )
    destination_account = IntegerField(choices=ACCOUNT_TYPES)
    description = CharField(max_length=250, blank=True, default="")
    watch_permissions = {
        "LineItemSerializer": [Any(OrderViewPermission, BillTo, IssuedBy, IsStaff)]
    }
    targets = ManyToManyField(
        "lib.GenericReference", through=LineItemAnnotation, related_name="line_items"
    )

    def __str__(self):
        return (
            f"{self.get_type_display()} ({self.amount}, {self.percentage}) for "
            f"#{self.invoice.id}, priority {self.priority}"
        )

    @property
    def deliverable(self):
        return Deliverable.objects.filter(invoice=self.invoice).first()

    def announce_channels(self):
        deliverable = self.deliverable
        channels = []
        if deliverable:
            channels.append(f"sales.Deliverable.pk.{deliverable.id}.line_items")
        channels.append(f"sales.Invoice.pk.{self.invoice.id}.line_items")
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
    amount: Money = Money("0", "USD")
    percentage: Decimal = Decimal(0)
    cascade_percentage: bool = False
    cascade_amount: bool = False
    back_into_percentage: bool = False
    type: int = BASE_PRICE
    description: str = ""


class Revision(ImageModel):
    comment_permissions = [OrderViewPermission]
    preserve_comments = True
    deliverable = ForeignKey(Deliverable, on_delete=CASCADE)
    approved_on = DateTimeField(default=None, blank=True, null=True)
    comments = GenericRelation(
        Comment,
        related_query_name="revisions",
        content_type_field="content_type",
        object_id_field="object_id",
    )

    def __str__(self):
        return f"Revision {self.id} for {self.deliverable}"

    def modified_kwargs(self, _data):
        return {"order": self.deliverable.order, "deliverable": self.deliverable}

    def can_reference_asset(self, user):
        return (user == self.owner and not self.deliverable.order.private) or (
            (user == self.deliverable.order.buyer)
            and self.deliverable.status == COMPLETED
        )

    def notification_link(self, context):
        return order_context_to_link(
            order_context(
                order=self.deliverable.order,
                deliverable=self.deliverable,
                logged_in=False,
                user=context["request"].user,
                extra_params={"revisionId": self.id},
                view_name="DeliverableRevision",
            ),
        )

    def notification_serialize(self, context):
        from apps.sales.serializers import RevisionSerializer

        if context["request"].user == self.owner:
            return RevisionSerializer(instance=self, context=context).data
        return {"id": self.id}

    def notification_display(self, context):
        from apps.sales.serializers import RevisionSerializer

        return RevisionSerializer(instance=self, context=context).data

    def notification_name(self, context):
        return (
            f"Revision ID #{self.id} on {self.deliverable.notification_name(context)}"
        )

    class Meta:
        ordering = ["created_on"]


revision_thumbnailer = receiver(post_save, sender=Revision)(thumbnail_hook)
revision_clear = receiver(post_delete, sender=Revision)(clear_markers)


@receiver(post_save, sender=Revision)
def create_revision_subscription(sender, instance, created, **kwargs):
    if not created:
        return
    Subscription.objects.create(
        content_type_id=ContentType.objects.get_for_model(instance).id,
        object_id=instance.id,
        subscriber=instance.owner,
        type=REVISION_APPROVED,
        email=True,
    )


def deliverable_from_context(context, check_request=True):
    # This data not to be trusted. It is user provided.
    deliverable = context["extra_data"].get("deliverable", None)
    if deliverable is not None:
        try:
            deliverable = int(deliverable)
            deliverable = Deliverable.objects.get(id=deliverable)
            if check_request:
                if not OrderViewPermission().has_object_permission(
                    context["request"], None, deliverable
                ):
                    raise ValueError
            return deliverable
        except (ValueError, Deliverable.DoesNotExist):
            return None


class Reference(ImageModel):
    """
    NOTE: References have to have their subscriptions created at the point of creation,
    as signals would not indicate which deliverable is being dealt with.
    """

    comment_permissions = [Any(ReferenceViewPermission, IsStaff)]
    preserve_comments = True
    deliverables = ManyToManyField(Deliverable)
    comments = GenericRelation(
        Comment,
        related_query_name="references",
        content_type_field="content_type",
        object_id_field="object_id",
    )

    def can_reference_asset(self, user):
        # Despite this being a reference, it should never be the source for any other
        # models/sharing.
        return False

    def modified_kwargs(self, data):
        deliverable = deliverable_from_context(
            {"extra_data": data}, check_request=False
        )
        if deliverable is None:
            return {}
        if not self.deliverables.filter(id=deliverable.id).exists():
            return {}
        return {"order": deliverable.order, "deliverable": deliverable}

    def notification_display(self, context):
        from apps.sales.serializers import ReferenceSerializer

        return ReferenceSerializer(context=context, instance=self).data

    def notification_link(self, context):
        deliverable = context.get("deliverable", deliverable_from_context(context))
        if deliverable is None:
            return None
        return order_context_to_link(
            order_context(
                order=deliverable.order,
                deliverable=deliverable,
                user=context["request"].user,
                view_name="DeliverableReference",
                extra_params={"referenceId": self.id},
                logged_in=False,
            )
        )

    def notification_name(self, context):
        deliverable = deliverable_from_context(context)
        return (
            f"Reference ID #{self.id} for "
            f"{deliverable and deliverable.notification_name(context)}"
        )

    class Meta:
        ordering = ["created_on"]


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
        type=COMMENT,
    )
    if instance.deliverable.arbitrator:
        Subscription.objects.create(
            subscriber=instance.deliverable.arbitrator,
            content_type=content_type,
            object_id=instance.id,
            email=True,
            type=COMMENT,
        )
    if not instance.deliverable.order.buyer:
        return
    Subscription.objects.create(
        subscriber=instance.deliverable.order.buyer,
        content_type=content_type,
        object_id=instance.id,
        email=True,
        type=COMMENT,
    )


revision_comment_receiver = receiver(post_save, sender=Revision)(auto_subscribe_image)


@receiver(post_delete, sender=Reference)
@disable_on_load
def delete_comments_and_events(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(instance)
    Event.objects.filter(object_id=instance.id, content_type=content_type).delete()
    Subscription.objects.filter(
        object_id=instance.id, content_type=content_type
    ).delete()
    Comment.objects.filter(object_id=instance.id, content_type=content_type).delete()
    Comment.objects.filter(
        top_object_id=instance.id, top_content_type=content_type
    ).delete()
    Event.objects.filter(data__reference=instance.id).delete()


class BankAccount(Model):
    """
    This was the model used to track Dwolla bank accounts for transfers.

    It is no longer used-- payouts via Dwolla have been removed, and we only retain
    these for record keeping purposes. Don't change the data on these entries.
    """

    CHECKING = 0
    SAVINGS = 1
    ACCOUNT_TYPES = ((CHECKING, "Checking"), (SAVINGS, "Savings"))
    user = ForeignKey(User, on_delete=CASCADE, related_name="banks")
    url = URLField()
    last_four = CharField(max_length=4)
    type = IntegerField(choices=ACCOUNT_TYPES)
    deleted = BooleanField(default=False)
    processor = "dwolla"

    # noinspection PyUnusedLocal
    def notification_serialize(self, context):  # pragma: no cover
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
        return f'Webhook {self.id}{" (Connect)" if self.connect else ""}'


class StripeAccount(Model):
    id = ShortCodeField(primary_key=True, db_index=True, default=gen_shortcode)
    user = OneToOneField(User, on_delete=CASCADE, related_name="stripe_account")
    country = CharField(max_length=2, db_index=True)
    active = BooleanField(default=False, db_index=True)
    token = CharField(max_length=50, db_index=True)
    processor = "stripe"
    watch_permissions = {"StripeAccountSerializer": [UserControls]}

    def announce_channels(self):
        return [f"profiles.User.pk.{self.user_id}.stripe_accounts"]

    def delete(self, using=None, keep_parents=False):
        with stripe as api:
            api.Account.delete(self.token)
        return super(StripeAccount, self).delete()


@receiver(post_save, sender=StripeAccount)
def update_stripe_products(instance, *args, **kwargs):
    international = instance.country != settings.SOURCE_COUNTRY
    # Need to invoke post_save hooks on the products
    for product in instance.user.products.all():
        product.international = international
        product.save()


class ServicePlan(models.Model):
    """
    Service plans describe levels of service for users.
    """

    post_pay_hook = "apps.sales.models.service_plan_post_pay"
    name = models.CharField(max_length=100, db_index=True, unique=True)
    description = models.CharField(max_length=1000)
    features = JSONField(default=list)
    sort_value = models.IntegerField(default=0, db_index=True)
    monthly_charge = MoneyField(
        default=Money("0.00", "USD"),
        db_index=True,
        help_text="Monthly subscription price.",
        max_digits=5,
        decimal_places=2,
    )
    per_deliverable_price = MoneyField(
        default=Money("0.00", "USD"),
        db_index=True,
        help_text="Amount we charge for each deliverable tracked.",
        max_digits=5,
        decimal_places=2,
    )
    max_simultaneous_orders = models.IntegerField(
        default=0,
        help_text="How many simultaneous orders are permitted. 0 means infinite.",
    )
    tipping = models.BooleanField(
        default=False,
        help_text="Whether tips are available for orders.",
    )
    waitlisting = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether the seller can add waitlist products or else waitlist a "
        "particular order.",
    )
    shield_static_price = MoneyField(
        default=Money("1.50", "USD"),
        help_text="Static amount charged per shield order. Replaces the per "
        "deliverable price on shield orders.",
        max_digits=5,
        decimal_places=2,
    )
    shield_percentage_price = DecimalField(
        default=Decimal("8"),
        help_text="Percentage amount applied to shield orders.",
        max_digits=5,
        decimal_places=2,
    )
    hidden = models.BooleanField(default=False)
    discord_role_id = models.CharField(
        db_index=True,
        help_text="Discord role ID to add to users who have this service plan.",
        max_length=30,
        default="",
    )

    def __str__(self):
        return f"{self.name} (#{self.id})"


class StripeLocation(models.Model):
    """
    Model to represent a location in the Stripe API
    """

    id = ShortCodeField(primary_key=True, default=gen_shortcode)
    name = CharField(max_length=150)
    stripe_token = CharField(max_length=50, default="", blank=True)
    line1 = CharField(max_length=250)
    line2 = CharField(max_length=250, default="", blank=True)
    city = CharField(max_length=250, default="", blank=True)
    state = CharField(max_length=5, default="", blank=True)
    postal_code = CharField(max_length=20, default="", blank=True)
    country = CharField(max_length=2)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) -> None:
        with stripe as stripe_api:
            address = {"line1": self.line1, "country": self.country}
            for field in ["city", "state", "postal_code", "line2"]:
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
                self.stripe_token = location["id"]
            super().save()

    def delete(self, *args, **kwargs):
        with stripe as stripe_api:
            stripe_api.terminal.Location.delete(self.stripe_token)
        super().delete(*args, **kwargs)


class StripeReader(models.Model):
    """
    Model to represent terminals in the API.
    """

    registration_code = ""
    id = ShortCodeField(primary_key=True, default=gen_shortcode)
    name = CharField(max_length=150, db_index=True)
    stripe_token = CharField(max_length=50)
    virtual = BooleanField(default=False)
    created_on = DateTimeField(default=timezone.now, db_index=True)
    location = ForeignKey(
        StripeLocation,
        on_delete=CASCADE,
        help_text="Primary location where reader will be used. Cannot be changed after "
        "it is initially set. You must delete the reader and recreate it to "
        "change its location.",
    )

    def __str__(self):
        return f"{self.name} at {self.location and self.location.name} (#{self.id})"

    def save(self, *args, **kwargs) -> None:
        with stripe as stripe_api:
            if not self.stripe_token:
                reader = stripe_api.terminal.Reader.create(
                    label=self.name,
                    location=self.location.stripe_token,
                    registration_code=self.registration_code,
                )
                if self.registration_code.startswith("simulated"):
                    self.virtual = True
                self.stripe_token = reader["id"]
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

    class Meta:
        ordering = ("created_on",)


# Force load of registrations for serializers.


def service_plan_post_pay(
    *,
    billable: Union[LineItem, Invoice],
    target: ServicePlan,
    context: dict,
    records: List["TransactionRecord"],
):
    if not context["successful"]:
        return records
    if not hasattr(billable, "invoice"):  # pragma: no cover
        raise RuntimeError(
            "Post payment hook for service called on the invoice level rather than on "
            "the line item level. This should not happen-- we're tracking service "
            "plans at the line item level.",
        )
    invoice = billable.invoice
    service_plan = target
    user = invoice.bill_to
    # Subscription type invoices are for starting new subscriptions. Term invoices are
    # for continuing existing ones.
    set_next = invoice.type == SUBSCRIPTION
    set_service_plan(
        user,
        service_plan,
        next_plan=set_next and service_plan,
        target_date=timezone.now().date() + relativedelta(months=1),
    )
    user.current_intent = ""
    user.save(update_fields=["current_intent"])
    return records
