import logging
from unittest.mock import patch
from uuid import UUID

from dateutil.relativedelta import relativedelta
from ddt import ddt, data, unpack
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from hitcount.models import HitCount, Hit
from rest_framework import status

from apps.lib.models import (
    Subscription, COMMENT, Notification, SUBMISSION_SHARED, CHAR_SHARED,
    NEW_PRODUCT, NEW_CHARACTER, Tag,
)
from apps.lib.tests.factories import AssetFactory
from apps.lib.tests.factories_interdepend import CommentFactory
from apps.lib.tests.test_utils import EnsurePlansMixin
from apps.lib.utils import watch_subscriptions
from apps.profiles.models import Character, Submission, Conversation, User, ConversationParticipant
from apps.lib.abstract_models import MATURE, ADULT, GENERAL, EXTREME
from apps.lib.test_resources import APITestCase, SignalsDisabledMixin, PermissionsTestCase, MethodAccessMixin
from apps.profiles.tests.factories import (
    UserFactory, CharacterFactory, SubmissionFactory,
    ConversationParticipantFactory, TOTPDeviceFactory,
    AttributeFactory)
from apps.profiles.tests.helpers import gen_characters
from apps.profiles.views import ArtistProfileSettings
from apps.sales.tests.factories import PromoFactory

logger = logging.getLogger(__name__)


class TestCharacterAPICase(SignalsDisabledMixin, APITestCase):
    def test_character_listing(self):
        user = UserFactory.create()
        characters = gen_characters(user)
        response = self.client.get('/api/profiles/v1/account/{}/characters/'.format(user.username))
        self.assertEqual(len(response.data['results']), 5)
        for key, value in characters.items():
            self.assertIDInList(
                key,
                response.data['results']
            )

    def test_no_list_private(self):
        user = UserFactory.create()
        characters = gen_characters(user)
        private_character = list(characters.keys())[0]
        private_character.private = True
        private_character.save()

        # Should fail for unregistered user
        response = self.client.get('/api/profiles/v1/account/{}/characters/'.format(user.username))
        self.assertEqual(len(response.data['results']), 4)
        self.assertNotIn(private_character.id, [result['id'] for result in response.data['results']])

        # Should fail for unprivileged user
        user2 = UserFactory.create()
        self.login(user2)
        self.assertEqual(len(response.data['results']), 4)
        self.assertNotIn(private_character.id, [result['id'] for result in response.data['results']])

    def test_list_private_for_privileged(self):
        user = UserFactory.create()
        characters = gen_characters(user)
        private_character = list(characters.keys())[0]
        private_character.private = True
        private_character.save()

        # Should work for character owner.
        self.login(user)
        response = self.client.get('/api/profiles/v1/account/{}/characters/'.format(user.username))
        self.assertEqual(len(response.data['results']), 5)
        self.assertIDInList(private_character, response.data['results'])
        # Should work for staff, too.
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        response = self.client.get('/api/profiles/v1/account/{}/characters/'.format(user.username))
        self.assertEqual(len(response.data['results']), 5)
        self.assertIDInList(private_character, response.data['results'])

    def test_new_character(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        watch_subscriptions(user2, user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/'.format(user.username), {
                'name': 'Fern',
                'description': 'The best of both worlds',
                'private': False,
                'open_requests': False,
                'open_requests_restrictions': 'Must be foxy.',
            }, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        char = Character.objects.get(name='Fern')
        self.assertEqual(char.description, 'The best of both worlds')
        self.assertEqual(char.open_requests_restrictions, 'Must be foxy.')
        self.assertEqual(char.taggable, True)

        # Should work for staffer.
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/'.format(user.username), {
                'name': 'Rain',
                'description': 'Heart breaker',
                'private': True,
                'open_requests': False,
                'open_requests_restrictions': 'Must be really foxy.',
                'taggable': False,
            }, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        char2 = Character.objects.get(name='Rain')
        self.assertEqual(char2.user, user)
        self.assertEqual(char2.description, 'Heart breaker')
        self.assertEqual(char2.private, True)
        self.assertEqual(char2.open_requests, False)
        self.assertEqual(char2.taggable, False)
        self.assertEqual(char2.open_requests_restrictions, 'Must be really foxy.')

    def test_edit_character(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        watch_subscriptions(user2, user)
        char = CharacterFactory.create(user=user)
        response = self.client.patch(
            '/api/profiles/v1/account/{}/characters/{}/'.format(user.username, char.name),
            {
                'name': 'Terrence',
                'description': 'Positively foxy.',
                'private': True
            }, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        char.refresh_from_db()
        self.assertEqual(char.name, 'Terrence')
        self.assertEqual(char.description, 'Positively foxy.')

        # Should work for staff, too.
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        response = self.client.patch(
            '/api/profiles/v1/account/{}/characters/{}/'.format(user.username, char.name),
            {
                'name': 'Rain',
                'description': 'Supremely foxy.'
            }, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        char.refresh_from_db()
        self.assertEqual(char.name, 'Rain')
        self.assertEqual(char.description, 'Supremely foxy.')

    def test_edit_character_other(self):
        char = CharacterFactory.create(name='Fern', description='Supremely Foxy')
        user = char.user
        user2 = UserFactory.create()
        self.login(user2)
        response = self.client.patch(
            '/api/profiles/v1/account/{}/characters/{}/'.format(user.username, char.name),
            {
                'name': 'Terrence',
                'description': 'Positively foxy.',
                'tags': ['new', 'set']
            }, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Fern')
        self.assertEqual(response.data['description'], 'Supremely Foxy')
        self.assertEqual(sorted(response.data['tags']), ['new', 'set'])

    def test_delete_character(self):
        char = CharacterFactory.create()
        user = char.user
        self.login(user)
        response = self.client.delete(
            '/api/profiles/v1/account/{}/characters/{}/'.format(user.username, char.name)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRaises(ObjectDoesNotExist, char.refresh_from_db)

        # Test for staff.
        char = CharacterFactory.create(user=user)

        response = self.client.delete(
            '/api/profiles/v1/account/{}/characters/{}/'.format(user.username, char.name)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRaises(ObjectDoesNotExist, char.refresh_from_db)


class TestSubmission(APITestCase):
    def test_submission_edit(self):
        char = CharacterFactory.create()
        user = char.user
        submission = SubmissionFactory.create(owner=user)
        self.login(user)
        submission.characters.add(char)
        response = self.client.patch(
            '/api/profiles/v1/submission/{}/'.format(submission.id),
            {
                'title': 'Porn',
                'caption': 'Shameless porn.',
                'private': True,
                'rating': MATURE,  # Bad user. You should know better!
            }, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        submission.refresh_from_db()
        self.assertEqual(submission.title, 'Porn')
        self.assertEqual(submission.caption, 'Shameless porn.')
        self.assertEqual(submission.private, True)
        self.assertEqual(submission.rating, MATURE)

        # Should work for staffer, too.
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        response = self.client.patch(
            '/api/profiles/v1/submission/{}/'.format(submission.id),
            {
                'title': 'Smut',
                'caption': 'Use the proper rating!',
                'private': False,
                'rating': ADULT,  # That's better.
            }, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        submission.refresh_from_db()
        self.assertEqual(submission.title, 'Smut')
        self.assertEqual(submission.caption, 'Use the proper rating!')
        self.assertEqual(submission.private, False)
        self.assertEqual(submission.rating, ADULT)

    def test_submission_edit_forbidden(self):
        user2 = UserFactory.create()
        self.login(user2)
        submission = SubmissionFactory.create(
            title='Stuff',
            caption='Things',
            rating=GENERAL,
            private=False,
        )
        response = self.client.patch(
            '/api/profiles/v1/submission/{}/'.format(submission.id),
            {
                'title': 'Porn',
                'caption': 'Shameless porn.',
                'private': True,
                'rating': MATURE,  # Bad user. You should know better!
            }, format='json',
        )
        # User can patch, but not anything specific to the piece, only their subscription to messages or
        # favorites.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Stuff')
        self.assertEqual(response.data['caption'], 'Things')
        self.assertEqual(response.data['private'], False)
        self.assertEqual(response.data['rating'], GENERAL)

    def test_submission_hidden(self):
        user2 = UserFactory.create()
        self.login(user2)
        submission = SubmissionFactory.create(
            title='Stuff',
            caption='Things',
            rating=GENERAL,
            private=True,
        )
        response = self.client.get(f'/api/profiles/v1/submission/{submission.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_submission_destroy(self):
        user = UserFactory.create()
        self.login(user)
        submission = SubmissionFactory.create(
            owner=user,
            title='Stuff',
            caption='Things',
            rating=GENERAL,
            private=False,
        )
        response = self.client.delete(
            f'/api/profiles/v1/submission/{submission.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_submission_destroy_denied(self):
        user = UserFactory.create()
        self.login(user)
        submission = SubmissionFactory.create(
            title='Stuff',
            caption='Things',
            rating=GENERAL,
            private=False,
        )
        response = self.client.delete(
            f'/api/profiles/v1/submission/{submission.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_submission_ip4_hitcount(self):
        user = UserFactory.create()
        self.login(user)
        submission = SubmissionFactory.create(
            title='Stuff',
            caption='Things',
            rating=GENERAL,
            private=False,
        )

        self.client.credentials(REMOTE_ADDR='34.56.73.23')
        response = self.client.get(
            f'/api/profiles/v1/submission/{submission.id}/?view=true',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        count = HitCount.objects.get(
            object_pk=submission.id, content_type=ContentType.objects.get_for_model(Submission),
        )
        self.assertEqual(count.hits, 1)
        hits = Hit.objects.all()
        self.assertEqual(hits.count(), 1)
        hit = hits[0]
        self.assertEqual(hit.ip, '34.56.73.23')

    def test_submission_ip6_hitcount(self):
        user = UserFactory.create()
        self.login(user)
        submission = SubmissionFactory.create(
            title='Stuff',
            caption='Things',
            rating=GENERAL,
            private=False,
        )

        self.client.credentials(REMOTE_ADDR='2001:0db8:85a3:0000:0000:8a2e:0370:7334')
        response = self.client.get(
            f'/api/profiles/v1/submission/{submission.id}/?view=true',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        count = HitCount.objects.get(
            object_pk=submission.id, content_type=ContentType.objects.get_for_model(Submission),
        )
        self.assertEqual(count.hits, 1)
        hits = Hit.objects.all()
        self.assertEqual(hits.count(), 1)
        hit = hits[0]
        self.assertEqual(hit.ip, '2001:0db8:85a3:0000:0000:8a2e:0370:7334')

    def test_create_submission(self):
        user = UserFactory.create()
        self.login(user)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            f'/api/profiles/v1/account/{user.username}/submissions/', {
                'title': 'This is a test',
                'rating': MATURE,
                'file': str(asset.id),
            }, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'This is a test')
        self.assertEqual(response.data['rating'], MATURE)
        self.assertTrue(response.data['file'])

    def test_create_submission_no_artist_clobber(self):
        user = UserFactory.create()
        self.login(user)
        asset = AssetFactory.create(uploaded_by=user)
        artist = UserFactory.create()
        artist2 = UserFactory.create()
        unrelated_submission = SubmissionFactory.create()
        unrelated_submission.artists.set([artist, artist2])
        response = self.client.post(
            f'/api/profiles/v1/account/{user.username}/submissions/', {
                'title': 'This is a test',
                'rating': MATURE,
                'file': str(asset.id),
                'artists': [artist.id],
            }, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        submission = Submission.objects.get(id=response.data['id'])
        self.assertEqual(submission.artists.all().first(), artist)
        self.assertCountEqual(list(unrelated_submission.artists.all()), [artist, artist2])
        self.assertEqual(response.data['title'], 'This is a test')
        self.assertEqual(response.data['rating'], MATURE)
        self.assertTrue(response.data['file'])

    def test_create_submission_file_blank(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            f'/api/profiles/v1/account/{user.username}/submissions/', {
                'title': 'This is a test',
                'rating': MATURE,
                'file': '',
            }, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_submission_file_null(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            f'/api/profiles/v1/account/{user.username}/submissions/', {
                'title': 'This is a test',
                'rating': MATURE,
                'file': None,
            }, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_submission_file_missing(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            f'/api/profiles/v1/account/{user.username}/submissions/', {
                'title': 'This is a test',
                'rating': MATURE,
            }, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestSettings(APITestCase):
    def test_settings_post(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.patch(
            '/api/profiles/v1/account/{}/'.format(user.username), {
                'birthday': '1988-08-01',
                'rating': ADULT,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], ADULT)
        self.assertEqual(response.data['birthday'], '1988-08-01')
        user.refresh_from_db()
        self.assertEqual(user.rating, ADULT)

    def test_credentials_post_username(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/auth/credentials/'.format(user.username),
            {'username': 'NewName', 'current_password': 'Test'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.username, 'NewName')

    def test_credentials_username_taken(self):
        user = UserFactory.create()
        self.login(user)
        conflicting = UserFactory.create()
        response = self.client.post(
            '/api/profiles/v1/account/{}/auth/credentials/'.format(user.username),
            {'username': conflicting.username, 'current_password': 'Test'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        old_name = user.username
        user.refresh_from_db()
        self.assertNotEqual(user.username, conflicting.username)
        self.assertEqual(user.username, old_name)

    def test_credentials_email_change(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/auth/credentials/'.format(user.username),
            {'current_password': 'Test', 'email': 'changed_email@example.com'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.email, 'changed_email@example.com')

    def test_credentials_email_taken(self):
        user = UserFactory.create()
        self.login(user)
        conflicting = UserFactory.create()
        response = self.client.post(
            '/api/profiles/v1/account/{}/auth/credentials/'.format(user.username),
            {'current_password': 'Test', 'email': conflicting.email}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        old_email = user.email
        user.refresh_from_db()
        self.assertNotEqual(user.email, conflicting.email)
        self.assertEqual(user.email, old_email)

    def test_credentials_username_no_password(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/auth/credentials/'.format(user.username),
            {'username': 'NewName'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        old_name = user.username
        user.refresh_from_db()
        self.assertEqual(old_name, user.username)

    def test_credentials_username_wrong_password(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/auth/credentials/'.format(user.username),
            {'username': 'NewName', 'current_password': 'password'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        old_name = user.username
        user.refresh_from_db()
        self.assertEqual(old_name, user.username)

    def test_credentials_change_password(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/auth/credentials/'.format(user.username),
            {
                'current_password': 'Test',
                'new_password': '1234TestABC',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertFalse(user.check_password('Test'))
        self.assertTrue(user.check_password('1234TestABC'))

    def test_credentials_wrong_password(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/auth/credentials/'.format(user.username),
            {
                'current_password': 'password',
                'new_password': '1234TestABC',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertFalse(user.check_password('1234'))
        self.assertTrue(user.check_password('Test'))

    def test_set_biography(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.patch(
            '/api/profiles/v1/account/{}/'.format(user.username),
            {
                'biography': 'test'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['biography'], 'test')

    def test_wrong_user(self):
        user = UserFactory.create(biography='I am a cool person')
        user2 = UserFactory.create()
        self.login(user2)
        response = self.client.patch(
            '/api/profiles/v1/account/{}/'.format(user.username),
            {
                'biography': 'I am not cool'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['biography'], 'I am a cool person')

    def test_guest_user(self):
        user = UserFactory.create(biography='I am a cool person')
        user2 = UserFactory.create(guest=True, username='__5', email='test@localhost', guest_email='test@example.com')
        self.login(user2)
        response = self.client.patch(
            '/api/profiles/v1/account/{}/'.format(user.username),
            {
                'biography': 'I am not cool'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_guest_user_self(self):
        user = UserFactory.create(
            biography='I am a cool person',
            guest=True,
            username='__5',
            email='test@localhost',
            guest_email='test@example.com',
        )
        self.login(user)
        response = self.client.patch(
            '/api/profiles/v1/account/{}/'.format(user.username),
            {
                'biography': 'I am not cool'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['biography'], 'I am a cool person')


class TestArtistProfilePermissions(MethodAccessMixin, PermissionsTestCase):
    passes = {
        **MethodAccessMixin.passes,
        'get': ['user', 'staff', 'outsider', 'anonymous'], 'patch': ['user', 'staff'],
        'put': ['user', 'staff'],
    }
    view_class = ArtistProfileSettings


class TestSetBiography(APITestCase):
    def test_set_biography(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.patch(
            '/api/profiles/v1/account/{}/'.format(user.username),
            {
                'biography': 'test'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['biography'], 'test')


class ValidatorChecks(APITestCase):
    def test_username_validator_taken(self):
        UserFactory.create(username='testola')
        response = self.client.post('/api/profiles/v1/form-validators/username/', {'username': 'testola'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['username'], ['A user with that username already exists.'])

    def test_username_validator_bad_request(self):
        response = self.client.post('/api/profiles/v1/form-validators/username/', format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['username'], ['This field is required.'])

    def test_username_validator_available(self):
        response = self.client.post('/api/profiles/v1/form-validators/username/', {'username': 'stuff'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TestSubmissionSearch(APITestCase):
    def test_submission_rating_search(self):
        artist = UserFactory.create()
        Tag.objects.create(name='stuff')
        SubmissionFactory.create(rating=GENERAL, owner=artist).tags.add('stuff')
        submission_risque = SubmissionFactory.create(rating=MATURE, owner=artist)
        submission_risque.tags.add('stuff')
        SubmissionFactory.create(rating=ADULT, title='Stuff', owner=artist).tags.add('stuff')
        submission_extreme = SubmissionFactory.create(rating=EXTREME, title='Stuff', owner=artist)
        submission_extreme.tags.add('stuff')
        self.login(user=UserFactory.create(rating=EXTREME))
        response = self.client.get('/api/profiles/v1/search/submission/?q=stuff&content_ratings=1,3')
        self.assertEqual(len(response.data['results']), 2)
        self.assertIDInList(submission_risque, response.data['results'])
        self.assertIDInList(submission_extreme, response.data['results'])


class TestCharacterSearch(APITestCase):
    def test_query_not_logged_in(self):
        char = CharacterFactory.create(name='Terrybutt')
        char2 = CharacterFactory.create(name='Terrencia', open_requests=False)
        CharacterFactory.create(name='Terrence', private=True)
        CharacterFactory.create(name='wutwut')
        CharacterFactory.create(name='Stuff')
        CharacterFactory.create(name='Terrifying', taggable=False)
        response = self.client.get('/api/profiles/v1/search/character/?q=terr&tagging=true')
        self.assertEqual(len(response.data['results']), 2)
        self.assertIDInList(char, response.data['results'])
        self.assertIDInList(char2, response.data['results'])

    def test_query_logged_in(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        visible = CharacterFactory.create(name='Terrybutt', user=user)
        visible2 = CharacterFactory.create(name='Terrencia', user=user2, open_requests=False)
        visible_private = CharacterFactory.create(name='Terrence', private=True, user=user)
        CharacterFactory.create(name='Terryvix', private=True, user=user2)
        visible_non_taggable = CharacterFactory.create(name='Terrifying', taggable=False, user=user)
        blocked_character = CharacterFactory.create(name='Terrific')
        blocked_character.user.blocking.add(user)
        CharacterFactory.create(name='Stuff')
        CharacterFactory.create(name='Terrible', taggable=False, user=user2)
        self.login(user)
        response = self.client.get('/api/profiles/v1/search/character/?q=terr&tagging=true')
        self.assertEqual(len(response.data['results']), 4)
        self.assertIDInList(visible, response.data['results'])
        self.assertIDInList(visible2, response.data['results'])
        self.assertIDInList(visible_non_taggable, response.data['results'])
        self.assertIDInList(visible_private, response.data['results'])
        self.assertEqual(visible2.id, response.data['results'][3]['id'])

    def test_query_logged_in_commission(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        visible = CharacterFactory.create(name='Terrybutt', open_requests=True, user=user)
        visible2 = CharacterFactory.create(name='Terrencia', open_requests=True, user=user2)
        visible3 = CharacterFactory.create(name='Terrifying', taggable=False, open_requests=True, user=user2)
        visible_private = CharacterFactory.create(name='Terrence', private=True, open_requests=True, user=user)
        CharacterFactory.create(name='Terryvix', private=True, open_requests=True, user=user2)
        CharacterFactory.create(name='Terrible', open_requests=False, user=user2)
        CharacterFactory.create(name='Terrp', taggable=True, open_requests=False, user=user2)
        CharacterFactory.create(name='Stuff', open_requests=True)
        self.login(user)
        response = self.client.get('/api/profiles/v1/search/character/?q=terr&new_order=1')
        self.assertEqual(len(response.data['results']), 4)
        self.assertIDInList(visible, response.data['results'])
        self.assertIDInList(visible_private, response.data['results'])
        self.assertIDInList(visible3, response.data['results'])
        self.assertEqual(visible2.id, response.data['results'][2]['id'])

    def test_query_logged_in_staffer(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        visible = CharacterFactory.create(name='Terrybutt', open_requests=True, user=user)
        visible2 = CharacterFactory.create(name='Terrencia', open_requests=True, user=user2)
        visible_private = CharacterFactory.create(name='Terrence', private=True, user=user)
        visible_non_taggable = CharacterFactory.create(name='Terrifying', taggable=False, user=user)
        CharacterFactory.create(name='Terryvix', open_requests=True, private=True, user=user2)
        CharacterFactory.create(name='Terrible', open_requests=False, user=user2)
        CharacterFactory.create(name='Stuff', open_requests=True)
        blocked_character = CharacterFactory.create(name='Terrific', open_requests=True)
        blocked_character.user.blocking.add(user)
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        response = self.client.get(
            '/api/profiles/v1/search/character/?q=terr&new_order=1&user={}&tagging=true'.format(user.id)
        )
        self.assertEqual(len(response.data['results']), 4)
        self.assertIDInList(visible, response.data['results'])
        self.assertIDInList(visible_private, response.data['results'])
        self.assertIDInList(visible_non_taggable, response.data['results'])
        self.assertEqual(visible2.id, response.data['results'][3]['id'])


class TestRefColor(APITestCase):
    def test_add_refcolor(self):
        char = CharacterFactory.create()
        self.login(char.user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/colors/'.format(char.user.username, char.name),
            {
                'color': '#456234',
                'note': 'Stuff'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['color'], '#456234')
        self.assertEqual(response.data['note'], 'Stuff')

    def test_add_refcolor_staff(self):
        char = CharacterFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/colors/'.format(char.user.username, char.name),
            {
                'color': '#456234',
                'note': 'Stuff'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['color'], '#456234')
        self.assertEqual(response.data['note'], 'Stuff')

    def test_add_refcolor_wrong_user(self):
        char = CharacterFactory.create()
        wrong_user = UserFactory.create()
        self.login(wrong_user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/colors/'.format(char.user.username, char.name),
            {
                'color': '#456234',
                'note': 'Stuff'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_color_not_logged_in(self):
        char = CharacterFactory.create()
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/colors/'.format(char.user.username, char.name),
            {
                'color': '#456234',
                'note': 'Stuff'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestTagArtist(APITestCase):
    def test_logged_in(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        submission = SubmissionFactory.create()
        self.login(submission.owner)
        response = self.client.post(
            '/api/profiles/v1/submission/{}/artists/'.format(submission.id),
            {'user_id': user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        submission.refresh_from_db()
        self.assertEqual(sorted(list(submission.artists.all().values_list('id', flat=True))), [user.id])

    def test_not_logged_in(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        submission = SubmissionFactory.create()
        response = self.client.post(
            '/api/profiles/v1/submission/{}/artists/'.format(submission.id),
            {'user_id': user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logged_in_different_user(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        submission = SubmissionFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/profiles/v1/submission/{}/artists/'.format(submission.id),
            {'user_id': user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        submission.refresh_from_db()
        self.assertEqual(sorted(list(submission.artists.all().values_list('id', flat=True))), [user.id])

    def test_delete_logged_in(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        submission = SubmissionFactory.create()
        submission.artists.add(user, user2, submission.owner)
        share = submission.artists.through.objects.get(user=user, submission=submission)
        self.login(submission.owner)
        response = self.client.delete(
            '/api/profiles/v1/submission/{}/artists/{}/'.format(submission.id, share.id),
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        submission.refresh_from_db()
        self.assertEqual(
            list(submission.artists.all().order_by('id').values_list('id', flat=True)),
            [user2.id, submission.owner.id],
        )

    def test_delete_not_logged_in(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        submission = SubmissionFactory.create()
        submission.artists.add(user, user2, submission.owner)
        share = submission.artists.through.objects.get(user=user, submission=submission)
        response = self.client.delete(
            '/api/profiles/v1/submission/{}/artists/{}/'.format(submission.id, share.id),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_other_user_tagged(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        submission = SubmissionFactory.create()
        submission.artists.add(user, user2, submission.owner)
        self.login(user)
        share = submission.artists.through.objects.get(user=user, submission=submission)
        response = self.client.delete(
            '/api/profiles/v1/submission/{}/artists/{}/'.format(submission.id, share.id),
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        submission.refresh_from_db()
        self.assertEqual(
            sorted(list(submission.artists.all().order_by('id').values_list('id', flat=True))),
            [user2.id, submission.owner.id],
        )


class TestShareSubmission(APITestCase):
    def test_logged_in(self):
        user = UserFactory.create()
        submission = SubmissionFactory.create()
        self.login(submission.owner)
        response = self.client.post(
            '/api/profiles/v1/submission/{}/share/'.format(submission.id),
            {'user_id': user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        submission.refresh_from_db()
        self.assertEqual(
            sorted(list(submission.shared_with.all().values_list('id', flat=True))), [user.id]
        )
        notification1 = Notification.objects.get(event__type=SUBMISSION_SHARED, user=user)
        self.assertEqual(notification1.event.data['user'], submission.owner.id)
        self.assertEqual(notification1.event.data['submission'], submission.id)

    def test_not_logged_in(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        submission = SubmissionFactory.create()
        response = self.client.post(
            '/api/profiles/v1/submission/{}/share/'.format(submission.id),
            {'user_id': user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logged_in_different_user(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        submission = SubmissionFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/profiles/v1/submission/{}/share/'.format(submission.id),
            {'user_id': user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_logged_in(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        submission = SubmissionFactory.create()
        submission.shared_with.add(user, user2, submission.owner)
        self.login(submission.owner)
        share_id = submission.shared_with.through.objects.get(user=user, submission=submission).id
        response = self.client.delete(
            '/api/profiles/v1/submission/{}/share/{}/'.format(submission.id, share_id),
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        submission.refresh_from_db()
        self.assertEqual(
            list(submission.shared_with.all().order_by('id').values_list('id', flat=True)),
            [user2.id, submission.owner.id],
        )

    def test_delete_not_logged_in(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        submission = SubmissionFactory.create()
        submission.shared_with.add(user, user2, submission.owner)
        share = submission.shared_with.through.objects.get(user=user, submission=submission)
        response = self.client.delete(
            f'/api/profiles/v1/submission/{submission.id}/share/{share.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_wrong_user(self):
        user = UserFactory.create()
        submission = SubmissionFactory.create()
        share = Submission.shared_with.through.objects.create(user=user, submission=submission)
        self.login(UserFactory.create())
        response = self.client.delete(
            f'/api/profiles/v1/submission/{submission.id}/share/{share.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_other_user_tagged(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        submission = SubmissionFactory.create()
        share = submission.shared_with.through.objects.create(user=user, submission=submission)
        self.login(user)
        response = self.client.delete(
            f'/api/profiles/v1/submission/{submission.id}/share/{share.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_notification_deleted(self):
        user = UserFactory.create()
        submission = SubmissionFactory.create()
        self.login(submission.owner)
        response = self.client.post(
            '/api/profiles/v1/submission/{}/share/'.format(submission.id),
            {'user_id': user.id}
        )
        self.assertEqual(response.data['user']['id'], user.id)
        self.client.delete(
            '/api/profiles/v1/submission/{}/share/{}/'.format(submission.id, response.data['id']),
        )
        notification = Notification.objects.get(event__type=SUBMISSION_SHARED, user=user)
        self.assertTrue(notification.event.recalled)


class TestCharacterTag(APITestCase):
    def test_tag_user(self):
        user = UserFactory.create()
        self.login(user)
        char = CharacterFactory.create(user=user)
        response = self.client.patch(
            '/api/profiles/v1/account/{}/characters/{}/'.format(user.username, char.name),
            {'tags': ['sexy', 'vix']}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        char.refresh_from_db()
        self.assertEqual(sorted(list(char.tags.all().values_list('name', flat=True))), ['sexy', 'vix'])


class TestSubmissionTag(APITestCase):
    def test_tag_user(self):
        user = UserFactory.create()
        self.login(user)
        submission = SubmissionFactory.create(owner=user)
        response = self.client.patch(
            '/api/profiles/v1/submission/{}/'.format(submission.id),
            {'tags': ['sexy', 'vix']}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        submission.refresh_from_db()
        self.assertEqual(sorted(list(submission.tags.all().values_list('name', flat=True))), ['sexy', 'vix'])


class TestTagCharacter(APITestCase):
    def test_tag_character(self):
        user = UserFactory.create()
        self.login(user)
        character = CharacterFactory.create(name='Gooby')
        submission = SubmissionFactory.create()
        response = self.client.post(
            '/api/profiles/v1/submission/{}/characters/'.format(submission.id),
            {'character_id': character.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        submission.refresh_from_db()
        self.assertEqual(submission.characters.all().count(), 1)
        self.assertEqual(submission.characters.all()[0], character)

    def test_delete_tag(self):
        user = UserFactory.create()
        self.login(user)
        character = CharacterFactory.create(name='Gooby', user=user)
        submission = SubmissionFactory.create()
        submission.characters.add(character)
        tag = submission.characters.through.objects.get(submission=submission, character=character)
        response = self.client.delete(
            f'/api/profiles/v1/submission/{submission.id}/characters/{tag.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(submission.characters.all().count(), 0)


class TestShareCharacter(APITestCase):
    def test_logged_in(self):
        user = UserFactory.create()
        character = CharacterFactory.create()
        self.login(character.user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/share/'.format(character.user.username, character.name),
            {'user_id': user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['id'], user.id)
        character.refresh_from_db()
        self.assertEqual(
            sorted(list(character.shared_with.all().values_list('id', flat=True))), [user.id]
        )
        notification1 = Notification.objects.get(event__type=CHAR_SHARED, user=user)
        self.assertEqual(notification1.event.data['user'], character.user.id)
        self.assertEqual(notification1.event.data['character'], character.id)

    def test_not_logged_in(self):
        user = UserFactory.create()
        character = CharacterFactory.create()
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/share/'.format(character.user.username, character.name),
            {'user_id': user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logged_in_different_user(self):
        character = CharacterFactory.create()
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/share/'.format(character.user.username, character.name),
            {'user': user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_logged_in(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        character = CharacterFactory.create()
        self.login(character.user)
        character.shared_with.add(user, user2)
        share = character.shared_with.through.objects.get(character=character, user=user2)
        response = self.client.delete(
            '/api/profiles/v1/account/{}/characters/{}/share/{}/'.format(
                character.user.username, character.name, share.id,
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        character.refresh_from_db()
        self.assertEqual(list(character.shared_with.all().values_list('id', flat=True)), [user.id])

    def test_delete_not_logged_in(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        character = CharacterFactory.create()
        character.shared_with.add(user, user2, character.user)
        share = character.shared_with.through.objects.get(character=character, user=user)
        response = self.client.delete(
            '/api/profiles/v1/account/{}/characters/{}/share/{}/'.format(
                character.user.username, character.name, share.id,
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_wrong_user(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        character = CharacterFactory.create()
        character.shared_with.add(user, user2, character.user)
        share = character.shared_with.through.objects.get(character=character, user=user)
        self.login(UserFactory.create())
        response = self.client.delete(
            '/api/profiles/v1/account/{}/characters/{}/share/{}/'.format(
                character.user.username, character.name, share.id,
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_other_user_tagged(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        character = CharacterFactory.create()
        character.shared_with.add(user, user2, character.user)
        share = character.shared_with.through.objects.get(character=character, user=user)
        self.login(user)
        response = self.client.delete(
            '/api/profiles/v1/account/{}/characters/{}/share/{}/'.format(
                character.user.username, character.name, share.id,
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_notification_deleted(self):
        user = UserFactory.create()
        character = CharacterFactory.create()
        self.login(character.user)
        self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/share/'.format(character.user.username, character.name),
            {'user_id': user.id}
        )
        share = character.shared_with.through.objects.get(character=character, user=user)
        self.client.delete(
            '/api/profiles/v1/account/{}/characters/{}/share/{}/'.format(
                character.user.username, character.name, share.id,
            ),
        )
        notification = Notification.objects.get(event__type=CHAR_SHARED, user=user)
        self.assertTrue(notification.event.recalled)


class TestWatch(APITestCase):
    def test_watch_user(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        response = self.client.patch(
            '/api/profiles/v1/account/{}/'.format(user2.username),
            {'watching': True}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.watching.all().count(), 1)
        self.assertEqual(user.watching.all()[0], user2)
        event_types = [NEW_CHARACTER, NEW_PRODUCT]
        for event_type in event_types:
            logger.info('Checking {}'.format(event_type))
            self.assertTrue(Subscription.objects.filter(
                subscriber=user,
                content_type=ContentType.objects.get_for_model(user2),
                object_id=user2.id,
                type=event_type
            ).exists())
        response = self.client.patch(
            '/api/profiles/v1/account/{}/'.format(user2.username),
            {'watching': False}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.watching.all().count(), 0)
        for event_type in event_types:
            logger.info('Checking {}'.format(event_type))
            self.assertFalse(Subscription.objects.filter(
                subscriber=user,
                content_type=ContentType.objects.get_for_model(user2),
                object_id=user2.id,
                type=event_type
            ).exists())

    def test_watch_user_no_login(self):
        user = UserFactory.create()
        response = self.client.patch(
            '/api/profiles/v1/account/{}/'.format(user.username),
            {'watching': True}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestFavorite(APITestCase):
    def test_favorite_submission(self):
        user = UserFactory.create()
        submission = SubmissionFactory.create()
        self.login(user)
        response = self.client.patch(
            '/api/profiles/v1/submission/{}/'.format(submission.id),
            {'favorites': True},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.favorites.all().count(), 1)
        self.assertEqual(user.favorites.all()[0], submission)
        response = self.client.patch(
            '/api/profiles/v1/submission/{}/'.format(submission.id),
            {'favorites': False},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.favorites.all().count(), 0)

    def test_favorite_submission_not_destroy_others(self):
        user = UserFactory.create()
        submission = SubmissionFactory.create()
        user2 = UserFactory.create()
        submission2 = SubmissionFactory.create()
        submission3 = SubmissionFactory.create()
        user.favorites.add(submission3)
        user2.favorites.add(submission)
        user2.favorites.add(submission2)
        self.assertEqual(user2.favorites.through.objects.filter(user=user2).count(), 2)
        self.assertEqual(user2.favorites.through.objects.filter(user=user).count(), 1)
        self.login(user)
        response = self.client.patch(
            '/api/profiles/v1/submission/{}/'.format(submission.id),
            {'favorites': True},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.favorites.all().count(), 2)
        self.assertEqual(user.favorites.all()[0], submission)
        response = self.client.patch(
            '/api/profiles/v1/submission/{}/'.format(submission.id),
            {'favorites': False},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.favorites.all().count(), 1)
        self.assertEqual(user2.favorites.through.objects.filter(user=user2).count(), 2)

    def test_favorite_submission_hidden_failure(self):
        user = UserFactory.create()
        submission = SubmissionFactory.create(private=True)
        self.login(user)
        response = self.client.patch(
            '/api/profiles/v1/submission/{}/'.format(submission.id),
            {'favorites': True},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_favorite_submission_hidden_shared(self):
        user = UserFactory.create()
        submission = SubmissionFactory.create(private=True)
        submission.shared_with.add(user)
        self.login(user)
        response = self.client.patch(
            '/api/profiles/v1/submission/{}/'.format(submission.id),
            {'favorites': True},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.favorites.all().count(), 1)
        self.assertEqual(user.favorites.all()[0], submission)
        response = self.client.patch(
            '/api/profiles/v1/submission/{}/'.format(submission.id),
            {'favorites': False},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.favorites.all().count(), 0)

    def test_favorite_submission_no_login(self):
        submission = SubmissionFactory.create()
        response = self.client.patch(
            '/api/profiles/v1/submission/{}/'.format(submission.id),
            {'favorites': True},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



class TestConversations(APITestCase):
    @patch('recaptcha.fields.ReCaptchaField.to_internal_value')
    def test_create_conversation(self, _mock_captcha):
        user = UserFactory.create(date_joined=timezone.now() - relativedelta(days=10))
        user2 = UserFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/conversations/'.format(user.username),
            {
                'participants': [user2.id],
                'captcha': 'dummy',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        conversation_id = response.data['id']
        response = self.client.get(
            '/api/profiles/v1/account/{}/conversations/{}/'.format(user.username, conversation_id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIDInList(user2.id, response.data['participants'])
        self.assertIDInList(user.id, response.data['participants'])

        self.login(user2)
        response = self.client.get(
            '/api/profiles/v1/account/{}/conversations/{}/'.format(user2.username, conversation_id),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIDInList(user2.id, response.data['participants'])
        self.assertIDInList(user.id, response.data['participants'])

        user3 = UserFactory.create()
        self.login(user3)
        response = self.client.get(
            '/api/profiles/v1/account/{}/conversations/{}/'.format(user.username, conversation_id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        subscriptions = Subscription.objects.filter(
            type=COMMENT, content_type=ContentType.objects.get_for_model(Conversation),
            object_id=conversation_id
        )
        self.assertEqual(subscriptions.count(), 2)
        self.assertTrue(subscriptions.filter(subscriber=user).exists())
        self.assertTrue(subscriptions.filter(subscriber=user2).exists())

    @patch('recaptcha.fields.ReCaptchaField.to_internal_value')
    def test_no_new_user_conversation(self, _mock_captcha):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/conversations/'.format(user.username),
            {
                'participants': [user2.id],
                'captcha': 'dummy',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Your account is too new. Please try again later.')

    @patch('recaptcha.fields.ReCaptchaField.to_internal_value')
    def test_singleton_conversation(self, _mock_captcha):
        user = UserFactory.create(date_joined=timezone.now() - relativedelta(days=10))
        user2 = UserFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/conversations/'.format(user.username),
            {
                'participants': [user2.id],
                'captcha': 'dummy',
            },
            format='json',
        )
        conversation1_id = response.data['id']
        response = self.client.post(
            '/api/profiles/v1/account/{}/conversations/'.format(user.username),
            {
                'participants': [user2.id],
                'captcha': 'dummy',
            },
            format='json',
        )
        conversation2_id = response.data['id']
        self.assertEqual(conversation1_id, conversation2_id)
        user3 = UserFactory.create()
        response = self.client.post(
            '/api/profiles/v1/account/{}/conversations/'.format(user.username),
            {
                'participants': [user3.id],
                'captcha': 'dummy',
            },
            format='json',
        )
        conversation3_id = response.data['id']
        self.assertNotEqual(conversation2_id, conversation3_id)

    @patch('recaptcha.fields.ReCaptchaField.to_internal_value')
    def test_conversation_no_delete_others(self, _mock_captcha):
        # Apparently one of my serializers had a terrible side effect of deleting all other conversations when a new
        # one was created.
        relation = ConversationParticipantFactory.create()
        user = UserFactory.create(date_joined=timezone.now() - relativedelta(days=10))
        user2 = UserFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/conversations/'.format(user.username),
            {
                'participants': [user2.id],
                'captcha': 'dummy',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        relation.refresh_from_db()
        self.assertTrue(relation.id)

    def test_conversations_list(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        relationships = [ConversationParticipantFactory.create(user=user) for _ in range(3)]
        conversations = [relationship.conversation for relationship in relationships]
        CommentFactory.create(
            object_id=conversations[0].id, content_type=ContentType.objects.get_for_model(Conversation),
            top=conversations[0],
        )
        self.login(user)
        response = self.client.get('/api/profiles/v1/account/{}/conversations/'.format(user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIDInList(conversations[0], response.data['results'])
        self.login(user2)
        response = self.client.get('/api/profiles/v1/account/{}/conversations/'.format(user.username))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        response = self.client.get('/api/profiles/v1/account/{}/conversations/'.format(user.username))
        # Even staffers can't just go browsing.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mark_read(self):
        participant_relationship = ConversationParticipantFactory.create()
        self.assertIs(participant_relationship.read, False)
        user, conversation = participant_relationship.user, participant_relationship.conversation
        self.login(user)
        url = f'/api/profiles/v1/account/{user.username}/conversations/{conversation.id}/'
        response = self.client.get(url)
        self.assertIs(response.data['read'], False)
        response = self.client.patch(url, {'read': True})
        participant_relationship.refresh_from_db()
        self.assertIs(participant_relationship.read, True)
        self.assertIs(response.data['read'], True)
        response = self.client.get(url)
        self.assertIs(response.data['read'], True)

    def test_leave_conversation(self):
        # The view creates the subscriptions, so use it for this test.
        user = UserFactory.create()
        user2 = UserFactory.create()
        user3 = UserFactory.create()
        conversation = ConversationParticipantFactory.create(user=user).conversation
        ConversationParticipantFactory.create(user=user2, conversation=conversation)
        ConversationParticipantFactory.create(user=user3, conversation=conversation)
        subscriptions = Subscription.objects.filter(
            type=COMMENT, content_type=ContentType.objects.get_for_model(Conversation),
            object_id=conversation.id,
        )
        self.assertEqual(subscriptions.count(), 3)
        self.assertEqual(ConversationParticipant.objects.all().count(), 3)
        self.login(user)
        response = self.client.delete(
            '/api/profiles/v1/account/{}/conversations/{}/'.format(user.username, conversation.id),
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        subscriptions = Subscription.objects.filter(
            type=COMMENT, content_type=ContentType.objects.get_for_model(Conversation),
            object_id=conversation.id,
        )
        self.assertEqual(ConversationParticipant.objects.all().count(), 2)
        self.assertEqual(subscriptions.count(), 2)

        self.login(user2)
        response = self.client.delete(
            '/api/profiles/v1/account/{}/conversations/{}/'.format(user2.username, conversation.id),
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        subscriptions = Subscription.objects.filter(
            type=COMMENT, content_type=ContentType.objects.get_for_model(Conversation),
            object_id=conversation.id
        )
        self.assertEqual(subscriptions.count(), 0)

        self.assertRaises(Conversation.DoesNotExist, conversation.refresh_from_db)


class ListTestCase(APITestCase):
    def test_gallery_list(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        submission = Submission.objects.create(owner=user2)
        submission.artists.add(user)
        submission2 = Submission.objects.create(owner=user2, private=True)
        submission2.artists.add(user)
        response = self.client.get(
            '/api/profiles/v1/account/{}/submissions/art/'.format(user.username),
            {'is_artist': True}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIDInList(submission, [item['submission'] for item in response.data['results']])
        self.assertEqual(1, len(response.data['results']))


@patch('recaptcha.fields.ReCaptchaField.to_internal_value')
class TestRegister(EnsurePlansMixin, APITestCase):
    def test_basic_user(self, _mock_captcha):
        response = self.client.post('/api/profiles/v1/register/', {
            'username': 'Goober',
            'password': 'test_password',
            'email': 'test@example.com',
            'recaptcha': 'dummy',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='Goober')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('test_password'))

    def test_user_promo_code(self, _mock_captcha):
        promo = PromoFactory.create()
        self.client.post('/api/profiles/v1/register/', {
            'username': 'Goober',
            'password': 'test_password',
            'email': 'test@example.com',
            'recaptcha': 'dummy',
            'registration_code': promo.code
        })
        user = User.objects.get(username='Goober')
        self.assertEqual(promo, user.registration_code)

    @patch('apps.profiles.views.claim_order_by_token')
    def test_claim_order(self, mock_claim, _mock_captcha):
        self.client.post('/api/profiles/v1/register/', {
            'username': 'Goober',
            'password': 'test_password',
            'email': 'test@example.com',
            'recaptcha': 'dummy',
            'order_claim': 'XtFxMb7qTJ-A'
        })
        user = User.objects.get(username='Goober')
        mock_claim.assert_called_with('XtFxMb7qTJ-A', user, force=True)


class TestLogin(APITestCase):
    def test_basic_login(self):
        UserFactory.create(username='Goober', password='Test', email='test@example.com')
        response = self.client.post('/api/profiles/v1/login/', {
            'email': 'test@example.com',
            'password': 'Test',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('apps.profiles.views.match_token')
    def test_2fa(self, mock_match_token):
        user = UserFactory.create(username='Goober', password='Test', email='test@example.com')
        device = TOTPDeviceFactory.create(user=user)
        mock_match_token.side_effect = [device]
        response = self.client.post('/api/profiles/v1/login/', {
            'email': 'test@example.com',
            'password': 'Test',
            'token': '123456'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_match_token.assert_called_with(user, '123456')

    @patch('apps.profiles.views.claim_order_by_token')
    def test_login_claim_order(self, _mock_claim):
        UserFactory.create(username='Goober', password='Test', email='test@example.com')
        response = self.client.post('/api/profiles/v1/login/', {
            'email': 'test@example.com',
            'password': 'Test',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestAttributes(APITestCase):
    def test_attribute_listing(self):
        character = CharacterFactory.create()
        attributes = [AttributeFactory.create(character=character) for _ in range(3)]
        response = self.client.get(
            f'/api/profiles/v1/account/{character.user.username}/characters/{character.name}/attributes/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for attr in attributes:
            self.assertIDInList(attr, response.data)

    def test_create_attribute(self):
        character = CharacterFactory.create()
        self.login(character.user)
        response = self.client.post(
            f'/api/profiles/v1/account/{character.user.username}/characters/{character.name}/attributes/',
            {'key': 'Test', 'value': 'Thing'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['key'], 'test')
        self.assertEqual(response.data['value'], 'Thing')

    def test_edit_attribute(self):
        attribute = AttributeFactory.create()
        character = attribute.character
        self.login(character.user)
        response = self.client.patch(
            f'/api/profiles/v1/account/{character.user.username}/characters/'
            f'{character.name}/attributes/{attribute.id}/',
            {'key': 'Beep', 'value': 'Boop'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        attribute.refresh_from_db()
        self.assertEqual(attribute.key, 'beep')
        self.assertEqual(attribute.value, 'Boop')

    def test_replace_existing(self):
        attribute = AttributeFactory.create(key='beep')
        character = attribute.character
        self.login(character.user)
        response = self.client.post(
            f'/api/profiles/v1/account/{character.user.username}/characters/'
            f'{character.name}/attributes/',
            {'key': 'Beep', 'value': 'Blorp'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        attribute.refresh_from_db()
        self.assertEqual(attribute.key, 'beep')
        self.assertEqual(attribute.value, 'Blorp')


@ddt
class TestWithdrawOnAutoWithdrawEnabled(APITestCase):
    @unpack
    @data((False, True, True), (False, False, False), (True, False, False), (True, True, False))
    @patch('apps.profiles.views.withdraw_all')
    def test_auto_withdraw_triggers(self, initial_value, new_value, triggered, mock_withdraw_all):
        user = UserFactory.create(artist_profile__auto_withdraw=initial_value)
        self.login(user)
        self.client.patch(f'/api/profiles/v1/account/{user.username}/artist-profile/', {'auto_withdraw': new_value})
        if triggered:
            mock_withdraw_all.apply_async.assert_called_with((user.id,), countdown=10)
        else:
            mock_withdraw_all.apply_async.assert_not_called()


class TestDestroyUser(EnsurePlansMixin, APITestCase):
    def test_destroy_user(self):
        user = UserFactory.create()
        self.login(user)
        self.assertTrue(user.is_active)
        response = self.client.post(
            f'/api/profiles/v1/account/{user.username}/auth/delete-account/',
            {'username': user.username, 'password': 'Test', 'email': user.email, 'verify': True},
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_destroy_user_fails_wrong_password(self):
        user = UserFactory.create()
        self.login(user)
        self.assertTrue(user.is_active)
        response = self.client.post(
            f'/api/profiles/v1/account/{user.username}/auth/delete-account/',
            {'username': user.username, 'password': 'WrongPassword', 'email': user.email, 'verify': True},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_destroy_user_fails_no_verify(self):
        user = UserFactory.create()
        self.login(user)
        self.assertTrue(user.is_active)
        response = self.client.post(
            f'/api/profiles/v1/account/{user.username}/auth/delete-account/',
            {'username': user.username, 'password': 'WrongPassword', 'email': user.email, 'verify': False},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('verify', response.data)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_destroy_user_fails_empty_request(self):
        user = UserFactory.create()
        self.login(user)
        self.assertTrue(user.is_active)
        response = self.client.post(
            f'/api/profiles/v1/account/{user.username}/auth/delete-account/',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('verify', response.data)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_destroy_user_fails_unauthenticated(self):
        user = UserFactory.create()
        self.assertTrue(user.is_active)
        response = self.client.post(
            f'/api/profiles/v1/account/{user.username}/auth/delete-account/',
            {'username': user.username, 'password': 'Test', 'email': user.email, 'verify': True},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_destroy_user_fails_wrong_user(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        self.assertTrue(user.is_active)
        response = self.client.post(
            f'/api/profiles/v1/account/{user.username}/auth/delete-account/',
            {'username': user.username, 'password': 'Test', 'email': user.email, 'verify': True},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_destroy_user_staff(self):
        user = UserFactory.create()
        user2 = UserFactory.create(is_staff=True)
        self.login(user2)
        self.assertTrue(user.is_active)
        response = self.client.post(
            f'/api/profiles/v1/account/{user.username}/auth/delete-account/',
            {'username': user.username, 'password': 'Test', 'email': user.email, 'verify': True},
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertFalse(user.is_active)


class TestProfilePreview(EnsurePlansMixin, APITestCase):
    def test_profile_preview(self):
        user = UserFactory.create(biography='Beep boop')
        response = self.client.get(f'/profile/{user.username}/about')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'Beep boop', response.content)
