# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-01 17:58
from __future__ import unicode_literals

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0014_auto_20180131_2118"),
    ]

    operations = [
        migrations.AlterField(
            model_name="refcolor",
            name="character",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="colors",
                to="profiles.Character",
            ),
        ),
        migrations.AlterField(
            model_name="refcolor",
            name="color",
            field=models.CharField(
                max_length=7,
                validators=[django.core.validators.RegexValidator("^#[0-9a-f]{6}$")],
            ),
        ),
    ]
