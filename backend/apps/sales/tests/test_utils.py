from django.test import TestCase
from moneyed import Money, Decimal

from apps.profiles.tests.factories import UserFactory
from apps.sales.models import PaymentRecord
from apps.sales.tests.factories import PaymentRecordFactory
from apps.sales.utils import escrow_balance, available_balance


class BalanceTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.user2 = UserFactory.create()
        self.user3 = UserFactory.create()

    def test_escrow_balances(self):
        PaymentRecordFactory.create(
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('10.00', 'USD')
        )
        self.assertEqual(escrow_balance(self.user), Decimal('10.00'))
        self.assertEqual(escrow_balance(self.user2), Decimal('0.00'))
        self.assertEqual(escrow_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('25.00', 'USD')
        )
        self.assertEqual(escrow_balance(self.user), Decimal('35.00'))
        self.assertEqual(escrow_balance(self.user2), Decimal('0.00'))
        self.assertEqual(escrow_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('5.00', 'USD')
        )
        self.assertEqual(escrow_balance(self.user), Decimal('40.00'))
        self.assertEqual(escrow_balance(self.user2), Decimal('0.00'))
        self.assertEqual(escrow_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            status=PaymentRecord.FAILURE,
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('6.00', 'USD')
        )
        self.assertEqual(escrow_balance(self.user), Decimal('40.00'))
        self.assertEqual(escrow_balance(self.user2), Decimal('0.00'))
        self.assertEqual(escrow_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=self.user,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ESCROW,
            amount=Money('10.00', 'USD')
        )
        self.assertEqual(escrow_balance(self.user), Decimal('30.00'))
        self.assertEqual(escrow_balance(self.user2), Decimal('0.00'))
        self.assertEqual(escrow_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=self.user,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ESCROW,
            amount=Money('25.00', 'USD')
        )
        self.assertEqual(escrow_balance(self.user), Decimal('5.00'))
        self.assertEqual(escrow_balance(self.user2), Decimal('0.00'))
        self.assertEqual(escrow_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=None,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ACCOUNT,
            type=PaymentRecord.DISBURSEMENT,
            amount=Money('15.00', 'USD')
        )
        self.assertEqual(escrow_balance(self.user), Decimal('5.00'))
        self.assertEqual(escrow_balance(self.user2), Decimal('0.00'))
        self.assertEqual(escrow_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=None,
            status=PaymentRecord.FAILURE,
            source=PaymentRecord.ACCOUNT,
            type=PaymentRecord.DISBURSEMENT,
            amount=Money('8.00', 'USD')
        )
        self.assertEqual(escrow_balance(self.user), Decimal('5.00'))
        self.assertEqual(escrow_balance(self.user2), Decimal('0.00'))
        self.assertEqual(escrow_balance(self.user3), Decimal('0.00'))

    def test_account_balance(self):
        PaymentRecordFactory.create(
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('10.00', 'USD')
        )
        self.assertEqual(available_balance(self.user), Decimal('0.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('25.00', 'USD')
        )
        self.assertEqual(available_balance(self.user), Decimal('0.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('5.00', 'USD')
        )
        self.assertEqual(available_balance(self.user), Decimal('0.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            status=PaymentRecord.FAILURE,
            payee=None,
            payer=self.user2,
            escrow_for=self.user,
            amount=Money('6.00', 'USD')
        )
        self.assertEqual(available_balance(self.user), Decimal('0.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=self.user,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ESCROW,
            amount=Money('10.00', 'USD')
        )
        self.assertEqual(available_balance(self.user), Decimal('10.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=self.user,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ESCROW,
            amount=Money('25.00', 'USD')
        )
        self.assertEqual(available_balance(self.user), Decimal('35.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payer=self.user,
            payee=None,
            status=PaymentRecord.SUCCESS,
            source=PaymentRecord.ACCOUNT,
            type=PaymentRecord.DISBURSEMENT,
            amount=Money('15.00', 'USD')
        )
        self.assertEqual(available_balance(self.user), Decimal('20.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
        PaymentRecordFactory.create(
            payee=None,
            status=PaymentRecord.FAILURE,
            source=PaymentRecord.ACCOUNT,
            type=PaymentRecord.DISBURSEMENT,
            amount=Money('8.00', 'USD')
        )
        self.assertEqual(available_balance(self.user), Decimal('20.00'))
        self.assertEqual(available_balance(self.user2), Decimal('0.00'))
        self.assertEqual(available_balance(self.user3), Decimal('0.00'))
