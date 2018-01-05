# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-05 17:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0007_auto_20180102_2215'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='favorites',
            field=models.ManyToManyField(blank=True, related_name='favorited_by', to='profiles.ImageAsset'),
        ),
    ]
