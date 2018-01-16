# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-16 16:02
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial_squashed_0023_auto_20180110_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='max_parallel',
            field=models.IntegerField(blank=True, default=0, help_text='How many of these you are willing to have in your backlog at one time.', validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
