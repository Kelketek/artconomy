from unittest.mock import patch

from apps.lib.models import Asset, Notification
from apps.lib.test_resources import APITestCase, EnsurePlansMixin
from apps.lib.tests.factories import AssetFactory
from apps.lib.tests.factories_interdepend import CommentFactory
from apps.lib.utils import (
    FakeRequest,
    related_iterable_from_field,
    replace_foreign_references,
)
from apps.profiles.models import User
from apps.profiles.tests.factories import SubmissionFactory, UserFactory
from apps.sales.tests.factories import ProductFactory, ReferenceFactory, RevisionFactory
from django.test import TestCase
from rest_framework import status


class TestComments(APITestCase):
    def test_comment_reply(self):
        user = UserFactory.create()
        submission = SubmissionFactory.create()
        # Start with initial comment, check notification is sent.
        comment = CommentFactory.create(content_object=submission, top=submission)
        self.assertEqual(user.comment_set.all().count(), 0)
        notifications = Notification.objects.all()
        self.assertEqual(notifications.count(), 1)
        notification = notifications[0]
        self.assertEqual(notification.user, submission.owner)
        self.assertEqual(notification.event.data["comments"], [comment.id])
        self.assertEqual(notification.event.data["subcomments"], [])
        self.assertEqual(notification.event.target, submission)
        # Create a reply to the comment
        self.login(user)
        response = self.client.post(
            "/api/lib/v1/comments/lib.Comment/{}/".format(comment.id),
            {
                "text": "This is a new comment",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_comment = response.data
        # Make sure a new notification is created and correct.
        self.assertEqual(new_comment["comments"], [])
        self.assertEqual(new_comment["edited"], False)
        self.assertEqual(new_comment["deleted"], False)
        self.assertEqual(new_comment["text"], "This is a new comment")
        user.refresh_from_db()
        self.assertEqual(user.comment_set.all().count(), 1)
        notifications = Notification.objects.all()
        self.assertEqual(notifications.count(), 2)
        # Grab the new notification and verify its contents are correct.
        new_notification = notifications.exclude(id=notification.id)[0]
        self.assertEqual(new_notification.user, comment.user)
        self.assertEqual(new_notification.event.data["comments"], [new_comment["id"]])
        self.assertEqual(new_notification.event.data["subcomments"], [])
        # ...And that the old one is updated with information.
        notification.event.refresh_from_db()
        self.assertEqual(notification.event.data["comments"], [comment.id])
        self.assertEqual(notification.event.data["subcomments"], [new_comment["id"]])
        # Mark the new notification read to verify it gets unread when updating.
        new_notification.read = True
        new_notification.save()
        # Make one more reply with another user.
        user2 = UserFactory.create()
        self.login(user2)
        response = self.client.post(
            "/api/lib/v1/comments/lib.Comment/{}/".format(comment.id),
            {
                "text": "This is a final comment.",
            },
        )
        last_comment = response.data
        # Verify first comment notification is updated.
        notification.event.refresh_from_db()
        self.assertEqual(notification.event.data["comments"], [comment.id])
        self.assertEqual(
            notification.event.data["subcomments"],
            [new_comment["id"], last_comment["id"]],
        )
        # And that the top level comment is updated.
        new_notification.event.refresh_from_db()
        new_notification.refresh_from_db()
        self.assertFalse(new_notification.read)
        self.assertEqual(
            new_notification.event.data["comments"],
            [new_comment["id"], last_comment["id"]],
        )


class TestAsset(EnsurePlansMixin, TestCase):
    def test_can_reference_uploaded(self):
        asset = AssetFactory.create(uploaded_by=UserFactory.create())
        self.assertTrue(asset.can_reference(FakeRequest(asset.uploaded_by)))

    def test_can_reference_outsider_no_usage_no_uploader(self):
        asset = AssetFactory.create()
        self.assertFalse(asset.can_reference(FakeRequest(UserFactory.create())))

    def test_can_reference_outsider_no_usage(self):
        asset = AssetFactory.create(uploaded_by=UserFactory.create())
        self.assertFalse(asset.can_reference(FakeRequest(UserFactory.create())))

    def test_can_reference_character_tagged(self):
        asset = AssetFactory.create(uploaded_by=UserFactory.create())
        submission = SubmissionFactory.create(file=asset)
        self.assertTrue(asset.can_reference(FakeRequest(submission.owner)))

    # If CELERY_ALWAYS_EAGER is enabled, the cleanup function is skipped, because it would
    # immediately delete any asset uploaded before you can use it. For this test case, we can't
    # just override settings. We have to patch the settings object to keep CELERY_ALWAYS_EAGER true
    # while reporting it false for the function tested.
    @patch("apps.lib.tasks.settings")
    def test_cleanup(self, mock_settings):
        mock_settings.CELERY_ALWAYS_EAGER = False
        asset = AssetFactory.create()
        # Should already be deleted.
        with self.assertRaises(Asset.DoesNotExist):
            asset.refresh_from_db()


class Test(EnsurePlansMixin, TestCase):
    def test_related_iterable_from_field(self):
        user = UserFactory.create()
        related_values = list(related_iterable_from_field(user, User.artist_profile))
        self.assertIn(user.artist_profile, related_values)
        self.assertEqual(len(related_values), 1)

    def test_replace_references(self):
        asset = AssetFactory.create()
        revision = RevisionFactory.create(file=asset)
        submission = SubmissionFactory.create(file=asset)
        reference = ReferenceFactory.create(file=asset)
        unrelated_revision = RevisionFactory.create()
        unrelated_submission = RevisionFactory.create()
        unrelated_reference = ReferenceFactory.create()
        new_asset = AssetFactory.create()
        replace_foreign_references(asset, new_asset)
        revision.refresh_from_db()
        submission.refresh_from_db()
        reference.refresh_from_db()
        unrelated_submission.refresh_from_db()
        self.assertEqual(submission.file, new_asset)
        self.assertEqual(revision.file, new_asset)
        self.assertEqual(reference.file, new_asset)
        self.assertNotEqual(unrelated_revision.file, new_asset)
        self.assertNotEqual(unrelated_revision.file, new_asset)
        self.assertNotEqual(unrelated_reference.file, new_asset)
        asset.refresh_from_db()
