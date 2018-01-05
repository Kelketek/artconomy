from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.transaction import atomic
from django.utils import timezone
from pycountry import countries, subdivisions

from apps.lib.models import Subscription, Event, Notification


def countries_tweaked():
    """
    Tweaked listing of countries.
    """
    us = countries.get(alpha_2='US')
    yield (us.alpha_2, us.name)
    for a in countries:
        if a.alpha_2 == 'TW':
            yield (a.alpha_2, "Taiwan")
        elif a.alpha_2 in settings.COUNTRIES_NOT_SERVED:
            continue
        elif a.alpha_2 != 'US':
            yield (a.alpha_2, a.name)


def country_choices():
    return [country_choice for country_choice in countries_tweaked()]


# Force pycountry to fetch data.
subdivisions.get(country_code='US')

subdivision_map = {
    country.alpha_2:
        {subdivision.code[3:]: subdivision.name for subdivision in subdivisions.get(country_code=country.alpha_2)}
        if country.alpha_2 in subdivisions.indices['country_code']
        else {}
    for country in countries
}

country_map = {country.name.lower(): country for country in countries}

for code, name in ('AE', 'AA', 'AP'):
    subdivision_map['US'][code] = code


def recall_notification(event_type, target, data=None, unique_data=False):
    content_type = ContentType.objects.get_for_model(target)
    events = get_matching_events(event_type, content_type, target, data, unique_data)
    events.update(recalled=True)


def update_event(event, data, subscriptions, mark_unread, time_override=None):
    event.recalled = False
    if mark_unread or time_override:
        event.date = time_override or timezone.now()
    event.data = data
    event.save()
    if mark_unread:
        subscribers = subscriptions.values_list('subscriber_id', flat=True)
        Notification.objects.filter(user__in=subscribers, event=event).update(read=False)


def get_matching_events(event_type, content_type, target, data, unique_data=False):
    kwargs = {'type': event_type, 'content_type': content_type, 'object_id': target.id}
    if unique_data:
        kwargs['data'] = data
    return Event.objects.filter(**kwargs)


@atomic
def notify(event_type, target, data=None, unique=False, unique_data=False, mark_unread=False, time_override=None):
    content_type = ContentType.objects.get_for_model(target)
    subscriptions = Subscription.objects.filter(
        type=event_type, object_id=target.id, content_type=content_type,
        removed=False
    )
    if not subscriptions.exists():
        return
    if unique or unique_data:
        events = get_matching_events(event_type, content_type, target, data, unique_data)
        if events.exists():
            update_event(events[0], data, subscriptions, mark_unread=mark_unread, time_override=time_override)
            return
    event = Event.objects.create(type=event_type, object_id=target.id, content_type=content_type, data=data)
    Notification.objects.bulk_create(
        (
            Notification(
                event_id=event.id, user_id=subscriber_id
            )
            for subscriber_id in subscriptions.values_list('subscriber_id', flat=True)
        ),
        batch_size=1000
    )
