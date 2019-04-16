from django.contrib import admin

# Register your models here.
from apps.lib.admin import CommentInline
from apps.sales.models import Product, Order, Revision, Promo, TransactionRecord, Rating


class OrderAdmin(admin.ModelAdmin):
    inlines = [
        CommentInline
    ]
    raw_id_fields = ['buyer', 'seller', 'product', 'arbitrator', 'characters']
    list_display = ('product', 'buyer', 'seller', 'price', 'shield_protected', 'status')
    list_filter = ('escrow_disabled', 'status')

    def shield_protected(self, obj):
        return not obj.escrow_disabled


class TransactionRecordAdmin(admin.ModelAdmin):
    raw_id_fields = ['payer', 'payee']
    list_display = ('id', 'status', 'payer', 'source', 'payee', 'destination', 'amount')
    ordering = ('-created_on',)


class RatingAdmin(admin.ModelAdmin):
    raw_id_fields = ['rater', 'target']

admin.site.register(Product, admin.ModelAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Revision, admin.ModelAdmin)
admin.site.register(Promo)
admin.site.register(TransactionRecord, TransactionRecordAdmin)
admin.site.register(Rating, RatingAdmin)
