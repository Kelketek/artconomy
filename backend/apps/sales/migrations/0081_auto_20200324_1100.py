# Generated by Django 3.0.4 on 2020-03-24 16:00

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0080_auto_20200224_1257"),
    ]

    operations = [
        migrations.AddField(
            model_name="lineitem",
            name="back_into_percentage",
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
