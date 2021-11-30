from unittest.mock import Mock

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.lib import models
from apps.lib.models import Subscription
from apps.profiles.models import Character
from apps.profiles.tests.factories import UserFactory, SubmissionFactory


expected_subscriptions = (
    (models.SUBMISSION_SHARED, False), (models.CHAR_SHARED, False), (models.RENEWAL_FAILURE, True),
    (models.SUBSCRIPTION_DEACTIVATED, True), (models.RENEWAL_FIXED, True),
    (models.TRANSFER_FAILED, True), (models.REFERRAL_LANDSCAPE_CREDIT, True),
    (models.WAITLIST_UPDATED, True),
)


class SubscriptionsTestCase(TestCase):
    def test_subscriptions_created_user(self):
        user = UserFactory.create()
        user_type = ContentType.objects.get_for_model(user)
        subscriptions = Subscription.objects.filter(
            subscriber=user
        ).order_by('id').values_list('type', 'content_type_id', 'object_id', 'email')
        checks = [(event_type, user_type.id, user.id, email) for event_type, email in expected_subscriptions]
        checks.insert(0, (models.SYSTEM_ANNOUNCEMENT, None, None, False))
        self.assertEqual(list(subscriptions), checks)

    def test_subscriptions_created_staff(self):
        user = UserFactory.create(is_staff=True)
        # 2: System announcement, New Dispute
        self.assertEqual(Subscription.objects.filter(subscriber=user).count(), len(expected_subscriptions) + 2)
        self.assertTrue(Subscription.objects.filter(
            subscriber=user, type=models.DISPUTE, content_type_id=None, object_id=None,
        ).exists())

    def test_subscriptions_created_superuser(self):
        user = UserFactory.create(is_staff=True, is_superuser=True)
        # 2: System announcement, New Dispute
        self.assertEqual(Subscription.objects.filter(subscriber=user).count(), len(expected_subscriptions) + 3)
        self.assertTrue(Subscription.objects.filter(
            subscriber=user, type=models.REFUND, content_type_id=None, object_id=None,
        ).exists())


class TestSubmissionSerializer(TestCase):
    def test_submission_serialization(self):
        submission = SubmissionFactory.create()
        request = Mock()
        request.user = submission.owner
        result = submission.notification_serialize({'request': request})
        self.assertEqual(result['id'], submission.id)


class TestCharacter(TestCase):
    def test_character_name(self):
        user = UserFactory.create()
        character = Character(name='.stuff', user=user)
        self.assertRaises(ValidationError, character.full_clean)
        character.name = 'stuff.'
        self.assertRaises(ValidationError, character.full_clean)
        character.name = 'thing?thing'
        self.assertRaises(ValidationError, character.full_clean)
        character.name = 'wat'
        character.full_clean()
