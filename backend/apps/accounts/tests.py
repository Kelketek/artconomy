from django.test import TestCase, override_settings

# Create your tests here.
from mock import patch, Mock

from apps.profiles.tests.factories import UserFactory


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
        response = self.client.get('/accounts/register_dwolla/?code=TestCode')
        user.refresh_from_db()
        mock_post.assert_called_with(
            "https://sandbox.dwolla.com/oauth/v2/token",
            json={
                'client_id': 'test_key',
                'client_secret': 'test_secret',
                'code': 'TestCode',
                'grant_type': 'authorization_code',
                'redirect_uri': 'https://wat.com/accounts/register_dwolla/'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/profiles/{}/'.format(user.username))
        self.assertEqual(user.dwolla_url, 'https://example.com/account_id_here')

    @patch('requests.post')
    def test_fail_on_anon(self, mock_post):
        response = self.client.get('/accounts/register_dwolla/?code=TestCode')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, b'Please log in and then re-attempt to link your account.')
        self.assertFalse(mock_post.called)
