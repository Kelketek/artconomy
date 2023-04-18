from apps.lib.models import Comment
from apps.profiles.tests.factories import SubmissionFactory, UserFactory
from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory


class CommentFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    top = SubFactory(SubmissionFactory)
    text = Sequence(lambda n: "Test comment {0}".format(n))

    class Meta:
        model = Comment
