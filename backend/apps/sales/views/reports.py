from datetime import datetime
from typing import Union

from dateutil.parser import parse, ParserError
from dateutil.relativedelta import relativedelta
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.timezone import make_aware
from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework_csv.renderers import CSVRenderer

from apps.profiles.models import User
from apps.profiles.permissions import IsSuperuser, UserControls
from apps.sales.constants import CANCELLED, NEW, PAYMENT_PENDING, WAITING, \
    FAILURE, PAID, SALE, HOLDINGS, BANK, PAYOUT_MIRROR_SOURCE, PAYOUT_MIRROR_DESTINATION, TIPPING, SUBSCRIPTION, TERM
from apps.sales.models import Deliverable, TransactionRecord, Invoice
from apps.sales.serializers import DeliverableValuesSerializer, \
    UnaffiliatedInvoiceSerializer, PayoutTransactionSerializer, UserPayoutTransactionSerializer, \
    HoldingsSummarySerializer, TipValuesSerializer, SubscriptionInvoiceSerializer


class CustomerHoldingsCSV(ListAPIView):
    serializer_class = HoldingsSummarySerializer
    permission_classes = [IsSuperuser]
    pagination_class = None
    renderer_classes = [CSVRenderer]

    def get_queryset(self):
        return User.objects.filter(guest=False, sales__isnull=False).order_by('username').distinct()

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = ['id', 'username', 'escrow', 'holdings']
        return context

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Content-Disposition'] = f'attachment; filename=holdings.csv'
        return response


class DateConstrained:
    request: Request
    date_field = 'created_on'

    @property
    def start_date(self) -> datetime:
        start_date = None
        default_start = timezone.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0,
        )
        default_start -= relativedelta(months=2)
        date_string = self.request.GET.get('start_date', '')
        try:
            start_date = make_aware(parse(date_string))
        except ParserError:
            pass
        if not start_date:
            start_date = default_start
        return start_date

    @property
    def end_date(self) -> Union[datetime, None]:
        end_date = None
        date_string = self.request.GET.get('end_date', '')
        default_end = timezone.now()
        try:
            end_date = make_aware(parse(date_string))
        except ParserError:
            pass
        if not end_date:
            end_date = default_end
        return end_date

    @property
    def date_kwargs(self):
        kwargs = {
            f'{self.date_field}__gte': self.start_date,
            f'{self.date_field}__lte': self.end_date,
        }
        return kwargs


class CSVReport:
    report_name = 'report'
    renderer_classes = [CSVRenderer]
    start_date: datetime
    end_date: datetime

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        name = self.report_name
        if self.start_date:
            name += '-from-' + str(self.start_date.date())
        if self.end_date:
            name += '-to-' + str(self.end_date.date())
        response['Content-Disposition'] = f'attachment; filename={name}.csv'
        return response


class OrderValues(CSVReport, ListAPIView, DateConstrained):
    date_field = 'paid_on'
    serializer_class = DeliverableValuesSerializer
    permission_classes = [IsSuperuser]
    pagination_class = None
    report_name = 'order-report'

    def get_queryset(self):
        return Deliverable.objects.filter(escrow_enabled=True, **self.date_kwargs).exclude(
            status__in=[CANCELLED, NEW, PAYMENT_PENDING, WAITING],
        ).order_by('paid_on')

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = [
            'id',
            'paid_on',
            'status',
            'seller',
            'buyer',
            'price',
            'payment_type',
            'created_on',
            'still_in_escrow',
            'artist_earnings',
            'in_reserve',
            'extra',
            'our_fees',
            'sales_tax_collected',
            'card_fees',
            'ach_fees',
            'profit',
            'refunded_on',
            'remote_ids',
        ]
        return context


class SubscriptionReportCSV(CSVReport, ListAPIView, DateConstrained):
    serializer_class = SubscriptionInvoiceSerializer
    permission_classes = [IsSuperuser]
    pagination_class = None
    date_field = 'paid_on'
    report_name = 'subscription-report'

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = [
            'id',
            'paid_on',
            'status',
            'bill_to',
            'blank',
            'total',
            'payment_type',
            'remote_ids',
        ]
        return context

    def get_queryset(self):
        return Invoice.objects.filter(
            type__in=[SUBSCRIPTION, TERM],
            status=PAID,
            **self.date_kwargs,
        ).order_by('paid_on')


class UnaffiliatedSaleReportCSV(CSVReport, ListAPIView, DateConstrained):
    serializer_class = UnaffiliatedInvoiceSerializer
    permission_classes = [IsSuperuser]
    pagination_class = None
    date_field = 'paid_on'
    report_name = 'unaffiliated-sales-report'

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = [
            'id',
            'paid_on',
            'total',
            'status',
            'created_on',
            'tax',
            'card_fees',
            'net',
            'source',
            'remote_ids',
        ]
        return context

    def get_queryset(self):
        result = Invoice.objects.filter(
            status=PAID,
            **self.date_kwargs,
            type=SALE,
            targets__isnull=True,
            deliverables__isnull=True,
        ).order_by('paid_on')
        return result


class TipReportCSV(CSVReport, ListAPIView, DateConstrained):
    serializer_class = TipValuesSerializer
    permission_classes = [IsSuperuser]
    pagination_class = None
    date_field = 'paid_on'
    report_name = 'tip-report'

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = [
            'id',
            'paid_on',
            'status',
            'issued_by',
            'bill_to',
            'total',
            'payment_type',
            'created_on',
            'blank1',
            'artist_earnings',
            'blank2',
            'blank3',
            'our_fees',
            'blank4',
            'card_fees',
            'ach_fees',
            'profit',
            'blank5',
            'remote_ids',
        ]
        return context

    def get_queryset(self):
        result = Invoice.objects.filter(
            status=PAID,
            **self.date_kwargs,
            type=TIPPING,
            targets__isnull=True,
            deliverables__isnull=True,
        ).order_by('paid_on')
        return result


class PayoutReportCSV(CSVReport, ListAPIView, DateConstrained):
    serializer_class = PayoutTransactionSerializer
    permission_classes = [IsSuperuser]
    pagination_class = None
    report_name = 'payout-report'

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = [
            'id',
            'status',
            'payee',
            'targets',
            'amount',
            'fees',
            'total_drafted',
            'created_on',
            'finalized_on',
            'remote_ids',
        ]
        return context

    def get_queryset(self):
        return TransactionRecord.objects.filter(
            payer=F('payee'),
            source=HOLDINGS,
            destination=BANK,
            **self.date_kwargs,
        ).exclude(payer=None).exclude(status=FAILURE).order_by('created_on')


class UserPayoutReportCSV(CSVReport, ListAPIView, DateConstrained):
    serializer_class = UserPayoutTransactionSerializer
    permission_classes = [UserControls]
    pagination_class = None
    date_field = 'finalized_on'
    report_name = 'user-payout-report'

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = [
            'id',
            'status',
            'targets',
            'amount',
            'currency',
            'created_on',
            'finalized_on',
            'remote_ids',
        ]
        return context

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return TransactionRecord.objects.filter(
            payer=user,
            payee=user,
            source=PAYOUT_MIRROR_SOURCE,
            destination=PAYOUT_MIRROR_DESTINATION,
            **self.date_kwargs,
        ).exclude(payer=None).exclude(status=FAILURE).order_by('finalized_on')
