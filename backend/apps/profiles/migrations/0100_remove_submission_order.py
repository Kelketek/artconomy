# Generated by Django 3.0.4 on 2020-03-15 16:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0099_submission_deliverable"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="submission",
            name="order",
        ),
    ]
