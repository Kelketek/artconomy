# Generated by Django 5.1.2 on 2024-11-04 22:19

import django.core.validators
import django.utils.timezone
import easy_thumbnails.fields
import uuid
from django.db import migrations, models
from django.contrib.postgres.operations import CreateCollation


class Migration(migrations.Migration):

    initial = True

    operations = [
        migrations.CreateModel(
            name="Asset",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                (
                    "file",
                    easy_thumbnails.fields.ThumbnailerImageField(
                        upload_to="art/%Y/%m/%d/",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=(
                                    "ACC",
                                    "AE",
                                    "AI",
                                    "AN",
                                    "AVI",
                                    "BMP",
                                    "DGN",
                                    "DOC",
                                    "DOCH",
                                    "DOCM",
                                    "DOCX",
                                    "DOTH",
                                    "DW",
                                    "DWFX",
                                    "DWG",
                                    "DXF",
                                    "EPS",
                                    "F4A",
                                    "F4V",
                                    "FLV",
                                    "FS",
                                    "GIF",
                                    "IND",
                                    "JPEG",
                                    "JPG",
                                    "JPP",
                                    "LR",
                                    "M4V",
                                    "MIDI",
                                    "MKV",
                                    "MOV",
                                    "MP3",
                                    "MP4",
                                    "MPEG",
                                    "MPG",
                                    "OGA",
                                    "OGG",
                                    "OGV",
                                    "PDF",
                                    "PNG",
                                    "PS",
                                    "PSD",
                                    "RTF",
                                    "SVG",
                                    "SWF",
                                    "TIF",
                                    "TIFF",
                                    "TXT",
                                    "VTX",
                                    "WAV",
                                    "WDP",
                                    "WEBM",
                                    "WMA",
                                    "WMV",
                                    "ZIP",
                                )
                            )
                        ],
                    ),
                ),
                ("hash", models.BinaryField(db_index=True, default=b"", max_length=32)),
                ("created_on", models.DateTimeField(default=django.utils.timezone.now)),
                ("edited_on", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Comment",
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
                ("deleted", models.BooleanField(db_index=True, default=False)),
                ("thread_deleted", models.BooleanField(db_index=True, default=False)),
                ("text", models.CharField(max_length=8000)),
                ("system", models.BooleanField(db_index=True, default=False)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("edited_on", models.DateTimeField(auto_now=True)),
                ("edited", models.BooleanField(default=False)),
                (
                    "object_id",
                    models.PositiveIntegerField(blank=True, db_index=True, null=True),
                ),
                ("extra_data", models.JSONField(blank=True, default=dict)),
                (
                    "top_object_id",
                    models.PositiveIntegerField(db_index=True, null=True),
                ),
            ],
            options={
                "ordering": ("created_on",),
            },
        ),
        migrations.CreateModel(
            name="EmailPreference",
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
                    "type",
                    models.IntegerField(
                        choices=[
                            (0, "New Character"),
                            (1, "New Watcher"),
                            (3, "Character Tagged"),
                            (4, "New Comment"),
                            (7, "Commission Slots Available"),
                            (6, "New Product"),
                            (11, "New Auction"),
                            (18, "Order Update"),
                            (22, "Revision Uploaded"),
                            (35, "Reference Uploaded"),
                            (19, "Sale Update"),
                            (15, "Dispute Filed"),
                            (16, "Refund Processed"),
                            (26, "Artist is streaming"),
                            (8, "New Submission of Character"),
                            (23, "Submission shared"),
                            (24, "Character Shared"),
                            (14, "New Favorite"),
                            (10, "Submission Tagged"),
                            (17, "Submission tagged with Character"),
                            (20, "Tagged as the artist of a submission"),
                            (21, "Tagged the artist of a submission"),
                            (12, "Announcement"),
                            (13, "System-wide announcement"),
                            (27, "Renewal Failure"),
                            (29, "Renewal Fixed"),
                            (34, "Referral Landscape Credit"),
                            (28, "Subscription Deactivated"),
                            (30, "New Journal Posted"),
                            (32, "Bank Transfer Failed"),
                            (36, "Wait list updated"),
                            (37, "Tip Received"),
                            (38, "Commissions automatically closed"),
                            (39, "WIP Approved"),
                        ],
                        db_index=True,
                    ),
                ),
                ("enabled", models.BooleanField(db_index=True, default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Event",
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
                    "type",
                    models.IntegerField(
                        choices=[
                            (0, "New Character"),
                            (1, "New Watcher"),
                            (3, "Character Tagged"),
                            (4, "New Comment"),
                            (7, "Commission Slots Available"),
                            (6, "New Product"),
                            (11, "New Auction"),
                            (18, "Order Update"),
                            (22, "Revision Uploaded"),
                            (35, "Reference Uploaded"),
                            (19, "Sale Update"),
                            (15, "Dispute Filed"),
                            (16, "Refund Processed"),
                            (26, "Artist is streaming"),
                            (8, "New Submission of Character"),
                            (23, "Submission shared"),
                            (24, "Character Shared"),
                            (14, "New Favorite"),
                            (10, "Submission Tagged"),
                            (17, "Submission tagged with Character"),
                            (20, "Tagged as the artist of a submission"),
                            (21, "Tagged the artist of a submission"),
                            (12, "Announcement"),
                            (13, "System-wide announcement"),
                            (27, "Renewal Failure"),
                            (29, "Renewal Fixed"),
                            (34, "Referral Landscape Credit"),
                            (28, "Subscription Deactivated"),
                            (30, "New Journal Posted"),
                            (32, "Bank Transfer Failed"),
                            (36, "Wait list updated"),
                            (37, "Tip Received"),
                            (38, "Commissions automatically closed"),
                            (39, "WIP Approved"),
                        ],
                        db_index=True,
                    ),
                ),
                ("data", models.JSONField(default=dict)),
                ("date", models.DateTimeField(auto_now_add=True)),
                (
                    "object_id",
                    models.PositiveIntegerField(blank=True, db_index=True, null=True),
                ),
                ("recalled", models.BooleanField(db_index=True, default=False)),
            ],
        ),
        migrations.CreateModel(
            name="GenericReference",
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
                ("object_id", models.UUIDField(db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name="ModifiedMarker",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ("modified_on", models.DateTimeField(db_index=True)),
                ("object_id", models.UUIDField(db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name="Note",
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
                ("text", models.TextField()),
                (
                    "hash",
                    models.BinaryField(
                        db_index=True, default=b"", max_length=32, unique=True
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Notification",
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
            name="ReadMarker",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ("last_read_on", models.DateTimeField(db_index=True, default=None)),
                ("object_id", models.UUIDField(db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name="Subscription",
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
                    "type",
                    models.IntegerField(
                        choices=[
                            (0, "New Character"),
                            (1, "New Watcher"),
                            (3, "Character Tagged"),
                            (4, "New Comment"),
                            (7, "Commission Slots Available"),
                            (6, "New Product"),
                            (11, "New Auction"),
                            (18, "Order Update"),
                            (22, "Revision Uploaded"),
                            (35, "Reference Uploaded"),
                            (19, "Sale Update"),
                            (15, "Dispute Filed"),
                            (16, "Refund Processed"),
                            (26, "Artist is streaming"),
                            (8, "New Submission of Character"),
                            (23, "Submission shared"),
                            (24, "Character Shared"),
                            (14, "New Favorite"),
                            (10, "Submission Tagged"),
                            (17, "Submission tagged with Character"),
                            (20, "Tagged as the artist of a submission"),
                            (21, "Tagged the artist of a submission"),
                            (12, "Announcement"),
                            (13, "System-wide announcement"),
                            (27, "Renewal Failure"),
                            (29, "Renewal Fixed"),
                            (34, "Referral Landscape Credit"),
                            (28, "Subscription Deactivated"),
                            (30, "New Journal Posted"),
                            (32, "Bank Transfer Failed"),
                            (36, "Wait list updated"),
                            (37, "Tip Received"),
                            (38, "Commissions automatically closed"),
                            (39, "WIP Approved"),
                        ],
                        db_index=True,
                    ),
                ),
                (
                    "object_id",
                    models.PositiveIntegerField(blank=True, db_index=True, null=True),
                ),
                ("implicit", models.BooleanField(db_index=True, default=True)),
                ("email", models.BooleanField(db_index=True, default=False)),
                ("telegram", models.BooleanField(db_index=True, default=False)),
                ("removed", models.BooleanField(db_index=True, default=False)),
                ("until", models.DateField(db_index=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "name",
                    models.SlugField(primary_key=True, serialize=False, unique=True),
                ),
            ],
        ),
        CreateCollation(
            "case_insensitive",
            provider="icu",
            locale="und-u-ks-level1",
            deterministic=False,
        ),
    ]