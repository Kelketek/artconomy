# Generated by Django 2.0.2 on 2018-03-05 23:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0016_user_biography"),
    ]

    operations = [
        migrations.AlterField(
            model_name="character",
            name="open_requests",
            field=models.BooleanField(
                default=False,
                help_text="Allow others to request commissions with my character, such as for gifts.",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="commissions_closed",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text="When enabled, no one may commission you.",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="primary_card",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="sales.CreditCardToken",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="primary_character",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="profiles.Character",
            ),
        ),
    ]
