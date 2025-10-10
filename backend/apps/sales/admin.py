import html

from django.conf import settings
from django.db.models.functions import Collate

from apps.lib.admin import CommentInline
from apps.lib.models import ref_for_instance
from apps.profiles.models import User
from apps.profiles.utils import get_anonymous_user
from apps.sales.constants import (
    CANCELLED,
    BEFORE_PAYMENT_STATUSES,
    PAID_STATUSES,
    REFUNDED,
    SUCCESS,
    FUND,
    CARD,
    ESCROW_REFUND,
    FAILURE,
    PAYOUT_ACCOUNT,
    HOLDINGS,
    ESCROW,
)
from apps.sales.models import (
    CreditCardToken,
    Deliverable,
    Invoice,
    LineItem,
    LineItemAnnotation,
    Order,
    Product,
    Promo,
    Rating,
    Revision,
    ServicePlan,
    StripeLocation,
    StripeReader,
    TransactionRecord,
    WebhookRecord,
    PaypalConfig,
    StripeAccount,
)
from apps.sales.stripe import stripe, reverse_transfer
from apps.sales.utils import reverse_record, issue_refund, fetch_prefixed
from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db.transaction import atomic

# Register your models here.
from django.forms import ModelForm, TextInput
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class ProductAdmin(admin.ModelAdmin):
    raw_id_fields = [
        "user",
        "owner",
        "primary_submission",
        "samples",
        "tags",
        "file",
        "preview",
    ]


class OrderAdmin(admin.ModelAdmin):
    inlines = [CommentInline]
    raw_id_fields = ["buyer", "seller"]
    list_display = ("buyer", "seller")


def safe_display_banned_user(record: User):
    """
    Safely render a user's info such that no user-written characters are shown and
    it can be HTML embedded in a message with a link.
    """
    return (
        f'<a href="{reverse("admin:profiles_user_change", args=[record.id])}'
        f'">{html.escape(record.username)}</a>'
        f" was forcibly deactivated."
    )


def get_payout_link_message(seller):
    """
    Get the link to the payout page for this seller so that reversals can be done.
    """
    if settings.ENV_NAME == "production":
        base_url = "https://dashboard.stripe.com/"
    else:
        base_url = "https://dashboard.stripe.com/test/"
    if not hasattr(seller, "stripe_account"):
        return (
            f"No stripe account on file for {seller.username}. "
            f"Are you sure you picked the right order?"
        )
    return (
        f'Visit <a href="{base_url}connect/accounts/'
        f"{seller.stripe_account.token}/\">{html.escape(seller.username)}'s Stripe "
        f"account</a> to reverse payouts."
    )


def deliverable_display(deliverable: Deliverable):
    url = reverse("admin:sales_deliverable_change", args=[deliverable.id])
    return f'<a href="{url}">Deliverable #{deliverable.id}</a>'


def mark_refunded(deliverable: Deliverable):
    deliverable.status = REFUNDED
    deliverable.refunded_on = deliverable.refunded_on or timezone.now()
    deliverable.save()


def force_refund(*, model_admin, request, deliverable, ref) -> None:
    fund_transaction = TransactionRecord.objects.filter(
        status=SUCCESS,
        destination=FUND,
        source=CARD,
        targets=ref,
        payer=deliverable.order.buyer,
    ).first()
    if not fund_transaction:
        model_admin.message_user(
            request,
            mark_safe(
                f"Could not find card transaction for "
                f"{deliverable_display(deliverable)}."
            ),
            level=messages.ERROR,
        )
        return
    record = issue_refund(
        fund_transaction,
        TransactionRecord.objects.filter(
            source=FUND,
            payer=deliverable.order.buyer,
            targets=ref,
            status=SUCCESS,
        ),
        ESCROW_REFUND,
        processor=deliverable.processor,
    )[0]
    if record.status == FAILURE:
        model_admin.message_user(
            request,
            mark_safe(
                f"Failed refunding {deliverable_display(deliverable)}. "
                f"{html.escape(record.response_message)}"
            ),
            level=messages.ERROR,
        )
    else:
        model_admin.message_user(
            request,
            mark_safe(f"Refunded {deliverable_display(deliverable)}."),
            level=messages.SUCCESS,
        )


@admin.action(description="Force refund of fraudulent")
def kill_fraudulent(model_admin, request, queryset):
    queryset.filter(escrow_enabled=False).update(status=CANCELLED)
    queryset.filter(status__in=BEFORE_PAYMENT_STATUSES).update(status=CANCELLED)
    sellers = set()
    users = set()
    deliverables = set()
    for deliverable in queryset:
        users.add(deliverable.order.seller)
        if deliverable.escrow_enabled:
            sellers.add(deliverable.order.seller)
        if deliverable.order.buyer:
            users.add(deliverable.order.buyer)
        if deliverable.status in PAID_STATUSES and deliverable.status != REFUNDED:
            deliverables.add(deliverable)
    for seller in sellers:
        seller.artist_profile.auto_withdraw = False
        seller.artist_profile.save()
        message = get_payout_link_message(seller)
        model_admin.message_user(
            request, mark_safe(message), level=messages.WARNING, extra_tags="safe"
        )
    for user in users:
        user.is_active = False
        user.notes += (
            f"\nBanned for fraud by {request.user.username} on {timezone.now()}"
        )
        user.save(update_fields=["is_active", "notes"])
        message = safe_display_banned_user(user)
        model_admin.message_user(
            request, mark_safe(message), level=messages.SUCCESS, extra_tags="safe"
        )
    for deliverable in deliverables:
        ref = ref_for_instance(deliverable)
        # First, we refund the card.
        force_refund(
            request=request, deliverable=deliverable, model_admin=model_admin, ref=ref
        )
        # Next, we reverse the intermediate escrow transaction. This may not exist if
        # the deliverable wasn't finalized.
        to_reverse = TransactionRecord.objects.filter(
            destination=HOLDINGS,
            source=ESCROW,
            targets=ref,
            payee=deliverable.order.seller,
        ).first()
        if to_reverse:
            reverse_record(to_reverse)
        # Finally, we reverse the transfer to the fraudster, if it exists.
        transfer_record = TransactionRecord.objects.filter(
            targets=ref,
            source=HOLDINGS,
            destination=PAYOUT_ACCOUNT,
            payee=deliverable.order.seller,
            payer=deliverable.order.seller,
            status=SUCCESS,
        ).first()
        if not transfer_record:
            mark_refunded(deliverable)
            continue
        result = fetch_prefixed("tr_", transfer_record.remote_ids)
        if not result:
            model_admin.message_user(
                request,
                mark_safe(
                    f"Failed reversing transfer for {deliverable_display(deliverable)}. "
                    f"Could not determine remote ID!"
                ),
                level=messages.ERROR,
            )
            continue
        with stripe as stripe_api:
            is_new, new_record = reverse_record(transfer_record)
            if not is_new:
                model_admin.message_user(
                    request,
                    mark_safe(
                        f"Failed reversing transfer for "
                        f"{deliverable_display(deliverable)}. "
                        f"Reverse transfer already exists!"
                    ),
                    level=messages.ERROR,
                )
                continue
            new_record.status = FAILURE
            new_record.save()
            try:
                transfer_info = reverse_transfer(
                    transfer_id=result, total=transfer_record.amount, api=stripe_api
                )
            except Exception as err:
                new_record.response_message = str(err)
                new_record.save()
                model_admin.message_user(
                    request,
                    mark_safe(
                        f"Failed reversing transfer for "
                        f"{deliverable_display(deliverable)}. "
                        f"{err}"
                    ),
                    level=messages.ERROR,
                )
                continue
            new_record.remote_ids.append(transfer_info["id"])
            new_record.status = SUCCESS
            new_record.save()
            mark_refunded(deliverable)


class DeliverableAdmin(admin.ModelAdmin):
    actions = [kill_fraudulent]
    inlines = [CommentInline]
    raw_id_fields = (
        "arbitrator",
        "characters",
        "product",
        "order",
        "invoice",
        "tip_invoice",
    )
    list_display = (
        "id",
        "name",
        "total",
        "tip_total",
        "product_name",
        "magic_link",
        "buyer",
        "seller",
        "created_on",
        "escrow_enabled",
        "status",
        "link",
    )
    list_filter = ("escrow_enabled", "status", "processor")
    readonly_fields = ("link",)

    def get_fields(self, request, obj=...):
        fields = super().get_fields(request, obj)
        fields.insert(0, "link")
        return fields

    def buyer(self, obj):
        return obj.order.buyer

    def seller(self, obj):
        return obj.order.seller

    def total(self, obj):
        return obj.invoice.total()

    def tip_total(self, obj):
        if obj.tip_invoice:
            return f"{obj.tip_invoice.total()}, {obj.tip_invoice.get_status_display()}"

    def product_name(self, obj):
        if not obj.product:
            return ""
        return obj.product.name

    def magic_link(self, obj):
        if obj.order.buyer and obj.order.buyer.guest:
            return format_html(
                f'<a href="/claim-order/{obj.order.id}/'
                f'{obj.order.claim_token}/{obj.id}/">MAGIC LINK</a>'
            )

    def link(self, obj):
        return format_html(
            f'<a href="/sales/{obj.order.seller.username}/sale/{obj.order.id}'
            f'/deliverables/{obj.id}/overview/">visit</a>',
        )


class LineItemAnnotationInline(admin.TabularInline):
    raw_id_fields = ["target"]
    model = LineItemAnnotation


line_fields = (
    "type",
    "priority",
    "amount",
    "frozen_value",
    "percentage",
    "cascade_percentage",
    "back_into_percentage",
    "cascade_amount",
    "destination_user",
    "destination_account",
    "description",
)


class LineItemAdmin(admin.ModelAdmin):
    fields = ("invoice",) + line_fields
    raw_id_fields = ("invoice", "destination_user")
    inlines = [LineItemAnnotationInline]


class LineItemInline(admin.StackedInline):
    fields = line_fields + ("edit_annotations",)
    raw_id_fields = ("destination_user",)
    readonly_fields = ("edit_annotations",)

    def edit_annotations(self, obj):
        if not obj.id:
            return "Save to edit annotations."
        return format_html(
            f'<a href="{reverse("admin:sales_lineitem_change", args=[obj.id])}">Edit '
            f"Annotations</a>"
        )

    model = LineItem


class InvoiceAdmin(admin.ModelAdmin):
    raw_id_fields = ("bill_to", "issued_by", "targets")
    readonly_fields = ("link",)
    list_display = ("id", "type", "issuer", "payer", "status", "total", "link")
    list_filter = ("type", "status")
    inlines = [LineItemInline]

    def get_fields(self, request, obj=...):
        fields = super().get_fields(request, obj=obj)
        fields.insert(0, "link")
        return fields

    def link(self, obj):
        target_user = obj.bill_to or get_anonymous_user()
        return format_html(
            f'<a href="/profile/{target_user.username}/invoice/{obj.id}/">visit</a>',
        )

    def payer(self, obj):
        if obj.bill_to:
            return obj.bill_to.username
        else:
            return "(Artconomy)"

    def issuer(self, obj):
        if obj.issued_by:
            return obj.issued_by.username
        else:
            return "(Artconomy)"


def safe_display_record(record):
    """
    Safely render a transaction name such that no user-written characters are shown and
    it can be HTML embedded in a message with a link.
    """
    return (
        f'<a href="{reverse("admin:sales_transactionrecord_change", args=[record.id])}'
        f'">{record.id}</a> '
        f"{record.get_category_display()} for {record.amount} from "
        f"{record.get_source_display()} to {record.get_destination_display()}"
    )


def reverse_message(source: TransactionRecord, destination: TransactionRecord):
    return (
        f"<p>{safe_display_record(source)} was reversed in "
        f'<a href="'
        f"{reverse('admin:sales_transactionrecord_change', args=[destination.id])}"
        f'">{destination.id}</a></p>'
    )


@admin.action(description="Reverse these transactions")
@atomic
def reverse_transactions(modeladmin, request, queryset):
    existing = {}
    wrong_status = []
    created = {}
    for record in queryset.order_by("created_on"):
        try:
            new, new_record = reverse_record(record)
            if new:
                created[record] = new_record
            else:
                existing[record] = new_record
        except ValueError:
            wrong_status.append(record)
    if created:
        entries = [
            reverse_message(source, destination)
            for source, destination in created.items()
        ]
        message = (
            f"<p>The following reversions were created successfully:</p>"
            f"{''.join(entries)}"
        )
        modeladmin.message_user(
            request, mark_safe(message), level=messages.SUCCESS, extra_tags="safe"
        )
    if existing:
        entries = [
            reverse_message(source, destination)
            for source, destination in existing.items()
        ]
        message = f"<p>The following reversions already existed:</p>{''.join(entries)}"
        modeladmin.message_user(
            request, mark_safe(message), level=messages.WARNING, extra_tags="safe"
        )
    if wrong_status:
        entries = [
            f"<p>{safe_display_record(record)} (status was: {record.get_status_display()})</p>"
            for record in wrong_status
        ]
        message = (
            f"<p>The following records could not be reversed, "
            f"as they were in the wrong status:</p>{''.join(entries)}"
        )
        modeladmin.message_user(request, mark_safe(message), level=messages.ERROR)


class TransactionRecordAdmin(admin.ModelAdmin):
    actions = [reverse_transactions]
    search_fields = (
        "id",
        "payee_username_case",
        "payer_username_case",
        "remote_ids__contains",
    )
    raw_id_fields = ("payer", "payee", "targets")
    list_filter = ("category", "status", "source", "destination")
    list_display = (
        "id",
        "status",
        "category",
        "created_on",
        "finalized_on",
        "paid_by",
        "source",
        "paid_to",
        "destination",
        "amount",
    )
    ordering = ("-created_on",)

    def get_queryset(self, request):
        return TransactionRecord.objects.all().annotate(
            payer_username_case=Collate("payer__username", "und-x-icu"),
            payee_username_case=Collate("payee__username", "und-x-icu"),
        )

    def paid_by(self, obj):
        if obj.payer:
            return obj.payer.username
        else:
            return "(Artconomy)"

    def paid_to(self, obj):
        if obj.payee:
            return obj.payee.username
        else:
            return "(Artconomy)"


class RatingAdmin(admin.ModelAdmin):
    raw_id_fields = ["rater", "target"]


class WebhookRecordAdminForm(forms.ModelForm):
    class Meta:
        model = WebhookRecord
        exclude = []
        widgets = {"secret": TextInput(attrs={"type": "password"})}


class WebhookRecordAdmin(admin.ModelAdmin):
    form = WebhookRecordAdminForm


class RevisionAdmin(admin.ModelAdmin):
    raw_id_fields = ["owner", "deliverable", "file", "preview"]


class StripeLocationAdmin(admin.ModelAdmin):
    readonly_fields = ["stripe_token"]


class StripeReaderForm(ModelForm):
    registration_code = forms.CharField(
        max_length=250,
        help_text="Pairing code given by reader. Only needed on initial creation, and "
        "not stored.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.stripe_token:
            self.fields["location"].disabled = True
            self.fields["registration_code"].disabled = True
            self.fields["registration_code"].required = False

    def save(self, commit: bool = ...):
        self.instance.registration_code = self.cleaned_data["registration_code"]
        return super().save(commit=commit)

    class Meta:
        model = StripeReader
        fields = ["id", "name", "location", "virtual"]
        readonly_fields = ["id", "stripe_token"]


class StripeReaderAdmin(admin.ModelAdmin):
    readonly_fields = ("stripe_token",)
    form = StripeReaderForm


class CreditCardTokenAdmin(admin.ModelAdmin):
    raw_id_fields = ["user"]


class PaypalConfigAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            self.fields[
                "secret"
            ].help_text = "Secret not displayed. Enter a new secret to overwrite."
            self.fields["secret"].required = False

    def clean_secret(self):
        instance = getattr(self, "instance", None)
        if self.cleaned_data["secret"]:
            return self.cleaned_data["secret"]
        elif instance.secret:
            return instance.secret
        raise ValidationError("Secret must be specified.")

    class Meta:
        model = PaypalConfig
        widgets = {
            "secret": forms.PasswordInput,
        }
        fields = "__all__"  # required for Django 3.x


class PaypalConfigAdmin(admin.ModelAdmin):
    raw_id_fields = ["user"]
    form = PaypalConfigAdminForm


class StripeAccountAdmin(admin.ModelAdmin):
    raw_id_fields = ["user"]
    search_fields = ["user_username_case", "user__email", "token"]

    def get_queryset(self, request):
        return StripeAccount.objects.all().annotate(
            user_username_case=Collate("user__username", "und-x-icu"),
        )


admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Deliverable, DeliverableAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(LineItem, LineItemAdmin)
admin.site.register(Revision, RevisionAdmin)
admin.site.register(Promo)
admin.site.register(TransactionRecord, TransactionRecordAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(WebhookRecord, WebhookRecordAdmin)
admin.site.register(ServicePlan)
admin.site.register(StripeLocation, StripeLocationAdmin)
admin.site.register(StripeReader, StripeReaderAdmin)
admin.site.register(CreditCardToken, CreditCardTokenAdmin)
admin.site.register(PaypalConfig, PaypalConfigAdmin)
admin.site.register(StripeAccount, StripeAccountAdmin)
