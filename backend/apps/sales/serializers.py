from datetime import datetime, date

from django.conf import settings
from django.core.validators import RegexValidator
from luhn import verify
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, DecimalField, IntegerField

from apps.lib.serializers import RelatedUserSerializer, Base64ImageField
from apps.lib.utils import country_choices
from apps.profiles.serializers import CharacterSerializer
from apps.sales.models import Product, Order, CreditCardToken, Revision


class ProductSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    file = Base64ImageField(thumbnail_namespace='sales.Product.file')

    def get_thumbnail_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.file.url)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'category', 'revisions', 'hidden', 'max_parallel', 'task_weight',
            'expected_turnaround', 'user', 'file', 'rating', 'price'
        )


class ProductNewOrderSerializer(serializers.ModelSerializer):
    seller = RelatedUserSerializer(read_only=True)
    buyer = RelatedUserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'placed_on', 'status', 'product', 'details', 'seller', 'buyer', 'characters')
        read_only_fields = (
            'status', 'id', 'placed_on'
        )


class OrderViewSerializer(serializers.ModelSerializer):
    seller = RelatedUserSerializer(read_only=True)
    buyer = RelatedUserSerializer(read_only=True)
    characters = CharacterSerializer(many=True, read_only=True)
    price = SerializerMethodField()
    product = ProductSerializer()

    def get_price(self, obj):
        if not obj.price:
            return obj.product.price.amount
        return obj.price.amount

    class Meta:
        model = Order
        fields = (
            'id', 'placed_on', 'status', 'price', 'product', 'details', 'seller', 'buyer', 'adjustment', 'characters'
        )
        read_only_fields = fields


class OrderAdjustSerializer(OrderViewSerializer):

    def validate(self, attrs):
        if attrs['adjustment'] is None:
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
        fields = ('id', 'user', 'last_four', 'card_type', 'primary')
        read_only_fields = fields


class NewCardSerializer(serializers.Serializer):
    """
    Form for getting and saving a credit card.
    """
    card_number = serializers.CharField(max_length=25)
    # If this code lasts long enough for this to be a problem, I will be both surprised and happy.
    exp_date = serializers.CharField(max_length=5, min_length=5)
    security_code = serializers.CharField(max_length=4, min_length=3, validators=[RegexValidator(r'\d+')])
    zip = serializers.CharField(max_length=20, required=False)

    def validate_exp_date(self, value):
        params = value.split('/')
        if len(params) != 2:
            raise serializers.ValidationError("Date must be in the format MM/YY.")
        try:
            # Avoid Y2K problem while still supporting two digit year.
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


class RevisionSerializer(serializers.ModelSerializer):
    """
    Serializer for order revisions.
    """
    uploaded_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

    def get_thumbnail_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.file.url)

    class Meta:
        model = Revision
        fields = ('id', 'rating', 'file', 'created_on', 'uploaded_by', 'order')
        read_only_fields = ('id', 'order', 'uploaded_by')
