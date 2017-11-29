from rest_framework import serializers

from apps.lib.models import Comment
from apps.profiles.models import User


class RelatedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')
        read_only_fields = ('id', 'username')


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

