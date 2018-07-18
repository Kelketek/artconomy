import logging

from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.lib.models import FAVORITE, Subscription, COMMENT, Notification, ASSET_SHARED, CHAR_SHARED, \
    NEW_PRODUCT, NEW_CHARACTER, NEW_PM
from apps.lib.utils import watch_subscriptions
from apps.profiles.models import Character, ImageAsset, Message
from apps.lib.abstract_models import MATURE, ADULT, GENERAL
from apps.lib.test_resources import APITestCase
from apps.profiles.tests.factories import UserFactory, CharacterFactory, ImageAssetFactory, \
    MessageRecipientRelationshipFactory
from apps.profiles.tests.helpers import gen_characters, gen_image


logger = logging.getLogger(__name__)


class CharacterAPITestCase(APITestCase):
    def test_character_listing(self):
        characters = gen_characters(self.user)
        response = self.client.get('/api/profiles/v1/account/{}/characters/'.format(self.user.username))
        self.assertEqual(len(response.data['results']), 5)
        for key, value in characters.items():
            self.assertIDInList(
                key,
                response.data['results']
            )

    def test_no_list_private(self):
        characters = gen_characters(self.user)
        private_character = list(characters.keys())[0]
        private_character.private = True
        private_character.save()

        # Should fail for unregistered user
        response = self.client.get('/api/profiles/v1/account/{}/characters/'.format(self.user.username))
        self.assertEqual(len(response.data['results']), 4)
        self.assertNotIn(private_character.id, [result['id'] for result in response.data['results']])

        # Should fail for unprivileged user
        self.login(self.user2)
        self.assertEqual(len(response.data['results']), 4)
        self.assertNotIn(private_character.id, [result['id'] for result in response.data['results']])

    def test_list_private_for_privileged(self):
        characters = gen_characters(self.user)
        private_character = list(characters.keys())[0]
        private_character.private = True
        private_character.save()

        # Should work for character owner.
        self.login(self.user)
        response = self.client.get('/api/profiles/v1/account/{}/characters/'.format(self.user.username))
        self.assertEqual(len(response.data['results']), 5)
        self.assertIDInList(private_character, response.data['results'])
        # Should work for staff, too.
        self.login(self.staffer)
        response = self.client.get('/api/profiles/v1/account/{}/characters/'.format(self.user.username))
        self.assertEqual(len(response.data['results']), 5)
        self.assertIDInList(private_character, response.data['results'])

    def test_new_character(self):
        self.login(self.user)
        watch_subscriptions(self.user2, self.user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/'.format(self.user.username), {
                'name': 'Fern',
                'description': 'The best of both worlds',
                'private': False,
                'open_requests': False,
                'open_requests_restrictions': 'Must be foxy.',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        char = Character.objects.get(name='Fern')
        self.assertEqual(char.description, 'The best of both worlds')
        self.assertEqual(char.private, False)
        self.assertEqual(char.open_requests, False)
        self.assertEqual(char.open_requests_restrictions, 'Must be foxy.')
        self.assertEqual(char.taggable, True)
        notifications = Notification.objects.filter(event__type=NEW_CHARACTER)
        self.assertEqual(notifications.count(), 1)
        notification = notifications[0]
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.event.data, {'character': char.id})

        # Should work for staffer.
        self.login(self.staffer)
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/'.format(self.user.username), {
                'name': 'Rain',
                'description': 'Heart breaker',
                'private': True,
                'open_requests': False,
                'open_requests_restrictions': 'Must be really foxy.',
                'taggable': False,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        char2 = Character.objects.get(name='Rain')
        self.assertEqual(char2.user, self.user)
        self.assertEqual(char2.description, 'Heart breaker')
        self.assertEqual(char2.private, True)
        self.assertEqual(char2.open_requests, False)
        self.assertEqual(char2.taggable, False)
        self.assertEqual(char2.open_requests_restrictions, 'Must be really foxy.')
        # No new notifications should have been created, since this character is private.
        notifications = Notification.objects.filter(event__type=NEW_CHARACTER)
        self.assertEqual(notifications.count(), 1)
        notification = notifications[0]
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.event.data, {'character': char.id})

    def test_edit_character(self):
        self.login(self.user)
        watch_subscriptions(self.user2, self.user)
        char = CharacterFactory.create(user=self.user)
        notifications = Notification.objects.filter(event__type=NEW_CHARACTER)
        self.assertEqual(notifications.count(), 1)
        notification = notifications[0]
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.event.data, {'character': char.id})
        self.assertFalse(notification.event.recalled)
        response = self.client.patch(
            '/api/profiles/v1/account/{}/characters/{}/'.format(self.user.username, char.name),
            {
                'name': 'Terrence',
                'description': 'Positively foxy.',
                'private': True
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        char.refresh_from_db()
        self.assertEqual(char.name, 'Terrence')
        self.assertEqual(char.description, 'Positively foxy.')
        notification.event.refresh_from_db()
        notification.refresh_from_db()
        self.assertTrue(notification.event.recalled)

        # Should work for staff, too.
        self.login(self.staffer)
        response = self.client.patch(
            '/api/profiles/v1/account/{}/characters/{}/'.format(self.user.username, char.name),
            {
                'name': 'Rain',
                'description': 'Supremely foxy.'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        char.refresh_from_db()
        self.assertEqual(char.name, 'Rain')
        self.assertEqual(char.description, 'Supremely foxy.')

    def test_edit_character_permission_denied(self):
        char = CharacterFactory.create(user=self.user)
        self.login(self.user2)
        response = self.client.patch(
            '/api/profiles/v1/account/{}/characters/{}/'.format(self.user.username, char.name),
            {
                'name': 'Terrence',
                'description': 'Positively foxy.'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_character(self):
        self.login(self.user)
        char = CharacterFactory.create(user=self.user)
        response = self.client.delete(
            '/api/profiles/v1/account/{}/characters/{}/'.format(self.user.username, char.name)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRaises(Character.DoesNotExist, char.refresh_from_db)

        # Test for staff.
        char = CharacterFactory.create(user=self.user)

        response = self.client.delete(
            '/api/profiles/v1/account/{}/characters/{}/'.format(self.user.username, char.name)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRaises(Character.DoesNotExist, char.refresh_from_db)

    def test_primary_asset(self):
        self.login(self.user)
        char = CharacterFactory.create(user=self.user)
        asset = ImageAssetFactory.create(owner=self.user)
        asset.characters.add(char)
        char.refresh_from_db()
        self.assertIsNone(char.primary_asset)

        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/asset/primary/{}/'.format(self.user.username, char.name, asset.id),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        char.refresh_from_db()
        self.assertEqual(char.primary_asset, asset)

        # Should work for staff, too.
        asset2 = ImageAssetFactory.create(owner=self.staffer)
        asset2.characters.add(char)

        self.login(self.staffer)
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/asset/primary/{}/'.format(self.user.username, char.name, asset2.id),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        char.refresh_from_db()
        self.assertEqual(char.primary_asset, asset2)

    def test_primary_asset_forbidden(self):
        self.login(self.user2)
        char = CharacterFactory.create(user=self.user)
        asset = ImageAssetFactory.create(owner=self.user)
        asset.characters.add(char)
        char.refresh_from_db()
        self.assertIsNone(char.primary_asset)

        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/asset/primary/{}/'.format(self.user.username, char.name, asset.id),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_asset_upload(self):
        self.login(self.user)
        char = CharacterFactory.create(user=self.user)
        watch_subscriptions(self.user2, self.user)
        uploaded = SimpleUploadedFile('bloo-oo.jpg', gen_image())
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/assets/'.format(self.user.username, char.name),
            {
                'title': 'Blooo',
                'caption': "A sea of blue.",
                'private': False,
                'rating': ADULT,  # Such a sexy color!
                'file': uploaded,
                'is_artist': True
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        asset = ImageAsset.objects.get(characters__name=char.name)
        self.assertEqual(asset.title, 'Blooo')
        self.assertEqual(asset.caption, 'A sea of blue.')
        self.assertFalse(asset.private)
        self.assertEqual(asset.rating, ADULT)
        self.assertEqual(asset.artists.all()[0], self.user)
        self.assertIn('bloo-oo', asset.file.url)
        self.assertEqual(Subscription.objects.filter(type=FAVORITE).count(), 1)
        asset.delete()
        self.assertEqual(Subscription.objects.filter(type=FAVORITE).count(), 0)
        # Should work for staffer, too.
        self.login(self.staffer)
        uploaded = SimpleUploadedFile('gree-een.jpg', gen_image(color='green'))
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/assets/'.format(self.user.username, char.name),
            {
                'title': 'Green',
                'caption': "A sea of green.",
                'private': False,
                'rating': ADULT,  # Such a sexy color!
                'file': uploaded,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        asset = ImageAsset.objects.get(characters__name=char.name)
        self.assertEqual(asset.title, 'Green')
        self.assertEqual(asset.caption, 'A sea of green.')
        self.assertFalse(asset.private)
        self.assertEqual(asset.rating, ADULT)
        self.assertIn('gree-een', asset.file.url)
        Subscription.objects.get(
            object_id=asset.id, content_type=ContentType.objects.get_for_model(asset),
            type=COMMENT,
            subscriber=asset.owner
        )

    def test_asset_upload_forbidden(self):
        self.login(self.user2)
        char = CharacterFactory.create(user=self.user)
        uploaded = SimpleUploadedFile('bloo-oo.jpg', gen_image())
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/assets/'.format(self.user.username, char.name),
            {
                'title': 'Blooo',
                'caption': "A sea of blue.",
                'private': False,
                'rating': ADULT,  # Such a sexy color!
                'file': uploaded,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_asset_edit(self):
        self.login(self.user)
        char = CharacterFactory.create(user=self.user)
        asset = ImageAssetFactory.create(owner=self.user)
        asset.characters.add(char)
        response = self.client.patch(
            '/api/profiles/v1/asset/{}/'.format(asset.id),
            {
                'title': 'Porn',
                'caption': 'Shameless porn.',
                'private': True,
                'rating': MATURE,  # Bad user. You should know better!
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        asset.refresh_from_db()
        self.assertEqual(asset.title, 'Porn')
        self.assertEqual(asset.caption, 'Shameless porn.')
        self.assertEqual(asset.private, True)
        self.assertEqual(asset.rating, MATURE)

        # Should work for staffer, too.
        self.login(self.staffer)
        response = self.client.patch(
            '/api/profiles/v1/asset/{}/'.format(asset.id),
            {
                'title': 'Smut',
                'caption': 'Use the proper rating!',
                'private': False,
                'rating': ADULT,  # That's better.
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        asset.refresh_from_db()
        self.assertEqual(asset.title, 'Smut')
        self.assertEqual(asset.caption, 'Use the proper rating!')
        self.assertEqual(asset.private, False)
        self.assertEqual(asset.rating, ADULT)

    def test_asset_edit_forbidden(self):
        self.login(self.user2)
        char = CharacterFactory.create(user=self.user)
        asset = ImageAssetFactory.create(owner=self.user)
        asset.characters.add(char)
        response = self.client.patch(
            '/api/profiles/v1/asset/{}/'.format(asset.id),
            {
                'title': 'Porn',
                'caption': 'Shameless porn.',
                'private': True,
                'rating': MATURE,  # Bad user. You should know better!
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestSettings(APITestCase):
    def test_settings_post(self):
        self.login(self.user)
        response = self.client.patch(
            '/api/profiles/v1/account/{}/settings/'.format(self.user.username), {
                'rating': ADULT,
                'max_load': 5,
                'use_load_tracker': False,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                'commissions_closed': False,
                'rating': ADULT,
                'sfw_mode': False,
                'favorites_hidden': False,
                'max_load': 5,
                'taggable': True,
                'commission_info': '',
            }
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.rating, ADULT)

    def test_settings_wrong_user(self):
        self.login(UserFactory.create())
        response = self.client.patch(
            '/api/profiles/v1/account/{}/settings/'.format(self.user.username), {
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.user.refresh_from_db()
        self.assertEqual(self.user.rating, GENERAL)

    def test_credentials_post_username(self):
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/credentials/'.format(self.user.username),
            {'username': 'NewName', 'current_password': 'Test'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'NewName')

    def test_credentials_username_taken(self):
        self.login(self.user)
        conflicting = UserFactory.create()
        response = self.client.post(
            '/api/profiles/v1/account/{}/credentials/'.format(self.user.username),
            {'username': conflicting.username, 'current_password': 'Test'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        old_name = self.user.username
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.username, conflicting.username)
        self.assertEqual(self.user.username, old_name)

    def test_credentials_wrong_user(self):
        self.login(UserFactory.create())
        response = self.client.post(
            '/api/profiles/v1/account/{}/credentials/'.format(self.user.username),
            {'username': 'NewName', 'current_password': 'Test'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        old_username = self.user.username
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.username, 'NewName')
        self.assertEqual(self.user.username, old_username)

    def test_credentials_email_change(self):
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/credentials/'.format(self.user.username),
            {'current_password': 'Test', 'email': 'changed_email@example.com'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'changed_email@example.com')

    def test_credentials_email_taken(self):
        self.login(self.user)
        conflicting = UserFactory.create()
        response = self.client.post(
            '/api/profiles/v1/account/{}/credentials/'.format(self.user.username),
            {'current_password': 'Test', 'email': conflicting.email}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        old_email = self.user.email
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, conflicting.email)
        self.assertEqual(self.user.email, old_email)

    def test_credentials_username_no_password(self):
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/credentials/'.format(self.user.username),
            {'username': 'NewName'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        old_name = self.user.username
        self.user.refresh_from_db()
        self.assertEqual(old_name, self.user.username)

    def test_credentials_username_wrong_password(self):
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/credentials/'.format(self.user.username),
            {'username': 'NewName', 'current_password': 'password'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        old_name = self.user.username
        self.user.refresh_from_db()
        self.assertEqual(old_name, self.user.username)

    def test_credentials_change_password(self):
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/credentials/'.format(self.user.username),
            {
                'current_password': 'Test',
                'new_password': '1234TestABC',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('Test'))
        self.assertTrue(self.user.check_password('1234TestABC'))

    def test_credentials_wrong_password(self):
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/credentials/'.format(self.user.username),
            {
                'current_password': 'password',
                'new_password': '1234TestABC',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('1234'))
        self.assertTrue(self.user.check_password('Test'))


class TestSetBiography(APITestCase):
    def test_set_biography(self):
        self.login(self.user)
        response = self.client.patch(
            '/api/profiles/v1/data/user/{}/'.format(self.user.username),
            {
                'biography': 'test'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['biography'], 'test')


class ValidatorChecks(TestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()

    def test_username_validator_taken(self):
        UserFactory.create(username='testola')
        response = self.client.get('/api/profiles/v1/form-validators/username/', {'username': 'testola'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['available'])

    def test_username_validator_bad_request(self):
        response = self.client.get('/api/profiles/v1/form-validators/username/', format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'No username provided.')

    def test_username_validator_available(self):
        response = self.client.get('/api/profiles/v1/form-validators/username/', {'username': 'stuff'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['available'])


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
        visible = CharacterFactory.create(name='Terrybutt', user=self.user)
        visible2 = CharacterFactory.create(name='Terrencia', user=self.user2, open_requests=False)
        visible_private = CharacterFactory.create(name='Terrence', private=True, user=self.user)
        CharacterFactory.create(name='Terryvix', private=True, user=self.user2)
        visible_non_taggable = CharacterFactory.create(name='Terrifying', taggable=False, user=self.user)
        blocked_character = CharacterFactory.create(name='Terrific')
        blocked_character.user.blocking.add(self.user)
        CharacterFactory.create(name='Stuff')
        CharacterFactory.create(name='Terrible', taggable=False, user=self.user2)
        self.login(self.user)
        response = self.client.get('/api/profiles/v1/search/character/?q=terr&tagging=true')
        self.assertEqual(len(response.data['results']), 4)
        self.assertIDInList(visible, response.data['results'])
        self.assertIDInList(visible2, response.data['results'])
        self.assertIDInList(visible_non_taggable, response.data['results'])
        self.assertIDInList(visible_private, response.data['results'])
        self.assertEqual(visible2.id, response.data['results'][3]['id'])

    def test_query_logged_in_commission(self):
        visible = CharacterFactory.create(name='Terrybutt', open_requests=True, user=self.user)
        visible2 = CharacterFactory.create(name='Terrencia', open_requests=True, user=self.user2)
        visible3 = CharacterFactory.create(name='Terrifying', taggable=False, open_requests=True, user=self.user2)
        visible_private = CharacterFactory.create(name='Terrence', private=True, open_requests=True, user=self.user)
        CharacterFactory.create(name='Terryvix', private=True, open_requests=True, user=self.user2)
        CharacterFactory.create(name='Terrible', open_requests=False, user=self.user2)
        CharacterFactory.create(name='Terrp', taggable=True, open_requests=False, user=self.user2)
        CharacterFactory.create(name='Stuff', open_requests=True)
        self.login(self.user)
        response = self.client.get('/api/profiles/v1/search/character/?q=terr&new_order=1')
        self.assertEqual(len(response.data['results']), 4)
        self.assertIDInList(visible, response.data['results'])
        self.assertIDInList(visible_private, response.data['results'])
        self.assertIDInList(visible3, response.data['results'])
        self.assertEqual(visible2.id, response.data['results'][2]['id'])

    def test_query_logged_in_staffer(self):
        visible = CharacterFactory.create(name='Terrybutt', open_requests=True, user=self.user)
        visible2 = CharacterFactory.create(name='Terrencia', open_requests=True, user=self.user2)
        visible_private = CharacterFactory.create(name='Terrence', private=True, user=self.user)
        visible_non_taggable = CharacterFactory.create(name='Terrifying', taggable=False, user=self.user)
        CharacterFactory.create(name='Terryvix', open_requests=True, private=True, user=self.user2)
        CharacterFactory.create(name='Terrible', open_requests=False, user=self.user2)
        CharacterFactory.create(name='Stuff', open_requests=True)
        blocked_character = CharacterFactory.create(name='Terrific', open_requests=True)
        blocked_character.user.blocking.add(self.user)
        self.login(self.staffer)
        response = self.client.get(
            '/api/profiles/v1/search/character/?q=terr&new_order=1&user={}&tagging=true'.format(self.user.id)
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
        asset = ImageAssetFactory.create()
        self.login(asset.owner)
        response = self.client.post(
            '/api/profiles/v1/asset/{}/tag-artists/'.format(asset.id),
            {'artists': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], asset.id)
        asset.refresh_from_db()
        self.assertEqual(sorted(list(asset.artists.all().values_list('id', flat=True))), [self.user.id, self.user2.id])

    def test_not_logged_in(self):
        asset = ImageAssetFactory.create()
        response = self.client.post(
            '/api/profiles/v1/asset/{}/tag-artists/'.format(asset.id),
            {'artists': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logged_in_different_user(self):
        asset = ImageAssetFactory.create()
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/asset/{}/tag-artists/'.format(asset.id),
            {'artists': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], asset.id)
        asset.refresh_from_db()
        self.assertEqual(sorted(list(asset.artists.all().values_list('id', flat=True))), [self.user.id, self.user2.id])

    def test_delete_logged_in(self):
        asset = ImageAssetFactory.create()
        asset.artists.add(self.user, self.user2, asset.owner)
        self.login(asset.owner)
        response = self.client.delete(
            '/api/profiles/v1/asset/{}/tag-artists/'.format(asset.id),
            {'artists': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], asset.id)
        asset.refresh_from_db()
        self.assertEqual(list(asset.artists.all().values_list('id', flat=True)), [asset.owner.id])

    def test_delete_not_logged_in(self):
        asset = ImageAssetFactory.create()
        asset.artists.add(self.user, self.user2, asset.owner)
        response = self.client.delete(
            '/api/profiles/v1/asset/{}/tag-artists/'.format(asset.id),
            {'artists': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_wrong_user(self):
        asset = ImageAssetFactory.create()
        asset.artists.add(self.user, self.user2, asset.owner)
        self.login(UserFactory.create())
        response = self.client.delete(
            '/api/profiles/v1/asset/{}/tag-artists/'.format(asset.id),
            {'artists': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_other_user_tagged(self):
        asset = ImageAssetFactory.create()
        asset.artists.add(self.user, self.user2, asset.owner)
        self.login(self.user)
        response = self.client.delete(
            '/api/profiles/v1/asset/{}/tag-artists/'.format(asset.id),
            {'artists': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        asset.refresh_from_db()
        self.assertEqual(
            sorted(list(asset.artists.all().values_list('id', flat=True))), [self.user2.id, asset.owner.id]
        )


class TestShareAsset(APITestCase):
    def test_logged_in(self):
        asset = ImageAssetFactory.create()
        self.login(asset.owner)
        response = self.client.post(
            '/api/profiles/v1/asset/{}/share/'.format(asset.id),
            {'shared_with': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], asset.id)
        asset.refresh_from_db()
        self.assertEqual(
            sorted(list(asset.shared_with.all().values_list('id', flat=True))), [self.user.id, self.user2.id]
        )
        notification1 = Notification.objects.get(event__type=ASSET_SHARED, user=self.user)
        notification2 = Notification.objects.get(event__type=ASSET_SHARED, user=self.user)
        self.assertEqual(notification1.event.data['user'], asset.owner.id)
        self.assertEqual(notification2.event, notification1.event)
        self.assertEqual(notification1.event.data['asset'], asset.id)
        self.assertEqual(notification2.event, notification1.event)

    def test_not_logged_in(self):
        asset = ImageAssetFactory.create()
        response = self.client.post(
            '/api/profiles/v1/asset/{}/share/'.format(asset.id),
            {'shared_with': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logged_in_different_user(self):
        asset = ImageAssetFactory.create()
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/asset/{}/share/'.format(asset.id),
            {'shared_with': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_logged_in(self):
        asset = ImageAssetFactory.create()
        asset.shared_with.add(self.user, self.user2, asset.owner)
        self.login(asset.owner)
        response = self.client.delete(
            '/api/profiles/v1/asset/{}/share/'.format(asset.id),
            {'shared_with': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], asset.id)
        asset.refresh_from_db()
        self.assertEqual(list(asset.shared_with.all().values_list('id', flat=True)), [asset.owner.id])

    def test_delete_not_logged_in(self):
        asset = ImageAssetFactory.create()
        asset.shared_with.add(self.user, self.user2, asset.owner)
        response = self.client.delete(
            '/api/profiles/v1/asset/{}/share/'.format(asset.id),
            {'shared_with': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_wrong_user(self):
        asset = ImageAssetFactory.create()
        asset.artists.add(self.user, self.user2, asset.owner)
        self.login(UserFactory.create())
        response = self.client.delete(
            '/api/profiles/v1/asset/{}/share/'.format(asset.id),
            {'shared_with': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_other_user_tagged(self):
        asset = ImageAssetFactory.create()
        asset.shared_with.add(self.user, self.user2, asset.owner)
        self.login(self.user)
        response = self.client.delete(
            '/api/profiles/v1/asset/{}/share/'.format(asset.id),
            {'shared_with': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_notification_deleted(self):
        asset = ImageAssetFactory.create()
        self.login(asset.owner)
        self.client.post(
            '/api/profiles/v1/asset/{}/share/'.format(asset.id),
            {'shared_with': [self.user.id]}
        )
        self.client.delete(
            '/api/profiles/v1/asset/{}/share/'.format(asset.id),
            {'shared_with': [self.user.id]}
        )
        notification = Notification.objects.get(event__type=ASSET_SHARED, user=self.user)
        self.assertTrue(notification.event.recalled)


class TestCharacterTag(APITestCase):
    def test_tag_user(self):
        self.login(self.user)
        char = CharacterFactory.create(user=self.user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/tag/'.format(self.user.username, char.name),
            {'tags': ['sexy', 'vix']}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        char.refresh_from_db()
        self.assertEqual(sorted(list(char.tags.all().values_list('name', flat=True))), ['sexy', 'vix'])


class TestAssetTag(APITestCase):
    def test_tag_user(self):
        self.login(self.user)
        asset = ImageAssetFactory.create(owner=self.user)
        response = self.client.post(
            '/api/profiles/v1/asset/{}/tag/'.format(asset.id),
            {'tags': ['sexy', 'vix']}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        asset.refresh_from_db()
        self.assertEqual(sorted(list(asset.tags.all().values_list('name', flat=True))), ['sexy', 'vix'])


class TestTagCharacter(APITestCase):
    def test_tag_character(self):
        self.login(self.user)
        character = CharacterFactory.create(name='Gooby')
        asset = ImageAssetFactory.create()
        response = self.client.post(
            '/api/profiles/v1/asset/{}/tag-characters/'.format(asset.id),
            {'characters': [character.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        asset.refresh_from_db()
        self.assertEqual(asset.characters.all().count(), 1)
        self.assertEqual(asset.characters.all()[0], character)


class TestShareCharacter(APITestCase):
    def test_logged_in(self):
        character = CharacterFactory.create()
        self.login(character.user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/share/'.format(character.user.username, character.name),
            {'shared_with': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], character.id)
        character.refresh_from_db()
        self.assertEqual(
            sorted(list(character.shared_with.all().values_list('id', flat=True))), [self.user.id, self.user2.id]
        )
        notification1 = Notification.objects.get(event__type=CHAR_SHARED, user=self.user)
        notification2 = Notification.objects.get(event__type=CHAR_SHARED, user=self.user)
        self.assertEqual(notification1.event.data['user'], character.user.id)
        self.assertEqual(notification2.event, notification1.event)
        self.assertEqual(notification1.event.data['character'], character.id)
        self.assertEqual(notification2.event, notification1.event)

    def test_not_logged_in(self):
        character = CharacterFactory.create()
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/share/'.format(character.user.username, character.name),
            {'shared_with': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logged_in_different_user(self):
        character = CharacterFactory.create()
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/share/'.format(character.user.username, character.name),
            {'shared_with': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_logged_in(self):
        character = CharacterFactory.create()
        character.shared_with.add(self.user, self.user2, character.user)
        self.login(character.user)
        response = self.client.delete(
            '/api/profiles/v1/account/{}/characters/{}/share/'.format(character.user.username, character.name),
            {'shared_with': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], character.id)
        character.refresh_from_db()
        self.assertEqual(list(character.shared_with.all().values_list('id', flat=True)), [character.user.id])

    def test_delete_not_logged_in(self):
        character = CharacterFactory.create()
        character.shared_with.add(self.user, self.user2, character.user)
        response = self.client.delete(
            '/api/profiles/v1/account/{}/characters/{}/share/'.format(character.user.username, character.name),
            {'shared_with': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_wrong_user(self):
        character = CharacterFactory.create()
        character.shared_with.add(self.user, self.user2, character.user)
        self.login(UserFactory.create())
        response = self.client.delete(
            '/api/profiles/v1/account/{}/characters/{}/share/'.format(character.user.username, character.name),
            {'shared_with': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_other_user_tagged(self):
        character = CharacterFactory.create()
        character.shared_with.add(self.user, self.user2, character.user)
        self.login(self.user)
        response = self.client.delete(
            '/api/profiles/v1/account/{}/characters/{}/share/'.format(character.user.username, character.name),
            {'shared_with': [self.user.id, self.user2.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_notification_deleted(self):
        character = CharacterFactory.create()
        self.login(character.user)
        self.client.post(
            '/api/profiles/v1/account/{}/characters/{}/share/'.format(character.user.username, character.name),
            {'shared_with': [self.user.id]}
        )
        self.client.delete(
            '/api/profiles/v1/account/{}/characters/{}/share/'.format(character.user.username, character.name),
            {'shared_with': [self.user.id]}
        )
        notification = Notification.objects.get(event__type=CHAR_SHARED, user=self.user)
        self.assertTrue(notification.event.recalled)


class TestWatch(APITestCase):
    def test_watch_user(self):
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/watch/'.format(self.user2.username),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.watching.all().count(), 1)
        self.assertEqual(self.user.watching.all()[0], self.user2)
        event_types = [NEW_CHARACTER, NEW_PRODUCT]
        for event_type in event_types:
            logger.info('Checking {}'.format(event_type))
            self.assertTrue(Subscription.objects.filter(
                subscriber=self.user,
                content_type=ContentType.objects.get_for_model(self.user2),
                object_id=self.user2.id,
                type=event_type
            ).exists())
        response = self.client.post(
            '/api/profiles/v1/account/{}/watch/'.format(self.user2.username),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.watching.all().count(), 0)
        for event_type in event_types:
            logger.info('Checking {}'.format(event_type))
            self.assertFalse(Subscription.objects.filter(
                subscriber=self.user,
                content_type=ContentType.objects.get_for_model(self.user2),
                object_id=self.user2.id,
                type=event_type
            ).exists())

    def test_watch_user_no_login(self):
        response = self.client.post(
            '/api/profiles/v1/account/{}/watch/'.format(self.user2.username),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestFavorite(APITestCase):
    def test_favorite_asset(self):
        asset = ImageAssetFactory.create()
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/asset/{}/favorite/'.format(asset.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.favorites.all().count(), 1)
        self.assertEqual(self.user.favorites.all()[0], asset)
        response = self.client.post(
            '/api/profiles/v1/asset/{}/favorite/'.format(asset.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.favorites.all().count(), 0)

    def test_favorite_asset_hidden_failure(self):
        asset = ImageAssetFactory.create(private=True)
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/asset/{}/favorite/'.format(asset.id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_favorite_asset_hidden_shared(self):
        asset = ImageAssetFactory.create(private=True)
        asset.shared_with.add(self.user)
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/asset/{}/favorite/'.format(asset.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.favorites.all().count(), 1)
        self.assertEqual(self.user.favorites.all()[0], asset)
        response = self.client.post(
            '/api/profiles/v1/asset/{}/favorite/'.format(asset.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.favorites.all().count(), 0)

    def test_favorite_asset_no_login(self):
        asset = ImageAssetFactory.create()
        response = self.client.post(
            '/api/profiles/v1/asset/{}/favorite/'.format(asset.id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestPrivateMessages(APITestCase):
    def test_create_message(self):
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/messages/sent/'.format(self.user.username),
            {
                'subject': 'This is a test',
                'body': 'O hai',
                'recipients': [self.user2.id]
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        message_id = response.data['id']
        response = self.client.get(
            '/api/profiles/v1/messages/{}/'.format(message_id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['body'], 'O hai')
        self.assertEqual(response.data['subject'], 'This is a test')
        self.assertEqual(response.data['recipients'][0]['id'], self.user2.id)
        self.assertEqual(response.data['sender']['id'], self.user.id)

        self.login(self.user2)
        response = self.client.get(
            '/api/profiles/v1/messages/{}/'.format(message_id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['body'], 'O hai')
        self.assertEqual(response.data['subject'], 'This is a test')
        self.assertEqual(response.data['recipients'][0]['id'], self.user2.id)
        self.assertEqual(response.data['sender']['id'], self.user.id)

        user3 = UserFactory.create()
        self.login(user3)
        response = self.client.get(
            '/api/profiles/v1/messages/{}/'.format(message_id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        subscriptions = Subscription.objects.filter(type=NEW_PM)
        self.assertEqual(subscriptions.count(), 1)
        self.assertEqual(subscriptions[0].subscriber, self.user2)

        subscriptions = Subscription.objects.filter(
            type=COMMENT, content_type=ContentType.objects.get_for_model(Message),
            object_id=message_id
        )
        self.assertEqual(subscriptions.count(), 2)
        self.assertTrue(subscriptions.filter(subscriber=self.user).exists())
        self.assertTrue(subscriptions.filter(subscriber=self.user2).exists())

    def test_list_from(self):
        relationships = [MessageRecipientRelationshipFactory.create(message__sender=self.user) for _ in range(3)]
        self.login(self.user)
        response = self.client.get('/api/profiles/v1/account/{}/messages/sent/'.format(self.user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(relationships))
        for relationship in relationships:
            self.assertIDInList(relationship.message, response.data['results'])

        self.login(self.user2)
        response = self.client.get('/api/profiles/v1/account/{}/messages/sent/'.format(self.user.username))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.login(self.staffer)
        response = self.client.get('/api/profiles/v1/account/{}/messages/sent/'.format(self.user.username))
        # Even staffers can't just go browsing.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_to(self):
        relationships = [MessageRecipientRelationshipFactory.create(user=self.user) for _ in range(3)]
        self.login(self.user)
        response = self.client.get('/api/profiles/v1/account/{}/messages/inbox/'.format(self.user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(relationships))
        for relationship in relationships:
            self.assertIDInList(relationship.message, response.data['results'])

        self.login(self.user2)
        response = self.client.get('/api/profiles/v1/account/{}/messages/inbox/'.format(self.user.username))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.login(self.staffer)
        response = self.client.get('/api/profiles/v1/account/{}/messages/inbox/'.format(self.user.username))
        # Even staffers can't just go browsing.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_leave_conversation(self):
        # The view creates the subscriptions, so use it for this test.
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/account/{}/messages/sent/'.format(self.user.username),
            {
                'subject': 'This is a test',
                'body': 'O hai',
                'recipients': [self.user2.id]
            }
        )
        message = Message.objects.get(id=response.data['id'])
        subscriptions = Subscription.objects.filter(
            type=COMMENT, content_type=ContentType.objects.get_for_model(Message),
            object_id=message.id
        )
        self.assertEqual(subscriptions.count(), 2)

        self.login(self.user)
        response = self.client.post('/api/profiles/v1/messages/{}/leave/'.format(message.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        subscriptions = Subscription.objects.filter(
            type=COMMENT, content_type=ContentType.objects.get_for_model(Message),
            object_id=message.id
        )
        self.assertEqual(subscriptions.count(), 1)

        message.refresh_from_db()
        self.assertTrue(message.sender_left)
        self.login(self.user2)
        response = self.client.post('/api/profiles/v1/messages/{}/leave/'.format(message.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRaises(Message.DoesNotExist, Message.objects.get, id=message.id)

        subscriptions = Subscription.objects.filter(
            type=COMMENT, content_type=ContentType.objects.get_for_model(Message),
            object_id=message.id
        )
        self.assertEqual(subscriptions.count(), 0)

        subscriptions = Subscription.objects.filter(
            type=NEW_PM, content_type=ContentType.objects.get_for_model(Message),
            object_id=message.id
        )
        self.assertEqual(subscriptions.count(), 0)
