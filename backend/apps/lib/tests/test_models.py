from rest_framework import status

from apps.lib.models import Notification
from apps.lib.test_resources import APITestCase
from apps.lib.tests.factories import CommentFactory
from apps.profiles.tests.factories import ImageAssetFactory, UserFactory


class TestComments(APITestCase):
    def test_comment_reply(self):
        user = UserFactory.create()
        asset = ImageAssetFactory.create()
        # Start with initial comment, check notification is sent.
        comment = CommentFactory.create(content_object=asset)
        self.assertEqual(user.comment_set.all().count(), 0)
        notifications = Notification.objects.all()
        self.assertEqual(notifications.count(), 1)
        notification = notifications[0]
        self.assertEqual(notification.user, asset.owner)
        self.assertEqual(notification.event.data['comments'], [comment.id])
        self.assertEqual(notification.event.data['subcomments'], [])
        self.assertEqual(notification.event.target, asset)
        # Create a reply to the comment
        self.login(user)
        response = self.client.post(
            '/api/lib/v1/comment/{}/reply/'.format(comment.id),
            {
                'text': 'This is a new comment',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_comment = response.data
        # Make sure a new notification is created and correct.
        self.assertEqual(new_comment['children'], [])
        self.assertEqual(new_comment['edited'], False)
        self.assertEqual(new_comment['deleted'], False)
        self.assertEqual(new_comment['text'], 'This is a new comment')
        user.refresh_from_db()
        self.assertEqual(user.comment_set.all().count(), 1)
        notifications = Notification.objects.all()
        self.assertEqual(notifications.count(), 2)
        # Grab the new notification and verify its contents are correct.
        new_notification = notifications.exclude(id=notification.id)[0]
        self.assertEqual(new_notification.user, comment.user)
        self.assertEqual(new_notification.event.data['comments'], [new_comment['id']])
        self.assertEqual(new_notification.event.data['subcomments'], [])
        # ...And that the old one is updated with information.
        notification.event.refresh_from_db()
        self.assertEqual(notification.event.data['comments'], [comment.id])
        self.assertEqual(notification.event.data['subcomments'], [new_comment['id']])
        # Mark the new notification read to verify it gets unread when updating.
        new_notification.read = True
        new_notification.save()
        # Make one more reply with another user.
        user2 = UserFactory.create()
        self.login(user2)
        response = self.client.post(
            '/api/lib/v1/comment/{}/reply/'.format(comment.id),
            {
                'text': 'This is a final comment.',
            }
        )
        last_comment = response.data
        # Verify first comment notification is updated.
        notification.event.refresh_from_db()
        self.assertEqual(notification.event.data['comments'], [comment.id])
        self.assertEqual(notification.event.data['subcomments'], [new_comment['id'], last_comment['id']])
        # And that the top level comment is updated.
        new_notification.event.refresh_from_db()
        new_notification.refresh_from_db()
        self.assertFalse(new_notification.read)
        self.assertEqual(new_notification.event.data['comments'], [new_comment['id'], last_comment['id']])
