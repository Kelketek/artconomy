import logging
from decimal import Decimal
from functools import lru_cache
from typing import Dict, Optional
from uuid import uuid4

from authlib.integrations.base_client import MissingTokenError
from django.contrib.postgres.search import SearchVector
from django.db.models.functions import Collate
from django.urls import reverse
from rest_framework.renderers import JSONRenderer
from short_stuff import gen_shortcode

from apps.lib.models import (
    Comment,
    Subscription,
    note_for_text,
    ref_for_instance,
)
from apps.lib.constants import (
    COMMENT,
    NEW_PRODUCT,
    DISPUTE,
    ORDER_UPDATE,
    SALE_UPDATE,
    REVISION_UPLOADED,
    STREAMING,
    REFERENCE_UPLOADED,
    WAITLIST_UPDATED,
    REVISION_APPROVED,
    PRODUCT_KILLED,
)
from apps.lib.permissions import (
    And,
    Or,
    IsMethod,
    IsSafeMethod,
    StaffPower,
    SessionKeySet,
)
from apps.lib.serializers import CommentSerializer, UserInfoSerializer, KillSerializer
from apps.lib.utils import (
    count_hit,
    create_comment,
    demark,
    mark_modified,
    mark_read,
    notify,
    preview_rating,
    recall_notification,
    send_transaction_email,
)
from apps.lib.views import BasePreview, PositionShift
from apps.profiles.models import (
    IN_SUPPORTED_COUNTRY,
    ArtistProfile,
    ArtistTag,
    Submission,
    User,
    trigger_reconnect,
)
from apps.profiles.permissions import (
    AccountCurrentPermission,
    BillTo,
    IsRegistered,
    IssuedBy,
    IsSuperuser,
    ObjectControls,
    staff_power,
)
from apps.profiles.serializers import SubmissionSerializer, UserSerializer
from apps.profiles.utils import (
    create_guest_user,
    empty_user,
    get_anonymous_user,
    available_submissions,
)
from apps.sales.constants import (
    ADD_ON,
    BASE_PRICE,
    CANCELLED,
    COMPLETED,
    CONCURRENCY_STATUSES,
    DISPUTED,
    DRAFT,
    ESCROW,
    EXTRA,
    FAILURE,
    IN_PROGRESS,
    LIMBO,
    MISSED,
    MONEY_HOLE,
    NEW,
    OPEN,
    PAYMENT_PENDING,
    QUEUED,
    REFUNDED,
    REVIEW,
    SALE,
    STRIPE,
    SUBSCRIPTION,
    TABLE_SERVICE,
    TAX,
    TIP,
    TIPPING,
    FUND,
    VOID,
    WAITING,
    WEIGHTED_STATUSES,
    WORK_IN_PROGRESS_STATUSES,
    VENDOR,
    HOLDINGS,
    ESCROW_HOLD,
    VENDOR_PAYMENT,
    DEFAULT_TYPE_TO_CATEGORY_MAP,
    TAXES,
    MONEY_HOLE_STAGE,
    PRIORITY_MAP,
    CASCADE_UNDER_MAP,
)
from apps.sales.models import (
    CreditCardToken,
    Deliverable,
    InventoryError,
    InventoryTracker,
    Invoice,
    LineItem,
    Order,
    Product,
    Rating,
    Reference,
    Revision,
    ServicePlan,
    TransactionRecord,
    inventory_change,
    PaypalConfig,
    ShoppingCart,
)
from apps.sales.paypal import (
    paypal_api,
    generate_paypal_invoice,
    delete_webhooks,
    clear_existing_invoice,
)
from apps.sales.permissions import (
    BankingConfigured,
    DeliverableNoProduct,
    DeliverableStatusPermission,
    EscrowDisabledPermission,
    EscrowPermission,
    HasRevisionsPermission,
    InvoiceStatus,
    InvoiceType,
    LandscapeSellerPermission,
    LimboCheck,
    LineItemTypePermission,
    OrderBuyerPermission,
    OrderPlacePermission,
    OrderSellerPermission,
    OrderTimeUpPermission,
    OrderViewPermission,
    PlanDeliverableAddition,
    PublicQueue,
    RevisionsVisible,
    RedactionAvailableDatePermission,
)
from apps.sales.serializers import (
    AccountBalanceSerializer,
    AccountQuerySerializer,
    CardSerializer,
    DeliverableCharacterTagSerializer,
    DeliverableReferenceSerializer,
    DeliverableSerializer,
    InventorySerializer,
    InvoiceSerializer,
    LineItemSerializer,
    NewDeliverableSerializer,
    NewInvoiceSerializer,
    OrderAuthSerializer,
    OrderPreviewSerializer,
    OrderViewSerializer,
    PaymentSerializer,
    ProductNewOrderSerializer,
    ProductSampleSerializer,
    ProductSerializer,
    RatingSerializer,
    ReferenceSerializer,
    RevisionSerializer,
    SearchQuerySerializer,
    ServicePlanSerializer,
    SetServiceSerializer,
    SubmissionFromOrderSerializer,
    TransactionRecordSerializer,
    NewPaypalConfigSerializer,
    PaypalConfigSerializer,
    SalesStatsSerializer,
    ShoppingCartSerializer,
    VendorInvoiceCreationSerializer,
)
from apps.sales.utils import (
    PENDING,
    POSTED_ONLY,
    account_balance,
    available_products,
    cancel_deliverable,
    claim_deliverable,
    ensure_buyer,
    finalize_deliverable,
    get_claim_token,
    initialize_tip_invoice,
    invoice_post_payment,
    refund_deliverable,
    set_service_plan,
    transfer_order,
    verify_total,
    mark_deliverable_paid,
    cart_for_request,
    redact_deliverable,
    pricing_spec,
)
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import login
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import (
    BooleanField,
    Case,
    Count,
    F,
    IntegerField,
    Q,
    QuerySet,
    When,
)
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.static import serve
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from moneyed import Money
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    GenericAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveDestroyAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.sales.views.webhooks import PAYPAL_WEBHOOK_ROUTES
from apps.sales.tasks import drip_placed_order
from shortcuts import make_url

logger = logging.getLogger(__name__)


def user_products(username: str, requester: User, show_hidden=False):
    qs = Product.objects.filter(user__username=username, active=True)
    if not (
        (
            requester.username.lower() == username.lower()
            or staff_power(requester, "view_as")
        )
        and show_hidden
    ):
        qs = qs.filter(hidden=False, table_product=False)
    qs = qs.order_by("-display_position")
    return qs


class ProductList(ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [
        Or(
            IsSafeMethod,
            And(
                IsRegistered,
                Or(
                    ObjectControls,
                    StaffPower("table_seller"),
                    StaffPower("moderate_content"),
                ),
            ),
        )
    ]

    def get(self, *args, **kwargs):
        self.check_object_permissions(self.request, self.request.subject)
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.check_object_permissions(self.request, self.request.subject)
        return super().post(*args, **kwargs)

    def perform_create(self, serializer):
        product = serializer.save(owner=self.request.subject, user=self.request.subject)
        if not product.hidden:
            notify(
                NEW_PRODUCT,
                self.request.subject,
                data={"product": product.id},
                unique_data=True,
            )
        return product

    def get_queryset(self):
        return user_products(
            self.kwargs["username"],
            self.request.user,
            show_hidden=self.kwargs.get("manage"),
        )


class ProductManager(RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [
        Or(
            IsSafeMethod,
            And(
                IsRegistered,
                Or(
                    StaffPower("moderate_content"),
                    StaffPower("table_seller"),
                    ObjectControls,
                ),
            ),
        )
    ]
    queryset = Product.objects.all()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        # post-save effects will change values.
        serializer.instance.refresh_from_db()

    @lru_cache()
    def get_object(self):
        product = get_object_or_404(
            Product,
            user__username=self.kwargs["username"],
            id=self.kwargs["product"],
            active=True,
        )
        hit_count = HitCount.objects.get_for_object(product)
        HitCountMixin.hit_count(self.request, hit_count)
        self.check_object_permissions(self.request, product)
        return product


class KillProduct(GenericAPIView):
    serializer = KillSerializer
    permission_classes = [StaffPower("moderate_content")]

    def get_object(self):
        product = get_object_or_404(
            Product,
            user__username=self.kwargs["username"],
            id=self.kwargs["product"],
            active=True,
        )
        self.check_object_permissions(self.request, product)
        return product

    def post(self, request, **kwargs):
        product = self.get_object()
        self.check_object_permissions(self.request, product)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reason = serializer.validated_data["flag"]
        product.removed_on = timezone.now()
        product.removed_by = request.user
        product.remove_reason = reason
        notify(
            PRODUCT_KILLED,
            product,
            data={"comment": serializer.validated_data["comment"]},
            unique=True,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductInventoryManager(RetrieveUpdateAPIView):
    serializer_class = InventorySerializer
    permission_classes = [
        Or(
            IsSafeMethod,
            And(IsRegistered, Or(ObjectControls, StaffPower("table_seller"))),
        )
    ]
    queryset = Product.objects.all()

    @lru_cache()
    def get_object(self):
        product = get_object_or_404(
            Product,
            user__username=self.kwargs["username"],
            id=self.kwargs["product"],
            active=True,
            track_inventory=True,
        )
        self.check_object_permissions(self.request, product)
        return product.inventory

    def perform_update(self, serializer):
        with transaction.atomic():
            tracker = InventoryTracker.objects.select_for_update().get(
                id=self.get_object().id
            )
            serializer.instance = tracker
            serializer.save()


class ProductSamples(ListCreateAPIView):
    serializer_class = ProductSampleSerializer
    permission_classes = [
        Or(
            IsSafeMethod,
            And(
                IsRegistered,
                Or(
                    ObjectControls,
                    StaffPower("moderate_content"),
                    StaffPower("table_seller"),
                ),
            ),
        )
    ]

    @lru_cache()
    def get_object(self):
        product = get_object_or_404(
            Product,
            id=self.kwargs["product"],
            user__username=self.kwargs["username"],
            active=True,
        )
        self.check_object_permissions(self.request, product)
        return product

    def get_serializer_context(self) -> Dict[str, Or]:
        context = super().get_serializer_context()
        context["product"] = self.get_object()
        return context

    def get_queryset(self) -> QuerySet:
        product = self.get_object()
        samples = Product.samples.through.objects.filter(product=self.get_object())
        if not self.request.user == product.user:
            samples = samples.exclude(submission__private=True)
        return samples.order_by("-submission__created_on")

    def perform_create(self, serializer):
        instance, _ = Product.samples.through.objects.get_or_create(
            product=self.get_object(),
            submission_id=serializer.validated_data["submission_id"],
        )
        serializer.instance = instance
        return instance


class ProductSampleManager(DestroyAPIView):
    permission_classes = [
        IsRegistered,
        Or(ObjectControls, StaffPower("moderate_content"), StaffPower("table_seller")),
    ]
    serializer_class = ProductSampleSerializer

    def get_object(self) -> Submission.artists.through:
        return get_object_or_404(
            Product.samples.through,
            id=self.kwargs["tag_id"],
            product__id=self.kwargs["product"],
            product__active=True,
        )

    def perform_destroy(self, instance: Submission.artists.through):
        self.check_object_permissions(self.request, instance.product)
        if instance.product.primary_submission == instance.submission:
            instance.product.primary_submission = None
            instance.product.save()
        instance.delete()


def derive_user_from_string(seller, user_string):
    if not user_string:
        return None
    try:
        user = User.objects.get(username=user_string, is_active=True)
    except User.DoesNotExist:
        try:
            user = User.objects.get(email=user_string, is_active=True)
        except User.DoesNotExist:
            user = create_guest_user(user_string)
            return user
    if user == seller:
        raise ValidationError("You cannot order your own product.")
    return user


class PlaceOrder(CreateAPIView):
    serializer_class = ProductNewOrderSerializer
    permission_classes = [
        Or(OrderPlacePermission, Or(ObjectControls, StaffPower("handle_disputes")))
    ]

    @lru_cache
    def get_object(self):
        return get_object_or_404(Product, id=self.kwargs["product"], active=True)

    def get_serializer_context(self) -> Dict[str, Or]:
        context = super().get_serializer_context()
        context["product"] = self.get_object()
        return context

    def perform_create(self, serializer):
        product = self.get_object()
        self.check_object_permissions(self.request, product)
        user = self.request.user
        reconnect = False
        user_string = serializer.validated_data.get("email", "")
        if staff_power(user, "table_seller") and product.table_product:
            user = create_guest_user(user_string)
        elif not user.is_authenticated:
            user = create_guest_user(user_string)
            login(self.request, user)
            reconnect = True
        elif (
            (product.user == self.request.user)
            or staff_power(user, "table_seller")
            and serializer.validated_data["invoicing"]
        ):
            user = derive_user_from_string(product.user, user_string)
        elif not user.is_registered:
            if self.request.user.guest_email != user_string:
                user = create_guest_user(user_string)
                login(self.request, user)
                reconnect = True
        order = serializer.save(
            buyer=user,
            seller=product.user,
        )
        over_limit = False
        if product.user.service_plan.max_simultaneous_orders:
            over_limit = (
                product.user.service_plan.max_simultaneous_orders
                <= Deliverable.objects.filter(
                    status__in=CONCURRENCY_STATUSES,
                    order__seller=product.user,
                ).count()
            )
        if product.wait_list:
            order_status = WAITING
        elif over_limit:
            order_status = LIMBO
        else:
            order_status = NEW
        escrow_enabled = product.escrow_enabled
        if not escrow_enabled and product.escrow_upgradable:
            escrow_enabled = serializer.validated_data["escrow_upgrade"]
        paypal = product.paypal
        paypal = paypal and not escrow_enabled
        deliverable = Deliverable.objects.create(
            order=order,
            product=product,
            status=order_status,
            paypal=paypal,
            table_order=product.table_product,
            name="Main",
            escrow_enabled=escrow_enabled,
            rating=serializer.validated_data["rating"],
            processor=STRIPE,
            created_by=user,
            cascade_fees=product.cascade_fees,
            details=serializer.validated_data["details"],
        )
        deliverable.characters.set(serializer.validated_data.get("characters", []))
        named_price = serializer.validated_data.get("named_price")
        if named_price:
            # This will always be at least as much as the default price.
            # If there's a remainder, add a line item to make up the difference.
            difference = named_price - deliverable.invoice.total()
            if difference:
                LineItem.objects.create(
                    type=ADD_ON,
                    priority=PRIORITY_MAP[ADD_ON],
                    cascade_under=CASCADE_UNDER_MAP[ADD_ON],
                    category=ESCROW_HOLD,
                    invoice=deliverable.invoice,
                    description="Offer",
                    amount=difference,
                    destination_account=ESCROW,
                    destination_user=deliverable.order.seller,
                )
        if self.request.user == user:
            drip_placed_order.delay(deliverable.order.id)
            cart = cart_for_request(self.request)
            if cart:
                cart.delete()
            for character in deliverable.characters.all():
                character.shared_with.add(order.seller)
        elif user:
            order.customer_email = user.guest_email
            order.save()
        for asset in serializer.validated_data.get("references", []):
            reference = Reference.objects.create(
                file=asset,
                owner=user or self.request.user,
                rating=deliverable.rating,
            )
            reference.deliverables.add(deliverable)
        if product.wait_list:
            notify(WAITLIST_UPDATED, order.seller, unique=True, mark_unread=True)
        else:
            notify(SALE_UPDATE, deliverable, unique=True, mark_unread=True)
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        if reconnect:
            trigger_reconnect(self.request, include_current=True)
        return order

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = self.get_object()
        try:
            with inventory_change(product):
                order = self.perform_create(serializer)
        except InventoryError:
            return Response(
                {"detail": "This product is not in stock."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = OrderPreviewSerializer(
            instance=order, context=self.get_serializer_context()
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class OrderManager(RetrieveUpdateAPIView):
    permission_classes = [OrderViewPermission]
    serializer_class = OrderViewSerializer
    queryset = Order.objects.all()

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs["order_id"])
        self.check_object_permissions(self.request, order)
        return order


class OrderDeliverables(ListCreateAPIView):
    permission_classes = [
        Or(
            And(OrderViewPermission, IsSafeMethod),
            And(OrderSellerPermission, LandscapeSellerPermission),
        )
    ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["seller"] = self.get_object().seller
        return context

    def get_serializer_class(self):
        if self.request.method == "POST":
            return NewDeliverableSerializer
        else:
            return DeliverableSerializer

    def get_queryset(self):
        return (
            self.get_object()
            .deliverables.exclude(status__in=[LIMBO, MISSED])
            .order_by("-created_on")
        )

    @lru_cache(256)
    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs["order_id"])
        self.check_object_permissions(self.request, order)
        return order

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data = DeliverableSerializer(
            instance=serializer.instance, context=self.get_serializer_context()
        ).data
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        order = self.get_object()
        self.check_object_permissions(self.request, order)
        product = serializer.validated_data.get("product", None)
        facts = get_order_facts(product, serializer, order.seller)
        deliverable_facts = {
            key: value
            for key, value in facts.items()
            if key
            not in (
                "price",
                "adjustment",
                "hold",
                "paid",
            )
        }
        deliverable = serializer.save(
            order=order,
            **deliverable_facts,
        )
        line, _ = deliverable.invoice.line_items.get_or_create(
            type=BASE_PRICE,
            amount=facts["price"],
            category=ESCROW_HOLD,
            priority=PRIORITY_MAP[BASE_PRICE],
            cascade_under=CASCADE_UNDER_MAP[BASE_PRICE],
            destination_account=ESCROW,
            destination_user=order.seller,
        )
        line.annotate(deliverable)
        if facts["adjustment"]:
            line, _ = deliverable.invoice.line_items.get_or_create(
                type=ADD_ON,
                amount=facts["adjustment"],
                priority=PRIORITY_MAP[ADD_ON],
                cascade_under=CASCADE_UNDER_MAP[ADD_ON],
                destination_account=ESCROW,
                category=ESCROW_HOLD,
                destination_user=order.seller,
            )
            line.annotate(deliverable)
        # Trigger line item creation.
        deliverable.save()
        deliverable.characters.set(serializer.validated_data.get("characters", []))
        deliverable.reference_set.set(serializer.validated_data.get("references", []))
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)


class DeliverableManager(RetrieveUpdateAPIView):
    permission_classes = [OrderViewPermission, LimboCheck]
    serializer_class = DeliverableSerializer
    queryset = Deliverable.objects.all()

    def get_object(self):
        deliverable = get_object_or_404(
            Deliverable,
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
        )
        self.check_object_permissions(self.request, deliverable)
        return deliverable

    @transaction.atomic
    def perform_update(self, serializer):
        escrow_changed = serializer.instance.escrow_enabled
        cascade_fees_changed = serializer.instance.cascade_fees
        deliverable = serializer.save()
        escrow_changed = escrow_changed != deliverable.escrow_enabled
        cascade_fees_changed = cascade_fees_changed != serializer.instance.cascade_fees
        field_name = "escrow_enabled" if escrow_changed else "amount"
        field_name = "cascade_fees" if cascade_fees_changed else field_name
        verify_total(deliverable, field_name)


class DeliverableInvite(GenericAPIView):
    permission_classes = [OrderSellerPermission, LimboCheck]
    serializer_class = OrderViewSerializer

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs["order_id"])
        return order

    def post(self, request, **kwargs):
        deliverable = get_object_or_404(
            Deliverable, order=self.get_object(), id=self.kwargs["deliverable_id"]
        )
        self.check_object_permissions(self.request, deliverable)
        if deliverable.order.buyer and not deliverable.order.buyer.guest:
            return Response(
                data={"detail": "This order has already been claimed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not deliverable.order.customer_email:
            return Response(
                data={"detail": "Customer email not set. Cannot send an invite!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        customer_email = deliverable.order.customer_email
        if deliverable.order.buyer:
            deliverable.order.buyer.guest_email = customer_email
            deliverable.order.buyer.save()
            subject = f"Claim Link for order #{deliverable.order.id}."
            template = "new_claim_link.html"
        else:
            new_user = create_guest_user(customer_email)
            transfer_order(deliverable.order, None, new_user, skip_notification=True)
            subject = (
                f"You have a new invoice from {deliverable.order.seller.username}!"
            )
            template = "invoice_issued.html"
        if not deliverable.order.claim_token:
            deliverable.order.claim_token = gen_shortcode()
            deliverable.order.save()
        send_transaction_email(
            subject,
            template,
            customer_email,
            {
                "deliverable": deliverable,
                "order": deliverable.order,
                "claim_token": deliverable.order.claim_token,
            },
        )
        return Response(
            status=status.HTTP_200_OK,
            data=self.get_serializer(instance=deliverable.order).data,
        )


class DeliverableAccept(GenericAPIView):
    permission_classes = [
        OrderSellerPermission,
        DeliverableStatusPermission(
            NEW, WAITING, error_message="Approval can only be applied to new orders."
        ),
    ]

    def get_object(self):
        deliverable = get_object_or_404(
            Deliverable,
            id=self.kwargs["deliverable_id"],
            order_id=self.kwargs["order_id"],
        )
        self.check_object_permissions(self.request, deliverable)
        return deliverable

    def post(self, request, *args, **kwargs):
        deliverable = self.get_object()
        deliverable.status = PAYMENT_PENDING
        deliverable.task_weight = (
            deliverable.product and deliverable.product.task_weight
        ) or deliverable.task_weight
        deliverable.expected_turnaround = (
            deliverable.product and deliverable.product.expected_turnaround
        ) or deliverable.expected_turnaround
        deliverable.revisions = (
            deliverable.product and deliverable.product.revisions
        ) or deliverable.revisions
        if deliverable.invoice.total() <= Money("0", "USD"):
            deliverable.status = QUEUED
            deliverable.revisions_hidden = False
            deliverable.escrow_enabled = False
        # Only actually generates if all conditions for generation are true.
        deliverable.paypal = generate_paypal_invoice(deliverable)
        deliverable.save()
        deliverable.invoice.status = OPEN
        deliverable.invoice.save()
        data = DeliverableSerializer(
            instance=deliverable, context=self.get_serializer_context()
        ).data
        if (not deliverable.order.buyer) and deliverable.order.customer_email:
            subject = (
                f"You have a new invoice from {deliverable.order.seller.username}!"
            )
            template = "invoice_issued.html"
            send_transaction_email(
                subject,
                template,
                deliverable.order.customer_email,
                {
                    "deliverable": deliverable,
                    "order": deliverable.order,
                    "claim_token": deliverable.order.claim_token,
                },
            )
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        return Response(data)


class WaitlistOrder(GenericAPIView):
    permission_classes = [
        OrderSellerPermission,
        DeliverableStatusPermission(
            NEW,
            error_message="You can only waitlist orders if they are new and haven't "
            "been accepted.",
        ),
    ]
    serializer_class = DeliverableSerializer

    def get_object(self):
        return get_object_or_404(
            Deliverable,
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
        )

    @transaction.atomic
    def post(self, request, **_kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(request, deliverable)
        deliverable.status = WAITING
        deliverable.save()
        data = self.serializer_class(
            instance=deliverable, context=self.get_serializer_context()
        ).data
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        return Response(data)


class MakeNew(GenericAPIView):
    permission_classes = [
        OrderSellerPermission,
        DeliverableStatusPermission(
            WAITING,
            error_message="This endpoint is for moving waitlisted orders back into "
            "'NEW' status.",
        ),
    ]
    serializer_class = DeliverableSerializer

    def get_object(self):
        return get_object_or_404(
            Deliverable,
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
        )

    @transaction.atomic
    def post(self, request, **_kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(request, deliverable)
        deliverable.status = NEW
        deliverable.auto_cancel_disabled = True
        deliverable.save()
        data = self.serializer_class(
            instance=deliverable, context=self.get_serializer_context()
        ).data
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        return Response(data)


class MarkPaid(GenericAPIView):
    permission_classes = [
        OrderSellerPermission,
        DeliverableStatusPermission(
            PAYMENT_PENDING,
            error_message="You can only mark orders paid if they are waiting for "
            "payment.",
        ),
    ]
    serializer_class = DeliverableSerializer

    def get_object(self):
        return get_object_or_404(
            Deliverable,
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
        )

    @transaction.atomic
    def post(self, request, **_kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(request, deliverable)
        if deliverable.invoice.paypal_token:
            # There exists a paypal invoice for this, which we need to cancel
            # since we're manually marking this paid.
            with paypal_api(deliverable.order.seller) as paypal:
                clear_existing_invoice(paypal, deliverable.invoice)
                deliverable.paypal = False
                deliverable.invoice.paypal_token = ""
                deliverable.invoice.save()
        else:
            deliverable.paypal = False
        mark_deliverable_paid(deliverable)
        data = self.serializer_class(
            instance=deliverable, context=self.get_serializer_context()
        ).data
        return Response(data)


class DeliverableStart(GenericAPIView):
    permission_classes = [
        OrderSellerPermission,
        DeliverableStatusPermission(
            QUEUED,
            error_message="You can only start orders that are queued.",
        ),
    ]
    serializer_class = DeliverableSerializer

    def get_object(self):
        order = get_object_or_404(
            Deliverable,
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
        )
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
                STREAMING,
                deliverable.order.seller,
                data={"order": deliverable.id},
                unique_data=True,
                exclude=[deliverable.order.buyer, deliverable.order.seller],
            )
        return Response(
            data=DeliverableSerializer(
                instance=deliverable, context=self.get_serializer_context()
            ).data
        )


class DeliverableCancel(GenericAPIView):
    permission_classes = [
        OrderViewPermission,
        DeliverableStatusPermission(
            WAITING,
            NEW,
            PAYMENT_PENDING,
            error_message="You cannot cancel this order. It is either already "
            "cancelled, finalized, or must be refunded instead.",
        ),
    ]
    serializer_class = DeliverableSerializer

    def get_object(self):
        deliverable = get_object_or_404(
            Deliverable,
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
        )
        self.check_object_permissions(self.request, deliverable)
        return deliverable

    # noinspection PyUnusedLocal
    def post(self, request, order_id, deliverable_id):
        deliverable = self.get_object()
        cancel_deliverable(deliverable, self.request.user)
        data = self.serializer_class(
            instance=deliverable, context=self.get_serializer_context()
        ).data
        return Response(data)


class DeliverableRedact(GenericAPIView):
    permission_classes = [
        Or(
            And(
                OrderSellerPermission,
                DeliverableStatusPermission(
                    CANCELLED,
                    REFUNDED,
                    COMPLETED,
                    error_message="This order must be completed, "
                    "cancelled, or refunded before it can be redacted.",
                ),
                RedactionAvailableDatePermission,
            ),
            And(
                StaffPower("table_seller"),
                DeliverableStatusPermission(
                    CANCELLED,
                    REFUNDED,
                    COMPLETED,
                    NEW,
                    PAYMENT_PENDING,
                    MISSED,
                    LIMBO,
                    error_message="This order is still in progress and must be "
                    "completed, cancelled, or refunded first.",
                ),
            ),
        ),
    ]
    serializer_class = DeliverableSerializer

    def get_object(self):
        deliverable = get_object_or_404(
            Deliverable,
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
        )
        self.check_object_permissions(self.request, deliverable)
        return deliverable

    # noinspection PyUnusedLocal
    def post(self, request, order_id, deliverable_id):
        deliverable = self.get_object()
        redact_deliverable(deliverable)
        data = self.serializer_class(
            instance=deliverable, context=self.get_serializer_context()
        ).data
        return Response(data)


class ClearWaitlist(GenericAPIView):
    permission_classes = [
        Or(ObjectControls, StaffPower("administrate_users"), StaffPower("table_seller"))
    ]

    def get_object(self):
        product = get_object_or_404(
            Product, user__username=self.kwargs["username"], id=self.kwargs["product"]
        )
        self.check_object_permissions(self.request, product)
        return product

    def post(self, *args, **kwargs):
        for deliverable in self.get_object().deliverables.filter(status=WAITING):
            cancel_deliverable(deliverable, self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class InvoiceLineItems(ListCreateAPIView):
    permission_classes = [
        Or(
            And(IsSafeMethod, Or(BillTo, IssuedBy)),
            StaffPower("table_seller"),
        ),
        Or(IsSafeMethod, InvoiceStatus(DRAFT, OPEN)),
    ]
    pagination_class = None
    serializer_class = LineItemSerializer

    def get_object(self):
        invoice = get_object_or_404(Invoice, id=self.kwargs["invoice"])
        self.check_object_permissions(self.request, invoice)
        return invoice

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["invoice"] = self.get_object()
        return context

    def get_queryset(self) -> QuerySet:
        return LineItem.objects.filter(invoice=self.get_object()).order_by(
            "priority", "id"
        )

    def perform_create(self, serializer: LineItemSerializer) -> None:
        if serializer.validated_data["type"] not in [EXTRA, TIP]:
            raise ValidationError(
                {"type": "Manual creation of this line-item type not supported."}
            )
        serializer.save(
            invoice=self.get_object(),
            destination_account=FUND,
            category=DEFAULT_TYPE_TO_CATEGORY_MAP[serializer.validated_data["type"]],
            priority=PRIORITY_MAP[serializer.validated_data["type"]],
            cascade_under=CASCADE_UNDER_MAP[serializer.validated_data["type"]],
        )


class InvoiceLineItemManager(RetrieveUpdateDestroyAPIView):
    permission_classes = [
        Or(StaffPower("table_seller"), BillTo, IssuedBy),
        InvoiceStatus(DRAFT),
    ]
    serializer_class = LineItemSerializer
    queryset = LineItem.objects.all()

    def get_object(self):
        line_item = get_object_or_404(
            LineItem, invoice_id=self.kwargs["invoice"], id=self.kwargs["line_item"]
        )
        self.check_object_permissions(self.request, line_item.invoice)
        return line_item


InvoiceLineItemManager.patch = transaction.atomic(InvoiceLineItemManager.patch)
InvoiceLineItemManager.delete = transaction.atomic(InvoiceLineItemManager.delete)


class DeliverableLineItems(ListCreateAPIView):
    permission_classes = [
        Or(
            And(
                Or(
                    IsSafeMethod,
                    And(
                        IsMethod("POST"),
                        DeliverableStatusPermission(
                            NEW,
                            WAITING,
                        ),
                    ),
                ),
                OrderViewPermission,
            ),
        )
    ]
    pagination_class = None
    serializer_class = LineItemSerializer

    @lru_cache()
    def get_object(self):
        return get_object_or_404(
            Deliverable.objects.select_for_update(),
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
        )

    def get_queryset(self):
        deliverable = self.get_object()
        return deliverable.invoice.line_items.exclude(type=TIP, amount=0)

    def get_serializer_context(self):
        deliverable = self.get_object()
        return {
            **super().get_serializer_context(),
            "deliverable": deliverable,
            "invoice": deliverable.invoice,
        }

    # Overkill, but only way to avoid writing a bunch of confusing, repetitive code
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(request, deliverable)
        return super().get(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(request, deliverable)
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        item_type = serializer.validated_data.get("type", ADD_ON)
        deliverable = self.get_object()
        destination_user = deliverable.order.seller
        if item_type in [TAX, EXTRA, TABLE_SERVICE]:
            destination_user = None
        accounts = {
            TAX: MONEY_HOLE_STAGE,
            ADD_ON: ESCROW,
            TIP: ESCROW,
            BASE_PRICE: ESCROW,
            TABLE_SERVICE: FUND,
            EXTRA: FUND,
        }
        destination_account = accounts[item_type]
        with transaction.atomic():
            line = serializer.save(
                destination_user=destination_user,
                destination_account=destination_account,
                invoice=deliverable.invoice,
                category=DEFAULT_TYPE_TO_CATEGORY_MAP[item_type],
                priority=CASCADE_UNDER_MAP[item_type],
                cascade_under=CASCADE_UNDER_MAP[item_type],
            )
            line.annotate(deliverable)
            deliverable.save()
            verify_total(deliverable)


class DeliverableLineItemManager(RetrieveUpdateDestroyAPIView):
    permission_classes = [
        Or(
            And(IsSafeMethod, OrderViewPermission),
            And(
                IsMethod("PATCH", "DELETE"),
                DeliverableStatusPermission(NEW, WAITING),
                Or(
                    And(
                        OrderSellerPermission,
                        Or(
                            LineItemTypePermission(ADD_ON),
                            And(
                                DeliverableNoProduct,
                                And(
                                    LineItemTypePermission(BASE_PRICE),
                                    IsMethod("PATCH"),
                                ),
                            ),
                        ),
                    ),
                    And(OrderBuyerPermission, LineItemTypePermission(TIP)),
                    And(
                        StaffPower("table_seller"),
                        LineItemTypePermission(EXTRA, TABLE_SERVICE),
                    ),
                    IsSuperuser,
                ),
            ),
        )
    ]
    serializer_class = LineItemSerializer
    queryset = LineItem.objects.all()

    @lru_cache
    def get_object(self):
        deliverable = get_object_or_404(Deliverable, id=self.kwargs["deliverable_id"])
        line_item = get_object_or_404(
            LineItem, id=self.kwargs["line_item_id"], invoice_id=deliverable.invoice_id
        )
        self.check_object_permissions(self.request, line_item)
        return line_item

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "deliverable": self.get_object()}

    def perform_destroy(self, instance):
        instance.delete()
        deliverable = get_object_or_404(Deliverable, id=self.kwargs["deliverable_id"])
        deliverable.save()

    def perform_update(self, serializer):
        serializer.save()
        deliverable = serializer.instance.invoice.deliverables.select_for_update().get()
        verify_total(deliverable)
        # Trigger automatic creation/destruction of shield lines.
        deliverable.save()


DeliverableLineItemManager.patch = transaction.atomic(DeliverableLineItemManager.patch)
DeliverableLineItemManager.delete = transaction.atomic(
    DeliverableLineItemManager.delete
)


class DeliverableRevisions(ListCreateAPIView):
    permission_classes = [
        Or(
            And(
                IsSafeMethod,
                OrderViewPermission,
                Or(RevisionsVisible, OrderSellerPermission),
            ),
            And(
                OrderSellerPermission,
                IsMethod("POST"),
                DeliverableStatusPermission(
                    IN_PROGRESS,
                    PAYMENT_PENDING,
                    NEW,
                    QUEUED,
                    DISPUTED,
                    WAITING,
                    error_message="You may not upload revisions while the order is in "
                    "this state.",
                ),
            ),
        ),
    ]
    pagination_class = None
    serializer_class = RevisionSerializer

    @lru_cache()
    def get_object(self):
        return get_object_or_404(
            Deliverable,
            id=self.kwargs["deliverable_id"],
            order_id=self.kwargs["order_id"],
        )

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
        comment_serializer: Optional[CommentSerializer] = None
        if text := serializer.validated_data.get("text", None):
            comment_serializer = CommentSerializer(data={"text": text})
            comment_serializer.is_valid(raise_exception=True)
        deliverable = self.get_object()
        revision = serializer.save(
            deliverable=deliverable, owner=self.request.user, rating=deliverable.rating
        )
        deliverable.refresh_from_db()
        if deliverable.status == QUEUED:
            deliverable.status = IN_PROGRESS
        if serializer.validated_data.get("final"):
            deliverable.final_uploaded = True
            if not deliverable.escrow_enabled:
                deliverable.status = COMPLETED
                deliverable.redact_available_on = timezone.now().date()
            elif deliverable.status == IN_PROGRESS:
                deliverable.status = REVIEW
                deliverable.auto_finalize_on = (
                    timezone.now() + relativedelta(days=5)
                ).date()
            deliverable.save()
            notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        else:
            notify(
                REVISION_UPLOADED,
                deliverable,
                data={"revision": revision.id},
                unique_data=True,
                mark_unread=True,
            )
        deliverable.save()
        recall_notification(
            STREAMING, deliverable.order.seller, data={"order": deliverable.id}
        )
        if comment_serializer:
            create_comment(revision, comment_serializer, self.request.user)
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
        return get_object_or_404(
            Deliverable,
            id=self.kwargs["deliverable_id"],
            order_id=self.kwargs["order_id"],
        )

    def get_queryset(self):
        deliverable = self.get_object()
        return Reference.deliverables.through.objects.filter(
            deliverable=deliverable
        ).order_by("-reference__created_on")

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
            subscriber=deliverable.order.seller,
            type=COMMENT,
            object_id=reference.id,
            content_type=content_type,
            email=True,
        )
        if deliverable.order.buyer:
            Subscription.objects.get_or_create(
                subscriber=deliverable.order.buyer,
                type=COMMENT,
                email=True,
                content_type=content_type,
                object_id=reference.id,
            )
        if deliverable.arbitrator:
            Subscription.objects.get_or_create(
                subscriber=deliverable.arbitrator,
                type=COMMENT,
                email=True,
                content_type=content_type,
                object_id=reference.id,
            )
        notify(
            REFERENCE_UPLOADED,
            deliverable,
            data={"reference": reference.id},
            unique_data=True,
            mark_unread=True,
            exclude=[self.request.user],
        )
        mark_modified(obj=reference, deliverable=deliverable, order=deliverable.order)
        mark_read(obj=reference, user=self.request.user)
        return deliverable_reference


class ReferenceManager(RetrieveUpdateDestroyAPIView):
    serializer_class = ReferenceSerializer
    permission_classes = [OrderViewPermission]

    def perform_destroy(self, instance):
        if not (
            staff_power(self.request.user, "handle_disputes")
            or instance.owner == self.request.user
        ):
            # Probably should find some cleaner way to check this with the permissions
            # framework.
            raise PermissionDenied(
                "You do not have the right to remove this reference."
            )
        deliverable = get_object_or_404(
            Deliverable,
            id=self.kwargs["deliverable_id"],
            order_id=self.kwargs["order_id"],
        )
        deliverable.reference_set.remove(instance)
        if not instance.deliverables.all().count():
            instance.delete()

    def get_object(self):
        deliverable = get_object_or_404(
            Deliverable,
            id=self.kwargs["deliverable_id"],
            order_id=self.kwargs["order_id"],
        )
        reference = get_object_or_404(
            Reference,
            deliverables=deliverable,
            id=self.kwargs["reference_id"],
        )
        self.check_object_permissions(self.request, deliverable)
        return reference


delete_forbidden_message = (
    "You may not remove revisions from this order. They are either locked or under "
    "dispute."
)


class RevisionManager(RetrieveDestroyAPIView):
    permission_classes = [
        Or(
            And(
                IsMethod("DELETE"),
                OrderSellerPermission,
                Or(
                    DeliverableStatusPermission(
                        REVIEW,
                        PAYMENT_PENDING,
                        NEW,
                        IN_PROGRESS,
                        WAITING,
                        error_message=delete_forbidden_message,
                    ),
                    And(
                        EscrowDisabledPermission,
                        DeliverableStatusPermission(
                            COMPLETED,
                            error_message=delete_forbidden_message,
                        ),
                    ),
                ),
            ),
            And(
                IsMethod("GET"),
                OrderViewPermission,
                Or(
                    OrderSellerPermission,
                    RevisionsVisible,
                ),
            ),
        )
    ]
    serializer_class = RevisionSerializer

    def get_object(self):
        deliverable = get_object_or_404(
            Deliverable,
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
        )
        revision = get_object_or_404(
            Revision,
            id=self.kwargs["revision_id"],
            deliverable_id=self.kwargs["deliverable_id"],
        )
        self.check_object_permissions(self.request, deliverable)
        return revision

    def perform_destroy(self, instance):
        revision_id = instance.id
        super(RevisionManager, self).perform_destroy(instance)
        deliverable = Deliverable.objects.get(
            id=self.kwargs["deliverable_id"], order_id=self.kwargs["order_id"]
        )
        recall_notification(
            REVISION_UPLOADED,
            deliverable,
            data={"revision": revision_id},
            unique_data=True,
        )
        if deliverable.final_uploaded:
            deliverable.final_uploaded = False
        if deliverable.status in [REVIEW, COMPLETED]:
            deliverable.auto_finalize_on = None
            deliverable.status = IN_PROGRESS
        deliverable.save()


reopen_error_message = "This order cannot be reopened."


class ReOpen(GenericAPIView):
    serializer_class = DeliverableSerializer
    permission_classes = [
        OrderSellerPermission,
        Or(
            DeliverableStatusPermission(
                REVIEW,
                PAYMENT_PENDING,
                DISPUTED,
                error_message=reopen_error_message,
            ),
            And(
                EscrowDisabledPermission,
                DeliverableStatusPermission(
                    COMPLETED, error_message=reopen_error_message
                ),
            ),
        ),
    ]

    def get_object(self):
        return get_object_or_404(
            Deliverable,
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
        )

    def post(self, _request, *_args, **_kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(self.request, deliverable)
        if deliverable.status not in [PAYMENT_PENDING, DISPUTED]:
            deliverable.status = IN_PROGRESS
        deliverable.final_uploaded = False
        deliverable.auto_finalize_on = None
        deliverable.redact_available_on = None
        deliverable.save()
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        serializer = self.get_serializer(instance=deliverable)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class MarkComplete(GenericAPIView):
    serializer_class = DeliverableSerializer
    permission_classes = [
        OrderSellerPermission,
        DeliverableStatusPermission(
            IN_PROGRESS,
            PAYMENT_PENDING,
            error_message="You cannot mark an order complete if it is not in progress.",
        ),
        HasRevisionsPermission,
    ]

    def get_object(self):
        return get_object_or_404(
            Deliverable,
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
        )

    def post(self, _request, *_args, **_kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(self.request, deliverable)
        if (
            deliverable.revision_set.all().exists()
            and deliverable.status == PAYMENT_PENDING
        ):
            deliverable.final_uploaded = True
            deliverable.save()
            serializer = self.get_serializer(instance=deliverable)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        deliverable.final_uploaded = True
        if not deliverable.escrow_enabled:
            deliverable.status = COMPLETED
            deliverable.redact_available_on = timezone.now().date()
        else:
            deliverable.status = REVIEW
            deliverable.auto_finalize_on = (
                timezone.now() + relativedelta(days=2)
            ).date()
        deliverable.save()
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        serializer = self.get_serializer(instance=deliverable)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class StartDispute(GenericAPIView):
    permission_classes = [
        OrderBuyerPermission,
        EscrowPermission,
        DeliverableStatusPermission(
            REVIEW,
            IN_PROGRESS,
            QUEUED,
            error_message="This order is not in a disputable state.",
        ),
        # Slight redundancy here to ensure the right error messages display.
        Or(
            And(
                OrderTimeUpPermission, DeliverableStatusPermission(IN_PROGRESS, QUEUED)
            ),
            DeliverableStatusPermission(REVIEW),
        ),
    ]
    serializer_class = DeliverableSerializer

    def get_object(self):
        return get_object_or_404(
            Deliverable,
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
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
    permission_classes = [StaffPower("handle_disputes")]
    serializer_class = DeliverableSerializer

    def get_object(self):
        return get_object_or_404(
            Deliverable,
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
        )

    # noinspection PyUnusedLocal
    def post(self, request, order_id, deliverable_id):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        if obj.arbitrator and obj.arbitrator != request.user:
            raise PermissionDenied(
                "An arbitrator has already been assigned to this dispute."
            )
        claim_deliverable(request.user, obj)
        serializer = self.get_serializer(instance=obj)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class DeliverableRefund(GenericAPIView):
    permission_classes = [
        OrderSellerPermission,
        DeliverableStatusPermission(
            QUEUED,
            IN_PROGRESS,
            REVIEW,
            DISPUTED,
            error_message="This order is not in a refundable state.",
        ),
    ]
    serializer_class = DeliverableSerializer

    def get_object(self):
        return get_object_or_404(
            Deliverable,
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
        )

    def post(self, request, *_args, **_kwargs):
        deliverable = self.get_object()
        self.check_object_permissions(request, deliverable)
        refunded, message = refund_deliverable(
            deliverable, requesting_user=request.user
        )
        if not refunded:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"detail": message}
            )
        serializer = self.get_serializer(
            instance=deliverable, context=self.get_serializer_context()
        )
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ApproveRevision(GenericAPIView):
    permission_classes = [
        DeliverableStatusPermission(
            QUEUED,
            IN_PROGRESS,
            REVIEW,
            DISPUTED,
            error_message="Revisions are finalized for this deliverable.",
        ),
        OrderBuyerPermission,
        RevisionsVisible,
    ]
    serializer_class = RevisionSerializer

    def get_object(self):
        deliverable = get_object_or_404(
            Deliverable,
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
        )
        revision = get_object_or_404(
            Revision,
            id=self.kwargs["revision_id"],
            deliverable_id=self.kwargs["deliverable_id"],
        )
        self.check_object_permissions(self.request, deliverable)
        return revision

    def post(self, request, *_args, **_kwargs):
        revision = self.get_object()
        if revision.approved_on:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"detail": "This revision has already been approved."},
            )
        revision.approved_on = timezone.now()
        revision.save()
        notify(REVISION_APPROVED, revision)
        return Response(
            status=status.HTTP_200_OK,
            data=RevisionSerializer(
                instance=revision, context=self.get_serializer_context()
            ).data,
        )


class ApproveFinal(GenericAPIView):
    permission_classes = [
        OrderBuyerPermission,
        EscrowPermission,
        DeliverableStatusPermission(
            REVIEW, DISPUTED, error_message="This order is not in an approvable state."
        ),
    ]
    serializer_class = DeliverableSerializer

    def get_object(self):
        return get_object_or_404(
            Deliverable,
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
        )

    def post(self, request, *_args, **_kwargs):
        order = self.get_object()
        self.check_object_permissions(self.request, order)
        finalize_deliverable(order, request.user)
        return Response(
            status=status.HTTP_200_OK,
            data=DeliverableSerializer(
                instance=order, context=self.get_serializer_context()
            ).data,
        )


class CurrentMixin(object):
    buyer = False

    def extra_filter(self, qs):
        statuses = [NEW, PAYMENT_PENDING, QUEUED, IN_PROGRESS, REVIEW, DISPUTED]
        if self.buyer:
            statuses.append(LIMBO)
        return (
            qs.filter(
                deliverables__status__in=statuses,
            )
            .distinct()
            .order_by("-created_on")
        )


class ArchivedMixin(object):
    def extra_filter(self, qs):
        return (
            qs.exclude(
                deliverables__status__in=[
                    WAITING,
                    NEW,
                    PAYMENT_PENDING,
                    QUEUED,
                    IN_PROGRESS,
                    REVIEW,
                    DISPUTED,
                ]
            )
            .filter(
                deliverables__status=COMPLETED,
            )
            .distinct()
            .order_by("-created_on")
        )


class CancelledMixin(object):
    buyer = False

    def extra_filter(self, qs):
        statuses = [
            WAITING,
            NEW,
            PAYMENT_PENDING,
            QUEUED,
            IN_PROGRESS,
            DISPUTED,
            REVIEW,
            COMPLETED,
            LIMBO,
        ]
        if not self.buyer:
            statuses.append(MISSED)
        return (
            qs.exclude(
                deliverables__status__in=statuses,
            )
            .distinct()
            .order_by("-created_on")
        )


class WaitingMixin(object):
    def extra_filter(self, qs):
        return (
            qs.filter(deliverables__status=WAITING).distinct().order_by("-created_on")
        )


class OrderListBase(ListAPIView):
    permission_classes = [
        Or(ObjectControls, StaffPower("view_as"), StaffPower("table_seller"))
    ]
    serializer_class = OrderPreviewSerializer

    def extra_filter(self, qs):  # pragma: no cover
        return qs

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs["username"])

    def get_queryset(self):
        return self.extra_filter(self.user.buys.all())

    # noinspection PyAttributeOutsideInit
    def get(self, *args, **kwargs):
        self.user = self.get_object()
        self.check_object_permissions(self.request, self.user)
        return super().get(*args, **kwargs)


class CurrentOrderList(CurrentMixin, OrderListBase):
    buyer = True


class ArchivedOrderList(ArchivedMixin, OrderListBase):
    buyer = True


class CancelledOrderList(CancelledMixin, OrderListBase):
    buyer = True


class WaitingOrderList(WaitingMixin, OrderListBase):
    buyer = True


class SalesListBase(ListAPIView):
    permission_classes = [
        Or(ObjectControls, StaffPower("view_as"), StaffPower("table_seller"))
    ]
    serializer_class = OrderPreviewSerializer

    def extra_filter(self, qs):  # pragma: no cover
        return qs

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs["username"])

    def get_queryset(self):
        qs = self.extra_filter(self.user.sales.all())
        self.check_object_permissions(self.request, self.get_object())
        query = self.request.GET.get("q", "").strip()
        try:
            kwargs = {
                "deliverables__product_id": int(self.request.GET.get("product", ""))
            }
        except (ValueError, TypeError):
            kwargs = {}
        qs = qs.filter(**kwargs)
        # Fox: Please note that this has been changed at user request at least once.
        # if we get complaints again, we're going to have to enable user sorting.
        if not query:
            return qs.distinct().order_by("created_on")
        qs = qs.annotate(
            buyer_username_case=Collate("buyer__username", "und-x-icu"),
        )
        qs = qs.annotate(
            search=SearchVector("deliverables__details", "deliverables__notes")
        )
        return (
            qs.filter(
                Q(buyer_username_case__startswith=query)
                | Q(buyer__email__istartswith=query)
                | Q(customer_email__istartswith=query)
                | Q(buyer__guest=True, buyer__guest_email__istartswith=query)
                | Q(search=query)
            )
            .distinct()
            .order_by("created_on")
        )

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


class WaitingSalesList(WaitingMixin, SalesListBase):
    pass


class PublicSalesQueue(ListAPIView):
    serializer_class = OrderPreviewSerializer
    permission_classes = [Or(ObjectControls, StaffPower("view_as"), PublicQueue)]

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs["username"])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["public"] = True
        return context

    def get_queryset(self):
        return self.extra_filter(self.user.sales.all())

    @staticmethod
    def extra_filter(qs):  # pragma: no cover
        return (
            qs.filter(
                deliverables__status__in=[
                    PAYMENT_PENDING,
                    QUEUED,
                    IN_PROGRESS,
                    REVIEW,
                    DISPUTED,
                ],
            )
            .distinct()
            .order_by("-created_on")
        )

    # noinspection PyAttributeOutsideInit
    def get(self, *args, **kwargs):
        self.user = self.get_object()
        self.check_object_permissions(self.request, self.user)
        return super().get(*args, **kwargs)


class SearchWaiting(ListAPIView):
    permission_classes = [IsRegistered, Or(ObjectControls, StaffPower("table_seller"))]
    serializer_class = OrderPreviewSerializer

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(self.request, user)
        return user


class CasesListBase(ListAPIView):
    permission_classes = [StaffPower("handle_disputes")]
    serializer_class = OrderPreviewSerializer

    @staticmethod
    def extra_filter(qs):  # pragma: no cover
        return qs

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs["username"])

    def get_queryset(self):
        self.check_object_permissions(self.request, self.user)
        return (
            self.extra_filter(
                Order.objects.filter(deliverables__in=self.user.cases.all()),
            )
            .distinct()
            .order_by("-created_on")
        )

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


# Included for test symmetry. Not used for anything practical.
class WaitingCasesList(WaitingMixin, CasesListBase):
    pass


class CardList(ListAPIView):
    permission_classes = [
        Or(
            And(IsSafeMethod, Or(ObjectControls, StaffPower("view_financials"))),
            And(
                IsRegistered,
                Or(
                    ObjectControls,
                    StaffPower("administrate_users"),
                    StaffPower("table_seller"),
                ),
            ),
        ),
    ]
    serializer_class = CardSerializer
    pagination_class = None

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(self.request, user)
        qs = user.credit_cards.filter(active=True)
        if self.kwargs.get("stripe"):
            qs = qs.exclude(stripe_token=None)
        # Primary card should always be listed first.
        qs = qs.annotate(
            primary=Case(
                When(user__primary_card_id=F("id"), then=1),
                default=0,
                output_field=BooleanField(),
            )
        )
        return qs.order_by("-primary", "-created_on")


class CardManager(RetrieveUpdateDestroyAPIView):
    permission_classes = [
        IsRegistered,
        Or(
            ObjectControls,
            StaffPower("administrate_users"),
            StaffPower("table_seller"),
            And(IsSafeMethod, StaffPower("view_financials")),
        ),
    ]
    serializer_class = CardSerializer
    queryset = CreditCardToken.objects.all()

    def get_object(self):
        card = get_object_or_404(
            CreditCardToken,
            user__username=self.kwargs["username"],
            id=self.kwargs["card_id"],
            active=True,
        )
        self.check_object_permissions(self.request, card)
        return card

    def perform_destroy(self, instance):
        instance.mark_deleted()


class MakePrimary(APIView):
    serializer_class = CardSerializer
    permission_classes = [IsRegistered, Or(ObjectControls, StaffPower("table_seller"))]

    def get_object(self):
        return get_object_or_404(
            CreditCardToken,
            id=self.kwargs["card_id"],
            user__username=self.kwargs["username"],
            active=True,
        )

    # noinspection PyUnusedLocal
    def post(self, *args, **kwargs):
        card = self.get_object()
        self.check_object_permissions(self.request, card)
        card.user.primary_card = card
        card.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


PAYMENT_PERMISSIONS = (
    OrderBuyerPermission,
    EscrowPermission,
    DeliverableStatusPermission(
        PAYMENT_PENDING,
        error_message="This has already been paid for, or is not ready for payment. "
        "Please refresh the page or contact support.",
    ),
)


class InvoicePayment(GenericAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [
        InvoiceStatus(OPEN),
        Or(
            And(
                StaffPower("table_seller"),
                InvoiceType(SALE, TIPPING),
            ),
            IsSuperuser,
        ),
    ]

    @lru_cache()
    def get_object(self):
        invoice = get_object_or_404(Invoice, id=self.kwargs["invoice"])
        self.check_object_permissions(self.request, invoice)
        return invoice

    # noinspection PyUnusedLocal
    def post(self, *args, **kwargs):
        invoice = self.get_object()
        attempt = self.get_serializer(
            data=self.request.data, context=self.get_serializer_context()
        )
        attempt.is_valid(raise_exception=True)
        attempt = attempt.validated_data
        try:
            invoice_post_payment(
                invoice,
                context={
                    "amount": attempt["amount"],
                    "successful": True,
                    "requesting_user": self.request.user,
                    "attempt": attempt,
                },
            )
        except AssertionError as err:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"detail": str(err)}
            )
        data = InvoiceSerializer(
            instance=invoice, context=self.get_serializer_context()
        ).data
        return Response(data=data)


class AccountBalance(RetrieveAPIView):
    permission_classes = [
        IsRegistered,
        Or(ObjectControls, StaffPower("view_financials")),
    ]
    serializer_class = AccountBalanceSerializer

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(self.request, user)
        return user


class ProductSearch(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        search_serializer = SearchQuerySerializer(data=self.request.GET)
        search_serializer.is_valid(raise_exception=True)
        query = search_serializer.validated_data.get("q", "")
        max_price = search_serializer.validated_data.get("max_price", None)
        min_price = search_serializer.validated_data.get("min_price", None)
        max_turnaround = search_serializer.validated_data.get("max_turnaround", None)
        shield_only = search_serializer.validated_data.get("shield_only", False)
        by_rating = search_serializer.validated_data.get("rating", False)
        featured = search_serializer.validated_data.get("featured", False)
        lgbt = search_serializer.validated_data.get("lgbt", False)
        artists_of_color = search_serializer.validated_data.get(
            "artists_of_color", False
        )
        content_rating = search_serializer.validated_data.get(
            "minimum_content_rating", 0
        )
        watchlist_only = False
        if self.request.user.is_authenticated:
            watchlist_only = search_serializer.validated_data.get("watch_list")

        # If staffer, allow search on behalf of user.
        if staff_power(self.request.user, "view_as"):
            user = get_object_or_404(
                User, username=self.request.GET.get("user", self.request.user.username)
            )
        else:
            user = self.request.user
        products = available_products(user, query=query, ordering=False)
        if max_price:
            if shield_only:
                products = products.filter(shield_price__lte=max_price)
            else:
                products = products.filter(starting_price__lte=max_price)
        if min_price:
            if shield_only:
                products = products.filter(shield_price__gte=min_price)
            else:
                products = products.filter(starting_price__gte=min_price)
        if max_turnaround:
            products = products.filter(expected_turnaround__lte=max_turnaround)
        if watchlist_only:
            products = products.filter(user__in=user.watching.all())
        if shield_only:
            products = products.exclude(starting_price=0).filter(
                Q(escrow_enabled=True)
                | Q(escrow_enabled=False, escrow_upgradable=True),
            )
        if featured:
            products = products.filter(Q(featured=True) | Q(user__featured=True))
        if artists_of_color:
            products = products.filter(user__artist_profile__artist_of_color=True)
        if lgbt:
            products = products.filter(user__artist_profile__lgbt=True)
        if content_rating:
            products = products.filter(max_rating__gte=content_rating)
        if by_rating:
            products = products.order_by(
                F("user__stars").desc(nulls_last=True), "-edited_on", "id"
            ).distinct()
        else:
            products = products.order_by("-edited_on", "id").distinct("edited_on", "id")
        return products.select_related("user").prefetch_related("tags")


class SetPlan(GenericAPIView):
    permission_classes = [Or(ObjectControls, StaffPower("administrate_users"))]

    def get_object(self) -> Or:
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(self.request, user)
        return user

    def post(self, *args, **kwargs):
        user = self.get_object()
        serializer = SetServiceSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        service_plan = get_object_or_404(
            ServicePlan, hidden=False, name=serializer.validated_data["service"]
        )
        if service_plan.monthly_charge and not service_plan == user.service_plan:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "service": [
                        "This endpoint may not be used for plans with monthly charges "
                        "unless it is the plan you are already on (which would induce "
                        "no charge).",
                    ]
                },
            )
        next_service_plan = service_plan
        if (
            user.service_plan.monthly_charge
            and user.service_plan_paid_through >= timezone.now().date()
        ):
            service_plan = user.service_plan
            target_date = user.service_plan_paid_through
        else:
            target_date = timezone.now().date() + relativedelta(months=1)
        set_service_plan(
            user, service_plan, next_plan=next_service_plan, target_date=target_date
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class PersonalProductSearch(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsRegistered]

    def get_queryset(self):
        search_serializer = SearchQuerySerializer(data=self.request.GET)
        search_serializer.is_valid(raise_exception=True)
        query = search_serializer.validated_data.get("q", "")
        products = Product.objects.filter(
            user=self.request.subject, name__icontains=query, active=True
        )
        return products.select_related("user")


class AccountStatus(GenericAPIView):
    permission_classes = [
        IsRegistered,
        Or(ObjectControls, StaffPower("view_financials")),
    ]
    serializer_class = TransactionRecordSerializer

    def get(self, request, *args, **kwargs):
        self.check_object_permissions(self.request, request.subject)
        query = AccountQuerySerializer(data=request.GET)
        query.is_valid(raise_exception=True)
        account = query.validated_data["account"]
        return Response(
            status=status.HTTP_200_OK,
            data={
                "available": float(account_balance(request.subject, account)),
                "posted": float(account_balance(request.subject, account, POSTED_ONLY)),
                "pending": float(account_balance(request.subject, account, PENDING)),
            },
        )


class AccountHistory(ListAPIView):
    permission_classes = [
        IsRegistered,
        Or(ObjectControls, StaffPower("view_financials")),
    ]
    serializer_class = TransactionRecordSerializer

    def get_queryset(self):
        query = AccountQuerySerializer(data=self.request.GET)
        query.is_valid(raise_exception=True)
        account = query.validated_data["account"]
        return (
            TransactionRecord.objects.filter(
                Q(payer=self.request.subject, source=account)
                | Q(payee=self.request.subject, destination=account),
            )
            .exclude(
                Q(payee=self.request.subject, destination=account, status=FAILURE),
            )
            .annotate(
                pending=Case(
                    When(status=PENDING, then=0), default=1, output_field=IntegerField()
                )
            )
            .order_by("pending", "-finalized_on", "-created_on")
        )

    def get(self, request, *args, **kwargs):
        self.check_object_permissions(self.request, self.request.subject)
        return super().get(request, *args, **kwargs)


class NewProducts(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = []

    def get_queryset(self):
        return (
            available_products(self.request.user, ordering=False)
            .order_by("-id")
            .distinct("id")
        )


class WhoIsOpen(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsRegistered]

    def get_queryset(self):
        return (
            available_products(self.request.user, ordering=False)
            .filter(user__in=self.request.user.watching.all())
            .distinct("id")
            .order_by("id", "user")
        )


class SalesStats(RetrieveAPIView):
    permission_classes = [
        IsRegistered,
        Or(
            ObjectControls,
            StaffPower("view_financials"),
            StaffPower("table_seller"),
            StaffPower("handle_disputes"),
        ),
    ]
    serializer_class = SalesStatsSerializer

    def get_object(self):
        profile = get_object_or_404(
            ArtistProfile,
            user__username=self.kwargs["username"],
        )
        self.check_object_permissions(self.request, profile)
        return profile


class RateBase(RetrieveUpdateAPIView):
    serializer_class = RatingSerializer
    # Override the permissions per-end.
    permission_classes = [OrderViewPermission]
    queryset = Rating.objects.all()

    def get_target(self):
        raise NotImplementedError("Override in subclass")  # pragma: no cover

    def get_rater(self):
        raise NotImplementedError("Override in subclass")  # pragma: no cover

    @lru_cache()
    def get_object(self):
        deliverable = self.get_deliverable()
        rater = self.get_rater()
        target = self.get_target()
        ratings = Rating.objects.filter(
            object_id=deliverable.id,
            content_type=ContentType.objects.get_for_model(deliverable),
            rater=rater,
            target=target,
        )
        return ratings.first() or Rating(
            object_id=deliverable.id,
            content_type=ContentType.objects.get_for_model(deliverable),
            rater=rater,
            target=target,
        )

    def get_deliverable(self):
        order = get_object_or_404(
            Deliverable,
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
        )
        self.check_object_permissions(self.request, order)
        return order


class RateBuyer(RateBase):
    permission_classes = [
        Or(And(IsSafeMethod, OrderViewPermission), And(OrderSellerPermission)),
        DeliverableStatusPermission(COMPLETED, REFUNDED),
    ]

    def get_target(self):
        return self.get_deliverable().order.buyer

    def get_rater(self):
        return self.get_deliverable().order.seller


class RateSeller(RateBase):
    permission_classes = [
        Or(
            And(IsSafeMethod, OrderViewPermission),
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
        user = get_object_or_404(User, username=self.kwargs["username"])
        return user.ratings.all().order_by("-created_on")


class PricingInfo(APIView):
    # noinspection PyMethodMayBeStatic
    def get(self, _request):
        return Response(
            status=status.HTTP_200_OK,
            data=pricing_spec(),
        )


class CancelPremium(APIView):
    permission_classes = [
        IsRegistered,
        Or(ObjectControls, StaffPower("administrate_users")),
    ]

    def post(self, request, *args, **kwargs):
        self.check_permissions(request)
        request.subject.landscape_enabled = False
        request.subject.save()
        return Response(
            status=status.HTTP_200_OK,
            data=UserSerializer(
                context={"request": request}, instance=self.request.subject
            ).data,
        )


class StorePreview(BasePreview):
    def context(self, username):
        user = get_object_or_404(User, username=username)
        count_hit(self.request, user)
        avatar_url = user.avatar_url
        if avatar_url.startswith("/"):
            avatar_url = make_url(avatar_url)
        return {
            "title": f"{username}'s store",
            "description": demark(user.artist_profile.commission_info),
            "image_links": [
                make_url(product.preview_link)
                # product.preview_link should always be true in production but may be
                # None in debugging development since we don't have all the uploads
                # locally when running off a copy of the DB.
                for product in user_products(username, self.request.user)[:24]
                if product.preview_link
            ]
            + [avatar_url],
        }

    @method_decorator(xframe_options_exempt)
    def get(self, request, *args, **kwargs):
        return super(StorePreview, self).get(request, *args, **kwargs)


class ProductPreview(BasePreview):
    def context(self, username, product_id):
        product = get_object_or_404(Product, id=product_id, active=True, hidden=False)
        hit_count = HitCount.objects.get_for_object(product)
        HitCountMixin.hit_count(self.request, hit_count)
        image = preview_rating(self.request, product.rating, product.preview_link)
        data = {
            "title": demark(product.name),
            "description": product.preview_description,
            "image_links": [
                preview_rating(self.request, sample.rating, sample.preview_link)
                for sample in product.samples.filter(private=False)
            ],
        }
        if image:
            data["image_links"].insert(0, image)
        return data


class PopulateCart(ProductPreview):
    def context(self, username, product_id):
        data = super().context(username, product_id)
        cart = cart_for_request(self.request, create=False)
        data["cart"] = (
            JSONRenderer()
            .render(ShoppingCartSerializer(instance=cart).data)
            .decode("utf-8")
        )
        return data


class CommissionStatusImage(View):
    # noinspection PyMethodMayBeStatic
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        if user.artist_profile.commissions_disabled:
            return serve(
                request,
                "/images/commissions-closed.png",
                document_root=settings.STATIC_ROOT,
            )
        else:
            return serve(
                request,
                "/images/commissions-open.png",
                document_root=settings.STATIC_ROOT,
            )


# TODO: Eliminate this. Should be able to do it with a patch request instead.
class FeatureProduct(APIView):
    permission_classes = [StaffPower("moderate_content")]

    # noinspection PyMethodMayBeStatic
    def post(self, request, username, product):
        product = get_object_or_404(Product, id=product, user__username=username)
        product.featured = not product.featured
        product.save()
        return Response(
            status=status.HTTP_200_OK,
            data=ProductSerializer(instance=product, context={"request": request}).data,
        )


class FeaturedProducts(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return (
            available_products(self.request.user, ordering=False)
            .filter(Q(featured=True) | Q(user__featured=True))
            .order_by("?")
            .distinct()
        )


class RandomTopSeller(RetrieveAPIView):
    def get_object(self):
        return User.objects.filter(featured=True).order_by("?").first()

    def get(self, request):
        context = self.get_serializer_context()
        user = self.get_object()
        if not user:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"detail": "No top sellers currently calculated."},
            )
        user_data = UserInfoSerializer(context=context, instance=user).data
        user_data["products"] = ProductSerializer(
            instance=available_products(self.request.user, ordering=False).filter(
                user=user
            )[:3],
            context=context,
            many=True,
        ).data
        user_data["submissions"] = SubmissionSerializer(
            instance=available_submissions(request, self.request.user)
            .filter(owner=user)
            .order_by("-display_position")[:5],
            context=context,
            many=True,
        ).data
        return Response(data=user_data)


class LowPriceProducts(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return (
            available_products(self.request.user, ordering=False)
            .filter(
                starting_price__lte=Decimal("30"),
            )
            .exclude(featured=True)
            .order_by("?")
        )


class HighlyRatedProducts(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return (
            available_products(self.request.user, ordering=False)
            .filter(user__stars__gte=4.5)
            .exclude(featured=True)
            .order_by("?")
        )


class LgbtProducts(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return (
            available_products(self.request.user, ordering=False)
            .filter(user__artist_profile__lgbt=True)
            .order_by("?")
        )


class ArtistsOfColor(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return (
            available_products(self.request.user, ordering=False)
            .filter(user__artist_profile__artist_of_color=True)
            .order_by("?")
        )


class NewArtistProducts(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        # Can't directly do order_by on this QS because the ORM breaks grouping by
        # placing it before the annotation.
        return (
            available_products(self.request.user, ordering=False)
            .filter(
                id__in=Product.objects.all()
                .annotate(
                    completed_orders=Count(
                        "user__sales",
                        filter=Q(user__sales__deliverables__status=COMPLETED),
                    )
                )
                .filter(completed_orders=0)
            )
            .order_by("?")
        )


class RandomProducts(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return (
            available_products(self.request.user, ordering=False)
            .filter(featured=False)
            .order_by("?")
        )


def get_order_facts(product: Optional[Product], serializer, seller: User):
    # Helper function for seller-initiated invoices
    facts = {
        "table_order": False,
        "hold": serializer.validated_data.get("hold", True),
        "rating": serializer.validated_data.get("rating", 0),
        "cascade_fees": serializer.validated_data.get("cascade_fees", False),
        "created_by": seller,
    }
    completed = serializer.validated_data.get("completed")
    if completed or not facts["hold"]:
        facts["commission_info"] = note_for_text(seller.artist_profile.commission_info)
    if completed:
        raw_task_weight = 0
        raw_expected_turnaround = 0
        raw_revisions = 0
    else:
        raw_task_weight = serializer.validated_data.get("task_weight", 1)
        raw_expected_turnaround = serializer.validated_data.get(
            "expected_turnaround", 5
        )
        raw_revisions = serializer.validated_data.get("revisions", 0)
    if product:
        facts["price"] = product.base_price
        facts["adjustment"] = (
            Money(serializer.validated_data["price"], "USD")
            - product.get_starting_price()
        )
        facts["task_weight"] = product.task_weight
        facts["adjustment_task_weight"] = raw_task_weight - product.task_weight
        facts["adjustment_expected_turnaround"] = (
            raw_expected_turnaround - product.expected_turnaround
        )
        facts["expected_turnaround"] = product.expected_turnaround
        facts["revisions"] = product.revisions
        facts["adjustment_revisions"] = raw_revisions - product.revisions
        facts["table_order"] = product.table_product
    else:
        facts["price"] = Money(serializer.validated_data.get("price", "50.00"), "USD")
        facts["task_weight"] = raw_task_weight
        facts["expected_turnaround"] = raw_expected_turnaround
        facts["revisions"] = raw_revisions
        facts["adjustment_task_weight"] = 0
        facts["adjustment_expected_turnaround"] = 0
        facts["adjustment_revisions"] = 0
        facts["adjustment"] = Money("0.00", "USD")
    facts["escrow_enabled"] = not (
        (seller.artist_profile.bank_account_status != IN_SUPPORTED_COUNTRY)
        and not (product and product.table_product)
    )
    if facts["hold"]:
        facts["status"] = NEW
        facts["revisions_hidden"] = True
    else:
        facts["status"] = PAYMENT_PENDING
        facts["revisions_hidden"] = True
    return facts


class CreateInvoice(GenericAPIView):
    """
    Used to create a new order from the seller's side.
    """

    permission_classes = [
        IsRegistered,
        Or(StaffPower("table_seller"), ObjectControls),
        BankingConfigured,
        PlanDeliverableAddition,
        AccountCurrentPermission,
    ]
    serializer_class = NewInvoiceSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["seller"] = self.request.subject
        return context

    def post(self, request, username):
        user = get_object_or_404(User, username=username)
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        buyer = serializer.validated_data["buyer"]
        facts = get_order_facts(None, serializer, user)

        if isinstance(buyer, str) or buyer is None:
            customer_email = buyer or ""
            buyer = None
        else:
            buyer = buyer
            customer_email = ""
        order = Order.objects.create(
            seller=user,
            buyer=buyer,
            hide_details=serializer.validated_data["hidden"],
            customer_email=customer_email,
        )
        deliverable_facts = {
            key: value
            for key, value in facts.items()
            if key
            not in (
                "price",
                "adjustment",
                "hold",
                "paid",
            )
        }
        deliverable = Deliverable.objects.create(
            name="Main",
            order=order,
            details=serializer.validated_data["details"],
            processor=STRIPE,
            **deliverable_facts,
        )
        deliverable.invoice.line_items.filter(
            type=BASE_PRICE,
        ).update(amount=facts["price"])
        # Trigger all signals/hooks to update calculations.
        deliverable.save()
        for asset in serializer.validated_data.get("references", []):
            reference = Reference.objects.create(
                file=asset, owner=user or self.request.user
            )
            reference.deliverables.add(deliverable)
        notify(ORDER_UPDATE, deliverable, unique=True, mark_unread=True)
        return Response(
            data=DeliverableSerializer(
                instance=deliverable, context=self.get_serializer_context()
            ).data
        )


class ProductRecommendations(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [
        Or(
            And(IsSafeMethod, OrderPlacePermission),
            Or(ObjectControls, StaffPower("view_as")),
        )
    ]

    @lru_cache()
    def get_object(self):
        return get_object_or_404(Product, id=self.kwargs["product"])

    def get_queryset(self):
        product = self.get_object()
        qs = available_products(self.request.user, ordering=False).exclude(
            id=product.id
        )
        qs = qs.annotate(n=Count("pk"))
        qs = qs.filter(tags__in=product.tags.all())
        qs = qs.annotate(
            same_artist=Case(
                When(user=product.user, then=1),
                default=0,
                output_field=IntegerField(),
            ),
        )
        qs = qs.order_by(
            "-n", "same_artist", "user__stars", "edited_on", "id"
        ).distinct()
        return qs


class DeliverableCharacterList(ListAPIView):
    permission_classes = [OrderViewPermission]
    pagination_class = None
    serializer_class = DeliverableCharacterTagSerializer

    def get_queryset(self) -> QuerySet:
        return Deliverable.characters.through.objects.filter(
            deliverable=self.get_object()
        )

    @lru_cache()
    def get_object(self) -> Deliverable:
        deliverable = get_object_or_404(
            Deliverable,
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
        )
        self.check_object_permissions(self.request, deliverable)
        return deliverable


class DeliverableOutputs(ListCreateAPIView):
    permission_classes = [
        OrderViewPermission,
        Or(
            DeliverableStatusPermission(COMPLETED),
            OrderSellerPermission,
        ),
        Or(
            IsRegistered,
            IsSafeMethod,
        ),
    ]
    pagination_class = None
    serializer_class = SubmissionSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SubmissionFromOrderSerializer
        return SubmissionSerializer

    def get_queryset(self) -> QuerySet:
        return self.get_object().outputs.all()

    @lru_cache()
    def get_object(self) -> Deliverable:
        order = get_object_or_404(
            Deliverable,
            order_id=self.kwargs["order_id"],
            id=self.kwargs["deliverable_id"],
        )
        self.check_object_permissions(self.request, order)
        return order

    def post(self, request, *args, **kwargs):
        deliverable = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        revision = serializer.validated_data.get("revision")
        last_revision = deliverable.revision_set.all().last()
        if not last_revision:
            return Response(
                data={
                    "detail": "You can not create a submission from an order with no "
                    "revisions."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not revision:
            if not deliverable.status == COMPLETED:
                return Response(
                    data={
                        "detail": "You must specify a specific revision if the order "
                        "is not completed."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            revision = last_revision
        else:
            if not deliverable.revision_set.filter(id=revision.id):
                raise ValidationError(
                    {
                        "revision": "The provided revision does not belong to this "
                        "deliverable."
                    }
                )
        if Submission.objects.filter(
            deliverable=deliverable, revision=revision, owner=request.user
        ).exists():
            return Response(
                data={
                    "detail": "You have already created a submission with this "
                    "deliverable and revision."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save(
            owner=request.user,
            deliverable=deliverable,
            rating=deliverable.rating,
            file=revision.file,
            revision=revision,
        )
        instance.characters.set(deliverable.characters.all())
        hidden = (
            deliverable.order.hide_details
            and instance.owner != deliverable.order.seller
        )
        ArtistTag(
            submission=instance, user=deliverable.order.seller, hidden=hidden
        ).save()
        is_final = last_revision == revision
        for character in instance.characters.all():
            if (
                request.user == character.user
                and not character.primary_submission
                and is_final
            ):
                character.primary_submission = instance
                character.save()
        if (
            deliverable.product
            and (request.user == deliverable.order.seller)
            and is_final
        ):
            deliverable.product.samples.add(instance)
        if instance.owner == deliverable.order.seller:
            # Hide the customer's copy if we make one of our own.
            submissions = Submission.objects.filter(
                deliverable=deliverable, revision=revision
            ).exclude(id=instance.id)
            ArtistTag.objects.filter(
                submission__in=submissions, user=deliverable.order.seller
            ).update(hidden=True)
        elif (
            Submission.objects.filter(deliverable=deliverable, revision=revision)
            .exclude(id=instance.id)
            .exists()
        ):
            # If we are not the artist, and there is already a copy, hide this one.
            ArtistTag.objects.filter(
                submission=instance, user=deliverable.order.seller
            ).update(hidden=True)
        return Response(
            data=SubmissionSerializer(
                instance=instance, context=self.get_serializer_context()
            ).data,
            status=status.HTTP_201_CREATED,
        )


class OrderAuth(GenericAPIView):
    serializer_class = OrderAuthSerializer

    def user_info(self, user):
        serializer = UserSerializer(
            instance=user, context=self.get_serializer_context()
        )
        data = serializer.data
        if not user.is_registered:
            patch_data = empty_user(
                user=self.request.user,
                session=self.request.session,
                ip=self.request.ip,
            )
            del patch_data["username"]
            data = {**data, **patch_data}
        return data

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invalid = (
            "Invalid claim token. It may have expired. A new link will be sent to your "
            "email, if this order can be claimed."
        )
        order = (
            Order.objects.filter(
                id=serializer.validated_data["id"],
            )
            .filter(Q(buyer__guest=True) | Q(buyer__isnull=True))
            .first()
        )
        if not order:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={"detail": invalid},
            )
        if request.user.is_authenticated and (
            order.buyer and (request.user.username == order.buyer.username)
        ):
            # Ignore the claim token since we're already the required user, and just
            # return success.
            return Response(status=status.HTTP_200_OK, data=self.user_info(order.buyer))
        if order.claim_token != serializer.validated_data["claim_token"]:
            target_email = (
                order.buyer and order.buyer.guest_email
            ) or order.customer_email
            send_transaction_email(
                f"Claim Link for order #{order.id}.",
                "new_claim_link.html",
                target_email,
                {"order": order, "claim_token": get_claim_token(order)},
            )
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={"detail": invalid},
            )
        if serializer.validated_data["chown"] and not request.user.is_registered:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "detail": "You must be logged in to claim this order for an "
                    "existing account. You may wish to continue as a "
                    "guest instead?"
                },
            )
        if serializer.validated_data["chown"]:
            old_buyer = order.buyer
            if order.seller == request.user:
                return Response(
                    status=status.HTTP_403_FORBIDDEN,
                    data={"detail": "You may not claim your own order!"},
                )
            transfer_order(order, old_buyer, request.user)
            return Response(
                status=status.HTTP_200_OK, data=self.user_info(request.user)
            )

        ensure_buyer(order)
        login(request, order.buyer)
        trigger_reconnect(self.request, include_current=True)
        order.claim_token = uuid4()
        order.save()
        order.buyer.verified_email = True
        order.buyer.save()
        return Response(status=status.HTTP_200_OK, data=self.user_info(order.buyer))


class Broadcast(CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [
        IsRegistered,
        Or(ObjectControls, StaffPower("handle_disputes")),
    ]

    def get_object(self):
        return self.request.subject

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["broadcast_mode"] = True
        return context

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except Http404:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"detail": "You have no matching orders to broadcast to."},
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        self.check_object_permissions(self.request, self.get_object())
        checks = []
        if serializer.validated_data["include_active"]:
            checks.extend(list(WEIGHTED_STATUSES) + list((REVIEW, DISPUTED, NEW)))
        if serializer.validated_data["include_waitlist"]:
            checks.append(WAITING)
        if not checks:
            raise ValidationError(
                {
                    "detail": "You must select at least one category of orders to broadcast to."
                }
            )
        deliverables = (
            Deliverable.objects.filter(
                status__in=checks,
                order__seller=self.request.subject,
            )
            .order_by("order_id")
            .distinct("order_id")
        )
        comment = None
        for deliverable in deliverables:
            comment = create_comment(deliverable, serializer, self.request.user)
            serializer.instance = Comment()
        if comment is None:
            raise Http404


class InvoiceDetail(RetrieveUpdateAPIView):
    permission_classes = [
        Or(BillTo, IssuedBy, StaffPower("table_seller")),
        Or(IsSafeMethod, Or(StaffPower("table_seller"), StaffPower("view_financials"))),
    ]
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()

    def get_object(self):
        invoice = get_object_or_404(Invoice, id=self.kwargs["invoice"])
        self.check_object_permissions(self.request, invoice)
        return invoice


class TableProducts(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [StaffPower("table_seller")]
    pagination_class = None

    def get_queryset(self) -> QuerySet:
        return Product.objects.filter(
            table_product=True, hidden=False, active=True
        ).order_by("user")


class TableOrders(ListAPIView):
    serializer_class = OrderPreviewSerializer
    permission_classes = [StaffPower("table_seller")]
    pagination_class = None

    def get_queryset(self) -> QuerySet:
        qs = Order.objects.filter(
            deliverables__table_order=True,
        )
        qs = qs.exclude(
            Q(deliverables__status__in=[CANCELLED, REFUNDED, COMPLETED])
            & Q(created_on__lte=timezone.now() - relativedelta(days=60)),
        )
        qs = qs.distinct().order_by("seller", "-created_on")
        return qs


class CreateVendorInvoice(GenericAPIView):
    """
    Creates an 'outvoice' for the platform to send money to a user.
    """

    permission_classes = [IsSuperuser]
    serializer_class = InvoiceSerializer

    @transaction.atomic
    def post(self, request):
        self.check_permissions(request)
        serializer = VendorInvoiceCreationSerializer(
            context=self.get_serializer_context(), data=request.data
        )
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, id=serializer.validated_data["issued_by_id"])
        invoice = Invoice.objects.create(
            bill_to=None,
            issued_by=user,
            status=DRAFT,
            manually_created=True,
            type=VENDOR,
        )
        invoice.line_items.create(
            destination_user=user,
            destination_account=HOLDINGS,
            category=VENDOR_PAYMENT,
            type=BASE_PRICE,
            priority=PRIORITY_MAP[BASE_PRICE],
            cascade_under=CASCADE_UNDER_MAP[BASE_PRICE],
            amount=Money("0.00", settings.DEFAULT_CURRENCY),
        )
        return Response(
            data=self.get_serializer(
                context=self.get_serializer_context(), instance=invoice
            ).data,
            status=status.HTTP_201_CREATED,
        )


class CreateAnonymousInvoice(GenericAPIView):
    """
    Creates an invoice with sales tax applied, and returns it for filling out.
    """

    permission_classes = [StaffPower("table_seller")]
    serializer_class = InvoiceSerializer

    @transaction.atomic
    def post(self, request):
        invoice = Invoice.objects.create(
            bill_to=get_anonymous_user(),
            status=DRAFT,
            manually_created=True,
            type=SALE,
        )
        invoice.line_items.create(
            percentage=settings.TABLE_TAX,
            cascade_percentage=True,
            cascade_amount=True,
            destination_user=None,
            destination_account=MONEY_HOLE,
            category=TAXES,
            type=TAX,
            priority=PRIORITY_MAP[TAX],
            cascade_under=CASCADE_UNDER_MAP[TAX],
        )
        return Response(
            data=self.get_serializer(
                context=self.get_serializer_context(), instance=invoice
            ).data,
            status=status.HTTP_201_CREATED,
        )


class VendorInvoices(ListAPIView):
    permission_classes = [StaffPower("view_financials")]
    serializer_class = InvoiceSerializer

    def get_queryset(self) -> QuerySet:
        return (
            Invoice.objects.filter(
                targets__isnull=True,
                type=VENDOR,
                record_only=False,
            )
            .all()
            .order_by("-created_on")
        )


class TableInvoices(ListAPIView):
    permission_classes = [StaffPower("table_seller")]
    serializer_class = InvoiceSerializer

    def get_queryset(self) -> QuerySet:
        return (
            Invoice.objects.filter(
                targets__isnull=True,
                type=SALE,
                record_only=False,
                manually_created=True,
            )
            .all()
            .order_by("-created_on")
        )


class FinalizeInvoice(GenericAPIView):
    permission_classes = [
        Or(
            And(StaffPower("table_seller"), InvoiceStatus(DRAFT)),
            And(BillTo, InvoiceStatus(DRAFT), InvoiceType(TIPPING)),
        )
    ]
    serializer_class = InvoiceSerializer

    def get_object(self):
        invoice = get_object_or_404(Invoice, id=self.kwargs.get("invoice"))
        self.check_object_permissions(self.request, invoice)
        return invoice

    def post(self, *args, **kwargs):
        invoice = self.get_object()
        invoice.status = OPEN
        invoice.save()
        return Response(data=self.get_serializer(instance=invoice).data)


class VoidInvoice(GenericAPIView):
    permission_classes = [
        Or(
            And(StaffPower("table_seller"), InvoiceStatus(OPEN, DRAFT)),
            And(BillTo, InvoiceStatus(OPEN, DRAFT), InvoiceType(TIPPING)),
        ),
    ]
    serializer_class = InvoiceSerializer

    def get_object(self):
        invoice = get_object_or_404(Invoice, id=self.kwargs.get("invoice"))
        self.check_object_permissions(self.request, invoice)
        return invoice

    def post(self, *args, **kwargs):
        invoice = self.get_object()
        invoice.status = VOID
        invoice.save()
        return Response(data=self.get_serializer(instance=invoice).data)


class Plans(ListAPIView):
    permission_classes = []
    serializer_class = ServicePlanSerializer
    pagination_class = None

    def get_queryset(self) -> QuerySet:
        return ServicePlan.objects.filter(hidden=False).order_by("sort_value")


class UserInvoices(ListAPIView):
    permission_classes = [Or(ObjectControls, StaffPower("view_financials"))]
    serializer_class = InvoiceSerializer

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs.get("username"))
        self.check_object_permissions(self.request, user)
        return user

    def get_queryset(self):
        user = self.get_object()
        return user.invoices_billed_to.exclude(Q(type=SUBSCRIPTION, status=OPEN))


class InvoiceTransactions(ListAPIView):
    permission_classes = [Or(StaffPower("view_financials"), StaffPower("table_seller"))]
    serializer_class = TransactionRecordSerializer

    def get_queryset(self):
        invoice = get_object_or_404(Invoice, id=self.kwargs.get("invoice"))
        return TransactionRecord.objects.filter(targets=ref_for_instance(invoice))


class IssueTipInvoice(GenericAPIView):
    permission_classes = [
        OrderBuyerPermission,
        DeliverableStatusPermission(COMPLETED),
    ]

    def get_object(self):
        deliverable = get_object_or_404(
            Deliverable,
            id=self.kwargs["deliverable_id"],
            order_id=self.kwargs["order_id"],
        )
        self.check_object_permissions(self.request, deliverable)
        return deliverable

    def post(self, *args, **kwargs):
        deliverable = self.get_object()
        with transaction.atomic():
            invoice = initialize_tip_invoice(deliverable)
        if not invoice:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "detail": "Cannot create a tipping invoice for this deliverable."
                },
            )
        return Response(
            data=InvoiceSerializer(
                instance=invoice, context=self.get_serializer_context()
            ).data,
            status=status.HTTP_201_CREATED,
        )


class StoreShift(PositionShift):
    serializer_class = ProductSerializer
    permission_classes = [Or(ObjectControls, StaffPower("moderate_content"))]

    def get_object(self) -> Or:
        return get_object_or_404(Product, id=self.kwargs["product"])


class QueueListing(View):
    def get(self, request, username):
        user = get_object_or_404(
            ArtistProfile, user__username=username, public_queue=True
        ).user
        orders = (
            Order.objects.filter(
                seller=user,
                deliverables__status__in=[
                    QUEUED,
                    IN_PROGRESS,
                    REVIEW,
                    DISPUTED,
                ],
            )
            .distinct()
            .order_by("created_on")
        )
        orders = OrderPreviewSerializer(
            instance=orders, many=True, context={"request": request, "public": True}
        ).data
        return render(
            request,
            "sales/queue_listing.html",
            context={"orders": orders, "user": user},
        )


class PaypalSettings(RetrieveUpdateDestroyAPIView):
    permission_classes = [
        IsRegistered,
        Or(ObjectControls, StaffPower("administrate_users")),
    ]
    queryset = PaypalConfig.objects.all()

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(self.request, user)
        if self.request.method == "POST":
            return user
        return get_object_or_404(PaypalConfig, user=user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return NewPaypalConfigSerializer
        else:
            return PaypalConfigSerializer

    def delete(self, request, **_kwargs):
        config = self.get_object()
        if (
            Deliverable.objects.filter(
                order__seller=config.user,
                status__in=WORK_IN_PROGRESS_STATUSES,
            )
            .exclude(invoice__paypal_token="")
            .exists()
        ):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "detail": "You must close out all orders currently managed "
                    "by PayPal to remove this integration.",
                },
            )
        delete_webhooks(config)
        config.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, **_kwargs):
        user = self.get_object()
        try:
            user.paypal_config
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"detail": "PayPal already configured."},
            )
        except PaypalConfig.DoesNotExist:
            pass
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        config = PaypalConfig(
            id=gen_shortcode(),
            user=user,
            key=data["key"],
            secret=data["secret"],
        )
        with paypal_api(user, config=config) as paypal:
            try:
                resp = paypal.get("v1/invoicing/templates/")
            except MissingTokenError:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        "key": ["Login failed. Check key."],
                        "secret": ["Login failed. Check secret."],
                    },
                )
            template = None
            for entry in resp.json()["templates"]:
                if entry["name"] == "Amount" and entry["currency_code"] == "USD":
                    template = entry
                    break
            if template is not None:
                config.template_id = template["template_id"]
                config.active = True
            webhook_path = reverse(
                "sales:paypal_webhooks",
                kwargs={"config_id": config.id},
            )
            resp = paypal.post(
                "v1/notifications/webhooks",
                {
                    "url": f"https://{settings.WEBHOOKS_DOMAIN}{webhook_path}",
                    "event_types": [
                        {"name": key} for key in PAYPAL_WEBHOOK_ROUTES.keys()
                    ],
                },
            )
            config.webhook_id = resp.json()["id"]
            config.save()
            # Force trigger of refresh of user serializer over websocket
            config.user.save(update_fields=[])
        return Response(
            status=status.HTTP_201_CREATED,
            data=PaypalConfigSerializer(
                instance=config,
                context=self.get_serializer_context(),
            ).data,
        )


class PaypalTemplates(GenericAPIView):
    permission_classes = [Or(ObjectControls, StaffPower("administrate_users"))]

    def get_object(self):
        config = get_object_or_404(
            PaypalConfig,
            user__username=self.kwargs.get("username"),
        )
        self.check_object_permissions(self.request, config)
        return config

    def get(self, request, *args, **kwargs):
        with paypal_api(config=self.get_object()) as paypal:
            resp = paypal.get("v2/invoicing/templates?page_size=100")
        templates = [
            {"name": template["name"], "id": template["id"]}
            for template in resp.json().get("templates", [])
            if template["template_info"]["detail"]["currency_code"] == "USD"
        ]
        return Response(data=templates)


class UpdateCart(UpdateAPIView):
    permission_classes = [SessionKeySet]
    serializer_class = ShoppingCartSerializer
    queryset = ShoppingCart.objects.all()

    def get_object(self):
        return cart_for_request(self.request, create=True)
