# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-06 15:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
        ('sales', '0003_remove_product_upfront_percentage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ratingset',
            name='comments',
        ),
        migrations.AddField(
            model_name='order',
            name='characters',
            field=models.ManyToManyField(to='profiles.Character'),
        ),
        migrations.AddField(
            model_name='rating',
            name='comments',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
    ]
