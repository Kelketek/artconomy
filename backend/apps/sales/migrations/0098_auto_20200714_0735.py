# Generated by Django 3.0.6 on 2020-07-14 12:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0097_fix_revision_subscriptions"),
    ]

    operations = [
        migrations.AddField(
            model_name="deliverable",
            name="product",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="deliverables",
                to="sales.Product",
            ),
        ),
        migrations.AlterField(
            model_name="transactionrecord",
            name="auth_code",
            field=models.CharField(blank=True, db_index=True, default="", max_length=6),
        ),
    ]
