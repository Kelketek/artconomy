# Generated by Django 2.2.1 on 2019-06-05 14:18

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0045_auto_20190603_1538"),
    ]

    operations = [
        migrations.RenameField(
            model_name="creditcardtoken",
            old_name="payment_id",
            new_name="token",
        ),
    ]
