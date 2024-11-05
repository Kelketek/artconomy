# Generated by Django 5.1.2 on 2024-11-04 22:19

import apps.lib.abstract_models
import apps.profiles.models
import django.contrib.auth.validators
import django.core.validators
import django.utils.timezone
import short_stuff.django.models
import short_stuff.lib
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("lib", "0001_initial"),
    ]

    replaces = [
        ("profiles", "0001_initial_squashed_0012_auto_20180110_2157"),
        ("profiles", "0002_auto_20180115_1537"),
        ("profiles", "0003_auto_20180117_1948"),
        ("profiles", "0004_auto_20180117_1951"),
        ("profiles", "0005_auto_20180118_1516"),
        ("profiles", "0006_auto_20180118_1632"),
        ("profiles", "0007_remove_imageasset_tags"),
        ("profiles", "0008_imageasset_tags"),
        ("profiles", "0009_character_tags"),
        ("profiles", "0010_auto_20180125_1502"),
        ("profiles", "0011_auto_20180125_1524"),
        ("profiles", "0012_auto_20180126_1645"),
        ("profiles", "0013_auto_20180131_1747"),
        ("profiles", "0014_auto_20180131_2118"),
        ("profiles", "0015_auto_20180201_1758"),
        ("profiles", "0016_user_biography"),
        ("profiles", "0017_auto_20180305_2322"),
        ("profiles", "0018_auto_20180322_1643"),
        ("profiles", "0019_auto_20180326_1420"),
        ("profiles", "0020_auto_20180327_1506"),
        ("profiles", "0021_auto_20180327_1734"),
        ("profiles", "0022_auto_20180327_1900"),
        ("profiles", "0023_user_load"),
        ("profiles", "0024_character_taggable"),
        ("profiles", "0025_user_taggable"),
        ("profiles", "0026_auto_20180404_1925"),
        ("profiles", "0027_auto_20180405_1952"),
        ("profiles", "0028_auto_20180405_1954"),
        ("profiles", "0029_character_transfer"),
        ("profiles", "0030_auto_20180424_1832"),
        ("profiles", "0031_auto_20180425_1626"),
        ("profiles", "0032_auto_20180430_1525"),
        ("profiles", "0033_user_watching"),
        ("profiles", "0034_user_commissions_disabled"),
        ("profiles", "0035_auto_20180510_1958"),
        ("profiles", "0036_user_blocking"),
        ("profiles", "0037_auto_20180516_1926"),
        ("profiles", "0038_user_commission_info"),
        ("profiles", "0039_auto_20180521_2202"),
        ("profiles", "0040_auto_20180523_1444"),
        ("profiles", "0041_auto_20180605_1846"),
        ("profiles", "0042_auto_20180612_2023"),
        ("profiles", "0043_auto_20180621_1510"),
        ("profiles", "0044_auto_20180625_1540"),
        ("profiles", "0045_auto_20180625_1631"),
        ("profiles", "0046_imageasset_preview"),
        ("profiles", "0047_journal"),
        ("profiles", "0048_auto_20180713_2019"),
        ("profiles", "0049_auto_20180718_1754"),
        ("profiles", "0050_auto_20180719_2128"),
        ("profiles", "0051_remove_user_use_load_tracker"),
        ("profiles", "0052_user_auto_withdraw"),
        ("profiles", "0053_auto_20180816_2112"),
        ("profiles", "0054_user_escrow_disabled"),
        ("profiles", "0055_auto_20180917_2355"),
        ("profiles", "0056_auto_20180919_1811"),
        ("profiles", "0057_user_has_products"),
        ("profiles", "0058_auto_20180919_1933"),
        ("profiles", "0059_user_avatar_url"),
        ("profiles", "0060_auto_20180919_2059"),
        ("profiles", "0061_user_bank_account_status"),
        ("profiles", "0062_auto_20180929_1440"),
        ("profiles", "0063_user_referred_by"),
        ("profiles", "0064_auto_20181003_1501"),
        ("profiles", "0065_auto_20181003_1532"),
        ("profiles", "0066_user_offered_mailchimp"),
        ("profiles", "0067_auto_20181003_1946"),
        ("profiles", "0068_auto_20190203_1820"),
        ("profiles", "0069_user_registration_code"),
        ("profiles", "0070_message_edited"),
        ("profiles", "0071_auto_20190417_1604"),
        ("profiles", "0071_remove_character_transfer"),
        ("profiles", "0072_auto_20190507_1726"),
        ("profiles", "0073_auto_20190516_1847"),
        ("profiles", "0074_auto_20190516_1848"),
        ("profiles", "0075_auto_20190516_2201"),
        ("profiles", "0076_user_authorize_token"),
        ("profiles", "0077_artistprofile"),
        ("profiles", "0078_auto_20190610_1803"),
        ("profiles", "0079_auto_20190610_1836"),
        ("profiles", "0080_user_artist_mode"),
        ("profiles", "0081_set_artist_mode"),
        ("profiles", "0082_artistprofile_max_rating"),
        ("profiles", "0083_set_max_rating"),
        ("profiles", "0084_merge_20190701_1722"),
        ("profiles", "0085_journal_edited"),
        ("profiles", "0086_message_to_conversation"),
        ("profiles", "0087_set_sender_participant"),
        ("profiles", "0088_conversation_cleanup"),
        ("profiles", "0089_auto_20190725_2023"),
        ("profiles", "0090_auto_20190725_2206"),
        ("profiles", "0091_auto_20191010_1012"),
        ("profiles", "0092_user_guest_email"),
        ("profiles", "0093_auto_20191119_1645"),
        ("profiles", "0094_conversation_last_activity"),
        ("profiles", "0095_user_trust_level"),
        ("profiles", "0096_user_notes"),
        ("profiles", "0097_auto_20200317_1659"),
        ("profiles", "0098_auto_20200605_1051"),
        ("profiles", "0099_submission_deliverable"),
        ("profiles", "0100_remove_submission_order"),
        ("profiles", "0101_merge_20200612_1459"),
        ("profiles", "0102_user_rating_count"),
        ("profiles", "0103_auto_20200711_0959"),
        ("profiles", "0104_user_birthday"),
        ("profiles", "0105_auto_20201230_1041"),
        ("profiles", "0106_subscribe_waitlist_emails"),
        ("profiles", "0106_user_stripe_token"),
        ("profiles", "0107_user_current_intent"),
        ("profiles", "0108_merge_20210820_1049"),
        ("profiles", "0109_auto_20210825_1339"),
        ("profiles", "0110_alter_user_processor"),
        ("profiles", "0111_remove_user_processor"),
        ("profiles", "0112_auto_20210930_1640"),
        ("profiles", "0113_artistprofile_public_queue"),
        ("profiles", "0114_remove_portrait"),
        ("profiles", "0115_submission_revision"),
        ("profiles", "0116_migrate_submission_order_inputs"),
        ("profiles", "0117_remove_artistprofile_max_rating"),
        ("profiles", "0118_service_plan_fields"),
        ("profiles", "0119_alter_user_landscape_enabled"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArtistProfile",
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
                ("load", models.IntegerField(default=0)),
                (
                    "max_load",
                    models.IntegerField(
                        default=10,
                        help_text="How much work you're willing to take on at once (for artists)",
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                (
                    "bank_account_status",
                    models.IntegerField(
                        blank=True,
                        choices=[
                            (0, "Unset"),
                            (1, "In supported country"),
                            (2, "No supported country"),
                        ],
                        db_index=True,
                        default=0,
                    ),
                ),
                (
                    "commissions_closed",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="When enabled, no one may commission you.",
                    ),
                ),
                (
                    "commissions_disabled",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="Internal check for commissions that prevents taking on more work when max load is exceeded.",
                    ),
                ),
                (
                    "public_queue",
                    models.BooleanField(
                        default=True, help_text="Allow people to see your queue."
                    ),
                ),
                ("has_products", models.BooleanField(db_index=True, default=False)),
                ("escrow_enabled", models.BooleanField(db_index=True, default=True)),
                ("artist_of_color", models.BooleanField(db_index=True, default=False)),
                ("lgbt", models.BooleanField(db_index=True, default=False)),
                ("auto_withdraw", models.BooleanField(default=True)),
                ("dwolla_url", models.URLField(blank=True, default="")),
                (
                    "commission_info",
                    models.CharField(blank=True, default="", max_length=14000),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArtistTag",
            fields=[
                (
                    "id",
                    short_stuff.django.models.ShortCodeField(
                        db_index=True,
                        default=short_stuff.lib.gen_shortcode,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "display_position",
                    models.FloatField(
                        db_index=True,
                        default=apps.profiles.models.get_next_artist_position,
                        unique=True,
                    ),
                ),
                ("hidden", models.BooleanField(db_index=True, default=False)),
            ],
            options={
                "ordering": ("-display_position", "id"),
            },
        ),
        migrations.CreateModel(
            name="Attribute",
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
                ("key", models.CharField(db_index=True, max_length=50)),
                ("value", models.CharField(default="", max_length=100)),
                ("sticky", models.BooleanField(db_index=True, default=False)),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="Character",
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
                    "name",
                    models.CharField(
                        max_length=150,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^[^/\\\\?%&+#@]+$",
                                message="Names may not contain /, \\, ?, #, @, or &.",
                            ),
                            django.core.validators.RegexValidator(
                                "^[^.]", message="Names may not start with a period."
                            ),
                            django.core.validators.RegexValidator(
                                "[^.]$", message="Names may not end with a period."
                            ),
                        ],
                    ),
                ),
                (
                    "description",
                    models.CharField(blank=True, default="", max_length=20000),
                ),
                (
                    "private",
                    models.BooleanField(
                        default=False,
                        help_text="Only show this character to people I have explicitly shared it to.",
                    ),
                ),
                (
                    "open_requests",
                    models.BooleanField(
                        default=False,
                        help_text="Allow others to request commissions with my character, such as for gifts.",
                    ),
                ),
                (
                    "open_requests_restrictions",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Write any particular conditions or requests to be considered when someone else is commissioning a piece with this character. For example, 'This character should only be drawn in Safe for Work Pieces.'",
                        max_length=2000,
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                (
                    "nsfw",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="Used to indicate that this character should not be shown when in SFW mode, and its tags should be excluded based on a user's NSFW blocked tags.",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_on",),
            },
            bases=(models.Model, apps.lib.abstract_models.HitsMixin),
        ),
        migrations.CreateModel(
            name="CharacterTag",
            fields=[
                (
                    "id",
                    short_stuff.django.models.ShortCodeField(
                        db_index=True,
                        default=short_stuff.lib.gen_shortcode,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "display_position",
                    models.FloatField(
                        db_index=True,
                        default=apps.profiles.models.get_next_character_position,
                        unique=True,
                    ),
                ),
                ("hidden", models.BooleanField(db_index=True, default=False)),
                ("reference", models.BooleanField(db_index=True, default=False)),
            ],
            options={
                "ordering": ("-display_position", "id"),
            },
        ),
        migrations.CreateModel(
            name="Conversation",
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
                    "created_on",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
                (
                    "last_activity",
                    models.DateTimeField(db_index=True, default=None, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ConversationParticipant",
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
                ("read", models.BooleanField(db_index=True, default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Favorite",
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
                    "created_on",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
            ],
            options={
                "ordering": ("-created_on",),
            },
        ),
        migrations.CreateModel(
            name="Journal",
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
                ("subject", models.CharField(max_length=150)),
                ("body", models.CharField(max_length=5000)),
                ("edited", models.BooleanField(default=False)),
                ("created_on", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("edited_on", models.DateTimeField(auto_now=True)),
                ("comments_disabled", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ("-created_on",),
            },
        ),
        migrations.CreateModel(
            name="RefColor",
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
                    "color",
                    models.CharField(
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator("^#[0-9a-fA-F]{6}$")
                        ],
                    ),
                ),
                ("note", models.CharField(max_length=100)),
            ],
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
            ],
        ),
        migrations.CreateModel(
            name="StaffPowers",
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
                ("handle_disputes", models.BooleanField(default=False)),
                ("view_social_data", models.BooleanField(default=False)),
                ("view_financials", models.BooleanField(default=False)),
                ("moderate_content", models.BooleanField(default=False)),
                ("moderate_discussion", models.BooleanField(default=False)),
                ("table_seller", models.BooleanField(default=False)),
                ("view_as", models.BooleanField(default=False)),
                ("administrate_users", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Submission",
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
                    "rating",
                    models.IntegerField(
                        choices=[
                            (0, "Clean/Safe for work"),
                            (
                                1,
                                "Risque/mature, not adult content but not safe for work",
                            ),
                            (2, "Adult content, not safe for work"),
                            (
                                3,
                                "Offensive/Disturbing to most viewers, not safe for work",
                            ),
                        ],
                        db_index=True,
                        default=0,
                    ),
                ),
                (
                    "created_on",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
                ("title", models.CharField(blank=True, default="", max_length=100)),
                ("caption", models.CharField(blank=True, default="", max_length=2000)),
                (
                    "private",
                    models.BooleanField(
                        default=False,
                        help_text="Only show this to people I have explicitly shared it to.",
                    ),
                ),
                ("comments_disabled", models.BooleanField(default=False)),
                (
                    "display_position",
                    models.FloatField(
                        db_index=True,
                        default=apps.profiles.models.get_next_submission_position,
                        unique=True,
                    ),
                ),
            ],
            options={
                "ordering": ("created_on",),
                "abstract": False,
            },
            bases=(
                apps.lib.abstract_models.AssetThumbnailMixin,
                models.Model,
                apps.lib.abstract_models.HitsMixin,
            ),
        ),
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        db_index=True,
                        max_length=255,
                        unique=True,
                        verbose_name="email address",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        db_collation="case_insensitive",
                        db_index=True,
                        max_length=40,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator(),
                            apps.profiles.models.banned_named_validator,
                            apps.profiles.models.banned_prefix_validator,
                        ],
                    ),
                ),
                ("favorites_hidden", models.BooleanField(default=False)),
                ("taggable", models.BooleanField(db_index=True, default=True)),
                ("verified_adult", models.BooleanField(db_index=True, default=False)),
                (
                    "authorize_token",
                    models.CharField(db_index=True, default="", max_length=50),
                ),
                (
                    "stripe_token",
                    models.CharField(db_index=True, default="", max_length=50),
                ),
                (
                    "bought_shield_on",
                    models.DateTimeField(
                        blank=True, db_index=True, default=None, null=True
                    ),
                ),
                (
                    "sold_shield_on",
                    models.DateTimeField(
                        blank=True, db_index=True, default=None, null=True
                    ),
                ),
                (
                    "email_nulled",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="Drop all emails that would otherwise be sent to this user. Will reset to off if the email address is updated by the user.",
                    ),
                ),
                (
                    "service_plan_paid_through",
                    models.DateField(blank=True, default=None, null=True),
                ),
                ("birthday", models.DateField(db_index=True, default=None, null=True)),
                ("guest", models.BooleanField(db_index=True, default=False)),
                (
                    "tg_key",
                    models.CharField(
                        db_index=True,
                        default=apps.profiles.models.tg_key_gen,
                        max_length=30,
                    ),
                ),
                (
                    "tg_chat_id",
                    models.CharField(db_index=True, default="", max_length=30),
                ),
                (
                    "discord_id",
                    models.CharField(
                        blank=True, db_index=True, default="", max_length=30
                    ),
                ),
                (
                    "guest_email",
                    models.EmailField(
                        blank=True, db_index=True, default="", max_length=254
                    ),
                ),
                ("avatar_url", models.URLField(blank=True)),
                (
                    "rating",
                    models.IntegerField(
                        choices=[
                            (0, "Clean/Safe for work"),
                            (
                                1,
                                "Risque/mature, not adult content but not safe for work",
                            ),
                            (2, "Adult content, not safe for work"),
                            (
                                3,
                                "Offensive/Disturbing to most viewers, not safe for work",
                            ),
                        ],
                        db_index=True,
                        default=0,
                        help_text="Shows the maximum rating to display. By setting this to anything other than general, you certify that you are of legal age to view adult content in your country.",
                    ),
                ),
                (
                    "sfw_mode",
                    models.BooleanField(
                        default=False,
                        help_text="Enable this to only display clean art. Useful if temporarily browsing from a location where adult content is not appropriate.",
                    ),
                ),
                (
                    "artist_mode",
                    models.BooleanField(
                        blank=True,
                        db_index=True,
                        default=False,
                        help_text="Enable Artist functionality",
                    ),
                ),
                (
                    "delinquent",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="Enabled when a user's account is in arrears beyond the grace period.",
                    ),
                ),
                (
                    "featured",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="Enabling features all of a user's products and puts them in the featured users listing. This is mostly managed by a scheduled task, but it can be manually triggered here, too.",
                    ),
                ),
                (
                    "biography",
                    models.CharField(blank=True, default="", max_length=5000),
                ),
                (
                    "stars",
                    models.DecimalField(
                        blank=True,
                        db_index=True,
                        decimal_places=2,
                        default=None,
                        max_digits=3,
                        null=True,
                    ),
                ),
                (
                    "processor_override",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("authorize", "EVO Authorize.net"),
                            ("stripe", "Stripe"),
                        ],
                        default="",
                        max_length=24,
                    ),
                ),
                (
                    "current_intent",
                    models.CharField(
                        blank=True, db_index=True, default="", max_length=30
                    ),
                ),
                ("rating_count", models.IntegerField(blank=True, default=0)),
                (
                    "reset_token",
                    models.CharField(blank=True, default=uuid.uuid4, max_length=36),
                ),
                ("verified_email", models.BooleanField(db_index=True, default=False)),
                ("token_expiry", models.DateTimeField(auto_now_add=True)),
                ("notes", models.TextField(blank=True, default="")),
                ("drip_id", models.CharField(db_index=True, default="", max_length=32)),
                (
                    "blacklist",
                    models.ManyToManyField(
                        blank=True, related_name="blacklisting_users", to="lib.tag"
                    ),
                ),
                (
                    "blocking",
                    models.ManyToManyField(
                        blank=True,
                        related_name="blocked_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
            ],
            options={
                "ordering": ("-date_joined",),
            },
            bases=(models.Model, apps.lib.abstract_models.HitsMixin),
        ),
    ]
