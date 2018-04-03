from factory import SubFactory, Sequence
from factory.django import DjangoModelFactory

from apps.lib.models import Comment, Tag
from apps.profiles.tests.factories import UserFactory


class CommentFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    text = Sequence(lambda n: 'Test comment {0}'.format(n))

    class Meta:
        model = Comment


class TagFactory(DjangoModelFactory):
    name = Sequence(lambda n: 'Tag {}'.format(n))

    class Meta:
        model = Tag
