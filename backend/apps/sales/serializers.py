from decimal import Decimal

from django.conf import settings
from django.core.validators import RegexValidator, MinValueValidator, EmailValidator
from django.db.transaction import atomic
from django.utils.datetime_safe import datetime, date
from luhn import verify
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, DecimalField, IntegerField, FloatField, EmailField
from rest_framework.generics import get_object_or_404
from short_stuff import slugify
from short_stuff.django import ShortUIDField

from apps.lib.serializers import (
    RelatedUserSerializer, RelatedAssetField, EventTargetRelatedField, SubscribedField,
    TagListField, RelatedAtomicMixin,
)
from apps.lib.utils import country_choices, add_check
from apps.profiles.models import User, Submission, Character
from apps.profiles.serializers import CharacterSerializer, SubmissionSerializer
from apps.profiles.utils import available_users
from apps.sales.models import Product, Order, CreditCardToken, Revision, BankAccount, \
    Rating, TransactionRecord
from apps.sales.utils import account_balance, PENDING, POSTED_ONLY


class ProductMixin:
    def get_thumbnail_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.file.file.url)

    def validate_price(self, value):
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
    price = FloatField()
    expected_turnaround = FloatField()
    escrow_disabled = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.related_list = kwargs.get('related_list', None)
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if not request:
            return
        if request.user.is_staff:
            self.fields['featured'].read_only = False

    def get_escrow_disabled(self, product):
        if not product.price:
            return True
        return product.user.artist_profile.escrow_disabled

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'revisions', 'hidden', 'max_parallel', 'task_weight',
            'expected_turnaround', 'user', 'price', 'tags', 'available', 'primary_submission',
            'featured', 'hits', 'escrow_disabled'
        )
        read_only_fields = ('tags', 'featured')
        extra_kwargs = {'price': {'required': True}}


class ProductNewOrderSerializer(serializers.ModelSerializer):
    email = EmailField(write_only=True, required=False, allow_blank=True)
    id = ShortUIDField(read_only=True)
    seller = RelatedUserSerializer(read_only=True)
    buyer = RelatedUserSerializer(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.context['request'].user.is_authenticated:
            del self.fields['characters']
            self.fields['email'].required = True
            self.fields['email'].allow_blank = False

    def create(self, validated_data):
        data = {**validated_data}
        data.pop('email', None)
        return super().create(data)

    def validate_characters(self, value):
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

    class Meta:
        model = Order
        fields = (
            'id', 'created_on', 'status', 'product', 'rating', 'details', 'seller', 'buyer', 'characters', 'private',
            'email',
        )
        extra_kwargs = {
            'characters': {'required': False},
        }
        read_only_fields = (
            'status', 'id', 'created_on', 'product'
        )


class OrderViewSerializer(RelatedAtomicMixin, serializers.ModelSerializer):
    seller = RelatedUserSerializer(read_only=True)
    buyer = RelatedUserSerializer(read_only=True)
    arbitrator = RelatedUserSerializer(read_only=True)
    price = SerializerMethodField()
    product = ProductSerializer(read_only=True)
    outputs = SubmissionSerializer(many=True, read_only=True)
    subscribed = SubscribedField(required=False)
    expected_turnaround = FloatField(read_only=True)
    adjustment = FloatField(read_only=True)
    adjustment_expected_turnaround = FloatField(read_only=True)
    display = serializers.SerializerMethodField()
    claim_token = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.is_seller:
            if self.instance.status in [Order.NEW, Order.PAYMENT_PENDING]:
                for field_name in [
                    'adjustment_expected_turnaround', 'adjustment', 'adjustment_task_weight', 'adjustment_revisions',
                ]:
                    self.fields[field_name].read_only = False
            # Should never be harmful. Helpful in many statuses.
            self.fields['stream_link'].read_only = False
            if ((not self.instance.buyer) or self.instance.buyer.guest) and self.instance.status not in [
                Order.DISPUTED, Order.COMPLETED, Order.REFUNDED, Order.CANCELLED
            ]:
                self.fields['customer_email'].read_only = False
                if not self.instance.buyer:
                    self.fields['customer_email'].allow_blank = True

    def validate_adjustment(self, val):
        adjustment = Decimal(val)
        base = self.instance.product or self.instance
        if (base.price.amount + adjustment) < settings.MINIMUM_PRICE:
            raise ValidationError("The total price may not be less than ${}".format(settings.MINIMUM_PRICE))
        return adjustment

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
        user = self.instance.seller
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

    def get_claim_token(self, order):
        user = self.context['request'].user
        if user == order.buyer and order.claim_token:
            return slugify(order.claim_token)
        return None

    @property
    def is_seller(self):
        user = self.context['request'].user
        return (user == self.instance.seller) or user.is_staff

    # noinspection PyMethodMayBeStatic
    def get_price(self, obj):
        if not obj.price:
            return obj.product.price.amount
        return obj.price.amount

    def get_display(self, obj):
        return obj.notification_display(context=self.context)

    class Meta:
        model = Order
        fields = (
            'id', 'created_on', 'status', 'price', 'product', 'details', 'seller', 'buyer', 'adjustment',
            'stream_link', 'revisions', 'outputs', 'private', 'subscribed', 'adjustment_task_weight',
            'adjustment_expected_turnaround', 'expected_turnaround', 'task_weight', 'paid_on', 'dispute_available_on',
            'auto_finalize_on', 'started_on', 'escrow_disabled', 'revisions_hidden', 'final_uploaded', 'arbitrator',
            'display', 'rating', 'claim_token', 'commission_info', 'adjustment_revisions', 'customer_email',
        )
        read_only_fields = [field for field in fields if field != 'subscribed']


class OrderPreviewSerializer(serializers.ModelSerializer):
    seller = RelatedUserSerializer(read_only=True)
    buyer = RelatedUserSerializer(read_only=True)
    price = SerializerMethodField()
    product = ProductSerializer(read_only=True)
    expected_turnaround = FloatField()
    adjustment = FloatField()
    adjustment_expected_turnaround = FloatField()
    display = serializers.SerializerMethodField()

    # noinspection PyMethodMayBeStatic
    def get_price(self, obj):
        if not obj.price:
            return obj.product.price.amount
        return obj.price.amount

    def get_display(self, obj):
        return obj.notification_display(context=self.context)

    class Meta:
        model = Order
        fields = (
            'id', 'created_on', 'status', 'price', 'product', 'seller', 'buyer', 'adjustment', 'private',
            'adjustment_task_weight', 'adjustment_expected_turnaround', 'expected_turnaround', 'task_weight',
            'paid_on', 'dispute_available_on', 'auto_finalize_on', 'started_on', 'escrow_disabled', 'arbitrator',
            'display', 'adjustment_revisions',
        )
        read_only_fields = [field for field in fields]


class CardSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    primary = SerializerMethodField('is_primary')

    # noinspection PyMethodMayBeStatic
    def is_primary(self, obj):
        return obj.user.primary_card_id == obj.id

    class Meta:
        model = CreditCardToken
        fields = ('id', 'user', 'last_four', 'type', 'primary', 'cvv_verified')
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
    exp_date = serializers.CharField(max_length=5, min_length=4)
    zip = serializers.CharField(max_length=20, required=False)
    cvv = serializers.CharField(max_length=4, min_length=3, validators=[RegexValidator(r'^[0-9]{3,4}$')])
    make_primary = serializers.BooleanField()
    save_card = serializers.BooleanField()

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
            hundreds = datetime.today().year // 100
            year = hundreds * 100 + year
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
        if 'data' in kwargs and kwargs['data'].get('card_id', None):
            for field_name in ['first_name', 'last_name', 'country', 'number', 'exp_date', 'zip', 'make_primary']:
                del self.fields[field_name]
            self.fields['cvv'].allow_blank = True
            self.fields['cvv'].required = False


# noinspection PyAbstractClass
class PaymentSerializer(MakePaymentMixin, NewCardSerializer):
    """
    Serializer for taking payments
    """
    card_id = IntegerField(allow_null=True)
    amount = DecimalField(max_digits=6, min_value=settings.MINIMUM_PRICE, decimal_places=2)


# noinspection PyAbstractClass
class ServicePaymentSerializer(MakePaymentMixin, NewCardSerializer):
    """
    Serializer for taking payments
    """
    card_id = IntegerField(allow_null=True)
    service = serializers.ChoiceField(choices=('portrait', 'landscape'))


class RevisionSerializer(serializers.ModelSerializer):
    """
    Serializer for order revisions.
    """
    owner = serializers.SlugRelatedField(slug_field='username', read_only=True)
    file = RelatedAssetField(thumbnail_namespace='sales.Revision.file')
    final = serializers.BooleanField(default=False, required=False)

    def create(self, validated_data):
        data = {**validated_data}
        data.pop('final', None)
        return super().create(data)

    def get_thumbnail_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.file.file.url)

    class Meta:
        model = Revision
        fields = ('id', 'rating', 'file', 'created_on', 'owner', 'order', 'final')
        read_only_fields = ('id', 'order', 'owner')
        extra_kwargs = {
            'final': {'write_only': True}
        }


# noinspection PyMethodMayBeStatic
class AccountBalanceSerializer(serializers.ModelSerializer):
    escrow = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()
    pending = serializers.SerializerMethodField()

    def get_escrow(self, obj):
        return str(account_balance(obj, TransactionRecord.ESCROW_HOLD))

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
    id = ShortUIDField()
    payer = RelatedUserSerializer(read_only=True)
    payee = RelatedUserSerializer(read_only=True)
    target = EventTargetRelatedField(read_only=True)
    card = CardSerializer(read_only=True)
    amount = FloatField()

    def to_representation(self, instance):
        result = super().to_representation(instance)
        if instance.payer != self.context['request'].subject:
            # In this case the user should not have access to the card information.
            result['card'] = None
        return result

    class Meta:
        model = TransactionRecord
        fields = (
            'id', 'source', 'destination', 'status', 'category', 'card', 'payer', 'payee', 'amount', 'remote_id',
            'created_on', 'response_message', 'finalized_on', 'target'
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
    by_rating = serializers.BooleanField(required=False)
    featured = serializers.BooleanField(required=False)
    min_price = serializers.DecimalField(decimal_places=2, max_digits=6, required=False)
    max_price = serializers.DecimalField(decimal_places=2, max_digits=6, required=False)


# noinspection PyAbstractClass
class NewInvoiceSerializer(serializers.Serializer):
    product = serializers.IntegerField(allow_null=True)
    buyer = serializers.CharField(allow_null=True, allow_blank=True)
    price = serializers.DecimalField(
        max_digits=6, decimal_places=2,
    )
    completed = serializers.BooleanField(allow_null=True)
    task_weight = serializers.IntegerField(min_value=0)
    revisions = serializers.IntegerField(min_value=0)
    private = serializers.BooleanField()
    details = serializers.CharField(max_length=5000)
    paid = serializers.BooleanField(allow_null=True)
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
        try:
            value = int(value)
        except ValueError:
            raise ValidationError("Not a valid email or user.")
        user = available_users(self.context['request']).filter(id=value).first()
        if not user:
            raise ValidationError("User with that ID not found, or they are blocking you.")
        return user

    def validate_product(self, value):
        if value is None:
            return None
        product = self.context['request'].user.products.exclude(active=False).filter(id=value).first()
        if not product:
            raise ValidationError("You don't have a product with that ID.")
        return product

    def validate_price(self, value):
        if not self.context['request'].subject.artist_profile.escrow_disabled:
            if value and (value < settings.MINIMUM_PRICE):
                raise ValidationError('Must be $0 or at least ${}'.format(settings.MINIMUM_PRICE))
        return value


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


class OrderCharacterTagSerializer(serializers.ModelSerializer):
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
        model = Order.characters.through


class SubmissionFromOrderSerializer(RelatedAtomicMixin, serializers.ModelSerializer):
    tags = TagListField(required=False)

    class Meta:
        model = Submission
        fields = (
            'id', 'title', 'caption', 'private', 'created_on', 'tags', 'comments_disabled',
        )
        read_only_fields = (
            'tags',
        )


class OrderAuthSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    claim_token = ShortUIDField()
    chown = serializers.BooleanField()
