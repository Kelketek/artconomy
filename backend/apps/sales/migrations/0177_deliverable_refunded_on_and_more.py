# Generated by Django 4.2 on 2023-05-06 19:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0176_remove_deliverable_commission_info"),
    ]

    operations = [
        migrations.AddField(
            model_name="deliverable",
            name="refunded_on",
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name="deliverable",
            name="tip_invoice",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="tipped_deliverables",
                to="sales.invoice",
            ),
        ),
    ]