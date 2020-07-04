from datetime import datetime
from decimal import Decimal
from functools import lru_cache
# Create your views here.
from math import ceil
from typing import Union, List
from uuid import uuid4

from dateutil.parser import parse, ParserError
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import login
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import When, F, Case, BooleanField, Q, Count, QuerySet, IntegerField
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.datetime_safe import date
from django.utils.decorators import method_decorator
from django.utils.timezone import make_aware
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.static import serve
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from moneyed import Money
# BDay is business day, not birthday.
from pandas.tseries.offsets import BDay
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView, \
    GenericAPIView, ListAPIView, DestroyAPIView, RetrieveUpdateAPIView, CreateAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_csv.renderers import CSVRenderer

from apps.lib.models import DISPUTE, REFUND, COMMENT, Subscription, ORDER_UPDATE, SALE_UPDATE, REVISION_UPLOADED, \
    NEW_PRODUCT, STREAMING, ref_for_instance, REFERENCE_UPLOADED, Comment, WAITLIST_UPDATED
from apps.lib.permissions import IsStaff, IsSafeMethod, Any, All, IsMethod
from apps.lib.serializers import CommentSerializer
from apps.lib.utils import notify, recall_notification, demark, preview_rating, send_transaction_email, create_comment
from apps.lib.views import BasePreview
from apps.profiles.models import User, Submission, HAS_US_ACCOUNT
from apps.profiles.permissions import ObjectControls, UserControls, IsUser, IsSuperuser, IsRegistered
from apps.profiles.serializers import UserSerializer, SubmissionSerializer
from apps.profiles.utils import credit_referral, create_guest_user, empty_user
from apps.sales.authorize import AuthorizeException, charge_saved_card, CardInfo, AddressInfo, \
    create_customer_profile, charge_card, card_token_from_transaction, get_card_type, transaction_details
from apps.sales.dwolla import add_bank_account, make_dwolla_account, \
    destroy_bank_account
from apps.sales.models import Product, Order, CreditCardToken, Revision, BankAccount, \
    WEIGHTED_STATUSES, Rating, TransactionRecord, BASE_PRICE, ADD_ON, TAX, EXTRA, \
    TABLE_SERVICE, TIP, LineItem, SHIELD, inventory_change, InventoryError, InventoryTracker, NEW, PAYMENT_PENDING, \
    QUEUED, COMPLETED, IN_PROGRESS, DISPUTED, REVIEW, CANCELLED, REFUNDED, Deliverable, Reference, WAITING
from apps.sales.permissions import (
    OrderViewPermission, OrderSellerPermission, OrderBuyerPermission,
    OrderPlacePermission, EscrowPermission, EscrowDisabledPermission, RevisionsVisible,
    BankingConfigured,
    DeliverableStatusPermission, HasRevisionsPermission, OrderTimeUpPermission, NoOrderOutput, PaidOrderPermission,
    LineItemTypePermission, OrderNoProduct, LandscapePermission)
from apps.sales.serializers import (
    ProductSerializer, ProductNewOrderSerializer, DeliverableViewSerializer, CardSerializer,
    NewCardSerializer, PaymentSerializer, RevisionSerializer,
    AccountBalanceSerializer, BankAccountSerializer, TransactionRecordSerializer,
    RatingSerializer,
    ServicePaymentSerializer, SearchQuerySerializer, NewInvoiceSerializer,
    HoldingsSummarySerializer, ProductSampleSerializer, OrderPreviewSerializer,
    AccountQuerySerializer, DeliverableCharacterTagSerializer, SubmissionFromOrderSerializer, OrderAuthSerializer,
    LineItemSerializer, DeliverableValuesSerializer, SimpleTransactionSerializer, InventorySerializer,
    PayoutTransactionSerializer, OrderViewSerializer, ReferenceSerializer, DeliverableReferenceSerializer,
    NewDeliverableSerializer)
from apps.sales.tasks import renew
from apps.sales.utils import available_products, service_price, set_service, \
    check_charge_required, available_products_by_load, finalize_deliverable, account_balance, \
    recuperate_fee, POSTED_ONLY, PENDING, transfer_order, early_finalize, cancel_deliverable, lines_to_transaction_specs, \
    get_totals, verify_total, issue_refund, ensure_buyer


def user_products(username: str, requester: User):
    qs = Product.objects.filter(user__username__iexact=username, active=True)
    if not (requester.username.lower() == username.lower() or requester.is_staff):
        qs = qs.filter(hidden=False, table_product=False)
    qs = qs.order_by('-created_on')
    return qs

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
        return user_products(self.kwargs['username'], self.request.user)


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


class ProductInventoryManager(RetrieveUpdateAPIView):
    serializer_class = InventorySerializer
    permission_classes = [Any(IsSafeMethod, All(IsRegistered, ObjectControls))]

    @lru_cache()
    def get_object(self):
        product = get_object_or_404(
            Product, user__username=self.kwargs['username'], id=self.kwargs['product'], active=True,
            track_inventory=True,
        )
        self.check_object_permissions(self.request, product)
        return product.inventory

    def perform_update(self, serializer):
        with transaction.atomic():
            tracker = InventoryTracker.objects.select_for_update().get(id=self.get_object().id)
            serializer.instance = tracker
            serializer.save()


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

    @lru_cache
    def get_object(self):
        return get_object_or_404(Product, id=self.kwargs['product'], active=True)

    def perform_create(self, serializer):
        product = self.get_object()
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
        )
        if product.wait_list:
            order_status = WAITING
        else:
            order_status = NEW
        deliverable = Deliverable.objects.create(
            order=order,
            status=order_status,
            name='Main',
            escrow_disabled=product.user.artist_profile.escrow_disabled,
            rating=serializer.validated_data['rating'],
            details=serializer.validated_data['details'],
        )
        deliverable.characters.set(serializer.validated_data.get('characters', []))
        if not user.guest:
            for character in deliverable.characters.all():
                character.shared_with.add(order.seller)
        else:
            order.customer_email = user.guest_email
            order.save()
        if product.wait_list:
            notify(WAITLIST_UPDATED, order.seller, unique=True, mark_unread=True)
        else:
            notify(SALE_UPDATE, deliverable, unique=True, mark_unread=True)
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        return order

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = self.get_object()
        try:
            with inventory_change(product):
                order = self.perform_create(serializer)
        except InventoryError:
            return Response({'detail': 'This product is not in stock.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = OrderPreviewSerializer(instance=order, context=self.get_serializer_context())
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OrderManager(RetrieveUpdateAPIView):
    permission_classes = [OrderViewPermission]
    serializer_class = OrderViewSerializer

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return order


class OrderDeliverables(ListCreateAPIView):
    permission_classes = [
        Any(
            All(OrderViewPermission, IsSafeMethod),
            All(OrderSellerPermission, LandscapePermission),
        )
    ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['seller'] = self.get_object().seller
        return context

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NewDeliverableSerializer
        else:
            return DeliverableViewSerializer

    def get_queryset(self):
        return self.get_object().deliverables.all().order_by('-created_on')

    @lru_cache(256)
    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return order

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data = DeliverableViewSerializer(instance=serializer.instance, context=self.get_serializer_context()).data
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        order = self.get_object()
        self.check_object_permissions(self.request, order)
        product = order.product
        facts = get_order_facts(product, serializer, order.seller)
        deliverable_facts = {key: value for key, value in facts.items() if key not in (
            'price', 'adjustment', 'hold', 'paid',
        )}
        deliverable = serializer.save(
            order=order,
            commission_info=order.seller.artist_profile.commission_info,
            **deliverable_facts,
        )
        deliverable.line_items.get_or_create(
            type=BASE_PRICE, amount=facts['price'], priority=0, destination_account=TransactionRecord.ESCROW,
            destination_user=order.seller,
        )
        if facts['adjustment']:
            deliverable.line_items.get_or_create(
                type=ADD_ON, amount=facts['adjustment'], priority=1, destination_account=TransactionRecord.ESCROW,
                destination_user=order.seller,
            )
        # Trigger line item creation.
        deliverable.save()
        deliverable.characters.set(serializer.validated_data.get('characters', []))
        deliverable.reference_set.set(serializer.validated_data.get('references', []))
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)



class DeliverableManager(RetrieveUpdateAPIView):
    permission_classes = [OrderViewPermission]
    serializer_class = DeliverableViewSerializer

    def get_object(self):
        order = get_object_or_404(Deliverable, order_id=self.kwargs['order_id'], id=self.kwargs['deliverable_id'])
        self.check_object_permissions(self.request, order)
        return order


class DeliverableInvite(GenericAPIView):
    permission_classes = [OrderSellerPermission]
    serializer_class = OrderViewSerializer

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        return order

    def post(self, request, **kwargs):
        deliverable = get_object_or_404(Deliverable, order=self.get_object(), id=self.kwargs['deliverable_id'])
        self.check_object_permissions(self.request, deliverable)
        if deliverable.order.buyer and not deliverable.order.buyer.guest:
            return Response(data={'detail': 'This order has already been claimed.'}, status=status.HTTP_400_BAD_REQUEST)
        if not deliverable.order.customer_email:
            return Response(
                data={'detail': 'Customer email not set. Cannot send an invite!'}, status=status.HTTP_400_BAD_REQUEST,
            )
        if deliverable.order.buyer:
            deliverable.order.buyer.guest_email = deliverable.order.customer_email
            deliverable.order.buyer.save()
            subject = f'Claim Link for order #{deliverable.order.id}.'
            template = 'new_claim_link.html'
        else:
            subject = f'You have a new invoice from {deliverable.order.seller.username}!'
            template = 'invoice_issued.html'
        send_transaction_email(
            subject,
            template, deliverable.order.customer_email,
            {'deliverable': deliverable, 'order': deliverable.order, 'claim_token': deliverable.order.claim_token}
        )
        return Response(status=status.HTTP_200_OK, data=self.get_serializer(instance=deliverable.order).data)


class DeliverableAccept(GenericAPIView):
    permission_classes = [
        OrderSellerPermission,
        DeliverableStatusPermission(NEW, WAITING, error_message="Approval can only be applied to new orders."),
    ]

    def get_object(self):
        deliverable = get_object_or_404(Deliverable, id=self.kwargs['deliverable_id'], order_id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, deliverable)
        return deliverable

    def post(self, request, *args, **kwargs):
        deliverable = self.get_object()
        deliverable.status = PAYMENT_PENDING
        deliverable.task_weight = (deliverable.order.product and deliverable.order.product.task_weight) or deliverable.task_weight
        deliverable.expected_turnaround = (deliverable.order.product and deliverable.order.product.expected_turnaround) or deliverable.expected_turnaround
        deliverable.revisions = (deliverable.order.product and deliverable.order.product.revisions) or deliverable.revisions
        if deliverable.total() <= Money('0', 'USD'):
            deliverable.status = QUEUED
            deliverable.revisions_hidden = False
            deliverable.escrow_disabled = True
        deliverable.save()
        data = DeliverableViewSerializer(instance=deliverable, context=self.get_serializer_context()).data
        if (not deliverable.order.buyer) and deliverable.order.customer_email:
            subject = f'You have a new invoice from {deliverable.order.seller.username}!'
            template = 'invoice_issued.html'
            send_transaction_email(
                subject,
                template, deliverable.order.customer_email,
                {'deliverable': deliverable, 'claim_token': deliverable.order.claim_token},
            )
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        return Response(data)


class MarkPaid(GenericAPIView):
    permission_classes = [
        OrderSellerPermission,
        DeliverableStatusPermission(
            PAYMENT_PENDING,
            error_message='You can only mark orders paid if they are waiting for payment.',
        ),
    ]
    serializer_class = DeliverableViewSerializer

    def get_object(self):
        return get_object_or_404(Deliverable, order_id=self.kwargs['order_id'], id=self.kwargs['deliverable_id'])

    def post(self, request, **_kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(request, deliverable)
        if deliverable.final_uploaded:
            deliverable.status = COMPLETED
        elif deliverable.revision_set.all():
            deliverable.status = IN_PROGRESS
        else:
            deliverable.status = QUEUED
        if deliverable.order.product:
            deliverable.task_weight = deliverable.order.product.task_weight
            deliverable.expected_turnaround = deliverable.order.product.expected_turnaround
            deliverable.revisions = deliverable.order.product.revisions
        deliverable.revisions_hidden = False
        deliverable.commission_info = deliverable.order.seller.artist_profile.commission_info
        deliverable.escrow_disabled = True
        deliverable.save()
        data = self.serializer_class(instance=deliverable, context=self.get_serializer_context()).data
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        return Response(data)


class DeliverableStart(GenericAPIView):
    permission_classes = [
        OrderSellerPermission,
        DeliverableStatusPermission(
            QUEUED,
            error_message='You can only start orders that are queued.',
        ),
    ]
    serializer_class = DeliverableViewSerializer

    def get_object(self):
        order = get_object_or_404(Deliverable, order_id=self.kwargs['order_id'], id=self.kwargs['deliverable_id'])
        self.check_object_permissions(self.request, order)
        return order

    def post(self, *args, **kwargs):
        deliverable = self.get_object()
        deliverable.started_on = timezone.now()
        deliverable.status = IN_PROGRESS
        deliverable.save()
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        if not deliverable.order.private and deliverable.stream_link:
            notify(
                STREAMING, deliverable.order.seller,
                data={'order': deliverable.id}, unique_data=True,
                exclude=[deliverable.order.buyer, deliverable.order.seller]
            )
        return Response(data=DeliverableViewSerializer(instance=deliverable, context=self.get_serializer_context()).data)


class DeliverableCancel(GenericAPIView):
    permission_classes = [
        OrderViewPermission,
        DeliverableStatusPermission(
            WAITING, NEW, PAYMENT_PENDING,
            error_message='You cannot cancel this order. It is either already cancelled, finalized, '
                          'or must be refunded instead.',
        ),
    ]
    serializer_class = DeliverableViewSerializer

    def get_object(self):
        deliverable = get_object_or_404(
            Deliverable, order_id=self.kwargs['order_id'], id=self.kwargs['deliverable_id'],
        )
        self.check_object_permissions(self.request, deliverable)
        return deliverable

    # noinspection PyUnusedLocal
    def post(self, request, order_id, deliverable_id):
        deliverable = self.get_object()
        cancel_deliverable(deliverable, self.request.user)
        data = self.serializer_class(instance=deliverable, context=self.get_serializer_context()).data
        return Response(data)


class DeliverableLineItems(ListCreateAPIView):
    permission_classes = [
        Any(
            All(
                Any(
                    IsSafeMethod,
                    All(
                        IsMethod('POST'), DeliverableStatusPermission(
                            NEW, PAYMENT_PENDING, WAITING,
                        )
                    )
                ),
                OrderViewPermission
            ),
        )
    ]
    pagination_class = None
    serializer_class = LineItemSerializer

    @lru_cache()
    def get_object(self):
        return get_object_or_404(
            Deliverable, order_id=self.kwargs['order_id'], id=self.kwargs['deliverable_id'],
        )

    def get_queryset(self):
        deliverable = self.get_object()
        return deliverable.line_items.exclude(type=TIP, amount=0)

    def get_serializer_context(self):
        return {**super().get_serializer_context(), 'deliverable': self.get_object()}

    def get(self, request, *args, **kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(request, deliverable)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(request, deliverable)
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        item_type = serializer.validated_data.get('type', ADD_ON)
        deliverable = self.get_object()
        destination_user = deliverable.order.seller
        if item_type in [TAX, EXTRA, TABLE_SERVICE]:
            destination_user = None
        accounts = {
            TAX: TransactionRecord.MONEY_HOLE,
            ADD_ON: TransactionRecord.ESCROW,
            TIP: TransactionRecord.ESCROW,
            BASE_PRICE: TransactionRecord.ESCROW,
            TABLE_SERVICE: TransactionRecord.UNPROCESSED_EARNINGS,
            EXTRA: TransactionRecord.UNPROCESSED_EARNINGS,
        }
        destination_account = accounts[item_type]
        tip = deliverable.line_items.filter(type=TIP).first()
        if item_type == TIP and tip:
            tip.amount = serializer.validated_data['amount']
            tip.save()
            serializer.instance = tip
            return
        if item_type == BASE_PRICE and serializer.validated_data.get('percentage', 0):
            raise ValidationError({'percentage': ['Base price may not have percentage.']})
        with transaction.atomic():
            base_price = deliverable.line_items.filter(type=BASE_PRICE).first()
            if base_price and item_type == BASE_PRICE:
                base_price.amount = serializer.validated_data['amount']
                base_price.save()
            else:
                serializer.save(
                    destination_user=destination_user, destination_account=destination_account, deliverable=deliverable,
                )
            verify_total(deliverable)


class LineItemManager(RetrieveUpdateDestroyAPIView):
    permission_classes = [
        Any(
            All(IsSafeMethod, OrderViewPermission),
            All(
                IsMethod('PATCH', 'DELETE'),
                DeliverableStatusPermission(NEW, PAYMENT_PENDING, WAITING),
                Any(
                    All(
                        OrderSellerPermission, Any(
                            LineItemTypePermission(ADD_ON),
                            All(OrderNoProduct, All(LineItemTypePermission(BASE_PRICE), IsMethod('PATCH'))),
                        )
                    ),
                    All(OrderBuyerPermission, LineItemTypePermission(TIP)),
                    All(IsStaff, LineItemTypePermission(EXTRA, TABLE_SERVICE)),
                    IsSuperuser,
                )
            ),
        )
    ]
    serializer_class = LineItemSerializer

    @lru_cache
    def get_object(self):
        line_item = LineItem.objects.get(id=self.kwargs['line_item_id'], deliverable__id=self.kwargs['deliverable_id'])
        self.check_object_permissions(self.request, line_item)
        return line_item

    def get_serializer_context(self):
        return {**super().get_serializer_context(), 'deliverable': self.get_object()}

    def perform_update(self, serializer):
        with transaction.atomic():
            serializer.save()
            deliverable = serializer.instance.deliverable
            verify_total(deliverable)
        # Trigger automatic creation/destruction of shield lines.
        deliverable.save()


class DeliverableRevisions(ListCreateAPIView):
    permission_classes = [
        Any(
            All(IsSafeMethod, OrderViewPermission, Any(RevisionsVisible, OrderSellerPermission)),
            All(OrderSellerPermission, IsMethod('POST'), DeliverableStatusPermission(
                IN_PROGRESS, PAYMENT_PENDING, NEW, QUEUED, DISPUTED, WAITING,
                error_message='You may not upload revisions while the order is in this state.',
            )),
        ),
    ]
    pagination_class = None
    serializer_class = RevisionSerializer

    @lru_cache()
    def get_object(self):
        return get_object_or_404(Deliverable, id=self.kwargs['deliverable_id'], order_id=self.kwargs['order_id'])

    def get_queryset(self):
        deliverable = self.get_object()
        return deliverable.revision_set.all()

    def get(self, *args, **kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(self.request, deliverable)
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(self.request, deliverable)
        return super().post(*args, **kwargs)

    def perform_create(self, serializer):
        deliverable = self.get_object()
        revision = serializer.save(deliverable=deliverable, owner=self.request.user, rating=deliverable.rating)
        deliverable.refresh_from_db()
        if deliverable.status == QUEUED:
            deliverable.status = IN_PROGRESS
        if serializer.validated_data.get('final'):
            deliverable.final_uploaded = True
            if deliverable.escrow_disabled:
                deliverable.status = COMPLETED
            elif deliverable.status == IN_PROGRESS:
                deliverable.status = REVIEW
                deliverable.auto_finalize_on = (timezone.now() + relativedelta(days=5)).date()
                early_finalize(deliverable, self.request.user)
            deliverable.save()
            notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        else:
            notify(REVISION_UPLOADED, deliverable, data={'revision': revision.id}, unique_data=True, mark_unread=True)
        deliverable.save()
        recall_notification(STREAMING, deliverable.order.seller, data={'order': deliverable.id})
        return revision


class References(CreateAPIView):
    serializer_class = ReferenceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)


class DeliverableReferences(ListCreateAPIView):
    permission_classes = [OrderViewPermission]
    pagination_class = None
    serializer_class = DeliverableReferenceSerializer

    @lru_cache()
    def get_object(self):
        return get_object_or_404(Deliverable, id=self.kwargs['deliverable_id'], order_id=self.kwargs['order_id'])

    def get_queryset(self):
        deliverable = self.get_object()
        return Reference.deliverables.through.objects.filter(deliverable=deliverable).order_by('-reference__created_on')

    def get(self, *args, **kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(self.request, deliverable)
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(self.request, deliverable)
        return super().post(*args, **kwargs)

    def perform_create(self, serializer):
        deliverable = self.get_object()
        deliverable_reference = serializer.save(deliverable=deliverable)
        reference = deliverable_reference.reference
        content_type = ContentType.objects.get_for_model(reference)
        Subscription.objects.get_or_create(
            subscriber=deliverable.order.seller, type=COMMENT, object_id=reference.id,
            content_type=content_type, email=True,
        )
        if deliverable.order.buyer:
            Subscription.objects.get_or_create(
                subscriber=deliverable.order.buyer, type=COMMENT, email=True,
                content_type=content_type,
                object_id=reference.id,
            )
        notify(
            REFERENCE_UPLOADED,
            deliverable,
            data={'reference': reference.id},
            unique_data=True,
            mark_unread=True,
            exclude=[self.request.user],
        )
        return deliverable_reference


class ReferenceManager(RetrieveDestroyAPIView):
    serializer_class = ReferenceSerializer
    permission_classes = [OrderViewPermission]

    def perform_destroy(self, instance):
        if not (self.request.user.is_staff or instance.owner == self.request.user):
            # Probably should find some cleaner way to check this with the permissions framework.
            raise PermissionDenied('You do not have the right to remove this reference.')
        deliverable = get_object_or_404(
            Deliverable, id=self.kwargs['deliverable_id'], order_id=self.kwargs['order_id'],
        )
        deliverable.reference_set.remove(instance)

    def get_object(self):
        deliverable = get_object_or_404(
            Deliverable, id=self.kwargs['deliverable_id'], order_id=self.kwargs['order_id'],
        )
        reference = deliverable.reference_set.filter(id=self.kwargs['reference_id']).first()
        if not reference:
            raise Http404("I didn't get that reference.")
        self.check_object_permissions(self.request, deliverable)
        return reference


delete_forbidden_message = 'You may not remove revisions from this order. They are either locked or under dispute.'


class RevisionManager(RetrieveDestroyAPIView):
    permission_classes = [
        Any(
            All(
                IsMethod('DELETE'),
                OrderSellerPermission,
                Any(
                    DeliverableStatusPermission(
                        REVIEW, PAYMENT_PENDING, NEW, IN_PROGRESS, WAITING,
                        error_message=delete_forbidden_message,
                    ),
                    All(
                        EscrowDisabledPermission,
                        DeliverableStatusPermission(
                            COMPLETED,
                            error_message=delete_forbidden_message,
                        )),
                ),
            ),
            All(
                IsMethod('GET'),
                OrderViewPermission,
                Any(
                    OrderSellerPermission,
                    RevisionsVisible,
                )
            )
        )
    ]
    serializer_class = RevisionSerializer

    def get_object(self):
        deliverable = get_object_or_404(Deliverable, order_id=self.kwargs['order_id'], id=self.kwargs['deliverable_id'])
        revision = get_object_or_404(
            Revision, id=self.kwargs['revision_id'], deliverable_id=self.kwargs['deliverable_id'],
        )
        self.check_object_permissions(self.request, deliverable)
        return revision

    def perform_destroy(self, instance):
        revision_id = instance.id
        super(RevisionManager, self).perform_destroy(instance)
        deliverable = Deliverable.objects.get(id=self.kwargs['deliverable_id'], order_id=self.kwargs['order_id'])
        recall_notification(REVISION_UPLOADED, deliverable, data={'revision': revision_id}, unique_data=True)
        if deliverable.final_uploaded:
            deliverable.final_uploaded = False
        if deliverable.status in [REVIEW, COMPLETED]:
            deliverable.auto_finalize_on = None
            deliverable.status = IN_PROGRESS
        deliverable.save()


reopen_error_message = 'This order cannot be reopened.'


class ReOpen(GenericAPIView):
    serializer_class = DeliverableViewSerializer
    permission_classes = [
        OrderSellerPermission,
        Any(
            DeliverableStatusPermission(
                REVIEW, PAYMENT_PENDING, DISPUTED, error_message=reopen_error_message,
            ),
            All(EscrowDisabledPermission, DeliverableStatusPermission(COMPLETED, error_message=reopen_error_message)),
        )
    ]

    def get_object(self):
        return get_object_or_404(Deliverable, order_id=self.kwargs['order_id'], id=self.kwargs['deliverable_id'])

    def post(self, _request, *_args, **_kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(self.request, deliverable)
        if deliverable.status not in [PAYMENT_PENDING, DISPUTED]:
            deliverable.status = IN_PROGRESS
        deliverable.final_uploaded = False
        deliverable.auto_finalize_on = None
        deliverable.save()
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        serializer = self.get_serializer(instance=deliverable)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class MarkComplete(GenericAPIView):
    serializer_class = DeliverableViewSerializer
    permission_classes = [
        OrderSellerPermission,
        DeliverableStatusPermission(
            IN_PROGRESS,
            PAYMENT_PENDING,
            error_message='You cannot mark an order complete if it is not in progress.',
        ),
        HasRevisionsPermission,
    ]

    def get_object(self):
        return get_object_or_404(Deliverable, order_id=self.kwargs['order_id'], id=self.kwargs['deliverable_id'])

    def post(self, _request, *_args, **_kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(self.request, deliverable)
        if deliverable.revision_set.all().exists() and deliverable.status == PAYMENT_PENDING:
            deliverable.final_uploaded = True
            deliverable.save()
            serializer = self.get_serializer(instance=deliverable)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        deliverable.final_uploaded = True
        if deliverable.escrow_disabled:
            deliverable.status = COMPLETED
        else:
            deliverable.status = REVIEW
            deliverable.auto_finalize_on = (timezone.now() + relativedelta(days=2)).date()
            early_finalize(deliverable, self.request.user)
        deliverable.save()
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        serializer = self.get_serializer(instance=deliverable)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class StartDispute(GenericAPIView):
    permission_classes = [
        OrderBuyerPermission, EscrowPermission,
        DeliverableStatusPermission(
            REVIEW, IN_PROGRESS, QUEUED, error_message='This order is not in a disputable state.',
        ),
        # Slight redundancy here to ensure the right error messages display.
        Any(
            All(OrderTimeUpPermission, DeliverableStatusPermission(IN_PROGRESS, QUEUED)),
            DeliverableStatusPermission(REVIEW),
        )
    ]
    serializer_class = DeliverableViewSerializer

    def get_object(self):
        return get_object_or_404(
            Deliverable, order_id=self.kwargs['order_id'], id=self.kwargs['deliverable_id'],
        )

    def post(self, _request, *_args, **_kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(self.request, deliverable)
        deliverable.status = DISPUTED
        deliverable.disputed_on = timezone.now()
        deliverable.save()
        notify(DISPUTE, deliverable, unique=True, mark_unread=True)
        notify(SALE_UPDATE, deliverable, unique=True, mark_unread=True)
        serializer = self.get_serializer(instance=deliverable)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ClaimDispute(GenericAPIView):
    permission_classes = [IsStaff]
    serializer_class = DeliverableViewSerializer

    def get_object(self):
        return get_object_or_404(Deliverable, order_id=self.kwargs['order_id'], id=self.kwargs['deliverable_id'])

    # noinspection PyUnusedLocal
    def post(self, request, order_id, deliverable_id):
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


class DeliverableRefund(GenericAPIView):
    permission_classes = [
        OrderSellerPermission,
        DeliverableStatusPermission(
            QUEUED, IN_PROGRESS, REVIEW, DISPUTED,
            error_message='This order is not in a refundable state.',
        )
    ]
    serializer_class = DeliverableViewSerializer

    def get_object(self):
        return get_object_or_404(
            Deliverable, order_id=self.kwargs['order_id'], id=self.kwargs['deliverable_id'],
        )

    def post(self, request, *_args, **_kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(self.request, deliverable)
        if deliverable.escrow_disabled:
            deliverable.status = REFUNDED
            deliverable.save()
            notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
            serializer = self.get_serializer(instance=deliverable, context=self.get_serializer_context())
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        order_type = ContentType.objects.get_for_model(deliverable)
        original_record = TransactionRecord.objects.get(
            targets__object_id=deliverable.id, targets__content_type=order_type, payer=deliverable.order.buyer,
            payee=deliverable.order.seller,
            destination=TransactionRecord.ESCROW,
            status=TransactionRecord.SUCCESS,
        )
        transaction_set = TransactionRecord.objects.filter(
            source__in=[TransactionRecord.CARD, TransactionRecord.CASH_DEPOSIT],
            targets__content_type=order_type, targets__object_id=deliverable.id,
            status=TransactionRecord.SUCCESS,
        ).exclude(category=TransactionRecord.SHIELD_FEE)
        record = issue_refund(transaction_set, TransactionRecord.ESCROW_REFUND)[0]
        if record.status == TransactionRecord.FAILURE:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': record.response_message})
        deliverable.status = REFUNDED
        deliverable.save()
        recuperate_fee(original_record)
        notify(REFUND, deliverable, unique=True, mark_unread=True)
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        if request.user != deliverable.order.seller:
            notify(SALE_UPDATE, deliverable, unique=True, mark_unread=True)
        serializer = self.get_serializer(instance=deliverable, context=self.get_serializer_context())
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ApproveFinal(GenericAPIView):
    permission_classes = [
        OrderBuyerPermission, EscrowPermission,
        DeliverableStatusPermission(REVIEW, DISPUTED, error_message='This order is not in an approvable state.')
    ]
    serializer_class = DeliverableViewSerializer

    def get_object(self):
        return get_object_or_404(Deliverable, order_id=self.kwargs['order_id'], id=self.kwargs['deliverable_id'])

    def post(self, request, *_args, **_kwargs):
        order = self.get_object()
        self.check_object_permissions(self.request, order)
        finalize_deliverable(order, request.user)
        return Response(
            status=status.HTTP_200_OK,
            data=DeliverableViewSerializer(instance=order, context=self.get_serializer_context()).data
        )


class CurrentMixin(object):
    @staticmethod
    def extra_filter(qs):
        return qs.filter(
            deliverables__status__in=[NEW, PAYMENT_PENDING, QUEUED, IN_PROGRESS, REVIEW, DISPUTED],
        ).distinct().order_by('-created_on')


class ArchivedMixin(object):
    @staticmethod
    def extra_filter(qs):
        return qs.exclude(
            deliverables__status__in=[WAITING, NEW, PAYMENT_PENDING, QUEUED, IN_PROGRESS, REVIEW, DISPUTED]).filter(
                deliverables__status=COMPLETED,
        ).distinct().order_by('-created_on')


class CancelledMixin(object):
    @staticmethod
    def extra_filter(qs):
        return qs.exclude(
            deliverables__status__in=[WAITING, NEW, PAYMENT_PENDING, QUEUED, IN_PROGRESS, DISPUTED, REVIEW, COMPLETED],
        ).distinct().order_by('-created_on')


class WaitingMixin(object):
    @staticmethod
    def extra_filter(qs):
        return qs.filter(deliverables__status=WAITING).distinct().order_by('-created_on')


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


class WaitingOrderList(WaitingMixin, OrderListBase):
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


class SearchWaiting(ListAPIView):
    permission_classes = [IsRegistered, UserControls]
    serializer_class = OrderPreviewSerializer

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return user

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        qs = Order.objects.filter(deliverables__status=WAITING, seller=self.request.subject)
        if not query:
            return qs.distinct().order_by('created_on')
        return qs.filter(
            Q(buyer__username__istartswith=query)
            | Q(buyer__email__istartswith=query)
            | Q(customer_email__istartswith=query)
            | Q(buyer__guest=True, buyer__guest_email__istartswith=query)
        ).distinct().order_by('created_on')


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
        return self.extra_filter(Order.objects.filter(
            deliverables__in=self.user.cases.all()),
        ).distinct().order_by('-created_on')

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
        if data.get('cash', False) and self.request.user.is_staff:
            return self.from_cash(data, amount, user)
        if data.get('remote_id') and self.request.user.is_staff:
            return self.from_remote_id(data, amount, user, data.get('remote_id'))
        if data.get('card_id'):
            return self.charge_existing_card(data, amount, user)
        else:
            return self.charge_new_card(data, amount, user)

    def from_cash(self, data: dict, amount: Money, user: User):
        transactions = self.init_transactions(data, amount, user)
        for transaction in transactions:
            transaction.status = TransactionRecord.SUCCESS
            transaction.source = TransactionRecord.CASH_DEPOSIT
        self.post_success(transactions, data, user)
        for transaction in transactions:
            transaction.save()
        self.post_save(transactions, data, user)
        return True, transactions

    def from_remote_id(self, data: dict, amount: Money, user: User, remote_id: str):
        # First, let's verify this remote ID is real.
        details = transaction_details(remote_id)
        auth_code = details['auth_code']
        if not auth_code:
            raise AuthorizeException('Transaction ID is for failed transaction.')
        if details['auth_amount'] != amount:
            raise AuthorizeException(
                f'This transaction ID is for the wrong amount. {amount} != {details["auth_amount"]}')
        if TransactionRecord.objects.filter(auth_code=auth_code).exists():
            raise AuthorizeException('An order with this transaction ID already exists.')
        transactions = self.init_transactions(data, amount, user)
        for transaction in transactions:
            transaction.status = TransactionRecord.SUCCESS
            transaction.auth_code = auth_code
            transaction.remote_id = remote_id
        self.post_success(transactions, data, user)
        for transaction in transactions:
            transaction.save()
        self.post_save(transactions, data, user)
        return True, transactions

    def annotate_error(
            self, transactions: List[TransactionRecord], err: Exception, data: dict, user: User
    ) -> (False, Response):
        response_message = str(err)
        for transaction in transactions:
            transaction.response_message = response_message
            transaction.save()
        self.post_save(transactions, data, user)
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
            remote_id, auth_code = charge_card(card_info, address_info, amount.amount)
        except Exception as err:
            return self.annotate_error(transactions, err, data, user)
        for transaction in transactions:
            transaction.status = TransactionRecord.SUCCESS
            transaction.remote_id = remote_id
            transaction.auth_code = auth_code
        self.post_success(transactions, data, user)
        for transaction in transactions:
            transaction.save()
        self.post_save(transactions, data, user)

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
            remote_id, auth_code = charge_saved_card(
                profile_id=card.profile_id,
                payment_id=card.payment_id, amount=amount.amount, cvv=data.get('cvv', None),
            )
        except Exception as err:
            return self.annotate_error(transactions, err, data, user)
        for transaction in transactions:
            transaction.status = TransactionRecord.SUCCESS
            transaction.remote_id = remote_id
            transaction.auth_code = auth_code
        self.post_success(transactions, data, user)
        for transaction in transactions:
            transaction.save()
        self.post_save(transactions, data, user)
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

    def post_save(self, transactions: List[TransactionRecord], data: dict, user: User):  # pragma: no cover
        """
        Override for actions that should be taken after the transactions are saved (such as adding targets)
        """
        pass


class MakePayment(PaymentMixin, GenericAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [
        OrderBuyerPermission, EscrowPermission,
        DeliverableStatusPermission(
            PAYMENT_PENDING,
            error_message='This has already been paid for, or is not ready for payment. '
                          'Please refresh the page or contact support.',
        )
    ]

    @lru_cache()
    def get_object(self):
        deliverable = get_object_or_404(Deliverable, order_id=self.kwargs['order_id'], id=self.kwargs['deliverable_id'])
        self.check_object_permissions(self.request, deliverable)
        return deliverable

    @lru_cache()
    def transaction_specs(self):
        return lines_to_transaction_specs(self.get_object().line_items.all())

    def init_transactions(self, data: dict, amount: Money, user: User) -> List[TransactionRecord]:
        deliverable = self.get_object()
        transaction_specs = self.transaction_specs()
        transactions = [
            TransactionRecord(
                payer=deliverable.order.buyer,
                status=TransactionRecord.FAILURE,
                category=category,
                source=TransactionRecord.CARD,
                payee=destination_user,
                destination=destination_account,
                amount=value,
                response_message="Failed when contacting payment processor.",
            ) for ((destination_user, destination_account, category), value) in transaction_specs.items()
        ]
        return transactions

    def post_save(self, transactions: List[TransactionRecord], data: dict, user: User):
        deliverable = self.get_object()
        for transaction in transactions:
            transaction.targets.add(ref_for_instance(deliverable))

    def post_success(self, transactions: List[TransactionRecord], data: dict, user: User):
        escrow_record, fee_record, *other = transactions
        deliverable = self.get_object()
        if deliverable.table_order:
            return
        reserve_item = deliverable.line_items.get(type=SHIELD)
        _value, discount, subtotals = get_totals(deliverable.line_items.all())
        record = TransactionRecord.objects.create(
            payer=None,
            payee=None,
            amount=subtotals[reserve_item],
            source=TransactionRecord.RESERVE,
            destination=TransactionRecord.UNPROCESSED_EARNINGS,
            remote_id=fee_record.remote_id,
            auth_code=fee_record.auth_code,
            status=TransactionRecord.SUCCESS,
            category=TransactionRecord.SHIELD_FEE,
        )
        record.targets.add(ref_for_instance(deliverable))

    # noinspection PyUnusedLocal
    def post(self, *args, **kwargs):
        deliverable = self.get_object()
        attempt = self.get_serializer(data=self.request.data, context=self.get_serializer_context())
        attempt.is_valid(raise_exception=True)
        attempt = attempt.validated_data
        if attempt['amount'] != deliverable.total().amount:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={'detail': 'The price has changed. Please refresh the page.'}
            )
        try:
            ensure_buyer(deliverable.order)
        except AssertionError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={
                    'detail': 'No buyer is set for this order, nor is there a customer email set.',
                }
            )
        success, response = self.perform_charge(attempt, Money(attempt['amount'], 'USD'), deliverable.order.buyer)
        if not success:
            return response
        if deliverable.final_uploaded:
            deliverable.status = REVIEW
            deliverable.auto_finalize_on = (timezone.now() + relativedelta(days=2)).date()
            early_finalize(deliverable, self.request.user)
        elif deliverable.revision_set.all().exists():
            deliverable.status = IN_PROGRESS
        else:
            deliverable.status = QUEUED
        deliverable.revisions_hidden = False
        # Save the original turnaround/weight.
        deliverable.task_weight = (
                (deliverable.order.product and deliverable.order.product.task_weight)
                or deliverable.task_weight
        )
        deliverable.expected_turnaround = (
                (deliverable.order.product and deliverable.order.product.expected_turnaround)
                or deliverable.expected_turnaround
        )
        deliverable.dispute_available_on = (
                timezone.now() + BDay(ceil(ceil(deliverable.expected_turnaround) * 1.25))
        ).date()
        deliverable.paid_on = timezone.now()
        # Preserve this so it can't be changed during disputes.
        deliverable.commission_info = deliverable.order.seller.artist_profile.commission_info
        deliverable.save()
        notify(SALE_UPDATE, deliverable, unique=True, mark_unread=True)
        credit_referral(deliverable)
        data = DeliverableViewSerializer(instance=deliverable, context=self.get_serializer_context()).data
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
        lgbt = search_serializer.validated_data.get('lgbt', False)
        artists_of_color = search_serializer.validated_data.get('artists_of_color', False)
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
            products = products.filter(starting_price__lte=max_price)
        if min_price:
            products = products.filter(starting_price__gte=min_price)
        if watchlist_only:
            products = products.filter(user__in=self.request.user.watching.all())
        if shield_only:
            products = products.exclude(starting_price=0).exclude(user__artist_profile__escrow_disabled=True)
        if featured:
            products = products.filter(featured=True)
        if artists_of_color:
            products = products.filter(user__artist_profile__artist_of_color=True)
        if lgbt:
            products = products.filter(user__artist_profile__lgbt=True)
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
        products = Product.objects.filter(user=self.request.subject, name__icontains=query, active=True)
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
            'active_orders': Deliverable.objects.filter(status__in=WEIGHTED_STATUSES, order__seller=user).count(),
            'new_orders': Deliverable.objects.filter(status=NEW, order__seller=user).count(),
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
        deliverable = self.get_deliverable()
        rater = self.get_rater()
        target = self.get_target()
        ratings = Rating.objects.filter(
            object_id=deliverable.id, content_type=ContentType.objects.get_for_model(deliverable), rater=rater,
            target=target,
        )
        return ratings.first() or Rating(
            object_id=deliverable.id, content_type=ContentType.objects.get_for_model(deliverable), rater=rater,
            target=target,
        )

    def get_deliverable(self):
        order = get_object_or_404(Deliverable, order_id=self.kwargs['order_id'], id=self.kwargs['deliverable_id'])
        self.check_object_permissions(self.request, order)
        return order


class RateBuyer(RateBase):
    permission_classes = [
        Any(
            All(IsSafeMethod, OrderViewPermission),
            All(OrderSellerPermission)
        ),
        DeliverableStatusPermission(COMPLETED, REFUNDED),
        PaidOrderPermission,
    ]

    def get_target(self):
        return self.get_deliverable().order.buyer

    def get_rater(self):
        return self.get_deliverable().order.seller


class RateSeller(RateBase):
    permission_classes = [
        Any(
            All(IsSafeMethod, OrderViewPermission),
            OrderBuyerPermission,
        ),
    ]

    def get_target(self):
        return self.get_deliverable().order.seller

    def get_rater(self):
        return self.get_deliverable().order.buyer


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
                'table_percentage': settings.TABLE_PERCENTAGE_FEE,
                'table_static': settings.TABLE_STATIC_FEE,
                'table_tax': settings.TABLE_TAX,
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
            'title': f"{username}'s store",
            'description': demark(user.artist_profile.commission_info),
            'image_links': [
                product.preview_link
                for product in user_products(username, self.request.user)[:24]
            ] + [user.avatar_url]
        }

    @method_decorator(xframe_options_exempt)
    def get(self, request, *args, **kwargs):
        return super(StorePreview, self).get(request, *args, **kwargs)


class ProductPreview(BasePreview):
    def context(self, username, product_id):
        product = get_object_or_404(Product, id=product_id, active=True, hidden=False)
        image = preview_rating(self.request, product.rating, product.preview_link)
        data = {
            'title': demark(product.name),
            'description': product.preview_description,
            'image_links': [
            preview_rating(self.request, sample.rating, sample.preview_link) for sample in
                product.samples.filter(private=False)
            ]
        }
        if image:
            data['image_links'] += [image]
        return data


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
        return Product.objects.filter(
            starting_price__lte=Decimal('30'), available=True,
        ).exclude(featured=True).exclude(table_product=True).order_by('?')


class HighlyRatedProducts(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(user__stars__gte=4.5, available=True).exclude(featured=True).order_by('?')


class LgbtProducts(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(user__artist_profile__lgbt=True, available=True).order_by('?')


class ArtistsOfColor(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(user__artist_profile__artist_of_color=True, available=True).order_by('?')



class NewArtistProducts(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        # Can't directly do order_by on this QS because the ORM breaks grouping by placing it before the annotation.
        return Product.objects.filter(id__in=Product.objects.all().annotate(
            completed_orders=Count('user__sales', filter=Q(user__sales__deliverables__status=COMPLETED))
        ).filter(completed_orders=0, available=True)).order_by('?')


class RandomProducts(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(featured=False, available=True).order_by('?')


def get_order_facts(product, serializer, seller):
    facts = {
        'table_order': False,
        'hold': serializer.validated_data.get('hold', False),
        'rating': serializer.validated_data.get('rating', 0),
    }
    if serializer.validated_data['completed']:
        raw_task_weight = 0
        raw_expected_turnaround = 0
        raw_revisions = 0
    else:
        raw_task_weight = serializer.validated_data['task_weight']
        raw_expected_turnaround = serializer.validated_data['expected_turnaround']
        raw_revisions = serializer.validated_data['revisions']
    if product:
        facts['price'] = product.base_price
        facts['adjustment'] = Money(serializer.validated_data['price'], 'USD') - product.get_starting_price()
        facts['task_weight'] = product.task_weight
        facts['adjustment_task_weight'] = raw_task_weight - product.task_weight
        facts['adjustment_expected_turnaround'] = raw_expected_turnaround - product.expected_turnaround
        facts['expected_turnaround'] = product.expected_turnaround
        facts['revisions'] = product.revisions
        facts['adjustment_revisions'] = raw_revisions - product.revisions
        facts['table_order'] = product.table_product
    else:
        facts['price'] = Money(serializer.validated_data['price'], 'USD')
        facts['task_weight'] = raw_task_weight
        facts['expected_turnaround'] = raw_expected_turnaround
        facts['revisions'] = raw_revisions
        facts['adjustment_task_weight'] = 0
        facts['adjustment_expected_turnaround'] = 0
        facts['adjustment_revisions'] = 0
        facts['adjustment'] = Money('0.00', 'USD')
    facts['paid'] = serializer.validated_data['paid'] or ((facts['price'] + facts['adjustment']) == Money('0', 'USD'))
    facts['escrow_disabled'] = (
            facts['paid'] or ((seller.artist_profile.bank_account_status != HAS_US_ACCOUNT) and not product.table_product)
    )
    if facts['paid']:
        if serializer.validated_data['completed']:
            # Seller still has to upload revisions.
            facts['status'] = IN_PROGRESS
        else:
            facts['status'] = QUEUED
        facts['revisions_hidden'] = False
    elif facts['hold']:
        facts['status'] = NEW
        facts['revisions_hidden'] = True
    else:
        facts['status'] = PAYMENT_PENDING
        facts['revisions_hidden'] = True
    return facts

class CreateInvoice(GenericAPIView):
    """
    Used to create a new order from the seller's side.
    """
    permission_classes = [IsRegistered, UserControls, BankingConfigured]
    serializer_class = NewInvoiceSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['seller'] = self.request.subject
        return context

    def post(self, request, username):
        user = get_object_or_404(User, username=username)
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        buyer = serializer.validated_data['buyer']
        product = serializer.validated_data.get('product', None)
        facts = get_order_facts(product, serializer, user)

        if isinstance(buyer, str) or buyer is None:
            customer_email = buyer or ''
            buyer = None
        else:
            buyer = buyer
            customer_email = ''
        try:
            with inventory_change(product):
                order = Order.objects.create(
                    seller=user,
                    buyer=buyer,
                    customer_email=customer_email,
                    product=product,
                    private=serializer.validated_data['private'],
                )
                deliverable_facts = {key: value for key, value in facts.items() if key not in (
                    'price', 'adjustment', 'hold', 'paid',
                )}
                deliverable = Deliverable.objects.create(
                    name='Main',
                    order=order,
                    details=serializer.validated_data['details'],
                    commission_info=request.subject.artist_profile.commission_info,
                    **deliverable_facts,
                )
                deliverable.line_items.get_or_create(
                    type=BASE_PRICE, amount=facts['price'], priority=0, destination_account=TransactionRecord.ESCROW,
                    destination_user=order.seller,
                )
                if facts['adjustment']:
                    deliverable.line_items.get_or_create(
                        type=ADD_ON, amount=facts['adjustment'], priority=1, destination_account=TransactionRecord.ESCROW,
                        destination_user=order.seller,
                    )
                # Trigger line item creation.
                deliverable.save()
                notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        except InventoryError:
            return Response(data={'detail': 'This product is out of stock.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=DeliverableViewSerializer(instance=deliverable, context=self.get_serializer_context()).data)


class CustomerHoldings(ListAPIView):
    permission_classes = [IsSuperuser]
    serializer_class = HoldingsSummarySerializer

    def get_queryset(self):
        return User.objects.filter(guest=False, sales__isnull=False).order_by('username').distinct()


class CustomerHoldingsCSV(CustomerHoldings):
    pagination_class = None
    renderer_classes = [CSVRenderer]

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = ['id', 'username', 'escrow', 'holdings']
        return context


class DateConstrained:
    request: Request
    date_field = 'created_on'

    @property
    def start_date(self) -> datetime:
        start_date = None
        default_start = timezone.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0,
        )
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
        default_end = self.start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        default_end += relativedelta(months=1)
        if default_end > timezone.now():
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
    serializer_class = DeliverableValuesSerializer
    permission_classes = [IsSuperuser]
    pagination_class = None
    report_name = 'order-report'

    def get_queryset(self):
        return Order.objects.filter(escrow_disabled=False).exclude(
            status__in=[CANCELLED, NEW, PAYMENT_PENDING],
        ).order_by('created_on')

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = [
            'id',
            'created_on',
            'status',
            'seller',
            'buyer',
            'price',
            'payment_type',
            'charged_on',
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
        ]
        return context


class SubscriptionReportCSV(CSVReport, ListAPIView, DateConstrained):
    serializer_class = SimpleTransactionSerializer
    permission_classes = [IsSuperuser]
    pagination_class = None
    report_name = 'subscription-report'

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = [
            'id',
            'status',
            'payer',
            'amount',
            'created_on',
            'remote_id',
        ]
        return context

    def get_queryset(self):
        return TransactionRecord.objects.filter(
            category__in=[TransactionRecord.SUBSCRIPTION_DUES, TransactionRecord.SUBSCRIPTION_REFUND],
            **self.date_kwargs,
        ).exclude(status=TransactionRecord.FAILURE)


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
            'remote_id',
        ]
        return context

    def get_queryset(self):
        return TransactionRecord.objects.filter(
            payer=F('payee'),
            source=TransactionRecord.HOLDINGS,
            destination=TransactionRecord.BANK,
            **self.date_kwargs,
        ).exclude(payer=None).exclude(status=TransactionRecord.FAILURE).order_by('-created_on')


class DwollaSetupFees(CSVReport, ListAPIView, DateConstrained):
    serializer_class = SimpleTransactionSerializer
    permission_classes = [IsSuperuser]
    pagination_class = None
    report_name = 'dwolla-report'

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = [
            'id',
            'status',
            'payer',
            'amount',
            'created_on',
        ]
        return context

    def get_queryset(self):
        return TransactionRecord.objects.filter(
            payee=None,
            destination=TransactionRecord.ACH_MISC_FEES,
            category=TransactionRecord.THIRD_PARTY_FEE,
            **self.date_kwargs,
        ).exclude(status=TransactionRecord.FAILURE)


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


class DeliverableCharacterList(ListAPIView):
    permission_classes = [OrderViewPermission]
    pagination_class = None
    serializer_class = DeliverableCharacterTagSerializer

    def get_queryset(self) -> QuerySet:
        return Deliverable.characters.through.objects.filter(deliverable=self.get_object())

    @lru_cache()
    def get_object(self) -> Deliverable:
        deliverable = get_object_or_404(
            Deliverable, order_id=self.kwargs['order_id'], id=self.kwargs['deliverable_id'],
        )
        self.check_object_permissions(self.request, deliverable)
        return deliverable


class DeliverableOutputs(ListCreateAPIView):
    permission_classes = [
        OrderViewPermission,
        DeliverableStatusPermission(COMPLETED),
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
        order = get_object_or_404(Deliverable, order_id=self.kwargs['order_id'], id=self.kwargs['deliverable_id'])
        self.check_object_permissions(self.request, order)
        return order

    def post(self, request, *args, **kwargs):
        deliverable = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        revision = deliverable.revision_set.all().last()
        if not revision:
            return Response(
                data={'detail': 'You can not create a submission from an order with no revisions.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save(
            owner=request.user, deliverable=deliverable, rating=deliverable.rating, file=revision.file,
        )
        instance.characters.set(deliverable.characters.all())
        instance.artists.add(deliverable.order.seller)
        for character in instance.characters.all():
            if request.user == character.user and not character.primary_submission:
                character.primary_submission = instance
                character.save()
        if deliverable.order.product and request.user == deliverable.order.seller:
            deliverable.order.product.samples.add(instance)
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
                'new_claim_link.html', target_email, {'order': order, 'claim_token': order.claim_token}
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

        ensure_buyer(order)
        login(request, order.buyer)
        order.claim_token = uuid4()
        order.save()
        return Response(status=status.HTTP_200_OK, data=self.user_info(order.buyer))


class Broadcast(CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsRegistered, UserControls]

    def get_object(self):
        return self.request.subject

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except Http404:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={'detail': 'You have no open orders to broadcast to.'},
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        self.check_object_permissions(self.request, self.get_object())
        checks = WEIGHTED_STATUSES + [REVIEW, DISPUTED, NEW]
        deliverables = Deliverable.objects.filter(
            status__in=checks, order__seller=self.request.subject,
        ).order_by('order_id').distinct('order_id')
        comment = None
        for deliverable in deliverables:
            comment = create_comment(deliverable, serializer, self.request.user)
            serializer.instance = Comment()
        if comment is None:
            raise Http404