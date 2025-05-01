from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.profiles.models import (
    ArtistProfile,
    Character,
    RefColor,
    Submission,
    User,
    StaffPowers,
    SocialSettings,
    SocialLink,
)
from custom_user.admin import EmailUserAdmin
from django.contrib import admin
from django.contrib.admin import ModelAdmin, StackedInline
from django.contrib.admin.options import TabularInline

from apps.profiles.utils import user_query


class StaffPowersInline(StackedInline):
    model = StaffPowers


class SocialSettingsInline(StackedInline):
    model = SocialSettings


class SocialLinkInline(StackedInline):
    model = SocialLink


class ArtistProfileInline(StackedInline):
    model = ArtistProfile


class ArtconomyUserAdmin(EmailUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "email", "password", "guest_email", "notes")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "email_nulled",
                    "is_staff",
                    "is_superuser",
                    "artist_mode",
                    "verified_adult",
                    "groups",
                    "user_permissions",
                    "guest",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        (
            "Premium Info",
            {
                "fields": (
                    "service_plan",
                    "service_plan_paid_through",
                    "next_service_plan",
                    "registration_code",
                    "discord_id",
                )
            },
        ),
        ("Preferences", {"fields": ("primary_card", "processor_override")}),
        ("Other details", {"fields": ("stars", "featured")}),
    )
    list_display = (
        "username",
        "email",
        "is_staff",
        "is_superuser",
        "profile_link",
        "service_plan",
        "next_service_plan",
    )
    list_filter = [
        "guest",
        "artist_mode",
        "is_staff",
        "is_superuser",
        "service_plan",
        "next_service_plan",
    ]
    search_fields = ["username_case", "email", "guest_email"]
    raw_id_fields = ["primary_card"]

    def profile_link(self, obj):
        return mark_safe(
            f'<a href="{reverse("profile:root_profile_preview", kwargs={"username": obj.username})}">profile</a>'
        )

    def get_inlines(self, request, obj):
        inlines = []
        if hasattr(obj, "staff_powers"):
            inlines.append(StaffPowersInline)
        if hasattr(obj, "artist_profile"):
            inlines.append(ArtistProfileInline)
        inlines.extend([SocialSettingsInline, SocialLinkInline])
        return inlines

    def get_queryset(self, request):
        return user_query()


class SubmissionAdmin(ModelAdmin):
    raw_id_fields = [
        "tags",
        "characters",
        "owner",
        "artists",
        "shared_with",
        "removed_by",
        "file",
        "preview",
        "revision",
        "deliverable",
    ]


class ArtistProfileAdmin(ModelAdmin):
    list_display = (
        "user",
        "commissions_disabled",
        "commissions_closed",
        "max_load",
        "load",
    )


class RefColorAdmin(ModelAdmin):
    raw_id_fields = ["character"]


class InlineRefColor(TabularInline):
    model = RefColor


class CharacterAdmin(ModelAdmin):
    inlines = [InlineRefColor]
    raw_id_fields = ["primary_submission", "user", "tags", "shared_with"]


admin.site.register(User, ArtconomyUserAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(RefColor, RefColorAdmin)
admin.site.register(ArtistProfile, ArtistProfileAdmin)
admin.site.register(Character, CharacterAdmin)
