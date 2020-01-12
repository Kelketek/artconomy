from collections import OrderedDict
from functools import lru_cache
from typing import Union, List
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import login
from django.contrib.contenttypes.models import ContentType
from django.views.static import serve
from django.db.models import When, F, Case, BooleanField, Q, Count, QuerySet, IntegerField
from django.shortcuts import get_object_or_404
from django.utils import timezone

# Create your views here.
from math import ceil

from django.utils.datetime_safe import date
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from moneyed import Money, Decimal
# BDay is business day, not birthday.
from pandas.tseries.offsets import BDay
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, RetrieveAPIView, \
    GenericAPIView, ListAPIView, DestroyAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from short_stuff import slugify

from apps.lib.models import DISPUTE, REFUND, COMMENT, Subscription, ORDER_UPDATE, SALE_UPDATE, REVISION_UPLOADED, \
    NEW_PRODUCT, STREAMING
from apps.lib.permissions import IsStaff, IsSafeMethod, Any, All, IsMethod
from apps.lib.utils import notify, recall_notification, demark, preview_rating, send_transaction_email
from apps.lib.views import BasePreview
from apps.profiles.models import User, Submission, HAS_US_ACCOUNT, NO_US_ACCOUNT, VERIFIED
from apps.profiles.permissions import ObjectControls, UserControls, IsUser, IsSuperuser, IsRegistered
from apps.profiles.serializers import UserSerializer, SubmissionSerializer
from apps.profiles.utils import credit_referral, create_guest_user, empty_user
from apps.sales.authorize import AuthorizeException, charge_saved_card, CardInfo, AddressInfo, \
    create_customer_profile, charge_card, card_token_from_transaction, get_card_type
from apps.sales.dwolla import add_bank_account, make_dwolla_account, \
    destroy_bank_account
from apps.sales.permissions import (
    OrderViewPermission, OrderSellerPermission, OrderBuyerPermission,
    OrderPlacePermission, EscrowPermission, EscrowDisabledPermission, RevisionsVisible,
    BankingConfigured,
    OrderStatusPermission, HasRevisionsPermission, OrderTimeUpPermission, NoOrderOutput, PaidOrderPermission)
from apps.sales.models import Product, Order, CreditCardToken, Revision, BankAccount, \
    WEIGHTED_STATUSES, Rating, TransactionRecord, buyer_subscriptions
from apps.sales.serializers import (
    ProductSerializer, ProductNewOrderSerializer, OrderViewSerializer, CardSerializer,
    NewCardSerializer, PaymentSerializer, RevisionSerializer,
    AccountBalanceSerializer, BankAccountSerializer, TransactionRecordSerializer,
    RatingSerializer,
    ServicePaymentSerializer, SearchQuerySerializer, NewInvoiceSerializer,
    HoldingsSummarySerializer, ProductSampleSerializer, OrderPreviewSerializer,
    AccountQuerySerializer, OrderCharacterTagSerializer, SubmissionFromOrderSerializer, OrderAuthSerializer)
from apps.sales.utils import available_products, service_price, set_service, \
    check_charge_required, available_products_by_load, finalize_order, account_balance, split_fee, \
    recuperate_fee, ALL, POSTED_ONLY, PENDING, transfer_order, early_finalize, cancel_order
from apps.sales.tasks import renew


class ProductList(ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [Any(IsSafeMethod, All(IsRegistered, UserControls))]

    def get(self, *args, **kwargs):
        self.check_object_permissions(self.request, self.request.subject)
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.check_object_permissions(self.request, self.request.subject)
        return super().post(*args, **kwargs)

    def perform_create(self, serializer):
        product = serializer.save(owner=self.request.subject, user=self.request.subject)
        if not product.hidden:
            notify(NEW_PRODUCT, self.request.subject, data={'product': product.id}, unique_data=True)
        return product

    def get_queryset(self):
        username = self.kwargs['username']
        qs = Product.objects.filter(user__username__iexact=self.kwargs['username'], active=True)
        if not (self.request.user.username.lower() == username.lower() or self.request.user.is_staff):
            qs = qs.filter(available=True, hidden=False)
        qs = qs.order_by('-created_on')
        return qs


class ProductManager(RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [Any(IsSafeMethod, All(IsRegistered, ObjectControls))]

    def perform_update(self, serializer):
        super().perform_update(serializer)
        # post-save effects will change values.
        serializer.instance.refresh_from_db()

    @lru_cache()
    def get_object(self):
        product = get_object_or_404(
            Product, user__username=self.kwargs['username'], id=self.kwargs['product'], active=True
        )
        hit_count = HitCount.objects.get_for_object(product)
        HitCountMixin.hit_count(self.request, hit_count)
        self.check_object_permissions(self.request, product)
        return product


class ProductSamples(ListCreateAPIView):
    serializer_class = ProductSampleSerializer
    permission_classes = [Any(IsSafeMethod, All(IsRegistered, ObjectControls))]

    @lru_cache()
    def get_object(self):
        product = get_object_or_404(
            Product, id=self.kwargs['product'], user__username=self.kwargs['username'], active=True,
        )
        self.check_object_permissions(self.request, product)
        return product

    def get_queryset(self) -> QuerySet:
        product = self.get_object()
        samples = Product.samples.through.objects.filter(product=self.get_object())
        if not self.request.user == product.user:
            samples = samples.exclude(submission__private=True)
        return samples.order_by('-submission__created_on')

    def perform_create(self, serializer):
        instance, _ = Product.samples.through.objects.get_or_create(
            product=self.get_object(), submission_id=serializer.validated_data['submission_id'],
        )
        serializer.instance = instance
        return instance


class ProductSampleManager(DestroyAPIView):
    permission_classes = [IsRegistered, ObjectControls]
    serializer_class = ProductSampleSerializer

    def get_object(self) -> Submission.artists.through:
        return get_object_or_404(
            Product.samples.through, id=self.kwargs['tag_id'],
            product__id=self.kwargs['product'],
            product__active=True,
        )

    def perform_destroy(self, instance: Submission.artists.through):
        self.check_object_permissions(self.request, instance.product)
        if instance.product.primary_submission == instance.submission:
            instance.product.primary_submission = None
            instance.product.save()
        instance.delete()



class PlaceOrder(CreateAPIView):
    serializer_class = ProductNewOrderSerializer
    permission_classes = [OrderPlacePermission]

    def perform_create(self, serializer):
        product = get_object_or_404(Product, id=self.kwargs['product'], active=True)
        self.check_object_permissions(self.request, product)
        user = self.request.user
        if not user.is_authenticated:
            user = create_guest_user(serializer.validated_data['email'])
            login(self.request, user)
        elif not user.is_registered:
            if self.request.user.guest_email != serializer.validated_data['email']:
                user = create_guest_user(serializer.validated_data['email'])
                login(self.request, user)
        order = serializer.save(
            product=product, buyer=user, seller=product.user,
            escrow_disabled=product.user.artist_profile.escrow_disabled,
        )
        if not user.guest:
            for character in order.characters.all():
                character.shared_with.add(order.seller)
        else:
            order.customer_email = user.guest_email
            order.save()
        notify(SALE_UPDATE, order, unique=True, mark_unread=True)
        notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
        return order

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = self.perform_create(serializer)
        serializer = OrderViewSerializer(instance=order, context=self.get_serializer_context())
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OrderManager(RetrieveUpdateAPIView):
    permission_classes = [OrderViewPermission]
    serializer_class = OrderViewSerializer

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return order


class OrderInvite(GenericAPIView):
    permission_classes = [OrderSellerPermission]
    serializer_class = OrderViewSerializer

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        return order

    def post(self, request, **kwargs):
        order = self.get_object()
        self.check_object_permissions(self.request, order)
        if order.buyer and not order.buyer.guest:
            return Response(data={'detail': 'This order has already been claimed.'}, status=status.HTTP_400_BAD_REQUEST)
        if not order.customer_email:
            return Response(
                data={'detail': 'Customer email not set. Cannot send an invite!'}, status=status.HTTP_400_BAD_REQUEST,
            )
        if order.buyer:
            order.buyer.guest_email = order.customer_email
            order.buyer.save()
            subject = f'Claim Link for order #{order.id}.'
            template = 'new_claim_link.html'
        else:
            subject = f'You have a new invoice from {order.seller.username}!'
            template = 'invoice_issued.html'
        send_transaction_email(
            subject,
            template, order.customer_email,
            {'order': order, 'claim_token': slugify(order.claim_token)}
        )
        return Response(status=status.HTTP_200_OK, data=self.get_serializer(instance=order).data)


class OrderAccept(GenericAPIView):
    permission_classes = [
        OrderSellerPermission,
        OrderStatusPermission(Order.NEW, error_message="Approval can only be applied to new orders."),
    ]

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return order

    def post(self, request, *args, **kwargs):
        order = self.get_object()
        order.status = Order.PAYMENT_PENDING
        order.price = order.product.price
        order.task_weight = order.product.task_weight
        order.expected_turnaround = order.product.expected_turnaround
        order.revisions = order.product.revisions
        if order.total() <= Money('0', 'USD'):
            order.status = Order.QUEUED
            order.revisions_hidden = False
            order.escrow_disabled = True
        order.save()
        data = OrderViewSerializer(instance=order, context=self.get_serializer_context()).data
        notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
        return Response(data)


class MarkPaid(GenericAPIView):
    permission_classes = [
        OrderSellerPermission,
        OrderStatusPermission(
            Order.PAYMENT_PENDING,
            error_message='You can only mark orders paid if they are waiting for payment.',
        ),
    ]
    serializer_class = OrderViewSerializer

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'])

    def post(self, request, **_kwargs):
        order = self.get_object()
        self.check_object_permissions(request, order)
        if order.final_uploaded:
            order.status = Order.COMPLETED
        elif order.revision_set.all():
            order.status = Order.IN_PROGRESS
        else:
            order.status = Order.QUEUED
        if order.product:
            order.task_weight = order.product.task_weight
            order.expected_turnaround = order.product.expected_turnaround
            order.revisions = order.product.revisions
        order.revisions_hidden = False
        order.commission_info = order.seller.artist_profile.commission_info
        order.escrow_disabled = True
        order.save()
        data = self.serializer_class(instance=order, context=self.get_serializer_context()).data
        notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
        return Response(data)


class OrderStart(GenericAPIView):
    permission_classes = [
        OrderSellerPermission,
        OrderStatusPermission(
            Order.QUEUED,
            error_message='You can only start orders that are queued.',
        ),
    ]
    serializer_class = OrderViewSerializer

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return order

    def post(self, *args, **kwargs):
        order = self.get_object()
        order.started_on = timezone.now()
        order.status = Order.IN_PROGRESS
        order.save()
        notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
        if not order.private and order.stream_link:
            notify(
                STREAMING, order.seller,
                data={'order': order.id}, unique_data=True,
                exclude=[order.buyer, order.seller]
            )
        return Response(data=OrderViewSerializer(instance=order, context=self.get_serializer_context()).data)


class OrderCancel(GenericAPIView):
    permission_classes = [
        OrderViewPermission,
        OrderStatusPermission(
            Order.NEW, Order.PAYMENT_PENDING,
            error_message='You cannot cancel this order. It is either already cancelled, finalized, '
                          'or must be refunded instead.',
        ),
    ]
    serializer_class = OrderViewSerializer

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return order

    # noinspection PyUnusedLocal
    def post(self, request, order_id):
        order = self.get_object()
        cancel_order(order, self.request.user)
        data = self.serializer_class(instance=order, context=self.get_serializer_context()).data
        return Response(data)


class OrderRevisions(ListCreateAPIView):
    permission_classes = [
        Any(
            All(IsSafeMethod, OrderViewPermission, Any(RevisionsVisible, OrderSellerPermission)),
            All(OrderSellerPermission, IsMethod('POST'), OrderStatusPermission(
                Order.IN_PROGRESS, Order.PAYMENT_PENDING, Order.NEW, Order.QUEUED, Order.DISPUTED,
                error_message='You may not upload revisions while the order is in this state.',
            )),
        ),
    ]
    pagination_class = None
    serializer_class = RevisionSerializer

    @lru_cache()
    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'])

    def get_queryset(self):
        order = self.get_object()
        return order.revision_set.all()

    def get(self, *args, **kwargs):
        order = self.get_object()
        self.check_object_permissions(self.request, order)
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        order = self.get_object()
        self.check_object_permissions(self.request, order)
        return super().post(*args, **kwargs)

    def perform_create(self, serializer):
        order = self.get_object()
        revision = serializer.save(order=order, owner=self.request.user, rating=order.rating)
        order.refresh_from_db()
        if order.status == Order.QUEUED:
            order.status = Order.IN_PROGRESS
        if serializer.validated_data.get('final'):
            order.final_uploaded = True
            if order.escrow_disabled:
                order.status = Order.COMPLETED
            elif order.status == Order.IN_PROGRESS:
                order.status = Order.REVIEW
                order.auto_finalize_on = (timezone.now() + relativedelta(days=5)).date()
                early_finalize(order, self.request.user)
            order.save()
            notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
        else:
            notify(REVISION_UPLOADED, order, data={'revision': revision.id}, unique_data=True, mark_unread=True)
        order.save()
        recall_notification(STREAMING, order.seller, data={'order': order.id})
        return revision


delete_forbidden_message = 'You may not remove revisions from this order. They are either locked or under dispute.'


class DeleteOrderRevision(DestroyAPIView):
    permission_classes = [
        OrderSellerPermission,
        Any(
            OrderStatusPermission(
                Order.REVIEW, Order.PAYMENT_PENDING, Order.NEW, Order.IN_PROGRESS,
                error_message=delete_forbidden_message,
            ),
            All(
                EscrowDisabledPermission,
                OrderStatusPermission(
                    Order.COMPLETED,
                    error_message=delete_forbidden_message,
            )),
        ),
    ]
    serializer_class = RevisionSerializer

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        revision = get_object_or_404(Revision, id=self.kwargs['revision_id'], order_id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return revision

    def perform_destroy(self, instance):
        revision_id = instance.id
        super(DeleteOrderRevision, self).perform_destroy(instance)
        order = Order.objects.get(id=self.kwargs['order_id'])
        recall_notification(REVISION_UPLOADED, order, data={'revision': revision_id}, unique_data=True)
        if order.final_uploaded:
            order.final_uploaded = False
        if order.status in [Order.REVIEW, Order.COMPLETED]:
            order.auto_finalize_on = None
            order.status = Order.IN_PROGRESS
        order.save()


reopen_error_message = 'This order cannot be reopened.'


class ReOpen(GenericAPIView):
    serializer_class = OrderViewSerializer
    permission_classes = [
        OrderSellerPermission,
        Any(
            OrderStatusPermission(
                Order.REVIEW, Order.PAYMENT_PENDING, Order.DISPUTED, error_message=reopen_error_message,
            ),
            All(EscrowDisabledPermission, OrderStatusPermission(Order.COMPLETED, error_message=reopen_error_message)),
        )
    ]

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'])

    def post(self, _request, *_args, **_kwargs):
        order = self.get_object()
        self.check_object_permissions(self.request, order)
        if order.status not in [Order.PAYMENT_PENDING, Order.DISPUTED]:
            order.status = Order.IN_PROGRESS
        order.final_uploaded = False
        order.auto_finalize_on = None
        order.save()
        notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
        serializer = self.get_serializer(instance=order)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class MarkComplete(GenericAPIView):
    serializer_class = OrderViewSerializer
    permission_classes = [
        OrderSellerPermission,
        OrderStatusPermission(
            Order.IN_PROGRESS,
            Order.PAYMENT_PENDING,
            error_message='You cannot mark an order complete if it is not in progress.',
        ),
        HasRevisionsPermission,
    ]

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'])

    def post(self, _request, *_args, **_kwargs):
        order = self.get_object()
        self.check_object_permissions(self.request, order)
        if order.revision_set.all().exists() and order.status == Order.PAYMENT_PENDING:
            order.final_uploaded = True
            order.save()
            serializer = self.get_serializer(instance=order)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        order.final_uploaded = True
        if order.escrow_disabled:
            order.status = Order.COMPLETED
        else:
            order.status = Order.REVIEW
            order.auto_finalize_on = (timezone.now() + relativedelta(days=2)).date()
            early_finalize(order, self.request.user)
        order.save()
        notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
        serializer = self.get_serializer(instance=order)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class StartDispute(GenericAPIView):
    permission_classes = [
        OrderBuyerPermission, EscrowPermission,
        OrderStatusPermission(
            Order.REVIEW, Order.IN_PROGRESS, Order.QUEUED, error_message='This order is not in a disputable state.',
        ),
        # Slight redundancy here to ensure the right error messages display.
        Any(
            All(OrderTimeUpPermission, OrderStatusPermission(Order.IN_PROGRESS, Order.QUEUED)),
            OrderStatusPermission(Order.REVIEW),
        )
    ]
    serializer_class = OrderViewSerializer

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'])

    def post(self, _request, *_args, **_kwargs):
        order = self.get_object()
        self.check_object_permissions(self.request, order)
        order.status = Order.DISPUTED
        order.disputed_on = timezone.now()
        order.save()
        notify(DISPUTE, order, unique=True, mark_unread=True)
        notify(SALE_UPDATE, order, unique=True, mark_unread=True)
        serializer = self.get_serializer(instance=order)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ClaimDispute(GenericAPIView):
    permission_classes = [IsStaff]
    serializer_class = OrderViewSerializer

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'])

    # noinspection PyUnusedLocal
    def post(self, request, order_id):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        if obj.arbitrator and obj.arbitrator != request.user:
            raise PermissionDenied("An arbitrator has already been assigned to this dispute.")
        obj.arbitrator = request.user
        obj.save()
        Subscription.objects.get_or_create(
            type=COMMENT,
            object_id=obj.id,
            content_type=ContentType.objects.get_for_model(obj),
            subscriber=request.user,
            email=True,
        )
        Subscription.objects.get_or_create(
            type=REVISION_UPLOADED,
            object_id=obj.id,
            content_type=ContentType.objects.get_for_model(obj),
            subscriber=request.user,
            email=True,
        )
        serializer = self.get_serializer(instance=obj)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class OrderRefund(GenericAPIView):
    permission_classes = [
        OrderSellerPermission,
        OrderStatusPermission(
            Order.QUEUED, Order.IN_PROGRESS, Order.REVIEW, Order.DISPUTED,
            error_message='This order is not in a refundable state.',
        )
    ]
    serializer_class = OrderViewSerializer

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'])

    def post(self, request, *_args, **_kwargs):
        order = self.get_object()
        self.check_object_permissions(self.request, order)
        if order.escrow_disabled:
            order.status = order.REFUNDED
            order.save()
            notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
            serializer = self.get_serializer(instance=order, context=self.get_serializer_context())
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        order_type = ContentType.objects.get_for_model(order)
        original_record = TransactionRecord.objects.get(
            object_id=order.id, content_type=order_type, payer=order.buyer,
            payee=order.seller,
            destination=TransactionRecord.ESCROW,
            status=TransactionRecord.SUCCESS,
        )
        record = original_record.refund()
        if record.status == TransactionRecord.FAILURE:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': record.response_message})
        order.status = Order.REFUNDED
        order.save()
        recuperate_fee(original_record)
        notify(REFUND, order, unique=True, mark_unread=True)
        notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
        if request.user != order.seller:
            notify(SALE_UPDATE, order, unique=True, mark_unread=True)
        serializer = self.get_serializer(instance=order, context=self.get_serializer_context())
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ApproveFinal(GenericAPIView):
    permission_classes = [
        OrderBuyerPermission, EscrowPermission,
        OrderStatusPermission(Order.REVIEW, Order.DISPUTED, error_message='This order is not in an approvable state.')
    ]
    serializer_class = OrderViewSerializer

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'])

    def post(self, request, *_args, **_kwargs):
        order = self.get_object()
        self.check_object_permissions(self.request, order)
        finalize_order(order, request.user)
        return Response(
            status=status.HTTP_200_OK,
            data=OrderViewSerializer(instance=order, context=self.get_serializer_context()).data
        )


class CurrentMixin(object):
    @staticmethod
    def extra_filter(qs):
        return qs.exclude(status__in=[Order.COMPLETED, Order.CANCELLED, Order.REFUNDED])


class ArchivedMixin(object):
    @staticmethod
    def extra_filter(qs):
        return qs.filter(status=Order.COMPLETED)


class CancelledMixin(object):
    @staticmethod
    def extra_filter(qs):
        return qs.filter(status__in=[Order.CANCELLED, Order.REFUNDED])


class OrderListBase(ListAPIView):
    permission_classes = [ObjectControls]
    serializer_class = OrderPreviewSerializer

    @staticmethod
    def extra_filter(qs):  # pragma: no cover
        return qs

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        return self.extra_filter(self.user.buys.all())

    # noinspection PyAttributeOutsideInit
    def get(self, *args, **kwargs):
        self.user = self.get_object()
        self.check_object_permissions(self.request, self.user)
        return super().get(*args, **kwargs)


class CurrentOrderList(CurrentMixin, OrderListBase):
    pass


class ArchivedOrderList(ArchivedMixin, OrderListBase):
    pass


class CancelledOrderList(CancelledMixin, OrderListBase):
    pass


class SalesListBase(ListAPIView):
    permission_classes = [ObjectControls]
    serializer_class = OrderPreviewSerializer

    @staticmethod
    def extra_filter(qs):  # pragma: no cover
        return qs

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        return self.extra_filter(self.user.sales.all())

    def get(self, *args, **kwargs):
        # noinspection PyAttributeOutsideInit
        self.user = self.get_object()
        self.check_object_permissions(self.request, self.user)
        return super().get(*args, **kwargs)


class CurrentSalesList(CurrentMixin, SalesListBase):
    pass


class ArchivedSalesList(ArchivedMixin, SalesListBase):
    pass


class CancelledSalesList(CancelledMixin, SalesListBase):
    pass


class CasesListBase(ListAPIView):
    permission_classes = [ObjectControls, IsStaff]
    serializer_class = OrderPreviewSerializer

    @staticmethod
    def extra_filter(qs):  # pragma: no cover
        return qs

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        self.check_object_permissions(self.request, self.user)
        return self.extra_filter(self.user.cases.all())

    def get(self, *args, **kwargs):
        # noinspection PyAttributeOutsideInit
        self.user = self.get_object()
        self.check_object_permissions(self.request, self.user)
        return super().get(*args, **kwargs)


class CurrentCasesList(CurrentMixin, CasesListBase):
    pass


class ArchivedCasesList(ArchivedMixin, CasesListBase):
    pass


class CancelledCasesList(CancelledMixin, CasesListBase):
    pass


class CardList(ListCreateAPIView):
    permission_classes = [
        Any(
            All(IsSafeMethod, UserControls),
            All(IsRegistered, UserControls),
        ),
    ]
    serializer_class = NewCardSerializer
    pagination_class = None

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        qs = user.credit_cards.filter(active=True)
        # Primary card should always be listed first.
        qs = qs.annotate(
            primary=Case(
                When(
                    user__primary_card_id=F('id'),
                    then=1
                ),
                default=0,
                output_field=BooleanField()
            )
        )
        return qs.order_by('-primary', '-created_on')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NewCardSerializer
        else:
            return CardSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            token = self.perform_create(serializer)
        except AuthorizeException as err:
            return Response(data={'detail': str(err)}, status=status.HTTP_400_BAD_REQUEST)
        if token.user.landscape_enabled:
            renew.delay(token.user.id, 'landscape')
        elif token.user.portrait_enabled:
            renew.delay(token.user.id, 'portrait')
        serializer = CardSerializer(instance=token)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        data = serializer.validated_data
        user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return CreditCardToken.create(
            first_name=data['first_name'], last_name=data['last_name'], country=data['country'],
            user=user, exp_month=data['exp_date'].month, exp_year=data['exp_date'].year,
            number=data['number'], cvv=data['cvv'], zip_code=data.get('zip'),
            make_primary=data['make_primary']
        )


class CardManager(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsRegistered, ObjectControls]
    serializer_class = NewCardSerializer

    def get_object(self):
        card = get_object_or_404(
            CreditCardToken, user__username=self.kwargs['username'], id=self.kwargs['card_id'], active=True
        )
        self.check_object_permissions(self.request, card)
        return card

    def perform_destroy(self, instance):
        instance.mark_deleted()


class MakePrimary(APIView):
    serializer_class = CardSerializer
    permission_classes = [IsRegistered, ObjectControls]

    def get_object(self):
        return get_object_or_404(
            CreditCardToken, id=self.kwargs['card_id'], user__username=self.kwargs['username'],
            active=True
        )

    # noinspection PyUnusedLocal
    def post(self, *args, **kwargs):
        card = self.get_object()
        self.check_object_permissions(self.request, card)
        card.user.primary_card = card
        card.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PaymentMixin:
    def perform_charge(
            self, data: dict, amount: Money, user: User,
    ) -> (bool, Union[Response, List[TransactionRecord]]):
        if data.get('card_id'):
            return self.charge_existing_card(data, amount, user)
        else:
            return self.charge_new_card(data, amount, user)

    def annotate_error(self, transactions: List[TransactionRecord], err: Exception) -> (False, Response):
        response_message = str(err)
        for transaction in transactions:
            transaction.response_message = response_message
            transaction.save()
        return False, Response(
            status=status.HTTP_400_BAD_REQUEST, data={'detail': response_message}
        )

    def charge_new_card(
            self, data: dict, amount: Money, user: User,
    ) -> (bool, Union[Response, TransactionRecord]):
        card_info = CardInfo(
            number=data['number'],
            exp_year=data['exp_date'].year,
            exp_month=data['exp_date'].month,
            cvv=data.get('cvv', None),
        )
        address_info = AddressInfo(
            first_name=data['first_name'],
            last_name=data['last_name'],
            postal_code=data['zip'],
            country=data['country'],
        )
        if not user.authorize_token:
            user.authorize_token = create_customer_profile(user.email)
            user.save()
        transactions = self.init_transactions(data, amount, user)
        try:
            remote_id = charge_card(card_info, address_info, amount.amount)
        except Exception as err:
            return self.annotate_error(transactions, err)
        for transaction in transactions:
            transaction.status = TransactionRecord.SUCCESS
            transaction.remote_id = remote_id
        self.post_success(transactions, data, user)
        for transaction in transactions:
            transaction.save()

        card_args = dict(
            type=CreditCardToken.TYPE_TRANSLATION[get_card_type(data['number'])],
            cvv_verified=True, user=user, last_four=data['number'][-4:],
        )
        if data['save_card'] and user.is_registered:
            card_args['token'] = card_token_from_transaction(remote_id, profile_id=user.authorize_token)
        else:
            card_args['token'] = 'XXXX'
            card_args['active'] = False
        card = CreditCardToken.objects.create(**card_args)
        if card.active and (user.primary_card is None or data['make_primary']):
            user.primary_card = card
            user.save()
        for transaction in transactions:
            transaction.card = card
            transaction.save()

        return True, transactions

    def charge_existing_card(self, data: dict, amount: Money, user: User):
        card = get_object_or_404(CreditCardToken, id=data['card_id'], active=True, user=user)
        if not card.cvv_verified and not data.get('cvv', None):
            return False, Response(
                status=status.HTTP_400_BAD_REQUEST, data={'detail': 'You must enter the security code for this card.'}
            )
        transactions = self.init_transactions(data, amount, user)
        for transaction in transactions:
            transaction.card = card
        try:
            remote_id = charge_saved_card(
                profile_id=card.profile_id,
                payment_id=card.payment_id, amount=amount.amount, cvv=data.get('cvv', None),
            )
        except Exception as err:
            return self.annotate_error(transactions, err)
        for transaction in transactions:
            transaction.status = TransactionRecord.SUCCESS
            transaction.remote_id = remote_id
        self.post_success(transactions, data, user)
        for transaction in transactions:
            transaction.save()
        card.cvv_verified = True
        card.save()
        return True, transactions

    def init_transactions(self, data: dict, amount: Money, user: User) -> List[TransactionRecord]:  # pragma: no cover
        """
        Override to create the initial transaction.
        """
        raise NotImplementedError('Subclass must implement init_transaction.')

    def post_success(self, transactions: List[TransactionRecord], data: dict, user: User):  # pragma: no cover
        """
        Override to further annotate the successful transaction.
        """
        pass


class MakePayment(PaymentMixin, GenericAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [
        OrderBuyerPermission, EscrowPermission,
        OrderStatusPermission(
            Order.PAYMENT_PENDING,
            error_message='This has already been paid for, or is not ready for payment. '
                          'Please refresh the page or contact support.',
        )
    ]

    @lru_cache()
    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return order

    def init_transactions(self, data: dict, amount: Money, user: User) -> List[TransactionRecord]:
        fee_amount = (
                (amount.amount * settings.SERVICE_PERCENTAGE_FEE * Decimal('.01'))
                + settings.SERVICE_STATIC_FEE
        )
        fee_amount = Money(fee_amount, 'USD')
        order = self.get_object()
        escrow_record = TransactionRecord.objects.create(
            payer=order.buyer,
            # Payment is currently in escrow.
            payee=order.seller,
            status=TransactionRecord.FAILURE,
            category=TransactionRecord.ESCROW_HOLD,
            source=TransactionRecord.CARD,
            destination=TransactionRecord.ESCROW,
            amount=amount - fee_amount,
            response_message="Failed when contacting payment processor.",
            target=order,
        )
        fee_record = TransactionRecord.objects.create(
            payer=order.buyer,
            payee=None,
            source=TransactionRecord.CARD,
            destination=TransactionRecord.RESERVE,
            status=TransactionRecord.FAILURE,
            category=TransactionRecord.SERVICE_FEE,
            amount=fee_amount,
            target=order,
            response_message="Failed when contacting payment processor.",
        )
        return [escrow_record, fee_record]

    def post_success(self, transactions: List[TransactionRecord], data: dict, user: User):
        escrow_record, fee_record = transactions
        split_fee(fee_record)

    # noinspection PyUnusedLocal
    def post(self, *args, **kwargs):
        order = self.get_object()
        attempt = self.get_serializer(data=self.request.data, context=self.get_serializer_context())
        attempt.is_valid(raise_exception=True)
        attempt = attempt.validated_data
        if attempt['amount'] != order.total().amount:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={'detail': 'The price has changed. Please refresh the page.'}
            )
        success, response = self.perform_charge(attempt, Money(attempt['amount'], 'USD'), order.buyer)
        if not success:
            return response
        if order.final_uploaded:
            order.status = Order.REVIEW
            order.auto_finalize_on = (timezone.now() + relativedelta(days=2)).date()
            early_finalize(order, self.request.user)
        elif order.revision_set.all().exists():
            order.status = Order.IN_PROGRESS
        else:
            order.status = Order.QUEUED
        order.revisions_hidden = False
        # Save the original turnaround/weight.
        order.task_weight = order.product.task_weight
        order.expected_turnaround = order.product.expected_turnaround
        order.dispute_available_on = (timezone.now() + BDay(ceil(ceil(order.expected_turnaround) * 1.25))).date()
        order.paid_on = timezone.now()
        # Preserve this so it can't be changed during disputes.
        order.commission_info = order.seller.artist_profile.commission_info
        order.save()
        notify(SALE_UPDATE, order, unique=True, mark_unread=True)
        credit_referral(order)
        data = OrderViewSerializer(instance=order, context=self.get_serializer_context()).data
        return Response(data=data)


class AccountBalance(RetrieveAPIView):
    permission_classes = [IsRegistered, UserControls]
    serializer_class = AccountBalanceSerializer

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return user


class BankAccounts(ListCreateAPIView):
    permission_classes = [IsUser]
    serializer_class = BankAccountSerializer
    pagination_class = None

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return BankAccount.objects.filter(user=user).exclude(deleted=True).order_by('-id')

    def perform_create(self, serializer):
        user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        # validated_data will have the additional fields, whereas data only contains fields for model creation.
        data = serializer.validated_data
        if account_balance(user, TransactionRecord.HOLDINGS) < Decimal('1.00'):
            raise PermissionDenied('You do not have sufficient balance to cover the $1.00 connection fee yet.')
        make_dwolla_account(self.request, user, data['first_name'], data['last_name'])
        account = add_bank_account(user, data['account_number'], data['routing_number'], data['type'])
        serializer.instance = account
        return account


class BankManager(DestroyAPIView):
    permission_classes = [IsUser]
    serializer_class = BankAccountSerializer

    def get_object(self):
        bank = get_object_or_404(BankAccount, user__username=self.kwargs['username'], id=self.kwargs['account'])
        self.check_object_permissions(self.request, bank.user)
        return bank

    def perform_destroy(self, instance):
        destroy_bank_account(instance)


class ProductSearch(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        search_serializer = SearchQuerySerializer(data=self.request.GET)
        search_serializer.is_valid(raise_exception=True)
        query = search_serializer.validated_data.get('q', '')
        max_price = search_serializer.validated_data.get('max_price', None)
        min_price = search_serializer.validated_data.get('min_price', None)
        shield_only = search_serializer.validated_data.get('shield_only', False)
        by_rating = search_serializer.validated_data.get('by_rating', False)
        featured = search_serializer.validated_data.get('featured', False)
        watchlist_only = False
        if self.request.user.is_authenticated:
            watchlist_only = search_serializer.validated_data.get('watch_list')

        # If staffer, allow search on behalf of user.
        if self.request.user.is_staff:
            user = get_object_or_404(User, id=self.request.GET.get('user', self.request.user.id))
        else:
            user = self.request.user
        products = available_products(user, query=query, ordering=False)
        if max_price:
            products = products.filter(price__lte=max_price)
        if min_price:
            products = products.filter(price__gte=min_price)
        if watchlist_only:
            products = products.filter(user__in=self.request.user.watching.all())
        if shield_only:
            products = products.exclude(price=0).exclude(user__artist_profile__escrow_disabled=True)
        if featured:
            products = products.filter(featured=True)
        if by_rating:
            products = products.order_by(
                F('user__stars').desc(nulls_last=True), '-edited_on', 'id').distinct('user__stars', 'created_on', 'id')
        else:
            products = products.order_by('-edited_on', 'id').distinct('edited_on', 'id')
        return products.select_related('user').prefetch_related('tags')


class PersonalProductSearch(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsRegistered]

    def get_queryset(self):
        search_serializer = SearchQuerySerializer(data=self.request.GET)
        search_serializer.is_valid(raise_exception=True)
        query = search_serializer.validated_data.get('q', '')
        products = Product.objects.filter(user=self.request.user, name__icontains=query, active=True)
        products = products.filter(user=self.request.user)
        return products.select_related('user')


class AccountStatus(GenericAPIView):
    permission_classes = [IsRegistered, UserControls]
    serializer_class = TransactionRecordSerializer

    def get(self, request, *args, **kwargs):
        self.check_object_permissions(self.request, request.subject)
        query = AccountQuerySerializer(data=request.GET)
        query.is_valid(raise_exception=True)
        account = query.validated_data['account']
        return Response(status=status.HTTP_200_OK, data={
            'available': float(account_balance(request.subject, account)),
            'posted': float(account_balance(request.subject, account, POSTED_ONLY)),
            'pending': float(account_balance(request.subject, account, PENDING)),
        })


class AccountHistory(ListAPIView):
    permission_classes = [IsRegistered, UserControls]
    serializer_class = TransactionRecordSerializer

    def get_queryset(self):
        query = AccountQuerySerializer(data=self.request.GET)
        query.is_valid(raise_exception=True)
        account = query.validated_data['account']
        return TransactionRecord.objects.filter(
            Q(payer=self.request.subject, source=account) | Q(payee=self.request.subject, destination=account),
        ).exclude(
            Q(payee=self.request.subject, destination=account, status=TransactionRecord.FAILURE),
        ).annotate(pending=Case(
            When(status=TransactionRecord.PENDING, then=0),
            default=1,
            output_field=IntegerField()
        )).order_by('pending', '-finalized_on', '-created_on')

    def get(self, request, *args, **kwargs):
        self.check_object_permissions(self.request, self.request.subject)
        return super().get(request, *args, **kwargs)


class NewProducts(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = []

    def get_queryset(self):
        return available_products(
            self.request.user, ordering=False
        ).order_by('-id').distinct('id')


class WhoIsOpen(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsRegistered]

    def get_queryset(self):
        return available_products(
            self.request.user, ordering=False
        ).filter(user__in=self.request.user.watching.all()).distinct('id').order_by('id', 'user')


class SalesStats(APIView):
    permission_classes = [IsRegistered, ObjectControls]

    # noinspection PyUnusedLocal
    def get(self, request, **kwargs):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        self.check_object_permissions(request, user)
        products_available = available_products_by_load(user.artist_profile).count()
        data = {
            'load': user.artist_profile.load,
            'max_load': user.artist_profile.max_load,
            'commissions_closed': user.artist_profile.commissions_closed,
            'commissions_disabled': user.artist_profile.commissions_disabled,
            'products_available': products_available,
            'active_orders': user.sales.filter(status__in=WEIGHTED_STATUSES).count(),
            'new_orders': user.sales.filter(status=Order.NEW).count(),
        }
        return Response(status=status.HTTP_200_OK, data=data)


class RateBase(RetrieveUpdateAPIView):
    serializer_class = RatingSerializer
    # Override the permissions per-end.
    permission_classes = [OrderViewPermission]

    def get_target(self):
        raise NotImplementedError('Override in subclass')  # pragma: no cover

    def get_rater(self):
        raise NotImplementedError('Override in subclass')  # pragma: no cover

    @lru_cache()
    def get_object(self):
        order = self.get_order()
        rater = self.get_rater()
        target = self.get_target()
        ratings = Rating.objects.filter(
            object_id=order.id, content_type=ContentType.objects.get_for_model(order), rater=rater,
            target=target,
        )
        return ratings.first() or Rating(
            object_id=order.id, content_type=ContentType.objects.get_for_model(order), rater=rater,
            target=target,
        )

    def get_order(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return order


class RateBuyer(RateBase):
    permission_classes = [
        Any(
            All(IsSafeMethod, OrderViewPermission),
            All(OrderSellerPermission)
        ),
        OrderStatusPermission(Order.COMPLETED, Order.REFUNDED),
        PaidOrderPermission,
    ]

    def get_target(self):
        return self.get_order().buyer

    def get_rater(self):
        return self.get_order().seller


class RateSeller(RateBase):
    permission_classes = [
        Any(
            All(IsSafeMethod, OrderViewPermission),
            OrderBuyerPermission,
        ),
    ]

    def get_target(self):
        return self.get_order().seller

    def get_rater(self):
        return self.get_order().buyer


class RatingList(ListAPIView):
    serializer_class = RatingSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        return user.ratings.all().order_by('-created_on')


class PremiumInfo(APIView):
    # noinspection PyMethodMayBeStatic
    def get(self, _request):
        return Response(
            status=status.HTTP_200_OK,
            data={
                'premium_percentage_bonus': settings.PREMIUM_PERCENTAGE_BONUS,
                'premium_static_bonus': settings.PREMIUM_STATIC_BONUS,
                'landscape_price': settings.LANDSCAPE_PRICE,
                'standard_percentage': settings.SERVICE_PERCENTAGE_FEE,
                'standard_static': settings.SERVICE_STATIC_FEE,
                'portrait_price': settings.PORTRAIT_PRICE,
                'minimum_price': settings.MINIMUM_PRICE,
            }
        )


class Premium(PaymentMixin, GenericAPIView):
    serializer_class = ServicePaymentSerializer
    permission_classes = [IsRegistered]

    def init_transactions(self, data: dict, amount: Money, user: User) -> List[TransactionRecord]:
        return [TransactionRecord.objects.create(
            payer=user,
            payee=None,
            source=TransactionRecord.CARD,
            destination=TransactionRecord.UNPROCESSED_EARNINGS,
            category=TransactionRecord.SUBSCRIPTION_DUES,
            status=TransactionRecord.FAILURE,
            amount=amount,
            response_message='Failed when contacting payment processor.',
        )]

    def post_success(self, transactions: List[TransactionRecord], data: dict, user: User):
        for transaction in transactions:
            transaction.response_message = 'Upgraded to {}'.format(data['service'])
        set_service(user, data['service'], target_date=date.today() + relativedelta(months=1))

    def post(self, request):
        serializer = self.get_serializer(data=self.request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        charge_required, target_date = check_charge_required(self.request.user, data['service'])
        if not charge_required:
            set_service(request.user, data['service'], target_date=target_date)
            return Response(
                status=status.HTTP_200_OK,
                data=UserSerializer(instance=self.request.user, context=self.get_serializer_context()).data
            )
        amount = service_price(request.user, data['service'])
        success, output = self.perform_charge(data, amount, self.request.user)
        if not success:
            return output
        response_data = UserSerializer(instance=request.user, context=self.get_serializer_context()).data
        return Response(data=response_data)


class CancelPremium(APIView):
    permission_classes = [IsRegistered, UserControls]

    def post(self, request, *args, **kwargs):
        self.check_permissions(request)
        request.subject.portrait_enabled = False
        request.subject.landscape_enabled = False
        request.subject.save()
        return Response(
            status=status.HTTP_200_OK,
            data=UserSerializer(context={'request': request}, instance=self.request.subject).data
        )


class StorePreview(BasePreview):
    def context(self, username):
        user = get_object_or_404(User, username__iexact=username)
        return {
            'title': "{}'s store",
            'description': demark(user.artist_profile.commission_info),
            'image_link': user.avatar_url
        }

    @method_decorator(xframe_options_exempt)
    def get(self, request, *args, **kwargs):
        return super(StorePreview, self).get(request, *args, **kwargs)


class ProductPreview(BasePreview):
    def context(self, username, product_id):
        product = get_object_or_404(Product, id=product_id, active=True, hidden=False)
        return {
            'title': demark(product.name),
            'description': product.preview_description,
            'image_link': preview_rating(self.request, product.rating, product.preview_link)
        }


class CommissionStatusImage(View):
    # noinspection PyMethodMayBeStatic
    def get(self, request, username):
        user = get_object_or_404(User, username__iexact=username)
        if user.artist_profile.commissions_disabled:
            return serve(request, '/images/commissions-closed.png', document_root=settings.STATIC_ROOT)
        else:
            return serve(request, '/images/commissions-open.png', document_root=settings.STATIC_ROOT)


class FeatureProduct(APIView):
    permission_classes = [IsStaff]

    # noinspection PyMethodMayBeStatic
    def post(self, request, username, product):
        product = get_object_or_404(Product, id=product, user__username=username)
        product.featured = not product.featured
        product.save()
        return Response(
            status=status.HTTP_200_OK, data=ProductSerializer(instance=product, context={'request': request}).data
        )


class FeaturedProducts(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(featured=True, available=True, active=True).order_by('?')


class LowPriceProducts(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(price__lte=Decimal('30'), available=True).exclude(featured=True).order_by('?')


class HighlyRatedProducts(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(user__stars__gte=4.5, available=True).exclude(featured=True).order_by('?')


class NewArtistProducts(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        # Can't directly do order_by on this QS because the ORM breaks grouping by placing it before the annotation.
        return Product.objects.filter(id__in=Product.objects.all().annotate(
            completed_orders=Count('user__sales', filter=Q(user__sales__status=Order.COMPLETED))
        ).filter(completed_orders=0, available=True)).order_by('?')


class RandomProducts(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(featured=False, available=True).order_by('?')


class CreateInvoice(GenericAPIView):
    """
    Used to create a new order from the seller's side.
    """
    permission_classes = [IsRegistered, UserControls, BankingConfigured]
    serializer_class = NewInvoiceSerializer

    def post(self, request, username):
        user = get_object_or_404(User, username=username)
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        buyer = serializer.validated_data['buyer']
        product = serializer.validated_data.get('product', None)
        if serializer.validated_data['completed']:
            raw_task_weight = 0
            raw_expected_turnaround = 0
            raw_revisions = 0
        else:
            raw_task_weight = serializer.validated_data['task_weight']
            raw_expected_turnaround = serializer.validated_data['expected_turnaround']
            raw_revisions = serializer.validated_data['revisions']
        if product:
            price = product.price
            adjustment = Money(serializer.validated_data['price'] - product.price.amount, 'USD')
            task_weight = product.task_weight
            adjustment_task_weight = raw_task_weight - product.task_weight
            adjustment_expected_turnaround = raw_expected_turnaround - product.expected_turnaround
            expected_turnaround = product.expected_turnaround
            revisions = product.revisions
            adjustment_revisions = raw_revisions - product.revisions
        else:
            price = Money(serializer.validated_data['price'], 'USD')
            task_weight = raw_task_weight
            expected_turnaround = raw_expected_turnaround
            revisions = raw_revisions
            adjustment_task_weight = 0
            adjustment_expected_turnaround = 0
            adjustment_revisions = 0
            adjustment = Money('0.00', 'USD')

        if isinstance(buyer, str) or buyer is None:
            customer_email = buyer or ''
            buyer = None
        else:
            buyer = buyer
            customer_email = ''
        paid = serializer.validated_data['paid'] or ((price + adjustment) == Money('0', 'USD'))
        escrow_disabled = (
                paid or (user.artist_profile.bank_account_status != HAS_US_ACCOUNT)
        )
        if paid:
            if serializer.validated_data['completed']:
                # Seller still has to upload revisions.
                order_status = Order.IN_PROGRESS
            else:
                order_status = Order.QUEUED
            revisions_hidden = False
        else:
            order_status = Order.PAYMENT_PENDING
            revisions_hidden = True

        order = Order.objects.create(
            seller=user,
            buyer=buyer,
            customer_email=customer_email,
            product=product,
            price=price,
            escrow_disabled=escrow_disabled,
            details=serializer.validated_data['details'],
            private=serializer.validated_data['private'],
            adjustment=adjustment,
            adjustment_task_weight=adjustment_task_weight,
            task_weight=task_weight,
            adjustment_expected_turnaround=adjustment_expected_turnaround,
            expected_turnaround=expected_turnaround,
            revisions_hidden=revisions_hidden,
            revisions=revisions,
            adjustment_revisions=adjustment_revisions,
            commission_info=request.subject.artist_profile.commission_info,
            status=order_status,
        )
        return Response(data=OrderViewSerializer(instance=order, context=self.get_serializer_context()).data)


class OverviewReport(APIView):
    permission_classes = [IsSuperuser]
    def get(self, request):
        data = OrderedDict()
        data['earned'] = str(account_balance(None, TransactionRecord.HOLDINGS))
        data['unprocessed'] = str(account_balance(None, TransactionRecord.UNPROCESSED_EARNINGS))
        data['escrow'] = str(account_balance(ALL, TransactionRecord.ESCROW))
        data['reserve'] = str(account_balance(None, TransactionRecord.RESERVE))
        data['holdings'] = str(
                account_balance(ALL, TransactionRecord.HOLDINGS) - account_balance(None, TransactionRecord.HOLDINGS)
        )
        return Response(data=data)


class CustomerHoldings(ListAPIView):
    permission_classes = [IsSuperuser]
    serializer_class = HoldingsSummarySerializer

    def get_queryset(self):
        return User.objects.all().order_by('username')


class ProductRecommendations(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [
        Any(
            All(IsSafeMethod, OrderPlacePermission),
            ObjectControls,
        )
    ]

    @lru_cache()
    def get_object(self):
        return get_object_or_404(Product, id=self.kwargs['product'])

    def get_queryset(self):
        product = self.get_object()
        qs = available_products(self.request.user, ordering=False).exclude(id=product.id)
        qs = qs.annotate(
            same_artist=Case(
                When(user=product.user, then=0-F('id')),
                default=0,
                output_field=IntegerField(),
            ),
        ).order_by('same_artist', '?')
        return qs


class OrderCharacterList(ListAPIView):
    permission_classes = [OrderViewPermission]
    pagination_class = None
    serializer_class = OrderCharacterTagSerializer

    def get_queryset(self) -> QuerySet:
        return Order.characters.through.objects.filter(order=self.get_object())

    @lru_cache()
    def get_object(self) -> Order:
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return order


class OrderOutputs(ListCreateAPIView):
    permission_classes = [
        OrderViewPermission,
        OrderStatusPermission(Order.COMPLETED),
        Any(
            All(IsRegistered, NoOrderOutput),
            IsSafeMethod,
        )
    ]
    pagination_class = None
    serializer_class = SubmissionSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SubmissionFromOrderSerializer
        return SubmissionSerializer

    def get_queryset(self) -> QuerySet:
        return self.get_object().outputs.all()

    @lru_cache()
    def get_object(self) -> Order:
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return order

    def post(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        revision = order.revision_set.all().last()
        if not revision:
            return Response(
                data={'detail': 'You can not create a submission from an order with no revisions.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save(
            owner=request.user, order=order, rating=order.rating, file=revision.file,
        )
        instance.characters.set(order.characters.all())
        instance.artists.add(order.seller)
        for character in instance.characters.all():
            if request.user == character.user and not character.primary_submission:
                character.primary_submission = instance
                character.save()
        if order.product and request.user == order.seller:
            order.product.samples.add(instance)
        return Response(
            data=SubmissionSerializer(instance=instance, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )


class OrderAuth(GenericAPIView):
    serializer_class = OrderAuthSerializer

    def user_info(self, user):
        serializer = UserSerializer(instance=user, context=self.get_serializer_context())
        data = serializer.data
        if not user.is_registered:
            patch_data = empty_user(self.request)
            del patch_data['username']
            data = {**data, **patch_data}
        return data

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invalid = 'Invalid claim token. It may have expired. A new link will be sent to your ' \
                  'email, if this order can be claimed.'
        order = Order.objects.filter(
            id=serializer.validated_data['id'],
        ).filter(Q(buyer__guest=True) | Q(buyer__isnull=True)).first()
        if not order:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED, data={'detail': invalid},
            )
        if request.user.is_authenticated and (order.buyer and (request.user.username == order.buyer.username)):
            # Ignore the claim token since we're already the required user, and just return success.
            return Response(status=status.HTTP_200_OK, data=self.user_info(order.buyer))
        if order.claim_token != serializer.validated_data['claim_token']:
            target_email = (order.buyer and order.buyer.guest_email) or order.customer_email
            send_transaction_email(
                f'Claim Link for order #{order.id}.',
                'new_claim_link.html', target_email, {'order': order, 'claim_token': slugify(order.claim_token)}
            )
            return Response(
                status=status.HTTP_401_UNAUTHORIZED, data={'detail': invalid},
            )
        if serializer.validated_data['chown'] and not request.user.is_registered:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={
                    'detail': 'You must be logged in to claim this order for an existing account. '
                              'You may wish to continue as a guest instead?'
                }
            )
        if serializer.validated_data['chown']:
            old_buyer = order.buyer
            if order.seller == request.user:
                return Response(
                    status=status.HTTP_403_FORBIDDEN, data={'detail': 'You may not claim your own order!'}
                )
            transfer_order(order, old_buyer, request.user)
            return Response(status=status.HTTP_200_OK, data=self.user_info(request.user))

        if not order.buyer:
            assert order.customer_email
            # Create the buyer now as a guest.
            user = create_guest_user(order.customer_email)
            order.buyer = user
            order.save()
            Subscription.objects.bulk_create(buyer_subscriptions(order), ignore_conflicts=True)
        login(request, order.buyer)
        order.claim_token = uuid4()
        order.save()
        return Response(status=status.HTTP_200_OK, data=self.user_info(order.buyer))
