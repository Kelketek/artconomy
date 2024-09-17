from unittest.mock import Mock

import apps.lib.constants
from apps.lib.models import Event, Subscription
from apps.lib.constants import COMMENT, DISPUTE
from apps.lib.test_resources import EnsurePlansMixin
from apps.lib.tests.test_utils import create_staffer
from apps.profiles.models import Character
from apps.profiles.tests.factories import (
    ConversationFactory,
    SubmissionFactory,
    UserFactory,
)
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import TestCase

expected_subscriptions = (
    (apps.lib.constants.SUBMISSION_SHARED, False),
    (apps.lib.constants.CHAR_SHARED, False),
    (apps.lib.constants.RENEWAL_FAILURE, True),
    (apps.lib.constants.SUBSCRIPTION_DEACTIVATED, True),
    (apps.lib.constants.RENEWAL_FIXED, True),
    (apps.lib.constants.TRANSFER_FAILED, True),
    (apps.lib.constants.REFERRAL_LANDSCAPE_CREDIT, True),
    (apps.lib.constants.WAITLIST_UPDATED, True),
    (apps.lib.constants.AUTO_CLOSED, True),
)


class SubscriptionsTestCase(EnsurePlansMixin, TestCase):
    def test_subscriptions_created_user(self):
        user = UserFactory.create()
        user_type = ContentType.objects.get_for_model(user)
        subscriptions = (
            Subscription.objects.filter(subscriber=user)
            .order_by("id")
            .values_list("type", "content_type_id", "object_id", "email")
        )
        checks = [
            (event_type, user_type.id, user.id, email)
            for event_type, email in expected_subscriptions
        ]
        checks.insert(0, (apps.lib.constants.SYSTEM_ANNOUNCEMENT, None, None, False))
        self.assertEqual(list(subscriptions), checks)

    def test_subscriptions_created_staff_disputes(self):
        user = create_staffer("handle_disputes")
        # 2: System announcement, New Dispute
        self.assertEqual(
            Subscription.objects.filter(subscriber=user).count(),
            len(expected_subscriptions) + 2,
        )
        self.assertTrue(
            Subscription.objects.filter(
                subscriber=user,
                type=DISPUTE,
                content_type_id=None,
                object_id=None,
            ).exists()
        )

    def test_subscriptions_created_staff_refunds(self):
        user = create_staffer("view_financials")
        # 2: System announcement, New Dispute
        self.assertEqual(
            Subscription.objects.filter(subscriber=user).count(),
            len(expected_subscriptions) + 2,
        )
        self.assertTrue(
            Subscription.objects.filter(
                subscriber=user,
                type=apps.lib.constants.REFUND,
                content_type_id=None,
                object_id=None,
            ).exists()
        )

    def test_subscriptions_created_superuser(self):
        user = UserFactory.create(is_staff=True, is_superuser=True)
        # 2: System announcement, New Dispute
        self.assertEqual(
            Subscription.objects.filter(subscriber=user).count(),
            len(expected_subscriptions) + 3,
        )
        self.assertTrue(
            Subscription.objects.filter(
                subscriber=user,
                type=apps.lib.constants.REFUND,
                content_type_id=None,
                object_id=None,
            ).exists()
        )


class TestSubmissionSerializer(EnsurePlansMixin, TestCase):
    def test_submission_serialization(self):
        submission = SubmissionFactory.create()
        request = Mock()
        request.user = submission.owner
        result = submission.notification_serialize({"request": request})
        self.assertEqual(result["id"], submission.id)


class TestCharacter(EnsurePlansMixin, TestCase):
    def test_character_name(self):
        user = UserFactory.create()
        character = Character(name=".stuff", user=user)
        self.assertRaises(ValidationError, character.full_clean)
        character.name = "stuff."
        self.assertRaises(ValidationError, character.full_clean)
        character.name = "thing?thing"
        self.assertRaises(ValidationError, character.full_clean)
        character.name = "wat"
        character.full_clean()


class TestConversation(EnsurePlansMixin, TestCase):
    def test_comment_removal(self):
        conversation = ConversationFactory.create()
        Event.objects.create(type=COMMENT, target=conversation, data={})
        self.assertTrue(Event.objects.filter(type=COMMENT).exists())
        conversation.delete()
        self.assertFalse(Event.objects.filter(type=COMMENT).exists())
