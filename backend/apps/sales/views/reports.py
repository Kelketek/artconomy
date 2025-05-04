from datetime import datetime
from decimal import Decimal
from io import BytesIO
from typing import Iterable, TypeVar, Any

import xlsxwriter
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.views import View
from moneyed import Money
from pytz import UTC
from rest_framework import status
from xlsxwriter.format import Format
from xlsxwriter.utility import xl_rowcol_to_cell
from xlsxwriter.worksheet import Worksheet

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
    TOP_UP,
    CARD_MISC_FEES,
    BANK_TRANSFER_FEES,
    BANK_MISC_FEES,
    VENDOR,
)
from apps.sales.models import Deliverable, Invoice, TransactionRecord
from apps.sales.serializers import (
    DeliverableSerializer,
    DeliverableValuesSerializer,
    HoldingsSummarySerializer,
    PayoutTransactionSerializer,
    InvoiceReportSerializer,
    TipValuesSerializer,
    UnaffiliatedInvoiceSerializer,
    ReconciliationRecordSerializer,
)
from apps.sales.utils import PENDING
from dateutil.parser import ParserError, parse
from dateutil.relativedelta import relativedelta
from django.db.models import F, Q
from django.utils import timezone
from django.utils.timezone import make_aware
from rest_framework.generics import ListAPIView
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
    def end_date(self) -> datetime:
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


def range_report_name(
    base_name: str, *, start_date: datetime, end_date: datetime
) -> str:
    name = base_name
    name += "-from-" + str(start_date.date())
    if end_date:
        name += "-to-" + str(end_date.date())
    return name


class CSVReport:
    report_name = "report"
    renderer_classes = [CSVRenderer]
    start_date: datetime
    end_date: datetime

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        name = range_report_name(
            self.report_name,
            start_date=self.start_date,
            end_date=self.end_date,
        )
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
    serializer_class = InvoiceReportSerializer
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


class JournalReport(View, DateConstrained):
    """
    Report that makes it easy to reconcile all activity into Quickbooks.

    Theoretically replaces all other reports, but they remain for diagnostics.
    """

    def get(self, request):
        if not request.user.is_authenticated and request.user.is_superuser:
            return HttpResponse(
                content="Access denied.",
                status=status.HTTP_403_FORBIDDEN,
            )
        report = build_journal_report(
            start_date=self.start_date,
            end_date=self.end_date,
        )
        # Set up the Http response.
        name = range_report_name(
            "journal-report",
            start_date=self.start_date,
            end_date=self.end_date,
        )
        filename = f"{name}.xlsx"
        response = HttpResponse(
            report,
            content_type="application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context["header"] = [
            "bank_starting_balance",
            "bank_ending_balance",
            "escrow_starting_balance",
            "escrow_ending_balance",
        ]
        return context


T = TypeVar("T")


def all_by_date(
    iterables: tuple[tuple[Iterable[T], str, str], ...],
) -> list[tuple[datetime, str, T]]:
    """
    Given disparate types with different applicable dates and their date field, return
    a sorted list that contains tuples of the datetime and the next object.
    """
    entries: list[tuple[datetime, str, T]] = []
    for iterable_set in iterables:
        [iterable, key, label] = iterable_set
        for entry in iterable:
            entries.append((getattr(entry, key), label, entry))
    entries.sort(key=lambda x: x[0])
    return entries


def write_revenue_entries(
    worksheet: Worksheet,
    entries: list[tuple[datetime, str, Any]],
    date_format: Format,
    headers: dict[str, int],
    sum_columns: tuple[str, ...] = tuple(),
    start_row: int = 1,
):
    row = start_row
    for timestamp, label, entry in entries:
        match label:
            case "paid_deliverables":
                data = DeliverableValuesSerializer(instance=entry).data
                del data["refunded"]
            case "refunded_deliverables":
                data = DeliverableValuesSerializer(instance=entry).data
                del data["our_fees"]
                del data["sales_tax_collected"]
                del data["card_fees"]
                del data["price"]
            case "other_invoices":
                if entry.total().amount == Decimal(0):
                    # We should probably find a way not to need these zero invoices.
                    continue
                data = InvoiceReportSerializer(instance=entry).data
                data["buyer"], data["seller"] = data["bill_to"], data["issued_by"]
                data["price"] = data["total"]
                # Do we really need to duplicate this?
                if entry.type != TIPPING:
                    data["subscription"] = data["price"]
                    del data["our_fees"]
            case "top_ups":
                data = ReconciliationRecordSerializer(instance=entry).data
                data["buyer"], data["seller"] = data["payer"], data["payee"]
                data["top_up"] = data["amount"]
                del data["amount"]
            case _:
                raise TypeError(f"Unrecognized label! Found {label}")
        for header, column in headers.items():
            if header in data:
                worksheet.write(row, column, data[header])
        worksheet.write_datetime(row, headers["date"], timestamp, date_format)
        row += 1
    if row != start_row:
        end_row = row - 1
    else:
        end_row = start_row
    row += 1
    for sum_column in sum_columns:
        column_number = headers[sum_column]
        start_cell = xl_rowcol_to_cell(start_row, column_number)
        end_cell = xl_rowcol_to_cell(end_row, column_number)
        worksheet.write(row, column_number, f"=SUM({start_cell}:{end_cell})")


def write_expense_entries(
    worksheet: Worksheet,
    entries: list[tuple[datetime, str, Any]],
    date_format: Format,
    headers: dict[str, int],
    sum_columns: tuple[str, ...] = tuple(),
    start_row: int = 1,
):
    row = start_row
    invoice_type = ContentType.objects.get_for_model(Invoice)
    for timestamp, label, entry in entries:
        data = ReconciliationRecordSerializer(instance=entry).data
        match label:
            case "payouts":
                invoice = entry.targets.filter(content_type=invoice_type).first()
                invoice = invoice and invoice.target
                vendor_invoice = invoice is None or invoice.type == VENDOR
                if vendor_invoice:
                    data["vendor fees"] = data["amount"]
                    del data["amount"]
            case "fees":
                data["processor fees"] = data["amount"]
                del data["amount"]
        for header, column in headers.items():
            if header in data:
                worksheet.write(row, column, data[header])
        worksheet.write_datetime(row, headers["date"], timestamp, date_format)
        row += 1
    if row != start_row:
        end_row = row - 1
    else:
        end_row = start_row
    row += 1
    for sum_column in sum_columns:
        column_number = headers[sum_column]
        start_cell = xl_rowcol_to_cell(start_row, column_number)
        end_cell = xl_rowcol_to_cell(end_row, column_number)
        worksheet.write(row, column_number, f"=SUM({start_cell}:{end_cell})")


def populate_expense_worksheet(
    worksheet: Worksheet,
    *,
    start_date: datetime,
    end_date: datetime,
    date_format: Format,
) -> None:
    """
    Adds the contents of the expense worksheet.
    """
    payouts = TransactionRecord.objects.filter(
        status=SUCCESS,
        payer=F("payee"),
        source=HOLDINGS,
        destination=PAYOUT_ACCOUNT,
        finalized_on__gt=start_date,
        finalized_on__lte=end_date,
    ).exclude(payer=None)
    fees = TransactionRecord.objects.filter(
        payer=None,
        payee=None,
        destination__in=[CARD_MISC_FEES, BANK_TRANSFER_FEES, BANK_MISC_FEES],
        finalized_on__gt=start_date,
        finalized_on__lte=end_date,
    )
    entries = all_by_date(
        iterables=(
            (payouts, "finalized_on", "payouts"),
            (fees, "finalized_on", "fees"),
        ),
    )
    headers: dict[str, int] = {
        key: index
        for index, key in enumerate(
            (
                "id",
                "date",
                "payee",
                "targets",
                "amount",
                "vendor fees",
                "processor fees",
                "remote_ids",
            )
        )
    }
    row = 0
    for header, column in headers.items():
        worksheet.write(row, column, header)
    write_expense_entries(
        worksheet=worksheet,
        entries=entries,
        date_format=date_format,
        headers=headers,
        sum_columns=(
            "amount",
            "vendor fees",
            "processor fees",
        ),
    )
    worksheet.autofit()
    worksheet.set_column(headers["date"], headers["date"], width=20)
    worksheet.set_column(headers["amount"], headers["amount"], width=10)


def populate_revenue_worksheet(
    worksheet: Worksheet,
    *,
    start_date: datetime,
    end_date: datetime,
    date_format: Format,
) -> None:
    """
    Adds the contents of the revenue worksheet.
    """
    paid = Deliverable.objects.filter(
        escrow_enabled=True,
        paid_on__isnull=False,
        paid_on__gte=start_date,
        paid_on__lt=end_date,
    )
    refunded = Deliverable.objects.filter(
        escrow_enabled=True,
        refunded_on__isnull=False,
        refunded_on__gte=start_date,
        refunded_on__lt=end_date,
    )
    invoices = Invoice.objects.filter(
        type__in=(TIPPING, SUBSCRIPTION, TERM),
        record_only=False,
        paid_on__isnull=False,
        paid_on__gte=start_date,
        paid_on__lt=end_date,
    )
    top_ups = TransactionRecord.objects.filter(
        status=SUCCESS,
        finalized_on__isnull=False,
        finalized_on__gte=start_date,
        finalized_on__lt=end_date,
        payer=None,
        payee=None,
        category=TOP_UP,
    )
    entries = all_by_date(
        iterables=(
            (paid, "paid_on", "paid_deliverables"),
            (refunded, "refunded_on", "refunded_deliverables"),
            (invoices, "paid_on", "other_invoices"),
            (top_ups, "finalized_on", "top_ups"),
        ),
    )
    headers: dict[str, int] = {
        key: index
        for index, key in enumerate(
            (
                "id",
                "date",
                "status",
                "seller",
                "buyer",
                "price",
                "card_fees",
                "our_fees",
                "subscription",
                "refunded",
                "sales_tax_collected",
                "top_up",
                "remote_ids",
            )
        )
    }
    row = 0
    for header, column in headers.items():
        worksheet.write(row, column, header)
    write_revenue_entries(
        worksheet=worksheet,
        entries=entries,
        date_format=date_format,
        headers=headers,
        sum_columns=(
            "price",
            "card_fees",
            "our_fees",
            "subscription",
            "refunded",
            "sales_tax_collected",
            "top_up",
        ),
    )
    worksheet.autofit()
    worksheet.set_column(headers["date"], headers["date"], width=20)
    worksheet.set_column(headers["price"], headers["price"], width=10)


def build_journal_report(*, start_date: datetime, end_date: datetime) -> BytesIO:
    """
    Build the journal report XLSX file.
    """
    output = BytesIO()
    workbook = xlsxwriter.Workbook(
        output,
        options={
            "in_memory": True,
            "remove_timezone": True,
        },
    )
    date_format = workbook.add_format(
        {
            "num_format": "YYYY/mm/dd hh:mm:ss",
            "align": "left",
        }
    )
    revenue = workbook.add_worksheet("revenue")
    expense = workbook.add_worksheet("expense")
    populate_revenue_worksheet(
        revenue,
        start_date=start_date,
        end_date=end_date,
        date_format=date_format,
    )
    populate_expense_worksheet(
        expense,
        start_date=start_date,
        end_date=end_date,
        date_format=date_format,
    )
    workbook.close()
    output.seek(0)
    return output
