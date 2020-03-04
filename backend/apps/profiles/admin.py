from custom_user.admin import EmailUserAdmin
from django.contrib import admin

from django.contrib.admin import ModelAdmin

from apps.profiles.models import User, Submission, RefColor, ArtistProfile


class ArtconomyUserAdmin(EmailUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Premium Info', {'fields': (
            'landscape_enabled', 'landscape_paid_through', 'portrait_enabled', 'portrait_paid_through',
            'registration_code', 'trust_level',
        )})
    )
    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    list_filter = ['guest', 'artist_mode', 'trust_level']
    search_fields = ['username', 'email']


class SubmissionAdmin(ModelAdmin):
    raw_id_fields = ['tags', 'characters', 'owner', 'artists', 'shared_with', 'file', 'preview']

class ArtistProfileAdmin(ModelAdmin):
    list_display = ('user', 'commissions_disabled', 'commissions_closed', 'max_load', 'load')

class RefColorAdmin(ModelAdmin):
    raw_id_fields = ['character']


admin.site.register(User, ArtconomyUserAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(RefColor, RefColorAdmin)
admin.site.register(ArtistProfile, ArtistProfileAdmin)

