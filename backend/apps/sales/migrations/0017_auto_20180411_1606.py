# Generated by Django 2.0.3 on 2018-04-11 16:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0016_charactertransfer"),
    ]

    operations = [
        migrations.AddField(
            model_name="charactertransfer",
            name="saved_name",
            field=models.CharField(blank=True, default="", max_length=150),
        ),
        migrations.AlterField(
            model_name="charactertransfer",
            name="character",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="profiles.Character",
            ),
        ),
    ]
