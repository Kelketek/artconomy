# Generated by Django 2.1.5 on 2019-05-16 18:47

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0072_auto_20190507_1726"),
        ("lib", "0021_asset"),
    ]

    operations = [
        migrations.RenameModel("ImageAsset", "Submission"),
    ]
