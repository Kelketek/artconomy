# Generated by Django 3.2.13 on 2022-07-10 12:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0138_merge_20220707_1021"),
    ]

    operations = [
        migrations.AlterField(
            model_name="creditcardtoken",
            name="stripe_token",
            field=models.CharField(
                blank=True, db_index=True, default=None, max_length=50, null=True
            ),
        ),
    ]
