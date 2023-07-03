# Generated by Django 3.2.9 on 2021-12-30 19:00

from django.db import migrations
from django.db.models import Max


def reset_ratings(apps, schema):
    User = apps.get_model("profiles", "User")
    for user in User.objects.filter(artist_profile__isnull=False):
        user.artist_profile.max_rating = (
            user.products.all().aggregate(Max("max_rating"))["max_rating__max"] or 0
        )
        user.artist_profile.save()


def set_all_ratings(apps, schema):
    Product = apps.get_model("sales", "Product")
    for product in Product.objects.all():
        product.max_rating = product.user.artist_profile.max_rating
        product.save()


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0124_product_max_rating"),
    ]

    operations = [migrations.RunPython(set_all_ratings, reverse_code=reset_ratings)]
