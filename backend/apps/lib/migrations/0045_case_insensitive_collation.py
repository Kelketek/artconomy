# Generated by Django 5.0.9 on 2024-09-18 14:22
from django.contrib.postgres.operations import CreateCollation
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("lib", "0044_create_shopping_cart"),
    ]

    operations = [
        CreateCollation(
            "case_insensitive",
            provider="icu",
            locale="und-u-ks-level1",
            deterministic=False,
        )
    ]
