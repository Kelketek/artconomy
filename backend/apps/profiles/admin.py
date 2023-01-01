from custom_user.admin import EmailUserAdmin
from django.contrib import admin

from django.contrib.admin import ModelAdmin
from django.contrib.admin.options import TabularInline

from apps.profiles.models import User, Submission, RefColor, ArtistProfile, Character


class ArtconomyUserAdmin(EmailUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'guest_email', 'notes')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions', 'guest')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Premium Info', {'fields': (
            'service_plan', 'service_plan_paid_through',
            'next_service_plan',
            'registration_code', 'trust_level',
        )}),
        ('Preferences', {'fields': ('primary_card', 'processor_override')})
    )
    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    list_filter = ['guest', 'artist_mode', 'trust_level']
    search_fields = ['username', 'email']
    raw_id_fields = ['primary_card']


class SubmissionAdmin(ModelAdmin):
    raw_id_fields = [
        'tags', 'characters', 'owner', 'artists', 'shared_with', 'file', 'preview', 'revision', 'deliverable',
    ]


class ArtistProfileAdmin(ModelAdmin):
    list_display = ('user', 'commissions_disabled', 'commissions_closed', 'max_load', 'load')


class RefColorAdmin(ModelAdmin):
    raw_id_fields = ['character']


class InlineRefColor(TabularInline):
    model = RefColor


class CharacterAdmin(ModelAdmin):
    inlines = [InlineRefColor]
    raw_id_fields = ['primary_submission', 'user', 'tags', 'shared_with']


admin.site.register(User, ArtconomyUserAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(RefColor, RefColorAdmin)
admin.site.register(ArtistProfile, ArtistProfileAdmin)
admin.site.register(Character, CharacterAdmin)
