# Generated by Django 2.0.3 on 2018-04-02 17:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lib", "0010_auto_20180220_1624"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="event",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notifications",
                to="lib.Event",
            ),
        ),
    ]
