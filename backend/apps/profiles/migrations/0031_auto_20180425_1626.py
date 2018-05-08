# Generated by Django 2.0.4 on 2018-04-25 16:26
from django.contrib.contenttypes.models import ContentType
from django.db import migrations


ASSET_SHARED = 23
CHAR_SHARED = 24


def add_share_subscriptions(apps, schema):
    User = apps.get_model('profiles', 'User')
    Subscription = apps.get_model('lib', 'Subscription')
    # Need to use native model to force creation if it does not exist.
    content_type = ContentType.objects.get_for_model(User)
    for user in User.objects.all():
        Subscription.objects.get_or_create(
            subscriber=user,
            content_type=content_type,
            object_id=user.id,
            type=ASSET_SHARED
        )


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0030_auto_20180424_1832'),
        ('lib', '0011_auto_20180402_1755'),
    ]

    operations = [
        migrations.RunPython(add_share_subscriptions, reverse_code=lambda x, y: None)
    ]
