# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-20 16:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0005_order_private"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="category",
        ),
    ]
