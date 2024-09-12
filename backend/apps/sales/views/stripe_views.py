from apps.lib.permissions import StaffPower, Any
from apps.profiles.models import User
from apps.profiles.permissions import IsRegistered, ObjectControls, BillTo
from apps.profiles.tasks import create_or_update_stripe_user
from apps.sales.constants import DRAFT, OPEN
from apps.sales.models import Invoice, ServicePlan, StripeAccount, StripeReader
from apps.sales.permissions import InvoiceStatus
from apps.sales.serializers import (
    PaymentIntentSettings,
    PremiumIntentSettings,
    StripeAccountSerializer,
    StripeBankSetupSerializer,
    StripeReaderSerializer,
    TerminalProcessSerializer,
    DashboardLinkSerializer,
)
from apps.sales.stripe import (
    create_account_link,
    create_stripe_account,
    get_country_list,
    stripe,
)
from apps.sales.utils import get_invoice_intent, subscription_invoice_for_service
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from stripe.error import InvalidRequestError


def create_account(*, user: User, country: str):
    """
    Create a stripe account for a user.
    Note: The account might already exist and be the wrong country code. In this case we
    need to delete the existing account.

    But in doing so, we'll need to start a new transaction to begin again, so we call
    this function one more time.
    """
    restart = False
    with transaction.atomic(), stripe as api:
        account, created = StripeAccount.objects.get_or_create(
            user=user,
            defaults={"token": "XXX", "country": country},
        )
        if not account.active and account.country != country:
            account.delete()
            restart = True
        if created:
            account_data = create_stripe_account(api=api, country=country)
            account.token = account_data["id"]
            account.save()
    if restart:
        return create_account(user=user, country=country)
    return account


class StripeAccountLink(GenericAPIView):
    permission_classes = [Any(ObjectControls, StaffPower("administrate_users"))]
    serializer_class = StripeBankSetupSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        with stripe as api:
            countries = tuple(
                (item["value"], item["title"]) for item in get_country_list(api=api)
            )
            context["countries"] = countries
        return context

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(self.request, user)
        return user

    def post(self, *_args, **_kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        country = serializer.validated_data["country"]
        try:
            account = create_account(user=user, country=country)
        except IntegrityError as err:  # pragma: no cover
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"detail": str(err)}
            )
        url = serializer.validated_data["url"]
        with stripe as api:
            account_link = create_account_link(
                api=api,
                token=account.token,
                refresh_url=url,
                return_url=url,
            )
        return Response(status=200, data={"link": account_link["url"]})


class StripeAccounts(ListAPIView):
    """
    StripeAccount is actually one-to-one, but we want to subscribe to this object being
    created, so we're piggy-backing on list creation for our websockets' sake.

    If we have many more singletons like this, it will be worth making a new websocket
    command.
    """

    permission_classes = [Any(ObjectControls, StaffPower("view_financials"))]
    serializer_class = StripeAccountSerializer
    pagination_class = None

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(self.request, user)
        return user

    def get_queryset(self):
        return StripeAccount.objects.filter(user=self.get_object())


class StripeCountries(APIView):
    def get(self, _request):
        with stripe as api:
            return Response(data={"countries": get_country_list(api=api)})


class PremiumPaymentIntent(APIView):
    """
    Create payment intent for upgrading to a premium service.

    We could just make an endpoint that only creates the invoice, but doing so means
    significantly complicating the frontend code.
    """

    permission_classes = [IsRegistered]

    def post(self, *args, **kwargs):
        serializer = PremiumIntentSettings(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, username=self.kwargs["username"])
        service_plan = get_object_or_404(
            ServicePlan, name=serializer.validated_data["service"]
        )
        invoice = subscription_invoice_for_service(user, service_plan)
        return Response(
            {
                "secret": get_invoice_intent(
                    invoice=invoice,
                    payment_settings=serializer.validated_data,
                )
            }
        )


class SetupIntent(APIView):
    permission_classes = [Any(ObjectControls, StaffPower("table_seller"))]

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(self.request, user)
        return user

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        create_or_update_stripe_user(user.id)
        user.refresh_from_db()
        with stripe as stripe_api:
            return Response(
                {
                    "secret": stripe_api.SetupIntent.create(
                        payment_method_types=["card"],
                        customer=user.stripe_token,
                    )["client_secret"]
                }
            )


class InvoicePaymentIntent(APIView):
    """
    Creates a payment intent for an invoice.
    """

    permission_classes = [
        Any(BillTo, StaffPower("table_seller")),
        InvoiceStatus(OPEN),
    ]

    def get_object(self):
        invoice = get_object_or_404(
            Invoice.objects.select_for_update(),
            id=self.kwargs["invoice"],
            status__in=[OPEN, DRAFT],
            record_only=False,
        )
        self.check_object_permissions(self.request, invoice)
        return invoice

    @transaction.atomic
    def post(self, *args, **kwargs):
        serializer = PaymentIntentSettings(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                "secret": get_invoice_intent(
                    invoice=self.get_object(),
                    payment_settings=serializer.validated_data,
                )
            }
        )


class ProcessPresentCard(APIView):
    """
    When the client is using an in-person card, we have to submit a request
    to have the reader engaged for processing. Get a reader from the staffer
    running the terminal and use it to process.
    """

    permission_classes = [
        Any(BillTo, StaffPower("table_seller")),
        InvoiceStatus(OPEN),
    ]
    serializer_class = TerminalProcessSerializer

    def get_object(self):
        invoice = get_object_or_404(
            Invoice,
            id=self.kwargs["invoice"],
            status__in=[OPEN, DRAFT],
            record_only=False,
        )
        self.check_object_permissions(self.request, invoice)
        return invoice

    def post(self, *args, **kwargs):
        invoice = self.get_object()
        if not invoice.current_intent:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "detail": "This invoice does not have a generated payment intent.",
                },
            )
        serializer = TerminalProcessSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        reader = get_object_or_404(StripeReader, id=serializer.validated_data["reader"])
        with stripe as stripe_api:
            try:
                stripe_api.terminal.Reader.process_payment_intent(
                    reader.stripe_token,
                    payment_intent=invoice.current_intent,
                )
            except InvalidRequestError as err:
                if "Reader is currently unreachable" in str(err):
                    return Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={
                            "detail": "Could not reach the card reader. Make sure it "
                            "is on and connected to the Internet."
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
    Lists all the Stripe Readers in the system.
    """

    permission_classes = [StaffPower("table_seller")]
    serializer_class = StripeReaderSerializer

    def get_queryset(self) -> QuerySet:
        return StripeReader.objects.all()


class StripeDashboardLink(GenericAPIView):
    """
    Generate an express Dashboard Link
    """

    permission_classes = [Any(ObjectControls, StaffPower("view_financials"))]
    serializer_class = DashboardLinkSerializer

    def get_object(self):
        account = get_object_or_404(
            StripeAccount, user__username=self.kwargs["username"]
        )
        self.check_object_permissions(self.request, account)
        return account

    def post(self, *args, **kwargs):
        account = self.get_object()
        serializer = self.get_serializer(instance=account)
        return Response(serializer.data, status=status.HTTP_200_OK)
