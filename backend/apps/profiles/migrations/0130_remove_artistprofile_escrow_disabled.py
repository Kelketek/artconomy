# Generated by Django 4.1.5 on 2023-01-25 21:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0038_alter_tag_name'),
        ('profiles', '0129_flip_escrow'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artistprofile',
            name='escrow_disabled',
        ),
    ]
