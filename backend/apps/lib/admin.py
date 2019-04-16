from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from apps.lib.models import Comment, Asset


class CommentInline(GenericTabularInline):
    raw_id_fields = ['user', 'parent']
    model = Comment


class AssetAdmin(admin.ModelAdmin):
    raw_id_fields = ['uploaded_by']


admin.site.register(Comment, admin.ModelAdmin)
admin.site.register(Asset, AssetAdmin)
