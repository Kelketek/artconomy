from rest_framework import status

from apps.lib.test_resources import APITestCase
from apps.lib.tests.factories import CommentFactory
from apps.profiles.tests.factories import ImageAssetFactory


class TestComments(APITestCase):
    def test_comment_reply(self):
        asset = ImageAssetFactory.create()
        comment = CommentFactory.create(content_object=asset)
        self.assertEqual(self.user.comment_set.all().count(), 0)
        self.login(self.user)
        response = self.client.post(
            '/api/lib/v1/comment/{}/reply/'.format(comment.id),
            {
                'text': 'This is a new comment',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_comment = response.data
        self.assertEqual(new_comment['children'], [])
        self.assertEqual(new_comment['edited'], False)
        self.assertEqual(new_comment['deleted'], False)
        self.assertEqual(new_comment['text'], 'This is a new comment')
        self.user.refresh_from_db()
        self.assertEqual(self.user.comment_set.all().count(), 1)
