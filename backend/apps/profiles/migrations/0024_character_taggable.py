# Generated by Django 2.0.3 on 2018-04-04 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0023_user_load'),
    ]

    operations = [
        migrations.AddField(
            model_name='character',
            name='taggable',
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]
