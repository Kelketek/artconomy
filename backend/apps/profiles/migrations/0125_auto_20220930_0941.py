# Generated by Django 3.2.15 on 2022-09-30 14:41

import apps.profiles.models
import django.contrib.auth.validators
import django.contrib.postgres.fields.citext
from django.contrib.postgres.operations import CITextExtension
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0145_auto_20220911_1140'),
        ('profiles', '0124_auto_20220603_2013'),
    ]

    operations = [
        CITextExtension(),
        migrations.AlterField(
            model_name='user',
            name='service_plan',
            field=models.ForeignKey(blank=True, default=apps.profiles.models.default_plan, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='current_users', to='sales.serviceplan'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=django.contrib.postgres.fields.citext.CICharField(db_index=True, max_length=40, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator(), apps.profiles.models.banned_named_validator, apps.profiles.models.banned_prefix_validator]),
        ),
    ]
