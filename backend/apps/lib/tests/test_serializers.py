from unittest.mock import Mock

from apps.lib.models import Notification
from apps.lib.serializers import comment_made
from apps.lib.test_resources import APITestCase
from apps.lib.tests.factories import CommentFactory
from apps.profiles.tests.factories import ImageAssetFactory


class TestComments(APITestCase):
    def test_comment_serializer(self):
        asset = ImageAssetFactory.create()
        comments = [CommentFactory.create(content_object=asset) for i in range(5)]
        self.assertEqual(Notification.objects.all().count(), 1)
        notification = Notification.objects.first()
        request = Mock()
        request.user = asset.uploaded_by
        context = {'request': request}
        data = comment_made(notification.event, context)
        self.assertEqual(data['additional'], 2)
        self.assertEqual(data['commenters'], [comment.user.username for comment in comments[:3]])
        self.assertEqual(data['display']['id'], asset.id)
        self.assertEqual(data['display']['caption'], asset.caption)
        self.assertEqual(data['is_thread'], False)
        self.assertEqual(
            data['link'],
            {'name': 'Submission', 'params': {'assetID': asset.id}, 'query': {'commentID': comments[-1].id}}
        )
