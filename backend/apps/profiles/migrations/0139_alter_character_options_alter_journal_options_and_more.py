# Generated by Django 4.2.10 on 2024-03-06 21:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0138_user_email_nulled_alter_character_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="character",
            options={"ordering": ("-created_on",)},
        ),
        migrations.AlterModelOptions(
            name="journal",
            options={"ordering": ("-created_on",)},
        ),
        migrations.AlterModelOptions(
            name="user",
            options={"ordering": ("-date_joined",)},
        ),
    ]