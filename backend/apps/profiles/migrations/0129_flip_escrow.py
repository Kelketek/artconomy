# Generated by Django 4.1.5 on 2023-01-25 20:35

from django.db import migrations
from django.db.models import Q


def forward_boolean(apps, schema):
    ArtistProfile = apps.get_model("profiles", "ArtistProfile")
    ArtistProfile.objects.update(escrow_enabled=Q(escrow_disabled=False))


def reverse_boolean(apps, schema):
    ArtistProfile = apps.get_model("profiles", "ArtistProfile")
    ArtistProfile.objects.update(escrow_disabled=Q(escrow_enabled=False))


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0128_remove_user_trust_level_artistprofile_escrow_enabled"),
    ]

    operations = [migrations.RunPython(forward_boolean, reverse_code=reverse_boolean)]
