from decimal import Decimal
from functools import lru_cache
from itertools import chain
from typing import List
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator, EmailValidator, MinValueValidator
from django.db.models import Sum, QuerySet, Q
from django.urls import reverse
from django.utils.datetime_safe import datetime, date
from luhn import verify
from moneyed import Money
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, DecimalField, IntegerField, FloatField, EmailField, ModelField, \
    ListField
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
from apps.lib.utils import country_choices, add_check, check_read, demark, FakeRequest
from apps.profiles.models import User, Submission, Character
from apps.profiles.serializers import CharacterSerializer, SubmissionSerializer
from apps.profiles.utils import available_users
from apps.sales.apis import AUTHORIZE, STRIPE
from apps.sales.models import (
    Product, Order, CreditCardToken, Revision, BankAccount,
    LineItemSim, Rating, TransactionRecord, LineItem, ADD_ON, TIP, BASE_PRICE, InventoryTracker,
    EXTRA, PAYMENT_PENDING, NEW, Deliverable, Reference,
    WAITING, StripeAccount, Invoice, StripeReader,
)
from apps.sales.stripe import stripe
from apps.sales.utils import account_balance, PENDING, POSTED_ONLY, AVAILABLE, get_totals, order_context, \
    order_context_to_link
from shortcuts import make_url


class ProductMixin:
    def get_thumbnail_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.file.file.url)

    def validate_base_price(self, value):
        if not self.context['request'].subject.artist_profile.escrow_disabled:
            if value and (value < settings.MINIMUM_PRICE):
                raise ValidationError('Must be at least ${}'.format(settings.MINIMUM_PRICE))
        return value

    def validate_primary_submission_id(self, value):
        if value is None:
            return None
        try:
            Submission.objects.get(id=value, artist=self.instance.user)
        except Submission.DoesNotExist:
            raise ValidationError("That submission does not exist, or you cannot use it as your sample.")
        return value

    def validate_tags(self, value):
        add_check(self.instance, 'tags', replace=True, *value)
        return value

    def mod_instance(self, instance, value):
        setattr(instance, self.field_name, value)


class ProductSerializer(ProductMixin, RelatedAtomicMixin, serializers.ModelSerializer):
    save_related = True
    user = RelatedUserSerializer(read_only=True)
    primary_submission = SubmissionSerializer(required=False, allow_null=True)
    tags = TagListField(required=False)
    base_price = MoneyToFloatField()
    starting_price = MoneyToFloatField(read_only=True)
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
        subject = getattr(request, 'subject', None)
        if subject and subject.is_registered and subject.landscape:
            self.fields['wait_list'].read_only = False

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'revisions', 'hidden', 'max_parallel', 'max_rating', 'task_weight',
            'expected_turnaround', 'user', 'base_price', 'starting_price', 'tags', 'available', 'primary_submission',
            'featured', 'hits', 'escrow_disabled', 'table_product', 'track_inventory', 'wait_list', 'catalog_enabled',
        )
        read_only_fields = ('tags', 'featured', 'table_product', 'starting_price')
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
        if not self.context['seller'].artist_profile.escrow_disabled:
            if value and (value < settings.MINIMUM_PRICE):
                raise ValidationError('Must be $0 or at least ${}'.format(settings.MINIMUM_PRICE))
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
    default_path = serializers.SerializerMethodField()
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

    def get_default_path(self, order):
        return order.notification_link(context=self.context)

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
            )}
        return super().create(data)

    class Meta:
        model = Order
        fields = (
            'id', 'created_on', 'rating', 'details', 'seller', 'buyer', 'private',
            'email', 'characters', 'references', 'default_path', 'product_name',
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
        if 'instance' not in kwargs:
            return
        try:
            self.is_seller
        except (KeyError, AttributeError):
            return
        if self.is_seller:
            if (not self.instance.buyer) or self.instance.buyer.guest and not self.instance.deliverables.filter():
                self.fields['customer_email'].read_only = False
            self.fields['hide_details'].read_only = False
        if not self.instance.buyer:
            self.fields['customer_email'].allow_blank = True

    @property
    def is_seller(self):
        user = self.context['request'].user
        return (user == self.instance.seller) or user.is_staff

    @property
    def is_buyer(self):
        user = self.context['request'].user
        return (user == self.instance.buyer) or user.is_staff

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
            'completed', 'paid', 'task_weight', 'references', 'rating', 'product',
        )


@register_serializer
class DeliverableViewSerializer(RelatedAtomicMixin, serializers.ModelSerializer):
    arbitrator = RelatedUserSerializer(read_only=True)
    outputs = SubmissionSerializer(many=True, read_only=True)
    product = ProductSerializer(read_only=True)
    subscribed = SubscribedField(required=False)
    expected_turnaround = FloatField(read_only=True)
    tip = MoneyToFloatField(read_only=True, validators=[MinValueValidator(0)])
    adjustment_expected_turnaround = FloatField(read_only=True, max_value=1000, min_value=-1000)
    display = serializers.SerializerMethodField()
    processor = serializers.CharField(read_only=True)
    order = OrderViewSerializer(read_only=True)
    read = serializers.SerializerMethodField()
    invoice = serializers.SerializerMethodField()

    def get_read(self, obj):
        return check_read(obj=obj, user=self.context['request'].user)

    def get_invoice(self, obj):
        # Can get triggered when loaded with a list. In that case there is no sensible answer.
        if not isinstance(obj, Deliverable):
            return ''
        if self.is_buyer or self.context['request'].user.is_staff:
            return obj.invoice.id
        return None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not (args or kwargs):
            # We're in the class definition.
            return
        try:
            self.is_seller
        except (KeyError, AttributeError):
            return
        if self.is_seller:
            if self.instance.status in [NEW, PAYMENT_PENDING, WAITING]:
                for field_name in [
                    'adjustment_expected_turnaround', 'adjustment_task_weight', 'adjustment_revisions',
                    'name'
                ]:
                    self.fields[field_name].read_only = False
            # Should never be harmful. Helpful in many statuses.
            self.fields['stream_link'].read_only = False
        elif self.is_buyer:
            if self.instance.status == PAYMENT_PENDING and self.instance.order.seller.landscape:
                self.fields['tip'].read_only = False

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

    def validate_customer_email(self, val):
        user = self.instance.order.seller
        if val.lower() == user.email.lower():
            raise ValidationError('You cannot set yourself as the customer.')
        return val

    def validate_adjustment_expected_turnaround(self, val):
        adjustment_expected_turnaround = Decimal(val)
        if (
                self.instance.product.expected_turnaround
                + adjustment_expected_turnaround < settings.MINIMUM_TURNAROUND
        ):
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

    def validate(self, attrs):
        # We're going to assume that tip is only edited on its own.
        tip = attrs.get('tip', None)
        if tip is None:
            return attrs
        current_total = self.instance.invoice.total()
        current_total -= self.instance.tip
        if (current_total.amount / 2) < tip:
            raise ValidationError({'tip': 'Tip should not be more than half of the original price.'})
        return attrs

    def get_display(self, obj):
        return obj.notification_display(context=self.context)

    class Meta:
        model = Deliverable
        fields = (
            'id', 'created_on', 'status', 'details',
            'stream_link', 'revisions', 'outputs', 'subscribed', 'adjustment_task_weight',
            'adjustment_expected_turnaround', 'expected_turnaround', 'task_weight', 'paid_on', 'dispute_available_on',
            'auto_finalize_on', 'started_on', 'escrow_disabled', 'revisions_hidden', 'final_uploaded', 'arbitrator',
            'display', 'rating', 'commission_info', 'adjustment_revisions',
            'tip', 'table_order', 'trust_finalized', 'order', 'name', 'product', 'read', 'processor',
            'invoice',
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
            if self.instance.type == BASE_PRICE:
                self.fields['percentage'].read_only = True
            if self.instance.id:
                self.fields['type'].read_only = True

    def validate_type(self, value):
        deliverable = self.context.get('deliverable')
        user = self.context['request'].user
        if user.is_staff:
            permitted_types = [EXTRA, ADD_ON, TIP]
        elif deliverable and user == deliverable.order.seller:
            permitted_types = [ADD_ON]
            if deliverable.product is None:
                permitted_types.append(BASE_PRICE)
        elif deliverable and user == deliverable.order.buyer:
            permitted_types = [TIP]
        else:
            permitted_types = []
        if value not in permitted_types:
            raise ValidationError('You do not have permission to create/modify line items of this type.')
        return value

    def validate_minimum(self, value):
        deliverable = self.context['order']
        user = self.context['request'].user
        if (not (user == deliverable.seller) or user.is_staff) and value < 0:
            raise ValidationError('Cannot be less than 0.')
        return value


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
        return order.buyer == requester or order.seller == requester or requester.is_staff

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
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    country = serializers.ChoiceField(choices=country_choices())
    number = serializers.CharField(max_length=25)
    exp_date = serializers.CharField(max_length=7, min_length=4)
    zip = serializers.CharField(max_length=20, required=False)
    cvv = serializers.CharField(max_length=4, min_length=3, validators=[RegexValidator(r'^[0-9]{3,4}$')])
    make_primary = serializers.BooleanField(default=False)
    save_card = serializers.BooleanField(default=False)

    # noinspection PyMethodMayBeStatic
    def validate_exp_date(self, value):
        value = value.replace('/', '')
        params = [val for val in [value[:2], value[2:]] if val]
        if len(params) != 2:
            raise serializers.ValidationError("Date must be in the format MM/YY.")
        try:
            # Avoid Y3K problem while still supporting two digit year.
            month = int(params[0])
            year = int(params[1])
            if year < 100:
                hundreds = datetime.today().year // 100
                year = hundreds * 100 + year
            if year > 9999 or year < 1000:
                raise TypeError
            exp_date = date(month=month, year=year, day=1)
        except ValueError:
            raise serializers.ValidationError("That is not a valid date.")
        except TypeError:
            raise serializers.ValidationError("Date must be in the format MM/YY. For example, 12/22")
        if exp_date < date.today().replace(day=1):
            raise serializers.ValidationError("This card has expired.")
        return exp_date

    # noinspection PyMethodMayBeStatic
    def validate_number(self, value):
        value = value.replace(' ', '')
        if 13 <= len(value) <= 19:
            if not verify(value):
                raise serializers.ValidationError("Please check the card number.")
            return value
        raise serializers.ValidationError("A card number must be at least 13 digits long and at most 19.")


class MakePaymentMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cash = kwargs['data'].get('cash')
        card_id = kwargs['data'].get('card_id', None)
        remote_id = kwargs['data'].get('remote_id', '')
        is_staff = kwargs['context']['request'].user.is_staff
        if 'data' in kwargs and (card_id or ((remote_id and is_staff) or (cash and is_staff))):
            for field_name in ['first_name', 'last_name', 'country', 'number', 'exp_date', 'zip', 'make_primary']:
                del self.fields[field_name]
            if (remote_id and is_staff) or (cash and is_staff):
                del self.fields['card_id']
            self.fields['cvv'].allow_blank = True
            self.fields['cvv'].required = False


# noinspection PyAbstractClass
class PaymentSerializer(MakePaymentMixin, NewCardSerializer):
    """
    Serializer for taking payments
    """
    remote_id = serializers.CharField(required=False, allow_blank=True)
    cash = serializers.BooleanField(default=False)
    card_id = IntegerField(allow_null=True)
    amount = DecimalField(max_digits=6, min_value=settings.MINIMUM_PRICE, decimal_places=2)

    def validate_remote_id(self, value: str):
        if not value:
            return value
        if not value.isnumeric():
            raise ValidationError('Authorize.net transaction IDs are numeric.')
        if not len(value) >= 10:
            raise ValidationError('Authorize.net transaction IDs are 10 or more digits in length.')
        return value

    def validate_amount(self, value: Decimal):
        return Money(value, 'USD')


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

    def get_thumbnail_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.file.file.url)

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
        return str(account_balance(obj, TransactionRecord.ESCROW))

    def get_available(self, obj):
        return str(account_balance(obj, TransactionRecord.HOLDINGS))

    def get_pending(self, obj):
        return str(account_balance(obj, TransactionRecord.BANK, PENDING))

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
        return str(account_balance(obj, TransactionRecord.ESCROW))

    def get_holdings(self, obj):
        return str(account_balance(obj, TransactionRecord.HOLDINGS, POSTED_ONLY))

    class Meta:
        model = User
        fields = ('id', 'username', 'escrow', 'holdings')


class ProductSampleSerializer(serializers.ModelSerializer):
    submission = SubmissionSerializer(read_only=True)
    submission_id = serializers.IntegerField(write_only=True)

    def validate_product_id(self, val):
        error = 'Either this character does not exist, or you are not allowed to tag them.'
        if self.context['request'].user.blocked_by.filter(id=val):
            raise ValidationError(error)
        if not Submission.objects.filter(id=val, user__taggable=True):
            raise ValidationError(error)
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

    def validate_character_id(self, val):
        error = 'Either this character does not exist, or you are not allowed to tag them.'
        if self.context['request'].user.blocked_by.filter(id=val):
            raise ValidationError(error)
        if not Character.objects.filter(id=val, user__taggable=True):
            raise ValidationError(error)
        return val

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
    charged_on = serializers.SerializerMethodField()
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
            return f'Guest #{obj.id}'
        elif obj.order.buyer:
            return obj.order.buyer.username
        else:
            return '(Empty)'

    def get_seller(self, obj):
        return str(obj.order.seller)

    @lru_cache(4)
    def charge_transactions(self, obj):
        return TransactionRecord.objects.filter(
            status=TransactionRecord.SUCCESS,
            # Will need this to expand to cash or similar?
            source__in=[TransactionRecord.CARD, TransactionRecord.CASH_DEPOSIT],
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

    def get_charged_on(self, obj):
        return self.charge_transactions(obj)[0].created_on

    def get_sales_tax_collected(self, obj):
        return account_balance(
            None, TransactionRecord.MONEY_HOLE, AVAILABLE, qs_kwargs=self.qs_kwargs(obj)
        )

    def get_extra(self, obj):
        _, discount, subtotals = get_totals(obj.invoice.line_items.all())
        return sum([value.amount for line, value in subtotals.items() if line.type == EXTRA])

    def get_still_in_escrow(self, obj):
        return account_balance(
            obj.order.seller, TransactionRecord.ESCROW, AVAILABLE, qs_kwargs=self.qs_kwargs(obj)
        )

    def get_artist_earnings(self, obj):
        return TransactionRecord.objects.filter(
            source=TransactionRecord.ESCROW, destination=TransactionRecord.HOLDINGS, **self.qs_kwargs(obj),
        ).aggregate(total=Sum('amount'))['total']

    def get_in_reserve(self, obj):
        return account_balance(
            None, TransactionRecord.RESERVE, AVAILABLE, qs_kwargs=self.qs_kwargs(obj)
        )

    @lru_cache(4)
    def get_card_fees(self, obj):
        return TransactionRecord.objects.filter(
            payer=None, payee=None, status=TransactionRecord.SUCCESS,
            source=TransactionRecord.UNPROCESSED_EARNINGS, destination=TransactionRecord.CARD_TRANSACTION_FEES,
            **self.qs_kwargs(obj),
        ).aggregate(total=Sum('amount'))['total']

    def get_our_fees(self, obj):
        destinations = [TransactionRecord.UNPROCESSED_EARNINGS]
        if obj.status is None:
            destinations.append(TransactionRecord.RESERVE)
        transactions = TransactionRecord.objects.filter(
            status=TransactionRecord.SUCCESS,
        ).filter(**self.qs_kwargs(obj)).filter(
            Q(payer=obj.order.buyer, payee=None,
              source__in=[TransactionRecord.CARD, TransactionRecord.CASH_DEPOSIT],
              destination__in=[TransactionRecord.UNPROCESSED_EARNINGS]) |
            Q(
                payer=None, payee=None, source=TransactionRecord.RESERVE,
                destination=TransactionRecord.UNPROCESSED_EARNINGS,
            )
        )
        return transactions.aggregate(total=Sum('amount'))['total']

    @lru_cache(4)
    def get_ach_fees(self, obj):
        transaction = TransactionRecord.objects.filter(
            payer=obj.order.seller, payee=obj.order.seller, status=TransactionRecord.SUCCESS,
            source=TransactionRecord.HOLDINGS, destination=TransactionRecord.BANK,
            **self.qs_kwargs(obj),
        ).first()
        if not transaction:
            return None
        fee = TransactionRecord.objects.filter(
            payer=None, payee=None, status=TransactionRecord.SUCCESS,
            source=TransactionRecord.UNPROCESSED_EARNINGS, destination=TransactionRecord.ACH_TRANSACTION_FEES,
            targets__content_type=ContentType.objects.get_for_model(transaction),
            targets__object_id=unslugify(transaction.id),
        ).first()
        if not fee:
            # Something's wrong here. Will need to find out why this transaction was not annotated.
            return
        deliverables = []
        deliverable_type = ContentType.objects.get_for_model(Deliverable)
        for target in transaction.targets.all():
            if target.content_type == deliverable_type:
                deliverables.append(target.target)
        lines = {}
        for order in deliverables:
            lines[order] = LineItemSim(
                id=order.id,
                amount=Money(TransactionRecord.objects.filter(
                    source=TransactionRecord.ESCROW, destination=TransactionRecord.HOLDINGS, **self.qs_kwargs(obj),
                ).aggregate(total=Sum('amount'))['total'], 'USD'),
                priority=0,
            )
        lines[None] = LineItemSim(id=-1, amount=fee.amount, cascade_amount=True, priority=1)
        _total, _discount, subtotals = get_totals(lines.values())
        return (lines[obj].amount - subtotals[lines[obj]]).amount

    def get_profit(self, obj):
        base = self.get_our_fees(obj)
        ach_fees = self.get_ach_fees(obj)
        card_fees = self.get_card_fees(obj)
        if not all([base, ach_fees, card_fees]):
            return
        return base - ach_fees - card_fees

    @lru_cache
    def get_refunded_on(self, obj):
        if refund := TransactionRecord.objects.filter(
                source=TransactionRecord.ESCROW, payer=obj.order.seller, status=TransactionRecord.SUCCESS,
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
            'id', 'created_on', 'status', 'seller', 'buyer', 'price', 'charged_on', 'payment_type', 'still_in_escrow',
            'artist_earnings', 'in_reserve', 'sales_tax_collected', 'refunded_on', 'extra', 'ach_fees', 'our_fees',
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

    def get_category(self, obj: TransactionRecord):
        return obj.get_category_display()

    def get_status(self, obj: TransactionRecord):
        return obj.get_status_display()

    def get_remote_ids(self, obj: TransactionRecord):
        return ', '.join(sorted(obj.remote_ids))

    @lru_cache
    def get_fees(self, obj):
        return (
                TransactionRecord.objects.filter(
                    targets=ref_for_instance(obj),
                    source=TransactionRecord.UNPROCESSED_EARNINGS,
                    status=TransactionRecord.SUCCESS,
                    destination=TransactionRecord.ACH_TRANSACTION_FEES).aggregate(total=Sum('amount'))['total']
                or Decimal('0')
        )

    def get_targets(self, obj: TransactionRecord):
        targets = obj.targets.order_by('content_type_id').all()
        items: List[str] = []
        for target in targets:
            if not target:
                continue
            base = f'{target.target.__class__.__name__} #{target.target.id}'
            if target.content_type.model_class == TransactionRecord:
                base += f' ({target.target.amount.amount})'
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

    def get_category(self, obj: TransactionRecord):
        return obj.get_category_display()

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
                base += f' ({target.target.amount.amount})'
            items.append(base)
        return ', '.join(items)

    class Meta:
        model = TransactionRecord
        fields = (
            'id', 'status', 'amount', 'currency', 'remote_ids',
            'created_on', 'finalized_on', 'targets',
        )
        read_only_fields = fields


def pin_link(url):
    return f'{url}?mtm_campaign=Pinterest&mtm_source=Pin'


def ad_link(url):
    return f'{url}?mtm_campaign=Pinterest&mtm_source=Ad'


def product_link(product):
    return make_url(
        reverse('store:product_preview', kwargs={'product_id': product.id, 'username': product.user.username}),
    )


class PinSerializer(serializers.ModelSerializer):
    availability = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    image_link = serializers.SerializerMethodField()
    additional_image_link = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()
    brand = serializers.StringRelatedField(source='user.username', read_only=True)

    def get_link(self, product):
        return pin_link(product_link(product))

    def get_price(self, product):
        return f'{product.starting_price.amount}{product.starting_price.currency}'

    def get_ad_link(self, product):
        return ad_link(product_link(product))

    def get_image_link(self, product):
        return product.preview_link

    def get_description(self, product):
        return demark(product.description)

    def get_title(self, product):
        return demark(product.name)

    def get_additional_image_link(self, product):
        return ','.join(
            make_url(sample.preview_link) for sample in product.samples.filter(rating=GENERAL, private=False)[:10]
            if sample.preview_link
        )

    def get_availability(self, product):
        if product.available:
            if product.wait_list:
                return 'preorder'
            return 'in stock'
        return 'out of stock'

    class Meta:
        model = Product
        fields = (
            'id', 'title', 'price', 'availability', 'description', 'link', 'image_link', 'brand',
            'additional_image_link',
        )


class SimpleTransactionSerializer(serializers.ModelSerializer):
    id = ShortCodeField()
    payer = serializers.StringRelatedField(read_only=True)
    payee = serializers.StringRelatedField(read_only=True)
    category = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    amount = MoneyToFloatField()
    remote_ids = serializers.SerializerMethodField()

    def get_category(self, obj):
        return obj.get_category_display()

    def get_status(self, obj):
        return obj.get_status_display()

    def get_remote_ids(self, obj: TransactionRecord):
        return ', '.join(sorted(obj.remote_ids))

    class Meta:
        model = TransactionRecord
        fields = (
            'id', 'source', 'status', 'payer', 'payee', 'amount', 'remote_ids',
            'category',
            'created_on', 'finalized_on',
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
        records = TransactionRecord.objects.filter(targets=ref_for_instance(obj), status=TransactionRecord.SUCCESS)
        if records.filter(source=TransactionRecord.CASH_DEPOSIT).exists():
            return 'Cash'
        if records.filter(source=TransactionRecord.CARD).exists():
            return 'Card'
        return '????'

    def get_status(self, obj):
        return obj.get_status_display()

    def get_tax(self, obj):
        return str(TransactionRecord.objects.filter(
            targets=ref_for_instance(obj),
            status=TransactionRecord.SUCCESS,
            destination=TransactionRecord.MONEY_HOLE,
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00'))

    def get_card_fees(self, obj):
        return str(TransactionRecord.objects.filter(
            targets=ref_for_instance(obj),
            status=TransactionRecord.SUCCESS,
            destination=TransactionRecord.CARD_TRANSACTION_FEES,
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00'))

    def get_remote_ids(self, obj):
        records = TransactionRecord.objects.filter(
            status=TransactionRecord.SUCCESS,
            targets=ref_for_instance(obj),
        )
        remote_ids = set(list(chain(*(record.remote_ids for record in records))))
        return ', '.join(sorted(list(remote_ids)))

    def get_net(self, obj):
        return str(obj.total().amount - Decimal(self.get_card_fees(obj)) - Decimal(self.get_tax(obj)))

    class Meta:
        model = TransactionRecord
        fields = (
            'id', 'source', 'status', 'total', 'card_fees', 'tax', 'net',
            'created_on', 'remote_ids',
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

    def get_thumbnail_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.file.file.url)

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


@register_serializer
class StripeAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripeAccount
        fields = ('id', 'active', 'country')
        read_only_fields = ('id', 'active', 'country')


class StripeBankSetupSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with stripe as api:
            self.fields['country'].choices = self.context.get('countries')
    country = serializers.ChoiceField(choices=[])
    url = serializers.URLField()

    def validate_url(self, value):
        try:
            parsed = urlparse(value)
        except ValueError as err:
            raise ValidationError(str(err))
        # * should only be in settings.ALLOWED_HOSTS in debug environments where someone may have stood up a random
        # external domain name, like with Ngrok.
        if parsed.hostname not in settings.ALLOWED_HOSTS and '*' not in settings.ALLOWED_HOSTS:
            raise ValidationError('Unrecognized domain.')
        return value


@register_serializer
class InvoiceSerializer(serializers.ModelSerializer):
    id = ShortCodeField()
    bill_to = RelatedUserSerializer()
    total = serializers.SerializerMethodField()

    def get_total(self, invoice):
        return str(invoice.total())

    class Meta:
        fields = ('id', 'status', 'type', 'bill_to', 'created_on', 'paid_on', 'total', 'record_only')
        read_only_fields = fields
        model = Invoice
