from urllib.parse import quote_plus

from avatar.templatetags.avatar_tags import avatar_url
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import connection
from django.middleware.csrf import get_token
from recaptcha.fields import ReCaptchaField
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from apps.lib.abstract_models import RATINGS
from apps.lib.serializers import RelatedUserSerializer, Base64ImageField, TagSerializer, SubscribedField, \
    SubscribeMixin, UserInfoMixin
from apps.profiles.models import Character, ImageAsset, User, RefColor, Attribute, Message, MessageRecipientRelationship


class RegisterSerializer(serializers.ModelSerializer):
    csrftoken = serializers.SerializerMethodField()
    recaptcha = ReCaptchaField(write_only=True)

    def create(self, validated_data):
        validated_data = {key: value for key, value in validated_data.items() if key != 'recaptcha'}
        return super(RegisterSerializer, self).create(validated_data)

    def get_csrftoken(self, value):
        return get_token(self.context['request'])

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise ValidationError("An account with this email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise ValidationError("An account with this username already exists.")
        return value

    def validate_password(self, value):
        if len(value) < settings.MIN_PASS_LENGTH:
            raise ValidationError("That password is too short.")
        return value

    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'csrftoken', 'recaptcha'
        )
        read_only_fields = (
            'csrftoken',
        )
        extra_kwargs = {
            'username': {'write_only': True},
            'email': {'write_only': True},
            'password': {'write_only': True}
        }


class ImageAssetSerializer(serializers.ModelSerializer):
    owner = RelatedUserSerializer(read_only=True)
    comment_count = serializers.SerializerMethodField()
    file = Base64ImageField(thumbnail_namespace='profiles.ImageAsset.file')
    is_artist = serializers.BooleanField(write_only=True)
    subscribed = SubscribedField(required=False)

    def get_comment_count(self, obj):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                WITH RECURSIVE q AS (SELECT id, parent_id, content_type_id, object_id
                                       FROM lib_comment
                                      WHERE object_id=%s AND content_type_id=%s
                                      UNION ALL
                                     SELECT m.id, m.parent_id, m.content_type_id, m.object_id
                                       FROM lib_comment m
                                       JOIN q ON q.id = m.parent_id)
                    SELECT COUNT(id) FROM q
                """,
                [obj.id, ContentType.objects.get(app_label="profiles", model="imageasset").id]
            )
            return cursor.fetchone()[0]

    def create(self, validated_data):
        data = dict(**validated_data)
        # Remove all of the data we need to handle specially in the view.
        data.pop('is_artist', None)
        data.pop('characters', None)
        data.pop('artists', None)
        return super().create(data)

    class Meta:
        model = ImageAsset
        fields = (
            'id', 'title', 'caption', 'rating', 'file', 'private', 'created_on', 'owner', 'comment_count',
            'favorite_count', 'comments_disabled', 'tags', 'is_artist', 'characters', 'artists', 'subscribed'
        )
        extra_kwargs = {
            'file': {'write_only': True},
            'characters': {'write_only': True},
            'artists': {'write_only': True}
        }
        read_only_fields = (
            'tags',
        )


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()

    class Meta:
        fields = (
            'avatar',
        )


class ImageAssetNotificationSerializer(serializers.ModelSerializer):
    owner = RelatedUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    file = Base64ImageField(thumbnail_namespace='profiles.ImageAsset.file')

    class Meta:
        model = ImageAsset
        fields = (
            'id', 'title', 'caption', 'rating', 'file', 'private', 'created_on', 'owner',
            'favorite_count', 'comments_disabled', 'tags'
        )
        extra_kwargs = {
            'file': {'write_only': True}
        }
        write_only_fields = (
            'file',
        )


class RefColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefColor
        fields = ('id', 'color', 'note')


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ('id', 'key', 'value', 'sticky')
        read_only_fields = ('sticky',)


class CharacterSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    primary_asset = ImageAssetSerializer(required=False)
    primary_asset_id = serializers.IntegerField(write_only=True, required=False)
    colors = RefColorSerializer(many=True, read_only=True)
    attributes = AttributeSerializer(many=True, read_only=True)
    taggable = serializers.BooleanField(default=True)
    shared_with = RelatedUserSerializer(many=True, read_only=True)

    def validate_primary_asset_id(self, value):
        if value is None:
            return None
        try:
            ImageAsset.objects.get(id=value, character=self.instance)
        except ImageAsset.DoesNotExist:
            raise ValidationError("That asset does not exist.")
        return value

    class Meta:
        model = Character
        fields = (
            'id', 'name', 'description', 'private', 'open_requests', 'open_requests_restrictions', 'user',
            'primary_asset', 'primary_asset_id', 'tags', 'colors', 'taggable', 'attributes', 'transfer',
            'shared_with'
        )
        read_only_fields = ('transfer',)


class ImageAssetManagementSerializer(SubscribeMixin, serializers.ModelSerializer):
    owner = RelatedUserSerializer(read_only=True)
    artists = RelatedUserSerializer(read_only=True, many=True)
    characters = CharacterSerializer(many=True, read_only=True)
    file = Base64ImageField(read_only=True, thumbnail_namespace='profiles.ImageAsset.file')
    favorite = serializers.SerializerMethodField()
    subscribed = SubscribedField(required=False)
    shared_with = RelatedUserSerializer(read_only=True, many=True)

    def get_favorite(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        if not request.user.is_authenticated:
            return None
        return request.user.favorites.filter(id=obj.id).exists()

    def get_thumbnail_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.file.url)

    class Meta:
        model = ImageAsset
        fields = (
            'id', 'title', 'caption', 'rating', 'file', 'private', 'created_on', 'order', 'owner', 'characters',
            'comments_disabled', 'favorite_count', 'favorite', 'artists', 'tags', 'subscribed', 'shared_with'
        )


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'commissions_closed', 'rating', 'sfw_mode', 'max_load', 'favorites_hidden', 'taggable', 'commission_info',
        )


class CorrectPasswordValidator(object):
    """
    Validates that the correct password was entered.
    """
    def set_context(self, serializer_field):
        self.instance = serializer_field.parent.instance

    def __call__(self, value):
        if not self.instance.check_password(value):
            raise ValidationError("That is not the correct password for this account.")


class FieldUniqueValidator(object):
    """
    Validates that a field is unique. Model field name can be a Django queryset API keyword, such as username__iexact.
    """

    def __init__(self, model_field_name, error_msg, model=None):
        self.model = model
        self.model_field_name = model_field_name
        self.error_msg = error_msg

    def set_context(self, serializer_field):
        self.instance = serializer_field.parent.instance

    def __call__(self, value):
        kwargs = {'pk': self.instance.pk, self.model_field_name: value}
        if self.model.objects.filter(**kwargs).exists():
            # This is already the current value.
            return
        if self.model.objects.filter(**{self.model_field_name: value}).exists():
            raise ValidationError(self.error_msg)


class CredentialsSerializer(serializers.ModelSerializer):
    username = serializers.SlugField(
        validators=[FieldUniqueValidator('username__iexact', 'This username is already taken.', User)],
        required=False
    )
    # Confirmation of new password should be done on client-side and refuse to send unless verified.
    new_password = serializers.CharField(
        write_only=True, required=False, allow_blank=True, validators=[validate_password]
    )
    current_password = serializers.CharField(write_only=True, validators=[CorrectPasswordValidator()])
    email = serializers.EmailField(
        validators=[FieldUniqueValidator('email__iexact', 'This email address is already taken.', User)],
        required=False,
    )

    def update(self, instance, validated_data):
        instance = super(CredentialsSerializer, self).update(instance, validated_data)
        if 'new_password' in validated_data and validated_data['new_password']:
            instance.set_password(validated_data['new_password'])
            instance.save()
        return instance

    class Meta:
        model = User
        fields = (
            'username', 'current_password', 'new_password', 'email'
        )


class UserSerializer(UserInfoMixin, serializers.ModelSerializer):
    dwolla_configured = serializers.SerializerMethodField()
    csrftoken = serializers.SerializerMethodField()
    authtoken = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    percentage_fee = serializers.DecimalField(decimal_places=2, max_digits=3)
    static_fee = serializers.DecimalField(decimal_places=2, max_digits=5)
    portrait_paid_through = serializers.DateField(read_only=True)
    landscape_paid_through = serializers.DateField(read_only=True)
    telegram_link = serializers.SerializerMethodField()
    has_products = serializers.SerializerMethodField()
    watching = serializers.SerializerMethodField()
    blocked = serializers.SerializerMethodField()

    def get_dwolla_configured(self, obj):
        return bool(obj.dwolla_url)

    def get_csrftoken(self, obj):
        # This will be the CSRFToken of the requesting user rather than the target user-- not a security risk,
        # but also not intuitively clear that it's not the right data if someone were trying to attack.
        return get_token(self.context['request'])

    def get_telegram_link(self, obj):
        return 'https://t.me/{}/?start={}%3A{}'.format(
            settings.TELEGRAM_BOT_USERNAME, quote_plus(obj.username), obj.tg_key
        )

    def get_avatar_url(self, obj):
        return avatar_url(obj)

    def get_authtoken(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        if not request.user == obj:
            return None
        return Token.objects.get(user_id=obj.id).key

    class Meta:
        model = User
        fields = (
            'commissions_closed', 'rating', 'sfw_mode', 'max_load', 'username', 'id', 'is_staff', 'is_superuser',
            'dwolla_configured', 'csrftoken', 'avatar_url', 'email', 'authtoken', 'favorites_hidden',
            'blacklist', 'biography', 'has_products', 'taggable', 'watching', 'blocked',  'commission_info',
            'stars', 'percentage_fee', 'static_fee', 'portrait', 'portrait_enabled', 'portrait_paid_through',
            'landscape', 'landscape_enabled', 'landscape_paid_through', 'telegram_link'
        )
        read_only_fields = fields


class SessionSettingsSerializer(serializers.Serializer):
    rating = serializers.ChoiceField(choices=RATINGS)


class MessageSerializer(serializers.ModelSerializer):
    sender = RelatedUserSerializer(read_only=True)
    read = serializers.SerializerMethodField()

    def get_read(self, obj):
        user = self.context['request'].user
        if user == obj.sender:
            return obj.sender_read
        if not MessageRecipientRelationship.objects.filter(user=user, message=obj, read=False).exists():
            return True
        return False

    def create(self, validated_data):
        data = dict(**validated_data)
        data.pop('recipients', None)
        return super().create(data)

    class Meta:
        model = Message
        fields = (
            'id', 'recipients', 'sender', 'subject', 'body', 'created_on', 'edited_on', 'read'
        )
        extra_kwargs = {
            'recipients': {'write_only': True, 'queryset': User.objects.all(), 'read_only': False}
        }


class MessageManagementSerializer(serializers.ModelSerializer):
    recipients = RelatedUserSerializer(read_only=True, many=True)
    sender = RelatedUserSerializer(read_only=True)
    read = serializers.SerializerMethodField()

    def get_read(self, obj):
        user = self.context['request'].user
        if user == obj.sender:
            return obj.sender_read
        if not MessageRecipientRelationship.objects.filter(user=user, message=obj, read=False).exists():
            return True
        return False

    class Meta:
        model = Message
        fields = (
            'id', 'recipients', 'sender', 'subject', 'body', 'created_on', 'edited_on', 'read'
        )


class PasswordResetSerializer(serializers.ModelSerializer):
    # Confirmation of new password should be done on client-side and refuse to send unless verified.
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

    class Meta:
        model = User
        fields = (
            'new_password',
        )
