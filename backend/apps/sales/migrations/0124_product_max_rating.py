# Generated by Django 3.2.9 on 2021-12-30 18:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0123_remove_transactionrecord_remote_id"),
        ("profiles", "0116_migrate_submission_order_inputs"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="max_rating",
            field=models.IntegerField(
                choices=[
                    (0, "Clean/Safe for work"),
                    (1, "Risque/mature, not adult content but not safe for work"),
                    (2, "Adult content, not safe for work"),
                    (3, "Offensive/Disturbing to most viewers, not safe for work"),
                ],
                db_index=True,
                default=0,
                help_text="The maximum content rating you will support for this "
                "product.",
            ),
        ),
    ]
