# Generated by Django 3.2.16 on 2022-11-15 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0126_merge_20221103_1021'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='discord_id',
            field=models.CharField(db_index=True, default='', max_length=30),
        ),
    ]
