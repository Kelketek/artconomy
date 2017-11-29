# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-15 15:57
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sales', '0010_auto_20171112_0005'),
    ]

    operations = [
        migrations.CreateModel(
            name='Revision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(0, 'Clean/Safe for work'), (1, 'Risque/mature, not adult content but not safe for work'), (2, 'Adult content, not safe for work')], db_index=True, default=0)),
                ('file', easy_thumbnails.fields.ThumbnailerImageField(upload_to='art/%Y/%m/%d/')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.Order')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_sales_revision', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
