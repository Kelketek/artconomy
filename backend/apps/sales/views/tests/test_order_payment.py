from decimal import Decimal

from apps.lib.test_resources import APITestCase
from apps.lib.tests.test_utils import create_staffer
from apps.profiles.tests.factories import UserFactory
from apps.sales.constants import CARD, CASH_DEPOSIT, PAYMENT_PENDING, STRIPE
from apps.sales.models import TransactionRecord
from apps.sales.tests.factories import DeliverableFactory, add_adjustment
from apps.sales.tests.test_utils import TransactionCheckMixin
from ddt import ddt
from django.db.models import Sum
from moneyed import Money
from rest_framework import status


@ddt
class TestOrderInvoicePayment(TransactionCheckMixin, APITestCase):
    def test_pay_order_fail_no_guest_email(self):
        user = create_staffer("table_seller")
        self.login(user)
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING,
            product__base_price=Money("10.00", "USD"),
            order__buyer=None,
        )
        self.assertIsNone(deliverable.order.buyer)
        add_adjustment(deliverable, Money("2.00", "USD"))
        response = self.client.post(
            f"/api/sales/v1/invoice/{deliverable.invoice.id}/pay/",
            {
                "cash": True,
                "amount": "12.00",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "No buyer is set for this order, nor is there a customer email set.",
        )

    def test_pay_order_staffer_cash(self):
        user = create_staffer("table_seller")
        self.login(user)
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING,
            product__base_price=Money("10.00", "USD"),
        )
        add_adjustment(deliverable, Money("2.00", "USD"))
        response = self.client.post(
            f"/api/sales/v1/invoice/{deliverable.invoice.id}/pay/",
            {
                "cash": True,
                "amount": "12.00",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_transactions(
            deliverable, deliverable.order.buyer, remote_id="", source=CASH_DEPOSIT
        )

    def test_pay_order_table_cash(self):
        user = create_staffer("table_seller")
        self.login(user)
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING,
            product__base_price=Money("45.00", "USD"),
            product__table_product=True,
            table_order=True,
            processor=STRIPE,
        )
        response = self.client.post(
            f"/api/sales/v1/invoice/{deliverable.invoice.id}/pay/",
            {
                "cash": True,
                "amount": "45.00",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        total = TransactionRecord.objects.filter(
            source__in=[CASH_DEPOSIT, CARD]
        ).aggregate(total=Sum("amount"))["total"]
        self.assertEqual(total, Decimal("45.00"))

    def test_pay_order_buyer_cash_fail(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user,
            status=PAYMENT_PENDING,
            product__base_price=Money("10.00", "USD"),
        )
        add_adjustment(deliverable, Money("2.00", "USD"))
        response = self.client.post(
            f"/api/sales/v1/invoice/{deliverable.invoice.id}/pay/",
            {
                "cash": True,
                "amount": "12.00",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
