# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-25 15:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0010_auto_20180125_1502"),
        ("lib", "0009_auto_20180125_1512"),
    ]

    database_operations = []

    state_operations = [
        migrations.AlterField(
            "Character", "tags", field=models.ManyToManyField(to="lib.Tag")
        ),
        migrations.AlterField(
            "ImageAsset", "tags", field=models.ManyToManyField(to="lib.Tag")
        ),
        migrations.DeleteModel("Tag"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations, state_operations=state_operations
        )
    ]
