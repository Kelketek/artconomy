from django.test import override_settings
from django.utils import timezone
from unittest.mock import patch

from apps.lib.constants import ILLEGAL_CONTENT
from apps.lib.models import Comment, Asset
from apps.lib.test_resources import APITestCase
from apps.lib.tests.factories_interdepend import CommentFactory
from apps.lib.tests.test_utils import create_staffer
from apps.profiles.tests.factories import JournalFactory, SubmissionFactory, UserFactory
from django.core.files.uploadedfile import SimpleUploadedFile


class TestComment(APITestCase):
    def test_delete_comment_with_child(self):
        journal = JournalFactory.create()
        comment = CommentFactory.create(
            user=journal.user, content_object=journal, top=journal
        )
        subcomment = CommentFactory.create()
        subcomment.content_object = comment
        subcomment.save()
        self.login(comment.user)
        response = self.client.delete(
            f"/api/lib/v1/comments/profiles.Journal/{journal.id}/{comment.id}/"
        )
        self.assertEqual(response.data["text"], "")
        self.assertIsNone(response.data["user"])
        self.assertFalse(response.data["edited"])
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertTrue(comment.deleted)

    def test_delete_comment(self):
        journal = JournalFactory.create()
        comment = CommentFactory.create(
            user=journal.user, content_object=journal, top=journal
        )
        self.login(comment.user)
        response = self.client.delete(
            f"/api/lib/v1/comments/profiles.Journal/{journal.id}/{comment.id}/"
        )
        self.assertEqual(response.status_code, 204)
        self.assertRaises(Comment.DoesNotExist, comment.refresh_from_db)

    def test_delete_comment_staff(self):
        journal = JournalFactory.create()
        comment = CommentFactory.create(
            user=journal.user, content_object=journal, top=journal
        )
        self.login(create_staffer("moderate_discussion"))
        response = self.client.delete(
            f"/api/lib/v1/comments/profiles.Journal/{journal.id}/{comment.id}/"
        )
        self.assertEqual(response.status_code, 204)
        self.assertRaises(Comment.DoesNotExist, comment.refresh_from_db)

    def test_list_comments(self):
        submission = SubmissionFactory.create()
        comment = CommentFactory.create(
            user=submission.owner, content_object=submission, top=submission
        )
        submission.comments.add(comment)
        response = self.client.get(
            f"/api/lib/v1/comments/profiles.Submission/{submission.id}/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["id"], comment.id)


class TestSupportRequest(APITestCase):
    def test_send_request(self):
        self.client.post(
            "/api/lib/v1/support/request/",
            {
                "email": "test@example.com",
                "body": "beep boop.",
                "referring_url": "https://example.com/",
            },
            format="json",
        )


class TestAssetUpload(APITestCase):
    @patch("apps.lib.views.cache")
    def test_upload_asset_no_login(self, mock_cache):
        # Force a cookie to get set.
        self.assertTrue(self.client.session)
        self.upload_asset(mock_cache)

    def do_upload(self):
        file = SimpleUploadedFile("file.mp4", b"file_content", content_type="video/mp4")
        response = self.client.post(
            "/api/lib/v1/asset/", {"files[]": file}, format="multipart"
        )
        return response

    def upload_asset(self, mock_cache):
        response = self.do_upload()
        self.assertEqual(response.status_code, 201)
        mock_cache.set.assert_called_with(
            f"upload_grant_{self.client.session.session_key}-to-{response.data['id']}",
            True,
            timeout=3600,
        )

    @patch("apps.lib.views.cache")
    @override_settings(DEDUPLICATE_ASSETS=True)
    def test_deduplicated_assets(self, mock_cache):
        # Force a cookie to get set.
        self.assertTrue(self.client.session)
        self.upload_asset(mock_cache)
        self.upload_asset(mock_cache)
        self.assertEqual(Asset.objects.all().count(), 1)

    @patch("apps.lib.views.cache")
    @override_settings(DEDUPLICATE_ASSETS=True)
    def test_upload_asset_redacted(self, mock_cache):
        # Force a cookie to get set.
        self.assertTrue(self.client.session)
        self.upload_asset(mock_cache)
        asset = Asset.objects.get()
        asset.redacted_on = timezone.now()
        asset.redacted_reason = ILLEGAL_CONTENT
        asset.save()
        response = self.do_upload()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["files[]"][0],
            "Detected non-permitted file. Reason: Illegal Content",
        )

    @patch("apps.lib.views.cache")
    def test_upload_asset_logged_in(self, mock_cache):
        user = UserFactory.create()
        self.login(user)
        self.upload_asset(mock_cache)
