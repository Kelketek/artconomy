from uuid import UUID

from django import forms
from django.conf import settings
from django.contrib import admin

# Register your models here.
from django.forms import ModelForm
from django.urls import reverse
from django.utils.html import format_html

from apps.lib.admin import CommentInline
from apps.sales.models import Product, Order, Revision, Promo, TransactionRecord, Rating, Deliverable, LineItem, \
    Invoice, WebhookRecord, LineItemAnnotation, ServicePlan, StripeLocation, StripeReader, CreditCardToken


class ProductAdmin(admin.ModelAdmin):
    raw_id_fields = ['user', 'owner', 'primary_submission', 'samples', 'tags', 'file', 'preview']


class OrderAdmin(admin.ModelAdmin):
    inlines = [
        CommentInline
    ]
    raw_id_fields = ['buyer', 'seller']
    list_display = ('buyer', 'seller')

    def shield_protected(self, obj):
        return not obj.escrow_disabled


class DeliverableAdmin(admin.ModelAdmin):
    inlines = [
        CommentInline
    ]
    raw_id_fields = ['arbitrator', 'characters', 'product', 'order', 'invoice']
    list_display = ('id', 'name', 'product', 'buyer', 'seller', 'created_on', 'shield_protected', 'status', 'link')
    list_filter = ('escrow_disabled', 'status', 'processor')

    def buyer(self, obj):
        return obj.order.buyer

    def seller(self, obj):
        return obj.order.seller

    def shield_protected(self, obj):
        return not obj.escrow_disabled

    def link(self, obj):
        return format_html(
            f'<a href="/sales/{obj.order.seller.username}/sale/{obj.order.id}'
            f'/deliverables/{obj.id}/overview/">visit</a>',
        )


class LineItemAnnotationInline(admin.TabularInline):
    raw_id_fields = ['target']
    model = LineItemAnnotation


line_fields = (
    'type', 'priority', 'amount', 'frozen_value', 'percentage', 'cascade_percentage', 'cascade_amount', 'back_into_percentage',
    'destination_user', 'destination_account', 'description',
)


class LineItemAdmin(admin.ModelAdmin):
    fields = ('invoice',) + line_fields
    raw_id_fields = ('invoice', 'destination_user')
    inlines = [LineItemAnnotationInline]


class LineItemInline(admin.StackedInline):
    fields = line_fields + ('edit_annotations',)
    raw_id_fields = ('destination_user',)
    readonly_fields = ('edit_annotations',)

    def edit_annotations(self, obj):
        if not obj.id:
            return 'Save to edit annotations.'
        return format_html(f'<a href="{reverse("admin:sales_lineitem_change", args=[obj.id])}">Edit Annotations</a>')

    model = LineItem


class InvoiceAdmin(admin.ModelAdmin):
    raw_id_fields = ['bill_to', 'targets']
    list_display = ('id', 'bill_to', 'status', 'total', 'link')
    list_filter = ['status']
    inlines = [LineItemInline]

    def link(self, obj):
        from apps.profiles.models import User
        target_user = obj.bill_to or User.objects.first()
        return format_html(
            f'<a href="/profile/{target_user.username}/invoices/{obj.id}/">visit</a>',
        )


class TransactionRecordAdmin(admin.ModelAdmin):
    raw_id_fields = ['payer', 'payee', 'targets']
    list_display = ('id', 'status', 'category', 'created_on', 'paid_by', 'source', 'paid_to', 'destination', 'amount')
    ordering = ('-created_on',)

    def paid_by(self, obj):
        if obj.payer:
            return obj.payer.username
        else:
            return '(Artconomy)'

    def paid_to(self, obj):
        if obj.payee:
            return obj.payee.username
        else:
            return '(Artconomy)'


class RatingAdmin(admin.ModelAdmin):
    raw_id_fields = ['rater', 'target']


class WebhookRecordAdmin(admin.ModelAdmin):
    pass


class RevisionAdmin(admin.ModelAdmin):
    raw_id_fields = ['owner', 'deliverable', 'file', 'preview']


class StripeLocationAdmin(admin.ModelAdmin):
    readonly_fields = ['stripe_token']


class StripeReaderForm(ModelForm):
    registration_code = forms.CharField(
        max_length=250,
        help_text="Pairing code given by reader. Only needed on initial creation, and not stored.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.stripe_token:
            self.fields['location'].disabled = True
            self.fields['registration_code'].disabled = True
            self.fields['registration_code'].required = False

    def save(self, commit: bool = ...):
        self.instance.registration_code = self.cleaned_data['registration_code']
        return super().save(commit=commit)

    class Meta:
        model = StripeReader
        fields = ['id', 'name', 'location', 'virtual']
        readonly_fields = ['id', 'stripe_token']


class StripeReaderAdmin(admin.ModelAdmin):
    readonly_fields = ('stripe_token',)
    form = StripeReaderForm


class CreditCardTokenAdmin(admin.ModelAdmin):
    raw_id_fields = ['user']


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
