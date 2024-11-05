# Generated by Django 5.1.2 on 2024-11-04 22:19

import apps.profiles.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("lib", "0003_initial"),
        ("profiles", "0001_initial"),
        ("sales", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="next_service_plan",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="future_users",
                to="sales.serviceplan",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="notifications",
            field=models.ManyToManyField(through="lib.Notification", to="lib.event"),
        ),
        migrations.AddField(
            model_name="user",
            name="nsfw_blacklist",
            field=models.ManyToManyField(
                related_name="nsfw_blacklisting_users", to="lib.tag"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="primary_card",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="sales.creditcardtoken",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="referred_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="referrals",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="registration_code",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="sales.promo",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="service_plan",
            field=models.ForeignKey(
                blank=True,
                default=apps.profiles.models.default_plan,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="current_users",
                to="sales.serviceplan",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.permission",
                verbose_name="user permissions",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="watching",
            field=models.ManyToManyField(
                blank=True, related_name="watched_by", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="artistprofile",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="artist_profile",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="artisttag",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="character",
            name="shared_with",
            field=models.ManyToManyField(
                blank=True,
                related_name="shared_characters",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="character",
            name="tags",
            field=models.ManyToManyField(
                blank=True, related_name="characters", to="lib.tag"
            ),
        ),
        migrations.AddField(
            model_name="character",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="characters",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="attribute",
            name="character",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attributes",
                to="profiles.character",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="primary_character",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="profiles.character",
            ),
        ),
        migrations.AddField(
            model_name="charactertag",
            name="character",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="profiles.character"
            ),
        ),
        migrations.AddField(
            model_name="conversationparticipant",
            name="conversation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="message_record",
                to="profiles.conversation",
            ),
        ),
        migrations.AddField(
            model_name="conversationparticipant",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="message_record",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="conversation",
            name="participants",
            field=models.ManyToManyField(
                blank=True,
                related_name="conversations",
                through="profiles.ConversationParticipant",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="favorite",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="journal",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="journals",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="refcolor",
            name="character",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="colors",
                to="profiles.character",
            ),
        ),
        migrations.AddField(
            model_name="sociallink",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="social_links",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="socialsettings",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="social_settings",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="staffpowers",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="staff_powers",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="submission",
            name="artists",
            field=models.ManyToManyField(
                blank=True,
                related_name="art",
                through="profiles.ArtistTag",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="submission",
            name="characters",
            field=models.ManyToManyField(
                blank=True,
                related_name="submissions",
                through="profiles.CharacterTag",
                to="profiles.character",
            ),
        ),
        migrations.AddField(
            model_name="submission",
            name="deliverable",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="outputs",
                to="sales.deliverable",
            ),
        ),
        migrations.AddField(
            model_name="submission",
            name="file",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="full_%(app_label)s_%(class)s",
                to="lib.asset",
            ),
        ),
        migrations.AddField(
            model_name="submission",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="owned_%(app_label)s_%(class)s",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="submission",
            name="preview",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="preview_%(app_label)s_%(class)s",
                to="lib.asset",
            ),
        ),
        migrations.AddField(
            model_name="submission",
            name="revision",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="submissions",
                to="sales.revision",
            ),
        ),
        migrations.AddField(
            model_name="submission",
            name="shared_with",
            field=models.ManyToManyField(
                blank=True,
                related_name="shared_submissions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="submission",
            name="tags",
            field=models.ManyToManyField(
                blank=True, related_name="submissions", to="lib.tag"
            ),
        ),
        migrations.AddField(
            model_name="favorite",
            name="submission",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="profiles.submission",
            ),
        ),
        migrations.AddField(
            model_name="charactertag",
            name="submission",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="profiles.submission"
            ),
        ),
        migrations.AddField(
            model_name="character",
            name="primary_submission",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="profiles.submission",
            ),
        ),
        migrations.AddField(
            model_name="artisttag",
            name="submission",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="profiles.submission"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="favorites",
            field=models.ManyToManyField(
                blank=True,
                related_name="favorites",
                through="profiles.Favorite",
                to="profiles.submission",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="attribute",
            unique_together={("key", "character")},
        ),
        migrations.AlterUniqueTogether(
            name="favorite",
            unique_together={("user", "submission")},
        ),
        migrations.AlterUniqueTogether(
            name="character",
            unique_together={("name", "user")},
        ),
    ]
