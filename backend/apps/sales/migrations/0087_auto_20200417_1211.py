# Generated by Django 3.0.5 on 2020-04-17 17:11

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0086_auto_20200328_0705"),
    ]

    operations = [
        migrations.AddField(
            model_name="transactionrecord",
            name="auth_code",
            field=models.CharField(db_index=True, default="", max_length=6),
        ),
    ]
