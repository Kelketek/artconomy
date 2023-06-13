# Generated by Django 4.2 on 2023-04-15 19:31

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lib", "0040_alter_event_type_alter_subscription_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="Note",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_on",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
                ("text", models.TextField()),
                (
                    "hash",
                    models.BinaryField(
                        db_index=True, default=b"", max_length=32, unique=True
                    ),
                ),
            ],
        ),
    ]