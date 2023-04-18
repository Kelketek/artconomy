# Generated by Django 2.0.7 on 2018-07-09 16:38

import easy_thumbnails.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0045_auto_20180625_1631"),
    ]

    operations = [
        migrations.AddField(
            model_name="imageasset",
            name="preview",
            field=easy_thumbnails.fields.ThumbnailerImageField(
                blank=True, default="", null=True, upload_to="thumbs/%Y/%m/%d/"
            ),
        ),
    ]
