# Generated by Django 4.1.5 on 2023-02-02 00:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0038_alter_tag_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sales', '0156_remove_deliverable_escrow_disabled_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='escrow_upgradable',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='escrow_enabled',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]