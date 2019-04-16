# Generated by Django 2.2.1 on 2019-07-25 20:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0024_auto_20190725_2023'),
        ('sales', '0049_merge_20190701_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='asset',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to='lib.Asset',
                related_name='full_%(app_label)s_%(class)s'
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='preview_asset',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to='lib.Asset',
                related_name='preview_%(app_label)s_%(class)s'
            ),
        ),
        migrations.AddField(
            model_name='revision',
            name='asset',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to='lib.Asset',
                related_name='full_%(app_label)s_%(class)s'
            ),
        ),
        migrations.AddField(
            model_name='revision',
            name='preview_asset',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to='lib.Asset',
                related_name='preview_%(app_label)s_%(class)s'
            ),
        ),
    ]
