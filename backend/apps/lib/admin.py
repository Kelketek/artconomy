from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from apps.lib.models import Comment


class CommentInline(GenericTabularInline):
    model = Comment


admin.site.register(Comment, admin.ModelAdmin)
