# Generated by Django 2.0.3 on 2018-03-27 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0020_auto_20180327_1506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='artist_tagging_disabled',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
