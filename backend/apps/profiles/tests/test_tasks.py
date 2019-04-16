from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import make_aware
from freezegun import freeze_time

from apps.lib.test_resources import SignalsDisabledMixin
from apps.lib.tests.factories_interdepend import CommentFactory
from apps.profiles.models import Conversation
from apps.profiles.tasks import clear_blank_conversations
from apps.profiles.tests.factories import ConversationFactory


class MessageClearTestCase(SignalsDisabledMixin, TestCase):
    @freeze_time('2019-08-03')
    def test_clear_messages(self):
        conversation = ConversationFactory.create(created_on=make_aware(datetime(year=2019, month=8, day=1)))
        clear_blank_conversations()
        # noinspection PyTypeChecker
        self.assertRaises(Conversation.DoesNotExist, conversation.refresh_from_db)

    @freeze_time('2019-08-01')
    def test_no_clear_too_new(self):
        conversation = ConversationFactory.create(created_on=make_aware(datetime(year=2019, month=8, day=1)))
        clear_blank_conversations()
        conversation.refresh_from_db()

    @freeze_time('2019-08-03')
    def test_no_clear_has_comments(self):
        timezone.now()
        conversation = ConversationFactory.create(created_on=make_aware(datetime(year=2019, month=8, day=1)))
        CommentFactory.create(object_id=conversation.id, content_type=ContentType.objects.get_for_model(Conversation))
        clear_blank_conversations()
        conversation.refresh_from_db()
