# Generated by Django 3.0.6 on 2020-06-05 15:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0097_auto_20200317_1659"),
    ]

    operations = [
        migrations.AddField(
            model_name="artistprofile",
            name="artist_of_color",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name="artistprofile",
            name="lgbt",
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
