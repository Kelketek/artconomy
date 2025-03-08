# Generated by Django 5.1.4 on 2025-01-04 22:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0003_alter_sociallink_options_sociallink_url_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="socialsettings",
            options={"ordering": ("-id",)},
        ),
        migrations.AddField(
            model_name="submission",
            name="removed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="submission_removals",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="submission",
            name="removed_on",
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="submission",
            name="removed_reason",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (0, "Improperly tagged"),
                    (1, "Improperly rated"),
                    (2, "Spammy Content"),
                    (3, "Copyright Claimed"),
                    (4, "Explicit Photographs"),
                    (5, "Illegal Content"),
                ],
                db_index=True,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="socialsettings",
            name="nsfw_promotion",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text="Whether we may promote your NSFW content on social media which allows such content, if applicable.",
            ),
        ),
    ]
