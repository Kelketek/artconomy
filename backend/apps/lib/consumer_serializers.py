"""
Serializers for consumer commands. Separate from normal serializers to prevent circular imports.
"""
from rest_framework import serializers


class WatchSpecSerializer(serializers.Serializer):
    app_label = serializers.CharField()
    model_name = serializers.CharField()
    serializer = serializers.CharField()
    pk = serializers.CharField()


class ViewerParamsSerializer(serializers.Serializer):
    socket_key = serializers.CharField(allow_blank=False, required=True)


class EmptySerializer(serializers.Serializer):
    """
    Shim placeholder for commands that need no payload.
    """
