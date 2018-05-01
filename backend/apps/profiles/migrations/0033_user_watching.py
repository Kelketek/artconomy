# Generated by Django 2.0.4 on 2018-04-30 19:50

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0032_auto_20180430_1525'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='watching',
            field=models.ManyToManyField(blank=True, related_name='watched_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
