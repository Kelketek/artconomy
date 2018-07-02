from datetime import date
from decimal import Decimal
from unittest.mock import patch, call

from authorize import AuthorizeError
from django.core import mail
from django.test import TestCase, override_settings
from djmoney.money import Money
from freezegun import freeze_time

from apps.lib.models import SUBSCRIPTION_DEACTIVATED, Notification, RENEWAL_FAILURE, RENEWAL_FIXED
from apps.profiles.tests.factories import UserFactory
from apps.sales.models import PaymentRecord
from apps.sales.tasks import run_billing, renew
from apps.sales.tests.factories import CreditCardTokenFactory


class TestAutoRenewal(TestCase):
    @patch('apps.sales.tasks.renew')
    @freeze_time('2018-02-10')
    def test_tasks_made(self, mock_renew):
        disable1 = UserFactory.create(landscape_enabled=True, landscape_paid_through=date(2018, 2, 5))
        disable2 = UserFactory.create(portrait_enabled=True, portrait_paid_through=date(2018, 2, 4))
        renew_portrait = UserFactory.create(portrait_enabled=True, portrait_paid_through=date(2018, 2, 10))
        renew_landscape = UserFactory.create(landscape_enabled=True, landscape_paid_through=date(2018, 2, 9))
        run_billing()
        disable1.refresh_from_db()
        disable2.refresh_from_db()
        self.assertFalse(disable1.landscape_enabled)
        self.assertFalse(disable2.portrait_enabled)
        mock_renew.delay.assert_has_calls([call(renew_portrait.id, 'portrait'), call(renew_landscape.id, 'landscape')])
        self.assertEqual(Notification.objects.filter(event__type=SUBSCRIPTION_DEACTIVATED).count(), 2)
        self.assertEqual(len(mail.outbox), 2)
        for letter in mail.outbox:
            self.assertEqual(letter.subject, 'Your subscription has been deactivated.')

    @override_settings(PORTRAIT_PRICE=Decimal('2.00'))
    @patch('apps.sales.models.sauce')
    @freeze_time('2018-02-10')
    def test_renew_portrait(self, mock_sauce):
        mock_sauce.saved_card.return_value.capture.return_value.uid = 'Trans123'
        card = CreditCardTokenFactory.create(user__portrait_enabled=True, user__portrait_paid_through=date(2018, 2, 10))
        card.user.primary_card = card
        card.user.save()
        renew(card.user.id, 'portrait')
        card.user.refresh_from_db()
        self.assertEqual(card.user.portrait_paid_through, date(2018, 3, 10))
        self.assertTrue(card.user.portrait_enabled)
        self.assertFalse(card.user.landscape_enabled)
        self.assertIsNone(card.user.landscape_paid_through)
        records = PaymentRecord.objects.filter(payer=card.user)
        self.assertEqual(records.count(), 1)
        record = records[0]
        self.assertIsNone(record.payee)
        self.assertTrue(record.finalized)
        self.assertEqual(record.status, PaymentRecord.SUCCESS)
        self.assertEqual(record.txn_id, 'Trans123')
        self.assertEqual(record.type, PaymentRecord.SALE)
        self.assertEqual(record.amount, Money('2.00', 'USD'))

    @override_settings(LANDSCAPE_PRICE=Decimal('6.00'))
    @patch('apps.sales.models.sauce')
    @freeze_time('2018-02-10')
    def test_renew_landscape(self, mock_sauce):
        mock_sauce.saved_card.return_value.capture.return_value.uid = 'Trans123'
        card = CreditCardTokenFactory.create(
            user__landscape_enabled=True, user__landscape_paid_through=date(2018, 2, 10)
        )
        card.user.primary_card = card
        card.user.save()
        renew(card.user.id, 'landscape')
        card.user.refresh_from_db()
        self.assertEqual(card.user.landscape_paid_through, date(2018, 3, 10))
        self.assertTrue(card.user.landscape_enabled)
        self.assertFalse(card.user.portrait_enabled)
        self.assertEqual(card.user.portrait_paid_through, date(2018, 3, 10))
        records = PaymentRecord.objects.filter(payer=card.user)
        self.assertEqual(records.count(), 1)
        record = records[0]
        self.assertIsNone(record.payee)
        self.assertTrue(record.finalized)
        self.assertEqual(record.status, PaymentRecord.SUCCESS)
        self.assertEqual(record.txn_id, 'Trans123')
        self.assertEqual(record.type, PaymentRecord.SALE)
        self.assertEqual(record.amount, Money('6.00', 'USD'))
        self.assertEqual(record.card, card)

    @override_settings(PORTRAIT_PRICE=Decimal('2.00'))
    @patch('apps.sales.models.sauce')
    @freeze_time('2018-02-10')
    def test_failed_renewal(self, mock_sauce):
        mock_sauce.saved_card.return_value.capture.side_effect = AuthorizeError('Crap.')
        card = CreditCardTokenFactory.create(
            user__portrait_enabled=True, user__portrait_paid_through=date(2018, 2, 10)
        )
        card.user.primary_card = card
        card.user.save()
        renew(card.user.id, 'portrait')
        card.user.refresh_from_db()
        self.assertTrue(card.user.portrait_enabled)
        self.assertEqual(card.user.portrait_paid_through, date(2018, 2, 10))
        records = PaymentRecord.objects.filter(payer=card.user)
        self.assertEqual(records.count(), 1)
        record = records[0]
        self.assertIsNone(record.payee)
        self.assertTrue(record.finalized)
        self.assertEqual(record.status, PaymentRecord.FAILURE)
        self.assertEqual(record.txn_id, '')
        self.assertEqual(record.type, PaymentRecord.SALE)
        self.assertEqual(record.amount, Money('2.00', 'USD'))
        self.assertEqual(record.card, card)
        self.assertEqual(record.response_message, 'Crap.')
        self.assertEqual(Notification.objects.filter(event__type=RENEWAL_FAILURE).count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Issue with your subscription')

    @patch('apps.sales.models.sauce')
    @freeze_time('2018-02-10')
    def test_already_renewed(self, mock_sauce):
        # Still mock out capture here to avoid chance of contacting outside server.
        mock_sauce.saved_card.return_value.capture.return_value.uid = 'Trans123'
        card = CreditCardTokenFactory.create(
            user__portrait_enabled=True, user__portrait_paid_through=date(2018, 2, 11)
        )
        card.user.primary_card = card
        card.user.save()
        renew(card.user.id, 'portrait')
        card.user.refresh_from_db()
        self.assertEqual(card.user.portrait_enabled, True)
        self.assertEqual(card.user.portrait_paid_through, date(2018, 2, 11))
        self.assertFalse(PaymentRecord.objects.all().exists())
        mock_sauce.saved_card.return_value.capture.assert_not_called()

    @override_settings(PORTRAIT_PRICE=Decimal('2.00'))
    @patch('apps.sales.models.sauce')
    @freeze_time('2018-02-10')
    def test_card_override(self, mock_sauce):
        mock_sauce.saved_card.return_value.capture.return_value.uid = 'Trans123'
        primary_card = CreditCardTokenFactory.create(user__portrait_enabled=True, user__portrait_paid_through=date(2018, 2, 10))
        primary_card.user.primary_card = primary_card
        primary_card.user.save()
        card = CreditCardTokenFactory.create(user=primary_card.user)
        renew(card.user.id, 'portrait', card_id=card.id)
        card.user.refresh_from_db()
        self.assertEqual(card.user.portrait_paid_through, date(2018, 3, 10))
        self.assertTrue(card.user.portrait_enabled)
        self.assertFalse(card.user.landscape_enabled)
        self.assertIsNone(card.user.landscape_paid_through)
        records = PaymentRecord.objects.filter(payer=card.user)
        self.assertEqual(records.count(), 1)
        record = records[0]
        self.assertIsNone(record.payee)
        self.assertTrue(record.finalized)
        self.assertEqual(record.status, PaymentRecord.SUCCESS)
        self.assertEqual(record.txn_id, 'Trans123')
        self.assertEqual(record.type, PaymentRecord.SALE)
        self.assertEqual(record.amount, Money('2.00', 'USD'))
        self.assertEqual(card.user.primary_card, primary_card)
        self.assertEqual(Notification.objects.filter(event__type=RENEWAL_FIXED).count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Subscription renewed successfully')
