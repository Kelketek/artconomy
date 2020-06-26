import logging
import os
from pathlib import Path
from typing import Optional, TYPE_CHECKING

import markdown
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.db import connection
from django.db.models import Q, Model, Subquery, IntegerField
from django.db.models.signals import pre_delete
from django.db.transaction import atomic
from django.dispatch import receiver
from django.http import HttpRequest
from django.template import Template, Context
from django.template.loader import get_template
from django.utils import timezone
from django.utils.datetime_safe import date
from django.utils.deconstruct import deconstructible
from django.utils.text import slugify
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from pycountry import countries, subdivisions
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from telegram import Bot

from apps.lib.models import Subscription, Event, Notification, Tag, Comment, COMMENT, \
    NEW_PRODUCT, COMMISSIONS_OPEN, NEW_CHARACTER, STREAMING, EMAIL_SUBJECTS, NEW_JOURNAL
from shortcuts import make_url, disable_on_load, gen_textifier

BOT = None
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from apps.profiles.models import User
    from apps.lib.serializers import NewCommentSerializer


def get_bot():
    global BOT
    if not BOT:
        BOT = Bot(settings.TELEGRAM_BOT_KEY)
    return BOT


def countries_tweaked():
    """
    Tweaked listing of countries.
    """
    us = countries.get(alpha_2='US')
    country_list = []
    for a in countries:
        if a.alpha_2 == 'TW':
            country_list.append((a.alpha_2, "Taiwan"))
        elif a.alpha_2 in settings.COUNTRIES_NOT_SERVED:
            continue
        elif a.alpha_2 != 'US':
            country_list.append((a.alpha_2, a.name))
    country_list.sort(key=lambda x: x[1])
    country_list.insert(0, (us.alpha_2, us.name))
    return country_list


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
    ).exclude(subscriber__in=exclude).filter(Q(until__isnull=True) | Q(until__gte=date.today()))


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


def commissions_open_subscription(watcher: 'User', watched: 'User', target_date: date):
    content_type = ContentType.objects.get_for_model(watched)
    sub, _ = Subscription.objects.get_or_create(
        subscriber=watcher,
        content_type=content_type,
        object_id=watched.id,
        type=COMMISSIONS_OPEN
    )
    sub.until = target_date
    sub.telegram = True
    sub.email = True
    sub.save()


def watch_subscriptions(watcher, watched):
    # To be implemented when paid service is in place.
    target_date = (
        watcher.portrait_paid_through or watcher.landscape_paid_through or (date.today() - relativedelta(days=5))
    )
    commissions_open_subscription(watcher, watched, target_date)
    content_type = ContentType.objects.get_for_model(watched)
    Subscription.objects.get_or_create(
        subscriber=watcher,
        content_type=content_type,
        object_id=watched.id,
        type=NEW_CHARACTER
    )
    Subscription.objects.get_or_create(
        subscriber=watcher,
        content_type=content_type,
        object_id=watched.id,
        type=NEW_PRODUCT
    )
    Subscription.objects.get_or_create(
        subscriber=watcher,
        content_type=content_type,
        object_id=watched.id,
        type=STREAMING
    )
    Subscription.objects.get_or_create(
        subscriber=watcher,
        content_type=content_type,
        object_id=watched.id,
        type=NEW_JOURNAL
    )


def remove_watch_subscriptions(watcher, watched):
    content_type = ContentType.objects.get_for_model(watched)
    Subscription.objects.filter(
        subscriber=watcher,
        content_type=content_type,
        object_id=watched.id,
        type=NEW_CHARACTER
    ).delete()
    Subscription.objects.filter(
        subscriber=watcher,
        content_type=content_type,
        object_id=watched.id,
        type=NEW_PRODUCT
    ).delete()
    Subscription.objects.filter(
        subscriber=watcher,
        content_type=content_type,
        object_id=watched.id,
        type=COMMISSIONS_OPEN
    ).delete()
    Subscription.objects.filter(
        subscriber=watcher,
        content_type=content_type,
        object_id=watched.id,
        type=STREAMING
    ).delete()
    Subscription.objects.filter(
        subscriber=watcher,
        content_type=content_type,
        object_id=watched.id,
        type=NEW_JOURNAL
    ).delete()


class FakeRequest:
    def __init__(self, user):
        self.user = user

    @staticmethod
    def build_absolute_uri(value):
        return make_url(value)


@atomic
def notify(
        event_type, target, data=None, unique=False, unique_data=None, mark_unread=False, time_override=None,
        transform=None, exclude=None, force_create=False, silent_broadcast=False
):
    """
    Send out notifications to people who are subscribed to particular events.

    event_type should be a type users are subscribed to. Target is a target they're subscribed to that event type on
    (or None, if it's a general category like SYSTEM_ANNOUNCEMENT).

    data should be the JSON-compatible data to save in the event.

    unique is to specify that the notification is universally unique and that if the notification is run again with the
    same parameters (aside from whatever is in data, which can vary), it should not create a new broadcast.
    The existing events will be updated based on the other parameters.

    unique_data means that the event will only be considered unique if the data is precisely the same.

    time_override will force a particular timestamp on the event.

    transform is a function that takes the original data in an event and modifies it.

    exclude is a list of users whose subscriptions will be ignored. For instance, a user might have a comment
    subscription, but they made the comment, so we shouldn't notify them.

    force_create will force the creation of the event even if it would reach no subscribers. Useful if the data stored
    will be useful for later subscribers.

    silent_broadcast will not generate any emails or telegram notifications if they otherwise would have been generated.
    """
    from apps.lib.serializers import NOTIFICATION_TYPE_MAP
    from apps.lib.serializers import notification_serialize

    if data is None:
        data = {}
    content_type = target and ContentType.objects.get_for_model(target)
    object_id = target and target.id
    subscriptions = get_matching_subscriptions(event_type, object_id, content_type, exclude)

    if not subscriptions.exists() and not force_create:
        return

    event = None
    if unique or unique_data:
        events = get_matching_events(event_type, content_type, object_id, data, unique_data)
        if events.exists():
            event = events[0]
            update_event(
                event, data, subscriptions,
                mark_unread=mark_unread,
                time_override=time_override,
                transform=transform
            )
    if not event:
        event = Event.objects.create(
            type=event_type, object_id=target and target.id, content_type=content_type, data=data
        )

    # Send email notifications if needed.
    email_subscriptions = subscriptions.filter(email=True)
    if not silent_broadcast and email_subscriptions.exists():
        path = Path(settings.BACKEND_ROOT) / 'templates' / 'notifications'
        template = [file for file in os.listdir(str(path)) if file.startswith(str(event_type))][0]
        template_path = path / template
        for subscription in email_subscriptions:
            subject = EMAIL_SUBJECTS[event_type]
            req_context = {'request': FakeRequest(subscription.subscriber)}
            ctx = {
                'data': NOTIFICATION_TYPE_MAP.get(event_type, lambda x, _: x.data)(event, req_context),
                'target': notification_serialize(event.target, req_context), 'user': subscription.subscriber
            }
            subject = Template(subject).render(Context(ctx))
            to = [subscription.subscriber.guest_email or subscription.subscriber.email]
            from_email = settings.DEFAULT_FROM_EMAIL
            message = get_template(template_path).render(ctx)
            textifier = gen_textifier()
            msg = EmailMultiAlternatives(
                subject, textifier.handle(message), to=to, from_email=from_email, headers={'Return-Path': settings.RETURN_PATH_EMAIL}
            )
            msg.attach_alternative(message, 'text/html')
            msg.send()

    telegram_subscriptions = subscriptions.filter(telegram=True)
    if not silent_broadcast and telegram_subscriptions.exists():
        path = Path(settings.BACKEND_ROOT) / 'templates' / 'notifications'
        template = [file for file in os.listdir(str(path)) if file.startswith('TG_' + str(event_type))][0]
        template_path = path / template
        for subscription in telegram_subscriptions:
            if not subscription.subscriber.tg_chat_id:
                continue
            req_context = {'request': FakeRequest(subscription.subscriber)}
            ctx = {
                'data': NOTIFICATION_TYPE_MAP.get(event_type, lambda x, _: x.data)(event, req_context),
                'target': notification_serialize(event.target, req_context), 'user': subscription.subscriber,
                'base_url': make_url('')
            }
            message = get_template(template_path).render(ctx)
            try:
                get_bot().send_message(chat_id=subscription.subscriber.tg_chat_id, parse_mode='Markdown', text=message)
            except Exception as err:
                logger.exception(err)

    # We need to make sure anyone who was previously ineligible for a notification who is now eligible can get one.
    # To do that, we must avoid creating any that already exist if we want to leverage bulk_create. This should
    # be a minority case that won't require too much overhead when it happens, but I suppose we will see.
    existing = Notification.objects.filter(event=event.id).values_list('user_id', flat=True)
    subscriptions = subscriptions.exclude(subscriber_id__in=existing)
    Notification.objects.bulk_create(
        (
            Notification(
                event_id=event.id, user_id=subscriber_id
            )
            for subscriber_id in subscriptions.values_list('subscriber_id', flat=True)
        ),
        batch_size=1000
    )


def subscribe(event_type, user, target, implicit=True):
    subscription, created = Subscription.objects.get_or_create(
        type=event_type, subscriber=user, content_type=ContentType.objects.get_for_model(target),
        object_id=target.id
    )
    subscription.implicit = implicit
    subscription.save()
    return subscription, created


# noinspection PyUnusedLocal
@disable_on_load
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
        'subcomments': subcomments,
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


def add_check(instance: Optional[Model], field_name: str, *args, replace: bool = False, fallback_max: int = 200):
    args_length = len(args)
    if instance:
        max_length = getattr(instance, field_name + '__max')
    else:
        max_length = fallback_max
    if replace or not instance:
        current_length = 0
    else:
        current_length = getattr(instance, field_name).all().count()
    proposed = args_length + current_length
    if proposed > max_length:
        raise ValidationError(
            'This would exceed the maximum number of entries for this relation. {} > {}'.format(proposed, max_length)
        )


def set_tags(instance, field_name, tag_names):
    """
    Idempotently sets the tags an instance field.
    Assumes you've done all other cleanup and verification aside from ensuring the tags exist and setting them.
    """
    ensure_tags(tag_names)
    getattr(instance, field_name).set(tag_names)


def safe_add(instance, field_name, *args):
    add_check(instance, field_name, *args)
    getattr(instance, field_name).add(*args)


def ensure_tags(tag_list):
    if not tag_list:
        return
    # May have already been run, but don't want to risk injection.
    tag_list = tag_list_cleaner(tag_list)
    with connection.cursor() as cursor:
        # Bulk get or create
        # Django's query prepper automatically wraps our arrays in parens, but we need to have them
        # act as individual values, so we have to custom build our placeholders here.
        formatted_list = ('%s, ' * len(tag_list)).rsplit(',', 1)[0]
        # noinspection SqlType
        statement = f"""
                    INSERT INTO lib_tag (name)
                    (
                             SELECT i.name
                             FROM (VALUES {formatted_list}) AS i(name)
                             LEFT JOIN lib_tag as existing
                                     ON (existing.name = i.name)
                             WHERE existing.name IS NULL
                    )
                    """
        cursor.execute(statement, [*tuple((tag,) for tag in tag_list)])


def tag_list_cleaner(tag_list):
    tag_list = [slugify(str(tag).lower().replace(' ', '_')).replace('-', '_')[:50] for tag in tag_list]
    return list({tag for tag in tag_list if tag})


def add_tags(value, target, field_name: str = 'tags'):
    # Slugify, but also do a few tricks to reduce the incidence rate of duplicates.
    tag_list = tag_list_cleaner(value)
    try:
        add_check(target, field_name, *tag_list)
    except Exception as err:
        raise ValidationError({field_name: str(err)})
    ensure_tags(tag_list)
    getattr(target, field_name).add(*Tag.objects.filter(name__in=tag_list))
    return tag_list


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
    for tag in qs:
        tag.self_clean()
    return True, None


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
                raise ValueError('%s is not a PostgreSQL supported lock mode.' % lock)
            from django.db import connection
            cursor = connection.cursor()
            # noinspection PyProtectedMember
            cursor.execute(
                'LOCK TABLE %s IN %s MODE' % (model._meta.db_table, lock)
            )
            return view_func(*args, **kwargs)
        return wrapper
    return require_lock_decorator


def translate_related_names(names):
    new_names = []
    for related_name in names:
        if not related_name.endswith('+'):
            new_names.append(related_name)
            continue
        base_name = related_name.split('_')[0]
        base_name = base_name.lower()
        base_name += '_set'
        new_names.append(base_name)
    return new_names


@deconstructible
class MinimumOrZero:
    def __init__(self, limit):
        self.limit = limit

    def __call__(self, value):
        if value == 0:
            return True
        if value < self.limit:
            raise ValidationError('Must be zero, or greater than or equal to {}'.format(self.limit))


def default_context():
    return {
        'title': 'Artconomy-- Where characters come alive!',
        'description': 'Provides a platform that makes it as easy for people to '
                       'commission artists online as it is in person.',
    }


def demark(text):
    return BeautifulSoup(markdown.markdown(text), features="lxml").get_text()


def preview_rating(request, target_rating, real_link, sub_link='/static/images/logo.png'):
    real_link = make_url(real_link)
    sub_link = make_url(sub_link)
    if request.user.is_authenticated:
        if request.max_rating < target_rating:
            return sub_link
        else:
            return real_link
    if target_rating >= 3:
        # extreme content, always avoid preview.
        return sub_link
    return real_link


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def send_transaction_email(subject, template_name, user, context):
    template_path = Path(settings.BACKEND_ROOT) / 'templates' / 'transactional' / template_name
    if isinstance(user, str):
        to = [user]
    else:
        to = [user.email]
    from_email = settings.DEFAULT_FROM_EMAIL
    message = get_template(template_path).render(context)
    textifier = gen_textifier()
    msg = EmailMultiAlternatives(
        subject, textifier.handle(message), to=to, from_email=from_email,
        headers={'Return-Path': settings.RETURN_PATH_EMAIL}
    )
    msg.attach_alternative(message, 'text/html')
    msg.send()


# noinspection PyAbstractClass
class SubCount(Subquery):
    """
    Version of Subquery that outputs the count instead of the result. Good for annotation.
    """
    template = "(SELECT count(*) FROM (%(subquery)s) _count)"
    output_field = IntegerField()


def count_hit(request: HttpRequest, instance: Model):
    if request.GET.get('view', None):
        hit_count = HitCount.objects.get_for_object(instance)
        HitCountMixin.hit_count(request, hit_count)


def fake_destroy_comment(instance):
    instance.text = ''
    instance.deleted = True
    if instance.comments.all().filter(deleted=True).count() == instance.comments.all().count():
        instance.thread_deleted = True
    instance.save()


def real_destroy_comment(instance):
    target = instance.content_object
    if not instance.comments.all().exists() or not target:
        instance.delete()
        if target and isinstance(target, Comment):
            if target.deleted and not target.comments.all().exists():
                target.delete()
    else:
        instance.text = ''
        instance.deleted = True
        instance.save()


def destroy_comment(instance):
    remove_comment(instance.id)
    if getattr(instance.top, 'preserve_comments', False):
        fake_destroy_comment(instance)
    else:
        real_destroy_comment(instance)
    if hasattr(instance.top, 'comment_deleted'):
        instance.top.comment_deleted(instance)


def create_comment(target: Model, serializer: 'NewCommentSerializer', user: 'User') -> Comment:
    if isinstance(target, Comment):
        top = target.top
    else:
        top = target
    return serializer.save(
        user=user,
        content_type=ContentType.objects.get_for_model(target),
        object_id=target.id,
        top_object_id=top.id,
        top_content_type=ContentType.objects.get_for_model(top)
    )