from avatar.models import Avatar
from django_otp.plugins.otp_totp.models import TOTPDevice
from factory import Sequence, PostGenerationMethodCall, SubFactory, RelatedFactory
from factory.django import DjangoModelFactory, ImageField
from django.conf import settings

from apps.lib.tests.factories import AssetFactory
from apps.profiles.models import Character, Submission, Conversation, ConversationParticipant, ArtistProfile, Journal, \
    Attribute


class ArtistProfileFactory(DjangoModelFactory):
    class Meta:
        model = ArtistProfile


class UserFactory(DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    username = Sequence(lambda n: 'user{0}'.format(n))
    email = Sequence(lambda n: 'person{0}@example.com'.format(n))
    password = PostGenerationMethodCall('set_password', 'Test')
    authorize_token = Sequence(lambda n: '{}'.format(n).zfill(8))
    artist_profile = RelatedFactory(ArtistProfileFactory, factory_related_name='user')


class CharacterFactory(DjangoModelFactory):
    class Meta:
        model = Character

    name = Sequence(lambda n: 'FOXSIS ID {0}'.format(n))
    description = Sequence(lambda n: 'Fox with FOXSIS id {0}'.format(n))
    user = SubFactory(UserFactory)


class SubmissionFactory(DjangoModelFactory):
    class Meta:
        model = Submission

    file = SubFactory(AssetFactory)
    title = Sequence(lambda n: 'Image {0}'.format(n))
    caption = Sequence(lambda n: 'This is image {0}'.format(n))
    owner = SubFactory(UserFactory)


class ConversationFactory(DjangoModelFactory):
    class Meta:
        model = Conversation


class ConversationParticipantFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    conversation = SubFactory(ConversationFactory)

    class Meta:
        model = ConversationParticipant


class TOTPDeviceFactory(DjangoModelFactory):
    name = Sequence(lambda x: f'Device {x}')
    user = SubFactory(UserFactory)
    confirmed = True

    class Meta:
        model = TOTPDevice


class JournalFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    subject = Sequence(lambda n: 'Message {}'.format(n))
    body = Sequence(lambda n: 'Body {}'.format(n))

    class Meta:
        model = Journal


class AttributeFactory(DjangoModelFactory):
    character = SubFactory(CharacterFactory)
    key = Sequence(lambda n: f'Key {n}')
    value = Sequence(lambda n: f'Value {n}')

    class Meta:
        model = Attribute


class AvatarFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    avatar = ImageField(color='blue')
    primary = True

    class Meta:
        model = Avatar
