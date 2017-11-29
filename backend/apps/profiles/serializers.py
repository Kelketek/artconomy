from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import connection
from django.middleware.csrf import get_token
from rest_framework import serializers

from apps.lib.serializers import RelatedUserSerializer
from apps.profiles.models import Character, ImageAsset, User


class RegisterSerializer(serializers.ModelSerializer):

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
            'username', 'email', 'password', 'csrftoken'
        )
        read_only_fields = (
            'csrftoken',
        )
        write_only_fields = (
            'username', 'email', 'password'
        )


class ImageAssetSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    comment_count = serializers.SerializerMethodField()
    favorite_count = serializers.SerializerMethodField()

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

    def get_favorite_count(self, obj):
        # Placeholder
        return 0

    def get_thumbnail_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.file.url)

    class Meta:
        model = ImageAsset
        fields = (
            'id', 'title', 'caption', 'rating', 'file', 'private', 'created_on', 'uploaded_by', 'comment_count',
            'favorite_count',
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
            'primary_asset', 'primary_asset_id'
        )


class ImageAssetManagementSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    characters = CharacterSerializer(many=True)

    def get_thumbnail_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.file.url)

    class Meta:
        model = ImageAsset
        fields = ('id', 'title', 'caption', 'rating', 'file', 'private', 'created_on', 'uploaded_by', 'characters')


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'commissions_closed', 'rating', 'sfw_mode', 'max_load'
        )


class UserSerializer(serializers.ModelSerializer):
    dwolla_configured = serializers.SerializerMethodField()
    csrftoken = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def get_dwolla_configured(self, obj):
        return bool(obj.dwolla_url)

    def get_csrftoken(self, value):
        return get_token(self.request)

    class Meta:
        model = User
        fields = (
            'commissions_closed', 'rating', 'sfw_mode', 'max_load', 'username', 'id', 'is_staff', 'is_superuser',
            'dwolla_configured', 'csrftoken',
        )
        read_only_fields = fields
