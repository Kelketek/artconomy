# Generated by Django 5.0.7 on 2024-08-04 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sales", "0191_deliverable_auto_cancel_disabled"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="customer_display_name",
            field=models.CharField(default="", max_length=40),
        ),
    ]