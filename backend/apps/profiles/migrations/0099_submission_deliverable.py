# Generated by Django 3.0.4 on 2020-03-15 02:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0097_auto_20200317_1659"),
    ]

    operations = [
        migrations.AddField(
            model_name="submission",
            name="deliverable",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="outputs",
                to="sales.Deliverable",
            ),
        ),
    ]
