from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from mock import Mock, patch
from rest_framework import status
from rest_framework.test import APIClient

from apps.profiles.models import Character, ImageAsset
from apps.lib.abstract_models import MATURE, ADULT, GENERAL
from apps.lib.test_resources import APITestCase
from apps.profiles.tests.factories import UserFactory, CharacterFactory, ImageAssetFactory
from apps.profiles.tests.helpers import gen_characters, serialize_char, gen_image


class CharacterAPITestCase(APITestCase):
    def test_character_listing(self):
        characters = gen_characters(self.user)
        response = self.client.get('/api/profiles/v1/{}/characters/'.format(self.user.username))
        self.assertEqual(len(response.data['results']), 5)
        for key, value in characters.items():
            self.assertIn(
                serialize_char(key),
                response.data['results']
            )

    def test_no_list_private(self):
        characters = gen_characters(self.user)
        private_character = list(characters.keys())[0]
        private_character.private = True
        private_character.save()

        # Should fail for unregistered user
        response = self.client.get('/api/profiles/v1/{}/characters/'.format(self.user.username))
        self.assertEqual(len(response.data['results']), 4)
        self.assertNotIn(serialize_char(private_character), response.data['results'])

        # Should fail for unprivileged user
        self.login(self.user2)
        self.assertEqual(len(response.data['results']), 4)
        self.assertNotIn(serialize_char(private_character), response.data['results'])

    def test_list_private_for_privileged(self):
        characters = gen_characters(self.user)
        private_character = list(characters.keys())[0]
        private_character.private = True
        private_character.save()

        # Should work for character owner.
        self.login(self.user)
        response = self.client.get('/api/profiles/v1/{}/characters/'.format(self.user.username))
        self.assertEqual(len(response.data['results']), 5)
        self.assertIn(serialize_char(private_character), response.data['results'])
        # Should work for staff, too.
        self.login(self.staffer)
        response = self.client.get('/api/profiles/v1/{}/characters/'.format(self.user.username))
        self.assertEqual(len(response.data['results']), 5)
        self.assertIn(serialize_char(private_character), response.data['results'])

    def test_new_character(self):
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/{}/characters/'.format(self.user.username), {
                'name': 'Fern',
                'description': 'The best of both worlds',
                'private': True,
                'open_requests': False,
                'open_requests_restrictions': 'Must be foxy.',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        char = Character.objects.get(name='Fern')
        self.assertEqual(char.description, 'The best of both worlds')
        self.assertEqual(char.private, True)
        self.assertEqual(char.open_requests, False)
        self.assertEqual(char.open_requests_restrictions, 'Must be foxy.')

        # Should work for staffer.
        self.login(self.staffer)
        response = self.client.post(
            '/api/profiles/v1/{}/characters/'.format(self.user.username), {
                'name': 'Rain',
                'description': 'Heart breaker',
                'private': True,
                'open_requests': False,
                'open_requests_restrictions': 'Must be really foxy.',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        char = Character.objects.get(name='Rain')
        self.assertEqual(char.description, 'Heart breaker')
        self.assertEqual(char.private, True)
        self.assertEqual(char.open_requests, False)
        self.assertEqual(char.open_requests_restrictions, 'Must be really foxy.')

    def test_edit_character(self):
        self.login(self.user)
        char = CharacterFactory.create(user=self.user)
        response = self.client.patch(
            '/api/profiles/v1/{}/characters/{}/'.format(self.user.username, char.name),
            {
                'name': 'Terrence',
                'description': 'Positively foxy.'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        char.refresh_from_db()
        self.assertEqual(char.name, 'Terrence')
        self.assertEqual(char.description, 'Positively foxy.')

        # Should work for staff, too.
        self.login(self.staffer)
        response = self.client.patch(
            '/api/profiles/v1/{}/characters/{}/'.format(self.user.username, char.name),
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
            '/api/profiles/v1/{}/characters/{}/'.format(self.user.username, char.name),
            {
                'name': 'Terrence',
                'description': 'Positively foxy.'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_character(self):
        self.login(self.user)
        char = CharacterFactory.create(user=self.user)
        response = self.client.delete('/api/profiles/v1/{}/characters/{}/'.format(self.user.username, char.name))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRaises(Character.DoesNotExist, char.refresh_from_db)

        # Force recreation, then test for staff.
        char.save()
        # Verify recreation worked.
        char.refresh_from_db()

        response = self.client.delete('/api/profiles/v1/{}/characters/{}/'.format(self.user.username, char.name))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRaises(Character.DoesNotExist, char.refresh_from_db)

    def test_primary_asset(self):
        self.login(self.user)
        char = CharacterFactory.create(user=self.user)
        asset = ImageAssetFactory.create(uploaded_by=self.user)
        asset.characters.add(char)
        char.refresh_from_db()
        self.assertIsNone(char.primary_asset)

        response = self.client.post(
            '/api/profiles/v1/{}/characters/{}/asset/primary/{}/'.format(self.user.username, char.name, asset.id),
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        char.refresh_from_db()
        self.assertEqual(char.primary_asset, asset)

        # Should work for staff, too.
        asset2 = ImageAssetFactory.create(uploaded_by=self.staffer)
        asset2.characters.add(char)

        self.login(self.staffer)
        response = self.client.post(
            '/api/profiles/v1/{}/characters/{}/asset/primary/{}/'.format(self.user.username, char.name, asset2.id),
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        char.refresh_from_db()
        self.assertEqual(char.primary_asset, asset2)

    def test_primary_asset_forbidden(self):
        self.login(self.user2)
        char = CharacterFactory.create(user=self.user)
        asset = ImageAssetFactory.create(uploaded_by=self.user)
        asset.characters.add(char)
        char.refresh_from_db()
        self.assertIsNone(char.primary_asset)

        response = self.client.post(
            '/api/profiles/v1/{}/characters/{}/asset/primary/{}/'.format(self.user.username, char.name, asset.id),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_asset_upload(self):
        self.login(self.user)
        char = CharacterFactory.create(user=self.user)
        uploaded = SimpleUploadedFile('bloo-oo.jpg', gen_image())
        response = self.client.post(
            '/api/profiles/v1/{}/characters/{}/assets/'.format(self.user.username, char.name),
            {
                'title': 'Blooo',
                'caption': "A sea of blue.",
                'private': False,
                'rating': ADULT,  # Such a sexy color!
                'file': uploaded,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        asset = ImageAsset.objects.get(characters__name=char.name)
        self.assertEqual(asset.title, 'Blooo')
        self.assertEqual(asset.caption, 'A sea of blue.')
        self.assertFalse(asset.private)
        self.assertEqual(asset.rating, ADULT)
        self.assertIn('bloo-oo', asset.file.url)
        asset.delete()

        # Should work for staffer, too.
        self.login(self.staffer)
        uploaded = SimpleUploadedFile('gree-een.jpg', gen_image(color='green'))
        response = self.client.post(
            '/api/profiles/v1/{}/characters/{}/assets/'.format(self.user.username, char.name),
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

    def test_asset_upload_forbidden(self):
        self.login(self.user2)
        char = CharacterFactory.create(user=self.user)
        uploaded = SimpleUploadedFile('bloo-oo.jpg', gen_image())
        response = self.client.post(
            '/api/profiles/v1/{}/characters/{}/assets/'.format(self.user.username, char.name),
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
        asset = ImageAssetFactory.create(uploaded_by=self.user)
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
        asset = ImageAssetFactory.create(uploaded_by=self.user)
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
            '/api/profiles/v1/{}/settings/'.format(self.user.username), {
                'rating': ADULT,
                'max_load': 5,
                'use_load_tracker': False,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                'commissions_closed': True,
                'rating': ADULT,
                'sfw_mode': False,
                'max_load': 5
            }
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.rating, ADULT)

    def test_settings_wrong_user(self):
        self.login(UserFactory.create())
        response = self.client.patch(
            '/api/profiles/v1/{}/settings/'.format(self.user.username), {
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.user.refresh_from_db()
        self.assertEqual(self.user.rating, GENERAL)

    def test_credentials_post_username(self):
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/{}/credentials/'.format(self.user.username),
            {'username': 'NewName', 'current_password': 'Test'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'NewName')

    def test_credentials_username_taken(self):
        self.login(self.user)
        conflicting = UserFactory.create()
        response = self.client.post(
            '/api/profiles/v1/{}/credentials/'.format(self.user.username),
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
            '/api/profiles/v1/{}/credentials/'.format(self.user.username),
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
            '/api/profiles/v1/{}/credentials/'.format(self.user.username),
            {'current_password': 'Test', 'email': 'changed_email@example.com'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'changed_email@example.com')

    def test_credentials_email_taken(self):
        self.login(self.user)
        conflicting = UserFactory.create()
        response = self.client.post(
            '/api/profiles/v1/{}/credentials/'.format(self.user.username),
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
            '/api/profiles/v1/{}/credentials/'.format(self.user.username),
            {'username': 'NewName'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        old_name = self.user.username
        self.user.refresh_from_db()
        self.assertEqual(old_name, self.user.username)

    def test_credentials_username_wrong_password(self):
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/{}/credentials/'.format(self.user.username),
            {'username': 'NewName', 'current_password': 'password'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        old_name = self.user.username
        self.user.refresh_from_db()
        self.assertEqual(old_name, self.user.username)

    def test_credentials_change_password(self):
        self.login(self.user)
        response = self.client.post(
            '/api/profiles/v1/{}/credentials/'.format(self.user.username),
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
            '/api/profiles/v1/{}/credentials/'.format(self.user.username),
            {
                'current_password': 'password',
                'new_password': '1234TestABC',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('1234'))
        self.assertTrue(self.user.check_password('Test'))


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


@override_settings(
    DWOLLA_KEY='test_key', DWOLLA_SECRET='test_secret', SANDBOX_APIS=True,
    DEFAULT_DOMAIN='wat.com', DEFAULT_PROTOCOL='https',
)
class RegisterDwollaTestCase(TestCase):
    @patch('requests.post')
    def test_register_dwolla(self, mock_post):
        user = UserFactory.create(email='test@example.com', password='123')
        self.client.login(email='test@example.com', password='123')
        mock_response = Mock()
        mock_post.return_value = mock_response
        mock_response.json.return_value = {
            '_links': {'account': {'href': 'https://example.com/account_id_here'}}
        }
        response = self.client.get('/api/profiles/v1/register_dwolla/?code=TestCode')
        user.refresh_from_db()
        mock_post.assert_called_with(
            "https://sandbox.dwolla.com/oauth/v2/token",
            json={
                'client_id': 'test_key',
                'client_secret': 'test_secret',
                'code': 'TestCode',
                'grant_type': 'authorization_code',
                'redirect_uri': 'https://wat.com/api/profiles/v1/register_dwolla/'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/profiles/{}/'.format(user.username))
        self.assertEqual(user.dwolla_url, 'https://example.com/account_id_here')

    @patch('requests.post')
    def test_fail_on_anon(self, mock_post):
        response = self.client.get('/api/profiles/v1/register_dwolla/?code=TestCode')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, b'Please log in and then re-attempt to link your account.')
        self.assertFalse(mock_post.called)


class TestCharacterSearch(APITestCase):
    def test_query_not_logged_in(self):
        char = CharacterFactory.create(name='Terrybutt')
        char2 = CharacterFactory.create(name='Terrencia', open_requests=False)
        CharacterFactory.create(name='Terrence', private=True)
        CharacterFactory.create(name='wutwut')
        CharacterFactory.create(name='Stuff')
        response = self.client.get('/api/profiles/v1/search/character/?q=terr')
        self.assertEqual(len(response.data['results']), 2)
        self.assertIn(serialize_char(char), response.data['results'])
        self.assertIn(serialize_char(char2), response.data['results'])

    def test_query_logged_in(self):
        visible = CharacterFactory.create(name='Terrybutt', user=self.user)
        visible2 = CharacterFactory.create(name='Terrencia', user=self.user2, open_requests=False)
        visible_private = CharacterFactory.create(name='Terrence', private=True, user=self.user)
        CharacterFactory.create(name='Terryvix', private=True, user=self.user2)
        CharacterFactory.create(name='Stuff')
        self.login(self.user)
        response = self.client.get('/api/profiles/v1/search/character/?q=terr')
        self.assertEqual(len(response.data['results']), 3)
        self.assertIn(serialize_char(visible), response.data['results'])
        self.assertIn(serialize_char(visible2), response.data['results'])
        self.assertIn(serialize_char(visible_private), response.data['results'])
        self.assertEqual(serialize_char(visible2), response.data['results'][2])

    def test_query_logged_in_commission(self):
        visible = CharacterFactory.create(name='Terrybutt', user=self.user)
        visible2 = CharacterFactory.create(name='Terrencia', user=self.user2)
        visible_private = CharacterFactory.create(name='Terrence', private=True, user=self.user)
        CharacterFactory.create(name='Terryvix', private=True, user=self.user2)
        CharacterFactory.create(name='Terrible', open_requests=False, user=self.user2)
        CharacterFactory.create(name='Stuff')
        self.login(self.user)
        response = self.client.get('/api/profiles/v1/search/character/?q=terr&new_order=1')
        self.assertEqual(len(response.data['results']), 3)
        self.assertIn(serialize_char(visible), response.data['results'])
        self.assertIn(serialize_char(visible_private), response.data['results'])
        self.assertEqual(serialize_char(visible2), response.data['results'][2])

    def test_query_logged_in_staffer(self):
        visible = CharacterFactory.create(name='Terrybutt', user=self.user)
        visible2 = CharacterFactory.create(name='Terrencia', user=self.user2)
        visible_private = CharacterFactory.create(name='Terrence', private=True, user=self.user)
        CharacterFactory.create(name='Terryvix', private=True, user=self.user2)
        CharacterFactory.create(name='Terrible', open_requests=False, user=self.user2)
        CharacterFactory.create(name='Stuff')
        self.login(self.staffer)
        response = self.client.get('/api/profiles/v1/search/character/?q=terr&new_order=1&user={}'.format(self.user.id))
        self.assertEqual(len(response.data['results']), 3)
        self.assertIn(serialize_char(visible), response.data['results'])
        self.assertIn(serialize_char(visible_private), response.data['results'])
        self.assertEqual(serialize_char(visible2), response.data['results'][2])