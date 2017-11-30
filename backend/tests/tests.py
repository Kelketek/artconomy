from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.profiles.tests.factories import UserFactory


class ValidatorChecks(TestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()

    def test_username_validator_taken(self):
        UserFactory.create(username='testola')
        response = self.client.get('/api/form-validators/username/', {'username': 'testola'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['available'])

    def test_username_validator_bad_request(self):
        response = self.client.get('/api/form-validators/username/', format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'No username provided.')

    def test_username_validator_available(self):
        response = self.client.get('/api/form-validators/username/', {'username': 'stuff'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['available'])
