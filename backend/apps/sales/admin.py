from uuid import UUID

from django.conf import settings
from django.contrib import admin

# Register your models here.
from django.utils.html import format_html

from apps.lib.admin import CommentInline
from apps.sales.models import Product, Order, Revision, Promo, TransactionRecord, Rating, Deliverable, LineItem, \
    Invoice, WebhookRecord


class ProductAdmin(admin.ModelAdmin):
    raw_id_fields = ['user', 'owner', 'primary_submission', 'samples', 'tags']


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
    list_display = ('id', 'name', 'product', 'buyer', 'seller', 'shield_protected', 'status', 'link')
    list_filter = ('escrow_disabled', 'status')

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


class LineItemInline(admin.TabularInline):
    model = LineItem


class InvoiceAdmin(admin.ModelAdmin):
    raw_id_fields = ['bill_to', 'targets']
    inlines = [LineItemInline]


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

    def remote_link(self, obj):
        if not obj.remote_id:
            return ''
        try:
            UUID(obj.remote_id)
        except (ValueError, TypeError):
            return ''
        if obj.remote_id.starts_with('pi_'):
            intent_id = obj.remote_id.split(';')[0]
            test_flag = 'test/' if settings.CARD_FLAG else ''
            return format_html(
                f'<a href="https://dashboard.stripe.com/{test_flag}payments/{intent_id}">Stripe Link</a>'
            )
        format_html(
            f'<a href="/sales/{obj.order.seller.username}/sale/{obj.order.id}'
            f'/deliverables/{obj.id}/overview/">visit</a>',
        )


class RatingAdmin(admin.ModelAdmin):
    raw_id_fields = ['rater', 'target']


class WebhookRecordAdmin(admin.ModelAdmin):
    pass


admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Deliverable, DeliverableAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Revision, admin.ModelAdmin)
admin.site.register(Promo)
admin.site.register(TransactionRecord, TransactionRecordAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(WebhookRecord, WebhookRecordAdmin)
