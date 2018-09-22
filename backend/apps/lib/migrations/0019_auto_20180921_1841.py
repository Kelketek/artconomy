# Generated by Django 2.0.8 on 2018-09-21 18:41

from django.db import migrations
from easy_thumbnails.files import generate_all_aliases


def regen_thumbnails(apps, schema):
    ImageAsset = apps.get_model('profiles', 'ImageAsset')
    Product = apps.get_model('sales', 'Product')
    Revision = apps.get_model('sales', 'Revision')
    models = [ImageAsset, Revision, Product]
    for model in models:
        for item in model.objects.all():
            item.file.delete_thumbnails()
            generate_all_aliases(item.file, include_global=True)
            item.preview.delete_thumbnails()
            generate_all_aliases(item.preview, include_global=True)


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0018_auto_20180723_1528'),
    ]

    operations = [
        migrations.RunPython(regen_thumbnails, reverse_code=lambda x, y: None)
    ]