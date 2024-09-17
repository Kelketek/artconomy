# Generated by Django 2.0.6 on 2018-06-25 16:31
from apps.lib.constants import RENEWAL_FAILURE, SUBSCRIPTION_DEACTIVATED
from django.contrib.contenttypes.models import ContentType
from django.db import migrations


def add_failure_subscription(apps, schema):
    User = apps.get_model("profiles", "User")
    Subscription = apps.get_model("lib", "Subscription")
    # Remove any broken subscriptions from previous iteration.
    Subscription.objects.filter(type=RENEWAL_FAILURE).delete()
    Subscription.objects.filter(type=SUBSCRIPTION_DEACTIVATED).delete()
    # Need to use native model to force creation if it does not exist.
    content_type = ContentType.objects.get_for_model(User)
    for user in User.objects.all():
        Subscription.objects.get_or_create(
            subscriber=user,
            content_type_id=content_type.id,
            object_id=user.id,
            type=RENEWAL_FAILURE,
            email=True,
        )
        Subscription.objects.get_or_create(
            subscriber=user,
            content_type_id=content_type.id,
            object_id=user.id,
            type=SUBSCRIPTION_DEACTIVATED,
            email=True,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0044_auto_20180625_1540"),
    ]

    operations = [migrations.RunPython(add_failure_subscription, lambda x, y: None)]
