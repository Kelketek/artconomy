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

from apps.lib.serializers import RelatedUserSerializer, Base64ImageField, TagSerializer
from apps.profiles.apis import dwolla_setup_link
from apps.profiles.models import Character, ImageAsset, User


class RegisterSerializer(serializers.ModelSerializer):
    csrftoken = serializers.SerializerMethodField()
    recaptcha = ReCaptchaField(write_only=True)

    def create(self, validated_data):
        validated_data = {key: value for key, value in validated_data.items() if key != 'recaptcha'}
        return super(RegisterSerializer, self).create(validated_data)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def get_csrftoken(self, value):
        return get_token(self.request)

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
        write_only_fields = (
            'username', 'email', 'password'
        )


class ImageAssetSerializer(serializers.ModelSerializer):
    uploaded_by = RelatedUserSerializer(read_only=True)
    comment_count = serializers.SerializerMethodField()
    file = Base64ImageField(thumbnail_namespace='profiles.ImageAsset.file')

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

    class Meta:
        model = ImageAsset
        fields = (
            'id', 'title', 'caption', 'rating', 'file', 'private', 'created_on', 'uploaded_by', 'comment_count',
            'favorite_count', 'comments_disabled', 'tags'
        )
        write_only_fields = (
            'file',
        )


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()

    class Meta:
        fields = (
            'avatar',
        )


class ImageAssetNotificationSerializer(serializers.ModelSerializer):
    uploaded_by = RelatedUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    file = Base64ImageField(thumbnail_namespace='profiles.ImageAsset.file')

    class Meta:
        model = ImageAsset
        fields = (
            'id', 'title', 'caption', 'rating', 'file', 'private', 'created_on', 'uploaded_by',
            'favorite_count', 'comments_disabled', 'tags'
        )
        write_only_fields = (
            'file',
        )


class CharacterSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    primary_asset = ImageAssetSerializer(required=False)
    primary_asset_id = serializers.IntegerField(write_only=True, required=False)

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
            'primary_asset', 'primary_asset_id', 'species', 'gender', 'tags'
        )


class ImageAssetManagementSerializer(serializers.ModelSerializer):
    uploaded_by = RelatedUserSerializer(read_only=True)
    artists = RelatedUserSerializer(read_only=True, many=True)
    characters = CharacterSerializer(many=True, read_only=True)
    file = Base64ImageField(read_only=True, thumbnail_namespace='profiles.ImageAsset.file')
    favorite = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def get_favorite(self, obj):
        if not self.request and not self.request.user.is_authenticated():
            return None
        return self.request.user.favorites.filter(id=obj.id).exists()

    def get_thumbnail_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.file.url)

    class Meta:
        model = ImageAsset
        fields = (
            'id', 'title', 'caption', 'rating', 'file', 'private', 'created_on', 'order', 'uploaded_by', 'characters',
            'comments_disabled', 'favorite_count', 'favorite', 'artists', 'tags'
        )


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'commissions_closed', 'rating', 'sfw_mode', 'max_load'
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


class UserSerializer(serializers.ModelSerializer):
    dwolla_configured = serializers.SerializerMethodField()
    csrftoken = serializers.SerializerMethodField()
    authtoken = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    dwolla_setup_url = serializers.SerializerMethodField()
    fee = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def get_dwolla_configured(self, obj):
        return bool(obj.dwolla_url)

    def get_dwolla_setup_url(self, obj):
        return dwolla_setup_link()

    def get_csrftoken(self, value):
        return get_token(self.request)

    def get_avatar_url(self, obj):
        return avatar_url(obj)

    def get_fee(self, obj):
        return .1

    def get_authtoken(self, obj):
        return Token.objects.get(user_id=obj.id).key

    class Meta:
        model = User
        fields = (
            'commissions_closed', 'rating', 'sfw_mode', 'max_load', 'username', 'id', 'is_staff', 'is_superuser',
            'dwolla_configured', 'dwolla_setup_url', 'csrftoken', 'avatar_url', 'email', 'fee', 'authtoken',
            'blacklist'
        )
        read_only_fields = fields
