from _decimal import InvalidOperation, Decimal
from datetime import datetime, date

from django.conf import settings
from django.core.validators import RegexValidator
from luhn import verify
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, DecimalField, IntegerField

from apps.lib.serializers import RelatedUserSerializer, Base64ImageField
from apps.lib.utils import country_choices
from apps.profiles.models import User
from apps.profiles.serializers import CharacterSerializer, ImageAssetSerializer
from apps.sales.models import Product, Order, CreditCardToken, Revision, PaymentRecord
from apps.sales.utils import escrow_balance, available_balance


class ProductSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    file = Base64ImageField(thumbnail_namespace='sales.Product.file')

    def get_thumbnail_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.file.url)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'revisions', 'hidden', 'max_parallel', 'task_weight',
            'expected_turnaround', 'user', 'file', 'rating', 'price', 'tags'
        )


class ProductNewOrderSerializer(serializers.ModelSerializer):
    seller = RelatedUserSerializer(read_only=True)
    buyer = RelatedUserSerializer(read_only=True)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def validate_characters(self, value):
        for character in value:
            if not (self.request.user.is_staff or character.user == self.request.user):
                if character.private or not character.open_requests:
                    raise serializers.ValidationError(
                        'You are not permitted to commission pieces for all of the characters you have specified, or '
                        'one or more characters you specified does not exist.'
                    )
        return value

    class Meta:
        model = Order
        fields = ('id', 'created_on', 'status', 'product', 'details', 'seller', 'buyer', 'characters', 'private')
        read_only_fields = (
            'status', 'id', 'created_on'
        )


class OrderViewSerializer(serializers.ModelSerializer):
    seller = RelatedUserSerializer(read_only=True)
    buyer = RelatedUserSerializer(read_only=True)
    characters = CharacterSerializer(many=True, read_only=True)
    price = SerializerMethodField()
    product = ProductSerializer()
    outputs = ImageAssetSerializer(many=True, read_only=True)

    def get_price(self, obj):
        if not obj.price:
            return obj.product.price.amount
        return obj.price.amount

    class Meta:
        model = Order
        fields = (
            'id', 'created_on', 'status', 'price', 'product', 'details', 'seller', 'buyer', 'adjustment', 'characters',
            'stream_link', 'revisions', 'outputs', 'private'
        )
        read_only_fields = fields


class OrderStartedSerializer(OrderViewSerializer):
    class Meta:
        model = Order
        fields = OrderViewSerializer.Meta.fields
        read_only_fields = tuple(field for field in OrderViewSerializer.Meta.read_only_fields if field != 'stream_link')


class OrderAdjustSerializer(OrderViewSerializer):
    def validate(self, attrs):
        if attrs.get('adjustment') is None:
            return attrs
        if self.instance.product.price.amount + attrs['adjustment'] < settings.MINIMUM_PRICE:
            raise ValidationError("The total price may not be less than ${}".format(settings.MINIMUM_PRICE))
        return attrs

    class Meta(OrderViewSerializer.Meta):
        read_only_fields = tuple(field for field in OrderViewSerializer.Meta.read_only_fields if field != 'adjustment')


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
    amount = DecimalField(max_digits=4, min_value=settings.MINIMUM_PRICE, decimal_places=2)
    cvv = serializers.CharField(validators=[RegexValidator(r'^\d{3,4}$')], required=False, default='', allow_blank=True)


class RevisionSerializer(serializers.ModelSerializer):
    """
    Serializer for order revisions.
    """
    uploaded_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    file = Base64ImageField(thumbnail_namespace='sales.Revision.file')

    def get_thumbnail_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.file.url)

    class Meta:
        model = Revision
        fields = ('id', 'rating', 'file', 'created_on', 'uploaded_by', 'order')
        read_only_fields = ('id', 'order', 'uploaded_by')


class AccountBalanceSerializer(serializers.ModelSerializer):
    escrow = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()

    def get_escrow(self, obj):
        return escrow_balance(obj)

    def get_available(self, obj):
        return available_balance(obj)

    class Meta:
        model = User
        fields = ('escrow', 'available')
