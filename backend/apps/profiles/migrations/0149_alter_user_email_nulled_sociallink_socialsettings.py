# Generated by Django 5.1.1 on 2024-09-28 15:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0148_alter_user_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email_nulled",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text="Drop all emails that would otherwise be sent to this user. Will reset to off if the email address is updated by the user.",
            ),
        ),
        migrations.CreateModel(
            name="SocialLink",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "site_name",
                    models.CharField(
                        db_index=True,
                        default="",
                        help_text="The name of the site your account is on.",
                        max_length=25,
                    ),
                ),
                (
                    "identifier",
                    models.CharField(
                        default="",
                        help_text="Username or URL of account on site.",
                        max_length=100,
                    ),
                ),
                (
                    "comment",
                    models.CharField(
                        default="",
                        help_text="Short comment, such as 'Cat Photo Account'.",
                        max_length=30,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="social_links",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SocialSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "allow_promotion",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="Whether we may promote you and your content in particular on social media. We will link/ping your account on the relevant service when we do this.",
                    ),
                ),
                (
                    "allow_site_promotion",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="Whether we may use assets you upload to promote the site in a general sense-- such as using screenshots with your content",
                    ),
                ),
                (
                    "nsfw_promotion",
                    models.BooleanField(
                        db_index=True,
                        default=True,
                        help_text="Whether we may promote your NSFW content on social media which allows such content, if applicable.",
                    ),
                ),
                (
                    "quick_description",
                    models.CharField(
                        default="",
                        help_text="A quick description of your art/style/offerings, for use by our social media specialist when promoting you.",
                        max_length=150,
                    ),
                ),
                (
                    "promotion_notes",
                    models.TextField(
                        help_text="Any notes/requests/conditions on using your content in promotions.",
                        max_length=500,
                    ),
                ),
                (
                    "display_socials",
                    models.BooleanField(
                        db_index=True,
                        default=True,
                        help_text="Whether to display your socials on your profile.",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="social_settings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]