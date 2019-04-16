# Generated by Django 2.2.1 on 2019-07-25 22:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0025_populate_assets'),
        ('sales', '0050_auto_20190725_2023'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='file',
            new_name='file_old',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='asset',
            new_name='file',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='preview',
            new_name='preview_old',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='preview_asset',
            new_name='preview',
        ),
        migrations.RenameField(
            model_name='revision',
            old_name='file',
            new_name='file_old',
        ),
        migrations.RenameField(
            model_name='revision',
            old_name='asset',
            new_name='file',
        ),
        migrations.RenameField(
            model_name='revision',
            old_name='preview',
            new_name='preview_old',
        ),
        migrations.RenameField(
            model_name='revision',
            old_name='preview_asset',
            new_name='preview',
        ),
        migrations.AlterField(
            model_name='revision',
            name='created_on',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]