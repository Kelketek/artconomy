# Generated by Django 2.0.8 on 2018-09-21 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0034_auto_20180919_2129'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='available',
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]
