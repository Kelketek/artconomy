from datetime import date
from urllib.parse import quote_plus
from uuid import UUID

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.db.transaction import atomic
from django.middleware.csrf import get_token
from django.utils import timezone
from django_otp.plugins.otp_totp.models import TOTPDevice
from recaptcha.fields import ReCaptchaField
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from short_stuff.django.serializers import ShortCodeField

from apps.lib.abstract_models import RATINGS, RATINGS_ANON
from apps.lib.serializers import (
    RelatedUserSerializer, RelatedAssetField, TagSerializer, SubscribedField,
    TagListField,
    RelatedAtomicMixin,
    UserRelationField,
    UserListField,
    CommentSerializer,
    CharacterListField, IdWritable)
from apps.profiles.models import (
    Character, Submission, User, RefColor, Attribute, Conversation,
    ConversationParticipant, Journal, banned_named_validator,
    banned_prefix_validator,
    ArtistProfile
)
from apps.sales.models import Promo
from apps.tg_bot.models import TelegramDevice


class RegisterSerializer(serializers.ModelSerializer):
    csrftoken = serializers.SerializerMethodField()
    recaptcha = ReCaptchaField(write_only=True)
    registration_code = serializers.CharField(required=False, write_only=True, allow_blank=True)
    mail = serializers.BooleanField(write_only=True, required=False)
    order_claim = ShortCodeField(required=False, allow_null=True)

    def create(self, validated_data):
        data = {key: value for key, value in validated_data.items() if key not in [
            'recaptcha', 'mail', 'order_claim'
        ]}
        return super(RegisterSerializer, self).create(data)

    # noinspection PyUnusedLocal
    def get_csrftoken(self, value):
        return get_token(self.context['request'])

    @staticmethod
    def validate_registration_code(value):
        if not value:
            return None
        promo = Promo.objects.filter(code__iexact=value).first()
        if not promo:
            raise ValidationError('We could not find this promo code.')
        if promo.expires and promo.expires < timezone.now():
            raise ValidationError('This promo code has expired.')
        if promo.starts > timezone.now():
            raise ValidationError('This promo code is not active.')
        return promo

    @staticmethod
    def validate_email(value):
        if User.objects.filter(email__iexact=value).exists():
            raise ValidationError("An account with this email already exists.")
        return value

    @staticmethod
    def validate_username(value):
        if User.objects.filter(username__iexact=value).exists():
            raise ValidationError("An account with this username already exists.")
        return value

    @staticmethod
    def validate_password(value):
        if len(value) < settings.MIN_PASS_LENGTH:
            raise ValidationError("That password is too short.")
        return value

    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'csrftoken', 'recaptcha', 'mail', 'registration_code', 'order_claim',
            'artist_mode',
        )
        read_only_fields = (
            'csrftoken',
        )
        extra_kwargs = {
            'username': {'write_only': True},
            'email': {'write_only': True},
            'password': {'write_only': True},
            'registration_code': {'required': False}
        }


class SubmissionSerializer(IdWritable, RelatedAtomicMixin, serializers.ModelSerializer):
    owner = RelatedUserSerializer(read_only=True)
    comment_count = serializers.SerializerMethodField()
    file = RelatedAssetField(thumbnail_namespace='profiles.Submission.file', required=True, allow_null=False)
    preview = RelatedAssetField(
        thumbnail_namespace='profiles.Submission.preview', required=False, allow_null=True,
    )
    artists = UserListField(tag_check=True, block_check=True, back_name='art', write_only=True, required=False)
    characters = CharacterListField(tag_check=True, back_name='submissions', write_only=True, required=False)
    subscribed = SubscribedField(required=False)
    tags = TagListField(required=False)
    private = serializers.BooleanField(default=False)

    # noinspection PyMethodMayBeStatic
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
                [obj.id, ContentType.objects.get(app_label="profiles", model="submission").id]
            )
            return cursor.fetchone()[0]

    @atomic
    def create(self, validated_data):
        instance = super().create(validated_data)
        for character in instance.characters.all():
            if self.context['request'].user == character.user and not character.primary_submission:
                character.primary_submission = instance
                character.save()
        return instance

    class Meta:
        model = Submission
        fields = (
            'id', 'title', 'caption', 'rating', 'file', 'private', 'created_on', 'owner', 'comment_count',
            'favorite_count', 'comments_disabled', 'tags', 'characters', 'artists', 'subscribed',
            'preview'
        )
        read_only_fields = (
            'tags',
        )


class SubmissionNotificationSerializer(serializers.ModelSerializer):
    owner = RelatedUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    file = RelatedAssetField(thumbnail_namespace='profiles.Submission.file')
    preview = RelatedAssetField(thumbnail_namespace='profiles.Submission.preview', required=False, allow_null=True)

    class Meta:
        model = Submission
        fields = (
            'id', 'title', 'caption', 'rating', 'file', 'private', 'created_on', 'owner',
            'favorite_count', 'comments_disabled', 'tags', 'preview'
        )
        extra_kwargs = {
            'file': {'write_only': True}
        }
        write_only_fields = (
            'file',
        )


class SubmissionArtNotificationSerializer(serializers.ModelSerializer):
    file = RelatedAssetField(thumbnail_namespace='profiles.Submission.file')
    preview = RelatedAssetField(thumbnail_namespace='profiles.Submission.preview', required=False)

    class Meta:
        model = Submission
        fields = (
            'id', 'title', 'rating', 'file', 'private', 'preview', 'created_on'
        )
        read_only_fields = fields


class RefColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefColor
        fields = ('id', 'color', 'note')


class AttributeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ('id', 'key', 'value', 'sticky')
        read_only_fields = ('sticky',)


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ('id', 'key', 'value', 'sticky')
        read_only_fields = ('sticky',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.sticky:
            self.fields['value'].allow_blank = True
            self.fields['key'].read_only = True


class CharacterSerializer(RelatedAtomicMixin, serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    primary_submission = SubmissionSerializer(required=False, allow_null=True)
    taggable = serializers.BooleanField(default=True)
    tags = TagListField(required=False)

    class Meta:
        model = Character
        fields = (
            'id', 'name', 'description', 'private', 'open_requests', 'open_requests_restrictions', 'user',
            'primary_submission', 'tags', 'taggable', 'hits',
        )


class CharacterManagementSerializer(RelatedAtomicMixin, serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    primary_submission = SubmissionSerializer(required=False, allow_null=True)
    colors = RefColorSerializer(many=True, read_only=True)
    taggable = serializers.BooleanField(default=True)
    tags = TagListField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context['request'].user
        if (not (user == self.instance.user)) and not user.is_staff:
            for value in self.fields.values():
                value.read_only = True
            if self.instance.user.taggable:
                self.fields['tags'].read_only = False

    def validate_primary_submission_id(self, value):
        if value is None:
            return None
        try:
            Submission.objects.get(id=value, character=self.instance)
        except Submission.DoesNotExist:
            raise ValidationError("That submission does not exist.")
        return value

    class Meta:
        model = Character
        fields = (
            'id', 'name', 'description', 'private', 'open_requests', 'open_requests_restrictions', 'user',
            'primary_submission', 'tags', 'colors', 'taggable', 'hits',
        )


class CharacterSharedSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    def validate_user_id(self, val):
        if self.context['request'].subject.id == val:
            raise ValidationError('You cannot share to yourself!')
        if self.context['request'].subject.blocked_by.filter(id=val):
            raise ValidationError('You cannot share to this person.')
        return val

    class Meta:
        fields = (
            'id', 'user', 'user_id',
        )
        model = Character.shared_with.through


class SubmissionSharedSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    def validate_user_id(self, val):
        user = self.context['request'].user
        if user.id == val:
            raise ValidationError('You cannot share to yourself!')
        if user.blocked_by.filter(id=val):
            raise ValidationError('You cannot share to this person.')
        return val

    class Meta:
        fields = (
            'id', 'user', 'user_id',
        )
        model = Submission.shared_with.through


class SubmissionArtistTagSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    def validate_user_id(self, val):
        if self.context['request'].user.blocked_by.filter(id=val):
            raise ValidationError('You cannot tag this person.')
        if self.context['request'].user.id == val:
            return val
        if not User.objects.filter(id=val, taggable=True):
            raise ValidationError('That user does not exist or has disabled tagging.')
        return val

    class Meta:
        fields = (
            'id', 'user', 'user_id',
        )
        model = Submission.artists.through


class SubmissionCharacterTagSerializer(serializers.ModelSerializer):
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
        model = Submission.characters.through


class SubmissionMixin:
    def get_product(self, obj):
        from apps.sales.serializers import ProductSerializer
        if not (obj.deliverable and obj.deliverable.product):
            return
        if not obj.deliverable.product.available:
            return
        return ProductSerializer(instance=obj.deliverable.product, context=self.context).data

    def get_thumbnail_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.file.file.url)


class SubmissionManagementSerializer(RelatedAtomicMixin, SubmissionMixin, serializers.ModelSerializer):
    owner = RelatedUserSerializer(read_only=True)
    artists = RelatedUserSerializer(read_only=True, many=True)
    file = RelatedAssetField(thumbnail_namespace='profiles.Submission.file')
    preview = RelatedAssetField(thumbnail_namespace='profiles.Submission.preview', required=False, allow_null=True)
    favorites = UserRelationField(required=False)
    subscribed = SubscribedField(required=False)
    product = serializers.SerializerMethodField()
    tags = TagListField(required=False, read_only=True)
    commission_link = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context['request'].user
        if (not (user == self.instance.owner)) and not user.is_staff:
            exempt = ['subscribed', 'favorites']
            for key, value in self.fields.items():
                if key not in exempt:
                    value.read_only = True
            if self.instance.owner.taggable:
                self.fields['tags'].read_only = False
        else:
            self.fields['tags'].read_only = False

    def get_order(self, instance):
        if instance.deliverable:
            return instance.deliverable.order.id

    def get_commission_link(self, instance):
        artists = instance.artists.all()
        if not instance.deliverable and not artists.count():
            return None
        if not instance.deliverable:
            artist = artists.order_by('artist_mode').first()
            return {'name': 'Products' if artist.artist_mode else 'Profile', 'params': {'username': artist.username}}
        # If we know who made this piece, don't give easy credit to anyone else.
        if not artists.filter(id=instance.deliverable.order.seller.id).exists():
            return None
        artist = instance.deliverable.order.seller
        return {'name': 'Products' if artist.artist_mode else 'Profile', 'params': {'username': artist.username}}

    class Meta:
        model = Submission
        fields = (
            'id', 'title', 'caption', 'rating', 'file', 'private', 'created_on', 'order', 'owner', 'characters',
            'comments_disabled', 'favorite_count', 'favorites', 'artists', 'tags', 'subscribed', 'shared_with',
            'preview', 'product', 'hits', 'commission_link',
        )


class ArtistProfileSerializer(serializers.ModelSerializer):

    @staticmethod
    def dwolla_configured(obj):
        return bool(obj.dwolla_url)

    class Meta:
        model = ArtistProfile
        fields = (
            'commissions_closed', 'max_load', 'commission_info',
            'auto_withdraw', 'escrow_disabled', 'bank_account_status', 'max_rating',
            'artist_of_color', 'lgbt',
        )
        extra_kwargs = {field: {'required': False} for field in fields}


class CorrectPasswordValidator(object):
    """
    Validates that the correct password was entered.
    """
    def set_context(self, serializer_field):
        # noinspection PyAttributeOutsideInit
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
        # noinspection PyAttributeOutsideInit
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


class UserSerializer(RelatedAtomicMixin, serializers.ModelSerializer):
    csrftoken = serializers.SerializerMethodField()
    authtoken = serializers.SerializerMethodField()
    portrait_paid_through = serializers.DateField(read_only=True)
    landscape_paid_through = serializers.DateField(read_only=True)
    telegram_link = serializers.SerializerMethodField()
    watching = UserRelationField(required=False)
    blocking = UserRelationField(required=False)
    artist_mode = serializers.BooleanField(required=False)
    blacklist = TagListField(required=False)
    stars = serializers.FloatField(required=False)

    # noinspection PyUnusedLocal
    def get_csrftoken(self, obj):
        # This will be the CSRFToken of the requesting user rather than the target user-- not a security risk,
        # but also not intuitively clear that it's not the right data if someone were trying to attack.
        return get_token(self.context['request'])

    @staticmethod
    def get_telegram_link(obj):
        # tg://resolve?domain=ArtconomyDevBot&start=Fox_9c005d61-8b84-4ad0-81b3-dae876
        return 'https://t.me/{}/?start={}_{}'.format(
            settings.TELEGRAM_BOT_USERNAME, quote_plus(obj.username), obj.tg_key
        )

    def get_authtoken(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        if not request.user == obj:
            return None
        return Token.objects.get(user_id=obj.id).key

    def validate(self, attrs):
        if attrs.get('rating', 0):
            birthday = attrs.get('birthday', self.instance.birthday)
            if birthday is None:
                raise ValidationError({'rating': 'You must indicate your birthday to view adult content.'})
            if relativedelta(date.today(), birthday).years < 18:
                raise ValidationError({'rating': 'You must be at least 18 years old to view adult content.'})
        return attrs

    class Meta:
        model = User
        fields = (
            'rating', 'username', 'id', 'is_staff', 'is_superuser',
            'csrftoken', 'avatar_url', 'email', 'authtoken', 'favorites_hidden',
            'blacklist', 'biography', 'taggable', 'watching', 'blocking',
            'stars', 'portrait', 'portrait_enabled', 'portrait_paid_through',
            'landscape', 'landscape_enabled', 'landscape_paid_through', 'telegram_link', 'sfw_mode',
            'offered_mailchimp', 'guest', 'artist_mode', 'hits', 'watches', 'guest_email', 'rating_count',
            'birthday',
        )
        read_only_fields = [field for field in fields if field not in [
            'rating', 'sfw_mode', 'taggable',
            'offered_mailchimp', 'artist_mode', 'favorites_hidden',
            'blacklist', 'biography', 'rating_count', 'birthday',
        ]]
        extra_kwargs = {field: {'required': False} for field in fields}


# noinspection PyAbstractClass
class SessionSettingsSerializer(serializers.Serializer):
    rating = serializers.ChoiceField(choices=RATINGS_ANON)
    sfw_mode = serializers.BooleanField()
    birthday = serializers.DateField(allow_null=True)

    def validate(self, attrs):
        if attrs.get('rating', 0):
            birthday = attrs.get('birthday')
            if birthday is None:
                raise ValidationError({'rating': 'You must indicate your birthday to view adult content.'})
            if relativedelta(date.today(), birthday).years < 18:
                raise ValidationError({'rating': 'You must be at least 18 years old to view adult content.'})
        return attrs

class ReadMarkerField(serializers.Field):
    save_related = True

    def get_initial(self):
        if hasattr(self, 'initial_data'):
            return self.initial_data
        return False

    def get_attribute(self, instance):
        request = self.context.get('request', None)
        if not request:
            return None
        if not request.user.is_authenticated:
            return None
        if not instance.id:
            return None
        participant_relationship = ConversationParticipant.objects.filter(
            user=request.user, conversation=instance,
        ).first()
        if participant_relationship is None:
            return None
        return participant_relationship.read

    def to_representation(self, instance):
        if isinstance(instance, Conversation):
            return self.get_attribute(instance)
        else:
            return instance

    def to_internal_value(self, data):
        return data

    def mod_instance(self, instance, value):
        request = self.context.get('request', None)
        participant_relationship = ConversationParticipant.objects.get(
            user=request.user, conversation=instance,
        )
        participant_relationship.read = value
        participant_relationship.save()


class ConversationSerializer(RelatedAtomicMixin, serializers.ModelSerializer):
    read = ReadMarkerField(read_only=True)
    participants = UserListField(model=ConversationParticipant, back_name='conversation', add_self=True, min_length=2)

    class Meta:
        model = Conversation
        fields = (
            'id', 'participants', 'created_on', 'read',
        )


class ConversationManagementSerializer(RelatedAtomicMixin, serializers.ModelSerializer):
    participants = RelatedUserSerializer(read_only=True, many=True)
    read = ReadMarkerField()
    last_comment = serializers.SerializerMethodField()

    def get_last_comment(self, obj):
        comment = obj.comments.filter(deleted=False).order_by('-created_on').first()
        if not comment:
            return None
        return CommentSerializer(instance=comment, context=self.context).data

    class Meta:
        model = Conversation
        fields = (
            'id', 'participants', 'created_on', 'read', 'last_comment',
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


class JournalSerializer(RelatedAtomicMixin, serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    subscribed = SubscribedField(required=False)

    class Meta:
        model = Journal
        fields = (
            'id', 'user', 'subject', 'body', 'created_on', 'edited_on', 'comments_disabled', 'subscribed',
            'edited',
        )
        read_only_fields = (
            'id', 'created_on', 'edited_on', 'edited',
        )


class TwoFactorTimerSerializer(serializers.ModelSerializer):
    config_url = serializers.SerializerMethodField()
    code = serializers.CharField(required=False, write_only=True)

    @staticmethod
    def get_config_url(obj):
        if obj.confirmed:
            return None
        return obj.config_url

    def validate_code(self, value):
        return value.replace(' ', '')

    class Meta:
        model = TOTPDevice
        fields = (
            'id', 'name', 'config_url', 'confirmed', 'code'
        )
        read_only_fields = (
            'id', 'config_url', 'confirmed'
        )

    def update(self, instance, validated_data, **kwargs):
        data = dict(**validated_data)
        code = data.pop('code', None)
        if not code:
            raise ValidationError({'code': ['You must supply a verification code.']})
        if instance.verify_token(code):
            instance.confirmed = True
            instance.save()
        else:
            raise ValidationError({'code': ['The verification code you provided was invalid or expired.']})
        return instance


class TelegramDeviceSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=False, write_only=True)

    def update(self, instance, validated_data, **kwargs):
        data = dict(**validated_data)
        code = data.pop('code', None)
        if not code:
            raise ValidationError({'code': ['You must supply a verification code.']})
        if instance.verify_token(code):
            instance.confirmed = True
            instance.save()
        else:
            raise ValidationError({'code': ['The verification code you provided was invalid or expired.']})
        return instance

    def validate_code(self, value):
        return value.replace(' ', '')

    class Meta:
        model = TelegramDevice
        fields = (
            'id', 'confirmed', 'code'
        )
        read_only_fields = (
            'id', 'confirmed'
        )



class ReferralStatsSerializer(serializers.ModelSerializer):
    total_referred = serializers.SerializerMethodField()
    portrait_eligible = serializers.SerializerMethodField()
    landscape_eligible = serializers.SerializerMethodField()

    @staticmethod
    def get_total_referred(obj):
        return User.objects.filter(referred_by=obj).count()

    # noinspection PyUnusedLocal
    @staticmethod
    def get_portrait_eligible(obj):
        return User.objects.filter(referred_by=obj, bought_shield_on__isnull=False).count()

    @staticmethod
    def get_landscape_eligible(obj):
        return User.objects.filter(referred_by=obj, sold_shield_on__isnull=False).count()

    class Meta:
        model = User
        fields = ('total_referred', 'portrait_eligible', 'landscape_eligible')


def user_value_taken(property_name):
    def validate(value):
        if User.objects.filter(**{property_name + '__iexact': value}):
            raise ValidationError("A user with that {} already exists.".format(property_name))
    return validate


# noinspection PyAbstractClass
class ContactSerializer(serializers.Serializer):
    email = serializers.EmailField()
    body = serializers.CharField(max_length=10000)
    referring_url = serializers.CharField(max_length=1000, required=False)


# noinspection PyAbstractClass
class PasswordValidationSerializer(serializers.Serializer):
    password = serializers.CharField(validators=[validate_password])


# noinspection PyAbstractClass
class UsernameValidationSerializer(serializers.Serializer):
    username = serializers.CharField(validators=[
        UnicodeUsernameValidator(), banned_named_validator, banned_prefix_validator, user_value_taken('username')
    ])


# noinspection PyAbstractClass
class EmailValidationSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[user_value_taken('email')])
