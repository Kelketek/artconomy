# Generated by Django 2.0.7 on 2018-07-18 17:54

from django.db import migrations


def remove_new_portfolio_items(apps, schema):
    Event = apps.get_model("lib", "Event")
    Event.objects.filter(type=9).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0048_auto_20180713_2019"),
    ]

    operations = [
        migrations.RunPython(remove_new_portfolio_items, reverse_code=lambda x, y: None)
    ]
