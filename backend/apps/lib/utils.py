from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import Q
from django.db.models.signals import pre_delete
from django.db.transaction import atomic
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from pycountry import countries, subdivisions
from rest_framework import status
from rest_framework.response import Response

from apps.lib.models import Subscription, Event, Notification, Tag, Comment, COMMENT


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


class RecallNotification(Exception):
    """
    Used during a transform function to recall a notification.
    For instance, if we're tracking all of the people who commented on a submission
    and the only person who commented removed their comment, we'd want to recall the event altogether.
    """
    def __init__(self, *args, **kwargs):
        self.data = kwargs.pop('data')
        super(*args, **kwargs)


def recall_notification(event_type, target, data=None, unique_data=False):
    content_type = target and ContentType.objects.get_for_model(target)
    object_id = target and target.id
    events = get_matching_events(event_type, content_type, object_id, data, unique_data)
    events.update(recalled=True)


def update_event(event, data, subscriptions, mark_unread, time_override=None, transform=None):
    event.recalled = False
    if mark_unread or time_override:
        event.date = time_override or timezone.now()
    if transform:
        try:
            data = transform(event.data, data)
        except RecallNotification as err:
            event.recalled = True
            event.data = err.data
            event.save()
            return
    event.data = data
    event.save()
    if mark_unread:
        subscribers = subscriptions.values_list('subscriber_id', flat=True)
        Notification.objects.filter(user__in=subscribers, event=event).update(read=False)


def target_params(object_id, content_type):
    query = Q(object_id__isnull=True, content_type__isnull=True)
    if content_type:
        query |= Q(object_id=object_id, content_type=content_type)
    return query


def get_matching_subscriptions(event_type, object_id, content_type, exclude=None):
    exclude = exclude or []
    return Subscription.objects.filter(
        Q(type=event_type, removed=False) & target_params(object_id, content_type)
    ).exclude(subscriber__in=exclude)


def get_matching_events(event_type, content_type, object_id, data, unique_data=None):
    query = Q(type=event_type)
    query &= target_params(object_id, content_type)
    if unique_data:
        if unique_data is True:
            query &= Q(data=data)
        else:
            kwargs = {'data__' + key: value for key, value in unique_data.items()}
            query &= Q(**kwargs)
    return Event.objects.filter(query)


@atomic
def notify(
        event_type, target, data=None, unique=False, unique_data=None, mark_unread=False, time_override=None,
        transform=None, exclude=None
):
    if data is None:
        data = {}
    content_type = target and ContentType.objects.get_for_model(target)
    object_id = target and target.id
    subscriptions = get_matching_subscriptions(event_type, object_id, content_type, exclude)
    if not subscriptions.exists():
        return
    if unique or unique_data:
        events = get_matching_events(event_type, content_type, object_id, data, unique_data)
        if events.exists():
            update_event(
                events[0], data, subscriptions,
                mark_unread=mark_unread,
                time_override=time_override,
                transform=transform
            )
            return
    event = Event.objects.create(
        type=event_type, object_id=target and target.id, content_type=content_type, data=data
    )
    Notification.objects.bulk_create(
        (
            Notification(
                event_id=event.id, user_id=subscriber_id
            )
            for subscriber_id in subscriptions.values_list('subscriber_id', flat=True)
        ),
        batch_size=1000
    )


def clear_events(sender, instance, **_kwargs):
    """
    To be used as a signal handler elsewhere on models to make sure any events that existed with this
    instance as the target are removed. Use in pre_delete.
    """
    Event.objects.filter(object_id=instance.id, content_type=ContentType.objects.get_for_model(instance)).delete()


# This receiver is not in models where it would normally be, since we want to have clear_events available in utils
# in a manner which my IDE will pull them in.

# ...Yeah, that sounds kinda dumb, maybe I'll change it later if it trips me up.
remove_order_events = receiver(pre_delete, sender=Comment)(clear_events)


def _comment_filter(old_data, comment_id):
    comments = [comment for comment in old_data['comments'] if comment != comment_id]
    subcomments = [comment for comment in old_data['subcomments'] if comment != comment_id]
    data = {
        'comments': comments,
        'subcomments': subcomments
    }
    if not comments:
        raise RecallNotification(data=data)
    return {
        'comments': comments,
        'subcomments': subcomments
    }


def remove_comment(comment_id):
    """
    Removes all notifications for a comment.
    """
    events = Event.objects.filter(type=COMMENT).filter(
        Q(data__comments__contains=comment_id) | Q(data__subcomments__contains=comment_id)
    )
    data = comment_id
    for event in events:
        update_event(event, data, False, Subscription.objects.none(), transform=_comment_filter)


def add_check(instance, field_name, *args):
    args_length = len(args)
    max_length = getattr(instance, field_name + '__max')
    current_length = getattr(instance, field_name).all().count()
    proposed = args_length + current_length
    if proposed > max_length:
        raise ValidationError(
            'This would exceed the maximum number of entries for this relation. {} > {}'.format(proposed, max_length)
        )


def safe_add(instance, field_name, *args):
    add_check(instance, field_name, *args)
    getattr(instance, field_name).add(*args)


def ensure_tags(tag_list):
    if not tag_list:
        return
    with connection.cursor() as cursor:
        # Bulk get or create
        # Django's query prepper automatically wraps our arrays in parens, but we need to have them
        # act as individual values, so we have to custom build our placeholders here.
        statement = """
                    INSERT INTO lib_tag (name)
                    (
                             SELECT i.name
                             FROM (VALUES {}) AS i(name)
                             LEFT JOIN lib_tag as existing
                                     ON (existing.name = i.name)
                             WHERE existing.name IS NULL
                    )
                    """.format(('%s, ' * len(tag_list)).rsplit(',', 1)[0])
        cursor.execute(statement, [*tuple((tag,) for tag in tag_list)])


def tag_list_cleaner(tag_list):
    tag_list = [slugify(str(tag).lower().replace(' ', '')).replace('-', '_')[:50] for tag in tag_list]
    return list({tag for tag in tag_list if tag})


def add_tags(request, target, field_name='tags'):
    if 'tags' not in request.data:
        return False, Response(status=status.HTTP_400_BAD_REQUEST, data={'tags': ['This field is required.']})
    tag_list = request.POST.getlist('tags')
    # Slugify, but also do a few tricks to reduce the incidence rate of duplicates.
    tag_list = tag_list_cleaner(tag_list)
    try:
        add_check(target, field_name, *tag_list)
    except ValueError as err:
        return False, Response(status=status.HTTP_400_BAD_REQUEST, data={'tags': [str(err)]})
    ensure_tags(tag_list)
    getattr(target, field_name).add(*Tag.objects.filter(name__in=tag_list))
    return True, tag_list


def remove_tags(request, target, field_name='tags'):
    if 'tags' not in request.data:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'tags': ['This field is required.']})
    tag_list = request.data['tags']
    qs = Tag.objects.filter(name__in=tag_list)
    if not qs.exists():
        return False, Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={'tags': [
                'No tags specified, or the requested tags do not exist.'
            ]}
        )
    getattr(target, field_name).remove(*qs)
    return True, qs


# https://www.caktusgroup.com/blog/2009/05/26/explicit-table-locking-with-postgresql-and-django/
LOCK_MODES = (
    'ACCESS SHARE',
    'ROW SHARE',
    'ROW EXCLUSIVE',
    'SHARE UPDATE EXCLUSIVE',
    'SHARE',
    'SHARE ROW EXCLUSIVE',
    'EXCLUSIVE',
    'ACCESS EXCLUSIVE',
)


def require_lock(model, lock):
    """
    Decorator for PostgreSQL's table-level lock functionality

    Example:
        @transaction.commit_on_success
        @require_lock(MyModel, 'ACCESS EXCLUSIVE')
        def myview(request)
            ...

    PostgreSQL's LOCK Documentation:
    http://www.postgresql.org/docs/8.3/interactive/sql-lock.html
    """
    def require_lock_decorator(view_func):
        def wrapper(*args, **kwargs):
            if lock not in LOCK_MODES:
                raise ValueError('%s is not a PostgreSQL supported lock mode.')
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute(
                'LOCK TABLE %s IN %s MODE' % (model._meta.db_table, lock)
            )
            return view_func(*args, **kwargs)
        return wrapper
    return require_lock_decorator
