# Generated by Django 2.1.5 on 2019-05-16 18:48

import apps.profiles.models
from django.conf import settings
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0073_auto_20190516_1847'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_profiles_submission', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(db_index=True, max_length=40, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator(), apps.profiles.models.banned_named_validator, apps.profiles.models.banned_prefix_validator]),
        ),
    ]
