# Generated by Django 3.2.15 on 2022-09-06 16:18

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0143_hide_private"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="stripereader",
            options={"ordering": ("created_on",)},
        ),
        migrations.AddField(
            model_name="stripereader",
            name="created_on",
            field=models.DateTimeField(
                db_index=True, default=django.utils.timezone.now
            ),
        ),
        migrations.AlterField(
            model_name="transactionrecord",
            name="category",
            field=models.IntegerField(
                choices=[
                    (400, "Artconomy Service Fee"),
                    (401, "Escrow hold"),
                    (402, "Escrow release"),
                    (403, "Escrow refund"),
                    (404, "Subscription dues"),
                    (405, "Refund for subscription dues"),
                    (406, "Cash withdrawal"),
                    (408, "Third party fee"),
                    (409, "Premium service bonus"),
                    (410, "Internal Transfer"),
                    (411, "Third party refund"),
                    (415, "Extra item"),
                    (412, "Correction"),
                    (413, "Table Service"),
                    (414, "Tax"),
                    (416, "Manual Payout"),
                    (417, "Payout Reversal"),
                ],
                db_index=True,
            ),
        ),
    ]
