from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.profiles.models import Character, ImageAsset
from apps.lib.abstract_models import MATURE, ADULT
from apps.profiles.tests.factories import UserFactory, CharacterFactory, ImageAssetFactory
from apps.profiles.tests.helpers import gen_characters, serialize_char, gen_image


class APITestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = UserFactory.create()
        self.user2 = UserFactory.create()
        self.staffer = UserFactory.create(is_staff=True)

    def login(self, user):
        result = self.client.login(email=user.email, password='Test')
        self.assertIs(result, True)


class CharacterAPITestCase(APITestCase):
    def test_character_listing(self):
        characters = gen_characters(self.user)
        response = self.client.get('/api/profiles/v1/{}/characters/'.format(self.user.username))
        self.assertEqual(len(response.data['results']), 5)
        for key, value in characters.items():
            self.assertIn(
                serialize_char(key, value),
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
        self.assertNotIn(serialize_char(private_character, characters[private_character]), response.data['results'])

        # Should fail for unprivileged user
        self.login(self.user2)
        self.assertEqual(len(response.data['results']), 4)
        self.assertNotIn(serialize_char(private_character, characters[private_character]), response.data['results'])

    def test_list_private_for_privileged(self):
        characters = gen_characters(self.user)
        private_character = list(characters.keys())[0]
        private_character.private = True
        private_character.save()

        # Should work for character owner.
        self.login(self.user)
        response = self.client.get('/api/profiles/v1/{}/characters/'.format(self.user.username))
        self.assertEqual(len(response.data['results']), 5)
        self.assertIn(serialize_char(private_character, characters[private_character]), response.data['results'])

        # Should work for staff, too.
        self.login(self.staffer)
        response = self.client.get('/api/profiles/v1/{}/characters/'.format(self.user.username))
        self.assertEqual(len(response.data['results']), 5)
        self.assertIn(serialize_char(private_character, characters[private_character]), response.data['results'])

    def test_new_character(self):
        self.login(self.user)
        response = self.client.post(
            '/profiles/api/{}/characters/'.format(self.user.username), {
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
            '/api/profiles/v1/{}/characters/{}/asset/'.format(self.user.username, char.name),
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
            '/api/profiles/v1/{}/characters/{}/asset/'.format(self.user.username, char.name),
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
            '/api/profiles/v1/{}/characters/{}/asset/'.format(self.user.username, char.name),
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
            '/api/profiles/v1/{}/characters/{}/asset/{}/'.format(self.user.username, char.name, asset.id),
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
            '/api/profiles/v1/{}/characters/{}/asset/{}/'.format(self.user.username, char.name, asset.id),
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
            '/api/profiles/v1/{}/characters/{}/asset/{}/'.format(self.user.username, char.name, asset.id),
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

    def test_credentials_post_username(self):
        self.login(self.user)
        response = self.client.patch(
            '/api/profiles/v1/{}/credentials/'.format(self.user.username),
            {'username': 'NewName', 'current_password': 'Test'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'NewName')

    def test_credentials_username_no_password(self):
        self.login(self.user)
        response = self.client.patch(
            '/api/profiles/v1/{}/credentials/'.format(self.user.username),
            {'username': 'NewName'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        old_name = self.user.username
        self.user.refresh_from_db()
        self.assertEqual(old_name, self.user.username)

    def test_credentials_username_wrong_password(self):
        self.login(self.user)
        response = self.client.patch(
            '/api/profiles/v1/{}/credentials/'.format(self.user.username),
            {'username': 'NewName', 'current_password': 'password'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        old_name = self.user.username
        self.user.refresh_from_db()
        self.assertEqual(old_name, self.user.username)

    def test_credentials_change_password(self):
        self.login(self.user)
        response = self.client.patch(
            '/api/profiles/v1/{}/credentials/'.format(self.user.username),
            {
                'username': 'NewName',
                'current_password': 'Test',
                'new_password1': '1234',
                'new_password2': '1234',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('Test'))
        self.assertTrue(self.user.check_password('1234'))

    def test_credentials_test_password_mismatch(self):
        self.login(self.user)
        response = self.client.patch(
            '/api/profiles/v1/{}/credentials/'.format(self.user.username),
            {
                'username': 'NewName',
                'current_password': 'Test',
                'new_password1': '1234',
                'new_password2': '',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('1234'))
        self.assertTrue(self.user.check_password('Test'))

    def test_credentials_wrong_password(self):
        self.login(self.user)
        response = self.client.patch(
            '/api/profiles/v1/{}/credentials/'.format(self.user.username),
            {
                'username': 'NewName',
                'current_password': 'password',
                'new_password1': '1234',
                'new_password2': '1234',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('1234'))
        self.assertTrue(self.user.check_password('Test'))
