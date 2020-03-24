from django.contrib import admin

# Register your models here.
from apps.lib.admin import CommentInline
from apps.sales.models import Product, Order, Revision, Promo, TransactionRecord, Rating


class ProductAdmin(admin.ModelAdmin):
    raw_id_fields = ['user', 'owner', 'primary_submission', 'samples', 'tags']


class OrderAdmin(admin.ModelAdmin):
    inlines = [
        CommentInline
    ]
    raw_id_fields = ['buyer', 'seller', 'product', 'arbitrator', 'characters']
    list_display = ('product', 'buyer', 'seller', 'shield_protected', 'status')
    list_filter = ('escrow_disabled', 'status')

    def shield_protected(self, obj):
        return not obj.escrow_disabled


class TransactionRecordAdmin(admin.ModelAdmin):
    raw_id_fields = ['payer', 'payee', 'targets']
    list_display = ('id', 'status', 'category', 'paid_by', 'source', 'paid_to', 'destination', 'amount')
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

admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Revision, admin.ModelAdmin)
admin.site.register(Promo)
admin.site.register(TransactionRecord, TransactionRecordAdmin)
admin.site.register(Rating, RatingAdmin)
