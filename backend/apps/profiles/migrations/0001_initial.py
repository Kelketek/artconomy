# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-21 16:47
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import easy_thumbnails.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(db_index=True, max_length=255, unique=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(db_index=True, max_length=30, unique=True)),
                ('dwolla_url', models.URLField(blank=True, default='')),
                ('commissions_closed', models.BooleanField(db_index=True, default=True, help_text='When enabled, no one may commission you.')),
                ('use_load_tracker', models.BooleanField(default=True, help_text='Whether to use load tracking to automatically open or close commissions.')),
                ('max_load', models.IntegerField(default=10, help_text="How much work you're willing to take on at once (for artists)", validators=[django.core.validators.MinValueValidator(1)])),
                ('rating', models.IntegerField(choices=[(0, 'Clean/Safe for work'), (1, 'Risque/mature, not adult content but not safe for work'), (2, 'Adult content, not safe for work')], db_index=True, default=0, help_text='Shows the maximum rating to display. By setting this to anything other than general, you certify that you are of legal age to view adult content in your country.')),
                ('sfw_mode', models.BooleanField(default=False, help_text='Enable this to only display clean art. Useful if temporarily browsing from a location where adult content is not appropriate.')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('description', models.CharField(blank=True, default='', max_length=5000)),
                ('private', models.BooleanField(default=False, help_text='Only show this character to people I have explicitly shared it to.')),
                ('open_requests', models.BooleanField(default=True, help_text='Allow others to request commissions with my character, such as for gifts.')),
                ('open_requests_restrictions', models.CharField(blank=True, default='', help_text="Write any particular conditions or requests to be considered when someone else is commissioning a piece with this character. For example, 'This character should only be drawn in Safe for Work Pieces.'", max_length=2000)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ImageAsset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(0, 'Clean/Safe for work'), (1, 'Risque/mature, not adult content but not safe for work'), (2, 'Adult content, not safe for work')], db_index=True, default=0)),
                ('file', easy_thumbnails.fields.ThumbnailerImageField(upload_to='art/%Y/%m/%d/')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(blank=True, default='', max_length=100)),
                ('caption', models.CharField(blank=True, default='', max_length=2000)),
                ('private', models.BooleanField(default=False, help_text='Only show this to people I have explicitly shared it to.')),
                ('characters', models.ManyToManyField(related_name='assets', to='profiles.Character')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField()),
            ],
        ),
        migrations.AddField(
            model_name='imageasset',
            name='tags',
            field=models.ManyToManyField(related_name='assets', to='profiles.Tag'),
        ),
        migrations.AddField(
            model_name='imageasset',
            name='uploaded_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_profiles_imageasset', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='character',
            name='primary_asset',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.ImageAsset'),
        ),
        migrations.AddField(
            model_name='character',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='characters', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='primary_character',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='profiles.Character'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='character',
            unique_together=set([('name', 'user')]),
        ),
    ]
