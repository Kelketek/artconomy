# Generated by Django 3.2.13 on 2022-05-07 10:35

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0121_replace_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submission',
            name='artists',
        ),
        migrations.RemoveField(
            model_name='submission',
            name='characters',
        ),
        migrations.RenameField(
            model_name='submission',
            old_name='artists_new',
            new_name='artists',
        ),
        migrations.RenameField(
            model_name='submission',
            old_name='characters_new',
            new_name='characters',
        ),
        migrations.AlterField(
            model_name='submission',
            name='artists',
            field=models.ManyToManyField(blank=True, related_name='art', through='profiles.ArtistTag', to=settings.AUTH_USER_MODEL),
        ),
    ]
