from uuid import uuid4

from authorize import AuthorizeError
from django.core.files.base import ContentFile
from django.db.models import When, F, Case, BooleanField, Q
from django.db.transaction import atomic
from django.shortcuts import render, get_object_or_404

# Create your views here.
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, RetrieveAPIView, \
    GenericAPIView, ListAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.lib.permissions import ObjectStatus
from apps.lib.serializers import CommentSerializer
from apps.profiles.models import User, ImageAsset, Character
from apps.profiles.permissions import ObjectControls, UserControls
from apps.profiles.serializers import ImageAssetSerializer
from apps.sales.permissions import OrderViewPermission, OrderSellerPermission, OrderBuyerPermission
from apps.sales.models import Product, Order, CreditCardToken, PaymentRecord, Revision
from apps.sales.serializers import ProductSerializer, ProductNewOrderSerializer, OrderViewSerializer, CardSerializer, \
    NewCardSerializer, OrderAdjustSerializer, PaymentSerializer, RevisionSerializer, OrderStartedSerializer


class ProductListAPI(ListCreateAPIView):
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        if not (self.request.user.is_staff or self.request.user == user):
            raise PermissionDenied("You do not have permission to create products for that user.")
        product = serializer.save(uploaded_by=user, user=user)
        return product

    def get_queryset(self):
        username = self.kwargs['username']
        qs = Product.objects.filter(user__username__iexact=self.kwargs['username'], active=True)
        if not (self.request.user.username.lower() == username or self.request.user.is_staff):
            qs = qs.exclude(hidden=True)
        qs = qs.order_by('created_on')
        return qs


class ProductManager(RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [ObjectControls]

    def get_object(self):
        product = get_object_or_404(Product, user__username=self.kwargs['username'], id=self.kwargs['product'])
        self.check_object_permissions(self.request, product)
        return product


class ProductExamples(ListAPIView):
    serializer_class = ImageAssetSerializer

    def get_queryset(self):
        product = get_object_or_404(Product, user__username=self.kwargs['username'], id=self.kwargs['product'])
        qs = ImageAsset.objects.filter(order__product=product, rating__lte=self.request.max_rating)
        if not (self.request.user == product.user or self.request.user.is_staff):
            if product.hidden:
                raise PermissionDenied('Example listings for this product are hidden.')
            qs = qs.exclude(private=True)
        return qs


class PlaceOrder(CreateAPIView):
    serializer_class = ProductNewOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer(self, instance=None, data=None, many=False, partial=False):
        return self.serializer_class(instance=instance, data=data, many=many, partial=partial, request=self.request)

    def perform_create(self, serializer):
        product = get_object_or_404(Product, id=self.kwargs['product'], hidden=False)
        order = serializer.save(product=product, buyer=self.request.user, seller=product.user)
        return order


class OrderRetrieve(RetrieveAPIView):
    permission_classes = [OrderViewPermission]
    serializer_class = OrderViewSerializer

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'])


class OrderAccept(GenericAPIView):
    permission_classes = [OrderSellerPermission]
    serializer_class = OrderViewSerializer

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'])

    def post(self, request, **_kwargs):
        order = self.get_object()
        self.check_object_permissions(request, order)
        if order.status != Order.NEW:
            return Response(
                {'error': "Approval can only be applied to new orders."}, status=status.HTTP_400_BAD_REQUEST
            )
        order.status = Order.PAYMENT_PENDING
        order.price = order.product.price
        order.revisions = order.product.revisions
        order.save()
        data = self.serializer_class(instance=order).data
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
        serializer.save(status=Order.IN_PROGRESS)
        return Response(serializer.data)


class OrderCancel(GenericAPIView):
    permission_classes = [OrderViewPermission]
    serializer_class = OrderViewSerializer

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        if order.status not in [Order.NEW, Order.PAYMENT_PENDING]:
            raise PermissionDenied(
                "You cannot cancel this order. It is either already cancelled or must be refunded instead."
            )
        return order

    def post(self, request, order_id):
        order = self.get_object()
        order.status = Order.CANCELLED
        order.save()
        data = self.serializer_class(instance=order).data
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
        serializer.save(user=self.request.user, content_object=order)


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
        revision = serializer.save(order=order, uploaded_by=self.request.user)
        order.refresh_from_db()
        if (order.revision_set.all().count() >= order.revisions + 1) and (order.status == Order.IN_PROGRESS):
            order.status = Order.REVIEW
            order.save()
        return revision


class DeleteOrderRevision(DestroyAPIView):
    permission_classes = [OrderSellerPermission]
    serializer_class = RevisionSerializer

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        if order.status not in [Order.REVIEW, Order.IN_PROGRESS]:
            raise PermissionDenied("This order's revisions are locked.")
        revision = get_object_or_404(Revision, id=self.kwargs['revision_id'], order_id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return revision

    def perform_destroy(self, instance):
        super(DeleteOrderRevision, self).perform_destroy(instance)
        order = Order.objects.get(id=self.kwargs['order_id'])
        if order.status == Order.REVIEW:
            order.status = Order.IN_PROGRESS
            order.save()


class ApproveFinal(GenericAPIView):
    permission_classes = [OrderBuyerPermission]
    serializer_class = OrderViewSerializer

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'])

    def post(self, _request, *_args, **_kwargs):
        order = self.get_object()
        self.check_object_permissions(self.request, order)
        if order.status not in [Order.REVIEW, Order.DISPUTED]:
            raise PermissionDenied('This order is not in an approvable state.')
        with atomic():
            order.status = order.COMPLETED
            order.save()
            final = order.revision_set.last()
            submission = ImageAsset(
                artist=order.seller, uploaded_by=order.seller, order=order,
                rating=final.rating
            )
            new_file = ContentFile(final.file.read())
            new_file.name = final.file.name
            submission.file = new_file
            submission.save()
            submission.characters.add(*order.characters.all())
            PaymentRecord(
                payer=None,
                amount=order.price + order.adjustment,
                payee=order.seller,
                source=PaymentRecord.ESCROW,
                txn_id=str(uuid4()),
                content_object=order,
                payment_type=PaymentRecord.TRANSFER,
                status=PaymentRecord.SUCCESS,
                response_code='OdrFnl',
                response_message='Order finalized.'
            ).save()
            PaymentRecord(
                payer=order.seller,
                amount=(order.price + order.adjustment) * order.seller.fee,
                payee=None,
                source=PaymentRecord.ACCOUNT,
                txn_id=str(uuid4()),
                content_object=order,
                payment_type=PaymentRecord.TRANSFER,
                status=PaymentRecord.SUCCESS,
                response_code='OdrFee',
                response_message='Artconomy Service Fee'
            ).save()
        return Response(status=status.HTTP_200_OK, data=OrderViewSerializer(instance=order).data)


class CurrentMixin(object):
    @staticmethod
    def extra_filter(qs):
        return qs.exclude(status__in=[Order.COMPLETED, Order.CANCELLED])


class ArchivedMixin(object):
    @staticmethod
    def extra_filter(qs):
        return qs.filter(status=Order.COMPLETED)


class CancelledMixin(object):
    @staticmethod
    def extra_filter(qs):
        return qs.filter(status=Order.CANCELLED)


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


class AdjustOrder(UpdateAPIView):
    permission_classes = [
        OrderSellerPermission, ObjectStatus(Order.NEW, "You may not adjust the price of a confirmed order.")
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
        return qs.order_by('-primary')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NewCardSerializer
        else:
            return CardSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = self.perform_create(serializer)
        serializer = CardSerializer(instance=token)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        data = serializer.validated_data
        user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return CreditCardToken.create(
            user=user, exp_month=data['exp_date'].month, exp_year=data['exp_date'].year,
            security_code=data['security_code'], number=data['card_number'],
            zip_code=data.get('zip')
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
    permission_classes = [OrderBuyerPermission]

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        self.check_object_permissions(self.request, order)
        return order

    def post(self, *args, **kwargs):
        order = self.get_object()
        attempt = self.get_serializer(data=self.request.data)
        attempt.is_valid(raise_exception=True)
        attempt = attempt.validated_data
        if attempt['amount'] != order.total().amount:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={'error': 'The price has changed. Please refresh the page.'}
            )
        card = get_object_or_404(CreditCardToken, id=attempt['card_id'], active=True, user=order.buyer)
        record = PaymentRecord.objects.create(
            card=card,
            payer=order.buyer,
            # Payment is currently in escrow.
            payee=None,
            escrow_for=order.seller,
            status=PaymentRecord.FAILURE,
            source=PaymentRecord.CARD,
            payment_type=PaymentRecord.SALE,
            amount=attempt['amount'],
            response_message="Failed when contacting Authorize.net.",
            content_object=order,
        )
        code = status.HTTP_400_BAD_REQUEST
        data = {'error': record.response_message}
        try:
            result = card.api.capture(attempt['amount'])
        except AuthorizeError as err:
            record.response_message = str(err)
            data['error'] = record.response_message
        else:
            record.status = PaymentRecord.SUCCESS
            record.txn_id = result.uid
            record.response_message = ''
            code = status.HTTP_202_ACCEPTED
            order.status = Order.QUEUED
            order.save()
            data = OrderViewSerializer(instance=order).data
        record.save()
        return Response(status=code, data=data)
