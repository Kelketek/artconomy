# Generated by Django 3.0.4 on 2020-03-24 17:43

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0083_auto_20200324_1231"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="transactionrecord",
            name="content_type",
        ),
        migrations.RemoveField(
            model_name="transactionrecord",
            name="object_id",
        ),
    ]
