# Generated by Django 2.0.7 on 2018-07-23 17:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0050_auto_20180719_2128'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='use_load_tracker',
        ),
    ]
