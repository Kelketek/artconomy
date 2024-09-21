from apps.profiles.models import (
    ArtistProfile,
    Character,
    RefColor,
    Submission,
    User,
    StaffPowers,
)
from custom_user.admin import EmailUserAdmin
from django.contrib import admin
from django.contrib.admin import ModelAdmin, StackedInline
from django.contrib.admin.options import TabularInline

from apps.profiles.utils import user_query


class StaffPowersInline(StackedInline):
    model = StaffPowers


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
    list_display = ("username", "email", "is_staff", "is_superuser")
    list_filter = ["guest", "artist_mode", "is_staff", "is_superuser"]
    search_fields = ["username_case", "email"]
    raw_id_fields = ["primary_card"]

    def get_inlines(self, request, obj):
        if hasattr(obj, "staff_powers"):
            return [StaffPowersInline]
        return []

    def get_queryset(self, request):
        return user_query()


class SubmissionAdmin(ModelAdmin):
    raw_id_fields = [
        "tags",
        "characters",
        "owner",
        "artists",
        "shared_with",
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
