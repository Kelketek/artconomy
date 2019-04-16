# Generated by Django 2.2.1 on 2019-11-19 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0092_user_guest_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='artist_mode',
            field=models.BooleanField(blank=True, db_index=True, default=False, help_text='Enable Artist functionality'),
        ),
    ]