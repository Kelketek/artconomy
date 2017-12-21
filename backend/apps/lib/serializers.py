import base64, uuid

from avatar.templatetags.avatar_tags import avatar_url
from django.core.files.base import ContentFile
from rest_framework import serializers

from apps.lib.models import Comment, Notification, Event
from apps.profiles.models import User, ImageAsset


class RelatedUserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    def get_avatar_url(self, obj):
        return avatar_url(obj)

    class Meta:
        model = User
        fields = ('id', 'username', 'avatar_url')
        read_only_fields = ('id', 'username', 'avatar_url')


# Custom image field - handles base 64 encoded images
class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            # base64 encoded image - decode
            fmt, image_string = data.split(';base64,')  # format ~= data:image/X,
            ext = fmt.split('/')[-1]  # guess file extension
            auto_id = uuid.uuid4()
            data = ContentFile(base64.b64decode(image_string), name=auto_id.urn[9:] + '.' + ext)
        result = super(Base64ImageField, self).to_internal_value(data)
        return result


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    children = RecursiveField(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'created_on', 'edited_on', 'user', 'children', 'edited', 'deleted')
        read_only_fields = ('id', 'created_on', 'edited_on', 'user', 'children', 'edited', 'deleted')


class EventRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        # Avoid circular imports.
        from apps.profiles.serializers import ImageAssetSerializer
        if isinstance(value, User):
            return RelatedUserSerializer(value)
        if isinstance(value, ImageAsset):
            ImageAssetSerializer(value)
        return str(value)


class EventSerializer(serializers.ModelSerializer):
    target = EventRelatedField(read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'type', 'data', 'date', 'target')
        read_only_fields = fields


class NotificationSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ('event', 'read')
        read_only_fields = ('event',)
