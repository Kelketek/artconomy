from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from apps.lib.models import Comment, Asset, GenericReference


class CommentInline(GenericTabularInline):
    raw_id_fields = ['user', 'parent']
    model = Comment


class AssetAdmin(admin.ModelAdmin):
    raw_id_fields = ['uploaded_by']


class GenericReferenceAdmin(admin.ModelAdmin):
    list_filter = ['content_type']
    search_fields = ['object_id']


class CommentAdmin(admin.ModelAdmin):
    raw_id_fields = ['user', 'parent']


admin.site.register(Comment, CommentAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(GenericReference, GenericReferenceAdmin)
