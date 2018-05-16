# Generated by Django 2.0.4 on 2018-05-15 18:14

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0035_auto_20180510_1958'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='blocking',
            field=models.ManyToManyField(blank=True, related_name='blocked_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
