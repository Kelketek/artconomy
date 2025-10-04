from csv import DictReader
from decimal import Decimal
from io import StringIO
from unittest.mock import patch

from dateutil.relativedelta import relativedelta

from apps.lib.models import ref_for_instance
from apps.lib.test_resources import APITestCase, DeliverableChargeMixin
from apps.lib.utils import utc_now
from apps.profiles.tests.factories import SubmissionFactory, UserFactory
from apps.sales.constants import (
    BANK_TRANSFER_FEES,
    PAYOUT_ACCOUNT,
    CARD,
    CARD_TRANSACTION_FEES,
    CASH_DEPOSIT,
    CASH_WITHDRAW,
    ESCROW,
    HOLDINGS,
    MONEY_HOLE,
    OPEN,
    PAID,
    PAYMENT_PENDING,
    PENDING,
    PROCESSING_FEE,
    SUBSCRIPTION_DUES,
    SUCCESS,
    THIRD_PARTY_FEE,
    TIP_SEND,
    TIPPING,
    FUND,
)
from apps.sales.models import Deliverable, StripeAccount, TransactionRecord
from apps.sales.tests.factories import (
    DeliverableFactory,
    InvoiceFactory,
    LineItemFactory,
    StripeAccountFactory,
    TransactionRecordFactory,
)
from apps.sales.utils import (
    finalize_deliverable,
    get_term_invoice,
)
from dateutil.parser import parse
from django.test import override_settings
from freezegun import freeze_time
from moneyed import Money
from rest_framework import status
from rest_framework.response import Response


class TestCustomerHoldings(APITestCase):
    def test_customer_holdings(self):
        buyer = UserFactory.create()
        deliverable = DeliverableFactory.create(order__buyer=buyer)
        TransactionRecordFactory.create(
            source=CARD,
            destination=ESCROW,
            amount=Money("25.00", "USD"),
            payee=deliverable.order.seller,
        )
        TransactionRecordFactory.create(
            payer=None,
            source=FUND,
            destination=HOLDINGS,
            payee=deliverable.order.seller,
            amount=Money("50.00", "USD"),
        )
        # Pending, so shouldn't be counted.
        TransactionRecordFactory.create(
            payer=None,
            source=FUND,
            destination=HOLDINGS,
            payee=deliverable.order.seller,
            status=PENDING,
            amount=Money("50.00", "USD"),
        )
        # Should not show up, as this account isn't checked, and the payee doesn't have
        # any sales, so should be excluded for performance reasons.
        TransactionRecordFactory.create(
            payer=deliverable.order.seller,
            source=CARD,
            destination=ESCROW,
            amount=Money("30.00", "USD"),
            payee=buyer,
        )
        staff = UserFactory.create(is_superuser=True)
        self.login(staff)
        end_date = utc_now() + relativedelta(days=1)
        response = self.client.get(
            "/api/sales/v1/reports/customer-holdings/csv/"
            f"?end_date={end_date.year}-{end_date.month}-{end_date.day}"
        )
        reader = DictReader(StringIO(response.content.decode("utf-8")))
        lines = [line for line in reader]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["username"], deliverable.order.seller.username)
        self.assertEqual(lines[0]["escrow"], "25.00")
        self.assertEqual(lines[0]["holdings"], "50.00")
        self.assertEqual(lines[0]["id"], str(deliverable.order.seller.id))


class TestUnaffiliatedSales(APITestCase):
    @freeze_time("2022-03-25")
    def test_unaffiliated_sales(self):
        # Too Early
        LineItemFactory.create(
            invoice__created_on=utc_now().replace(month=1),
            invoice__paid_on=utc_now().replace(month=1),
            invoice__status=PAID,
        )
        # Wrong Status
        LineItemFactory.create(
            invoice__created_on=utc_now().replace(day=5),
            invoice__status=OPEN,
        )
        # Deliverable creates invoice, which shouldn't appear.
        DeliverableFactory.create(invoice__status=PAID)
        # Card invoice
        card_line_item = LineItemFactory.create(
            invoice__created_on=utc_now().replace(day=5),
            invoice__paid_on=utc_now().replace(day=5),
            invoice__status=PAID,
            amount=Money("15.00", "USD"),
        )
        # Amount doesn't matter here-- determines whether the invoice is cash or card by
        # the presence of this transaction.
        card_main_transaction = TransactionRecordFactory.create(
            source=CARD,
            payer=card_line_item.invoice.bill_to,
            amount=Money("25.00", "USD"),
            remote_ids=["1234"],
        )
        card_main_transaction.targets.add(ref_for_instance(card_line_item.invoice))
        tax = TransactionRecordFactory.create(
            payer=card_main_transaction.payer,
            payee=card_main_transaction.payee,
            destination=MONEY_HOLE,
            amount=Money("2.00", "USD"),
        )
        tax.targets.add(ref_for_instance(card_line_item.invoice))
        fees = TransactionRecordFactory.create(
            payer=card_main_transaction.payer,
            payee=None,
            remote_ids=["5678"],
            destination=CARD_TRANSACTION_FEES,
            amount=Money("2.00", "USD"),
        )
        fees.targets.add(ref_for_instance(card_line_item.invoice))
        # Cash invoice
        cash_line_item = LineItemFactory.create(
            invoice__created_on=utc_now().replace(day=1, month=1),
            invoice__paid_on=utc_now().replace(day=7),
            invoice__status=PAID,
            amount=Money("10", "USD"),
        )
        # Same deal on the amount not mattering here.
        cash_main_transaction = TransactionRecordFactory.create(
            source=CASH_DEPOSIT,
            payer=cash_line_item.invoice.bill_to,
            amount=Money("100.00", "USD"),
        )
        cash_main_transaction.targets.add(ref_for_instance(cash_line_item.invoice))
        cash_tax = TransactionRecordFactory.create(
            payer=cash_main_transaction.payer,
            payee=cash_main_transaction.payee,
            destination=MONEY_HOLE,
            amount=Money("3.00", "USD"),
        )
        cash_tax.targets.add(ref_for_instance(cash_line_item.invoice))
        # Last invoice-- one that is weird, and we don't know the source of it
        unknown_main_transaction = LineItemFactory.create(
            invoice__paid_on=utc_now().replace(day=8),
            invoice__status=PAID,
            amount=Money("25.00", "USD"),
        )
        staff = UserFactory.create(is_superuser=True)
        self.login(staff)
        response = self.client.get(
            "/api/sales/v1/reports/unaffiliated-sales/csv/",
            {
                "start_date": utc_now().replace(day=1).date().isoformat(),
                "end_date": utc_now().date().isoformat(),
            },
        )
        reader = DictReader(StringIO(response.content.decode("utf-8")))
        lines = [line for line in reader]
        self.assertEqual(len(lines), 3)
        # Card
        self.assertEqual(lines[0]["id"], card_line_item.invoice.id)
        self.assertEqual(lines[0]["remote_ids"], "1234, 5678")
        self.assertEqual(lines[0]["total"], "15.00")
        self.assertEqual(lines[0]["tax"], "2.00")
        self.assertEqual(lines[0]["card_fees"], "2.00")
        self.assertEqual(lines[0]["source"], "Card")
        # Cash
        self.assertEqual(lines[1]["id"], cash_line_item.invoice.id)
        self.assertEqual(lines[1]["remote_ids"], "")
        self.assertEqual(lines[1]["total"], "10.00")
        self.assertEqual(lines[1]["tax"], "3.00")
        self.assertEqual(lines[1]["card_fees"], "0.00")
        self.assertEqual(lines[1]["source"], "Cash")
        # Unknown
        self.assertEqual(lines[2]["id"], unknown_main_transaction.invoice.id)
        self.assertEqual(lines[2]["remote_ids"], "")
        self.assertEqual(lines[2]["total"], "25.00")
        self.assertEqual(lines[2]["tax"], "0.00")
        self.assertEqual(lines[2]["card_fees"], "0.00")
        self.assertEqual(lines[2]["source"], "????")


class TestPayoutReport(APITestCase):
    @freeze_time("2022-03-25")
    def test_payout_report(self):
        user = UserFactory.create()
        source_transaction = TransactionRecordFactory.create()
        transaction = TransactionRecordFactory.create(
            source=HOLDINGS,
            destination=PAYOUT_ACCOUNT,
            remote_ids=["1234", "5678"],
            created_on=utc_now().replace(day=5),
            finalized_on=utc_now().replace(day=5),
            amount=Money("20.00", "USD"),
            payer=user,
            payee=user,
            status=SUCCESS,
        )
        fee = TransactionRecordFactory.create(
            source=FUND,
            destination=BANK_TRANSFER_FEES,
            amount=Money("2.00", "USD"),
        )
        fee.targets.add(ref_for_instance(transaction))
        submission = SubmissionFactory.create(owner=transaction.payer)
        deleted_submission = SubmissionFactory.create(owner=transaction.payer)
        transaction.targets.add(ref_for_instance(submission))
        transaction.targets.add(ref_for_instance(deleted_submission))
        transaction.targets.add(ref_for_instance(source_transaction))
        deleted_submission.delete()
        # Shouldn't be included
        TransactionRecordFactory.create(
            source=CARD, destination=HOLDINGS, amount=Money("10.00", "USD")
        )
        # Too old
        TransactionRecordFactory.create(
            source=HOLDINGS,
            destination=PAYOUT_ACCOUNT,
            remote_ids=["1234", "5678"],
            created_on=utc_now().replace(month=1),
            finalized_on=utc_now().replace(month=1),
            payer=user,
            payee=user,
            status=SUCCESS,
        )
        staff = UserFactory.create(is_superuser=True)
        self.login(staff)
        response = self.client.get(
            "/api/sales/v1/reports/payout-report/csv/",
            {
                "start_date": utc_now().replace(day=1).date().isoformat(),
                "end_date": utc_now().date().isoformat(),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reader = DictReader(StringIO(response.content.decode("utf-8")))
        lines = [line for line in reader]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["id"], transaction.id)
        self.assertEqual(lines[0]["amount"], "20.00")
        self.assertEqual(lines[0]["status"], "Successful")
        self.assertEqual(
            lines[0]["targets"],
            f"Submission #{submission.id}, TransactionRecord #{source_transaction.id} "
            f"($10.00)",
        )
        self.assertEqual(lines[0]["payee"], transaction.payee.username)
        self.assertEqual(lines[0]["total_drafted"], "22.00")
        self.assertEqual(lines[0]["fees"], "2.00")
        self.assertEqual(parse(lines[0]["created_on"]), transaction.created_on)
        self.assertEqual(parse(lines[0]["finalized_on"]), transaction.finalized_on)


class TestTipReport(APITestCase):
    @freeze_time("2022-03-25")
    def test_tip_report_all_data_available(self):
        user = UserFactory.create()
        invoice = InvoiceFactory.create(type=TIPPING, issued_by=user)
        invoice.paid_on = utc_now().replace(day=5)
        invoice.status = PAID
        invoice.save()
        transaction = TransactionRecordFactory.create(
            source=CARD,
            destination=HOLDINGS,
            category=TIP_SEND,
            created_on=utc_now().replace(day=5),
            finalized_on=utc_now().replace(day=5),
            amount=Money("20.00", "USD"),
            remote_ids=["1234", "5678"],
            payer=invoice.bill_to,
            payee=user,
            status=SUCCESS,
        )
        transaction.targets.set([ref_for_instance(invoice)])
        transaction = TransactionRecordFactory.create(
            source=CARD,
            destination=FUND,
            category=PROCESSING_FEE,
            created_on=utc_now().replace(day=5),
            finalized_on=utc_now().replace(day=5),
            amount=Money("5.00", "USD"),
            remote_ids=["1234", "5678"],
            payer=invoice.bill_to,
            payee=None,
            status=SUCCESS,
        )
        transaction.targets.set([ref_for_instance(invoice)])
        transaction = TransactionRecordFactory.create(
            source=FUND,
            destination=CARD_TRANSACTION_FEES,
            category=THIRD_PARTY_FEE,
            created_on=utc_now().replace(day=5),
            finalized_on=utc_now().replace(day=5),
            amount=Money("1.00", "USD"),
            remote_ids=["1234", "5678"],
            payer=None,
            payee=None,
            status=SUCCESS,
        )
        transaction.targets.set([ref_for_instance(invoice)])
        transaction = TransactionRecordFactory.create(
            source=HOLDINGS,
            destination=PAYOUT_ACCOUNT,
            category=CASH_WITHDRAW,
            created_on=utc_now().replace(day=5),
            finalized_on=utc_now().replace(day=5),
            amount=Money("20.00", "USD"),
            remote_ids=["1234", "5678"],
            payer=user,
            payee=user,
            status=SUCCESS,
        )
        transaction.targets.set([ref_for_instance(invoice)])
        transaction_fee = TransactionRecordFactory.create(
            source=FUND,
            destination=BANK_TRANSFER_FEES,
            category=THIRD_PARTY_FEE,
            created_on=utc_now().replace(day=5),
            finalized_on=utc_now().replace(day=5),
            amount=Money(".50", "USD"),
            remote_ids=["1234", "5678"],
            payer=None,
            payee=None,
            status=SUCCESS,
        )
        transaction_fee.targets.set(
            [ref_for_instance(invoice), ref_for_instance(transaction)]
        )
        staff = UserFactory.create(is_superuser=True)
        self.login(staff)
        response = self.client.get(
            "/api/sales/v1/reports/tip-report/csv/",
            {
                "start_date": utc_now().replace(day=1).date().isoformat(),
                "end_date": utc_now().date().isoformat(),
            },
        )
        reader = DictReader(StringIO(response.content.decode("utf-8")))
        lines = [line for line in reader]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["id"], invoice.id)
        self.assertEqual(lines[0]["bill_to"], invoice.bill_to.username)
        self.assertEqual(lines[0]["remote_ids"], "1234, 5678")
        self.assertEqual(lines[0]["status"], "Paid")
        self.assertEqual(Decimal(lines[0]["artist_earnings"]), Decimal("20.00"))
        self.assertEqual(Decimal(lines[0]["card_fees"]), Decimal("1"))
        self.assertEqual(parse(lines[0]["paid_on"]), invoice.paid_on)

    @freeze_time("2022-03-25")
    def test_tip_report_guest_user(self):
        user = UserFactory.create()
        invoice = InvoiceFactory.create(type=TIPPING, issued_by=user)
        invoice.bill_to.username = f"__{invoice.bill_to.id}"
        invoice.bill_to.guest = True
        invoice.bill_to.save()
        invoice.paid_on = utc_now().replace(day=5)
        invoice.status = PAID
        invoice.save()
        transaction = TransactionRecordFactory.create(
            source=CARD,
            destination=HOLDINGS,
            category=TIP_SEND,
            created_on=utc_now().replace(day=5),
            finalized_on=utc_now().replace(day=5),
            amount=Money("20.00", "USD"),
            remote_ids=["1234", "5678"],
            payer=invoice.bill_to,
            payee=user,
            status=SUCCESS,
        )
        transaction.targets.set([ref_for_instance(invoice)])
        transaction = TransactionRecordFactory.create(
            source=CARD,
            destination=FUND,
            category=PROCESSING_FEE,
            created_on=utc_now().replace(day=5),
            finalized_on=utc_now().replace(day=5),
            amount=Money("5.00", "USD"),
            remote_ids=["1234", "5678"],
            payer=invoice.bill_to,
            payee=None,
            status=SUCCESS,
        )
        transaction.targets.set([ref_for_instance(invoice)])
        staff = UserFactory.create(is_superuser=True)
        self.login(staff)
        response = self.client.get(
            "/api/sales/v1/reports/tip-report/csv/",
            {
                "start_date": utc_now().replace(day=1).date().isoformat(),
                "end_date": utc_now().date().isoformat(),
            },
        )
        reader = DictReader(StringIO(response.content.decode("utf-8")))
        lines = [line for line in reader]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["id"], invoice.id)
        self.assertEqual(lines[0]["bill_to"], f"Guest #{invoice.bill_to.id}")

    @freeze_time("2022-03-25")
    def test_tip_report_fees_not_yet_calculated(self):
        user = UserFactory.create()
        invoice = InvoiceFactory.create(type=TIPPING, issued_by=user)
        invoice.paid_on = utc_now().replace(day=5)
        invoice.status = PAID
        invoice.save()
        transaction = TransactionRecordFactory.create(
            source=CARD,
            destination=HOLDINGS,
            category=TIP_SEND,
            created_on=utc_now().replace(day=5),
            finalized_on=utc_now().replace(day=5),
            amount=Money("20.00", "USD"),
            remote_ids=["1234", "5678"],
            payer=invoice.bill_to,
            payee=user,
            status=SUCCESS,
        )
        transaction.targets.set([ref_for_instance(invoice)])
        transaction = TransactionRecordFactory.create(
            source=CARD,
            destination=FUND,
            category=PROCESSING_FEE,
            created_on=utc_now().replace(day=5),
            finalized_on=utc_now().replace(day=5),
            amount=Money("5.00", "USD"),
            remote_ids=["1234", "5678"],
            payer=invoice.bill_to,
            payee=None,
            status=SUCCESS,
        )
        transaction.targets.set([ref_for_instance(invoice)])
        transaction = TransactionRecordFactory.create(
            source=HOLDINGS,
            destination=PAYOUT_ACCOUNT,
            category=CASH_WITHDRAW,
            created_on=utc_now().replace(day=5),
            finalized_on=utc_now().replace(day=5),
            amount=Money("20.00", "USD"),
            remote_ids=["1234", "5678"],
            payer=user,
            payee=user,
            status=SUCCESS,
        )
        transaction.targets.set([ref_for_instance(invoice)])
        staff = UserFactory.create(is_superuser=True)
        self.login(staff)
        response = self.client.get(
            "/api/sales/v1/reports/tip-report/csv/",
            {
                "start_date": utc_now().replace(day=1).date().isoformat(),
                "end_date": utc_now().date().isoformat(),
            },
        )
        reader = DictReader(StringIO(response.content.decode("utf-8")))
        lines = [line for line in reader]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["id"], invoice.id)
        self.assertEqual(lines[0]["bill_to"], invoice.bill_to.username)


class TestSubscriptionReport(APITestCase):
    @freeze_time("2022-03-25")
    def test_subscription_report(self):
        user = UserFactory.create()
        term_invoice = get_term_invoice(user)
        LineItemFactory.create(
            invoice=term_invoice,
            amount=Money("5.00", "USD"),
        )
        term_invoice.paid_on = utc_now().replace(day=5)
        term_invoice.status = PAID
        term_invoice.save()
        transaction = TransactionRecordFactory.create(
            source=CARD,
            destination=FUND,
            category=SUBSCRIPTION_DUES,
            created_on=utc_now().replace(day=5),
            finalized_on=utc_now().replace(day=5),
            amount=Money("20.00", "GBP"),
            remote_ids=["1234", "5678"],
            payer=user,
            payee=None,
            status=SUCCESS,
        )
        transaction.targets.add(ref_for_instance(term_invoice))
        # Too old
        old_invoice = get_term_invoice(user)
        old_invoice.status = PAID
        old_invoice.created_on = utc_now().replace(month=1)
        old_invoice.paid_on = utc_now().replace(month=1)
        old_invoice.save()
        old_transaction = TransactionRecordFactory.create(
            source=CARD,
            destination=FUND,
            category=SUBSCRIPTION_DUES,
            created_on=utc_now().replace(month=1),
            finalized_on=utc_now().replace(month=1),
            amount=Money("20.00", "GBP"),
            payer=user,
            payee=None,
            status=SUCCESS,
        )
        old_transaction.targets.add(ref_for_instance(old_invoice))
        staff = UserFactory.create(is_superuser=True)
        self.login(staff)
        response = self.client.get(
            "/api/sales/v1/reports/subscription-report/csv/",
            {
                "start_date": utc_now().replace(day=1).date().isoformat(),
                "end_date": utc_now().date().isoformat(),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reader = DictReader(StringIO(response.content.decode("utf-8")))
        lines = [line for line in reader]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["id"], term_invoice.id)
        self.assertEqual(lines[0]["bill_to"], term_invoice.bill_to.username)
        self.assertEqual(lines[0]["remote_ids"], "1234, 5678")
        self.assertEqual(lines[0]["status"], "Paid")
        self.assertEqual(parse(lines[0]["paid_on"]), term_invoice.paid_on)

    # Adding a few tests to check the date filter since this is a simple endpoint.

    @freeze_time("2022-03-25")
    def test_default_date(self):
        user = UserFactory.create()
        term_invoice = get_term_invoice(user)
        LineItemFactory.create(
            invoice=term_invoice,
            amount=Money("5.00", "USD"),
        )
        term_invoice.paid_on = utc_now().replace(day=5)
        term_invoice.status = PAID
        term_invoice.save()
        transaction = TransactionRecordFactory.create(
            source=CARD,
            destination=FUND,
            category=SUBSCRIPTION_DUES,
            created_on=utc_now().replace(day=5),
            finalized_on=utc_now().replace(day=5),
            amount=Money("20.00", "GBP"),
            remote_ids=["1234", "5678"],
            payer=user,
            payee=None,
            status=SUCCESS,
        )
        transaction.targets.add(ref_for_instance(term_invoice))
        # Too old
        old_invoice = get_term_invoice(user)
        old_invoice.status = PAID
        old_invoice.paid_on = utc_now().replace(year=2021)
        old_invoice.save()
        old_record = TransactionRecordFactory.create(
            source=CARD,
            destination=FUND,
            category=SUBSCRIPTION_DUES,
            created_on=utc_now().replace(year=2021),
            finalized_on=utc_now().replace(year=2021),
            amount=Money("20.00", "GBP"),
            payer=user,
            payee=None,
            status=SUCCESS,
        )
        old_record.targets.add(ref_for_instance(term_invoice))
        staff = UserFactory.create(is_superuser=True)
        self.login(staff)
        response = self.client.get(
            "/api/sales/v1/reports/subscription-report/csv/",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reader = DictReader(StringIO(response.content.decode("utf-8")))
        lines = [line for line in reader]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["id"], term_invoice.id)
        self.assertEqual(lines[0]["bill_to"], term_invoice.bill_to.username)
        self.assertEqual(lines[0]["remote_ids"], "1234, 5678")
        self.assertEqual(lines[0]["status"], "Paid")
        self.assertEqual(parse(lines[0]["paid_on"]), term_invoice.paid_on)

    @freeze_time("2022-03-25")
    def test_default_date_malformed_date(self):
        user = UserFactory.create()
        term_invoice = get_term_invoice(user)
        LineItemFactory.create(
            invoice=term_invoice,
            amount=Money("5.00", "USD"),
        )
        term_invoice.paid_on = utc_now().replace(day=5)
        term_invoice.status = PAID
        term_invoice.save()
        transaction = TransactionRecordFactory.create(
            source=CARD,
            destination=FUND,
            category=SUBSCRIPTION_DUES,
            created_on=utc_now().replace(day=5),
            finalized_on=utc_now().replace(day=5),
            amount=Money("20.00", "GBP"),
            remote_ids=["1234", "5678"],
            payer=user,
            payee=None,
            status=SUCCESS,
        )
        transaction.targets.add(ref_for_instance(term_invoice))
        # Too old
        old_invoice = get_term_invoice(user)
        old_invoice.status = PAID
        old_invoice.paid_on = utc_now().replace(year=2021)
        old_invoice.save()
        old_transaction = TransactionRecordFactory.create(
            source=CARD,
            destination=FUND,
            category=SUBSCRIPTION_DUES,
            created_on=utc_now().replace(year=2021),
            finalized_on=utc_now().replace(year=2021),
            amount=Money("20.00", "GBP"),
            payer=user,
            payee=None,
            status=SUCCESS,
        )
        old_invoice.targets.add(ref_for_instance(old_transaction))
        staff = UserFactory.create(is_superuser=True)
        self.login(staff)
        response = self.client.get(
            "/api/sales/v1/reports/subscription-report/csv/",
            {
                "start_date": "wat",
                "end_date": "thing",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reader = DictReader(StringIO(response.content.decode("utf-8")))
        lines = [line for line in reader]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["id"], term_invoice.id)
        self.assertEqual(lines[0]["bill_to"], term_invoice.bill_to.username)
        self.assertEqual(lines[0]["remote_ids"], "1234, 5678")
        self.assertEqual(lines[0]["status"], "Paid")
        self.assertEqual(parse(lines[0]["paid_on"]), term_invoice.paid_on)


@freeze_time("2022-03-25")
@override_settings(TABLE_TAX=Decimal("8.25"))
class TestOrderValues(APITestCase, DeliverableChargeMixin):
    def setUp(self):
        super().setUp()
        self.staff = UserFactory.create(is_superuser=True, is_staff=True)
        self.login(self.staff)

    def get_lines(self, response: Response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reader = DictReader(StringIO(response.content.decode("utf-8")))
        return [line for line in reader]

    @patch("apps.sales.tasks.stripe")
    def payout_transactions(
        self,
        deliverable: Deliverable,
        mock_stripe,
        success=True,
    ):
        try:
            deliverable.order.seller.stripe_account
        except StripeAccount.DoesNotExist:
            StripeAccountFactory.create(user=deliverable.order.seller)
        mock_stripe.__enter__.return_value.Transfer.create.return_value = {
            "id": f"outbound{deliverable.id}",
            "destination_payment": f"outbound_payment{deliverable.id}",
            "balance_transaction": f"txn_balance{deliverable.id}",
        }
        finalize_deliverable(deliverable)
        deliverable.refresh_from_db()
        if success:
            record = TransactionRecord.objects.get(
                remote_ids__contains=f"outbound{deliverable.id}"
            )
            record.status = SUCCESS
            record.save()

    def test_participant_display(self):
        deliverable_normal = DeliverableFactory.create(
            created_on=utc_now().replace(day=1), status=PAYMENT_PENDING
        )
        self.charge_transaction(deliverable_normal)
        deliverable_guest = DeliverableFactory.create(
            created_on=utc_now().replace(day=2),
            status=PAYMENT_PENDING,
            order__buyer__guest=True,
        )
        self.charge_transaction(deliverable_guest)
        lines = self.get_lines(
            self.client.get("/api/sales/v1/reports/order-values/csv/")
        )
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0]["buyer"], deliverable_normal.order.buyer.username)
        self.assertEqual(lines[0]["seller"], deliverable_normal.order.seller.username)
        self.assertEqual(
            lines[1]["buyer"], f"Guest #{deliverable_guest.order.buyer.id}"
        )
        self.assertEqual(lines[1]["seller"], deliverable_guest.order.seller.username)

    def test_completed_values(self):
        deliverable = DeliverableFactory.create(
            created_on=utc_now().replace(day=1),
            status=PAYMENT_PENDING,
            product__base_price=Money("15.00", "USD"),
        )
        self.charge_transaction(deliverable)
        deliverable.invoice.paid_on = utc_now().replace(day=1)
        deliverable.invoice.save()
        self.payout_transactions(deliverable)
        lines = self.get_lines(
            self.client.get("/api/sales/v1/reports/order-values/csv/")
        )
        self.assertEqual(len(lines), 1)
        line = lines[0]
        self.assertEqual(Decimal(line["our_fees"]), Decimal("5.43"))
        self.assertEqual(Decimal(line["card_fees"]), Decimal("0.89"))
        self.assertEqual(Decimal(line["price"]), Decimal("20.43"))

    def test_refunded_transaction(self):
        deliverable = DeliverableFactory.create(
            created_on=utc_now().replace(day=1),
            status=PAYMENT_PENDING,
            product__base_price=Money("15.00", "USD"),
        )
        self.charge_transaction(deliverable)
        self.refund_transaction(deliverable)
        lines = self.get_lines(
            self.client.get("/api/sales/v1/reports/order-values/csv/")
        )
        self.assertEqual(len(lines), 1)
        line = lines[0]
        self.assertEqual(Decimal(line["our_fees"]), Decimal("5.43"))
        self.assertEqual(Decimal(line["price"]), Decimal("20.43"))
