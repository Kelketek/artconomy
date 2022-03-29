from collections import defaultdict
from decimal import Decimal
from functools import lru_cache
from itertools import chain
from typing import List
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.validators import EmailValidator, MinValueValidator
from django.db.models import Sum, QuerySet, Q
from dotted_dict import DottedDict
from moneyed import Money
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, DecimalField, IntegerField, FloatField, EmailField, ModelField, \
    ListField, BooleanField
from short_stuff import unslugify
from short_stuff.django.serializers import ShortCodeField

from apps.lib.abstract_models import GENERAL, EXTREME, RATINGS
from apps.lib.models import Asset
from apps.lib.consumers import register_serializer
from apps.lib.models import ref_for_instance
from apps.lib.serializers import (
    RelatedUserSerializer, RelatedAssetField, EventTargetRelatedField, SubscribedField,
    TagListField, RelatedAtomicMixin,
    MoneyToFloatField)
from apps.lib.utils import add_check, check_read
from apps.profiles.models import User, Submission, Character
from apps.profiles.serializers import CharacterSerializer, SubmissionSerializer
from apps.profiles.utils import available_users
from apps.sales.constants import STRIPE, AUTHORIZE, BASE_PRICE, ADD_ON, TIP, EXTRA, WAITING, NEW, PAYMENT_PENDING, \
    ESCROW, HOLDINGS, BANK, UNPROCESSED_EARNINGS, SUCCESS, CARD_TRANSACTION_FEES, RESERVE, CARD, CASH_DEPOSIT, \
    MONEY_HOLE, ACH_TRANSACTION_FEES, TIPPING, LIMBO
from apps.sales.models import (
    Product, Order, CreditCardToken, Revision, BankAccount,
    LineItemSim, Rating, TransactionRecord, LineItem, InventoryTracker,
    Deliverable, Reference,
    StripeAccount, Invoice, StripeReader, ServicePlan,
)
from apps.sales.utils import account_balance, PENDING, POSTED_ONLY, AVAILABLE, order_context, \
    order_context_to_link, lines_for_product
from apps.sales.line_item_funcs import get_totals, reckon_lines


class ProductSerializer(RelatedAtomicMixin, serializers.ModelSerializer):
    save_related = True
    user = RelatedUserSerializer(read_only=True)
    primary_submission = SubmissionSerializer(required=False, allow_null=True)
    tags = TagListField(required=False)
    base_price = MoneyToFloatField()
    starting_price = MoneyToFloatField(read_only=True)
    shield_price = MoneyToFloatField(read_only=True)
    expected_turnaround = FloatField()

    def __init__(self, *args, **kwargs):
        self.related_list = kwargs.get('related_list', None)
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if not request:
            return
        if request.user.is_staff:
            self.fields['featured'].read_only = False
            self.fields['catalog_enabled'].read_only = False
            self.fields['table_product'].read_only = False
        self.subject = getattr(request, 'subject', None)
        if self.subject and self.subject.is_registered and self.subject.landscape:
            self.fields['wait_list'].read_only = False

    def validate_base_price(self, value):
        if value < 0:
            raise ValidationError('Price cannot be negative.')
        return Money(value, settings.DEFAULT_CURRENCY)

    def validate_primary_submission(self, value):
        if value is None:
            return None
        try:
            Submission.objects.get(id=value.id, artists=self.instance.user)
        except Submission.DoesNotExist:
            raise ValidationError("That submission does not exist, or you cannot use it as your sample.")
        return value

    def validate_tags(self, value):
        add_check(self.instance, 'tags', replace=True, *value)
        return value

    def validate(self, data):
        errors = defaultdict(list)
        instance = self.instance or DottedDict(**data)
        revised = DottedDict()
        for field in self.fields:
            setattr(revised, field, getattr(instance, field, None))
        revised.update(data)
        if not getattr(revised, 'user', None):
            revised.user = self.context['request'].subject
        escrow_enabled = revised.escrow_enabled and self.context['request'].subject.artist_profile.escrow_enabled
        data.escrow_enabled = escrow_enabled
        minimum = settings.MINIMUM_PRICE
        total = reckon_lines(lines_for_product(revised))
        if escrow_enabled and (total < minimum):
            errors['escrow_enabled'].append(
                f'Cannot have shield enabled on products whose total is less than {minimum}'
            )
            errors['base_price'].append(
                f'Value too small to have shield enabled. Raise until the total is at least {minimum}.'
            )
        shield_total = reckon_lines(lines_for_product(revised, force_shield=True))
        if revised.escrow_upgradable and (shield_total < minimum):
            errors['escrow_enabled'].append(
                f'Cannot have shield enabled on products whose total would be less than {minimum}'
            )
            errors['base_price'].append(
                f'Value too small to have shield upgrade available. Raise until the total is at least {minimum}.'
            )
        if errors:
            raise ValidationError(errors)
        return data

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'revisions', 'hidden', 'max_parallel', 'max_rating', 'task_weight',
            'expected_turnaround', 'user', 'base_price', 'starting_price', 'shield_price', 'tags', 'available',
            'primary_submission', 'featured', 'hits', 'escrow_enabled', 'table_product', 'track_inventory', 'wait_list',
            'catalog_enabled', 'cascade_fees', 'escrow_upgradable', 'international',
        )
        read_only_fields = ('tags', 'featured', 'table_product', 'starting_price', 'shield_price', 'international')
        extra_kwargs = {'price': {'required': True}}


class CharacterValidationMixin:
    def validate_characters(self, value):
        value = Character.objects.filter(id__in=value)
        for character in value:
            user = self.context['request'].user
            if not (user.is_staff or character.user == user):
                private = character.private and not character.shared_with.filter(id=user.id)
                if private or not character.open_requests:
                    raise serializers.ValidationError(
                        'You are not permitted to commission pieces for all of the characters you have specified, or '
                        'one or more characters you specified does not exist.'
                    )
        return value


class ProductValidationMixin:
    def validate_product(self, value):
        if value is None:
            return None
        product = self.context['seller'].products.exclude(active=False).filter(id=value).first()
        if not product:
            raise ValidationError("You don't have a product with that ID.")
        return product


class PriceValidationMixin:
    def validate_price(self, value):
        if self.context['seller'].artist_profile.escrow_enabled:
            if value and (value < settings.MINIMUM_PRICE.amount):
                raise ValidationError('Must be $0 or at least ${}'.format(settings.MINIMUM_PRICE.amount))
        return value


class ProductNameMixin:
    def get_product_name(self, order):
        try:
            deliverable = order.deliverables.get()
        except Deliverable.MultipleObjectsReturned:
            return '(Multi-part order)'
        name = deliverable.product and deliverable.product.name
        if not name:
            return '(Custom Order)'
        return name


class ProductNewOrderSerializer(ProductNameMixin, serializers.ModelSerializer, CharacterValidationMixin):
    email = EmailField(write_only=True, required=False, allow_blank=True)
    seller = RelatedUserSerializer(read_only=True)
    buyer = RelatedUserSerializer(read_only=True)
    characters = ListField(child=IntegerField(), required=False)
    references = ListField(
        child=serializers.CharField(), required=False, write_only=True,
        max_length=10,
    )
    rating = ModelField(model_field=Deliverable()._meta.get_field('rating'))
    details = ModelField(model_field=Deliverable()._meta.get_field('details'), max_length=5000)
    escrow_upgrade = BooleanField()
    product_name = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        requires_email = any([
            not self.context['request'].user.is_authenticated,
            self.context['request'].user.is_staff and self.context['product'].table_product,
        ])
        if requires_email:
            del self.fields['characters']
            self.fields['email'].required = True
            self.fields['email'].allow_blank = False

    def validate_references(self, value):
        value = set(value)
        assets = Asset.objects.filter(id__in=value)
        error_message = 'Either you do not have permission to use those assets for reference, those asset IDs are ' \
                        'invalid, or they have expired. Please try re-uploading.'
        if assets.count() < len(value):
            raise serializers.ValidationError(error_message)
        for asset in assets:
            request = self.context['request']
            if not asset.can_reference(request):
                raise serializers.ValidationError(error_message)
        return assets

    def create(self, validated_data):
        data = {
            key: value for key, value in validated_data.items() if key not in (
                'characters', 'references', 'details', 'rating', 'email',
                'escrow_upgrade',
            )}
        return super().create(data)

    class Meta:
        model = Order
        fields = (
            'id', 'created_on', 'rating', 'details', 'seller', 'buyer', 'private',
            'email', 'characters', 'references', 'product_name', 'escrow_upgrade',
        )
        extra_kwargs = {
            'characters': {'required': False},
        }
        read_only_fields = (
            'status', 'id', 'created_on', 'default_path',
        )


class OrderViewSerializer(ProductNameMixin, RelatedAtomicMixin, serializers.ModelSerializer):
    claim_token = serializers.SerializerMethodField()
    seller = RelatedUserSerializer(read_only=True)
    buyer = RelatedUserSerializer(read_only=True)
    deliverable_count = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()

    def get_deliverable_count(self, obj):
        return obj.deliverables.count()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, 'instance'):  # pragma: no cover
            return
        try:
            self.is_seller
        except (KeyError, AttributeError) as err:  # pragma: no cover
            # Can happen if the instance property is a queryset/list, which can happen
            # on list endpoints.
            return
        if self.is_seller:
            if (not self.instance.buyer) or (self.instance.buyer.guest and not self.instance.buyer.verified_email):
                self.fields['customer_email'].read_only = False
            self.fields['hide_details'].read_only = False
        if not self.instance.buyer:
            self.fields['customer_email'].allow_blank = True

    @property
    def is_seller(self):
        user = self.context['request'].user
        return (user == self.instance.seller) or user.is_staff

    def get_claim_token(self, order):
        user = self.context['request'].user
        if user == order.buyer and order.claim_token:
            return order.claim_token
        return None

    class Meta:
        model = Order
        fields = (
            'id', 'seller', 'buyer', 'private', 'hide_details', 'customer_email', 'claim_token',
            'deliverable_count', 'product_name',
        )
        read_only_fields = fields


class NewDeliverableSerializer(
    RelatedAtomicMixin, CharacterValidationMixin, PriceValidationMixin, serializers.ModelSerializer,
    ProductValidationMixin,
):
    characters = ListField(child=IntegerField(), required=False)
    references = ListField(child=IntegerField(), required=False)
    product = serializers.IntegerField(allow_null=True)
    price = serializers.DecimalField(
        max_digits=6, decimal_places=2,
    )
    task_weight = serializers.IntegerField(min_value=0)
    revisions = serializers.IntegerField(min_value=0)
    details = serializers.CharField(max_length=5000)
    hold = serializers.BooleanField()
    rating = serializers.IntegerField(min_value=GENERAL, max_value=EXTREME)
    completed = serializers.BooleanField()
    paid = serializers.BooleanField()
    expected_turnaround = serializers.DecimalField(
        max_digits=5, decimal_places=2, min_value=settings.MINIMUM_TURNAROUND,
    )

    def validate_references(self, references):
        return Reference.objects.filter(id__in=references, deliverables__order__seller=self.context['seller'])

    def create(self, validated_data):
        validated_data = {**validated_data}
        for field_name in ['hold', 'completed', 'paid', 'price', 'characters', 'references']:
            validated_data.pop(field_name, None)
        return super(NewDeliverableSerializer, self).create(validated_data)

    class Meta:
        model = Deliverable
        fields = (
            'name', 'characters', 'price', 'revisions', 'details', 'details', 'hold', 'expected_turnaround',
            'completed', 'paid', 'task_weight', 'references', 'rating', 'product', 'cascade_fees',
        )


@register_serializer
class DeliverableSerializer(RelatedAtomicMixin, serializers.ModelSerializer):
    arbitrator = RelatedUserSerializer(read_only=True)
    outputs = SubmissionSerializer(many=True, read_only=True)
    product = ProductSerializer(read_only=True)
    subscribed = SubscribedField(required=False)
    expected_turnaround = FloatField(read_only=True)
    adjustment_expected_turnaround = FloatField(read_only=True, max_value=1000, min_value=-1000)
    display = serializers.SerializerMethodField()
    processor = serializers.CharField(read_only=True)
    order = OrderViewSerializer(read_only=True)
    read = serializers.SerializerMethodField()
    invoice = serializers.SerializerMethodField()
    tip_invoice = serializers.SerializerMethodField()

    def get_read(self, obj):
        return check_read(obj=obj, user=self.context['request'].user)

    def invoice_field(self, obj, key):
        # Can get triggered when loaded with a list. In that case there is no sensible answer.
        if not isinstance(obj, Deliverable):  # pragma: no cover
            return ''
        if self.is_buyer or self.is_seller or self.context['request'].user.is_staff:
            return getattr(getattr(obj, key, None), 'id', None)
        return None

    def get_invoice(self, obj):
        return self.invoice_field(obj, 'invoice')

    def get_tip_invoice(self, obj):
        return self.invoice_field(obj, 'tip_invoice')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not (args or kwargs):  # pragma: no cover
            # We're in the class definition. I can't remember when and where (nor why) this happens,
            # so I don't have a test for it, but it does.
            return
        try:
            self.is_seller
        except (KeyError, AttributeError):  # pragma: no cover
            return
        if self.is_buyer and self.instance.status in [NEW, WAITING, LIMBO]:
            for field_name in [
                'details', 'rating',
            ]:
                self.fields[field_name].read_only = False
        if self.is_seller:
            if self.instance.status in [NEW, WAITING]:
                for field_name in [
                    'adjustment_expected_turnaround', 'adjustment_task_weight', 'adjustment_revisions',
                    'name', 'cascade_fees', 'rating', 'details',
                ]:
                    self.fields[field_name].read_only = False
                if (not self.instance.table_order) and self.instance.order.seller.escrow_available:
                    self.fields['escrow_enabled'].read_only = False
            # Should never be harmful. Helpful in many statuses.
            self.fields['stream_link'].read_only = False

    def validate_adjustment_revisions(self, val):
        base = self.instance.product or self.instance
        if base.revisions + val < 0:
            raise ValidationError('Total revisions may not be less than 0.')
        return val

    def validate_adjustment_task_weight(self, val):
        adjustment_task_weight = Decimal(val)
        base = self.instance.product or self.instance
        if base.task_weight + adjustment_task_weight < 1:
            raise ValidationError('Task weight may not be less than 1.')
        return adjustment_task_weight

    def validate_adjustment_expected_turnaround(self, val):
        adjustment_expected_turnaround = Decimal(val)
        base_turnaround = (self.instance.product and self.instance.product.expected_turnaround) or 0
        adjusted_turnaround = base_turnaround + adjustment_expected_turnaround
        if adjusted_turnaround < settings.MINIMUM_TURNAROUND:
            raise ValidationError('Expected turnaround may not be less than {}'.format(
                settings.MINIMUM_TURNAROUND
            ))
        return adjustment_expected_turnaround

    @property
    def is_seller(self):
        if not isinstance(self.instance, Deliverable):
            return False
        user = self.context['request'].user
        return (user == self.instance.order.seller) or user.is_staff

    @property
    def is_buyer(self):
        if not isinstance(self.instance, Deliverable):
            return False
        user = self.context['request'].user
        return (user == self.instance.order.buyer) or user.is_staff

    def get_display(self, obj):
        return obj.notification_display(context=self.context)

    class Meta:
        model = Deliverable
        fields = (
            'id', 'created_on', 'status', 'details',
            'stream_link', 'revisions', 'outputs', 'subscribed', 'adjustment_task_weight',
            'adjustment_expected_turnaround', 'expected_turnaround', 'task_weight', 'paid_on', 'dispute_available_on',
            'auto_finalize_on', 'started_on', 'escrow_enabled', 'revisions_hidden', 'final_uploaded', 'arbitrator',
            'display', 'rating', 'commission_info', 'adjustment_revisions',
            'table_order', 'trust_finalized', 'order', 'name', 'product', 'read', 'processor',
            'invoice', 'tip_invoice', 'cascade_fees', 'international',
        )
        read_only_fields = [field for field in fields if field != 'subscribed']
        extra_kwargs = {
            'adjustment_task_weight': {'max_value': 1000, 'min_value': -1000},
            'adjustment_revisions': {'max_value': 1000, 'min_value': -1000},
        }


@register_serializer
class LineItemSerializer(serializers.ModelSerializer):
    percentage = serializers.FloatField()
    amount = MoneyToFloatField()
    frozen_value = MoneyToFloatField(read_only=True)
    targets = EventTargetRelatedField(read_only=True, many=True)

    class Meta:
        model = LineItem
        fields = (
            'id', 'priority', 'percentage', 'amount', 'frozen_value', 'type', 'destination_account', 'destination_user',
            'description', 'cascade_percentage', 'cascade_amount', 'back_into_percentage', 'targets',
        )
        read_only_fields = ('id', 'priority', 'destination_account', 'destination_user', 'targets')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(self, 'instance') and not isinstance(self.instance, QuerySet):
            if self.instance.type in [BASE_PRICE, TIP]:
                self.fields['percentage'].read_only = True
            if self.instance.id:
                self.fields['type'].read_only = True

    def validate_type(self, value):
        deliverable = self.context.get('deliverable')
        invoice = self.context.get('invoice')
        user = self.context['request'].user
        if user.is_staff:
            permitted_types = [EXTRA, ADD_ON, TIP]
        elif deliverable and user == deliverable.order.seller:
            permitted_types = [ADD_ON]
        else:  # pragma: no cover
            # This should never happen (security should filter this out) but included for completeness.
            permitted_types = []
        if value not in permitted_types:
            raise ValidationError('You do not have permission to create/modify line items of this type.')
        return value

    def validate(self, data):
        errors = defaultdict(list)
        instance = self.instance or DottedDict(**data)
        revised = DottedDict()
        for field in self.fields:
            setattr(revised, field, getattr(instance, field, None))
        revised.update(data)
        if revised.type == TIP:
            if revised.amount < settings.MINIMUM_TIP.amount:
                errors['amount'].append(f'Tip may not be less than {settings.MINIMUM_TIP}.')
            if revised.amount > settings.MAXIMUM_TIP.amount:
                errors['amount'].append(f'Tip may not be more than {settings.MAXIMUM_TIP}.')
        if errors:
            raise ValidationError(errors)
        return data


class OrderPreviewSerializer(ProductNameMixin, serializers.ModelSerializer):
    seller = RelatedUserSerializer(read_only=True)
    buyer = RelatedUserSerializer(read_only=True)
    display = serializers.SerializerMethodField()
    default_path = serializers.SerializerMethodField()
    read = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    guest_email = serializers.SerializerMethodField()

    def get_read(self, obj):
        return check_read(obj=obj, user=self.context['request'].user)

    def get_display(self, obj):
        return obj.notification_display(context=self.context)

    def get_default_path(self, order):
        if not self.can_view(order):
            return None
        return order_context_to_link(order_context(order=order, user=self.context['request'].user, logged_in=True))

    def can_view(self, order):
        requester = self.context['request'].user
        return (order.buyer == requester) or (order.seller == requester) or requester.is_staff

    def get_status(self, order):
        last_order = order.deliverables.all().order_by('created_on').last()
        return last_order and last_order.status

    def get_guest_email(self, order):
        user = self.context['request'].user
        if not (user == order.seller or user.is_staff):
            return ''
        if order.buyer and order.buyer.guest:
            return order.buyer.guest_email
        elif not order.buyer:
            return order.customer_email
        return ''

    def to_representation(self, instance):
        checks = self.can_view(instance)
        if (instance.private or instance.hide_details) and not checks:
            return {'private': True, 'id': instance.id}
        return super().to_representation(instance)

    class Meta:
        model = Order
        fields = (
            'id', 'created_on', 'seller', 'buyer', 'private', 'hide_details', 'display', 'default_path', 'read',
            'product_name', 'status', 'guest_email',
        )
        read_only_fields = [field for field in fields]


@register_serializer
class CardSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    primary = SerializerMethodField('is_primary')
    processor = SerializerMethodField()

    # noinspection PyMethodMayBeStatic
    def is_primary(self, obj):
        return obj.user.primary_card_id == obj.id

    def get_processor(self, obj):
        return AUTHORIZE if obj.token else STRIPE

    class Meta:
        model = CreditCardToken
        fields = ('id', 'user', 'last_four', 'type', 'primary', 'cvv_verified', 'processor')
        read_only_fields = fields


# noinspection PyAbstractClass
class NewCardSerializer(serializers.Serializer):
    """
    Form for getting and saving a credit card.
    """
    make_primary = serializers.BooleanField(default=False)
    save_card = serializers.BooleanField(default=False)


class MakePaymentMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cash = kwargs['data'].get('cash')
        card_id = kwargs['data'].get('card_id', None)
        is_staff = kwargs['context']['request'].user.is_staff
        if 'data' in kwargs and (card_id or (cash and is_staff)):
            del self.fields['make_primary']
            if cash and is_staff:
                del self.fields['card_id']


# noinspection PyAbstractClass
class PaymentSerializer(MakePaymentMixin, NewCardSerializer):
    """
    Serializer for taking payments
    """
    cash = serializers.BooleanField(default=False)
    card_id = IntegerField(allow_null=True)
    amount = DecimalField(max_digits=6, min_value=settings.MINIMUM_PRICE.amount, decimal_places=2)

    def validate_amount(self, value: Decimal):
        return Money(value, settings.DEFAULT_CURRENCY)


# noinspection PyAbstractClass
class ServicePaymentSerializer(MakePaymentMixin, NewCardSerializer):
    """
    Serializer for taking payments
    """
    remote_id = serializers.CharField(required=False, allow_blank=True)
    cash = serializers.BooleanField(default=False)
    card_id = IntegerField(allow_null=True)


class RevisionSerializer(serializers.ModelSerializer):
    """
    Serializer for order revisions.
    """
    owner = serializers.SlugRelatedField(slug_field='username', read_only=True)
    file = RelatedAssetField(thumbnail_namespace='sales.Revision.file')
    final = serializers.BooleanField(default=False, required=False, write_only=True)
    submissions = serializers.SerializerMethodField()
    read = serializers.SerializerMethodField()

    def create(self, validated_data):
        data = {**validated_data}
        data.pop('final', None)
        return super().create(data)

    def get_read(self, obj):
        return check_read(obj=obj, user=self.context['request'].user)

    def get_submissions(self, obj):
        return list(obj.submissions.all().values('owner_id', 'id'))

    class Meta:
        model = Revision
        fields = ('id', 'rating', 'file', 'created_on', 'owner', 'deliverable', 'final', 'read', 'submissions')
        read_only_fields = ('id', 'deliverable', 'owner', 'read')


# noinspection PyMethodMayBeStatic
class AccountBalanceSerializer(serializers.ModelSerializer):
    escrow = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()
    pending = serializers.SerializerMethodField()

    def get_escrow(self, obj):
        return str(account_balance(obj, ESCROW))

    def get_available(self, obj):
        return str(account_balance(obj, HOLDINGS))

    def get_pending(self, obj):
        return str(account_balance(obj, BANK, PENDING))

    class Meta:
        model = User
        fields = ('escrow', 'available', 'pending')


class BankAccountSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    account_number = serializers.CharField(write_only=True)
    routing_number = serializers.CharField(write_only=True, max_length=9, min_length=9)

    class Meta:
        model = BankAccount
        fields = ('first_name', 'last_name', 'last_four', 'account_number', 'routing_number', 'type', 'id')
        read_only_fields = ('last_four',)


# noinspection PyAbstractClass
class WithdrawSerializer(serializers.Serializer):
    bank = serializers.IntegerField()
    amount = serializers.DecimalField(6, decimal_places=2, min_value=1)


class TransactionRecordSerializer(serializers.ModelSerializer):
    id = ShortCodeField()
    payer = RelatedUserSerializer(read_only=True)
    payee = RelatedUserSerializer(read_only=True)
    targets = EventTargetRelatedField(read_only=True, many=True)
    card = CardSerializer(read_only=True)
    amount = MoneyToFloatField()

    def to_representation(self, instance):
        result = super().to_representation(instance)
        subject = getattr(self.context['request'], 'subject', self.context['request'].user)
        if (instance.payer != subject) and not subject.is_staff:
            # In this case the user should not have access to the card information.
            result['card'] = None
        return result

    class Meta:
        model = TransactionRecord
        fields = (
            'id', 'source', 'destination', 'status', 'category', 'card', 'payer', 'payee', 'amount', 'remote_ids',
            'created_on', 'response_message', 'finalized_on', 'targets'
        )
        read_only_fields = fields


class PublishFinalSerializer(serializers.ModelSerializer):
    preview = RelatedAssetField(thumbnail_namespace='profiles.Submissiont.preview', required=False, allow_null=True)

    class Meta:
        model = Submission
        fields = (
            'title', 'caption', 'preview'
        )


class RatingSerializer(serializers.ModelSerializer):
    rater = RelatedUserSerializer(read_only=True)
    target = RelatedUserSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = (
            'stars',
            'comments',
            'rater',
            'target',
            'id'
        )
        read_only_fields = ('rater', 'id')


# noinspection PyAbstractClass
class SearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(required=False)
    shield_only = serializers.BooleanField(required=False)
    watch_list = serializers.BooleanField(required=False)
    commissions = serializers.BooleanField(required=False)
    rating = serializers.BooleanField(required=False)
    minimum_content_rating = serializers.ChoiceField(choices=RATINGS, required=False)
    content_ratings = serializers.RegexField(r'^[0-4](,[0-4]){0,3}$', required=False)
    featured = serializers.BooleanField(required=False)
    artists_of_color = serializers.BooleanField(required=False)
    lgbt = serializers.BooleanField(required=False)
    min_price = serializers.DecimalField(decimal_places=2, max_digits=6, required=False)
    max_price = serializers.DecimalField(decimal_places=2, max_digits=6, required=False)
    max_turnaround = serializers.DecimalField(decimal_places=2, max_digits=6, required=False)

    def validate_content_ratings(self, value):
        return [int(val) for val in value.split(',')]


# noinspection PyAbstractClass
class NewInvoiceSerializer(serializers.Serializer, PriceValidationMixin, ProductValidationMixin):
    product = serializers.IntegerField(allow_null=True)
    buyer = serializers.CharField(allow_null=True, allow_blank=True)
    price = serializers.DecimalField(
        max_digits=6, decimal_places=2,
    )
    completed = serializers.BooleanField()
    task_weight = serializers.IntegerField(min_value=0)
    revisions = serializers.IntegerField(min_value=0)
    private = serializers.BooleanField()
    rating = serializers.IntegerField(min_value=GENERAL, max_value=EXTREME)
    details = serializers.CharField(max_length=5000)
    paid = serializers.BooleanField()
    hold = serializers.BooleanField()
    cascade_fees = serializers.BooleanField()
    expected_turnaround = serializers.DecimalField(
        max_digits=5, decimal_places=2, min_value=settings.MINIMUM_TURNAROUND,
    )

    def validate_buyer(self, value):
        if not value:
            return None
        if '@' in value:
            EmailValidator()(value)
            user = User.objects.filter(email=value).first()
            if user:
                if user.blocking.filter(id=self.context['request'].user.id).exists():
                    raise ValidationError('Cannot send an invoice to this user. They may be blocking you.')
                if user == self.context['request'].user:
                    raise ValidationError('You cannot send yourself an invoice.')
                return user
            return User.objects.filter(email=value).first() or value
        user = available_users(self.context['request'].user).filter(username__iexact=value).first()
        if not user:
            raise ValidationError("User with that username not found, or they are blocking you.")
        return user


class HoldingsSummarySerializer(serializers.ModelSerializer):
    escrow = serializers.SerializerMethodField()
    holdings = serializers.SerializerMethodField()

    def get_escrow(self, obj):
        return str(account_balance(obj, ESCROW))

    def get_holdings(self, obj):
        return str(account_balance(obj, HOLDINGS, POSTED_ONLY))

    class Meta:
        model = User
        fields = ('id', 'username', 'escrow', 'holdings')


class ProductSampleSerializer(serializers.ModelSerializer):
    submission = SubmissionSerializer(read_only=True)
    submission_id = serializers.IntegerField(write_only=True)

    def validate_submission_id(self, val):
        user = self.context['product'].user
        if not Submission.objects.filter(id=val, artists=user):
            raise ValidationError('Either this submission does not exist, or you are not tagged as the artist in it.')
        return val

    class Meta:
        fields = (
            'id', 'submission', 'submission_id',
        )
        model = Product.samples.through


class AccountQuerySerializer(serializers.Serializer):
    account = serializers.ChoiceField(choices=((300, 'Purchases'), (302, 'Escrow'), (303, 'Holdings')), required=True)


class DeliverableCharacterTagSerializer(serializers.ModelSerializer):
    character = CharacterSerializer(read_only=True)
    character_id = serializers.IntegerField(write_only=True)

    class Meta:
        fields = (
            'id', 'character', 'character_id',
        )
        model = Deliverable.characters.through


class SubmissionFromOrderSerializer(RelatedAtomicMixin, serializers.ModelSerializer):
    tags = TagListField(required=False)

    class Meta:
        model = Submission
        fields = (
            'id', 'title', 'caption', 'private', 'created_on', 'tags', 'comments_disabled',
            'revision',
        )
        read_only_fields = (
            'tags',
        )


class OrderAuthSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    claim_token = ShortCodeField()
    chown = serializers.BooleanField()


class DeliverableValuesSerializer(serializers.ModelSerializer):
    """
    Tracks all relevant finance info from an order. This serializer should only be used on orders which have at
    least been initially paid for.
    """
    status = serializers.SerializerMethodField()
    buyer = serializers.SerializerMethodField()
    seller = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    payment_type = serializers.SerializerMethodField()
    still_in_escrow = serializers.SerializerMethodField()
    artist_earnings = serializers.SerializerMethodField()
    in_reserve = serializers.SerializerMethodField()
    sales_tax_collected = serializers.SerializerMethodField()
    our_fees = serializers.SerializerMethodField()
    card_fees = serializers.SerializerMethodField()
    ach_fees = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()
    refunded_on = serializers.SerializerMethodField()
    extra = serializers.SerializerMethodField()
    remote_ids = serializers.SerializerMethodField()

    def get_status(self, obj):
        return obj.get_status_display()

    def get_buyer(self, obj):
        if obj.order.buyer and obj.order.buyer.guest:
            return f'Guest #{obj.order.buyer.id}'
        elif obj.order.buyer:
            return obj.order.buyer.username
        else:  # pragma: no cover
            # Should never occur, since the sales are always attached to some user.
            return '(Empty)'

    def get_seller(self, obj):
        return str(obj.order.seller)

    @lru_cache(4)
    def charge_transactions(self, obj):
        return TransactionRecord.objects.filter(
            status=SUCCESS,
            # Will need this to expand to cash or similar?
            source__in=[CARD, CASH_DEPOSIT],
            **self.qs_kwargs(obj),
        )

    @lru_cache(4)
    def qs_kwargs(self, obj):
        return {
            'targets__content_type': ContentType.objects.get_for_model(obj),
            'targets__object_id': obj.id,
        }

    def get_price(self, obj):
        return self.charge_transactions(obj).aggregate(total=Sum('amount'))['total']

    def get_payment_type(self, obj):
        return self.charge_transactions(obj)[0].get_source_display()

    def get_sales_tax_collected(self, obj):
        return account_balance(
            None, MONEY_HOLE, AVAILABLE, qs_kwargs=self.qs_kwargs(obj)
        )

    def get_extra(self, obj):
        _, discount, subtotals = get_totals(obj.invoice.line_items.all())
        return sum([value.amount for line, value in subtotals.items() if line.type == EXTRA])

    def get_still_in_escrow(self, obj):
        return account_balance(
            obj.order.seller, ESCROW, AVAILABLE, qs_kwargs=self.qs_kwargs(obj)
        )

    def get_artist_earnings(self, obj):
        return TransactionRecord.objects.filter(
            source=ESCROW, destination=HOLDINGS, **self.qs_kwargs(obj),
        ).aggregate(total=Sum('amount'))['total']

    def get_in_reserve(self, obj):
        return account_balance(
            None, RESERVE, AVAILABLE, qs_kwargs=self.qs_kwargs(obj)
        )

    @lru_cache(4)
    def get_card_fees(self, obj):
        return TransactionRecord.objects.filter(
            payer=None, payee=None, status=SUCCESS,
            source=UNPROCESSED_EARNINGS, destination=CARD_TRANSACTION_FEES,
            **self.qs_kwargs(obj),
        ).aggregate(total=Sum('amount'))['total']

    def get_our_fees(self, obj):
        transactions = TransactionRecord.objects.filter(
            status=SUCCESS,
        ).filter(**self.qs_kwargs(obj)).filter(
            Q(payer=obj.order.buyer, payee=None,
              source__in=[CARD, CASH_DEPOSIT],
              destination__in=[UNPROCESSED_EARNINGS]) |
            Q(
                payer=None, payee=None, source=RESERVE,
                destination=UNPROCESSED_EARNINGS,
            )
        )
        return transactions.aggregate(total=Sum('amount'))['total']

    @lru_cache(4)
    def get_ach_fees(self, obj):
        transaction = TransactionRecord.objects.filter(
            payer=obj.order.seller, payee=obj.order.seller, status=SUCCESS,
            source=HOLDINGS, destination=BANK,
            **self.qs_kwargs(obj),
        ).first()
        if not transaction:
            return None
        fee = TransactionRecord.objects.filter(
            payer=None, payee=None, status=SUCCESS,
            source=UNPROCESSED_EARNINGS, destination=ACH_TRANSACTION_FEES,
            targets__content_type=ContentType.objects.get_for_model(transaction),
            targets__object_id=unslugify(transaction.id),
        ).first()
        if not fee:
            # Something's wrong here. Will need to find out why this transaction was not annotated.
            return
        invoices = []
        invoice_type = ContentType.objects.get_for_model(Deliverable)
        for target in transaction.targets.all():
            if target.content_type == invoice_type:
                invoices.append(target.target)
        lines = {}
        for invoice in invoices:
            lines[invoice] = LineItemSim(
                id=invoice.id,
                amount=Money(TransactionRecord.objects.filter(
                    destination=HOLDINGS, **self.qs_kwargs(obj),
                ).aggregate(total=Sum('amount'))['total'], settings.DEFAULT_CURRENCY),
                priority=0,
            )
        lines[None] = LineItemSim(id=-1, amount=fee.amount, cascade_amount=True, priority=1)
        _total, _discount, subtotals = get_totals(lines.values())
        return (lines[obj].amount - subtotals[lines[obj]]).amount

    def get_profit(self, obj):
        base = self.get_our_fees(obj)
        ach_fees = self.get_ach_fees(obj) or Decimal('0')
        card_fees = self.get_card_fees(obj)
        refunded = self.get_refunded_on(obj)
        if not all([base, (ach_fees or refunded), card_fees]):
            return
        return base - ach_fees - card_fees

    @lru_cache
    def get_refunded_on(self, obj):
        if refund := TransactionRecord.objects.filter(
                source=ESCROW, payer=obj.order.seller, status=SUCCESS,
                payee=obj.order.buyer,
                **self.qs_kwargs(obj),
        ).first():
            return refund.created_on

    def get_remote_ids(self, obj):
        records = TransactionRecord.objects.filter(**self.qs_kwargs(obj))
        remote_ids = set(list(chain(*(record.remote_ids for record in records))))
        return ', '.join(sorted(list(remote_ids)))

    class Meta:
        model = Deliverable
        fields = (
            'id', 'created_on', 'status', 'seller', 'buyer', 'price', 'paid_on', 'payment_type', 'still_in_escrow',
            'artist_earnings', 'in_reserve', 'sales_tax_collected', 'refunded_on', 'extra', 'ach_fees', 'our_fees',
            'card_fees', 'profit', 'remote_ids',
        )


class TipValuesSerializer(serializers.ModelSerializer):
    """
    Tracks all relevant finance info from a tip invoice.
    """
    status = serializers.SerializerMethodField()
    bill_to = serializers.SerializerMethodField()
    issued_by = serializers.CharField(source='issued_by.username', read_only=True)
    payment_type = serializers.SerializerMethodField()
    artist_earnings = serializers.SerializerMethodField()
    our_fees = serializers.SerializerMethodField()
    card_fees = serializers.SerializerMethodField()
    ach_fees = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()
    remote_ids = serializers.SerializerMethodField()

    def get_status(self, obj):
        return obj.get_status_display()

    def get_bill_to(self, obj):
        if obj.bill_to and obj.bill_to.guest:
            return f'Guest #{obj.bill_to.id}'
        elif obj.bill_to:
            return obj.bill_to.username
        else:  # pragma: no cover
            # Should never occur, since the tips are always attached to some user.
            return '(Empty)'

    @lru_cache(4)
    def charge_transactions(self, obj):
        return TransactionRecord.objects.filter(
            status=SUCCESS,
            # Will need this to expand to cash or similar?
            source__in=[CARD, CASH_DEPOSIT],
            **self.qs_kwargs(obj),
        )

    @lru_cache(4)
    def qs_kwargs(self, obj):
        return {
            'targets__content_type': ContentType.objects.get_for_model(obj),
            'targets__object_id': unslugify(obj.id),
        }

    def get_payment_type(self, obj):
        return self.charge_transactions(obj)[0].get_source_display()

    def get_artist_earnings(self, obj):
        return TransactionRecord.objects.filter(
            destination=HOLDINGS, **self.qs_kwargs(obj),
        ).aggregate(total=Sum('amount'))['total']

    @lru_cache(4)
    def get_card_fees(self, obj):
        return TransactionRecord.objects.filter(
            payer=None, payee=None, status=SUCCESS,
            source=UNPROCESSED_EARNINGS, destination=CARD_TRANSACTION_FEES,
            **self.qs_kwargs(obj),
        ).aggregate(total=Sum('amount'))['total']

    def get_our_fees(self, obj):
        transactions = TransactionRecord.objects.filter(
            status=SUCCESS,
        ).filter(**self.qs_kwargs(obj)).filter(
            payer=obj.bill_to, payee=None,
            source__in=[CARD, CASH_DEPOSIT],
            destination__in=[UNPROCESSED_EARNINGS],
        )
        return transactions.aggregate(total=Sum('amount'))['total']

    @lru_cache(4)
    def get_ach_fees(self, obj):
        transaction = TransactionRecord.objects.filter(
            payer=obj.issued_by, payee=obj.issued_by, status=SUCCESS,
            source=HOLDINGS, destination=BANK,
            **self.qs_kwargs(obj),
        ).first()
        if not transaction:
            return None
        fee = TransactionRecord.objects.filter(
            payer=None, payee=None, status=SUCCESS,
            source=UNPROCESSED_EARNINGS, destination=ACH_TRANSACTION_FEES,
            targets__content_type=ContentType.objects.get_for_model(transaction),
            targets__object_id=unslugify(transaction.id),
        ).first()
        if not fee:
            # Something's wrong here. Will need to find out why this transaction was not annotated.
            return
        invoices = []
        invoice_type = ContentType.objects.get_for_model(Invoice)
        for target in transaction.targets.all():
            if target.content_type == invoice_type:
                invoices.append(target.target)
        lines = {}
        for invoice in invoices:
            lines[invoice] = LineItemSim(
                id=invoice.id,
                amount=Money(TransactionRecord.objects.filter(
                    destination=HOLDINGS, **self.qs_kwargs(obj),
                ).aggregate(total=Sum('amount'))['total'], settings.DEFAULT_CURRENCY),
                priority=0,
            )
        lines[None] = LineItemSim(id=-1, amount=fee.amount, cascade_amount=True, priority=1)
        _total, _discount, subtotals = get_totals(lines.values())
        return (lines[obj].amount - subtotals[lines[obj]]).amount

    def get_profit(self, obj):
        base = self.get_our_fees(obj)
        ach_fees = self.get_ach_fees(obj) or Decimal('0')
        card_fees = self.get_card_fees(obj)
        if not all([base, ach_fees, card_fees]):
            return
        return base - ach_fees - card_fees

    def get_remote_ids(self, obj):
        records = TransactionRecord.objects.filter(**self.qs_kwargs(obj))
        remote_ids = set(list(chain(*(record.remote_ids for record in records))))
        return ', '.join(sorted(list(remote_ids)))

    class Meta:
        model = Invoice
        fields = (
            'id', 'created_on', 'status', 'issued_by', 'bill_to', 'total', 'paid_on', 'payment_type',
            'artist_earnings', 'ach_fees', 'our_fees',
            'card_fees', 'profit', 'remote_ids',
        )


class PayoutTransactionSerializer(serializers.ModelSerializer):
    id = ShortCodeField()
    payee = serializers.StringRelatedField(read_only=True)
    status = serializers.SerializerMethodField()
    amount = MoneyToFloatField()
    fees = serializers.SerializerMethodField()
    total_drafted = serializers.SerializerMethodField()
    targets = serializers.SerializerMethodField()
    remote_ids = serializers.SerializerMethodField()

    def get_status(self, obj: TransactionRecord):
        return obj.get_status_display()

    def get_remote_ids(self, obj: TransactionRecord):
        return ', '.join(sorted(obj.remote_ids))

    @lru_cache
    def get_fees(self, obj):
        return (
                TransactionRecord.objects.filter(
                    targets=ref_for_instance(obj),
                    source=UNPROCESSED_EARNINGS,
                    status=SUCCESS,
                    destination=ACH_TRANSACTION_FEES).aggregate(total=Sum('amount'))['total']
                or Decimal('0')
        )

    def get_targets(self, obj: TransactionRecord):
        targets = obj.targets.order_by('content_type_id').all()
        items: List[str] = []
        for target in targets:
            if not target.target:
                continue
            base = f'{target.target.__class__.__name__} #{target.target.id}'
            if target.content_type.model_class() == TransactionRecord:
                base += f' ({target.target.amount})'
            items.append(base)
        return ', '.join(items)

    def get_total_drafted(self, obj: TransactionRecord):
        return obj.amount.amount + self.get_fees(obj)

    class Meta:
        model = TransactionRecord
        fields = (
            'id', 'status', 'payee', 'amount', 'fees', 'total_drafted', 'remote_ids',
            'created_on', 'finalized_on', 'targets',
        )
        read_only_fields = fields


class UserPayoutTransactionSerializer(serializers.ModelSerializer):
    id = ShortCodeField()
    amount = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    targets = serializers.SerializerMethodField()
    remote_ids = serializers.SerializerMethodField()

    def get_amount(self, obj: TransactionRecord):
        return str(obj.amount.amount)

    def get_currency(self, obj: TransactionRecord):
        return str(obj.amount.currency.code)

    def get_status(self, obj: TransactionRecord):
        return obj.get_status_display()

    def get_remote_ids(self, obj: TransactionRecord):
        return ', '.join(obj.remote_ids)

    def get_targets(self, obj: TransactionRecord):
        targets = obj.targets.order_by('content_type_id').all()
        items: List[str] = []
        for target in targets:
            if not target.target:
                continue
            model_class = target.content_type.model_class()
            if model_class == StripeAccount:
                continue
            if model_class == BankAccount:
                continue
            base = f'{target.target.__class__.__name__} #{target.target.id}'
            if model_class == Deliverable:
                base = target.target.notification_name(self.context)
            if target.content_type.model_class() == TransactionRecord:
                base += f' ({target.target.amount})'
            items.append(base)
        return ', '.join(items)

    class Meta:
        model = TransactionRecord
        fields = (
            'id', 'status', 'amount', 'currency', 'remote_ids',
            'created_on', 'finalized_on', 'targets',
        )
        read_only_fields = fields


class SubscriptionInvoiceSerializer(serializers.ModelSerializer):
    id = ShortCodeField()
    type = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    bill_to = serializers.CharField(read_only=True, source='bill_to.username')
    source = serializers.SerializerMethodField()
    total = MoneyToFloatField()
    remote_ids = serializers.SerializerMethodField()

    def get_type(self, obj):
        return obj.get_type_display()

    def get_status(self, obj):
        return obj.get_status_display()

    def get_source(self, obj):
        record = TransactionRecord.objects.filter(targets=ref_for_instance(obj), status=SUCCESS).first()
        if not record:  # pragma: no cover
            # Should never happen in the reports we're doing.
            return ''
        return record.get_source_display()

    def get_remote_ids(self, obj: TransactionRecord):
        ids = set()
        records = TransactionRecord.objects.filter(targets=ref_for_instance(obj), status=SUCCESS)
        for record in records:
            ids |= set(record.remote_ids)
        ids = list(ids)
        return ', '.join(sorted(ids))

    class Meta:
        model = Invoice
        fields = (
            'id', 'source', 'status', 'bill_to', 'total', 'remote_ids',
            'type', 'created_on', 'paid_on',
        )
        read_only_fields = fields


class UnaffiliatedInvoiceSerializer(serializers.ModelSerializer):
    id = ShortCodeField()
    source = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    total = MoneyToFloatField()
    tax = serializers.SerializerMethodField()
    card_fees = serializers.SerializerMethodField()
    net = serializers.SerializerMethodField()
    remote_ids = serializers.SerializerMethodField()

    def get_source(self, obj):
        records = TransactionRecord.objects.filter(targets=ref_for_instance(obj), status=SUCCESS)
        if records.filter(source=CASH_DEPOSIT).exists():
            return 'Cash'
        if records.filter(source=CARD).exists():
            return 'Card'
        return '????'

    def get_status(self, obj):
        return obj.get_status_display()

    def get_tax(self, obj):
        return str(TransactionRecord.objects.filter(
            targets=ref_for_instance(obj),
            status=SUCCESS,
            destination=MONEY_HOLE,
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00'))

    def get_card_fees(self, obj):
        return str(TransactionRecord.objects.filter(
            targets=ref_for_instance(obj),
            status=SUCCESS,
            destination=CARD_TRANSACTION_FEES,
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00'))

    def get_remote_ids(self, obj):
        records = TransactionRecord.objects.filter(
            status=SUCCESS,
            targets=ref_for_instance(obj),
        )
        remote_ids = set(list(chain(*(record.remote_ids for record in records))))
        return ', '.join(sorted(list(remote_ids)))

    def get_net(self, obj):
        return str(obj.total().amount - Decimal(self.get_card_fees(obj)) - Decimal(self.get_tax(obj)))

    class Meta:
        model = TransactionRecord
        fields = (
            'id', 'created_on', 'total', 'source', 'status', 'card_fees', 'tax', 'net',
            'remote_ids',
        )
        read_only_fields = fields


class InventorySerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(validators=[MinValueValidator(0)])

    class Meta:
        model = InventoryTracker
        fields = ('count',)


class ReferenceSerializer(serializers.ModelSerializer):
    id = ShortCodeField(read_only=True)
    owner = serializers.SlugRelatedField(slug_field='username', read_only=True)
    file = RelatedAssetField(thumbnail_namespace='sales.Reference.file')
    read = serializers.SerializerMethodField()

    def get_read(self, obj):
        return check_read(obj=obj, user=self.context['request'].user)

    class Meta:
        model = Reference
        fields = ('owner', 'file', 'rating', 'id', 'read')


class DeliverableReferenceSerializer(serializers.ModelSerializer):
    reference = ReferenceSerializer(read_only=True)
    reference_id = serializers.IntegerField(write_only=True)

    def validate_reference_id(self, val):
        if not Reference.objects.filter(id=val, owner=self.context['request'].user).exists():
            raise ValidationError('Either this reference does not exist, or you are not allowed to use it.')
        return val

    class Meta:
        fields = (
            'id', 'reference', 'reference_id',
        )
        model = Reference.deliverables.through


class PaymentIntentSettings(serializers.Serializer):
    make_primary = serializers.BooleanField(default=False)
    save_card = serializers.BooleanField(default=False)
    card_id = serializers.IntegerField(required=False, allow_null=True)
    use_reader = serializers.BooleanField(default=False)


class TerminalProcessSerializer(serializers.Serializer):
    reader = serializers.CharField()


class StripeReaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripeReader
        fields = (
            'id', 'name',
        )
        read_only_fields = fields


class PremiumIntentSettings(serializers.Serializer):
    make_primary = serializers.BooleanField(default=False)
    save_card = serializers.BooleanField(default=False)
    service = serializers.CharField()
    card_id = serializers.IntegerField(required=False, allow_null=True)
    use_reader = serializers.BooleanField(default=False)


class SetServiceSerializer(serializers.Serializer):
    service = serializers.CharField()


@register_serializer
class StripeAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripeAccount
        fields = ('id', 'active', 'country')
        read_only_fields = ('id', 'active', 'country')


class StripeBankSetupSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].choices = self.context.get('countries')
    country = serializers.ChoiceField(choices=[])
    url = serializers.URLField()

    def validate_url(self, value):
        parsed = urlparse(value)
        # '*' should only be in settings.ALLOWED_HOSTS in debug environments where someone may have stood up a random
        # external domain name, like with Ngrok.
        if parsed.hostname not in settings.ALLOWED_HOSTS and '*' not in settings.ALLOWED_HOSTS:
            raise ValidationError('Unrecognized domain.')
        return value


@register_serializer
class InvoiceSerializer(serializers.ModelSerializer):
    id = ShortCodeField()
    bill_to = RelatedUserSerializer()
    issued_by = RelatedUserSerializer()
    total = serializers.SerializerMethodField()
    targets = EventTargetRelatedField(read_only=True, many=True)

    def get_total(self, invoice):
        return str(invoice.total())

    class Meta:
        fields = (
            'id', 'status', 'type', 'bill_to', 'issued_by', 'created_on', 'paid_on', 'total', 'targets', 'record_only',
        )
        read_only_fields = fields
        model = Invoice


class ServicePlanSerializer(serializers.ModelSerializer):
    monthly_charge = MoneyToFloatField()
    per_deliverable_price = MoneyToFloatField()
    shield_static_price = MoneyToFloatField()
    shield_percentage_price = serializers.FloatField()

    class Meta:
        fields = (
            'id', 'name', 'description', 'features', 'monthly_charge', 'per_deliverable_price',
            'max_simultaneous_orders', 'tipping', 'shield_static_price', 'shield_percentage_price',
            'waitlisting',
        )
        read_only_fields = fields
        model = ServicePlan
