# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-18 16:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0006_auto_20180118_1632"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="imageasset",
            name="tags",
        ),
    ]
