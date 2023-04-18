# Generated by Django 2.1.5 on 2019-03-14 11:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0040_auto_20190314_1134"),
        ("profiles", "0068_auto_20190203_1820"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="registration_code",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="sales.Promo",
            ),
        ),
    ]
