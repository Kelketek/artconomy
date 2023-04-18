# Generated by Django 3.1.8 on 2021-05-14 20:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0106_user_stripe_token"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="current_intent",
            field=models.CharField(
                blank=True, db_index=True, default="", max_length=30
            ),
        ),
    ]
