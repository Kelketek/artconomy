# Generated by Django 4.1.7 on 2023-02-28 17:36

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("sales", "0166_deliverable_term_billed_alter_invoice_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="deliverable",
            name="auto_cancel_on",
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
    ]
