from django.conf import settings
from django.core.validators import RegexValidator
from django.utils.datetime_safe import datetime, date
from luhn import verify
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, DecimalField, IntegerField, FileField

from apps.lib.serializers import RelatedUserSerializer, Base64ImageField, EventTargetRelatedField, SubscribedField, \
    SubscribeMixin
from apps.lib.utils import country_choices
from apps.profiles.models import User, ImageAsset
from apps.profiles.serializers import CharacterSerializer, ImageAssetSerializer
from apps.sales.models import Product, Order, CreditCardToken, Revision, PaymentRecord, BankAccount, CharacterTransfer, \
    PlaceholderSale, Rating, OrderToken
from apps.sales.utils import escrow_balance, available_balance, pending_balance


class ProductSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    file = Base64ImageField(thumbnail_namespace='sales.Product.file', _DjangoImageField=FileField)
    preview = Base64ImageField(thumbnail_namespace='profiles.ImageAsset.preview', required=False)

    def get_thumbnail_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.file.url)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'revisions', 'hidden', 'max_parallel', 'task_weight',
            'expected_turnaround', 'user', 'file', 'rating', 'price', 'tags', 'preview', 'available',
            'featured'
        )
        read_only_fields = ('tags', 'featured')


class ProductNewOrderSerializer(serializers.ModelSerializer):
    seller = RelatedUserSerializer(read_only=True)
    buyer = RelatedUserSerializer(read_only=True)
    order_token = serializers.CharField(max_length=8, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def validate_characters(self, value):
        for character in value:
            if not (self.request.user.is_staff or character.user == self.request.user):
                private = character.private and not character.shared_with.filter(id=self.request.user.id)
                if private or not character.open_requests:
                    raise serializers.ValidationError(
                        'You are not permitted to commission pieces for all of the characters you have specified, or '
                        'one or more characters you specified does not exist.'
                    )
        return value

    def create(self, validated_data):
        data = dict(**validated_data)
        data.pop('order_token', None)
        return super().create(data)

    class Meta:
        model = Order
        fields = (
            'id', 'created_on', 'status', 'product', 'details', 'seller', 'buyer', 'characters', 'private',
            'order_token',
        )
        extra_kwargs = {
            'order_token': {'write_only': True, 'read_only': False},
            'characters': {'required': False},
        }
        read_only_fields = (
            'status', 'id', 'created_on'
        )


class OrderViewSerializer(SubscribeMixin, serializers.ModelSerializer):
    seller = RelatedUserSerializer(read_only=True)
    buyer = RelatedUserSerializer(read_only=True)
    characters = CharacterSerializer(many=True, read_only=True)
    price = SerializerMethodField()
    product = ProductSerializer(read_only=True)
    outputs = ImageAssetSerializer(many=True, read_only=True)
    subscribed = SubscribedField()

    def get_price(self, obj):
        if not obj.price:
            return obj.product.price.amount
        return obj.price.amount

    class Meta:
        model = Order
        fields = (
            'id', 'created_on', 'status', 'price', 'product', 'details', 'seller', 'buyer', 'adjustment', 'characters',
            'stream_link', 'revisions', 'outputs', 'private', 'subscribed', 'adjustment_task_weight',
            'adjustment_expected_turnaround', 'expected_turnaround', 'task_weight', 'paid_on', 'dispute_available_on',
            'auto_finalize_on', 'started_on', 'escrow_disabled',
        )
        read_only_fields = fields


class OrderStartedSerializer(OrderViewSerializer):
    class Meta:
        model = Order
        fields = OrderViewSerializer.Meta.fields
        read_only_fields = tuple(field for field in OrderViewSerializer.Meta.read_only_fields if field != 'stream_link')


class OrderAdjustSerializer(OrderViewSerializer):
    def validate(self, attrs):
        errors = {}
        if attrs.get('adjustment'):
            if self.instance.product.price.amount + attrs['adjustment'] < settings.MINIMUM_PRICE:
                errors['adjustment'] = "The total price may not be less than ${}".format(settings.MINIMUM_PRICE)
        if attrs.get('adjustment_task_weight'):
            if self.instance.product.task_weight + attrs['adjustment_task_weight'] < 1:
                errors['adjustment_task_weight'] = 'Task weight may not be less than 1.'
        if attrs.get('adjustment_expected_turnaround'):
            if (
                    self.instance.product.expected_turnaround
                    + attrs['adjustment_expected_turnaround'] < settings.MINIMUM_TURNAROUND
            ):
                errors['adjustment_expected_turnaround'] = 'Expected turnaround may not be less than {}'.format(
                    settings.MINIMUM_TURNAROUND
                )
        if errors:
            raise ValidationError(errors)

        return attrs

    class Meta(OrderViewSerializer.Meta):
        read_only_fields = tuple(
            field for field in OrderViewSerializer.Meta.read_only_fields if field not in [
                'adjustment', 'adjustment_expected_turnaround', 'adjustment_task_weight'
            ]
        )


class CardSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    primary = SerializerMethodField('is_primary')

    def is_primary(self, obj):
        return obj.user.primary_card_id == obj.id

    class Meta:
        model = CreditCardToken
        fields = ('id', 'user', 'last_four', 'card_type', 'primary', 'cvv_verified')
        read_only_fields = fields


class NewCardSerializer(serializers.Serializer):
    """
    Form for getting and saving a credit card.
    """
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    country = serializers.ChoiceField(choices=country_choices())
    card_number = serializers.CharField(max_length=25)
    exp_date = serializers.CharField(max_length=5, min_length=4)
    zip = serializers.CharField(max_length=20, required=False)
    cvv = serializers.CharField(max_length=4, min_length=3, validators=[RegexValidator(r'^[0-9]{3,4}$')])
    make_primary = serializers.BooleanField()

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

    def validate_card_number(self, value):
        value = value.replace(' ', '')
        if 13 <= len(value) <= 19:
            if not verify(value):
                raise serializers.ValidationError("Please check the card number.")
            return value
        raise serializers.ValidationError("A card number must be at least 13 digits long and at most 19.")


class PaymentSerializer(serializers.Serializer):
    """
    Serializer for taking payments
    """
    card_id = IntegerField()
    amount = DecimalField(max_digits=6, min_value=settings.MINIMUM_PRICE, decimal_places=2)
    cvv = serializers.CharField(validators=[RegexValidator(r'^\d{3,4}$')], required=False, default='', allow_blank=True)


class ServicePaymentSerializer(serializers.Serializer):
    """
    Serializer for taking payments
    """
    card_id = IntegerField()
    service = serializers.ChoiceField(choices=('portrait', 'landscape'))
    cvv = serializers.CharField(validators=[RegexValidator(r'^\d{3,4}$')], required=False, default='', allow_blank=True)


class RevisionSerializer(serializers.ModelSerializer):
    """
    Serializer for order revisions.
    """
    owner = serializers.SlugRelatedField(slug_field='username', read_only=True)
    file = Base64ImageField(thumbnail_namespace='sales.Revision.file', _DjangoImageField=FileField)

    def get_thumbnail_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.file.url)

    class Meta:
        model = Revision
        fields = ('id', 'rating', 'file', 'created_on', 'owner', 'order')
        read_only_fields = ('id', 'order', 'owner')


class AccountBalanceSerializer(serializers.ModelSerializer):
    escrow = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()
    pending = serializers.SerializerMethodField()

    def get_escrow(self, obj):
        return str(escrow_balance(obj))

    def get_available(self, obj):
        return str(available_balance(obj))

    def get_pending(self, obj):
        return str(pending_balance(obj))

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


class WithdrawSerializer(serializers.Serializer):
    bank = serializers.IntegerField()
    amount = serializers.DecimalField(6, decimal_places=2, min_value=1)


class PaymentRecordSerializer(serializers.ModelSerializer):
    payer = RelatedUserSerializer(read_only=True)
    payee = RelatedUserSerializer(read_only=True)
    escrow_for = RelatedUserSerializer(read_only=True)
    target = EventTargetRelatedField(read_only=True)
    card = CardSerializer(read_only=True)
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(PaymentRecordSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        result = super().to_representation(instance)
        if instance.payer != self.user:
            # In this case the user should not have access to the card information.
            result['card'] = None
        return result

    class Meta:
        model = PaymentRecord
        fields = (
            'id', 'source', 'status', 'type', 'card', 'payer', 'payee', 'escrow_for', 'amount', 'txn_id', 'created_on',
            'response_code', 'response_message', 'finalized', 'target'
        )
        read_only_fields = fields


class CharacterTransferSerializer(serializers.ModelSerializer):
    character = CharacterSerializer(read_only=True)
    seller = RelatedUserSerializer(read_only=True)
    buyer = RelatedUserSerializer(read_only=True)

    class Meta:
        model = CharacterTransfer
        fields = (
            'status', 'created_on', 'buyer', 'seller', 'character', 'price', 'include_assets', 'id',
            'saved_name', 'completed_on'
        )
        read_only_fields = ('seller', 'character', 'created_on', 'status', 'buyer', 'id', 'saved_name', 'completed_on')


class PlaceholderSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceholderSale
        fields = (
            'id', 'title', 'status', 'task_weight', 'description', 'expected_turnaround'
        )


class PublishFinalSerializer(serializers.ModelSerializer):
    preview = Base64ImageField(thumbnail_namespace='profiles.ImageAsset.preview', required=False)

    class Meta:
        model = ImageAsset
        fields = (
            'title', 'caption', 'preview'
        )


class RatingSerializer(serializers.ModelSerializer):
    rater = RelatedUserSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = (
            'stars',
            'comments',
            'rater',
            'id'
        )
        read_only_fields = ('rater', 'id')


class OrderTokenSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderToken
        fields = (
            'id',
            'product',
            'activation_code',
            'expires_on',
            'email'
        )
        read_only_fields = (
            'id',
            'product',
            'activation_code',
            'expires_on',
        )


class SearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(required=False)
    shield_only = serializers.BooleanField(required=False)
    watchlist_only = serializers.BooleanField(required=False)
    by_rating = serializers.BooleanField(required=False)
    featured = serializers.BooleanField(required=False)
    min_price = serializers.DecimalField(decimal_places=2, max_digits=6, required=False)
    max_price = serializers.DecimalField(decimal_places=2, max_digits=6, required=False)
