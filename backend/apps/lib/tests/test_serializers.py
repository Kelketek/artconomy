from unittest.mock import Mock

from django.test import TestCase

from apps.lib.models import Notification, NEW_PRODUCT, Event
from apps.lib.serializers import comment_made, new_product
from apps.lib.test_resources import APITestCase
from apps.lib.tests.factories_interdepend import CommentFactory
from apps.profiles.tests.factories import SubmissionFactory, UserFactory
from apps.sales.tests.factories import ProductFactory


class TestComments(APITestCase):
    def test_comment_serializer(self):
        submission = SubmissionFactory.create()
        comments = [CommentFactory.create(content_object=submission) for i in range(5)]
        self.assertEqual(Notification.objects.all().count(), 1)
        notification = Notification.objects.first()
        request = Mock()
        request.user = submission.owner
        context = {'request': request}
        data = comment_made(notification.event, context)
        self.assertEqual(data['additional'], 2)
        self.assertEqual(data['commenters'], sorted([comment.user.username for comment in comments])[:3])
        self.assertEqual(data['display']['id'], submission.id)
        self.assertEqual(data['display']['caption'], submission.caption)
        self.assertEqual(data['is_thread'], False)
        self.assertEqual(
            data['link'],
            {'name': 'Submission', 'params': {'submissionId': submission.id}, 'query': {'commentId': comments[-1].id}}
        )


class TestNotificationSerializers(TestCase):
    def test_new_product(self):
        user = UserFactory.create()
        product = ProductFactory.create(user=user, primary_submission=SubmissionFactory.create())
        event = Event.objects.create(
            target=user, data={'product': product.id}, type=NEW_PRODUCT,
        )
        request = Mock()
        request.user = user
        output = new_product(event, {'request': request})
        self.assertEqual(output['product']['id'], product.id)
        self.assertEqual(output['product']['name'], product.name)
        self.assertEqual(output['display']['title'], product.primary_submission.title)