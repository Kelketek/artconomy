# Generated by Django 4.1.5 on 2023-01-25 21:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lib', '0038_alter_tag_name'),
        ('sales', '0155_flip_escrow'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliverable',
            name='escrow_disabled',
        ),
    ]
