from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile

from apps.lib.models import Comment
from apps.lib.test_resources import APITestCase
from apps.lib.tests.factories_interdepend import CommentFactory
from apps.profiles.tests.factories import JournalFactory, SubmissionFactory, UserFactory


class TestComment(APITestCase):
    def test_delete_comment_with_child(self):
        journal = JournalFactory.create()
        comment = CommentFactory.create(user=journal.user, content_object=journal, top=journal)
        subcomment = CommentFactory.create()
        subcomment.content_object = comment
        subcomment.save()
        self.login(comment.user)
        response = self.client.delete(f'/api/lib/v1/comments/profiles.Journal/{journal.id}/{comment.id}/')
        self.assertEqual(response.data['text'], '')
        self.assertIsNone(response.data['user'])
        self.assertFalse(response.data['edited'])
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertTrue(comment.deleted)

    def test_delete_comment(self):
        journal = JournalFactory.create()
        comment = CommentFactory.create(user=journal.user, content_object=journal, top=journal)
        self.login(comment.user)
        response = self.client.delete(f'/api/lib/v1/comments/profiles.Journal/{journal.id}/{comment.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertRaises(Comment.DoesNotExist, comment.refresh_from_db)

    def test_list_comments(self):
        submission = SubmissionFactory.create()
        comment = CommentFactory.create(user=submission.owner, content_object=submission, top=submission)
        submission.comments.add(comment)
        response = self.client.get(f'/api/lib/v1/comments/profiles.Submission/{submission.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['id'], comment.id)


class TestSupportRequest(APITestCase):
    def test_send_request(self):
        self.client.post('/api/lib/v1/support/request/', {
            'email': 'test@example.com',
            'body': 'beep boop.',
            'referring_url': 'https://example.com/',
        })


class TestAssetUpload(APITestCase):
    @patch('apps.lib.views.cache')
    def test_upload_asset_no_login(self, mock_cache):
        # Force a cookie to get set.
        self.assertTrue(self.client.session)
        self.upload_asset(mock_cache)

    def upload_asset(self, mock_cache):
        file = SimpleUploadedFile("file.mp4", b"file_content", content_type="video/mp4")
        response = self.client.post('/api/lib/v1/asset/', {'files[]': file}, format='multipart')
        self.assertEqual(response.status_code, 200)
        mock_cache.set.assert_called_with(
            f'upload_grant_{self.client.session.session_key}-to-{response.data["id"]}', True, timeout=3600,
        )

    @patch('apps.lib.views.cache')
    def test_upload_asset_logged_in(self, mock_cache):
        user = UserFactory.create()
        self.login(user)
        self.upload_asset(mock_cache)
