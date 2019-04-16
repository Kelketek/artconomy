from factory import SubFactory, Sequence
from factory.django import DjangoModelFactory

from apps.lib.models import Comment
from apps.profiles.tests.factories import UserFactory


class CommentFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    text = Sequence(lambda n: 'Test comment {0}'.format(n))

    class Meta:
        model = Comment
