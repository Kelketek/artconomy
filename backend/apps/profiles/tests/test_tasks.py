from datetime import datetime

from apps.lib.test_resources import EnsurePlansMixin
from apps.lib.tests.factories_interdepend import CommentFactory
from apps.profiles.models import Conversation
from apps.profiles.tasks import clear_blank_conversations, derive_tags, mailchimp_tag
from apps.profiles.tests.factories import ConversationFactory, UserFactory
from apps.sales.mailchimp import chimp
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from django.utils import timezone
from django.utils.timezone import make_aware
from freezegun import freeze_time


class MessageClearTestCase(EnsurePlansMixin, TestCase):
    @freeze_time("2019-08-03")
    def test_clear_messages(self):
        conversation = ConversationFactory.create(
            created_on=make_aware(datetime(year=2019, month=8, day=1))
        )
        clear_blank_conversations()
        # noinspection PyTypeChecker
        self.assertRaises(Conversation.DoesNotExist, conversation.refresh_from_db)

    @freeze_time("2019-08-01")
    def test_no_clear_too_new(self):
        conversation = ConversationFactory.create(
            created_on=make_aware(datetime(year=2019, month=8, day=1))
        )
        clear_blank_conversations()
        conversation.refresh_from_db()

    @freeze_time("2019-08-03")
    def test_no_clear_has_comments(self):
        timezone.now()
        conversation = ConversationFactory.create(
            created_on=make_aware(datetime(year=2019, month=8, day=1))
        )
        CommentFactory.create(
            object_id=conversation.id,
            content_type=ContentType.objects.get_for_model(Conversation),
        )
        clear_blank_conversations()
        conversation.refresh_from_db()


class MailchimpTaskTestCase(EnsurePlansMixin, TestCase):
    def setUp(self):
        super().setUp()
        chimp.lists.members.tags.update.reset_mock()
        chimp.lists.members.update.reset_mock()

    def test_derive_tags(self):
        user = UserFactory.create(artist_mode=False)
        self.assertEqual(derive_tags(user), [{"name": "artist", "status": "inactive"}])
        user.artist_mode = True
        self.assertEqual(derive_tags(user), [{"name": "artist", "status": "active"}])

    @override_settings(MAILCHIMP_LIST_SECRET="9999")
    def test_send_useful_call(self):
        user = UserFactory.create(
            artist_mode=False, mailchimp_id="wat", email="goober@example.com"
        )
        mailchimp_tag(user.id)
        chimp.lists.members.tags.update.assert_called_with(
            list_id="9999",
            subscriber_hash="wat",
            data={"tags": [{"name": "artist", "status": "inactive"}]},
        )
        chimp.lists.members.update.assert_called_with(
            list_id="9999",
            subscriber_hash="wat",
            data={"email_address": "goober@example.com"},
        )

    @override_settings(MAILCHIMP_LIST_SECRET="9999")
    def test_skip_disqualified(self):
        guest = UserFactory.create(artist_mode=False, mailchimp_id="wat", guest=True)
        deactivated = UserFactory.create(
            artist_mode=False,
            mailchimp_id="wat",
            is_active=False,
        )
        no_entry = UserFactory.create(artist_mode=False, mailchimp_id="")
        mailchimp_tag(guest.id)
        mailchimp_tag(deactivated.id)
        mailchimp_tag(no_entry.id)
        chimp.lists.members.tags.update.assert_not_called()
        chimp.lists.members.update.assert_not_called()
