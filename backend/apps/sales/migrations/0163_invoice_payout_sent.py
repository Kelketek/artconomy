# Generated by Django 4.1.7 on 2023-02-21 19:29

import django.db.models.deletion
import djmoney.models.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("lib", "0038_alter_tag_name"),
        ("sales", "0162_set_finalized_on"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoice",
            name="payout_sent",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name="invoice",
            name="payout_available",
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
