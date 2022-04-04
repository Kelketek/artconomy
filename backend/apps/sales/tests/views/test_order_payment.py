from datetime import date
from decimal import Decimal
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from ddt import ddt
from django.db.models import Sum
from django.test import override_settings
from django.utils import timezone
from freezegun import freeze_time
from moneyed import Money
from rest_framework import status

from apps.lib.models import Subscription, SALE_UPDATE, Notification, REFERRAL_LANDSCAPE_CREDIT
from apps.lib.test_resources import APITestCase
from apps.profiles.tests.factories import UserFactory
from apps.sales.apis import STRIPE
from apps.sales.models import PAYMENT_PENDING, REVIEW, IN_PROGRESS, TransactionRecord
from apps.sales.tests.factories import DeliverableFactory, add_adjustment, CreditCardTokenFactory, RevisionFactory
from apps.sales.tests.test_utils import TransactionCheckMixin


@override_settings(
    SERVICE_STATIC_FEE=Decimal('0.50'), SERVICE_PERCENTAGE_FEE=Decimal('4'),
    PREMIUM_STATIC_BONUS=Decimal('0.25'), PREMIUM_PERCENTAGE_BONUS=Decimal('4'),
)
@ddt
class TestOrderPayment(TransactionCheckMixin, APITestCase):

    def test_pay_order_fail_no_guest_email(self):
        user = UserFactory.create(is_staff=True)
        self.login(user)
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            order__buyer=None,
        )
        self.assertIsNone(deliverable.order.buyer)
        add_adjustment(deliverable, Money('2.00', 'USD'))
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'cash': True,
                'amount': '12.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'No buyer is set for this order, nor is there a customer email set.')

    def test_pay_order_staffer_cash(self):
        user = UserFactory.create(is_staff=True)
        self.login(user)
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'cash': True,
                'amount': '12.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_transactions(deliverable, deliverable.order.buyer, remote_id='', source=TransactionRecord.CASH_DEPOSIT)

    def test_pay_order_table_cash(self):
        user = UserFactory.create(is_staff=True)
        self.login(user)
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, product__base_price=Money('45.00', 'USD'),
            product__table_product=True, table_order=True,
            processor=STRIPE,
        )
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'cash': True,
                'amount': '50.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        total = TransactionRecord.objects.filter(source__in=[TransactionRecord.CASH_DEPOSIT, TransactionRecord.CARD]).aggregate(total=Sum('amount'))['total']
        self.assertEqual(total, Decimal('50.00'))

    def test_pay_order_table_edge_case(self):
        # This edge case has showed up before-- it created an extra penny. Putting this in to prevent a regression.
        user = UserFactory.create(is_staff=True)
        self.login(user)
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, product__base_price=Money('25.00', 'USD'),
            product__table_product=True, table_order=True,
            processor=STRIPE,
        )
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'cash': True,
                'amount': '30.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transactions = TransactionRecord.objects.filter(source__in=[TransactionRecord.CASH_DEPOSIT, TransactionRecord.CARD])
        total = transactions.aggregate(total=Sum('amount'))['total']
        self.assertEqual(total, Decimal('30.00'))

    def test_pay_order_buyer_cash_fail(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'cash': True,
                'amount': '12.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
