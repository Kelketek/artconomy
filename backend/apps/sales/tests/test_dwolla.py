from unittest.mock import Mock, patch, PropertyMock

from django.test import TestCase, override_settings

from freezegun import freeze_time

from apps.sales.apis import DwollaContext
from apps.sales.dwolla import destroy_bank_account
from apps.sales.tests.factories import BankAccountFactory


@patch('apps.sales.apis.DwollaContext.dwolla_api', new_callable=PropertyMock)
class DwollaTestCase(TestCase):

    def test_destroy_bank_account(self, mock_api):
        account = BankAccountFactory.create()
        destroy_bank_account(account)
        mock_api.return_value.post.assert_called_with(
            account.url, {'removed': True}
        )


TEST_VALUES = (
    ('5.00', '.05'),
    ('8.45', '.05'),
    ('47.50', '.24'),
    ('37.90', '.19'),
    ('20.65', '.10'),
    ('29.85', '.15'),
    ('24.78', '.12'),
    ('49.85', '.25'),
    ('111.25', '.56'),
    ('13.05', '.07'),
    ('92.62', '.46'),
    ('103.18', '.52'),
    ('23.50', '.12'),
    ('13.90', '.07'),
    # Nice.
    ('137.74', '.69'),
    ('16.52', '.08'),
    ('33.04', '.17'),
    ('71.50', '.36'),
    ('1000', '5'),
    ('1024', '5'),
    ('100000', '5')
)


@patch('apps.sales.apis.client')
class TestDwollaContext(TestCase):
    @override_settings(DWOLLA_FUNDING_SOURCE_KEY='https://example.com/123/')
    def test_funding_url(self, _mock_client):
        dwolla = DwollaContext()
        self.assertEqual(dwolla.funding_url, 'https://example.com/123/')

    def test_account_url(self, mock_client):
        dwolla = DwollaContext()
        mock_client.Auth.client.return_value.get.return_value.body = {
            '_links': {'account': {'href': 'https://wheee.com/'}}
        }
        self.assertEqual(dwolla.account_url, 'https://wheee.com/')

    def test_dwolla_caches_token(self, mock_client):
        dwolla = DwollaContext()
        target = Mock()
        mock_client.Auth.client.return_value = target
        self.assertIs(dwolla.dwolla_api, target)
        mock_client.Auth.client.return_value = Mock()
        self.assertIs(dwolla.dwolla_api, target)

    @freeze_time('2019-08-01')
    def test_dwolla_expires_token(self, mock_client):
        dwolla = DwollaContext()
        target = Mock()
        mock_client.Auth.client.return_value = target
        self.assertIs(dwolla.dwolla_api, target)
        new_target = Mock()
        mock_client.Auth.client.return_value = new_target
        with freeze_time('2019-08-02'):
            self.assertIs(dwolla.dwolla_api, new_target)

    def test_dwolla_context(self, mock_client):
        dwolla = DwollaContext()
        target = Mock()
        mock_client.Auth.client.return_value = target
        with dwolla as api:
            self.assertIs(api, target)
