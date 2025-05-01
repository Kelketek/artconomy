from datetime import datetime
from decimal import Decimal
from typing import Union

from moneyed import Money
from pytz import UTC
from rest_framework.response import Response

from apps.lib.permissions import StaffPower, Or
from apps.lib.utils import utc_now, utc
from apps.profiles.models import User
from apps.profiles.permissions import IsSuperuser
from apps.sales.constants import (
    PAYOUT_ACCOUNT,
    CANCELLED,
    DISPUTED,
    FAILURE,
    HOLDINGS,
    IN_PROGRESS,
    NEW,
    PAID,
    PAYMENT_PENDING,
    QUEUED,
    SALE,
    SUBSCRIPTION,
    TERM,
    TIPPING,
    WAITING,
    FUND,
    CASH_DEPOSIT,
    CARD,
    SUCCESS,
    CARD_TRANSACTION_FEES,
    ESCROW,
)
from apps.sales.models import Deliverable, Invoice, TransactionRecord
from apps.sales.serializers import (
    DeliverableSerializer,
    DeliverableValuesSerializer,
    HoldingsSummarySerializer,
    PayoutTransactionSerializer,
    SubscriptionInvoiceSerializer,
    TipValuesSerializer,
    UnaffiliatedInvoiceSerializer,
    ReconciliationRecordSerializer,
)
from apps.sales.utils import PENDING, account_balance, ALL
from dateutil.parser import ParserError, parse
from dateutil.relativedelta import relativedelta
from django.db.models import F, Q
from django.utils import timezone
from django.utils.timezone import make_aware
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.request import Request
from rest_framework_csv.renderers import CSVRenderer


class DateConstrained:
    request: Request
    date_fields = ["created_on"]

    def __init__(self, *args, **kwargs):
        if hasattr(self, "date_field"):
            raise AttributeError("date_field is deprecated. Use date_fields instead.")
        if isinstance(self.date_fields, str):
            raise AttributeError("date_fields must be a list of strings.")
        super().__init__(*args, **kwargs)

    @property
    def start_date(self) -> datetime:
        start_date = None
        default_start = utc_now().replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        default_start -= relativedelta(months=2)
        date_string = self.request.GET.get("start_date", "")
        try:
            start_date = make_aware(parse(date_string), timezone=utc)
        except ParserError:
            pass
        if not start_date:
            start_date = default_start
        return start_date

    @property
    def end_date(self) -> Union[datetime, None]:
        end_date = None
        date_string = self.request.GET.get("end_date", "")
        default_end = (utc_now() + relativedelta(days=1)).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        try:
            end_date = make_aware(parse(date_string), timezone=utc)
        except ParserError:
            pass
        if not end_date:
            end_date = default_end
        return end_date

    @property
    def date_filter(self):
        date_filter = None
        for field in self.date_fields:
            new_filter = Q(
                **{
                    f"{field}__gte": self.start_date,
                    f"{field}__lte": self.end_date,
                }
            )
            if date_filter:
                date_filter |= new_filter
                continue
            date_filter = new_filter
        return date_filter


class CustomerHoldingsCSV(DateConstrained, ListAPIView):
    date_fields = ["finalized_on"]
    serializer_class = HoldingsSummarySerializer
    permission_classes = [IsSuperuser]
    pagination_class = None
    renderer_classes = [CSVRenderer]

    def get_queryset(self):
        return (
            User.objects.filter(guest=False, sales__isnull=False)
            .order_by("username")
            .distinct()
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        end_date = self.end_date
        context["end_date"] = datetime(
            year=end_date.year,
            month=end_date.month,
            day=end_date.day,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=UTC,
        )
        return context

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context["header"] = ["id", "username", "escrow", "holdings"]
        return context

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Content-Disposition"] = (
            f"attachment; filename=holdings_before_{self.end_date.date()}.csv"
        )
        return response


class CSVReport:
    report_name = "report"
    renderer_classes = [CSVRenderer]
    start_date: datetime
    end_date: datetime

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        name = self.report_name
        if self.start_date:
            name += "-from-" + str(self.start_date.date())
        if self.end_date:
            name += "-to-" + str(self.end_date.date())
        response["Content-Disposition"] = f"attachment; filename={name}.csv"
        return response


class OrderValues(CSVReport, ListAPIView, DateConstrained):
    date_fields = ["paid_on", "refunded_on"]
    serializer_class = DeliverableValuesSerializer
    permission_classes = [IsSuperuser]
    pagination_class = None
    report_name = "order-report"

    def get_queryset(self):
        return (
            Deliverable.objects.filter(escrow_enabled=True)
            .filter(self.date_filter)
            .exclude(
                status__in=[CANCELLED, NEW, PAYMENT_PENDING, WAITING],
            )
            .order_by("paid_on", "created_on")
        )

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context["header"] = [
            "id",
            "paid_on",
            "status",
            "seller",
            "buyer",
            "price",
            "payment_type",
            "created_on",
            "still_in_escrow",
            "artist_earnings",
            "in_reserve",
            "extra",
            "our_fees",
            "sales_tax_collected",
            "card_fees",
            "ach_fees",
            "profit",
            "refunded_on",
            "remote_ids",
        ]
        return context


class SubscriptionReportCSV(CSVReport, ListAPIView, DateConstrained):
    serializer_class = SubscriptionInvoiceSerializer
    permission_classes = [IsSuperuser]
    pagination_class = None
    date_fields = ["paid_on"]
    report_name = "subscription-report"

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context["header"] = [
            "id",
            "paid_on",
            "status",
            "bill_to",
            "blank",
            "total",
            "payment_type",
            "remote_ids",
        ]
        return context

    def get_queryset(self):
        return (
            Invoice.objects.filter(
                type__in=[SUBSCRIPTION, TERM],
                status=PAID,
            )
            .filter(
                line_items__amount__gt=Money("0", "USD"),
            )
            .filter(self.date_filter)
            .distinct()
            .order_by("paid_on")
        )


class UnaffiliatedSaleReportCSV(CSVReport, ListAPIView, DateConstrained):
    serializer_class = UnaffiliatedInvoiceSerializer
    permission_classes = [IsSuperuser]
    pagination_class = None
    date_fields = ["paid_on"]
    report_name = "unaffiliated-sales-report"

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context["header"] = [
            "id",
            "paid_on",
            "total",
            "status",
            "created_on",
            "tax",
            "card_fees",
            "net",
            "source",
            "remote_ids",
        ]
        return context

    def get_queryset(self):
        result = (
            Invoice.objects.filter(
                status=PAID,
                type=SALE,
                targets__isnull=True,
                deliverables__isnull=True,
            )
            .filter(self.date_filter)
            .order_by("paid_on")
        )
        return result


class TipReportCSV(CSVReport, ListAPIView, DateConstrained):
    serializer_class = TipValuesSerializer
    permission_classes = [IsSuperuser]
    pagination_class = None
    date_fields = ["paid_on"]
    report_name = "tip-report"

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context["header"] = [
            "deliverable_id",
            "paid_on",
            "status",
            "issued_by",
            "bill_to",
            "total",
            "payment_type",
            "created_on",
            "id",
            "artist_earnings",
            "blank2",
            "blank3",
            "our_fees",
            "blank4",
            "card_fees",
            "ach_fees",
            "profit",
            "blank5",
            "remote_ids",
        ]
        return context

    def get_queryset(self):
        result = (
            Invoice.objects.filter(
                status=PAID,
                type=TIPPING,
                targets__isnull=True,
                deliverables__isnull=True,
            )
            .filter(self.date_filter)
            .order_by("paid_on")
        )
        return result


class ReconciliationReport(CSVReport, ListAPIView, DateConstrained):
    serializer_class = ReconciliationRecordSerializer
    permission_classes = [StaffPower("view_financials")]
    pagination_class = None
    report_name = "reconciliation-report"

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context["header"] = [
            "finalized_on",
            "amount",
            "invoice_type",
            "category",
            "deliverable",
            "invoice",
            "id",
            "source",
            "destination",
            "payer",
            "payee",
            "remote_ids",
            "targets",
        ]
        return context

    def get_queryset(self):
        return (
            TransactionRecord.objects.filter(
                status=SUCCESS,
            )
            .filter(
                Q(destination=FUND, source__in=[CARD, CASH_DEPOSIT])
                | Q(destination__in=[PAYOUT_ACCOUNT, CARD, CASH_DEPOSIT])
                | Q(source=FUND, payer=None, payee=None)
            )
            .exclude(Q(destination=CARD_TRANSACTION_FEES))
            .filter(self.date_filter)
            .order_by("-finalized_on")
            .exclude(amount=Decimal("0"))
            .distinct()
        )


class PayoutReportCSV(CSVReport, ListAPIView, DateConstrained):
    serializer_class = PayoutTransactionSerializer
    permission_classes = [StaffPower("view_financials")]
    pagination_class = None
    report_name = "payout-report"

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context["header"] = [
            "id",
            "status",
            "payee",
            "targets",
            "amount",
            "fees",
            "total_drafted",
            "created_on",
            "finalized_on",
            "remote_ids",
        ]
        return context

    def get_queryset(self):
        return (
            TransactionRecord.objects.filter(
                payer=F("payee"),
                source=HOLDINGS,
                destination=PAYOUT_ACCOUNT,
            )
            .filter(self.date_filter)
            .exclude(payer=None)
            .exclude(status=FAILURE)
            .order_by("created_on")
        )


class TroubledDeliverables(ListAPIView):
    permission_classes = [
        Or(StaffPower("handle_disputes"), StaffPower("view_financials"))
    ]
    serializer_class = DeliverableSerializer

    def get_queryset(self):
        return (
            Deliverable.objects.filter(
                status__in=[DISPUTED, IN_PROGRESS, QUEUED, PENDING],
                escrow_enabled=True,
            )
            .filter(
                Q(paid_on__lte=timezone.now() - relativedelta(months=4))
                | Q(
                    paid_on__isnull=True,
                    created_on__lte=timezone.now() - relativedelta(months=4),
                ),
            )
            .exclude(Q(order__buyer__isnull=True) & Q(order__customer_email=""))
            .order_by("-status", "paid_on")
        )


class BalanceReport(CSVReport, GenericAPIView, DateConstrained):
    """
    Report that shows the balance for accounts in a period.
    """
    report_name = "journal"
    permission_classes = [IsSuperuser]

    def get(self, request):
        bank_starting_balance = account_balance(
            user=ALL,
            account_type=FUND,
            additional_filters=[Q(finalized_on__lte=self.start_date)],
        )
        bank_ending_balance = account_balance(
            user=ALL,
            account_type=FUND,
            additional_filters=[Q(finalized_on__lt=self.end_date)],
        )
        escrow_starting_balance = account_balance(
            user=ALL,
            account_type=ESCROW,
            additional_filters=[Q(finalized_on__lte=self.start_date)],
        )
        escrow_ending_balance = account_balance(
            user=ALL,
            account_type=ESCROW,
            additional_filters=[Q(finalized_on__lt=self.end_date)],
        )



        return Response(
            data={
                "bank_starting_balance": bank_starting_balance,
                "bank_ending_balance": bank_ending_balance,
                "escrow_starting_balance": escrow_starting_balance,
                "escrow_ending_balance": escrow_ending_balance,
            })

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context["header"] = [
            "bank_starting_balance",
            "bank_ending_balance",
            "escrow_starting_balance",
            "escrow_ending_balance",
        ]
        return context
