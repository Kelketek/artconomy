# Generated by Django 4.1.5 on 2023-01-25 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0037_auto_20221030_1740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.SlugField(primary_key=True, serialize=False, unique=True),
        ),
    ]