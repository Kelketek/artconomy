from unittest.mock import Mock, patch, PropertyMock

from django.test import TestCase, override_settings
from moneyed import Money, Decimal
from rest_framework.exceptions import ValidationError

from apps.profiles.tests.factories import UserFactory
from apps.sales.dwolla import make_dwolla_account, add_bank_account, destroy_bank_account, initiate_withdraw, \
    perform_transfer, refund_transfer
from apps.sales.models import BankAccount, PaymentRecord
from apps.sales.tests.factories import BankAccountFactory, PaymentRecordFactory


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
                'email': 'test@example.com',
                'ipAddress': '100.0.0.0'
            }
        )
        user.refresh_from_db()
        self.assertEqual(user.dwolla_url, 'http://example.com')

    def test_make_dwolla_url_exists(self, mock_api):
        request = Mock()
        user = UserFactory.create(dwolla_url='http://example.com')
        self.assertEqual(make_dwolla_account(request, user, 'Jim', 'Bob'), 'http://example.com')
        mock_api.assert_not_called()

    def test_add_bank_account(self, mock_api):
        user = UserFactory.create(dwolla_url='http://example.com', username='testuser')
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

    @patch('apps.sales.dwolla.available_balance')
    def test_initiate_withdraw(self, mock_account_balance, _mock_api):
        account = BankAccountFactory.create(url='http://whatever.com/')
        mock_account_balance.return_value = Decimal('10.00')
        record = initiate_withdraw(account.user, account, Money('5.00', 'USD'), False)
        self.assertEqual(record.status, PaymentRecord.SUCCESS)
        self.assertEqual(record.amount, Money('5.00', 'USD'))
        self.assertEqual(record.target, account)
        self.assertEqual(record.type, PaymentRecord.DISBURSEMENT_SENT)
        self.assertEqual(record.source, PaymentRecord.ACCOUNT)
        self.assertEqual(record.txn_id, 'N/A')

    @patch('apps.sales.dwolla.available_balance')
    def test_initiate_withdraw_test_only(self, mock_account_balance, _mock_api):
        account = BankAccountFactory.create(url='http://whatever.com/')
        mock_account_balance.return_value = Decimal('10.00')
        record = initiate_withdraw(account.user, account, Money('5.00', 'USD'), True)
        self.assertIsNone(record)
        self.assertEqual(PaymentRecord.objects.all().count(), 0)

    @override_settings(DWOLLA_FUNDING_SOURCE_KEY='http://someplace.com/')
    def test_perform_transfer(self, mock_api):
        account = BankAccountFactory.create(url='http://whatever.com/')
        record = PaymentRecordFactory.create(
            type=PaymentRecord.DISBURSEMENT_SENT,
            status=PaymentRecord.SUCCESS,
            amount=Money('5.00', 'USD'),
            source=PaymentRecord.ACCOUNT,
            target=account
        )
        mock_api.return_value.post.return_value.headers = {'location': 'http://transfers/123'}
        perform_transfer(record)
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
        self.assertEqual(record.status, PaymentRecord.SUCCESS)
        self.assertEqual(record.txn_id, '123')

    def test_perform_transfer_failure(self, mock_api):
        account = BankAccountFactory.create(url='http://whatever.com/')
        record = PaymentRecordFactory.create(
            type=PaymentRecord.DISBURSEMENT_SENT,
            status=PaymentRecord.SUCCESS,
            amount=Money('5.00', 'USD'),
            source=PaymentRecord.ACCOUNT,
            target=account,
            txn_id='N/A'
        )
        mock_api.return_value.post.side_effect = ValueError()
        self.assertRaises(ValueError, perform_transfer, record)
        record.refresh_from_db()
        self.assertEqual(record.txn_id, 'N/A')
        self.assertEqual(record.status, PaymentRecord.FAILURE)


class TestRefundTransfer(TestCase):
    def test_refund_transfer(self):
        record = PaymentRecordFactory.create(
            payee=None,
            payer=UserFactory.create(),
            type=PaymentRecord.DISBURSEMENT_SENT,
            source=PaymentRecord.ACCOUNT,
            txn_id='1234'
        )
        refund_transfer(record)
        PaymentRecord.objects.get(type=PaymentRecord.DISBURSEMENT_RETURNED, txn_id='1234')
        self.assertEqual(PaymentRecord.objects.all().count(), 2)

    def test_refund_transfer_no_duplicates(self):
        record = PaymentRecordFactory.create(
            payee=None,
            payer=UserFactory.create(),
            type=PaymentRecord.DISBURSEMENT_SENT,
            source=PaymentRecord.ACCOUNT,
            txn_id='1234',
            finalized=False,
        )
        refund_transfer(record)
        PaymentRecord.objects.get(type=PaymentRecord.DISBURSEMENT_RETURNED, txn_id='1234')
        self.assertEqual(PaymentRecord.objects.all().count(), 2)
        refund_transfer(record)
        self.assertEqual(PaymentRecord.objects.all().count(), 2)
