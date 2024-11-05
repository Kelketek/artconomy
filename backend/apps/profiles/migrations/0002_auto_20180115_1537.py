# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-15 15:37
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0001_initial_squashed_0012_auto_20180110_2157"),
    ]

    operations = [
        migrations.AddField(
            model_name="imageasset",
            name="order",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="outputs",
                to="sales.Order",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="notifications",
            field=models.ManyToManyField(through="lib.Notification", to="lib.Event"),
        ),
        migrations.AddField(
            model_name="user",
            name="primary_card",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="sales.CreditCardToken",
            ),
        ),
    ]
