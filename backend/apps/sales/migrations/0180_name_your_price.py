# Generated by Django 4.2.3 on 2023-08-04 16:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0180_merge_20230808_1937"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="name_your_price",
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]