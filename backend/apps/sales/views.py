from uuid import uuid4

from authorize import AuthorizeResponseError
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.db.models import When, F, Case, BooleanField, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

# Create your views here.
from math import ceil

from django.utils.datetime_safe import date
from moneyed import Money, Decimal
# BDay is business day, not birthday.
from pandas.tseries.offsets import BDay
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, RetrieveAPIView, \
    GenericAPIView, ListAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.lib.models import DISPUTE, REFUND, COMMENT, Subscription, ORDER_UPDATE, SALE_UPDATE, REVISION_UPLOADED, \
    CHAR_TRANSFER, NEW_PRODUCT, STREAMING
from apps.lib.permissions import ObjectStatus, IsStaff, IsSafeMethod, Any
from apps.lib.serializers import CommentSerializer
from apps.lib.utils import notify, recall_notification, subscribe, add_tags, demark
from apps.lib.views import BaseTagView, BasePreview
from apps.profiles.models import User, ImageAsset, Character
from apps.profiles.permissions import ObjectControls, UserControls
from apps.profiles.serializers import ImageAssetSerializer, UserSerializer
from apps.sales.dwolla import add_bank_account, initiate_withdraw, perform_transfer, make_dwolla_account, \
    destroy_bank_account
from apps.sales.permissions import OrderViewPermission, OrderSellerPermission, OrderBuyerPermission, \
    OrderPlacePermission, EscrowPermission, EscrowDisabledPermission
from apps.sales.models import Product, Order, CreditCardToken, PaymentRecord, Revision, BankAccount, CharacterTransfer, \
    PlaceholderSale, WEIGHTED_STATUSES, Rating, OrderToken
from apps.sales.serializers import ProductSerializer, ProductNewOrderSerializer, OrderViewSerializer, CardSerializer, \
    NewCardSerializer, OrderAdjustSerializer, PaymentSerializer, RevisionSerializer, OrderStartedSerializer, \
    AccountBalanceSerializer, BankAccountSerializer, WithdrawSerializer, PaymentRecordSerializer, \
    CharacterTransferSerializer, PlaceholderSaleSerializer, PublishFinalSerializer, RatingSerializer, \
    ServicePaymentSerializer, ProductDetailSerializer, OrderTokenSerializer
from apps.sales.utils import translate_authnet_error, available_products, service_price, set_service, \
    check_charge_required, available_products_by_load, finalize_order, available_products_from_user
from apps.sales.tasks import renew


class ProductList(ListCreateAPIView):
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        if not (self.request.user.is_staff or self.request.user == user):
            raise PermissionDenied("You do not have permission to create products for that user.")
        product = serializer.save(owner=user, user=user)
        # ignore the tagging result. In the case it fails, someone's doing something pretty screwwy anyway, and it's
        # not essential for creating the character.
        add_tags(self.request, product, field_name='tags')
        if not product.hidden:
            notify(NEW_PRODUCT, user, data={'product': product.id}, unique_data=True)
        return product

    def get_queryset(self):
        username = self.kwargs['username']
        qs = Product.objects.filter(user__username__iexact=self.kwargs['username'], active=True)
        if not (self.request.user.username.lower() == username.lower() or self.request.user.is_staff):
            qs = qs.exclude(hidden=True)
            qs = qs.exclude(task_weight__gt=F('user__max_load') - F('user__load'))
            qs = qs.exclude(Q(parallel__gte=F('max_parallel')) & ~Q(max_parallel=0))
        qs = qs.order_by('created_on')
        return qs


class ProductManager(RetrieveUpdateDestroyAPIView):
    serializer_class = ProductDetailSerializer
    permission_classes = [Any(IsSafeMethod, ObjectControls)]

    def get_object(self):
        product = get_object_or_404(
            Product, user__username=self.kwargs['username'], id=self.kwargs['product'], active=True
        )
        self.check_object_permissions(self.request, product)
        return product


class ProductOrderTokens(ListCreateAPIView):
    serializer_class = OrderTokenSerializer
    permission_classes = [ObjectControls]

    def get_queryset(self):
        product = get_object_or_404(
            Product, user__username=self.kwargs['username'], id=self.kwargs['product'], active=True
        )
        self.check_object_permissions(self.request, product)
        return product.tokens.filter(expires_on__gte=timezone.now())

    def perform_create(self, serializer):
        product = get_object_or_404(
            Product, user__username=self.kwargs['username'], id=self.kwargs['product'], active=True
        )
        self.check_object_permissions(self.request, product)
        return serializer.save(product=product)


class OrderTokenManager(DestroyAPIView):
    serializer_class = OrderTokenSerializer
    permission_classes = [ObjectControls]

    def get_object(self):
        product = get_object_or_404(
            Product, user__username=self.kwargs['username'], id=self.kwargs['product'], active=True
        )
        self.check_object_permissions(self.request, product)
        return get_object_or_404(OrderToken, product=product, id=self.kwargs['order_token'])


class ProductExamples(ListAPIView):
    serializer_class = ImageAssetSerializer

    def get_queryset(self):
        product = get_object_or_404(
            Product, user__username=self.kwargs['username'], id=self.kwargs['product'], active=True
        )
        qs = ImageAsset.objects.filter(order__product=product, rating__lte=self.request.max_rating)
        if not (self.request.user == product.user or self.request.user.is_staff):
            if product.hidden:
                raise PermissionDenied('Example listings for this product are hidden.')
            qs = qs.exclude(private=True)
        return qs


class PlaceOrder(CreateAPIView):
    serializer_class = ProductNewOrderSerializer
    permission_classes = [IsAuthenticated, OrderPlacePermission]

    def get_serializer(self, instance=None, data=None, many=False, partial=False):
        return self.serializer_class(
            instance=instance, data=data, many=many, partial=partial, request=self.request,
            context=self.get_serializer_context()
        )

    def can_create(self, product, serializer):
        if self.request.user == product.user:
            return False, 'You cannot order your own products. Use a placeholder order instead.', None
        token = serializer.validated_data.get('order_token')
        token_failed = False
        if token:
            tokens = product.tokens.filter(activation_code=token, expires_on__gte=timezone.now())
            if tokens.exists():
                return True, '', tokens[0]
            else:
                token_failed = True
        if available_products_from_user(product.user).filter(id=product.id).exists():
            return True, '', None
        if token_failed:
            return False, 'The order token you provided is expired, revoked, or invalid.', None
        return False, 'This product is not available at this time.', None

    def perform_create(self, serializer):
        product = get_object_or_404(Product, id=self.kwargs['product'], active=True)
        can_order, message, token = self.can_create(product, serializer)
        if not can_order:
            raise ValidationError({'errors': [message]})
        order = serializer.save(
            product=product, buyer=self.request.user, seller=product.user, escrow_disabled=product.user.escrow_disabled
        )
        if token:
            token.delete()
        for character in order.characters.all():
            character.shared_with.add(order.seller)
        notify(SALE_UPDATE, order, unique=True, mark_unread=True)
        return order


class OrderRetrieve(RetrieveAPIView):
    permission_classes = [OrderViewPermission]
    serializer_class = OrderViewSerializer

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'])

    def put(self, request, *args, **kwargs):
        order = self.get_object()
        data = {'subscribed': request.data.get('subscribed')}
        serializer = self.get_serializer(instance=order, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class OrderAccept(UpdateAPIView):
    permission_classes = [OrderSellerPermission]
    serializer_class = OrderAdjustSerializer

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        if order.status != Order.NEW:
            self.permission_denied(self.request, "Approval can only be applied to new orders.")
        return order

    def perform_update(self, serializer):
        order = serializer.save()
        order.status = Order.PAYMENT_PENDING
        order.price = order.product.price
        order.task_weight = order.product.task_weight
        order.expected_turnaround = order.product.expected_turnaround
        order.revisions = order.product.revisions
        if order.total() <= Money('0', 'USD'):
            order.status = Order.QUEUED
            order.escrow_disabled = True
        order.save()
        data = self.serializer_class(instance=order, context=self.get_serializer_context()).data
        notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
        return Response(data)


class MarkPaid(GenericAPIView):
    permission_classes = [OrderSellerPermission, EscrowDisabledPermission]
    serializer_class = OrderViewSerializer

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'])

    def post(self, request, **_kwargs):
        order = self.get_object()
        self.check_object_permissions(request, order)
        if order.status != Order.PAYMENT_PENDING:
            return Response(
                {'error': 'You can only mark orders paid if they are waiting for payment.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = Order.QUEUED
        order.save()
        data = self.serializer_class(instance=order, context=self.get_serializer_context()).data
        notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
        return Response(data)


class OrderStart(UpdateAPIView):
    permission_classes = [OrderSellerPermission]
    serializer_class = OrderStartedSerializer

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        if order.status not in (Order.QUEUED, Order.IN_PROGRESS):
            raise PermissionDenied('You can only start orders that are queued.')
        return order

    def perform_update(self, serializer):
        order = serializer.save(status=Order.IN_PROGRESS, started_on=timezone.now())
        notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
        if not order.private and order.stream_link:
            notify(
                STREAMING, order.seller,
                data={'order': order.id}, unique_data=True,
                exclude=[order.buyer, order.seller]
            )
        return Response(serializer.data)


class OrderCancel(GenericAPIView):
    permission_classes = [OrderViewPermission]
    serializer_class = OrderViewSerializer

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        if self.request.user != order.seller:
            notify(SALE_UPDATE, order, unique=True, mark_unread=True)
        if self.request.user != order.buyer:
            notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
        if order.status not in [Order.NEW, Order.PAYMENT_PENDING]:
            raise PermissionDenied(
                "You cannot cancel this order. It is either already cancelled or must be refunded instead."
            )
        return order

    def post(self, request, order_id):
        order = self.get_object()
        order.status = Order.CANCELLED
        order.save()
        data = self.serializer_class(instance=order, context=self.get_serializer_context()).data
        return Response(data)


class OrderComments(ListCreateAPIView):
    permission_classes = [OrderViewPermission]
    serializer_class = CommentSerializer

    def get_queryset(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return order.comments.all()

    def perform_create(self, serializer):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        serializer.save(
            user=self.request.user, object_id=order.id, content_type=ContentType.objects.get_for_model(order)
        )


class OrderRevisions(ListCreateAPIView):
    permission_classes = [OrderViewPermission]
    serializer_class = RevisionSerializer

    def get_queryset(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return order.revision_set.all()

    def perform_create(self, serializer):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        if order.revision_set.all().count() >= order.revisions + 1:
            raise PermissionDenied("The maximum number of revisions for this order has already been reached.")
        if not (self.request.user.is_staff or self.request.user == order.seller):
            raise PermissionDenied("You are not the seller on this order.")
        revision = serializer.save(order=order, owner=self.request.user)
        order.refresh_from_db()
        if (order.revision_set.all().count() >= order.revisions + 1) and (order.status == Order.IN_PROGRESS):
            if order.escrow_disabled:
                order.status = Order.COMPLETED
            else:
                order.status = Order.REVIEW
                order.auto_finalize_on = (timezone.now() + relativedelta(days=5)).date()
            order.save()
            notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
        else:
            notify(REVISION_UPLOADED, order, data={'revision': revision.id}, unique_data=True, mark_unread=True)
        recall_notification(STREAMING, order.seller, data={'order': order.id})
        return revision


class DeleteOrderRevision(DestroyAPIView):
    permission_classes = [OrderSellerPermission]
    serializer_class = RevisionSerializer

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        statuses = [Order.REVIEW, Order.IN_PROGRESS]
        if order.escrow_disabled:
            statuses.append(Order.COMPLETED)
        if order.status not in statuses:
            raise PermissionDenied("This order's revisions are locked.")
        revision = get_object_or_404(Revision, id=self.kwargs['revision_id'], order_id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return revision

    def perform_destroy(self, instance):
        revision_id = instance.id
        super(DeleteOrderRevision, self).perform_destroy(instance)
        order = Order.objects.get(id=self.kwargs['order_id'])
        recall_notification(REVISION_UPLOADED, order, data={'revision': revision_id}, unique_data=True)
        if order.status in [Order.REVIEW, Order.COMPLETED]:
            order.auto_finalize_on = None
            order.status = Order.IN_PROGRESS
            order.save()


class StartDispute(GenericAPIView):
    permission_classes = [OrderBuyerPermission, EscrowPermission]
    serializer_class = OrderViewSerializer

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'])

    def post(self, _request, *_args, **_kwargs):
        order = self.get_object()
        self.check_object_permissions(self.request, order)
        if order.status not in [Order.IN_PROGRESS, Order.QUEUED, Order.REVIEW]:
            raise PermissionDenied('This order is not in a disputable state.')
        if order.status in [Order.IN_PROGRESS, Order.QUEUED]:
            if order.dispute_available_on < timezone.now().date():
                raise PermissionDenied(
                    "This order is not old enough to dispute. You can dispute it on {}".format(
                        order.dispute_available_on
                    )
                )
        order.status = Order.DISPUTED
        order.disputed_on = timezone.now()
        order.save()
        notify(DISPUTE, order, unique=True, mark_unread=True)
        notify(SALE_UPDATE, order, unique=True, mark_unread=True)
        serializer = self.get_serializer()
        serializer.instance = order
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ClaimDispute(GenericAPIView):
    permission_classes = [IsStaff]
    serializer_class = OrderViewSerializer

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'])

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
            subscriber=request.user
        )
        serializer = self.get_serializer()
        serializer.instance = obj
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class OrderRefund(GenericAPIView):
    permission_classes = [OrderSellerPermission, EscrowPermission]
    serializer_class = OrderViewSerializer

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'])

    def post(self, request, *_args, **_kwargs):
        order = self.get_object()
        self.check_object_permissions(self.request, order)
        if order.status not in [Order.QUEUED, Order.IN_PROGRESS, Order.REVIEW, Order.DISPUTED]:
            raise PermissionDenied('This order is not in a refundable state.')
        if order.escrow_disabled or order.total() <= Money('0', 'USD'):
            order.status = order.REFUNDED
            notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
            if request.user != order.seller:
                notify(SALE_UPDATE, order, unique=True, mark_unread=True)
            serializer = self.get_serializer(instance=order, context=self.get_serializer_context())
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        old_transaction = PaymentRecord.objects.get(
            object_id=order.id, content_type=ContentType.objects.get_for_model(order), payer=order.buyer,
            type=PaymentRecord.SALE
        )
        old_transaction.finalized = True
        old_transaction.save()
        record = PaymentRecord.objects.get(
            status=PaymentRecord.SUCCESS,
            object_id=order.id,
            content_type=ContentType.objects.get_for_model(order),
            payer=order.buyer,
            payee=None
        )
        record = record.refund()
        if record.status == PaymentRecord.FAILURE:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': record.response_message})
        order.status = Order.REFUNDED
        order.save()
        PaymentRecord.objects.create(
            payer=order.seller,
            amount=Money(settings.REFUND_FEE, 'USD'),
            payee=None,
            source=PaymentRecord.ACCOUNT,
            txn_id=str(uuid4()),
            target=order,
            type=PaymentRecord.TRANSFER,
            status=PaymentRecord.SUCCESS,
            response_code='RfndFee',
            response_message='Artconomy Refund Fee'
        )
        notify(REFUND, order, unique=True, mark_unread=True)
        notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
        if request.user != order.seller:
            notify(SALE_UPDATE, order, unique=True, mark_unread=True)
        serializer = self.get_serializer(instance=order, context=self.get_serializer_context())
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ApproveFinal(GenericAPIView):
    permission_classes = [OrderBuyerPermission, EscrowPermission]
    serializer_class = OrderViewSerializer

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'])

    def post(self, request, *_args, **_kwargs):
        order = self.get_object()
        self.check_object_permissions(self.request, order)
        if order.status not in [Order.REVIEW, Order.DISPUTED]:
            raise PermissionDenied('This order is not in an approvable state.')
        finalize_order(order, request.user)
        return Response(
            status=status.HTTP_200_OK,
            data=OrderViewSerializer(instance=order, context=self.get_serializer_context()).data
        )


class PublishFinal(GenericAPIView):
    permission_classes = [OrderBuyerPermission]
    serializer_class = PublishFinalSerializer

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'])

    def post(self, request, *args, **kwargs):
        order = self.get_object()
        self.check_object_permissions(request, order)
        if order.outputs.exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={'errors': ['A submission for this order already exists.']}
            )
        if not order.status == Order.COMPLETED:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={'errors': ['Order not yet completed, or it is cancelled.']}
            )
        final = order.revision_set.last()
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        new_file = ContentFile(final.file.read())
        new_file.name = final.file.name
        submission = serializer.save(
            owner=order.buyer, order=order,
            rating=final.rating,
            file=new_file, private=order.private
        )
        submission.characters.add(*order.characters.all())
        submission.artists.add(order.seller)
        submission.shared_with.add(order.seller)
        # Subscribe seller to comments on resulting work.
        Subscription.objects.create(
            type=COMMENT,
            object_id=submission.id,
            content_type=ContentType.objects.get_for_model(submission),
            subscriber=order.seller
        )
        if not order.private:
            for character in order.characters.all():
                if not character.primary_asset:
                    character.primary_asset = submission
                    character.save()
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


class OrderListBase(ListCreateAPIView):
    permission_classes = [ObjectControls]
    serializer_class = OrderViewSerializer

    @staticmethod
    def extra_filter(qs):
        return qs

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, self.user)
        return self.extra_filter(self.user.buys.all())


class CurrentOrderList(CurrentMixin, OrderListBase):
    pass


class ArchivedOrderList(ArchivedMixin, OrderListBase):
    pass


class CancelledOrderList(CancelledMixin, OrderListBase):
    pass


class SalesListBase(ListAPIView):
    permission_classes = [ObjectControls]
    serializer_class = OrderViewSerializer

    @staticmethod
    def extra_filter(qs):
        return qs

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, self.user)
        return self.extra_filter(self.user.sales.all())


class CurrentSalesList(CurrentMixin, SalesListBase):
    pass


class ArchivedSalesList(ArchivedMixin, SalesListBase):
    pass


class CancelledSalesList(CancelledMixin, SalesListBase):
    pass


class PlaceholderSalesListBase(ListCreateAPIView):
    permission_classes = [ObjectControls]
    serializer_class = PlaceholderSaleSerializer

    @staticmethod
    def extra_filter(qs):
        return qs

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, self.user)
        return self.extra_filter(self.user.placeholder_sales.all())


class CurrentPlaceholderSalesList(CurrentMixin, PlaceholderSalesListBase):
    def perform_create(self, serializer):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        return serializer.save(seller=user)


class ArchivedPlaceholderSalesList(ArchivedMixin, PlaceholderSalesListBase):
    pass


class PlaceholderManager(RetrieveUpdateDestroyAPIView):
    permission_classes = [OrderSellerPermission]
    serializer_class = PlaceholderSaleSerializer

    def get_object(self):
        placeholder = get_object_or_404(
            PlaceholderSale, id=self.kwargs['placeholder_id'], seller__username__iexact=self.kwargs['username']
        )
        self.check_object_permissions(self.request, placeholder)
        return placeholder


class CasesListBase(ListAPIView):
    permission_classes = [ObjectControls, IsStaff]
    serializer_class = OrderViewSerializer

    @staticmethod
    def extra_filter(qs):
        return qs

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, self.user)
        return self.extra_filter(self.user.cases.all())


class CurrentCasesList(CurrentMixin, CasesListBase):
    pass


class ArchivedCasesList(ArchivedMixin, CasesListBase):
    pass


class CancelledCasesList(CancelledMixin, CasesListBase):
    pass


class AdjustOrder(UpdateAPIView):
    permission_classes = [
        OrderSellerPermission, ObjectStatus(
            [Order.NEW, Order.PAYMENT_PENDING], "You may not adjust the price of a confirmed order."
        )
    ]
    serializer_class = OrderAdjustSerializer

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return order


class CardList(ListCreateAPIView):
    permission_classes = [UserControls]
    serializer_class = NewCardSerializer

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, self.user)
        qs = self.user.credit_cards.filter(active=True)
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
        except AuthorizeResponseError as err:
            return Response(data={'errors': [translate_authnet_error(err)]}, status=status.HTTP_400_BAD_REQUEST)
        if token.user.portrait_enabled:
            renew.delay(token.user.id, 'portrait')
        elif token.user.landscape_enabled:
            renew.delay(token.user.id, 'landscape')
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
            card_number=data['card_number'], cvv=data['cvv'], zip_code=data.get('zip'),
            make_primary=data['make_primary']
        )


class CardManager(RetrieveUpdateDestroyAPIView):
    permission_classes = [ObjectControls]
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
    permission_classes = [ObjectControls]

    def get_object(self):
        return get_object_or_404(
            CreditCardToken, id=self.kwargs['card_id'], user__username=self.kwargs['username'],
            active=True
        )

    def post(self, *args, **kwargs):
        card = self.get_object()
        self.check_object_permissions(self.request, card)
        card.user.primary_card = card
        card.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MakePayment(GenericAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [OrderBuyerPermission, EscrowPermission]

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return order

    def post(self, *args, **kwargs):
        order = self.get_object()
        attempt = self.get_serializer(data=self.request.data, context=self.get_serializer_context())
        attempt.is_valid(raise_exception=True)
        attempt = attempt.validated_data
        if attempt['amount'] != order.total().amount:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={'error': 'The price has changed. Please refresh the page.'}
            )
        card = get_object_or_404(CreditCardToken, id=attempt['card_id'], active=True, user=order.buyer)
        if not card.cvv_verified and not attempt['cvv']:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={'error': 'You must enter the security code for this card.'}
            )
        record = PaymentRecord.objects.create(
            card=card,
            payer=order.buyer,
            # Payment is currently in escrow.
            payee=None,
            escrow_for=order.seller,
            status=PaymentRecord.FAILURE,
            source=PaymentRecord.CARD,
            type=PaymentRecord.SALE,
            amount=attempt['amount'],
            response_message="Failed when contacting payment processor.",
            target=order,
        )
        code = status.HTTP_400_BAD_REQUEST
        data = {'error': record.response_message}
        try:
            result = card.api.capture(attempt['amount'], cvv=attempt['cvv'] or None)
        except Exception as err:
            record.response_message = translate_authnet_error(err)
            data['error'] = record.response_message
        else:
            record.status = PaymentRecord.SUCCESS
            record.txn_id = result.uid
            record.finalized = False
            record.response_message = ''
            code = status.HTTP_202_ACCEPTED
            order.status = Order.QUEUED
            order.task_weight = order.task_weight + order.adjustment_task_weight
            order.expected_turnaround = order.expected_turnaround + order.expected_turnaround
            order.dispute_available_on = (timezone.now() + BDay(ceil(ceil(order.expected_turnaround) * 1.25))).date()
            order.paid_on = timezone.now()
            order.save()
            card.cvv_verified = True
            card.save()
            notify(SALE_UPDATE, order, unique=True, mark_unread=True)
            data = OrderViewSerializer(instance=order, context=self.get_serializer_context()).data
        record.save()
        return Response(status=code, data=data)


class AccountBalance(RetrieveAPIView):
    permission_classes = [UserControls]
    serializer_class = AccountBalanceSerializer

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return user


class BankAccounts(ListCreateAPIView):
    permission_classes = [UserControls]
    serializer_class = BankAccountSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return BankAccount.objects.filter(user=user).exclude(deleted=True).order_by('-id')

    def perform_create(self, serializer):
        user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        # validated_data will have the additional fields, whereas data only contains fields for model creation.
        data = serializer.validated_data
        make_dwolla_account(self.request, user, data['first_name'], data['last_name'])
        account = add_bank_account(user, data['account_number'], data['routing_number'], data['type'])
        serializer.instance = account
        return account


class BankManager(DestroyAPIView):
    permission_classes = [ObjectControls]
    serializer_class = BankAccountSerializer

    def get_object(self):
        bank = get_object_or_404(BankAccount, user__username=self.kwargs['username'], id=self.kwargs['account'])
        self.check_object_permissions(self.request, bank)
        return bank

    def perform_destroy(self, instance):
        destroy_bank_account(instance)


class PerformWithdraw(APIView):
    permission_classes = [ObjectControls]
    serializer_class = WithdrawSerializer

    def post(self, request, username):
        errors = {}
        user = get_object_or_404(User, username=username)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        bank = None
        try:
            bank = BankAccount.objects.get(id=serializer.data['bank'])
            if not bank.user == user or bank.deleted:
                errors['account'] = ['The user has no such account.']
        except BankAccount.DoesNotExist:
            errors['account'] = ['The user has no such account.']
        self.check_object_permissions(request, bank)
        try:
            record = initiate_withdraw(user, bank, Money(serializer.data['amount'], 'USD'), test_only=errors)
        except ValidationError as err:
            errors.update(err.detail)
        if errors:
            return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)
        perform_transfer(record, note='Disbursement')
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductTag(BaseTagView):
    permission_classes = [ObjectControls]

    def get_object(self):
        return get_object_or_404(Product, user__username__iexact=self.kwargs['username'], id=self.kwargs['product'])

    def post_delete(self, product, qs):
        return Response(
            status=status.HTTP_200_OK,
            data=ProductSerializer(instance=product).data
        )

    def post_post(self, product, tag_list):
        return Response(
            status=status.HTTP_200_OK, data=ProductDetailSerializer(instance=product).data
        )


class ProductSearch(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if not query:
            return Product.objects.none()

        # If staffer, allow search on behalf of user.
        if self.request.user.is_staff:
            user = get_object_or_404(User, id=self.request.GET.get('user', self.request.user.id))
        else:
            user = self.request.user
        return available_products(user, query=query)


class PurchaseHistory(ListAPIView):
    permission_classes = [UserControls]
    serializer_class = PaymentRecordSerializer

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(user=self.user, context=self.get_serializer_context(), *args, **kwargs)

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, self.user)
        return PaymentRecord.objects.filter(
            payer=self.user
        ).exclude(type__in=[PaymentRecord.DISBURSEMENT_SENT, PaymentRecord.TRANSFER]).order_by('-id').distinct('id')


class EscrowHistory(ListAPIView):
    permission_classes = [UserControls]
    serializer_class = PaymentRecordSerializer

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(user=self.user, context=self.get_serializer_context(), *args, **kwargs)

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, self.user)
        return PaymentRecord.objects.filter(
            Q(payee=self.user, source=PaymentRecord.ESCROW) | Q(escrow_for=self.user)
        ).order_by('-id').distinct('id')


class AvailableHistory(ListAPIView):
    permission_classes = [UserControls]
    serializer_class = PaymentRecordSerializer

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(user=self.user, context=self.get_serializer_context(), *args, **kwargs)

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, self.user)
        return PaymentRecord.objects.filter(
            Q(payee=self.user, source=PaymentRecord.ESCROW) | Q(payer=self.user, type=PaymentRecord.DISBURSEMENT_SENT) |
            Q(payee=self.user, type=PaymentRecord.DISBURSEMENT_RETURNED) |
            Q(payer=self.user, type=PaymentRecord.TRANSFER)
        ).order_by('-id').distinct('id')


class CreateCharacterTransfer(CreateAPIView):
    serializer_class = CharacterTransferSerializer
    permission_classes = [ObjectControls]

    def post(self, *args, **kwargs):
        errors = {}
        try:
            if not self.request.data.get('buyer'):
                raise ValueError
            self.buyer = User.objects.get(id=self.request.data.get('buyer'))
        except User.DoesNotExist:
            errors = {'buyer': 'That user does not exist.'}
        except ValueError:
            errors = {'buyer': 'This field is required.'}
        serializer = self.get_serializer(data=self.request.data, context=self.get_serializer_context())
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as err:
            err.detail.update(errors)
            raise
        if errors:
            raise ValidationError(errors)
        return super().post(*args, **kwargs)

    def perform_create(self, serializer):
        character = get_object_or_404(
            Character, user__username__iexact=self.kwargs['username'], name=self.kwargs['character']
        )
        self.check_object_permissions(self.request, character)
        instance = serializer.save(
            character=character, seller=character.user, status=CharacterTransfer.NEW, buyer=self.buyer
        )
        # event_type, target, data=None, unique=False, unique_data=None, mark_unread=False, time_override=None,
        # transform=None, exclude=None, force_create=False
        subscribe(CHAR_TRANSFER, instance.buyer, instance)
        subscribe(CHAR_TRANSFER, instance.seller, instance)
        notify(CHAR_TRANSFER, instance, unique=True, exclude=[instance.seller])
        return instance


class RetrieveCharacterTransfer(RetrieveAPIView):
    serializer_class = CharacterTransferSerializer
    permission_classes = [OrderViewPermission]

    def get_object(self):
        transfer = get_object_or_404(CharacterTransfer, id=self.kwargs['transfer_id'])
        self.check_object_permissions(self.request, transfer)
        return transfer


class CancelCharTransfer(GenericAPIView):
    serializer_class = CharacterTransferSerializer
    permission_classes = [OrderViewPermission]

    def get_object(self):
        transfer = get_object_or_404(CharacterTransfer, id=self.kwargs['transfer_id'])
        self.check_object_permissions(self.request, transfer)
        return transfer

    def post(self, request, *args, **kwargs):
        transfer = self.get_object()
        if transfer.status != CharacterTransfer.NEW:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={
                    'error': 'This character transfer has already been closed.'
                }
            )
        if request.user == transfer.buyer:
            transfer.status = CharacterTransfer.REJECTED
        else:
            transfer.status = CharacterTransfer.CANCELLED
        transfer.save()
        transfer.character.transfer = None
        transfer.character.save()
        notify(CHAR_TRANSFER, transfer, unique=True, exclude=[request.user])
        return Response(status=status.HTTP_200_OK, data=self.get_serializer(instance=transfer).data)


class AcceptCharTransfer(GenericAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [OrderBuyerPermission]

    def get_object(self):
        transfer = get_object_or_404(CharacterTransfer, id=self.kwargs['transfer_id'])
        self.check_object_permissions(self.request, transfer)
        return transfer

    def mark_transfer_completed(self, transfer):
        transfer.status = CharacterTransfer.COMPLETED
        transfer.saved_name = transfer.character.name
        transfer.save()
        transfer.character.user = transfer.buyer
        transfer.character.transfer = None
        transfer.character.save()
        if transfer.include_assets:
            transfer.character.assets.filter(owner=transfer.seller).update(owner=transfer.buyer)
        notify(CHAR_TRANSFER, transfer, unique=True, exclude=[transfer.buyer])

    def post(self, *args, **kwargs):
        transfer = self.get_object()
        if transfer.status != CharacterTransfer.NEW:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={
                    'error': 'This character transfer has already been closed.'
                }
            )
        if transfer.buyer.characters.filter(name=transfer.character.name).exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={
                    'error': 'You already have a character with that name. '
                             'Please rename or remove the existing character.'
                }
            )
        if not transfer.price:
            self.mark_transfer_completed(transfer)
            return Response(
                status=status.HTTP_200_OK, data=CharacterTransferSerializer(
                    instance=transfer, context=self.get_serializer_context()
                ).data
            )
        attempt = self.get_serializer(data=self.request.data, context=self.get_serializer_context())
        attempt.is_valid(raise_exception=True)
        attempt = attempt.validated_data
        if attempt['amount'] != transfer.price.amount:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={'error': 'The price has changed. Please refresh the page.'}
            )
        card = get_object_or_404(CreditCardToken, id=attempt['card_id'], active=True, user=transfer.buyer)
        if not card.cvv_verified and not attempt['cvv']:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={'error': 'You must enter the security code for this card.'}
            )
        record = PaymentRecord.objects.create(
            card=card,
            payer=transfer.buyer,
            payee=transfer.seller,
            escrow_for=transfer.seller,
            status=PaymentRecord.FAILURE,
            source=PaymentRecord.CARD,
            type=PaymentRecord.SALE,
            amount=attempt['amount'],
            response_message="Failed when contacting payment processor.",
            target=transfer,
        )
        code = status.HTTP_400_BAD_REQUEST
        data = {'error': record.response_message}
        try:
            result = card.api.capture(attempt['amount'], cvv=attempt['cvv'] or None)
        except Exception as err:
            record.response_message = translate_authnet_error(err)
            data['error'] = record.response_message
        else:
            record.status = PaymentRecord.SUCCESS
            record.txn_id = result.uid
            record.finalized = False
            record.response_message = ''
            code = status.HTTP_202_ACCEPTED
            self.mark_transfer_completed(transfer)
            card.cvv_verified = True
            card.save()
            notify(SALE_UPDATE, transfer, unique=True, mark_unread=True)
            data = CharacterTransferSerializer(instance=transfer, context=self.get_serializer_context()).data
            PaymentRecord.objects.create(
                payer=transfer.seller,
                amount=(
                    (transfer.price * transfer.seller.percentage_fee * Decimal('.01'))
                    + Money(transfer.seller.static_fee, 'USD')
                ),
                payee=None,
                source=PaymentRecord.ACCOUNT,
                txn_id=str(uuid4()),
                target=transfer,
                type=PaymentRecord.TRANSFER,
                status=PaymentRecord.SUCCESS,
                response_code='ChrTrFee',
                response_message='Artconomy Service Fee'
            )
        record.save()
        return Response(status=code, data=data)


class CharacterTransferAssets(ListAPIView):
    serializer_class = ImageAssetSerializer
    permission_classes = [OrderViewPermission]

    def get_queryset(self):
        transfer = get_object_or_404(CharacterTransfer, id=self.kwargs['transfer_id'])
        self.check_object_permissions(self.request, transfer)
        if transfer.status == CharacterTransfer.NEW and transfer.include_assets:
            return transfer.character.assets.filter(owner=transfer.seller)
        else:
            return ImageAsset.objects.none()


class CharactersInbound(ListAPIView):
    serializer_class = CharacterTransferSerializer
    permission_classes = [UserControls]

    def get_queryset(self):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return CharacterTransfer.objects.filter(buyer=user, status=CharacterTransfer.NEW)


class CharactersOutbound(ListAPIView):
    serializer_class = CharacterTransferSerializer
    permission_classes = [UserControls]

    def get_queryset(self):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return CharacterTransfer.objects.filter(seller=user, status=CharacterTransfer.NEW)


class CharactersArchive(ListAPIView):
    serializer_class = CharacterTransferSerializer
    permission_classes = [UserControls]

    def get_queryset(self):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return CharacterTransfer.objects.filter(Q(seller=user)|Q(buyer=user)).exclude(status=CharacterTransfer.NEW)


class NewProducts(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = []

    def get_queryset(self):
        return available_products(
            self.request.user, ordering=False
        ).order_by('-id').distinct('id')


class WhoIsOpen(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return available_products(
            self.request.user, ordering=False
        ).filter(user__in=self.request.user.watching.all()).order_by('user')


class SalesStats(APIView):
    permission_classes = [ObjectControls]

    def get(self, request, **kwargs):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        self.check_object_permissions(request, user)
        products_available = available_products_by_load(user).count()
        data = {
            'load': user.load,
            'max_load': user.max_load,
            'commissions_closed': user.commissions_closed,
            'commissions_disabled': user.commissions_disabled,
            'products_available': products_available,
            'active_orders': user.sales.filter(status__in=WEIGHTED_STATUSES).count(),
            'new_orders': user.sales.filter(status=Order.NEW).count(),
        }
        return Response(status=status.HTTP_200_OK, data=data)


class RateOrder(GenericAPIView):
    serializer_class = RatingSerializer
    permission_classes = [OrderViewPermission]

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return order

    def get_target(self, order):
        target = None
        if order.seller == self.request.user:
            target = order.buyer
        elif order.buyer == self.request.user:
            target = order.seller
        elif self.request.GET('end'):
            end = self.request.GET('end')
            if end in ['buyer', 'seller']:
                target = getattr(order, end)
        return target

    def get_rating(self, order, target):
        ratings = Rating.objects.filter(
            object_id=order.id, content_type=ContentType.objects.get_for_model(order), rater=self.request.user,
            target=target
        )
        if ratings:
            return ratings[0]
        return None

    def get(self, request, **_kwargs):
        order = self.get_object()
        target = self.get_target(order)
        if target is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'stars': 'Target could not be determined.'})
        rating = self.get_rating(order, target)
        if rating is None:
            return Response(status=status.HTTP_200_OK, data={'stars': None})
        serializer = self.get_serializer(instance=rating)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def post(self, request, **_kwargs):
        order = self.get_object()
        target = self.get_target(order)
        if target is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'stars': 'Target could not be determined.'})
        if target == request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'stars': 'You may not rate yourself.'})
        if order.total() <= Money(0, 'USD'):
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={'stars': 'You may not rate an order that was free.'}
            )
        rating = self.get_rating(order, target)
        serializer = self.get_serializer(instance=rating, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            rater=request.user, object_id=order.id, content_type=ContentType.objects.get_for_model(order),
            target=target
        )
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class RatingList(ListAPIView):
    serializer_class = RatingSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        return user.ratings.all().order_by('-created_on')


class PremiumInfo(APIView):
    def get(self, _request):
        return Response(
            status=status.HTTP_200_OK,
            data={
                'landscape_percentage': str(settings.PREMIUM_PERCENTAGE_FEE),
                'landscape_static': str(settings.PREMIUM_STATIC_FEE),
                'landscape_price': str(settings.LANDSCAPE_PRICE),
                'standard_percentage': str(settings.STANDARD_PERCENTAGE_FEE),
                'standard_static': str(settings.STANDARD_STATIC_FEE),
                'portrait_price': str(settings.PORTRAIT_PRICE)
            }
        )


class Premium(GenericAPIView):
    serializer_class = ServicePaymentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        attempt = self.get_serializer(data=self.request.data, context=self.get_serializer_context())
        attempt.is_valid(raise_exception=True)
        attempt = attempt.validated_data
        card = get_object_or_404(CreditCardToken, id=attempt['card_id'], active=True, user=request.user)
        if not card.cvv_verified and not attempt['cvv']:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={'error': 'You must enter the security code for this card.'}
            )
        charge_required, target_date = check_charge_required(self.request.user, attempt['service'])
        if not charge_required:
            set_service(request.user, attempt['service'], target_date=target_date)
            return Response(
                status=status.HTTP_200_OK,
                data=UserSerializer(instance=self.request.user, context=self.get_serializer_context()).data
            )
        price = service_price(request.user, attempt['service'])
        record = PaymentRecord.objects.create(
            card=card,
            payer=self.request.user,
            payee=None,
            status=PaymentRecord.FAILURE,
            source=PaymentRecord.CARD,
            type=PaymentRecord.SALE,
            amount=price,
            response_message="Failed when contacting payment processor.",
            target=request.user,
        )
        code = status.HTTP_400_BAD_REQUEST
        data = {'error': record.response_message}
        try:
            result = card.api.capture(price.amount, cvv=attempt['cvv'] or None)
        except Exception as err:
            record.response_message = translate_authnet_error(err)
            data['error'] = record.response_message
        else:
            record.status = PaymentRecord.SUCCESS
            record.txn_id = result.uid
            record.finalized = True
            record.response_message = 'Upgraded to {}'.format(attempt['service'])
            code = status.HTTP_202_ACCEPTED
            card.cvv_verified = True
            card.save()
            set_service(request.user, attempt['service'], target_date=date.today() + relativedelta(months=1))
            data = UserSerializer(instance=request.user, context=self.get_serializer_context()).data
        record.save()
        return Response(status=code, data=data)


class CancelPremium(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        self.check_permissions(request)
        request.user.portrait_enabled = False
        request.user.landscape_enabled = False
        request.user.save()
        return Response(
            status=status.HTTP_200_OK,
            data=UserSerializer(context={'request': request}, instance=self.request.user).data
        )


class ProductPreview(BasePreview):
    def context(self, username, product_id):
        product = get_object_or_404(Product, id=product_id, active=True, hidden=False)
        if self.request.max_rating < product.rating:
            image = '/static/images/logo.png'
        else:
            image = product.preview_link
        return {
            'title': demark(product.name),
            'description': demark(product.description),
            'image_link': image
        }
