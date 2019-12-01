from apps.lib.models import Comment
from apps.lib.test_resources import APITestCase, SignalsDisabledMixin
from apps.lib.tests.factories_interdepend import CommentFactory
from apps.profiles.tests.factories import JournalFactory, SubmissionFactory


class TestComment(SignalsDisabledMixin, APITestCase):
    def test_delete_comment_with_child(self):
        journal = JournalFactory.create()
        comment = CommentFactory.create(user=journal.user)
        comment.content_object = journal
        comment.save()
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
        comment = CommentFactory.create(user=journal.user)
        self.login(comment.user)
        response = self.client.delete(f'/api/lib/v1/comments/profiles.Journal/{journal.id}/{comment.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertRaises(Comment.DoesNotExist, comment.refresh_from_db)

    def test_list_comments(self):
        submission = SubmissionFactory.create()
        comment = CommentFactory.create(user=submission.owner)
        submission.comments.add(comment)
        response = self.client.get(f'/api/lib/v1/comments/profiles.Submission/{submission.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['id'], comment.id)
