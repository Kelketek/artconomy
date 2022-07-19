from django.db import transaction, IntegrityError
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from stripe.error import InvalidRequestError

from apps.lib.models import ref_for_instance
from apps.lib.permissions import IsStaff
from apps.profiles.models import User
from apps.profiles.permissions import UserControls, IsRegistered
from apps.profiles.tasks import create_or_update_stripe_user
from apps.sales.models import StripeAccount, ServicePlan, TransactionRecord, PREMIUM_SUBSCRIPTION, OPEN, Invoice, DRAFT, \
    StripeReader
from apps.sales.permissions import InvoiceStatus
from apps.sales.serializers import StripeBankSetupSerializer, StripeAccountSerializer, PremiumIntentSettings, \
    PaymentIntentSettings, TerminalProcessSerializer, StripeReaderSerializer
from apps.sales.stripe import stripe, create_stripe_account, get_country_list, create_account_link
from apps.sales.utils import get_intent_card_token, get_term_invoice


def create_account(*, user: User, country: str):
    """
    Create a stripe account for a user.
    Note: The account might already exist and be the wrong country code. In this case we need to delete the existing
    account.

    But in doing so, we'll need to start a new transaction to begin again, so we call this function one more time.
    """
    restart = False
    with transaction.atomic(), stripe as api:
        account, created = StripeAccount.objects.get_or_create(
            user=user, defaults={'token': 'XXX', 'country': country},
        )
        if not account.active and account.country != country:
            account.delete()
            restart = True
        if created:
            account_data = create_stripe_account(api=api, country=country)
            account.token = account_data['id']
            account.save()
    if restart:
        return create_account(user=user, country=country)
    return account


class StripeAccountLink(GenericAPIView):
    permission_classes = [UserControls]
    serializer_class = StripeBankSetupSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        with stripe as api:
            countries = tuple(
                (item['value'], item['text']) for item in get_country_list(api=api)
            )
            context['countries'] = countries
        return context

    def get_object(self):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return user

    def post(self, *_args, **_kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        country = serializer.validated_data['country']
        try:
            account = create_account(user=user, country=country)
        except IntegrityError as err:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': str(err)})
        url = serializer.validated_data['url']
        with stripe as api:
            account_link = create_account_link(
                api=api,
                token=account.token,
                refresh_url=url,
                return_url=url,
            )
        return Response(status=200, data={'link': account_link['url']})


class StripeAccounts(ListAPIView):
    """
    StripeAccount is actually one-to-one, but we want to subscribe to this object being created, so we're piggy-backing
    on list creation for our websockets' sake.

    If we have many more singletons like this, it will be worth making a new websocket command.
    """
    permission_classes = [UserControls]
    serializer_class = StripeAccountSerializer
    pagination_class = None

    def get_object(self):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return user

    def get_queryset(self):
        return StripeAccount.objects.filter(user=self.get_object())


class StripeCountries(APIView):
    def get(self, _request):
        with stripe as api:
            return Response(data={'countries': get_country_list(api=api)})


class PremiumPaymentIntent(APIView):
    """
    Create payment intent for upgrading to a premium service.

    TODO: Find a way to eliminate this.
    """
    permission_classes = [IsRegistered]

    def post(self, *args, **kwargs):
        card = get_intent_card_token(self.request.user, self.kwargs.get('card_id'))
        serializer = PremiumIntentSettings(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        make_primary = serializer.validated_data['make_primary']
        service_plan = ServicePlan.objects.get(name='Landscape')
        # In case the initial creation failed for some reason.
        create_or_update_stripe_user(self.request.user.id)
        self.request.user.refresh_from_db()
        invoice = get_term_invoice(self.request.user)
        amount = service_plan.monthly_charge
        item, _created = invoice.line_items.update_or_create(
            defaults={'amount': amount, 'description': service_plan.name},
            destination_account=TransactionRecord.UNPROCESSED_EARNINGS,
            type=PREMIUM_SUBSCRIPTION,
            destination_user=None,
        )
        item.targets.add(ref_for_instance(service_plan))
        with stripe as stripe_api:
            # Can only do string values, so won't be json true value.
            metadata = {'make_primary': make_primary, 'save_card': True, 'invoice_id': invoice.id}
            intent_kwargs = {
                # Need to figure out how to do this per-currency.
                'amount': int(amount.amount * amount.currency.sub_unit),
                'currency': str(amount.currency).lower(),
                'customer': self.request.user.stripe_token,
                # Note: If we expand the payment types, we may need to take into account that linking the
                # charge_id to the source_transaction field of the payout transfer could cause problems. See:
                # https://stripe.com/docs/connect/charges-transfers#transfer-availability
                'payment_method_types': ['card'],
                'payment_method': card,
                'metadata': metadata,
                'receipt_email': self.request.user.email,
                'setup_future_usage': 'off_session',
            }
            if invoice.current_intent:
                intent = stripe_api.PaymentIntent.modify(invoice.current_intent, **intent_kwargs)
                return Response({'secret': intent['client_secret']})
            intent = stripe_api.PaymentIntent.create(**intent_kwargs)
            invoice.current_intent = intent['id']
            invoice.save()
            return Response({'secret': intent['client_secret']})


class SetupIntent(APIView):
    permission_classes = [UserControls]

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return user

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        create_or_update_stripe_user(user.id)
        user.refresh_from_db()
        with stripe as stripe_api:
            return Response({'secret': stripe_api.SetupIntent.create(
                payment_method_types=["card"],
                customer=user.stripe_token,
            )['client_secret']})


class InvoicePaymentIntent(APIView):
    """
    Creates a payment intent for an invoice. Right now this only works for table
    invoices-- Fixes for permissions will need to be made to make sure someone
    doesn't pay for a deliverable in the wrong status.
    """
    permission_classes = [UserControls, InvoiceStatus(OPEN)]

    def get_object(self):
        invoice = get_object_or_404(
            Invoice.objects.select_for_update(), id=self.kwargs['invoice'],
            status__in=[OPEN, DRAFT], record_only=False,
        )
        self.check_object_permissions(self.request, invoice)
        return invoice

    @transaction.atomic
    def post(self, *args, **kwargs):
        invoice = self.get_object()
        if invoice.bill_to.is_registered:
            create_or_update_stripe_user(invoice.bill_to.id)
            invoice.bill_to.refresh_from_db()
        serializer = PaymentIntentSettings(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        stripe_token = get_intent_card_token(invoice.bill_to, serializer.validated_data.get('card_id'))
        use_terminal = serializer.validated_data['use_reader']
        save_card = serializer.validated_data['save_card'] and not invoice.bill_to.guest
        make_primary = (save_card and serializer.validated_data['make_primary']) and not invoice.bill_to.guest
        total = invoice.total()
        amount = int(total.amount * total.currency.sub_unit)
        if not amount:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'detail': 'Cannot create a payment intent for a zero invoice.'},
            )
        if use_terminal:
            # We set card here as well to prevent a transaction issue on Stripe's side where
            # We can't unset the payment method at the same time as changing the payment method
            # types to just card_present.
            payment_method_types = ['card_present', 'card']
            capture_method = 'manual'
            save_card = False
            make_primary = False
            stripe_token = None
        else:
            payment_method_types = ['card']
            capture_method = 'automatic'
        with stripe as stripe_api:
            # Can only do string values, so won't be json true value.
            metadata = {'invoice_id': invoice.id, 'make_primary': make_primary, 'save_card': save_card}
            intent_kwargs = {
                # Need to figure out how to do this per-currency.
                'amount': int(total.amount * total.currency.sub_unit),
                'currency': str(total.currency).lower(),
                'customer': invoice.bill_to.stripe_token or None,
                # Note: If we expand the payment types, we may need to take into account that linking the
                # charge_id to the source_transaction field of the payout transfer could cause problems. See:
                # https://stripe.com/docs/connect/charges-transfers#transfer-availability
                'payment_method_types': payment_method_types,
                'payment_method': stripe_token,
                'capture_method': capture_method,
                'transfer_group': f'ACInvoice#{invoice.id}',
                'metadata': metadata,
                'receipt_email': invoice.bill_to.guest_email or invoice.bill_to.email,
            }
            if save_card:
                intent_kwargs['setup_future_usage'] = 'off_session'
            if invoice.current_intent:
                try:
                    intent = stripe_api.PaymentIntent.modify(invoice.current_intent, **intent_kwargs)
                except InvalidRequestError as err:
                    if err.code == 'payment_intent_unexpected_state':
                        return Response({
                            'detail': 'Payment intent not in expected state. '
                                      'Likely, it has been paid and we are waiting on webhooks.',
                        }, status=status.HTTP_400_BAD_REQUEST)
                return Response({'secret': intent['client_secret']})
            intent = stripe_api.PaymentIntent.create(**intent_kwargs)
            invoice.current_intent = intent['id']
            invoice.save()
            return Response({'secret': intent['client_secret']})


class ProcessPresentCard(APIView):
    """
    When the client is using an in-person card, we have to submit a request
    to have the reader engaged for processing. Get a reader from the staffer
    running the terminal and use it to process.
    """
    permission_classes = [UserControls, InvoiceStatus(OPEN)]
    serializer_class = TerminalProcessSerializer

    def get_object(self):
        invoice = get_object_or_404(
            Invoice, id=self.kwargs['invoice'],
            status__in=[OPEN, DRAFT], record_only=False,
        )
        self.check_object_permissions(self.request, invoice)
        return invoice

    def post(self, *args, **kwargs):
        invoice = self.get_object()
        if not invoice.current_intent:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    'detail': 'This invoice does not have a generated payment intent.',
                }
            )
        serializer = TerminalProcessSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        reader = get_object_or_404(StripeReader, id=serializer.validated_data['reader'])
        with stripe as stripe_api:
            try:
                stripe_api.terminal.Reader.process_payment_intent(
                    reader.stripe_token,
                    payment_intent=invoice.current_intent,
                )
            except InvalidRequestError as err:
                if 'Reader is currently unreachable' in str(err):
                    return Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={
                            'detail': 'Could not reach the card reader. Make sure it is on and connected '
                                      'to the Internet.'
                        },
                    )
                else:
                    raise
            if reader.virtual:
                stripe_api.terminal.Reader.TestHelpers.present_payment_method(
                    reader.stripe_token,
                )
        return Response(status=status.HTTP_204_NO_CONTENT)


class StripeReaders(ListAPIView):
    """
    Lists all of the Stripe Readers in the system.
    """
    permission_classes = [IsStaff]
    serializer_class = StripeReaderSerializer

    def get_queryset(self) -> QuerySet:
        return StripeReader.objects.all()
