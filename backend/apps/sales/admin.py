from django.contrib import admin

# Register your models here.
from apps.lib.admin import CommentInline
from apps.sales.models import Product, Order, PaymentRecord, Revision


class OrderAdmin(admin.ModelAdmin):
    inlines = [
        CommentInline
    ]


admin.site.register(Product, admin.ModelAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(PaymentRecord, admin.ModelAdmin)
admin.site.register(Revision, admin.ModelAdmin)
