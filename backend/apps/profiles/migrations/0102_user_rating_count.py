# Generated by Django 3.0.6 on 2020-07-11 14:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0101_merge_20200612_1459"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="rating_count",
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
