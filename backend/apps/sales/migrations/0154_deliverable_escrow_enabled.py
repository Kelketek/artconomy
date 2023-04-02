# Generated by Django 4.1.5 on 2023-01-25 20:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lib', '0038_alter_tag_name'),
        ('sales', '0153_auto_20230103_1759'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverable',
            name='escrow_enabled',
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]