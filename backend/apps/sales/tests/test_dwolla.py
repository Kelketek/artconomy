from decimal import Decimal
from unittest.mock import Mock, patch, PropertyMock

from django.test import TestCase, override_settings

from freezegun import freeze_time
from moneyed import Money
from rest_framework.exceptions import ValidationError

from apps.lib.models import ref_for_instance
from apps.profiles.tests.factories import UserFactory
from apps.sales.apis import DwollaContext
from apps.sales.dwolla import make_dwolla_account, add_bank_account, destroy_bank_account, initiate_withdraw, \
    perform_transfer
from apps.sales.models import BankAccount, TransactionRecord, COMPLETED, IN_PROGRESS, Deliverable
from apps.sales.tests.factories import BankAccountFactory, TransactionRecordFactory,  DeliverableFactory


@patch('apps.sales.apis.DwollaContext.dwolla_api', new_callable=PropertyMock)
class DwollaTestCase(TestCase):
    @patch('apps.sales.dwolla.get_client_ip')
    def test_make_dwolla_account(self, mock_get_client_ip, mock_api):
        request = Mock()
        user = UserFactory.create(email='test@example.com')
        mock_get_client_ip.return_value = ('100.0.0.0', True)
        mock_api.return_value.post.return_value.headers = {'location': 'http://example.com'}
        make_dwolla_account(request, user, 'Jim', 'Bob')
        mock_api.return_value.post.assert_called_with(
            'customers', {
                'firstName': 'Jim',
                'lastName': 'Bob',
                'type': 'receive-only',
                'email': 'test@example.com',
                'ipAddress': '100.0.0.0'
            }
        )
        user.refresh_from_db()
        self.assertEqual(user.artist_profile.dwolla_url, 'http://example.com')

    def test_make_dwolla_url_exists(self, mock_api):
        request = Mock()
        user = UserFactory.create()
        user.artist_profile.dwolla_url = 'http://example.com'
        user.artist_profile.save()
        self.assertEqual(make_dwolla_account(request, user, 'Jim', 'Bob'), 'http://example.com')
        mock_api.assert_not_called()

    def test_add_bank_account(self, mock_api):
        user = UserFactory.create(username='testuser')
        user.artist_profile.dwolla_url = 'http://example.com'
        user.artist_profile.save()
        mock_api.return_value.post.return_value.headers = {'location': 'http://example.com/funding/1'}
        add_bank_account(user, '12345678', '1111', BankAccount.CHECKING)
        mock_api.return_value.post.assert_called_with(
            'http://example.com/funding-sources', {
                'routingNumber': '1111',
                'accountNumber': '12345678',
                'bankAccountType': 'checking',
                'name': 'testuser (ID: {}) - Checking 5678'.format(user.id)
            }
        )
        BankAccount.objects.get(
            user=user, type=BankAccount.CHECKING, last_four='5678', deleted=False, url='http://example.com/funding/1'
        )

    def test_destroy_bank_account(self, mock_api):
        account = BankAccountFactory.create()
        destroy_bank_account(account)
        mock_api.return_value.post.assert_called_with(
            account.url, {'removed': True}
        )

    def test_initiate_withdraw_low_balance(self, _mock_api):
        account = BankAccountFactory.create()
        self.assertRaises(ValidationError, initiate_withdraw, account.user, account, Money('5.00', 'USD'), False)

    @patch('apps.sales.dwolla.account_balance')
    def test_initiate_withdraw(self, mock_account_balance, _mock_api):
        account = BankAccountFactory.create(url='http://whatever.com/')
        included_deliverable = DeliverableFactory.create(order__seller=account.user, status=COMPLETED)
        self.assertFalse(included_deliverable.payout_sent)
        unincluded_deliverables = [
            DeliverableFactory.create(order__seller=account.user, status=IN_PROGRESS),
            DeliverableFactory.create(status=IN_PROGRESS),
        ]
        mock_account_balance.return_value = Decimal('10.00')
        record, deliverables = initiate_withdraw(account.user, account, Money('5.00', 'USD'), False)
        self.assertEqual(record.status, TransactionRecord.PENDING)
        self.assertEqual(record.amount, Money('5.00', 'USD'))
        self.assertEqual(record.targets.first().target, account)
        self.assertEqual(record.category, TransactionRecord.CASH_WITHDRAW)
        self.assertEqual(record.source, TransactionRecord.HOLDINGS)
        self.assertEqual(record.destination, TransactionRecord.BANK)
        included_deliverable.refresh_from_db()
        self.assertIn(included_deliverable, deliverables)
        unincluded_deliverables = Deliverable.objects.filter(id__in=[deliverable.id for deliverable in unincluded_deliverables])
        self.assertNotIn(unincluded_deliverables[0], deliverables)
        self.assertNotIn(unincluded_deliverables[1], deliverables)
        self.assertEqual(unincluded_deliverables.count(), 2)

    @patch('apps.sales.dwolla.account_balance')
    def test_initiate_withdraw_test_only(self, mock_account_balance, _mock_api):
        account = BankAccountFactory.create(url='http://whatever.com/')
        # Remove the post-creation hook payment record.
        TransactionRecord.objects.all().delete()
        mock_account_balance.return_value = Decimal('10.00')
        record, _deliverables = initiate_withdraw(account.user, account, Money('5.00', 'USD'), True)
        self.assertIsNone(record)
        self.assertEqual(TransactionRecord.objects.all().count(), 0)

    @override_settings(DWOLLA_FUNDING_SOURCE_KEY='http://someplace.com/')
    def test_perform_transfer(self, mock_api):
        account = BankAccountFactory.create(url='http://whatever.com/')
        record = TransactionRecordFactory.create(
            category=TransactionRecord.CASH_WITHDRAW,
            status=TransactionRecord.PENDING,
            amount=Money('5.00', 'USD'),
            source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK,
        )
        record.targets.add(ref_for_instance(account))
        mock_api.return_value.post.return_value.headers = {'location': 'http://transfers/123'}
        perform_transfer(record, Deliverable.objects.none())
        mock_api.return_value.post.assert_called_with(
            'transfers', {
                '_links': {
                    'source': {
                        'href': 'http://someplace.com/'
                    },
                    'destination': {
                        'href': 'http://whatever.com/'
                    }
                },
                'amount': {
                    'currency': 'USD',
                    'value': '5.00',
                },
                'metadata': {
                    'customerId': str(account.user.id),
                    'notes': 'Disbursement'
                }
            }
        )
        record.refresh_from_db()
        self.assertEqual(record.status, TransactionRecord.PENDING)
        self.assertIn('123', record.remote_ids)

    def test_perform_transfer_failure(self, mock_api):
        account = BankAccountFactory.create(url='http://whatever.com/')
        deliverable = DeliverableFactory.create()
        record = TransactionRecordFactory.create(
            category=TransactionRecord.CASH_WITHDRAW,
            status=TransactionRecord.PENDING,
            amount=Money('5.00', 'USD'),
            source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK,
            remote_ids=['N/A'],
        )
        record.targets.add(ref_for_instance(account), ref_for_instance(deliverable))
        mock_api.return_value.post.side_effect = ValueError()
        self.assertRaises(ValueError, perform_transfer, record, Deliverable.objects.none())
        record.refresh_from_db()
        self.assertEqual(record.remote_ids, ['N/A'])
        self.assertEqual(record.status, TransactionRecord.FAILURE)


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
