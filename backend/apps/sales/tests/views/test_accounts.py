from decimal import Decimal
from unittest.mock import patch

from moneyed import Money
from rest_framework import status

from apps.lib.test_resources import MethodAccessMixin, PermissionsTestCase, SignalsDisabledMixin, APITestCase
from apps.profiles.models import User
from apps.profiles.tests.factories import UserFactory
from apps.sales.models import TransactionRecord, BankAccount
from apps.sales.tests.factories import CreditCardTokenFactory, TransactionRecordFactory, BankAccountFactory
from apps.sales.utils import PENDING
from apps.sales.views import AccountHistory

history_passes = {**MethodAccessMixin.passes, 'get': ['user', 'staff']}


class TestAccountHistoryPermissions(PermissionsTestCase, MethodAccessMixin):
    passes = history_passes
    view_class = AccountHistory


class TestHistoryViews(SignalsDisabledMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create(username='Fox')
        self.user2 = UserFactory.create(username='Amber')
        card = CreditCardTokenFactory.create()
        [
            TransactionRecordFactory.create(
                amount=Money(amount, 'USD'),
                category=TransactionRecord.ESCROW_HOLD,
                payer=self.user2,
                payee=self.user,
                source=TransactionRecord.CARD,
                destination=TransactionRecord.ESCROW,
                card=card,
            )
            for amount in ('5.00', '10.00', '15.00')
        ]
        [
            TransactionRecordFactory.create(
                amount=Money(amount, 'USD'),
                payer=self.user,
                payee=self.user,
                source=TransactionRecord.ESCROW,
                destination=TransactionRecord.HOLDINGS,
                category=TransactionRecord.ESCROW_RELEASE,
            )
            for amount in ('5.00', '10.00')
        ]
        [
            TransactionRecordFactory.create(
                amount=Money(amount, 'USD'),
                payer=self.user,
                payee=self.user,
                card=None,
                source=TransactionRecord.HOLDINGS,
                destination=TransactionRecord.BANK,
                category=TransactionRecord.CASH_WITHDRAW,
            )
            for amount in (1, 2, 3, 4)
        ]

    def test_purchase_history(self):
        self.login(self.user)
        response = self.client.get(f'/api/sales/v1/account/{self.user.username}/transactions/?account=300')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)
        self.login(self.user2)
        response = self.client.get(f'/api/sales/v1/account/{self.user2.username}/transactions/?account=300')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)
        for result in response.data['results']:
            self.assertTrue(result['card']['id'])

    def test_escrow_history(self):
        self.login(self.user)
        response = self.client.get(f'/api/sales/v1/account/{self.user.username}/transactions/?account=302')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 5)
        for result in response.data['results']:
            self.assertIsNone(result['card'])
        self.login(self.user2)
        response = self.client.get(f'/api/sales/v1/account/{self.user2.username}/transactions/?account=302')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

    def test_available_history(self):
        self.login(self.user)
        response = self.client.get(f'/api/sales/v1/account/{self.user.username}/transactions/?account=303')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 6)
        self.login(self.user2)
        response = self.client.get(f'/api/sales/v1/account/{self.user2.username}/transactions/?account=303')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)


class TestBankAccounts(APITestCase):
    def test_bank_listing(self):
        user = UserFactory.create()
        accounts = [BankAccountFactory.create(user=user) for _ in range(3)]
        BankAccountFactory.create(user=user, deleted=True)
        [BankAccountFactory.create() for _ in range(3)]
        self.login(user)
        response = self.client.get('/api/sales/v1/account/{}/banks/'.format(user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(accounts))

    @patch('apps.sales.views.make_dwolla_account')
    @patch('apps.sales.views.add_bank_account')
    @patch('apps.sales.views.account_balance')
    def test_bank_addition(self, mock_account_balance, mock_add_bank_account, _mock_make_dwolla_account):
        user = UserFactory.create()
        self.login(user)
        mock_add_bank_account.side_effect = lambda *args, **kwargs: BankAccountFactory.create(user=user)
        mock_account_balance.return_value = Decimal('3.00')
        response = self.client.post(
            f'/api/sales/v1/account/{user.username}/banks/',
            {
                'type': BankAccount.CHECKING, 'account_number': '123434', 'routing_number': '123455666',
                'first_name': 'Jim', 'last_name': 'Bob',
            }, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_account_balance.assert_called_with(user, TransactionRecord.HOLDINGS)
        mock_add_bank_account.assert_called_with(user, '123434', '123455666', BankAccount.CHECKING)

    @patch('apps.sales.views.make_dwolla_account')
    @patch('apps.sales.views.add_bank_account')
    def test_bank_addition_insufficient_funds(self, mock_add_bank_account, _mock_make_dwolla_account):
        user = UserFactory.create()
        self.login(user)
        mock_add_bank_account.side_effect = lambda *args, **kwargs: BankAccountFactory.create(user=user)
        response = self.client.post(
            f'/api/sales/v1/account/{user.username}/banks/',
            {
                'type': BankAccount.CHECKING, 'account_number': '123434', 'routing_number': '123455666',
                'first_name': 'Jim', 'last_name': 'Bob',
            }, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'], 'You do not have sufficient balance to cover the $1.00 connection fee yet.',
        )

    @patch('apps.sales.views.make_dwolla_account')
    @patch('apps.sales.views.add_bank_account')
    @patch('apps.sales.views.account_balance')
    def test_bank_addition_already_paid_fee(self, mock_account_balance, mock_add_bank_account, _mock_make_dwolla_account):
        user = UserFactory.create()
        self.login(user)
        BankAccountFactory.create(user=user, deleted=True)
        mock_add_bank_account.side_effect = lambda *args, **kwargs: BankAccountFactory.create(user=user)
        response = self.client.post(
            f'/api/sales/v1/account/{user.username}/banks/',
            {
                'type': BankAccount.CHECKING, 'account_number': '123434', 'routing_number': '123455666',
                'first_name': 'Jim', 'last_name': 'Bob',
            }, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_account_balance.assert_not_called()
        mock_add_bank_account.assert_called_with(user, '123434', '123455666', BankAccount.CHECKING)

    def test_bank_listing_staff(self):
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        response = self.client.get('/api/sales/v1/account/{}/banks/'.format(user.username))
        self.assertEqual(response.status_code, 403)

    def test_bank_listing_wrong_user(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        response = self.client.get('/api/sales/v1/account/{}/banks/'.format(user.username))
        self.assertEqual(response.status_code, 403)


class TestBankManager(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.account = BankAccountFactory.create(user=self.user)

    @patch('apps.sales.views.destroy_bank_account')
    def test_bank_account_destroy(self, _mock_destroy_account):
        self.login(self.user)
        response = self.client.delete('/api/sales/v1/account/{}/banks/{}/'.format(self.user.username, self.account.id))
        self.assertEqual(response.status_code, 204)

    def test_bank_account_destroy_wrong_user(self):
        user2 = UserFactory.create()
        self.login(user2)
        response = self.client.delete('/api/sales/v1/account/{}/banks/{}/'.format(self.user.username, self.account.id))
        self.assertEqual(response.status_code, 403)

    @patch('apps.sales.views.destroy_bank_account')
    def test_bank_account_destroy_staffer(self, _mock_destroy_account):
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        response = self.client.delete('/api/sales/v1/account/{}/banks/{}/'.format(self.user.username, self.account.id))
        self.assertEqual(response.status_code, 403)

    def test_bank_account_destroy_not_logged_in(self):
        response = self.client.delete('/api/sales/v1/account/{}/banks/{}/'.format(self.user.username, self.account.id))
        self.assertEqual(response.status_code, 403)


class TestAccountBalance(APITestCase):
    @patch('apps.sales.serializers.account_balance')
    def test_account_balance(self, mock_account_balance):
        user = UserFactory.create()
        self.login(user)
        mock_account_balance.side_effect = mock_balance
        response = self.client.get('/api/sales/v1/account/{}/balance/'.format(user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['available'], '100.00')
        self.assertEqual(response.data['escrow'], '50.00')

    @patch('apps.sales.serializers.account_balance')
    def test_account_balance_staff(self, mock_account_balance):
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        mock_account_balance.side_effect = mock_balance
        response = self.client.get('/api/sales/v1/account/{}/balance/'.format(user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['available'], '100.00')
        self.assertEqual(response.data['escrow'], '50.00')
        self.assertEqual(response.data['pending'], '10.00')

    def test_account_balance_wrong_user(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        response = self.client.get('/api/sales/v1/account/{}/balance/'.format(user.username))
        self.assertEqual(response.status_code, 403)

    def test_account_balance_not_logged_in(self):
        user = UserFactory.create()
        response = self.client.get('/api/sales/v1/account/{}/balance/'.format(user.username))
        self.assertEqual(response.status_code, 403)


def mock_balance(obj, account_type, status_filter=None):
    if status_filter == PENDING:
        return Decimal('10.00')
    if account_type == TransactionRecord.HOLDINGS:
        return Decimal('100.00')
    return Decimal('50.00')
