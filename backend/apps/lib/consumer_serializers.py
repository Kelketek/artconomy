"""
Serializers for consumer commands. Separate from normal serializers to prevent circular imports.
"""
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from rest_framework import serializers


dotless = RegexValidator(r'.*[.].*', inverse_match=True, message='May not have a "." in this field.')


class WatchNewSpecSerializer(serializers.Serializer):
    app_label = serializers.CharField(validators=[dotless])
    model_name = serializers.CharField(validators=[dotless])
    serializer = serializers.CharField(validators=[dotless])
    pk = serializers.CharField(required=False, validators=[dotless])
    list_name = serializers.CharField(validators=[dotless])

    def validate_list_name(self, val):
        if '.' in val:
            raise ValidationError('Cannot have a dot in list_name')
        return val


class WatchSpecSerializer(serializers.Serializer):
    app_label = serializers.CharField(validators=[dotless])
    model_name = serializers.CharField(validators=[dotless])
    serializer = serializers.CharField(validators=[dotless])
    pk = serializers.CharField(validators=[dotless])


class ViewerParamsSerializer(serializers.Serializer):
    socket_key = serializers.CharField(allow_blank=False, required=True)


class EmptySerializer(serializers.Serializer):
    """
    Shim placeholder for commands that need no payload.
    """
