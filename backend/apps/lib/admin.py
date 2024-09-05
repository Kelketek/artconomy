from apps.lib.models import Asset, Comment, GenericReference
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from apps.sales.models import WebhookEventRecord


class CommentInline(GenericTabularInline):
    raw_id_fields = ["user", "parent"]
    model = Comment


class AssetAdmin(admin.ModelAdmin):
    raw_id_fields = ["uploaded_by"]


class GenericReferenceAdmin(admin.ModelAdmin):
    list_filter = ["content_type"]
    search_fields = ["object_id"]
    readonly_fields = ["target"]


class CommentAdmin(admin.ModelAdmin):
    raw_id_fields = ["user", "parent"]


class WebhookEventRecordAdmin(admin.ModelAdmin):
    pass


admin.site.register(Comment, CommentAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(GenericReference, GenericReferenceAdmin)
admin.site.register(WebhookEventRecord, WebhookEventRecordAdmin)
