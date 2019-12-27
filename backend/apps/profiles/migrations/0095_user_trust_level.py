# Generated by Django 2.2.1 on 2019-12-26 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0094_conversation_last_activity'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='trust_level',
            field=models.IntegerField(choices=[(0, 'Normal'), (1, 'Verified')], db_index=True, default=0),
        ),
    ]