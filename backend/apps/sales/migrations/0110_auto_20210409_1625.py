# Generated by Django 3.1.7 on 2021-04-09 21:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0109_webhookrecord"),
    ]

    operations = [
        migrations.AlterField(
            model_name="deliverable",
            name="processor",
            field=models.CharField(
                choices=[("authorize", "EVO Authorize.net"), ("stripe", "Stripe")],
                db_index=True,
                default="authorize",
                max_length=24,
            ),
        ),
    ]
