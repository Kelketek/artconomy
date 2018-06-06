# Generated by Django 2.0.4 on 2018-06-05 18:46

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0040_auto_20180523_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='stars',
            field=models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=3, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='reset_token',
            field=models.CharField(blank=True, default=uuid.uuid4, max_length=36),
        ),
    ]
