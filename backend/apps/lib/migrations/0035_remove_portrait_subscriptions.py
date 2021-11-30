# Generated by Django 3.2.9 on 2021-11-30 17:29

from django.db import migrations

REFERRAL_PORTRAIT_CREDIT = 33
COMMISSIONS_OPEN = 7


def remove_portrait_subscriptions(apps, schema):
    Subscription = apps.get_model('lib', 'Subscription')
    Event = apps.get_model('lib', 'Event')
    Subscription.objects.filter(type=REFERRAL_PORTRAIT_CREDIT).delete()
    Event.objects.filter(type=REFERRAL_PORTRAIT_CREDIT).delete()
    Subscription.objects.filter(type=7).update(email=False, telegram=False, until=None)


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0034_merge_0033_auto_20210422_1554_0033_auto_20210721_1001'),
    ]

    operations = [
        migrations.RunPython(remove_portrait_subscriptions, reverse_code=lambda x, y: None)
    ]
