# Generated by Django 2.2.1 on 2019-06-10 18:03

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0076_user_authorize_token"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArtistProfile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        related_name="artist_profile",
                    ),
                ),
                ("load", models.IntegerField(default=0)),
                (
                    "max_load",
                    models.IntegerField(
                        default=10,
                        help_text="How much work you're willing to take on at once "
                        "(for artists)",
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                (
                    "bank_account_status",
                    models.IntegerField(
                        blank=True,
                        choices=[
                            (0, "Unset"),
                            (1, "Has US Bank account"),
                            (2, "No US Bank account"),
                        ],
                        db_index=True,
                        default=0,
                    ),
                ),
                (
                    "commissions_closed",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="When enabled, no one may commission you.",
                    ),
                ),
                (
                    "commissions_disabled",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="Internal check for commissions that prevents "
                        "taking on more work when max load is exceeded.",
                    ),
                ),
                ("has_products", models.BooleanField(db_index=True, default=False)),
                ("escrow_disabled", models.BooleanField(db_index=True, default=False)),
                ("auto_withdraw", models.BooleanField(default=True)),
                ("dwolla_url", models.URLField(blank=True, default="")),
                (
                    "commission_info",
                    models.CharField(blank=True, default="", max_length=5000),
                ),
            ],
        ),
    ]
