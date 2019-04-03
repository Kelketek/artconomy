from django_otp.plugins.otp_totp.models import TOTPDevice
from factory import Sequence, PostGenerationMethodCall, SubFactory
from factory.django import DjangoModelFactory, ImageField
from django.conf import settings

from apps.profiles.models import Character, ImageAsset, Message, MessageRecipientRelationship


class UserFactory(DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    username = Sequence(lambda n: 'user{0}'.format(n))
    email = Sequence(lambda n: 'person{0}@example.com'.format(n))
    password = PostGenerationMethodCall('set_password', 'Test')


class CharacterFactory(DjangoModelFactory):
    class Meta:
        model = Character

    name = Sequence(lambda n: 'FOXSIS ID {0}'.format(n))
    description = Sequence(lambda n: 'Fox with FOXSIS id {0}'.format(n))
    user = SubFactory(UserFactory)


class ImageAssetFactory(DjangoModelFactory):
    class Meta:
        model = ImageAsset

    file = ImageField(color='blue')
    title = Sequence(lambda n: 'Image {0}'.format(n))
    caption = Sequence(lambda n: 'This is image {0}'.format(n))
    owner = SubFactory(UserFactory)


class MessageFactory(DjangoModelFactory):
    sender = SubFactory(UserFactory)
    subject = Sequence(lambda n: 'Message {}'.format(n))
    body = Sequence(lambda n: 'Body {}'.format(n))

    class Meta:
        model = Message


class MessageRecipientRelationshipFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    message = SubFactory(MessageFactory)

    class Meta:
        model = MessageRecipientRelationship


class TOTPDeviceFactory(DjangoModelFactory):
    name = Sequence(lambda x: f'Device {x}')
    user = SubFactory(UserFactory)
    confirmed = True

    class Meta:
        model = TOTPDevice
