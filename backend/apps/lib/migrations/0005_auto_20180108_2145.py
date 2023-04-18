# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-08 21:45
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lib", "0004_auto_20180107_1548"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="data",
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name="event",
            name="type",
            field=models.IntegerField(
                choices=[
                    (0, "New Submission"),
                    (1, "New Follower"),
                    (2, "Character Transfer Request"),
                    (3, "Character Tag Approval"),
                    (4, "New Comment"),
                    (5, "New Character"),
                    (7, "Commission Slots Available"),
                    (6, "New Product"),
                    (11, "New Auction"),
                    (15, "Dispute Filed"),
                    (16, "Refund Processed"),
                    (8, "New Submission of Character"),
                    (9, "New Portfolio Item"),
                    (14, "New Favorite"),
                    (10, "Submission Tag Approval"),
                    (12, "Announcement"),
                    (13, "System-wide announcement"),
                ],
                db_index=True,
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="type",
            field=models.IntegerField(
                choices=[
                    (0, "New Submission"),
                    (1, "New Follower"),
                    (2, "Character Transfer Request"),
                    (3, "Character Tag Approval"),
                    (4, "New Comment"),
                    (5, "New Character"),
                    (7, "Commission Slots Available"),
                    (6, "New Product"),
                    (11, "New Auction"),
                    (15, "Dispute Filed"),
                    (16, "Refund Processed"),
                    (8, "New Submission of Character"),
                    (9, "New Portfolio Item"),
                    (14, "New Favorite"),
                    (10, "Submission Tag Approval"),
                    (12, "Announcement"),
                    (13, "System-wide announcement"),
                ],
                db_index=True,
            ),
        ),
    ]
