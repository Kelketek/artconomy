# Generated by Django 2.0.8 on 2018-09-19 19:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0056_auto_20180919_1811"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="has_products",
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
