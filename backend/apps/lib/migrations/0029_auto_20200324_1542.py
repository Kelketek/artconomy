# Generated by Django 3.0.4 on 2020-03-24 20:42

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("lib", "0028_genericreference"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="genericreference",
            unique_together={("object_id", "content_type")},
        ),
    ]
