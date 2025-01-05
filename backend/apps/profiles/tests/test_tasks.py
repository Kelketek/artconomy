from datetime import datetime, date
from unittest.mock import patch

from apps.lib.abstract_models import ADULT, MATURE
from apps.lib.test_resources import EnsurePlansMixin
from apps.lib.tests.factories_interdepend import CommentFactory
from apps.profiles.models import Conversation, Submission
from apps.profiles.tasks import (
    clear_blank_conversations,
    drip_tag,
    remove_expired_submissions,
)
from apps.profiles.tests.factories import (
    ConversationFactory,
    UserFactory,
    CharacterFactory,
    SubmissionFactory,
)
from apps.sales.constants import COMPLETED
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from django.utils import timezone
from django.utils.timezone import make_aware
from freezegun import freeze_time

from apps.sales.tests.factories import DeliverableFactory, ProductFactory


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


class SubmissionRemovalTestCase(EnsurePlansMixin, TestCase):
    @freeze_time("2019-08-01")
    @override_settings(EVIDENCE_DAYS=30)
    def test_remove_only_past_cutoff(self):
        submission_stays = SubmissionFactory.create(
            removed_on=make_aware(datetime(year=2019, month=8, day=1))
        )
        submission_stays_2 = SubmissionFactory.create(
            removed_on=make_aware(datetime(year=2019, month=7, day=15))
        )
        submission_removed = SubmissionFactory.create(
            removed_on=make_aware(datetime(year=2019, month=6, day=1))
        )
        remove_expired_submissions()
        with self.assertRaises(Submission.DoesNotExist):
            submission_removed.refresh_from_db()
        submission_stays.refresh_from_db()
        submission_stays_2.refresh_from_db()


@patch("apps.profiles.tasks.drip")
@override_settings(DRIP_ACCOUNT_ID="bork")
class DripTaskTestCase(EnsurePlansMixin, TestCase):
    def test_drip_tags_basic(self, mock_drip):
        mock_drip.post.assert_not_called()
        user = UserFactory.create(
            email="bork@bork.com", username="Bork", drip_id="blargh"
        )
        with self.captureOnCommitCallbacks(execute=True):
            user.save()
        mock_drip.post.assert_called_with(
            f"/v2/bork/subscribers",
            json={
                "subscribers": [
                    {
                        "id": "blargh",
                        "email": "bork@bork.com",
                        "tags": [],
                        "first_name": "Bork",
                        "custom_fields": {},
                    }
                ]
            },
        )
        self.assertEqual(mock_drip.post.call_count, 1)
        user.artist_mode = True
        with self.captureOnCommitCallbacks(execute=True):
            user.save()
        mock_drip.post.assert_called_with(
            f"/v2/bork/subscribers",
            json={
                "subscribers": [
                    {
                        "id": "blargh",
                        "email": "bork@bork.com",
                        "tags": ["artist"],
                        "first_name": "Bork",
                        "custom_fields": {},
                    }
                ]
            },
        )

    def test_has_sold(self, mock_drip):
        user = UserFactory.create(
            email="bork@bork.com",
            username="Bork",
            drip_id="blargh",
            artist_mode=True,
        )
        DeliverableFactory(
            order__seller=user,
            status=COMPLETED,
            product__active=False,
        )
        drip_tag(user.id)
        mock_drip.post.assert_called_with(
            f"/v2/bork/subscribers",
            json={
                "subscribers": [
                    {
                        "id": "blargh",
                        "email": "bork@bork.com",
                        "tags": ["artist", "has_sold"],
                        "first_name": "Bork",
                        "custom_fields": {},
                    }
                ]
            },
        )

    def test_has_bought(self, mock_drip):
        user = UserFactory.create(
            email="bork@bork.com",
            username="Bork",
            drip_id="blargh",
        )
        DeliverableFactory(order__buyer=user, status=COMPLETED)
        drip_tag(user.id)
        mock_drip.post.assert_called_with(
            f"/v2/bork/subscribers",
            json={
                "subscribers": [
                    {
                        "id": "blargh",
                        "email": "bork@bork.com",
                        "tags": ["has_bought"],
                        "first_name": "Bork",
                        "custom_fields": {},
                    }
                ]
            },
        )

    def test_nsfw_artist(self, mock_drip):
        user = UserFactory.create(
            email="bork@bork.com",
            username="Bork",
            drip_id="blargh",
            artist_mode=True,
        )
        ProductFactory.create(user=user, max_rating=ADULT)
        drip_tag(user.id)
        mock_drip.post.assert_called_with(
            f"/v2/bork/subscribers",
            json={
                "subscribers": [
                    {
                        "id": "blargh",
                        "email": "bork@bork.com",
                        "tags": ["artist", "nsfw_artist"],
                        "first_name": "Bork",
                        "custom_fields": {},
                    }
                ]
            },
        )

    def test_clean_artist(self, mock_drip):
        user = UserFactory.create(
            email="bork@bork.com",
            username="Bork",
            drip_id="blargh",
            artist_mode=True,
        )
        ProductFactory.create(user=user, max_rating=MATURE)
        drip_tag(user.id)
        mock_drip.post.assert_called_with(
            f"/v2/bork/subscribers",
            json={
                "subscribers": [
                    {
                        "id": "blargh",
                        "email": "bork@bork.com",
                        "tags": ["artist", "clean_artist"],
                        "first_name": "Bork",
                        "custom_fields": {},
                    }
                ]
            },
        )

    def test_char_no_ref(self, mock_drip):
        user = UserFactory.create(
            email="bork@bork.com",
            username="Bork",
            drip_id="blargh",
        )
        CharacterFactory.create(
            user=user,
            primary_submission=None,
            name="Boop",
        )
        drip_tag(user.id)
        mock_drip.post.assert_called_with(
            f"/v2/bork/subscribers",
            json={
                "subscribers": [
                    {
                        "id": "blargh",
                        "email": "bork@bork.com",
                        "tags": [],
                        "first_name": "Bork",
                        "custom_fields": {
                            "character_no_ref": "Boop",
                        },
                    }
                ]
            },
        )

    def test_nsfw_viewer(self, mock_drip):
        user = UserFactory.create(
            email="bork@bork.com",
            username="Bork",
            drip_id="blargh",
            birthday=date(1988, 8, 1),
            rating=ADULT,
        )
        drip_tag(user.id)
        mock_drip.post.assert_called_with(
            f"/v2/bork/subscribers",
            json={
                "subscribers": [
                    {
                        "id": "blargh",
                        "email": "bork@bork.com",
                        "tags": ["nsfw_viewer"],
                        "first_name": "Bork",
                        "custom_fields": {},
                    }
                ]
            },
        )

    def test_char_no_ref_with_species(self, mock_drip):
        user = UserFactory.create(
            email="bork@bork.com",
            username="Bork",
            drip_id="blargh",
        )
        character = CharacterFactory.create(
            user=user,
            primary_submission=None,
            name="Boop",
        )
        character.attributes.filter(key="species").update(value="Dork")
        drip_tag(user.id)
        mock_drip.post.assert_called_with(
            f"/v2/bork/subscribers",
            json={
                "subscribers": [
                    {
                        "id": "blargh",
                        "email": "bork@bork.com",
                        "tags": [],
                        "first_name": "Bork",
                        "custom_fields": {
                            "character_no_ref": "Boop",
                            "character_no_ref_species": "Dork",
                        },
                    }
                ]
            },
        )
