# Generated by Django 2.0.4 on 2018-06-04 19:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0019_auto_20180503_2000"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="rating",
            name="rating_set",
        ),
        migrations.RemoveField(
            model_name="ratingset",
            name="rater",
        ),
        migrations.RemoveField(
            model_name="ratingset",
            name="target",
        ),
        migrations.DeleteModel(
            name="Rating",
        ),
        migrations.DeleteModel(
            name="RatingSet",
        ),
    ]
